"""Study 8 — assemble the reading material for the residual classification (§1.5).

The residual is every stratum-P instance that **no draw of any family ever flagged**.
Classifying it is the one hand step in this study, and the categories were fixed in the
preregistration before the first residual instance was read.

This script only assembles evidence; it decides nothing. For each residual instance it
writes the specification, the visible suite, the candidate solution, the dataset's own
canonical solution, and which hidden inputs failed and with what values — and, so the
classification is checkable rather than merely asserted, it re-runs the failing hidden
inputs through ``execute.py``'s sandbox to recover the expected and actual values.

Output goes to the run directory, not the repository: it contains corpus text and full
candidate solutions. The **classification** that comes out of reading it — instance id,
category, one phrase — is what gets committed, in
``records/ceiling/residual_classification.json``.

    python benchmarks/code/residual_dump.py --run <run-dir>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import execute  # noqa: E402
import report_ceiling as rc  # noqa: E402
from corpus import load_problems  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--population", default="three_families_all_P")
    args = parser.parse_args(argv)

    numbers_path = rc.CEILING / "numbers.json"
    if not numbers_path.exists():
        raise SystemExit("run report_ceiling.py first")
    numbers = json.loads(numbers_path.read_text(encoding="utf-8"))
    residual = numbers["ceiling1"]["residual"].get(args.population)
    if not residual:
        raise SystemExit(f"no residual population named {args.population!r}")
    ids = residual["instance_ids"]
    print(f"{len(ids)} residual instances "
          f"({', '.join(residual['families'])}, {residual['total_draws']} draws)")

    run_dir = Path(args.run)
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

    out_dir = run_dir / "residual"
    out_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for iid in ids:
        batch, problem_id = iid.split(":", 1)
        problem = problems[problem_id]
        solution = solutions[iid]["solution"]
        hidden = scored[iid]["hidden"]
        # Recover the failing inputs and the values, so the category rests on evidence.
        witness = witness_for(problem, solution, hidden)
        record = {
            "instance_id": iid, "benchmark": problem.benchmark,
            "hidden_total": hidden.get("total"), "hidden_mode": hidden.get("mode"),
            "hidden_timed_out": hidden.get("timed_out"),
            "hidden_error": hidden.get("error", "")[:400],
            "hidden_failed_n": len(hidden.get("failed_indices") or []),
            "hidden_failed_indices": (hidden.get("failed_indices") or [])[:20],
            "witness": witness,
        }
        index.append(record)
        (out_dir / f"{iid.replace('/', '_').replace(':', '_')}.txt").write_text(
            "\n\n".join([
                f"=== {iid}  ({problem.benchmark}) ===",
                f"--- hidden outcome ---\n{json.dumps(record, indent=2)[:4000]}",
                f"--- specification ---\n{problem.spec}",
                f"--- visible suite ---\n{problem.visible_tests_text()}",
                f"--- candidate solution ---\n{solution}",
                f"--- dataset canonical solution ---\n{problem.canonical_solution}",
            ]), encoding="utf-8")
    (out_dir / "index.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {len(index)} files to {out_dir}")
    return 0


def witness_for(problem, solution: str, hidden: dict) -> dict:
    """The first failing hidden input, with the expected and the actual value.

    Runs in ``execute.py``'s subprocess sandbox — candidate code is untrusted and is never
    imported into this interpreter. Where the suite is not the instrumented EvalPlus shape
    (``mode == "binary"``) there is no per-input vector to recover and the witness says so
    rather than inventing one.
    """
    failed = hidden.get("failed_indices") or []
    if hidden.get("timed_out"):
        return {"kind": "timeout", "detail": "the hidden suite did not terminate"}
    if hidden.get("mode") != "vector" or not failed:
        return {"kind": "no_vector",
                "detail": f"mode={hidden.get('mode')}, "
                          f"error={(hidden.get('error') or '')[:200]}"}
    program, instrumented = problem.hidden_program(solution)
    if not instrumented:
        return {"kind": "no_vector", "detail": "suite is not the instrumented shape"}
    probe = program + f"""

import json as __j, sys as __s
__w = []
for __i in {failed[:5]!r}:
    try:
        __inp = inputs[__i]
        __exp = results[__i]
        try:
            __act = {problem.entry_point}(*__inp)
        except BaseException as __e:
            __act = f"<raised {{type(__e).__name__}}: {{__e}}>"
        __w.append({{"index": __i, "input": repr(__inp)[:400],
                     "expected": repr(__exp)[:400], "actual": repr(__act)[:400]}})
    except BaseException as __e:
        __w.append({{"index": __i, "error": f"{{type(__e).__name__}}: {{__e}}"}})
__s.stderr.write("__CROSSAUDIT_WITNESS__" + __j.dumps(__w) + "\\n")
"""
    code, _out, err, timed = execute._run(probe, execute.DEFAULT_TIMEOUT)
    if timed:
        return {"kind": "timeout", "detail": "witness probe timed out"}
    for line in err.splitlines():
        if line.startswith("__CROSSAUDIT_WITNESS__"):
            try:
                return {"kind": "vector",
                        "cases": json.loads(line[len("__CROSSAUDIT_WITNESS__"):])}
            except json.JSONDecodeError:
                break
    return {"kind": "probe_failed", "detail": err[-400:]}


if __name__ == "__main__":
    raise SystemExit(main())
