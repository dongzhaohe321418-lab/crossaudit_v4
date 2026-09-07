#!/usr/bin/env python3
"""Study 15 — Arm 6: the shipped check on a second domain, T01LegalMDS.

Preregistered at `study15/PREREGISTRATION-ARM6.md`, committed before any model
call. Arm 5's harness (`provenance_arm6.py` → `provenance_arm4.py`) with the
declared changes: the task is T01LegalMDS (transcribed at e70b7f5), the
population is every instance whose input is at most 200,000 characters, the
budget is $30.00, the seed 20261108, and the primary is adjudicated on the
quotation (the sheet builder shows the quoted run).

    export PYTHONPATH=<worktree>/src
    set -a && . ~/.crossaudit-keys.env && set +a
    python3 benchmarks/expertlongbench/provenance_arm6.py --dry-run --out <abs>
    python3 benchmarks/expertlongbench/provenance_arm6.py --out <abs>
    python3 benchmarks/expertlongbench/provenance_arm6.py --reanalyse --out <abs>
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
BUDGET_USD = 30.00
BOOT_SEED = 20261108


INPUT_CAP = 200_000


def all_rows(task_id: str) -> list[dict]:
    """Every corpus row whose input is at most INPUT_CAP characters, in corpus
    order; no seed. The cap is the generator's context (PREREGISTRATION §2.2)."""
    return [r for r in load_task_rows(task_id) if len(r["input"]) <= INPUT_CAP]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="", help="run directory (absolute)")
    ap.add_argument("--task", default="T01LegalMDS")
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
        run_mod.RUNS_DIR / f"arm6-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    if not out_dir.is_absolute():
        raise SystemExit("--out must be absolute: the loop chdirs into each project")
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"arm6-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"

    options = Options(
        task_id=args.task, n=len(chosen), seed=BOOT_SEED, generator=GENERATOR,
        auditor=AUDITOR, judge=AUDITOR, mapper=AUDITOR, adjudicator=AUDITOR,
        max_rounds=1, checks=CHECKS_YAML, lone_model_blocker="block",
        na_policy="literal", arms="B", out=str(out_dir),
        audit_rules="general", subset=0, label="arm6")

    skill = arm4.shipped_skill()
    contract = describe(CHECKS_LIST)
    plan = {
        "run_id": run_id, "task": args.task, "corpus_sha256": corpus_sha,
        "instance_ids": [r["id"] for r in chosen],
        "input_cap_chars": INPUT_CAP,
        "population_of": len(load_task_rows(args.task)),
        "input_chars": {r["id"]: len(r["input"]) for r in chosen},
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
