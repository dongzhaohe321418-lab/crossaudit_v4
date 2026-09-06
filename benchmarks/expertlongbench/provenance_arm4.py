#!/usr/bin/env python3
"""Study 8 — Arm 4: the shipped check and the shipped skill, on a fresh sample.

Preregistered at `study8/PREREGISTRATION-ARM4.md`, committed before any model
call. One arm, S: the product's own annotation skill (rendered by
`scaffold.annotation_skill_tree`), the product's own contract sentence
(`dcl.describe`), and the product's own verifier (`numbers._row_findings`) on
the audited increment rebuilt from the committed tree. Nothing under `src/` is
modified and nothing in the prompt is wrapped.

    export PYTHONPATH=<worktree>/src
    set -a && . ~/.crossaudit-keys.env && set +a
    python3 benchmarks/expertlongbench/provenance_arm4.py --out <abs>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "src"))

import run as run_mod                                              # noqa: E402
import provenance_arm3 as arm3                                     # noqa: E402
from provenance_probe import NUM                                   # noqa: E402
from run import (OUTPUT_PATH, Options, SCOPE_DIR, INCREMENT_DIR,   # noqa: E402
                 RECIPE_PATH, load_task_rows, load_credentials, verify_corpus)
from crossaudit.dcl import numbers as num_mod                      # noqa: E402
from crossaudit.dcl import describe                                # noqa: E402
from crossaudit.dcl.framework import ADVISORY, BLOCKER             # noqa: E402
from crossaudit.scaffold import annotation_skill_tree              # noqa: E402

GENERATOR = arm3.GENERATOR
AUDITOR = arm3.AUDITOR
CHECKS_LIST = ["number_source"]
CHECKS_YAML = json.dumps(CHECKS_LIST)
ARM = "S"
BUDGET_USD = 3.00
BOOT_SEED = 20261106
SKILL_PATH = "skills/provenance-numbers.md"
MANIFEST_ARM3 = HERE / "study8" / "manifest.json"


def shipped_skill() -> str:
    """Byte-identical to what `crossaudit init` writes for this check."""
    return annotation_skill_tree(CHECKS_LIST)[SKILL_PATH]


def matcher_version() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD:src/crossaudit/dcl/numbers.py"],
                          cwd=str(HERE), capture_output=True, text=True).stdout.strip()


def fresh_rows(task_id: str) -> list[dict]:
    """Every corpus row no earlier arm saw: excluded by id against Arm 3's plan."""
    used = set(json.loads(MANIFEST_ARM3.read_text(encoding="utf-8"))["instance_ids"])
    return [r for r in load_task_rows(task_id) if r["id"] not in used]


# ---------------------------------------------------------------- the project

def bootstrap_shipped_project(scratch: Path, task, row: dict, options: Options) -> Path:
    """The product's own bootstrap, plus the shipped skill committed beside it."""
    project = run_mod.bootstrap_project(scratch, task, row, options)
    dest = project / SKILL_PATH
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(shipped_skill(), encoding="utf-8", newline="\n")
    subprocess.run(["git", "add", "-A"], cwd=str(project), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "shipped annotation skill"],
                   cwd=str(project), check=True)
    return project


# ------------------------------------------------------------- the verifier

def _reason(findings: list, src) -> str:
    """A machine key for the classifier, never an observation string."""
    if src == "uncited":
        return "uncited"
    if isinstance(src, str) and src.startswith("governed:"):
        return "governed"
    if not findings:
        return ""
    text = " ".join(f.observation for f in findings)
    if "across a line break" in text:
        return "quote-crosses-line"
    if "does not contain those characters" in text:
        return "quote-absent"
    if "names no one place" in text:
        return "ambiguous"
    if "is not in it" in text:
        return "pair-not-in-location"
    if "not in the audited scope" in text:
        return "unresolved:path"
    if "pinned" in text or "sha256 prefix" in text:
        return "unresolved:sha"
    if "not readable" in text:
        return "unresolved:not-text"
    if "no file" in text or "no quotation" in text:
        return "malformed:src"
    return "malformed:row"


def verify_shipped(files, row: dict, draft: str):
    findings = num_mod._row_findings(OUTPUT_PATH, files, row, draft)
    src = row.get("src")
    if any(f.severity == BLOCKER for f in findings):
        severity = BLOCKER
    elif findings:
        severity = ADVISORY
    else:
        severity = "PASS"
    rules = sorted({f.rule for f in findings})
    return severity, ",".join(rules) or "pass", _reason(findings, src)


