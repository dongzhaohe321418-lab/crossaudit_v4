"""Study 8, ceiling 2 — the closed loop: audit, revise once, score against hidden tests.

Preregistered in ``ceiling/PREREGISTRATION.md`` §2, committed before the first model call.

The owner's question is whether self-audit raises *accuracy*, not whether it raises
recall, so this module measures accuracy and nothing else. For each instance in a frozen
paired sample it runs

    frozen solution -> run_audit -> (if BLOCKED) the product's revision -> hidden suite

and records whether the *revised* solution passes the hidden tests. Ground truth is a
Python interpreter raising ``AssertionError`` or not; no model judges anything.

Three things about the shape, all preregistered and all load-bearing:

* **Generation is not repeated.** Every arm starts from study 2's byte-identical frozen
  solution, so no difference between arms can be generation variance.
* **A revision happens iff the audit BLOCKS**, which is what the product does. Where it
  does not block, the revised solution *is* the original and the instance still counts in
  the denominator. The loop's reach is bounded by its recall, and the primary outcome is
  unconditional on whether a revision occurred — ``CORRECTIONS.md`` item 9 is this
  project's largest retraction and it is exactly the error of conditioning on that event.
* **The revision prompt is the product's own.** ``crossaudit.generator.GENERATOR_SYSTEM``
  with ``build_prompt(..., findings=render_findings(outcome.report))``, called as
  ``cli/build.py`` calls it on a repair round. No new prompt is written for this study.

Arms differ in the auditor and in nothing else; the reviser is the same model, through the
same project config, in every arm.

    python benchmarks/code/loop.py --probe --run <run-dir>
    python benchmarks/code/loop.py --run <run-dir> --arm self-loop --budget-usd 5
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "expertlongbench"))

import audit as study1  # noqa: E402
import execute  # noqa: E402
from corpus import Problem, load_problems  # noqa: E402

REPO = HERE.parent.parent
RECORDS = HERE / "records"
CEILING = RECORDS / "ceiling"
LOOP = CEILING / "loop"

SOLUTION_PATH = study1.SOLUTION_PATH          # work/solution/solution.py
TESTS_PATH = study1.TESTS_PATH                # work/solution/tests_visible.py

CROSS = "openai:gpt-5.6-terra"
SELF = "anthropic:claude-haiku-4-5-20251001"
GENERATOR = "anthropic:claude-haiku-4-5-20251001"

#: The sample seed, fixed in the preregistration before any instance was drawn.
SAMPLE_SEED = 20260907
#: Instances per (stratum, batch) cell — 28 x 4 cells = 56 P and 56 C.
PER_CELL = 28

#: The one rule the referent arm adds, and the only thing that differs between
#: ``cross-loop`` and ``referent-loop``. Quoted verbatim in the preregistration.
REFERENT_RULE = """

