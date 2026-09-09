"""Study 16 — a test-generating auditor against the reading auditor.

Preregistered in ``testgen/PREREGISTRATION.md`` (with Amendment 1) before any model call
and before this module existed. The question is an architecture's, not a matcher's: does an
auditor that WRITES tests from the visible specification and RUNS them against the
candidate find defects the reading auditors (study 7's front, D162's ceiling) do not?

    testgen              one generation call per PROBLEM; every candidate to that problem
                         meets the identical suite; flag = at least one generated test
                         fails on the candidate
    testgen-validated    the same suite with every test that fails on the CANONICAL
                         solution dropped first — an oracle the product does not have, so
                         an UPPER BOUND, never a product number
    hc                   the shipped reading auditor, from study 7's records; no new call
    hc_u_testgen         the union over records; no new call

Ground truth, the split, the instances and the objective are study 7's, frozen
(``records/explore/split.json``, ``records/study2/instances.jsonl``,
``explore/PREREGISTRATION.md`` §5). The information boundary is ``architectures.py``'s:
the generator receives ``problem.spec`` and ``problem.visible_tests_text()`` as plain
strings; the hidden suite is unreachable by construction, and ``tests/test_architectures.py``
proves it for this prompt as for the others.

Generated tests are executed with ``execute.py`` unchanged — a subprocess with a wall-clock
timeout and a fresh cwd. Nothing in this module imports candidate code.

    python benchmarks/code/testgen.py run --run <dir with solutions-*.jsonl> \
        --scratch /tmp/testgen --budget-usd 5
    python benchmarks/code/testgen.py report
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "expertlongbench"))

import architectures as arch  # noqa: E402
import execute  # noqa: E402
import explore  # noqa: E402
from corpus import Problem, load_problems  # noqa: E402
from report_ceiling import cluster_bootstrap_ci, signflip_p  # noqa: E402

RECORDS = HERE / "records" / "testgen"
SUITES = RECORDS / "suites.json"          # per-problem shapes: counts, hashes, cost — no text
ROWS = RECORDS / "rows.jsonl"             # per-instance outcomes
NUMBERS = RECORDS / "numbers.json"
MANIFEST = RECORDS / "manifest.json"

#: Study 7's shipped detector, the comparator. Its records are read, never re-run.
HC_KEY = ("holistic", "cross", 1)
#: The generator's route is the comparator's: the model is held fixed, the structure varies.
MODEL_SPEC = explore.ROUTES["cross"]
#: Amendment 1.
BOOTSTRAP_SEED = 20260909
BOOTSTRAP_REPS = 10_000
FP_CONSTRAINT = 0.067          # explore/PREREGISTRATION.md §5, unchanged
TIMEOUT_S = execute.DEFAULT_TIMEOUT


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------------
# generation — once per problem, cached with its text OUTSIDE the records
# ---------------------------------------------------------------------------------

def suite_for(client, problem: Problem, cache: dict, cache_path: Path) -> tuple[list[str], dict]:
    """The generated suite of a problem: strings in, one call, cached by problem id.

    ``cache`` holds the test text and lives in the run directory (the archive), not in
    ``records/``. What ``records/suites.json`` keeps is the shape: counts, hashes, cost.
    """
    pid = problem.problem_id
    if pid in cache:
        entry = cache[pid]
        return entry["tests"], {"cached": True, "cost_usd": 0.0, "input_tokens": 0,
                                "output_tokens": 0, "wall_s": 0.0,
                                "n_uncompilable": entry["n_uncompilable"],
                                "n_parsed": entry["n_parsed"],
                                "prompt_sha256": entry["prompt_sha256"],
                                "response_sha256": entry["response_sha256"]}
    system, user = arch.testgen_prompt(problem.spec, problem.visible_tests_text())
    started = time.monotonic()
    completion = client.complete(model=MODEL_SPEC, system=system, user=user)
    parsed = arch.parse_tests(completion.text)
    tests, dropped = arch.compilable(parsed)
    meta = {"cached": False, "cost_usd": float(completion.cost_usd),
            "input_tokens": int(completion.input_tokens),
            "output_tokens": int(completion.output_tokens),
            "wall_s": time.monotonic() - started,
            "n_uncompilable": dropped, "n_parsed": len(parsed),
            "prompt_sha256": sha256_text(system + "\n" + user),
            "response_sha256": sha256_text(completion.text)}
    cache[pid] = {"tests": tests, "n_parsed": len(parsed), "n_uncompilable": dropped,
                  "prompt_sha256": meta["prompt_sha256"],
                  "response_sha256": meta["response_sha256"],
                  "cost_usd": meta["cost_usd"], "input_tokens": meta["input_tokens"],
                  "output_tokens": meta["output_tokens"], "model": completion.model}
    cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return tests, meta


# ---------------------------------------------------------------------------------
# execution — the generated suite around a solution, per-test failure vector
# ---------------------------------------------------------------------------------

def run_generated(solution: str, imports: list[str], tests: list[str]) -> dict:
    """Run every generated test separately against ``solution``; report which failed.

    ``execute.mbpp_visible`` already assembles exactly this program shape — each source
    string attempted in its own try/except, failures reported as indices — so it is reused
    for both benchmarks. An empty suite runs nothing and fails nothing.
    """
    if not tests:
        return {"failed": [], "timed_out": False, "total": 0, "wall_s": 0.0, "error": ""}
    program = execute.mbpp_visible(solution, imports, tests)
    result = execute.run_suite(program, timeout=TIMEOUT_S, instrumented=True)
    if result.timed_out:
        return {"failed": list(range(len(tests))), "timed_out": True, "total": len(tests),
                "wall_s": result.wall_s, "error": "timeout"}
    if result.mode != "vector":
        # The program died before the collector ran (an import the candidate needs is
        # missing, say). Every test counts as failed: the candidate cannot be exercised.
        return {"failed": list(range(len(tests))), "timed_out": False, "total": len(tests),
                "wall_s": result.wall_s, "error": (result.error or "")[:200]}
    return {"failed": sorted(result.failed_indices), "timed_out": False, "total": result.total,
            "wall_s": result.wall_s, "error": ""}


def judge(tests: list[str], candidate: dict, canonical: dict) -> dict:
    """The two arms' flags from the two runs. Pure; tested."""
    n = len(tests)
    failed_candidate = set(candidate["failed"])
    flagged = bool(failed_candidate) or bool(candidate["timed_out"])
    if canonical["timed_out"]:
        # The oracle cannot be consulted; the validated arm does not flag (Amendment 1).
        return {"flagged_testgen": flagged, "flagged_validated": False,
                "n_dropped_by_validation": n, "n_validated": 0, "canonical_unusable": True}
    wrong = set(canonical["failed"])              # tests the canonical solution fails
    surviving = [i for i in range(n) if i not in wrong]
    flagged_validated = any(i in failed_candidate for i in surviving) or bool(candidate["timed_out"])
    return {"flagged_testgen": flagged, "flagged_validated": flagged_validated and bool(surviving),
            "n_dropped_by_validation": len(wrong), "n_validated": len(surviving),
            "canonical_unusable": False}


