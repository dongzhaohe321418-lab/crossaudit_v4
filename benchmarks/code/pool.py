"""Pool the generation batches and draw study 2's audit set. Runs once, before any arm.

Study 1's stratum P is 56 instances, which the preregistration's power table shows has only
0.36 power against a 10-point recall difference. P is ~10% of generated solutions, so more
P instances require more *solutions*, not more problems — the corpus is only 540.

An **instance** is therefore a ``(batch, problem_id)`` pair. Batch 1 is study 1's committed
solution set, reused byte-identically so that its arms remain comparable; batch 2 is a
second pass of the same frozen generator over the same problems.

The draw is seeded and happens before any auditor sees anything, so no arm can influence
which instances it is measured on. The pooling rule reads execution outcomes only and never
an audit score.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

CAPS = {"P": 10_000, "C": 150, "F": 30}   # P: take every one there is
EXCLUDED = ["HumanEval/32", "Mbpp/590"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(HERE), capture_output=True,
                          text=True).stdout.strip()


def load_batches(run_dir: Path, batches: list[str]) -> list[dict]:
    """One record per instance: batch, problem id, stratum, and the solution's hash."""
    instances: list[dict] = []
    for batch in batches:
        scored = {json.loads(l)["problem_id"]: json.loads(l)
                  for l in (run_dir / f"scored-{batch}.jsonl").read_text(
                      encoding="utf-8").splitlines() if l.strip()}
        solutions = {json.loads(l)["problem_id"]: json.loads(l)
                     for l in (run_dir / f"solutions-{batch}.jsonl").read_text(
                         encoding="utf-8").splitlines() if l.strip()}
        for pid, row in sorted(scored.items()):
            instances.append({
                "instance_id": f"{batch}:{pid}",
                "batch": batch,
                "problem_id": pid,
                "stratum": row["stratum"],
                "solution_sha256": solutions[pid].get("solution_sha256", ""),
            })
    return instances


def choose(instances: list[dict], seed: int, caps: dict[str, int]) -> list[str]:
    by_stratum: dict[str, list[str]] = {"P": [], "C": [], "F": []}
    for row in sorted(instances, key=lambda r: r["instance_id"]):
        by_stratum[row["stratum"]].append(row["instance_id"])
    chosen: list[str] = []
    rng = random.Random(seed)
    for stratum in ("P", "C", "F"):
        pool = by_stratum[stratum]
        cap = caps.get(stratum, 0)
        chosen.extend(sorted(pool) if cap >= len(pool) else sorted(rng.sample(pool, cap)))
    return sorted(chosen)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--batches", default="b1,b2")
    parser.add_argument("--seed", type=int, default=20260905)
    args = parser.parse_args(argv)

    run_dir = Path(args.run)
    batches = [b for b in args.batches.split(",") if b]
    instances = load_batches(run_dir, batches)
    chosen = choose(instances, args.seed, CAPS)
    by_id = {row["instance_id"]: row for row in instances}

    population: dict[str, int] = {}
    for row in instances:
        population[row["stratum"]] = population.get(row["stratum"], 0) + 1
    audited: dict[str, int] = {}
    for iid in chosen:
        stratum = by_id[iid]["stratum"]
        audited[stratum] = audited.get(stratum, 0) + 1

    (run_dir / "instances.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n"
                for row in sorted(instances, key=lambda r: r["instance_id"])),
        encoding="utf-8")
    (run_dir / "audit_set.json").write_text(json.dumps({
        "seed": args.seed, "caps": CAPS, "batches": batches,
        "population": population, "audited": audited,
        "weights": {s: (population[s] / audited[s]) if audited.get(s) else None
                    for s in ("P", "C", "F")},
        "instance_ids": chosen,
    }, indent=2) + "\n", encoding="utf-8")

    own = {name: sha256_file(HERE / name)
           for name in sorted(p.name for p in HERE.glob("*.py"))}
    corpus = json.loads((HERE / "manifest_corpus.json").read_text(encoding="utf-8"))
    (run_dir / "manifest.json").write_text(json.dumps({
        "study": "study2-architectures",
        "frozen_sha": git("rev-parse", "HEAD"),
        "git_status_porcelain": git("status", "--porcelain"),
        "prereg": "benchmarks/code/PREREGISTRATION-2.md",
        "seed": args.seed,
        "batches": batches,
        "batch_1_provenance": "study 1's committed solutions, reused byte-identically",
        "generator": "anthropic:claude-haiku-4-5-20251001",
        "auditor_cross": "openai:gpt-5.6-terra",
        "auditor_self": "anthropic:claude-haiku-4-5-20251001",
        "excluded_problems": EXCLUDED,
        "population": population,
        "audited": audited,
        "harness_files": own,
        "corpus": corpus,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "planned_utc": datetime.now(timezone.utc).isoformat(),
    }, indent=2) + "\n", encoding="utf-8")

    print(f"instances {len(instances)} over batches {batches}")
    for stratum in ("P", "C", "F"):
        print(f"  {stratum}: population {population.get(stratum,0)}  "
              f"audited {audited.get(stratum,0)}  "
              f"weight {population.get(stratum,0)/max(audited.get(stratum,1),1):.2f}")
    print(f"audit set {len(chosen)} instances -> {run_dir/'audit_set.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