### CA-COVER-001
**BLOCKER.** The increment's visible test suite is shown to you. It is not a
specification and it is not complete. Identify the behaviour the specification
requires that the visible tests **do not exercise** — the input classes they
never construct — and judge the solution on those. A defect the visible tests
would not catch is the defect this rule exists to find.
"""

ARMS: dict[str, dict] = {
    "self-loop":     {"auditor": SELF,  "referent": False, "same_vendor": True,  "draw": 1},
    "self-loop-rep": {"auditor": SELF,  "referent": False, "same_vendor": True,  "draw": 2},
    "cross-loop":    {"auditor": CROSS, "referent": False, "same_vendor": False, "draw": 1},
    "referent-loop": {"auditor": CROSS, "referent": True,  "same_vendor": False, "draw": 1},
}
#: Preregistered completion order when the budget cap binds part-way.
ARM_ORDER = ("self-loop", "self-loop-rep", "cross-loop", "referent-loop")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------------
# the sample, drawn once from a seed fixed in the preregistration
# ---------------------------------------------------------------------------------

def build_sample(audit_set: list[str], instances: dict[str, dict]) -> dict:
    """28 instances from each of the four (stratum, batch) cells: 56 P and 56 C.

    Deterministic given the seed — ids are sorted before the shuffle, so the sample does
    not depend on file order. Drawn and committed before the first audit of this ceiling.
    """
    rng = random.Random(SAMPLE_SEED)
    cells: dict[tuple[str, str], list[str]] = {}
    for iid in audit_set:
        inst = instances[iid]
        if inst["stratum"] in ("P", "C"):
            cells.setdefault((inst["stratum"], inst["batch"]), []).append(iid)
    chosen: list[str] = []
    for key in sorted(cells):
        ids = sorted(cells[key])
        rng.shuffle(ids)
        chosen.extend(sorted(ids[:PER_CELL]))
    return {"seed": SAMPLE_SEED, "per_cell": PER_CELL,
            "method": "28 per (stratum, batch) cell; random.Random(seed).shuffle over "
                      "sorted ids; first 28 taken, then re-sorted",
            "instance_ids": sorted(chosen)}


# ---------------------------------------------------------------------------------
# projects
# ---------------------------------------------------------------------------------

def build_audit_project(root: Path, arm: str, constitution: str) -> Path:
    """The audit project for one arm: the product's real config and real constitution.

    A ``self`` arm leaves ``generator:`` unset so the product's same-vendor gate has
    nothing to compare against — the identical deliberate bypass studies 1, 2 and 7
    recorded, confined to the harness. ``src/`` is not touched.
    """
    from provider import role_for

    spec = ARMS[arm]
    project = root / f"audit-{arm}"
    (project / "work" / "solution").mkdir(parents=True, exist_ok=True)
    auditor = role_for(spec["auditor"])
    generator_block = ""
    if not spec["same_vendor"]:
        gen = role_for(GENERATOR)
        generator_block = study1.GENERATOR_BLOCK.format(
            vendor=gen.vendor, provider=gen.provider, model=gen.model, key_env=gen.key_env)
    (project / "crossaudit.yml").write_text(study1.CONFIG_TEMPLATE.format(
        auditor_vendor=auditor.vendor, auditor_provider=auditor.provider,
        auditor_model=auditor.model, auditor_key_env=auditor.key_env,
        generator_block=generator_block, checks="general"), encoding="utf-8")
    (project / "AUDIT_RULES.md").write_text(constitution, encoding="utf-8")
    return project


def build_reviser_project(root: Path, constitution: str) -> Path:
    """One reviser project, shared by every arm.

    The arms' independent variable is the auditor, so the reviser must be identical
    across them: same model, same config, same constitution, same prompt builder. It
    declares both roles, so the product's heterogeneity gate is live here exactly as it
    is in a real project.
    """
    from provider import role_for

    project = root / "reviser"
    (project / "work" / "solution").mkdir(parents=True, exist_ok=True)
    auditor = role_for(CROSS)
    gen = role_for(GENERATOR)
    (project / "crossaudit.yml").write_text(study1.CONFIG_TEMPLATE.format(
        auditor_vendor=auditor.vendor, auditor_provider=auditor.provider,
        auditor_model=auditor.model, auditor_key_env=auditor.key_env,
        generator_block=study1.GENERATOR_BLOCK.format(
            vendor=gen.vendor, provider=gen.provider, model=gen.model, key_env=gen.key_env),
        checks="general"), encoding="utf-8")
    (project / "AUDIT_RULES.md").write_text(constitution, encoding="utf-8")
    return project


# ---------------------------------------------------------------------------------
# one audit, keeping the report the product would show a generator
# ---------------------------------------------------------------------------------

def audit_one(cfg, problem: Problem, solution: str, inst: dict, constitution: str,
              run_id: str, arm: str) -> dict:
    """``run_audit`` — the product's real audit — on the study's increment.

    Field for field this is ``audit2.holistic_one``. It is restated because this study
    needs ``outcome.report``: the report is what the product hands the generator on a
    repair round, and reproducing the loop means passing exactly that. The report text
    quotes the corpus, so it stays in the gitignored run directory and never reaches a
    committed record — only its sha256 and length do.
    """
    from crossaudit.auditor.run import run_audit

    files = study1.increment_files(problem, solution)
    study1._VISIBLE_RESULT = {}          # this study carries no deterministic layer
    started = time.monotonic()

    def on_event(*_args, **_kwargs):
        return None
    on_event.run_id = run_id
    on_event.heartbeat = lambda: None

    row = {"arm": arm, "draw": ARMS[arm]["draw"], "instance_id": inst["instance_id"],
           "batch": inst["batch"], "problem_id": inst["problem_id"],
           "stratum": inst["stratum"], "benchmark": problem.benchmark,
           "solution_sha256": inst["solution_sha256"], "run_id": run_id}
    try:
        outcome = run_audit(
            cfg=cfg, sha="0" * 40, round_=1, files=files, notes=[],
            constitution=constitution, constitution_commit="frozen",
            task=problem.spec, on_event=on_event,
            usage_context={"run_id": run_id, "arm": arm,
                           "problem_id": problem.problem_id})
    except Exception as exc:  # noqa: BLE001 - recorded, never swallowed
        row.update({"audit_ok": False, "audit_error": f"{type(exc).__name__}: {exc}",
                    "audit_wall_s": round(time.monotonic() - started, 3)})
        return row

    model_findings = ((outcome.model_reply or {}).get("findings") or [])
    dcl_findings = outcome.dcl.get("findings", [])
    blockers = [f for f in model_findings if f.get("severity") == "BLOCKER"]
    dcl_blockers = [f for f in dcl_findings if f.get("severity") == "BLOCKER"]
    row.update({
        "audit_ok": True, "audit_error": "",
        "verdict": outcome.verdict,
        "dcl_verdict": outcome.dcl.get("verdict"),
        "model_findings": len(model_findings),
        "model_blockers": len(blockers),
        "model_advisories": len(model_findings) - len(blockers),
        "dcl_blockers": len(dcl_blockers),
        "flagged": bool(blockers or dcl_blockers),
        "rules": sorted({f.get("rule", "") for f in blockers}),
        "advisory_rules": sorted({f.get("rule", "") for f in model_findings
                                  if f.get("severity") != "BLOCKER"}),
        "finding_sha256": [sha256_text(f.get("observation", "")) for f in blockers],
        "finding_chars": [len(f.get("observation", "")) for f in blockers],
        "invalid_reason": outcome.invalid_reason or "",
        "prompt_sha256": outcome.prompt_sha256,
        "report_sha256": sha256_text(outcome.report or ""),
        "report_chars": len(outcome.report or ""),
        "audit_wall_s": round(time.monotonic() - started, 3),
        # kept in memory for the revision step; dropped before anything is written
        "_report": outcome.report or "",
    })
    return row


# ---------------------------------------------------------------------------------
# one revision, through the product's own generator path
# ---------------------------------------------------------------------------------

def revise_one(cfg, complete, problem: Problem, solution: str, report: str,
               constitution: str) -> dict:
    """One repair round, exactly as ``cli/build.py`` runs one.

    ``current`` — "THE WORK AS IT STANDS" — is **the solution file alone** (deviation 2).
    The visible suite is in the *audit* increment exactly as studies 1, 2 and 7 put it
    there, so the audit prompt is byte-identical to theirs; but it is a supplied contract,
    not this generator's deliverable, and a pilot of 8 instances found the reviser
    answering test-file findings by rewriting the tests rather than the solution. Editing
    the contract is the "make a check disappear" move the product's own generator system
    prompt forbids, and scoring a solution against a suite the solution's author just
    rewrote would measure nothing. Any file other than the solution that the generator
    returns is discarded and counted in ``returned_non_solution``.
    """
    import crossaudit.generator as gen_mod

    root = cfg.root
    (root / "work" / "solution").mkdir(parents=True, exist_ok=True)
    tests_text = problem.visible_tests_text()
    (root / SOLUTION_PATH).write_text(solution, encoding="utf-8")
    (root / TESTS_PATH).write_text(tests_text, encoding="utf-8")
    current = {SOLUTION_PATH: solution}
    findings = gen_mod.render_findings(report)

    out: dict = {"findings_sha256": sha256_text(findings), "findings_chars": len(findings)}
    started = time.monotonic()
    try:
        work = gen_mod.generate(
            task=problem.spec, constitution=constitution,
            current=current, complete=complete, findings=findings,
            allowed_dirs=cfg.scope_dirs, root=root,
            document_growth_budget=(cfg.repair.max_document_growth or None
                                    if cfg.repair.enabled else None))
    except Exception as exc:  # noqa: BLE001
        out.update({"revise_ok": False, "revise_error": f"{type(exc).__name__}: {exc}",
                    "revise_wall_s": round(time.monotonic() - started, 3)})
        return out
    files = getattr(work, "files", None)
    if not isinstance(files, dict):
        out.update({"revise_ok": False,
                    "revise_error": f"generator returned {type(work).__name__}, not work",
                    "revise_wall_s": round(time.monotonic() - started, 3)})
        return out
    revised = files.get(SOLUTION_PATH, solution)
    out.update({
        "revise_ok": True, "revise_error": "",
        "touched_tests": TESTS_PATH in files and files[TESTS_PATH] != tests_text,
        "returned_non_solution": sorted(p for p in files if p != SOLUTION_PATH),
        "returned_paths": sorted(files),
        "revised_solution": revised,
        "changed": revised != solution,
        "revise_wall_s": round(time.monotonic() - started, 3),
    })
    return out


# ---------------------------------------------------------------------------------
# scoring — model-free, in execute.py's subprocess sandbox
# ---------------------------------------------------------------------------------

def score(problem: Problem, solution: str, timeout: float) -> dict:
    """The two suites on one candidate. Nothing here is executed in this interpreter."""
    visible = execute.run_suite(problem.visible_program(solution), timeout=timeout,
                               instrumented=problem.visible_instrumented)
    program, instrumented = problem.hidden_program(solution)
    hidden = execute.run_suite(program, timeout=timeout, instrumented=instrumented)
    return {"visible_passed": visible.passed, "visible_error": visible.error[:200],
            "hidden_passed": hidden.passed, "hidden_total": hidden.total,
            "hidden_failed_n": len(hidden.failed_indices),
            "hidden_failed_indices": hidden.failed_indices[:50],
            "hidden_mode": hidden.mode, "hidden_timed_out": hidden.timed_out,
            "hidden_error": hidden.error[:200]}


# ---------------------------------------------------------------------------------
# the arm
# ---------------------------------------------------------------------------------

class Spend:
    """Cumulative model spend for this study, read from the projects' usage ledgers."""

    def __init__(self, prefix: str) -> None:
        #: A per-invocation stamp. ``run_id`` is the key the usage ledger is read back
        #: on, so two invocations must never mint the same one: a resumed or repeated
        #: arm would otherwise inherit the earlier call's cost as well as its own.
        self.stamp = time.strftime("%m%d%H%M%S", time.gmtime())
        self.prefix = prefix
        self.ledgers: list[Path] = []
        self._lock = threading.Lock()

    def add_ledger(self, path: Path) -> None:
        with self._lock:
            if path not in self.ledgers:
                self.ledgers.append(path)

    def by_run_id(self) -> dict[str, float]:
        from crossaudit import usage
        totals: dict[str, float] = {}
        with self._lock:
            ledgers = list(self.ledgers)
        for ledger in ledgers:
            if not ledger.exists():
                continue
            events, _ = usage.read_events(ledger)
            for event in events:
                run_id = str(event.get("run_id") or "")
                if run_id.startswith(self.prefix):
                    totals[run_id] = totals.get(run_id, 0.0) + float(
                        event.get("api_value_usd") or 0.0)
        return totals

    def total(self) -> float:
        return sum(self.by_run_id().values())