def located_line(files, row: dict):
    """The whitespace-folded LINE the shipped rule selects for this row's quote,
    resolved by the harness (not asked of the verifier): `(key, line, lines)` or
    None where the row names nothing this study can re-read."""
    src = row.get("src")
    if not isinstance(src, dict):
        return None
    named, quote = src.get("file"), src.get("quote")
    if not isinstance(named, str) or not isinstance(quote, str) or not quote.strip():
        return None
    key = arm3.resolve_key(files, OUTPUT_PATH, named)
    if key is None:
        return None
    body = arm3._decode(files, key)
    if body is None:
        return None
    located, hits = num_mod._quote_span(body, quote)
    if located is None:
        return None
    return key, located.line, hits


# -------------------------------------------------------------- one instance

def analyse_project(project: Path, instance: str) -> dict:
    from crossaudit.config import load as load_cfg

    cfg = load_cfg(project / "crossaudit.yml")
    record: dict = {"instance": instance, "arm": ARM, "rows": []}
    sha_science = arm3.science_commit(project)
    record["science_sha"] = sha_science
    if not sha_science:
        record["analysis_error"] = "the loop committed no deliverable"
        return record
    files = arm3.audited_increment(project, sha_science, cfg)
    record["increment_files"] = sorted(files)
    record["manifest_agrees"] = None
    for cycle in sorted((project / cfg.ledger_dir).glob("*/receipt.json")):
        manifest = json.loads(cycle.read_text(encoding="utf-8")).get(
            "inputs", {}).get("manifest", {})
        record["manifest_agrees"] = manifest == {
            k: hashlib.sha256(v).hexdigest() for k, v in files.items()}
    draft = files.get(OUTPUT_PATH, b"").decode("utf-8", "replace")
    record["output_sha256"] = arm3.sha(draft)
    record["draft_chars"] = len(draft)
    record["draft_lines"] = draft.count("\n") + 1
    record["numbers_present"] = len(NUM.findall(arm3.strip_fences(draft)))
    record["fence_blocks"] = len(num_mod._FENCE.findall(draft))
    record["shipped_check_blocks"] = sum(
        1 for f in num_mod.check_number_source(files) if f.severity == BLOCKER)
    record["matcher_version"] = matcher_version()
    for row_no, ann in enumerate(arm3.fence_rows(draft)):
        severity, rule, reason = verify_shipped(files, ann, draft)
        v, u = str(ann.get("v", "")), str(ann.get("u", ""))
        src = ann.get("src")
        location = located_line(files, ann)
        adj_a = adj_b = None
        if location is not None:
            adj_a = num_mod.contains_pair(location[1], v, u)
            adj_b = arm3.adjudicator_b(location[1], v, u)
        if isinstance(src, dict):
            kind, src_file = "quote", str(src.get("file", ""))
            quote = src.get("quote") if isinstance(src.get("quote"), str) else None
            quote_len, quote_sha = (len(quote), arm3.sha(quote)) if quote else (None, "")
        else:
            text = str(src)
            kind = ("uncited" if text == "uncited"
                    else "governed" if text.startswith("governed:") else "other")
            src_file, quote_len, quote_sha = text if kind != "other" else "", None, ""
        key = arm3.resolve_key(files, OUTPUT_PATH, src["file"]) if (
            isinstance(src, dict) and isinstance(src.get("file"), str)) else None
        body = arm3._decode(files, key) if key else None
        record["rows"].append({
            "instance": instance, "arm": ARM, "row": row_no,
            "src_kind": kind, "src_addr": src_file,
            "quote_len": quote_len, "quote_sha256": quote_sha,
            "v_sha256": arm3.sha(v), "u_sha256": arm3.sha(u),
            "v_len": len(v), "u_len": len(u),
            "severity": severity, "disposition": rule, "reason": reason,
            "resolved_location": location is not None,
            "occurrences": location[2] if location else None,
            "location_file": location[0] if location else "",
            "adj_a": adj_a, "adj_b": adj_b,
            "unit_shortened": (arm3.unit_shortened(location[1], v, u)
                               if location is not None else None),
            "pair_in_named_file": (num_mod.contains_pair(body, v, u)
                                   if body is not None else None),
            "matcher_version": record["matcher_version"],
        })
    return record


