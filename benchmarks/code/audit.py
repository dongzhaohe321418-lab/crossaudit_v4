"""The five arms, run over one fixed set of solutions.

Every model arm enters ``crossaudit.auditor.run.run_audit`` — the product's real audit:
the same SYSTEM prompt, the same deterministic layer, the same reply validation, the same
verdict synthesis in code. Nothing about the audit is simulated. What the arms vary is
exactly two things, and nothing else:

    arm            auditor model                        deterministic layer
    ----------------------------------------------------------------------------------
    none           —                                    —
    checks         —                                    general + visible_tests
    self           the generator's own model            general
    cross          a different vendor                   general
    cross+checks   a different vendor                   general + visible_tests

``visible_tests`` is a study-supplied deterministic check registered through the DCL
registry. CrossAudit ships no test-runner check (its ``general`` profile is
parses/declared/links/placeholders), so a code project would supply one; this is that
check, and it runs the *visible* suite only. The hidden suite never reaches any prompt,
any check, or any model.

**The `self` arm is a configuration the product refuses.** ``auditor/run.py`` raises
``ConfigDenial`` on a same-vendor generator/auditor pair — "a same-vendor pair is not
CrossAudit". The arm exists as the control the study needs, and is obtained by leaving
``generator_vendor`` unset in its config so the gate has nothing to compare against. That
is a deliberate bypass of a product guarantee, for measurement only, and it is recorded
here and in the report rather than hidden.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "expertlongbench"))

from corpus import Problem, load_problems  # noqa: E402

SOLUTION_PATH = "work/solution/solution.py"
TESTS_PATH = "work/solution/tests_visible.py"

ARMS = ("none", "checks", "self", "cross", "cross+checks")
MODEL_ARMS = ("self", "cross", "cross+checks")
CHECKS_ARMS = ("checks", "cross+checks")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------------
# the study-supplied deterministic check
# ---------------------------------------------------------------------------------

#: Set per instance immediately before ``run_audit``. A check is a pure function of the
#: increment bytes in the product's contract; running a test suite is I/O, so the result
#: is computed outside and handed in here rather than pretending otherwise. It is still
#: fully deterministic and no model is involved.
_VISIBLE_RESULT: dict = {}


def register_visible_tests_check() -> None:
    from crossaudit.dcl.framework import BLOCKER, Finding, register

    def check_visible_tests(files):
        result = _VISIBLE_RESULT
        if not result:
            return []
        if result["passed"]:
            return []
        failed = result.get("failed_indices") or []
        detail = (f"{len(failed)} of {result.get('total', 0)} visible assertions failed"
                  if failed else (result.get("error") or "the visible suite did not pass"))
        return [Finding(
            BLOCKER, "CA-TEST-001", SOLUTION_PATH,
            f"the visible test suite does not pass: {detail}")]

    register("visible_tests", check_visible_tests,
             "The project's visible test suite runs and every assertion in it passes.")


# ---------------------------------------------------------------------------------
# configs
# ---------------------------------------------------------------------------------

CONFIG_TEMPLATE = """\
version: 1
science_repo: evalplus-code-study
constitution: AUDIT_RULES.md
max_rounds: 1
auditor:
  vendor: {auditor_vendor}
  provider: {auditor_provider}
  model: {auditor_model}
  key_env: {auditor_key_env}
{generator_block}\
isolation:
  minimum:
    parametric: true
    contextual: true
    permissive: false
state:
  dir: .crossaudit
ledger:
  dir: cycles
scope:
  dirs: [work]
checks: {checks}
authority:
  lone_model_blocker: block
"""

GENERATOR_BLOCK = """\
generator:
  vendor: {vendor}
  provider: {provider}
  model: {model}
  key_env: {key_env}