def run_arm(arm: str, sample: list[str], *, instances, problems, solutions, scored,
            scratch: Path, spend: Spend, budget_usd: float, workers: int,
            timeout: float, run_dir: Path, limit: int = 0,
            max_passes: int = 6, cooldown_s: float = 75.0) -> int:
    """Audit every sampled instance, revise the blocked ones, score what comes out.

    Two phases on purpose. Audits are independent and run in parallel; revisions stage
    files into one shared reviser project and run sequentially, so no two revisions can
    see each other's working tree. Everything is cached per instance, so an interrupted
    arm resumes without re-spending.
    """
    from crossaudit.config import load
    from crossaudit import usage as usage_mod

    LOOP.mkdir(parents=True, exist_ok=True)
    cache_path = LOOP / f"{arm}.jsonl"
    private_dir = run_dir / "loop" / arm
    private_dir.mkdir(parents=True, exist_ok=True)

    constitution = study1.shipped_constitution()
    audit_constitution = (constitution + REFERENT_RULE) if ARMS[arm]["referent"] else constitution
    audit_project = build_audit_project(scratch, arm, audit_constitution)
    audit_cfg = load(audit_project / "crossaudit.yml")
    spend.add_ledger(audit_cfg.root / audit_cfg.state_dir / usage_mod.LEDGER_NAME)

    reviser_project = build_reviser_project(scratch, constitution)
    reviser_cfg = load(reviser_project / "crossaudit.yml")
    spend.add_ledger(reviser_cfg.root / reviser_cfg.state_dir / usage_mod.LEDGER_NAME)

    done: set[str] = set()
    if cache_path.exists():
        done = {json.loads(l)["instance_id"]
                for l in cache_path.read_text(encoding="utf-8").splitlines() if l.strip()}
    todo = [i for i in sample if i not in done]
    if limit:
        todo = todo[:limit]
    print(f"\narm {arm}: {len(done)} cached, {len(todo)} to run "
          f"(auditor {ARMS[arm]['auditor']}, referent={ARMS[arm]['referent']})", flush=True)
    if not todo:
        return 0

    halted = threading.Event()

    def audit(index_iid: tuple[int, str]) -> dict | None:
        index, iid = index_iid
        if halted.is_set():
            return None
        inst = instances[iid]
        problem = problems[inst["problem_id"]]
        run_id = f"{spend.prefix}{arm}-{spend.stamp}-a{index}"[:64]
        return audit_one(audit_cfg, problem, solutions[iid]["solution"], inst,
                         audit_constitution, run_id, arm)

    # The provider layer opens a circuit breaker after three consecutive route failures
    # and cools down for 60 s, during which every queued instance fails immediately — one
    # transient error therefore takes a whole pass with it. Study 7 recorded exactly this
    # (its deviation 3) and study 8's first attempt at this arm reproduced it. A failed
    # audit is NOT cached: it is simply still missing, and a later pass retries it after
    # the cooldown. Passes are bounded and whatever never lands is reported as a count.
    rows: list[dict] = []
    remaining = list(todo)
    failed_path = LOOP / f"{arm}.failed.jsonl"
    for attempt in range(1, max_passes + 1):
        if not remaining or halted.is_set():
            break
        if attempt > 1:
            print(f"  {arm}: pass {attempt}, {len(remaining)} still missing; waiting "
                  f"{cooldown_s:.0f}s for the breaker to close", flush=True)
            time.sleep(cooldown_s)
        landed: set[str] = set()
        with ThreadPoolExecutor(max_workers=workers) as pool, \
                failed_path.open("a", encoding="utf-8") as failures:
            for done_n, row in enumerate(pool.map(audit, list(enumerate(remaining))),
                                         start=1):
                if row is None:
                    continue
                if row.get("audit_ok"):
                    rows.append(row)
                    landed.add(row["instance_id"])
                else:
                    failures.write(json.dumps(
                        {"instance_id": row["instance_id"], "arm": arm, "pass": attempt,
                         "error": (row.get("audit_error") or "")[:300]},
                        sort_keys=True) + "\n")
                    failures.flush()
                if done_n % 20 == 0 or done_n == len(remaining):
                    total = spend.total()
                    print(f"  {arm} audit {done_n}/{len(remaining)} pass {attempt}  "
                          f"${total:.3f}  ok {len(landed)}", flush=True)
                    if budget_usd and total >= budget_usd:
                        print(f"  STOP: spend ${total:.3f} reached the "
                              f"${budget_usd:.2f} cap")
                        halted.set()
        remaining = [i for i in remaining if i not in landed]
    if remaining:
        print(f"  {arm}: {len(remaining)} instances never landed after {max_passes} "
              f"passes", flush=True)

    # Phase 2: revise every BLOCKED instance, sequentially, through the product's path.
    from crossaudit.cli.build import _generator_complete
    revise_run_id = f"{spend.prefix}{arm}-{spend.stamp}-revise"
    complete = _generator_complete(reviser_cfg, False,
                                   usage_context={"run_id": revise_run_id})
    blocked = [r for r in rows if r.get("audit_ok") and r.get("verdict") == "BLOCKED"]
    print(f"  {arm}: {len(blocked)} of {len(rows)} audits BLOCKED -> revising", flush=True)
    revisions: dict[str, dict] = {}
    for n, row in enumerate(blocked, start=1):
        if halted.is_set():
            break
        inst = instances[row["instance_id"]]
        problem = problems[inst["problem_id"]]
        revisions[row["instance_id"]] = revise_one(
            reviser_cfg, complete, problem, solutions[row["instance_id"]]["solution"],
            row["_report"], constitution)
        if n % 10 == 0 or n == len(blocked):
            print(f"  {arm} revise {n}/{len(blocked)}  ${spend.total():.3f}", flush=True)

    # Phase 3: score. Model-free, parallel, in execute.py's sandbox.
    costs = spend.by_run_id()
    revise_total = costs.get(revise_run_id, 0.0)
    revise_each = (revise_total / len(revisions)) if revisions else 0.0

    def finish(row: dict) -> dict:
        iid = row["instance_id"]
        inst = instances[iid]
        problem = problems[inst["problem_id"]]
        original = solutions[iid]["solution"]
        rev = revisions.get(iid, {})
        revised = rev.get("revised_solution", original)
        before = scored[iid]
        row = {k: v for k, v in row.items() if not k.startswith("_")}
        row["audit_cost_usd"] = round(costs.get(row.get("run_id", ""), 0.0), 8)
        row["revised"] = iid in revisions
        row["revise_ok"] = rev.get("revise_ok", None)
        row["revise_error"] = rev.get("revise_error", "")
        row["revise_cost_usd_apportioned"] = round(revise_each, 8) if iid in revisions else 0.0
        row["touched_tests"] = bool(rev.get("touched_tests", False))
        row["returned_paths"] = rev.get("returned_paths", [])
        row["returned_non_solution"] = rev.get("returned_non_solution", [])
        row["changed"] = bool(rev.get("changed", False))
        row["findings_sha256"] = rev.get("findings_sha256", "")
        row["findings_chars"] = rev.get("findings_chars", 0)
        row["revised_solution_sha256"] = sha256_text(revised)
        row["hidden_passed_before"] = bool(before["hidden"]["passed"])
        row["visible_passed_before"] = bool(before["visible"]["passed"])
        row["hidden_failed_n_before"] = len(before["hidden"].get("failed_indices") or [])
        row["hidden_timed_out_before"] = bool(before["hidden"].get("timed_out"))
        after = score(problem, revised, timeout) if row["changed"] else {
            "visible_passed": bool(before["visible"]["passed"]),
            "visible_error": "", "hidden_passed": bool(before["hidden"]["passed"]),
            "hidden_total": before["hidden"].get("total", 0),
            "hidden_failed_n": len(before["hidden"].get("failed_indices") or []),
            "hidden_failed_indices": (before["hidden"].get("failed_indices") or [])[:50],
            "hidden_mode": before["hidden"].get("mode", "binary"),
            "hidden_timed_out": bool(before["hidden"].get("timed_out")),
            "hidden_error": "", "not_rerun": True}
        row.update({f"{k}_after": v for k, v in after.items()})
        return row

    finished: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(4, workers)) as pool:
        for row in pool.map(finish, rows):
            finished.append(row)

    # The revised solutions are model output over a redistributable corpus, so they are
    # committed: the primary outcome re-scores from them with no key and no network.
    # The findings prose quotes the corpus and stays in the run directory.
    with cache_path.open("a", encoding="utf-8") as handle:
        for row in sorted(finished, key=lambda r: r["instance_id"]):
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    sol_path = LOOP / f"solutions-{arm}.jsonl"
    with sol_path.open("a", encoding="utf-8") as handle:
        for row in sorted(finished, key=lambda r: r["instance_id"]):
            iid = row["instance_id"]
            rev = revisions.get(iid, {})
            handle.write(json.dumps(
                {"arm": arm, "instance_id": iid, "problem_id": row["problem_id"],
                 "revised": iid in revisions, "changed": row["changed"],
                 "solution": rev.get("revised_solution", solutions[iid]["solution"]),
                 "solution_sha256": row["revised_solution_sha256"]},
                sort_keys=True) + "\n")
    with (private_dir / "reports.jsonl").open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(
                {"instance_id": row["instance_id"], "report": row.get("_report", ""),
                 "findings": revisions.get(row["instance_id"], {}).get("findings_sha256", "")},
                sort_keys=True) + "\n")
    print(f"  {arm}: wrote {len(finished)} rows; arm spend so far ${spend.total():.4f}",
          flush=True)
    return len(finished)


