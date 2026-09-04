"""Score solutions against the visible and hidden suites. Model-free, parallel.

Reads a solutions JSONL (``{"problem_id", "solution"}`` per line, plus whatever else the
producer wrote) and writes one row per solution carrying both outcome vectors and the
stratum the study assigns from them:

    P  passes every visible test, fails at least one hidden test   <- "looks right, is wrong"
    C  passes both                                                  <- correct
    F  fails at least one visible test                              <- the deterministic layer sees it

``--canonical`` scores the datasets' own reference solutions instead, which validates the
harness: a reference that fails its own hidden suite means the harness is wrong, not the
solution, and the study does not proceed until that count is zero (or is enumerated and
excluded before any generation).
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import execute  # noqa: E402
from corpus import Problem, load_problems  # noqa: E402


def score_one(problem: Problem, solution: str, timeout: float) -> dict:
    visible = execute.run_suite(problem.visible_program(solution),
                                timeout=timeout,
                                instrumented=problem.visible_instrumented)
    program, instrumented = problem.hidden_program(solution)
    hidden = execute.run_suite(program, timeout=timeout, instrumented=instrumented)
    if not visible.passed:
        stratum = "F"
    elif hidden.passed:
        stratum = "C"
    else:
        stratum = "P"
    return {
        "problem_id": problem.problem_id,
        "benchmark": problem.benchmark,
        "stratum": stratum,
        "visible": visible.as_dict(),
        "hidden": hidden.as_dict(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solutions", default="", help="solutions JSONL")
    parser.add_argument("--canonical", action="store_true",
                        help="score the datasets' reference solutions (harness validation)")
    parser.add_argument("--out", required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=execute.DEFAULT_TIMEOUT)
    args = parser.parse_args(argv)

    problems = {p.problem_id: p for p in load_problems()}
    if args.canonical:
        jobs = [(p, p.canonical_solution) for p in problems.values()]
        extra: dict[str, dict] = {}
    else:
        rows = [json.loads(line) for line in
                Path(args.solutions).read_text(encoding="utf-8").splitlines() if line.strip()]
        rows = [r for r in rows if r.get("solution")]
        jobs = [(problems[r["problem_id"]], r["solution"]) for r in rows]
        extra = {r["problem_id"]: r for r in rows}

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(score_one, problem, solution, args.timeout)
                   for problem, solution in jobs]
        for index, future in enumerate(futures, start=1):
            row = future.result()
            meta = extra.get(row["problem_id"], {})
            for key in ("cost_usd", "input_tokens", "output_tokens", "wall_s",
                        "solution_sha256", "model", "prompt_sha256", "response_sha256"):
                if key in meta:
                    row[key] = meta[key]
            results.append(row)
            if index % 25 == 0:
                print(f"  {index}/{len(jobs)}", flush=True)

    results.sort(key=lambda r: r["problem_id"])
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for row in results:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    counts: dict[str, int] = {}
    for row in results:
        counts[row["stratum"]] = counts.get(row["stratum"], 0) + 1
    print(f"{len(results)} scored -> {out}")
    for stratum in ("C", "P", "F"):
        print(f"  {stratum}: {counts.get(stratum, 0)}")
    if args.canonical and (counts.get("P", 0) or counts.get("F", 0)):
        print("\nreference solutions that do not pass their own suites "
              "(harness or dataset defect, NOT a study result):")
        for row in results:
            if row["stratum"] != "C":
                print(f"  {row['problem_id']}  {row['stratum']}  "
                      f"visible={row['visible']['passed']} hidden={row['hidden']['passed']} "
                      f"{row['hidden']['error'][:120] or row['visible']['error'][:120]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
