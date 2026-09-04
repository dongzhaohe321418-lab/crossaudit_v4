"""Study 2's arms: one fixed set of solutions, judged by different audit *architectures*.

The model is not the independent variable here — the structure is. ``holistic-cross`` and
``holistic-self`` enter ``crossaudit.auditor.run.run_audit``, the product's real audit,
exactly as study 1's ``cross`` and ``self`` arms did. ``decomposed-cross`` and
``two-stage-filter`` are the architectures study 1 did not have, built in
``architectures.py`` on the same metered provider layer.

    arm                 structure                                     auditor
    ---------------------------------------------------------------------------------
    checks              deterministic layer only (visible tests)      none
    holistic-cross      one auditor reads code + rules -> findings    cross vendor
    holistic-self       the same, the generator's own model           self
    decomposed-cross    decompose spec -> check each property alone   cross vendor
    two-stage-filter    holistic-self proposes, cross filters         both

Every arm judges byte-identical solutions on the identical audit set. An **instance** is a
``(batch, problem_id)`` pair; see ``pool.py``.

The hidden suite never reaches any prompt, any check, or any model. In the decomposed arm
that is enforced structurally — the prompt builders take strings, never a ``Problem`` — and
proved in ``tests/test_architectures.py``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "expertlongbench"))

import architectures as arch  # noqa: E402
import audit as study1  # noqa: E402
from corpus import Problem, load_problems  # noqa: E402

ARMS = ("checks", "holistic-cross", "holistic-self", "decomposed-cross", "two-stage-filter")
HOLISTIC_ARMS = ("holistic-cross", "holistic-self")

CONFIG_TEMPLATE = study1.CONFIG_TEMPLATE
GENERATOR_BLOCK = study1.GENERATOR_BLOCK
sha256_text = study1.sha256_text


def build_project(root: Path, arm: str, auditor_spec: str, generator_spec: str,
                  constitution: str, with_checks: bool) -> Path:
    """A real crossaudit project: real config, real constitution, real state dir.

    ``holistic-self`` leaves ``generator:`` unset so the product's same-vendor gate has
    nothing to compare against — the same deliberate bypass study 1 recorded, and the only
    arm that could not be run as a customer would run it.
    """
    from provider import role_for

    project = root / f"project-{arm}"
    (project / "work" / "solution").mkdir(parents=True, exist_ok=True)
    auditor = role_for(auditor_spec)
    checks = ("[parseable, declared, internal, complete, visible_tests]"
              if with_checks else "general")
    generator_block = ""
    if arm != "holistic-self":
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


def blank_row(arm: str, inst: dict) -> dict:
    return {"arm": arm, "instance_id": inst["instance_id"], "batch": inst["batch"],
            "problem_id": inst["problem_id"], "stratum": inst["stratum"],
            "solution_sha256": inst["solution_sha256"]}


# ---------------------------------------------------------------------------------
# the holistic architecture — the product's real audit, unchanged
# ---------------------------------------------------------------------------------

def holistic_one(cfg, problem: Problem, solution: str, inst: dict, constitution: str,
                 run_id: str, arm: str) -> dict:
    """One holistic audit through ``run_audit``.

    Field for field this is study 1's ``audit.audit_one``; it is restated here only because
    the two-stage arm needs the BLOCKER observation *text* as its stage-2 input, and study 1
    deliberately records hashes rather than text. The extra ``blocker_texts`` key stays in
    the gitignored run directory — ``export2.py`` drops it, so no model output that could
    quote the corpus reaches the committed record.
    """
    from crossaudit.auditor.run import run_audit

    files = study1.increment_files(problem, solution)
    study1._VISIBLE_RESULT = {}          # these arms carry no deterministic layer
    started = time.monotonic()

    def on_event(*_args, **_kwargs):
        return None
    on_event.run_id = run_id
    on_event.heartbeat = lambda: None

    row = blank_row(arm, inst)
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
        return row

    model_findings = ((outcome.model_reply or {}).get("findings") or [])
    dcl_findings = outcome.dcl.get("findings", [])
    blockers = [f for f in model_findings if f.get("severity") == "BLOCKER"]
    dcl_blockers = [f for f in dcl_findings if f.get("severity") == "BLOCKER"]
    row.update({
        "ok": True, "error": "",
        "verdict": outcome.verdict,
        "dcl_verdict": outcome.dcl.get("verdict"),
        "dcl_hard_failures": outcome.dcl.get("total_hard_failures", 0),
        "model_findings": len(model_findings),
        "model_blockers": len(blockers),
        "dcl_blockers": len(dcl_blockers),
        "flagged": bool(blockers or dcl_blockers),
        "flagged_by_model": bool(blockers),
        "flagged_by_checks": bool(dcl_blockers),
        "rules": sorted({f.get("rule", "") for f in blockers}),
        "dcl_rules": sorted({f.get("rule", "") for f in dcl_blockers}),
        "finding_sha256": [sha256_text(f.get("observation", "")) for f in blockers],
        "finding_chars": [len(f.get("observation", "")) for f in blockers],
        "blocker_texts": [f.get("observation", "") for f in blockers],
        "invalid_reason": outcome.invalid_reason or "",
        "prompt_sha256": outcome.prompt_sha256,
        "wall_s": time.monotonic() - started,
    })
    return row


# ---------------------------------------------------------------------------------
# the decomposed architecture
# ---------------------------------------------------------------------------------

def properties_for(client, model: str, problem: Problem, cache: dict,
                   cache_path: Path) -> tuple[list[dict], dict]:
    """The checkable properties of a problem, computed once per *problem* and cached.

    The decomposer is shown ``problem.spec`` and nothing else — not the candidate solution,
    not the visible tests, not the hidden suite. The property list is therefore a function
    of the problem, so every candidate solution to it is checked against the identical list.
    """
    pid = problem.problem_id
    if pid in cache:
        return cache[pid]["properties"], {"cached": True, "cost_usd": 0.0,
                                          "input_tokens": 0, "output_tokens": 0,
                                          "wall_s": 0.0}
    system, user = arch.decompose_prompt(problem.spec)   # strings only; see architectures.py
    started = time.monotonic()
    completion = client.complete(model=model, system=system, user=user)
    properties = arch.parse_properties(completion.text)
    meta = {"cached": False, "cost_usd": completion.cost_usd,
            "input_tokens": completion.input_tokens,
            "output_tokens": completion.output_tokens,
            "wall_s": time.monotonic() - started,
            "prompt_sha256": sha256_text(system + "\n" + user),
            "response_sha256": sha256_text(completion.text)}
    cache[pid] = {"properties": properties,
                  "prompt_sha256": meta["prompt_sha256"],
                  "response_sha256": meta["response_sha256"]}
    cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")
    return properties, meta


def decomposed_one(client, model: str, problem: Problem, solution: str, inst: dict,
                   cache: dict, cache_path: Path, property_workers: int = 4) -> dict:
    """Decompose, then check each property **alone**, then aggregate."""
    row = blank_row("decomposed-cross", inst)
    started = time.monotonic()
    try:
        properties, dmeta = properties_for(client, model, problem, cache, cache_path)
    except Exception as exc:  # noqa: BLE001
        row.update({"ok": False, "error": f"decompose: {type(exc).__name__}: {exc}",
                    "wall_s": time.monotonic() - started})
        return row

    visible_tests = problem.visible_tests_text()
    cost = float(dmeta["cost_usd"])
    tokens_in = int(dmeta["input_tokens"])
    tokens_out = int(dmeta["output_tokens"])

    def check_one(prop: dict) -> tuple[dict, object, str]:
        """One property, checked alone. Each call sees this property and no other."""
        system, user = arch.check_prompt(          # strings only; see architectures.py
            problem.spec, solution, visible_tests, prop["category"], prop["property"])
        return prop, client.complete(model=model, system=system, user=user), \
            sha256_text(system + "\n" + user)

    # The properties are independent by construction — that is the architecture — so they
    # are checked concurrently. Concurrency changes wall time, never a verdict: no call
    # sees another's prompt or reply, and the results are reassembled in the original
    # property order below.
    try:
        with ThreadPoolExecutor(max_workers=property_workers) as pool:
            results = list(pool.map(check_one, properties))
    except Exception as exc:  # noqa: BLE001
        row.update({"ok": False, "error": f"check: {type(exc).__name__}: {exc}",
                    "wall_s": time.monotonic() - started, "cost_usd": cost})
        return row

    checks: list[dict] = []
    prompt_hashes: list[str] = []
    # The evidence text of VIOLATED properties, kept so the combined decomposed+two-stage
    # arm has something to filter. It stays in the gitignored run directory; export2.py
    # drops it, exactly as it drops the holistic arms' blocker_texts.
    violated_texts: list[str] = []
    for prop, completion, prompt_hash in results:
        verdict = arch.parse_check(completion.text)
        verdict["category"] = prop["category"]
        verdict["property_sha256"] = sha256_text(prop["property"])
        evidence = verdict.pop("evidence", "")
        verdict["evidence_sha256"] = sha256_text(evidence)
        if verdict["verdict"] == "VIOLATED":
            violated_texts.append(f"{prop['property']} — {evidence}".strip())
        checks.append(verdict)
        cost += completion.cost_usd
        tokens_in += completion.input_tokens
        tokens_out += completion.output_tokens
        prompt_hashes.append(prompt_hash)

    flagged = arch.aggregate(checks)
    row.update({
        "ok": True, "error": "",
        "flagged": flagged, "flagged_by_model": flagged, "flagged_by_checks": False,
        "verdict": "FAIL" if flagged else "PASS",
        "n_properties": len(properties),
        "n_violated": sum(1 for c in checks if c["verdict"] == "VIOLATED"),
        "n_unclear": sum(1 for c in checks if c["verdict"] == "UNCLEAR"),
        "n_unparsed": sum(1 for c in checks if not c.get("parsed")),
        "checks": checks,
        "blocker_texts": violated_texts,
        "decomposition_cached": dmeta["cached"],
        "decomposition_prompt_sha256": cache[problem.problem_id]["prompt_sha256"],
        "prompt_sha256": prompt_hashes,
        "cost_usd": cost, "input_tokens": tokens_in, "output_tokens": tokens_out,
        "wall_s": time.monotonic() - started,
    })
    return row


# ---------------------------------------------------------------------------------
# the two-stage architecture
# ---------------------------------------------------------------------------------

def two_stage_one(client, model: str, problem: Problem, solution: str, inst: dict,
                  proposed: list[str]) -> dict:
    """``holistic-self`` proposed these findings; the cross-vendor model triages them."""
    row = blank_row("two-stage-filter", inst)
    row["n_proposed"] = len(proposed)
    started = time.monotonic()
    if not proposed:
        # Nothing was proposed, so nothing can survive. No call, no cost.
        row.update({"ok": True, "error": "", "flagged": False, "flagged_by_model": False,
                    "flagged_by_checks": False, "verdict": "PASS", "n_kept": 0,
                    "kept": [], "cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0,
                    "wall_s": 0.0, "prompt_sha256": "", "filter_called": False})
        return row
    system, user = arch.filter_prompt(              # strings only; see architectures.py
        problem.spec, solution, problem.visible_tests_text(), proposed)
    try:
        completion = client.complete(model=model, system=system, user=user)
    except Exception as exc:  # noqa: BLE001
        row.update({"ok": False, "error": f"filter: {type(exc).__name__}: {exc}",
                    "wall_s": time.monotonic() - started})
        return row
    kept = arch.parse_filter(completion.text, len(proposed))
    row.update({
        "ok": True, "error": "",
        "flagged": any(kept), "flagged_by_model": any(kept), "flagged_by_checks": False,
        "verdict": "FAIL" if any(kept) else "PASS",
        "n_kept": sum(1 for k in kept if k), "kept": kept, "filter_called": True,
        "cost_usd": completion.cost_usd,
        "input_tokens": completion.input_tokens,
        "output_tokens": completion.output_tokens,
        "prompt_sha256": sha256_text(system + "\n" + user),
        "response_sha256": sha256_text(completion.text),
        "wall_s": time.monotonic() - started,
    })
    return row


# ---------------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, help="study run dir")
    parser.add_argument("--arm", required=True, choices=list(ARMS))
    parser.add_argument("--out", required=True)
    parser.add_argument("--auditor-cross", default="openai:gpt-5.6-terra")
    parser.add_argument("--auditor-self", default="anthropic:claude-haiku-4-5-20251001")
    parser.add_argument("--generator", default="anthropic:claude-haiku-4-5-20251001")
    parser.add_argument("--propose-from", default="",
                        help="two-stage-filter: the holistic-self arm's JSONL")
    parser.add_argument("--scratch", required=True)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--budget-usd", type=float, default=0.0)
    parser.add_argument("--property-workers", type=int, default=4,
                        help="concurrent per-property checks within one instance")
    args = parser.parse_args(argv)

    from run import load_credentials
    load_credentials()
    from crossaudit.config import load
    study1.register_visible_tests_check()

    run_dir = Path(args.run)
    problems = {p.problem_id: p for p in load_problems()}
    instances = {json.loads(l)["instance_id"]: json.loads(l)
                 for l in (run_dir / "instances.jsonl").read_text(
                     encoding="utf-8").splitlines() if l.strip()}
    audit_set = json.loads((run_dir / "audit_set.json").read_text(
        encoding="utf-8"))["instance_ids"]

    solutions: dict[str, dict] = {}
    scored: dict[str, dict] = {}
    for batch in sorted({inst["batch"] for inst in instances.values()}):
        for line in (run_dir / f"solutions-{batch}.jsonl").read_text(
                encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                solutions[f"{batch}:{row['problem_id']}"] = row
        for line in (run_dir / f"scored-{batch}.jsonl").read_text(
                encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                scored[f"{batch}:{row['problem_id']}"] = row

    arm = args.arm
    auditor_spec = args.auditor_self if arm == "holistic-self" else args.auditor_cross
    scratch = Path(args.scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    constitution = study1.shipped_constitution()
    project = build_project(scratch, arm, auditor_spec, args.generator, constitution,
                            with_checks=(arm == "checks"))
    cfg = load(project / "crossaudit.yml")
    run_id = args.run_id or f"{arm}-{int(time.time())}"

    proposed_by_instance: dict[str, list[str]] = {}
    if arm == "two-stage-filter":
        if not args.propose_from:
            parser.error("two-stage-filter needs --propose-from (the holistic-self arm)")
        for line in Path(args.propose_from).read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                proposed_by_instance[row["instance_id"]] = row.get("blocker_texts") or []

    client = None
    if arm in ("decomposed-cross", "two-stage-filter"):
        from provider import CrossAuditClient
        client = CrossAuditClient(cfg=cfg, phase=f"arch-{arm}", run_id=run_id)

    cache_path = run_dir / "properties.json"
    cache: dict = {}
    if arm == "decomposed-cross" and cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done: set[str] = set()
    if out.exists():
        done = {json.loads(l)["instance_id"]
                for l in out.read_text(encoding="utf-8").splitlines() if l.strip()}
    # P first, then C, then F. The primary outcome lives on P, and the preregistered
    # stopping rule is a budget; ordering the work this way means running out of money
    # truncates a secondary outcome rather than the number the study exists for. Each
    # instance is audited independently, so the order cannot change any instance's result.
    priority = {"P": 0, "C": 1, "F": 2}
    todo = sorted((iid for iid in audit_set if iid not in done),
                  key=lambda i: (priority[instances[i]["stratum"]], i))
    print(f"arm {arm}: {len(done)} done, {len(todo)} to go, auditor {auditor_spec}",
          flush=True)

    from crossaudit import usage
    ledger = cfg.root / cfg.state_dir / usage.LEDGER_NAME

    def spend_so_far() -> float:
        events, _ = usage.read_events(ledger)
        return sum(float(e.get("api_value_usd") or 0.0)
                   for e in events if e.get("run_id") == run_id)

    with out.open("a", encoding="utf-8") as handle:
        for index, iid in enumerate(todo, start=1):
            inst = instances[iid]
            problem = problems[inst["problem_id"]]
            solution = solutions[iid]["solution"]
            visible = scored[iid]["visible"]

            if arm == "checks":
                base = study1.deterministic_only(problem, solution, visible, cfg, arm)
                row = blank_row(arm, inst)
                for key in ("ok", "error", "verdict", "dcl_verdict", "dcl_hard_failures",
                            "model_findings", "model_blockers", "dcl_blockers", "flagged",
                            "flagged_by_model", "flagged_by_checks", "dcl_rules", "wall_s"):
                    row[key] = base[key]
                row.update({"cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0})
            elif arm in HOLISTIC_ARMS:
                before = spend_so_far()
                row = holistic_one(cfg, problem, solution, inst, constitution, run_id, arm)
                row["cost_usd"] = round(spend_so_far() - before, 6)
            elif arm == "decomposed-cross":
                row = decomposed_one(client, auditor_spec, problem, solution, inst,
                                     cache, cache_path, args.property_workers)
            else:
                row = two_stage_one(client, auditor_spec, problem, solution, inst,
                                    proposed_by_instance.get(iid, []))

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
