"""Draw the audit set and write the study manifest. Runs once, before any arm.

The draw is seeded and happens before any auditor sees anything, so no arm can influence
which instances it is measured on.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import audit  # noqa: E402
import execute  # noqa: E402

CAPS = {"P": 200, "C": 150, "F": 80}
EXCLUDED = ["HumanEval/32", "Mbpp/590"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(HERE), capture_output=True,
                          text=True).stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--seed", type=int, default=20260904)
    parser.add_argument("--generator", default="anthropic:claude-haiku-4-5-20251001")
    parser.add_argument("--auditor-cross", default="openai:gpt-5.6-terra")
    args = parser.parse_args(argv)

    run_dir = Path(args.run)
    scored = [json.loads(l) for l in
              (run_dir / "scored.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    chosen = audit.choose_audit_set(scored, args.seed, CAPS)
    (run_dir / "audit_set.json").write_text(
        json.dumps({"seed": args.seed, "caps": CAPS, "problem_ids": chosen}, indent=2) + "\n",
        encoding="utf-8")

    strata: dict[str, int] = {}
    for row in scored:
        strata[row["stratum"]] = strata.get(row["stratum"], 0) + 1

    corpus = json.loads((HERE / "manifest_corpus.json").read_text(encoding="utf-8"))
    own_files = {}
    for name in sorted(p.name for p in HERE.glob("*.py")):
        own_files[name] = sha256_file(HERE / name)
    own_files["PREREGISTRATION.md"] = sha256_file(HERE / "PREREGISTRATION.md")

    executor_version = subprocess.run(
        [execute.EXECUTOR, "-c",
         "import sys,platform,numpy;print(sys.version.split()[0], platform.platform(), numpy.__version__)"],
        capture_output=True, text=True).stdout.strip()

    manifest = {
        "study": "code — does an independent model catch what the visible tests miss",
        "preregistration": "benchmarks/code/PREREGISTRATION.md",
        "code": {
            "frozen_commit": git("rev-parse", "HEAD"),
            "status_porcelain": git("status", "--porcelain"),
            "study_files_sha256": own_files,
        },
        "data": corpus,
        "excluded_problems": {
            "ids": EXCLUDED,
            "reason": "their own reference solutions fail their own hidden suites in this "
                      "harness (numerical tolerance), so 'fails a hidden test' would not "
                      "mean 'is wrong'",
            "reference_validation": "540 of 542 reference solutions pass both suites",
        },
        "models": {
            "generator": {"spec": args.generator, "role": "generator",
                          "base_url": "https://api.anthropic.com/v1",
                          "temperature": "provider-default (not settable through the "
                                         "product's provider layer)",
                          "reasoning_effort": "provider-default"},
            "auditor_cross": {"spec": args.auditor_cross, "role": "auditor",
                              "base_url": "https://api.openai.com/v1",
                              "reasoning_effort": "provider-default"},
            "auditor_self": {"spec": args.generator, "role": "auditor",
                             "base_url": "https://api.anthropic.com/v1",
                             "reasoning_effort": "provider-default"},
            "judge": None,
            "note": "no model judges any outcome in this study; ground truth is test "
                    "execution",
        },
        "sampling": {
            "seed": args.seed,
            "derivation": "solutions sorted by problem_id; stratum P taken whole; strata "
                          "C and F drawn with random.Random(seed).sample after sorting",
            "caps": CAPS,
            "strata_full": strata,
            "audit_set_size": len(chosen),
        },
        "environment": {
            "harness_python": sys.version.split()[0],
            "harness_platform": platform.platform(),
            "executor": execute.EXECUTOR,
            "executor_python_platform_numpy": executor_version,
            "test_timeout_s": execute.DEFAULT_TIMEOUT,
        },
        "times_utc": {"plan": datetime.now(timezone.utc).isoformat()},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                           encoding="utf-8")
    print(f"audit set: {len(chosen)} instances")
    for stratum in ("P", "C", "F"):
        n = sum(1 for pid in chosen
                if next(r for r in scored if r["problem_id"] == pid)["stratum"] == stratum)
        print(f"  {stratum}: {n} of {strata.get(stratum, 0)}")
    print(f"manifest -> {run_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
