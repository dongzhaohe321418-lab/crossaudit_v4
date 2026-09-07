#!/usr/bin/env python3
"""Study 8 — Arm 5: the shipped check and the shipped skill, after the containment
extensions, on every T03 instance.

Preregistered at `study8/PREREGISTRATION-ARM5.md`, committed before any model
call. Everything Arm 4 did (`provenance_arm4.py`: the product's own skill,
contract sentence and per-row verifier on the audited increment, nothing under
`src/` modified, nothing in the prompt wrapped) with three declared changes:
the matcher is the one that ships after slices 4–8 (E5, E6, E1, E2, E3; M10
measured and not shipped); the sample is ALL 50 corpus rows — the 26 of Arm 4
as a replicate under the changed matcher and the 24 of Arms 2–3 as instances
the shipped skill has not seen (D161 ruling 3's second option, said so); the
budget is $5.00.

    export PYTHONPATH=<worktree>/src
    set -a && . ~/.crossaudit-keys.env && set +a
    python3 benchmarks/expertlongbench/provenance_arm5.py --dry-run --out <abs>
    python3 benchmarks/expertlongbench/provenance_arm5.py --out <abs>
    python3 benchmarks/expertlongbench/provenance_arm5.py --reanalyse --out <abs>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "src"))

import run as run_mod                                              # noqa: E402
import provenance_arm4 as arm4                                     # noqa: E402
from run import (OUTPUT_PATH, Options, SCOPE_DIR, INCREMENT_DIR,   # noqa: E402
                 RECIPE_PATH, load_task_rows, load_credentials, verify_corpus)
from crossaudit.dcl import describe                                # noqa: E402
from crossaudit.dcl.framework import BLOCKER                       # noqa: E402

GENERATOR = arm4.GENERATOR
AUDITOR = arm4.AUDITOR
CHECKS_LIST = arm4.CHECKS_LIST
CHECKS_YAML = arm4.CHECKS_YAML
ARM = arm4.ARM                       # "S": the shipped configuration, as in Arm 4
BUDGET_USD = 5.00
BOOT_SEED = 20261107
MANIFEST_ARM3 = HERE / "study8" / "manifest.json"
MANIFEST_ARM4 = HERE / "study8" / "manifest-arm4.json"


def all_rows(task_id: str) -> list[dict]:
    """Every corpus row, in corpus order; no selection and no seed."""
    return list(load_task_rows(task_id))


def earlier_ids() -> dict[str, list[str]]:
    arm3 = json.loads(MANIFEST_ARM3.read_text(encoding="utf-8"))["instance_ids"]
    arm4_ids = json.loads(MANIFEST_ARM4.read_text(encoding="utf-8"))["plan"]["instance_ids"]
    return {"arm3": list(arm3), "arm4": list(arm4_ids)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="", help="run directory (absolute)")
    ap.add_argument("--task", default="T03MaterialSEG")
    ap.add_argument("--only", default="", help="comma-separated instance ids (a retry)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--reanalyse", action="store_true")
    args = ap.parse_args(argv)
    if args.reanalyse:
        if not args.out:
            raise SystemExit("--reanalyse needs --out")
        return arm4.reanalyse(Path(args.out))

    load_credentials()
    from tasks import get_task

    task = get_task(args.task)
    corpus_sha = verify_corpus(args.task)
    chosen = all_rows(args.task)
    if args.only:
        wanted = set(args.only.split(","))
        chosen = [r for r in chosen if r["id"] in wanted]

    out_dir = Path(args.out) if args.out else (
        run_mod.RUNS_DIR / f"arm5-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    if not out_dir.is_absolute():
        raise SystemExit("--out must be absolute: the loop chdirs into each project")
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"arm5-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"

    options = Options(
        task_id=args.task, n=len(chosen), seed=BOOT_SEED, generator=GENERATOR,
        auditor=AUDITOR, judge=AUDITOR, mapper=AUDITOR, adjudicator=AUDITOR,
        max_rounds=1, checks=CHECKS_YAML, lone_model_blocker="block",
        na_policy="literal", arms="B", out=str(out_dir),
        audit_rules="general", subset=0, label="arm5")

    skill = arm4.shipped_skill()
    contract = describe(CHECKS_LIST)
    earlier = earlier_ids()
    plan = {
        "run_id": run_id, "task": args.task, "corpus_sha256": corpus_sha,
        "instance_ids": [r["id"] for r in chosen],
        "replicate_of_arm4_ids": [r["id"] for r in chosen if r["id"] in set(earlier["arm4"])],
        "new_to_the_shipped_skill_ids": [r["id"] for r in chosen if r["id"] in set(earlier["arm3"])],
        "arm": ARM, "models": {"generator": GENERATOR, "auditor": AUDITOR},
        "settings": {"max_rounds": 1, "checks": CHECKS_LIST, "audit_rules": "general",
                     "scope": SCOPE_DIR, "increment_dir": INCREMENT_DIR,
                     "output": OUTPUT_PATH, "recipe": RECIPE_PATH,
                     "budget_usd": BUDGET_USD, "bootstrap_seed": BOOT_SEED},
        "skill_sha256": hashlib.sha256(skill.encode("utf-8")).hexdigest(),
        "contract_sha256": hashlib.sha256(contract.encode("utf-8")).hexdigest(),
        "matcher_version": arm4.matcher_version(),
        "code_sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(HERE),
                                   capture_output=True, text=True).stdout.strip(),
        "git_status": subprocess.run(["git", "status", "--porcelain"], cwd=str(HERE),
                                     capture_output=True, text=True).stdout,
        "python": sys.version.split()[0], "platform": sys.platform,
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }
    if args.only and (out_dir / "plan.json").exists():
        # A retry never rewrites the run's plan: the first retry of Arm 5 did, and the
        # plan had to be restored from the log where it was printed.
        print(f"retry of {args.only}: the run's plan.json is kept")
    else:
        (out_dir / "plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        (out_dir / "contract-S.txt").write_text(contract + "\n", encoding="utf-8")
        (out_dir / "skill-S.md").write_text(skill, encoding="utf-8")
        print(json.dumps({k: v for k, v in plan.items() if k != "git_status"}, indent=2))
    if args.dry_run:
        return 0

    records_path = out_dir / "records.jsonl"
    done = set()
    if records_path.exists() and not args.only:
        done = {json.loads(l)["instance"] for l in
                records_path.read_text(encoding="utf-8").splitlines() if l.strip()}
    spend = 0.0
    for index, row in enumerate(chosen, start=1):
        if row["id"] in done:
            print(f"[{index}/{len(chosen)}] {row['id']} — recorded")
            continue
        print(f"[{index}/{len(chosen)}] {row['id']} …", flush=True)
        record = arm4.run_instance(out_dir, task, row, options, run_id)
        with records_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        spend += float(record.get("usage", {}).get("all", {}).get("cost_usd", 0.0))
        blocks = sum(1 for r in record["rows"] if r["severity"] == BLOCKER)
        passes = sum(1 for r in record["rows"] if r["severity"] == "PASS")
        print(f"    ok={record['ok']} rows={len(record['rows'])} pass={passes} "
              f"blocks={blocks} "
              f"gencalls={record.get('usage', {}).get('generator_role_calls')} "
              f"cost=${record.get('usage', {}).get('all', {}).get('cost_usd', 0):.4f} "
              f"(run so far ${spend:.3f})", flush=True)
        if spend > BUDGET_USD:
            print("STOPPING: the preregistered budget is spent")
            break
    print(f"spend ${spend:.4f}; records at {records_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