# ---------------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------------

def load_instances() -> dict[str, dict]:
    rows = {}
    for line in (RECORDS / "study2/instances.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row["instance_id"]] = row
    return rows


def probe(scratch: Path, spend: Spend) -> None:
    """One cheap call per route before any budget is committed."""
    from crossaudit.config import load
    from crossaudit import usage as usage_mod
    from provider import CrossAuditClient

    constitution = study1.shipped_constitution()
    project = build_reviser_project(scratch, constitution)
    cfg = load(project / "crossaudit.yml")
    spend.add_ledger(cfg.root / cfg.state_dir / usage_mod.LEDGER_NAME)
    client = CrossAuditClient(cfg=cfg, phase="ceiling-probe", run_id=f"{spend.prefix}probe")
    for spec in (CROSS, SELF):
        reply = client.complete(model=spec, system="Answer in one word.", user="Say READY.")
        print(f"probe {spec:44s} -> {reply.text.strip()[:40]!r}  ${reply.cost_usd:.6f}",
              flush=True)
    print(f"probe spend ${spend.total():.6f}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, help="the run dir: solutions and scored rows")
    parser.add_argument("--arm", default="", choices=("",) + ARM_ORDER)
    parser.add_argument("--budget-usd", type=float, default=5.0)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=execute.DEFAULT_TIMEOUT)
    parser.add_argument("--limit", type=int, default=0,
                        help="pilot: run only the first N uncached instances of the arm")
    parser.add_argument("--max-passes", type=int, default=6,
                        help="re-attempt passes for instances the provider "
                             "layer failed; a pass waits out the cooldown")
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args(argv)

    CEILING.mkdir(parents=True, exist_ok=True)
    LOOP.mkdir(parents=True, exist_ok=True)
    instances = load_instances()
    audit_set = json.loads(
        (RECORDS / "study2/audit_set.json").read_text(encoding="utf-8"))["instance_ids"]

    sample_path = CEILING / "loop_sample.json"
    if sample_path.exists():
        sample = json.loads(sample_path.read_text(encoding="utf-8"))
    else:
        sample = build_sample(audit_set, instances)
        sample_path.write_text(json.dumps(sample, indent=2, sort_keys=True) + "\n",
                               encoding="utf-8")
    ids = sample["instance_ids"]
    counts: dict[str, int] = {}
    for iid in ids:
        counts[instances[iid]["stratum"]] = counts.get(instances[iid]["stratum"], 0) + 1
    print(f"loop sample (seed {sample['seed']}): {len(ids)} instances {counts}", flush=True)

    from run import load_credentials
    load_credentials()
    study1.register_visible_tests_check()

    run_dir = Path(args.run)
    scratch = run_dir / "projects"
    scratch.mkdir(parents=True, exist_ok=True)
    spend = Spend("ceiling-loop-")

    if args.probe:
        probe(scratch, spend)
        return 0

    problems = {p.problem_id: p for p in load_problems()}
    solutions: dict[str, dict] = {}
    scored: dict[str, dict] = {}
    for batch in ("b1", "b2"):
        for line in (run_dir / f"study2-inputs/solutions-{batch}.jsonl").read_text(
                encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                solutions[f"{batch}:{row['problem_id']}"] = row
        for line in (run_dir / f"study2-inputs/scored-{batch}.jsonl").read_text(
                encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                scored[f"{batch}:{row['problem_id']}"] = row

    arms = [args.arm] if args.arm else list(ARM_ORDER)
    for arm in arms:
        if spend.total() >= args.budget_usd:
            print(f"budget ${args.budget_usd:.2f} reached; {arm} not run")
            break
        run_arm(arm, ids, instances=instances, problems=problems, solutions=solutions,
                scored=scored, scratch=scratch, spend=spend, budget_usd=args.budget_usd,
                workers=args.workers, timeout=args.timeout, run_dir=run_dir,
                limit=args.limit, max_passes=args.max_passes)
    print(f"\nceiling-2 spend this invocation: ${spend.total():.4f}", flush=True)
    write_manifest(spend, run_dir, scratch)
    return 0


def write_manifest(spend: Spend, run_dir: Path, scratch: Path) -> None:
    import platform
    from crossaudit.auditor import prompt as prompt_mod
    import crossaudit.generator as gen_mod

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                          text=True).stdout.strip()
    porcelain = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                               capture_output=True, text=True).stdout
    path = CEILING / "manifest_loop.json"
    prior = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    manifest = {
        "study": "ceiling (study 8), ceiling 2 — the closed loop",
        "code": {"commit": head, "status_porcelain": porcelain,
                 "files": {f: hashlib.sha256((REPO / f).read_bytes()).hexdigest()
                           for f in ("benchmarks/code/loop.py",
                                     "benchmarks/code/ceiling/PREREGISTRATION.md")
                           if (REPO / f).exists()}},
        "arms": {a: {"auditor": ARMS[a]["auditor"], "reviser": GENERATOR,
                     "referent_rule": ARMS[a]["referent"], "draw": ARMS[a]["draw"],
                     "same_vendor_bypass": ARMS[a]["same_vendor"]} for a in ARM_ORDER},
        "prompts": {
            "auditor_system_sha256": sha256_text(prompt_mod.SYSTEM),
            "generator_system_sha256": sha256_text(gen_mod.GENERATOR_SYSTEM),
            "referent_rule_sha256": sha256_text(REFERENT_RULE),
            "referent_rule_text": REFERENT_RULE,
        },
        "sampling": {"temperature": "provider default; the auditor capability card "
                                    "carries temperature=False (D154), so no sampling "
                                    "parameter is sent",
                     "reasoning_effort": None, "max_rounds": 1},
        "data": {"audit_set_sha256": hashlib.sha256(
                     (RECORDS / "study2/audit_set.json").read_bytes()).hexdigest(),
                 "instances_sha256": hashlib.sha256(
                     (RECORDS / "study2/instances.jsonl").read_bytes()).hexdigest(),
                 "sample_seed": SAMPLE_SEED, "per_cell": PER_CELL},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform(),
                        "executor": execute.EXECUTOR},
        "run_dir": str(run_dir), "scratch": str(scratch),
        "spend_usd_by_run_id": {k: round(v, 6) for k, v in sorted(spend.by_run_id().items())},
        "spend_usd_total": round(spend.total(), 6),
        "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if prior.get("spend_usd_total") and not manifest["spend_usd_total"]:
        manifest["spend_usd_total"] = prior["spend_usd_total"]
        manifest["spend_usd_by_run_id"] = prior["spend_usd_by_run_id"]
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