"""


def build_project(root: Path, arm: str, auditor_spec: str, generator_spec: str,
                  constitution: str) -> Path:
    """A real crossaudit project: real config, real constitution, real state dir."""
    from provider import role_for

    project = root / f"project-{arm.replace('+', '_')}"
    (project / "work" / "solution").mkdir(parents=True, exist_ok=True)
    auditor = role_for(auditor_spec)
    checks = ("[parseable, declared, internal, complete, visible_tests]"
              if arm in CHECKS_ARMS else "general")
    # The self arm leaves generator: unset so heterogeneity() has nothing to compare;
    # see this module's docstring. Every other arm declares the real generator, so the
    # same-vendor gate is live exactly as it is in the product.
    generator_block = ""
    if arm != "self":
        generator = role_for(generator_spec)
        generator_block = GENERATOR_BLOCK.format(
            vendor=generator.vendor, provider=generator.provider,
            model=generator.model, key_env=generator.key_env)
    (project / "crossaudit.yml").write_text(CONFIG_TEMPLATE.format(
        auditor_vendor=auditor.vendor, auditor_provider=auditor.provider,
        auditor_model=auditor.model, auditor_key_env=auditor.key_env,
        generator_block=generator_block, checks=checks), encoding="utf-8")
    (project / "AUDIT_RULES.md").write_text(constitution, encoding="utf-8")
    return project


def shipped_constitution() -> str:
    from crossaudit.scaffold import read as read_template
    return read_template("GENERAL_AUDIT_RULES.md").replace("<PROJECT>", "evalplus-code-study")


# ---------------------------------------------------------------------------------
# one audited instance
# ---------------------------------------------------------------------------------

def increment_files(problem: Problem, solution: str) -> dict[str, bytes]:
    """What the auditor is shown. The hidden suite is not in it and never is."""
    return {
        SOLUTION_PATH: solution.encode("utf-8"),
        TESTS_PATH: problem.visible_tests_text().encode("utf-8"),
    }


def audit_one(cfg, problem: Problem, solution: str, visible_result: dict,
              constitution: str, run_id: str, arm: str) -> dict:
    global _VISIBLE_RESULT
    from crossaudit.auditor.run import run_audit

    files = increment_files(problem, solution)
    _VISIBLE_RESULT = visible_result if arm in CHECKS_ARMS else {}
    started = time.monotonic()

    def on_event(*_args, **_kwargs):  # the loop's event sink; this study consumes nothing
        return None
    on_event.run_id = run_id
    on_event.heartbeat = lambda: None

    row: dict = {"arm": arm, "problem_id": problem.problem_id,
                 "benchmark": problem.benchmark}
    try:
        outcome = run_audit(
            cfg=cfg, sha="0" * 40, round_=1, files=files, notes=[],
            constitution=constitution, constitution_commit="frozen",
            task=problem.spec, on_event=on_event,
            usage_context={"run_id": run_id, "arm": arm,
                           "problem_id": problem.problem_id})
    except Exception as exc:  # noqa: BLE001
        row.update({"ok": False, "error": f"{type(exc).__name__}: {exc}",
                    "wall_s": time.monotonic() - started})
        _VISIBLE_RESULT = {}
        return row
    finally:
        _VISIBLE_RESULT = {}

    model_findings = ((outcome.model_reply or {}).get("findings") or [])
    dcl_findings = outcome.dcl.get("findings", [])
    blockers = [f for f in model_findings if f.get("severity") == "BLOCKER"]
    dcl_blockers = [f for f in dcl_findings if f.get("severity") == "BLOCKER"]
    row.update({
        "ok": True,
        "error": "",
        "verdict": outcome.verdict,
        "dcl_verdict": outcome.dcl.get("verdict"),
        "dcl_hard_failures": outcome.dcl.get("total_hard_failures", 0),
        "model_findings": len(model_findings),
        "model_blockers": len(blockers),
        "dcl_blockers": len(dcl_blockers),
        # The flag: at least one BLOCKER from either tier. ADVISORY never gates in the
        # product, so it must not count as a flag here either.
        "flagged": bool(blockers or dcl_blockers),
        "flagged_by_model": bool(blockers),
        "flagged_by_checks": bool(dcl_blockers),
        "rules": sorted({f.get("rule", "") for f in blockers}),
        "dcl_rules": sorted({f.get("rule", "") for f in dcl_blockers}),
        "finding_sha256": [sha256_text(f.get("observation", "")) for f in blockers],
        "finding_chars": [len(f.get("observation", "")) for f in blockers],
        "invalid_reason": outcome.invalid_reason or "",
        "prompt_sha256": outcome.prompt_sha256,
        "wall_s": time.monotonic() - started,
    })
    return row


def deterministic_only(problem: Problem, solution: str, visible_result: dict,
                       cfg, arm: str) -> dict:
    """The `checks` arm: the deterministic layer, no model, no cost."""
    global _VISIBLE_RESULT
    from crossaudit.dcl import run_checks

    _VISIBLE_RESULT = visible_result
    try:
        result = run_checks(increment_files(problem, solution), cfg.checks, [], cfg.plugins)
    finally:
        _VISIBLE_RESULT = {}
    dcl = result.as_dict()
    blockers = [f for f in dcl["findings"] if f.get("severity") == "BLOCKER"]
    return {
        "arm": arm, "problem_id": problem.problem_id, "benchmark": problem.benchmark,
        "ok": True, "error": "", "verdict": dcl["verdict"], "dcl_verdict": dcl["verdict"],
        "dcl_hard_failures": dcl["total_hard_failures"],
        "model_findings": 0, "model_blockers": 0, "dcl_blockers": len(blockers),
        "flagged": bool(blockers), "flagged_by_model": False,
        "flagged_by_checks": bool(blockers),
        "rules": [], "dcl_rules": sorted({f.get("rule", "") for f in blockers}),
        "finding_sha256": [], "finding_chars": [], "invalid_reason": "",
        "prompt_sha256": "", "wall_s": 0.0,
    }


# ---------------------------------------------------------------------------------
# sampling
# ---------------------------------------------------------------------------------

def choose_audit_set(scored: list[dict], seed: int, caps: dict[str, int]) -> list[str]:
    """The audited subset, drawn once and shared by every arm.

    Auditing all 540 solutions in three model arms costs more than the budget, so the
    study audits a stratified sample with known, preregistered strata: every instance of
    the population the study is about, and capped random draws of the other two. Drawn
    from a seed before any audit runs, so no arm can influence which instances it sees.
    """
    by_stratum: dict[str, list[str]] = {"P": [], "C": [], "F": []}
    for row in sorted(scored, key=lambda r: r["problem_id"]):
        by_stratum[row["stratum"]].append(row["problem_id"])
    chosen: list[str] = []
    rng = random.Random(seed)
    for stratum in ("P", "C", "F"):
        pool = by_stratum[stratum]
        cap = caps.get(stratum, 0)
        chosen.extend(sorted(pool) if cap >= len(pool) else sorted(rng.sample(pool, cap)))
    return sorted(chosen)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scored", required=True, help="evaluate.py output JSONL")
    parser.add_argument("--solutions", required=True, help="generate.py output JSONL")
    parser.add_argument("--arm", required=True, choices=list(ARMS))
    parser.add_argument("--out", required=True, help="findings JSONL for this arm")
    parser.add_argument("--audit-set", required=True, help="json file of chosen problem ids")
    parser.add_argument("--auditor", default="openai:gpt-5.6-terra")
    parser.add_argument("--generator", default="anthropic:claude-haiku-4-5-20251001")
    parser.add_argument("--scratch", required=True)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--budget-usd", type=float, default=0.0,
                        help="stop this arm when its own spend passes this")
    args = parser.parse_args(argv)

    from run import load_credentials
    load_credentials()
    from crossaudit.config import load
    register_visible_tests_check()

    problems = {p.problem_id: p for p in load_problems()}
    scored = {json.loads(l)["problem_id"]: json.loads(l)
              for l in Path(args.scored).read_text(encoding="utf-8").splitlines() if l.strip()}
    solutions = {json.loads(l)["problem_id"]: json.loads(l)
                 for l in Path(args.solutions).read_text(encoding="utf-8").splitlines()
                 if l.strip()}
    audit_set = json.loads(Path(args.audit_set).read_text(encoding="utf-8"))["problem_ids"]

    arm = args.arm
    if arm == "none":
        rows = [{"arm": "none", "problem_id": pid, "benchmark": problems[pid].benchmark,
                 "ok": True, "error": "", "verdict": "PASS", "dcl_verdict": "PASS",
                 "dcl_hard_failures": 0, "model_findings": 0, "model_blockers": 0,
                 "dcl_blockers": 0, "flagged": False, "flagged_by_model": False,
                 "flagged_by_checks": False, "rules": [], "dcl_rules": [],
                 "finding_sha256": [], "finding_chars": [], "invalid_reason": "",
                 "prompt_sha256": "", "wall_s": 0.0}
                for pid in audit_set]
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with Path(args.out).open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, sort_keys=True) + "\n")
        print(f"arm none: {len(rows)} rows, $0.00 (by construction)")
        return 0

    scratch = Path(args.scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    constitution = shipped_constitution()
    project = build_project(scratch, arm, args.auditor, args.generator, constitution)
    cfg = load(project / "crossaudit.yml")
    run_id = args.run_id or f"{arm}-{int(time.time())}"

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done: set[str] = set()
    if out.exists():
        done = {json.loads(l)["problem_id"]
                for l in out.read_text(encoding="utf-8").splitlines() if l.strip()}
    todo = [pid for pid in audit_set if pid not in done]
    print(f"arm {arm}: {len(done)} done, {len(todo)} to go, auditor {args.auditor}")

    from crossaudit import usage

    def spend_so_far() -> float:
        events, _ = usage.read_events(cfg.root / cfg.state_dir / usage.LEDGER_NAME)
        return sum(float(e.get("api_value_usd") or 0.0)
                   for e in events if e.get("run_id") == run_id)

    with out.open("a", encoding="utf-8") as handle:
        for index, pid in enumerate(todo, start=1):
            problem = problems[pid]
            solution = solutions[pid]["solution"]
            visible = scored[pid]["visible"]
            if arm == "checks":
                row = deterministic_only(problem, solution, visible, cfg, arm)
            else:
                row = audit_one(cfg, problem, solution, visible, constitution, run_id, arm)
            row["stratum"] = scored[pid]["stratum"]
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            handle.flush()
            if arm != "checks" and (index % 10 == 0 or index == len(todo)):
                spent = spend_so_far()
                print(f"  {index}/{len(todo)}  ${spent:.3f}", flush=True)
                if args.budget_usd and spent >= args.budget_usd:
                    print(f"  stopping: arm spend ${spent:.3f} reached the "
                          f"${args.budget_usd:.2f} cap after {index} instances")
                    break
    if arm != "checks":
        print(f"arm {arm} spend ${spend_so_far():.4f}; run_id {run_id}; project {project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