def run_instance(out_dir: Path, task, row: dict, options: Options, run_id: str) -> dict:
    saved_bootstrap = run_mod.bootstrap_project
    run_mod.bootstrap_project = bootstrap_shipped_project
    try:
        safe = row["id"].replace("/", "__")
        scratch = out_dir / "instances" / f"{safe}__{ARM}"
        scratch.mkdir(parents=True, exist_ok=True)
        started = time.time()
        result = run_mod.run_arm_b(scratch, task, row, options, run_id)
        project = scratch / "project"
        record: dict = {
            "instance": row["id"], "arm": ARM, "ok": result.ok,
            "error": result.error, "exit_code": result.exit_code,
            "rounds": result.rounds, "wall_s": round(result.wall_s, 2),
            "prompt_sha256": result.prompt_sha256,
            "started_utc": datetime.fromtimestamp(started, timezone.utc).isoformat(),
        }
        from crossaudit.config import load as load_cfg

        cfg = load_cfg(project / "crossaudit.yml")
        record["usage"] = arm3.usage_split(project, cfg, run_id)
        record.update(analyse_project(project, row["id"]))
        return record
    finally:
        run_mod.bootstrap_project = saved_bootstrap


def reanalyse(out_dir: Path) -> int:
    path = out_dir / "records.jsonl"
    kept = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    rewritten = []
    for old in kept:
        safe = old["instance"].replace("/", "__")
        project = out_dir / "instances" / f"{safe}__{ARM}" / "project"
        fresh = analyse_project(project, old["instance"])
        merged = {k: v for k, v in old.items() if k in (
            "instance", "arm", "ok", "error", "exit_code", "rounds", "wall_s",
            "prompt_sha256", "started_utc", "usage")}
        merged.update(fresh)
        rewritten.append(merged)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n"
                            for r in rewritten), encoding="utf-8")
    print(f"reanalysed {len(rewritten)} record(s) in {path}")
    return 0


# ------------------------------------------------------------------ the study

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
        return reanalyse(Path(args.out))

    load_credentials()
    from tasks import get_task

    task = get_task(args.task)
    corpus_sha = verify_corpus(args.task)
    chosen = fresh_rows(args.task)
    if args.only:
        wanted = set(args.only.split(","))
        chosen = [r for r in chosen if r["id"] in wanted]

    out_dir = Path(args.out) if args.out else (
        run_mod.RUNS_DIR / f"arm4-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    if not out_dir.is_absolute():
        raise SystemExit("--out must be absolute: the loop chdirs into each project")
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"arm4-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"

    options = Options(
        task_id=args.task, n=len(chosen), seed=BOOT_SEED, generator=GENERATOR,
        auditor=AUDITOR, judge=AUDITOR, mapper=AUDITOR, adjudicator=AUDITOR,
        max_rounds=1, checks=CHECKS_YAML, lone_model_blocker="block",
        na_policy="literal", arms="B", out=str(out_dir),
        audit_rules="general", subset=0, label="arm4")

    skill = shipped_skill()
    contract = describe(CHECKS_LIST)
    plan = {
        "run_id": run_id, "task": args.task, "corpus_sha256": corpus_sha,
        "instance_ids": [r["id"] for r in chosen],
        "excluded_ids": json.loads(MANIFEST_ARM3.read_text(encoding="utf-8"))["instance_ids"],
        "arm": ARM, "models": {"generator": GENERATOR, "auditor": AUDITOR},
        "settings": {"max_rounds": 1, "checks": CHECKS_LIST, "audit_rules": "general",
                     "scope": SCOPE_DIR, "increment_dir": INCREMENT_DIR,
                     "output": OUTPUT_PATH, "recipe": RECIPE_PATH,
                     "budget_usd": BUDGET_USD, "bootstrap_seed": BOOT_SEED},
        "skill_sha256": hashlib.sha256(skill.encode("utf-8")).hexdigest(),
        "contract_sha256": hashlib.sha256(contract.encode("utf-8")).hexdigest(),
        "matcher_version": matcher_version(),
        "code_sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(HERE),
                                   capture_output=True, text=True).stdout.strip(),
        "git_status": subprocess.run(["git", "status", "--porcelain"], cwd=str(HERE),
                                     capture_output=True, text=True).stdout,
        "python": sys.version.split()[0], "platform": sys.platform,
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }
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
        record = run_instance(out_dir, task, row, options, run_id)
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