# ---------------------------------------------------------------------------------
# the run
# ---------------------------------------------------------------------------------

def load_rows() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    if ROWS.exists():
        for line in ROWS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                rows[row["instance_id"]] = row
    return rows


def run(args) -> int:
    from run import load_credentials
    from provider import CrossAuditClient
    from crossaudit.config import load
    import audit as study1

    instances = explore.load_instances()
    audit_set = explore.load_audit_set()
    audit_ids = set(audit_set)
    split = json.loads((explore.EXPLORE / "split.json").read_text(encoding="utf-8"))
    halves = split["halves"]
    wanted = [i for i in audit_set if args.half == "all" or halves[i] == args.half]
    have = load_rows()
    todo = [i for i in wanted if i not in have]
    problems = {p.problem_id: p for p in load_problems()}
    run_dir = Path(args.run)
    solutions: dict[str, dict] = {}
    for batch in sorted({inst["batch"] for inst in instances.values()}):
        for line in (run_dir / f"solutions-{batch}.jsonl").read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                solutions[f"{batch}:{row['problem_id']}"] = row
    hc = explore.load_detector(HC_KEY, audit_ids)
    cache_path = run_dir / "generated_tests.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    need_calls = sorted({instances[i]["problem_id"] for i in todo} - set(cache))
    print(f"{args.half}: {len(wanted)} instances, {len(todo)} without a row, "
          f"{len(need_calls)} problems need a generation call "
          f"({len(cache)} suites cached)", flush=True)
    if args.dry_run:
        return 0

    RECORDS.mkdir(parents=True, exist_ok=True)
    load_credentials()
    study1.register_visible_tests_check()
    scratch = Path(args.scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    project = explore.build_project(scratch, HC_KEY, study1.shipped_constitution())
    cfg = load(project / "crossaudit.yml")
    client = CrossAuditClient(cfg=cfg, phase="testgen", run_id="testgen")
    spend = {"usd": 0.0}
    lock = threading.Lock()
    halted = threading.Event()

    # Generation first — one call per problem — P before C before F, so a budget halt
    # truncates the secondary strata, as in study 7.
    priority = {"P": 0, "C": 1, "F": 2}
    order = sorted(need_calls, key=lambda pid: (
        min(priority[instances[i]["stratum"]] for i in todo if instances[i]["problem_id"] == pid), pid))

    # One call per problem; the cache write and the spend tally are serialised by the lock.
    def generate_locked(pid: str) -> str | None:
        if halted.is_set():
            return None
        try:
            with lock:
                if pid in cache:
                    return pid
            system, user = arch.testgen_prompt(problems[pid].spec, problems[pid].visible_tests_text())
            started = time.monotonic()
            completion = client.complete(model=MODEL_SPEC, system=system, user=user)
            parsed = arch.parse_tests(completion.text)
            tests, dropped = arch.compilable(parsed)
            with lock:
                cache[pid] = {"tests": tests, "n_parsed": len(parsed), "n_uncompilable": dropped,
                              "prompt_sha256": sha256_text(system + "\n" + user),
                              "response_sha256": sha256_text(completion.text),
                              "cost_usd": float(completion.cost_usd),
                              "input_tokens": int(completion.input_tokens),
                              "output_tokens": int(completion.output_tokens),
                              "model": completion.model,
                              "wall_s": round(time.monotonic() - started, 3)}
                cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n",
                                      encoding="utf-8")
                spend["usd"] += float(completion.cost_usd)
                if args.budget_usd and spend["usd"] >= args.budget_usd:
                    print(f"    STOP: spend ${spend['usd']:.3f} reached the "
                          f"${args.budget_usd:.2f} cap", flush=True)
                    halted.set()
        except Exception as exc:  # noqa: BLE001
            with lock:
                with (RECORDS / "generation.failed.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({"problem_id": pid,
                                             "error": f"{type(exc).__name__}: {exc}"[:300]}) + "\n")
            return None
        return pid

    for attempt in range(1, args.max_passes + 1):
        pending = [pid for pid in order if pid not in cache]
        if not pending or halted.is_set():
            break
        if attempt > 1:
            print(f"    pass {attempt}: {len(pending)} problems still without a suite; "
                  f"waiting 75s for the breaker to close", flush=True)
            time.sleep(75)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for done, _ in enumerate(pool.map(generate_locked, pending), start=1):
                if done % 20 == 0 or done == len(pending):
                    print(f"    generated {done}/{len(pending)}  ${spend['usd']:.3f}", flush=True)
    print(f"generation spend this invocation: ${spend['usd']:.4f}", flush=True)

    # Execution — no model, no spend. Every instance whose problem has a suite.
    executed = 0
    with ROWS.open("a", encoding="utf-8") as handle:
        for iid in todo:
            inst = instances[iid]
            pid = inst["problem_id"]
            if pid not in cache:
                continue
            problem = problems[pid]
            tests = cache[pid]["tests"]
            imports = problem.test_imports()
            started = time.monotonic()
            candidate = run_generated(solutions[iid]["solution"], imports, tests)
            canonical = run_generated(problem.canonical_solution, imports, tests)
            verdict = judge(tests, candidate, canonical)
            row = {"instance_id": iid, "problem_id": pid, "batch": inst["batch"],
                   "stratum": inst["stratum"], "half": halves[iid],
                   "n_parsed": cache[pid]["n_parsed"], "n_uncompilable": cache[pid]["n_uncompilable"],
                   "n_tests": len(tests),
                   "failed_candidate": candidate["failed"], "candidate_timed_out": candidate["timed_out"],
                   "candidate_error": candidate["error"],
                   "failed_canonical": canonical["failed"], "canonical_timed_out": canonical["timed_out"],
                   "hc_flagged": (bool(hc[iid]["flagged"]) if iid in hc else None),
                   "wall_s": round(time.monotonic() - started, 3),
                   "suite_response_sha256": cache[pid]["response_sha256"]}
            row.update(verdict)
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            handle.flush()
            executed += 1
    print(f"executed {executed} instances", flush=True)

    shapes = {pid: {k: v for k, v in entry.items() if k != "tests"} | {"n_tests": len(entry["tests"])}
              for pid, entry in cache.items()}
    SUITES.write_text(json.dumps(shapes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# ---------------------------------------------------------------------------------
# the report — the preregistered objective, applied and nothing else
# ---------------------------------------------------------------------------------

ARMS = ("testgen", "testgen-validated", "hc", "hc_u_testgen")


def arm_flag(arm: str, row: dict) -> bool | None:
    if arm == "testgen":
        return bool(row["flagged_testgen"])
    if arm == "testgen-validated":
        return bool(row["flagged_validated"])
    if arm == "hc":
        return row["hc_flagged"]
    if arm == "hc_u_testgen":
        return None if row["hc_flagged"] is None else bool(row["hc_flagged"] or row["flagged_testgen"])
    raise ValueError(arm)


def rate(rows: list[dict], flag_of) -> dict:
    flags = [flag_of(r) for r in rows]
    flags = [f for f in flags if f is not None]
    k, n = sum(1 for f in flags if f), len(flags)
    lo, hi = explore.wilson(k, n) if n else (None, None)
    by_cluster: dict[str, list[float]] = {}
    for r in rows:
        f = flag_of(r)
        if f is not None:
            by_cluster.setdefault(r["problem_id"], []).append(1.0 if f else 0.0)
    blo, bhi = cluster_bootstrap_ci(by_cluster, BOOTSTRAP_REPS, BOOTSTRAP_SEED)
    return {"k": k, "n": n, "rate": (k / n if n else None),
            "wilson": [lo, hi], "bootstrap_problem_cluster": [blo, bhi]}


def residual_classes() -> dict[str, str]:
    """instance_id -> the ceiling study's residual category, where it classified one."""
    path = HERE / "records" / "ceiling" / "residual_classification.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {iid: str(item["category"])
            for iid, item in data.get("classification", {}).items() if item.get("category")}


def report(args) -> int:
    rows = list(load_rows().values())
    if not rows:
        print("no rows; run first")
        return 1
    out: dict = {"n_rows": len(rows), "bootstrap": {"seed": BOOTSTRAP_SEED, "reps": BOOTSTRAP_REPS,
                                                      "unit": "problem"},
                 "objective": {"from": "explore/PREREGISTRATION.md §5 — highest confirm P-recall "
                                       "with confirm C-false-positive rate <= 6.7%",
                               "fp_constraint": FP_CONSTRAINT}, "arms": {}}
    for arm in ARMS:
        entry: dict = {}
        for half in ("confirm", "explore", "all"):
            sub = [r for r in rows if half == "all" or r["half"] == half]
            entry[half] = {s: rate([r for r in sub if r["stratum"] == s], lambda r, a=arm: arm_flag(a, r))
                           for s in ("P", "C", "F")}
        out["arms"][arm] = entry

    # The decision, on the confirm half (§3): testgen's P-recall above hc's, at an FP rate
    # within the constraint plus one instance.
    conf = [r for r in rows if r["half"] == "confirm"]
    c_n = out["arms"]["testgen"]["confirm"]["C"]["n"]
    fp_bar_k = int(FP_CONSTRAINT * c_n) + 1 if c_n else 0
    tg, hc_ = out["arms"]["testgen"]["confirm"], out["arms"]["hc"]["confirm"]
    within = tg["C"]["k"] <= fp_bar_k
    above = tg["P"]["k"] > hc_["P"]["k"] if (tg["P"]["n"] and hc_["P"]["n"]) else False
    # Paired: P instances flagged by testgen and not hc, and the reverse (exact McNemar).
    b = sum(1 for r in conf if r["stratum"] == "P" and r["flagged_testgen"] and r["hc_flagged"] is False)
    c = sum(1 for r in conf if r["stratum"] == "P" and not r["flagged_testgen"] and r["hc_flagged"])
    # Cluster-aware sensitivity beside the instance-level McNemar (EXPERIMENT_RECORD §9): the
    # per-instance signed change testgen − hc on P, bootstrapped and sign-flipped by problem.
    signed: dict[str, list[float]] = {}
    for r in conf:
        if r["stratum"] == "P" and r["hc_flagged"] is not None:
            signed.setdefault(r["problem_id"], []).append(
                float(bool(r["flagged_testgen"])) - float(bool(r["hc_flagged"])))
    d_lo, d_hi = cluster_bootstrap_ci(signed, BOOTSTRAP_REPS, BOOTSTRAP_SEED)
    out["decision"] = {
        "fp_objective_max_instances": int(FP_CONSTRAINT * c_n) if c_n else 0,
        "fp_bar_instances": fp_bar_k, "testgen_within_fp_bar": within,
        "testgen_recall_above_hc": above,
        "H16": ("HOLDS" if (within and above) else
                "KILL: false positives" if not within else "KILL: recall"),
        "paired_P_testgen_only": b, "paired_P_hc_only": c,
        "mcnemar_exact_p": explore.mcnemar_exact(b, c),
        "delta_recall_points": (100 * (tg["P"]["k"] - hc_["P"]["k"]) / tg["P"]["n"]) if tg["P"]["n"] else None,
        "delta_recall_problem_cluster_bootstrap_points": [100 * d_lo, 100 * d_hi],
        "delta_recall_signflip": signflip_p(signed)}

    # Secondaries.
    suites = json.loads(SUITES.read_text(encoding="utf-8")) if SUITES.exists() else {}
    per_problem = {pid: s for pid, s in suites.items()}
    n_tests = [s["n_tests"] for s in per_problem.values()]
    n_unc = [s["n_uncompilable"] for s in per_problem.values()]
    dropped = [r["n_dropped_by_validation"] for r in rows if not r["canonical_unusable"]]
    total_tests = sum(r["n_tests"] for r in rows if not r["canonical_unusable"])
    # unique tests: one suite per problem; a test is wrong once, however many candidates
    wrong_by_problem: dict[str, set] = {}
    unusable_problems = {r["problem_id"] for r in rows if r["canonical_unusable"]}
    for r in rows:
        if not r["canonical_unusable"]:
            wrong_by_problem.setdefault(r["problem_id"], set()).update(r["failed_canonical"])
    classifiable = {pid: s["n_tests"] for pid, s in per_problem.items() if pid not in unusable_problems}
    n_unique_classifiable = sum(classifiable.values())
    n_unique_wrong = sum(len(v) for v in wrong_by_problem.values())
    n_unique_unknown = sum(s["n_tests"] for pid, s in per_problem.items() if pid in unusable_problems)
    w_lo, w_hi = explore.wilson(n_unique_wrong, n_unique_classifiable) if n_unique_classifiable else (None, None)
    wb_lo, wb_hi = cluster_bootstrap_ci(
        {pid: [1.0 if i in wrong_by_problem.get(pid, set()) else 0.0 for i in range(n)]
         for pid, n in classifiable.items() if n}, BOOTSTRAP_REPS, BOOTSTRAP_SEED)
    classes = residual_classes()
    flagged_p = [r for r in conf if r["stratum"] == "P" and r["flagged_testgen"]]
    testgen_only = [r for r in flagged_p if r["hc_flagged"] is False]
    validated_only = [r for r in conf if r["stratum"] == "P" and r["flagged_validated"] and r["hc_flagged"] is False]
    out["secondaries"] = {
        "problems_with_suite": len(per_problem),
        "tests_per_problem": {"mean": (sum(n_tests) / len(n_tests) if n_tests else None),
                              "min": min(n_tests, default=None), "max": max(n_tests, default=None),
                              "zero": sum(1 for x in n_tests if x == 0)},
        "uncompilable_total": sum(n_unc),
        "wrong_tests": {"dropped_by_validation_instance_rows": sum(dropped),
                        "of_test_applications": total_tests,
                        "unique_wrong": n_unique_wrong, "unique_classifiable": n_unique_classifiable,
                        "unique_unknown_canonical_timed_out": n_unique_unknown,
                        "unique_rate": (n_unique_wrong / n_unique_classifiable if n_unique_classifiable else None),
                        "unique_wilson": [w_lo, w_hi],
                        "unique_bootstrap_problem_cluster": [wb_lo, wb_hi],
                        "problems_with_a_wrong_test": sum(1 for v in wrong_by_problem.values() if v),
                        "note": "tests that fail on the canonical solution; the false-positive mechanism named in §1"},
        "canonical_unusable_rows": sum(1 for r in rows if r["canonical_unusable"]),
        "candidate_timeouts": sum(1 for r in rows if r["candidate_timed_out"]),
        "candidate_died_before_collector": sum(1 for r in rows if r["candidate_error"] and not r["candidate_timed_out"]),
        "confirm_P_flagged_by_testgen_and_hc": sum(1 for r in flagged_p if r["hc_flagged"]),
        "confirm_P_flagged_by_testgen_only": b,
        "confirm_P_testgen_only_by_residual_class": _count_by(
            [classes.get(r["instance_id"], "unclassified") for r in testgen_only]),
        "confirm_P_validated_only": len(validated_only),
        "confirm_P_validated_only_by_residual_class": _count_by(
            [classes.get(r["instance_id"], "unclassified") for r in validated_only]),
        "confirm_P_not_flagged_by_hc_by_residual_class": _count_by(
            [classes.get(r["instance_id"], "unclassified") for r in conf if r["stratum"] == "P" and r["hc_flagged"] is False]),
        "confirm_P_residual_classes_available": len(classes),
        "cost_usd_generation_total": round(sum(float(s.get("cost_usd", 0.0)) for s in per_problem.values()), 6),
        "cost_usd_per_instance_amortised": (round(sum(float(s.get("cost_usd", 0.0)) for s in per_problem.values()) / len(rows), 6) if rows else None),
        "hc_cost_usd_per_instance_explore_leaderboard": _hc_cost(),
    }
    if out["secondaries"]["hc_cost_usd_per_instance_explore_leaderboard"]:
        out["secondaries"]["cost_ratio_testgen_over_hc"] = round(
            out["secondaries"]["cost_usd_per_instance_amortised"]
            / out["secondaries"]["hc_cost_usd_per_instance_explore_leaderboard"], 4)
    NUMBERS.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for arm in ARMS:
        e = out["arms"][arm]["confirm"]
        print(f"{arm:18s} confirm P {e['P']['k']:3d}/{e['P']['n']:3d} "
              f"({_pct(e['P'])})   C {e['C']['k']:3d}/{e['C']['n']:3d} ({_pct(e['C'])})")
    print(f"\nH16: {out['decision']['H16']}   (FP bar {fp_bar_k} instances; "
          f"testgen-only P {b}, hc-only P {c}, McNemar p={out['decision']['mcnemar_exact_p']:.3f})")
    w = out["secondaries"]["wrong_tests"]
    print(f"wrong tests (unique): {w['unique_wrong']}/{w['unique_classifiable']} "
          f"(+{w['unique_unknown_canonical_timed_out']} unknown); "
          f"uncompilable {out['secondaries']['uncompilable_total']}; "
          f"generation ${out['secondaries']['cost_usd_generation_total']:.3f}")
    return 0


def _hc_cost() -> float | None:
    """The shipped auditor's per-instance cost as the explore leaderboard recorded it."""
    path = explore.EXPLORE / "leaderboard.jsonl"
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("spec_id") == "hc":
                return float(row["cost_usd_per_instance"])
    return None


def _count_by(values: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return dict(sorted(out.items()))


def _pct(block: dict) -> str:
    if block["rate"] is None:
        return "n/a"
    lo, hi = block["wilson"]
    return f"{100 * block['rate']:.1f}% W {100 * lo:.1f}–{100 * hi:.1f}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--run", required=True, help="dir with solutions-*.jsonl; the suite cache is written here")
    r.add_argument("--scratch", default="/tmp/testgen")
    r.add_argument("--budget-usd", type=float, default=5.0)
    r.add_argument("--workers", type=int, default=3)
    r.add_argument("--max-passes", type=int, default=4)
    r.add_argument("--half", choices=("confirm", "explore", "all"), default="all")
    r.add_argument("--dry-run", action="store_true")
    sub.add_parser("report")
    args = parser.parse_args(argv)
    return run(args) if args.cmd == "run" else report(args)


if __name__ == "__main__":
    raise SystemExit(main())
