"""Generate one solution per problem, once, with the generator model.

Every arm judges these same solutions. Regenerating per arm would make the arms
incomparable — a difference between them could then be generation variance, which is the
exact confound that made study 1's headline meaningless.

The generator is shown the problem specification and nothing else: not the visible test
suite as an executable artefact, not the hidden suite, not a rubric, not the constitution.
Its prompt is a plain "write this function", because the object of study is the auditor,
and a generator prompt tuned for the audit would be tuning the population.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "expertlongbench"))

from corpus import Problem, load_problems  # noqa: E402

SYSTEM = (
    "You are an expert Python programmer. You write correct, complete, self-contained "
    "solutions.\n\n"
    "Reply with exactly one fenced Python code block and no other text. The block must "
    "contain the complete solution — every import it needs and the full function "
    "definition — so that it runs as written."
)

USER_HUMANEVAL = (
    "Complete this Python function. Reproduce the signature and the docstring exactly, "
    "then write the body.\n\n```python\n{spec}\n```"
)

USER_MBPP = "Write a Python function for this task.\n\n{spec}"

_FENCE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.S)


def extract_code(text: str) -> str:
    """The last fenced block, or the whole reply if it is unfenced.

    Deterministic and stated in advance: a reply that ignores the format is not silently
    dropped (that would quietly select for compliant models), it is taken as written and
    scored — usually as a syntax error, which is a real failure of the generator.
    """
    blocks = _FENCE.findall(text)
    if blocks:
        return blocks[-1].strip("\n")
    return text.strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def user_prompt(problem: Problem) -> str:
    template = USER_HUMANEVAL if problem.benchmark == "humaneval" else USER_MBPP
    return template.format(spec=problem.spec.rstrip())


def generate_one(client, model: str, problem: Problem) -> dict:
    user = user_prompt(problem)
    started = time.monotonic()
    row = {
        "problem_id": problem.problem_id,
        "benchmark": problem.benchmark,
        "model": model,
        "prompt_sha256": sha256_text(SYSTEM + "\n" + user),
    }
    try:
        completion = client.complete(model=model, system=SYSTEM, user=user)
    except Exception as exc:  # noqa: BLE001 - recorded, never swallowed
        row.update({"solution": "", "error": f"{type(exc).__name__}: {exc}",
                    "wall_s": time.monotonic() - started})
        return row
    code = extract_code(completion.text)
    row.update({
        "solution": code,
        "solution_sha256": sha256_text(code),
        "response_sha256": sha256_text(completion.text),
        "wall_s": time.monotonic() - started,
        "cost_usd": completion.cost_usd,
        "input_tokens": completion.input_tokens,
        "output_tokens": completion.output_tokens,
        "error": "",
    })
    return row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="anthropic:claude-haiku-4-5-20251001")
    parser.add_argument("--out", required=True)
    parser.add_argument("--exclude", default="", help="comma-separated problem ids to skip")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--project", required=True,
                        help="a crossaudit project dir supplying the config and usage ledger")
    args = parser.parse_args(argv)

    from run import load_credentials  # expertlongbench harness
    load_credentials()
    from crossaudit.config import load
    from provider import CrossAuditClient

    cfg = load(Path(args.project) / "crossaudit.yml")
    run_id = args.run_id or f"gen-{int(time.time())}"
    client = CrossAuditClient(cfg=cfg, phase="code-generation", run_id=run_id)

    excluded = {p for p in args.exclude.split(",") if p}
    problems = [p for p in load_problems() if p.problem_id not in excluded]
    if args.limit:
        problems = problems[: args.limit]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done: set[str] = set()
    if out.exists():
        done = {json.loads(line)["problem_id"]
                for line in out.read_text(encoding="utf-8").splitlines() if line.strip()}
        problems = [p for p in problems if p.problem_id not in done]
        print(f"resuming: {len(done)} already generated, {len(problems)} to go")

    spend = 0.0
    with out.open("a", encoding="utf-8") as handle, \
            ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(generate_one, client, args.model, p) for p in problems]
        for index, future in enumerate(futures, start=1):
            row = future.result()
            spend += float(row.get("cost_usd") or 0.0)
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            handle.flush()
            if index % 25 == 0 or index == len(futures):
                print(f"  {index}/{len(futures)}  spend ${spend:.3f}", flush=True)
    print(f"generation spend ${spend:.4f} over {len(problems)} problems; run_id {run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
