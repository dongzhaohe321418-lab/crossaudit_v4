#!/usr/bin/env python3
"""Turn the Arm 6 run directory into the committed record set (corpus-free).

One JSONL row per annotation row (`rows-arm6.jsonl`) and a manifest
(`manifest-arm6.json`), carrying every measured quantity and never corpus text:
values, units and quotes appear only as sha256 digests and lengths. The gold
label (`GOLD-arm6.csv` via `key-arm6.jsonl`) and the block mechanism
(`CONTAINMENT_RULE.md` §1's M-labels, read from the archived drafts by hand
after labelling) are joined in.

    python3 benchmarks/expertlongbench/study15/emit_records_arm6.py <run-dir>
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent

#: `(instance, row) -> mechanism` for every Arm 6 block, `CONTAINMENT_RULE.md` §1's
#: M-labels, read from the archived located lines by hand after labelling. Filled
#: after the run; the assertion below refuses to emit records while a block has none.
#: No source text in the comments (corpus licence): the shapes only.
MECHANISM: dict[tuple[str, int], str] = {
    ("T01LegalMDS-15516", 7): "M1b",   # the value written in words (gold N)
    ("T01LegalMDS-16123", 6): "M13",   # NEW: a currency sign BEFORE the value, transcribed as the unit; the scanner reads units after the number (gold C)
    ("T01LegalMDS-13885", 4): "M13",   # the same, a decimal amount (gold C)
    ("T01LegalMDS-16123", 9): "M13",   # the same, a whole amount (gold C)
    ("T01LegalMDS-15207", 9): "M1b",   # the value lies outside the quoted run, which ends before it (gold N under the quotation adjudicator)
}


def main(argv=None) -> int:
    run_dir = pathlib.Path(argv[0] if argv else sys.argv[1])
    records = [json.loads(l) for l in (run_dir / "records.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    key = {(r["instance"], r["row"]): r for r in (json.loads(l) for l in
           (HERE / "key-arm6.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
    gold = {}
    for line in (HERE / "GOLD-arm6.csv").read_text(encoding="utf-8").splitlines():
        if line.startswith("A6"):
            i, lab, rule = (line.split(",") + ["", ""])[:3]
            gold[i] = (lab.strip(), rule.strip())
    rows, drafts = [], []
    for rec in records:
        drafts.append({k: rec.get(k) for k in (
            "instance", "arm", "ok", "error", "exit_code", "rounds", "wall_s",
            "prompt_sha256", "started_utc", "usage", "science_sha", "increment_files",
            "manifest_agrees", "output_sha256", "draft_chars", "draft_lines",
            "numbers_present", "fence_blocks", "shipped_check_blocks", "matcher_version")})
        for r in rec.get("rows", []):
            k = key.get((r["instance"], r["row"]))
            item_id = k["id"] if k else ""
            lab, rule = gold.get(item_id, ("", ""))
            out = dict(r)
            out["gold_item"] = item_id
            out["gold_label"] = lab
            out["gold_rule"] = rule
            out["gold_kind"] = k["kind"] if k else ""
            # A block with no located quotation is the CONTRACT's, not the matcher's:
            # Q1 — the quotation crosses a hard line break (the one-line rule, H6b);
            # Q2 — the quotation is not in the file as quoted (rendering, elision or
            # paraphrase; the shapes are counted in RESULTS-ARM6 §2 without quoting).
            out["mechanism"] = MECHANISM.get((r["instance"], r["row"]), "") or (
                {"quote-crosses-line": "Q1", "quote-absent": "Q2"}.get(r["reason"], "")
                if r["severity"] == "BLOCKER" else "")
            rows.append(out)
    for r in rows:
        assert r["severity"] != "BLOCKER" or r["mechanism"], (r["instance"], r["row"])
    (HERE / "rows-arm6.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
    # Attempt 2 was resumed in the same directory after the credit outage, and the runner
    # then rewrote plan.json (review round 1). The plan printed at the run's START was
    # recovered from the log into plan-start.json; both are recorded, with what differs.
    start_path = run_dir / "plan-start.json"
    plan_start = json.loads(start_path.read_text(encoding="utf-8")) if start_path.exists() else None
    manifest = {
        "study": "study15 / Arm 6",
        "preregistration": "benchmarks/expertlongbench/study15/PREREGISTRATION-ARM6.md",
        "plan": {k: v for k, v in plan.items() if k != "git_status"},
        "git_status_at_start": plan.get("git_status", ""),
        "plan_at_start": ({k: v for k, v in plan_start.items() if k != "git_status"}
                          if plan_start else None),
        # The runner prints the plan WITHOUT git_status; the log therefore cannot say whether
        # the tree was clean at the true start. Unknown is recorded as unknown, not as "".
        "git_status_at_true_start": (plan_start["git_status"] if plan_start and "git_status" in plan_start
                                     else "NOT RECORDED: the logged plan omits git_status"),
        "plan_fields_differing_start_vs_resume": (
            sorted(k for k in set(plan) | set(plan_start) if plan.get(k) != plan_start.get(k))
            if plan_start else None),
        "plan_note": ("plan.json is the RESUME's plan (the runner rewrote it; fixed in "
                      "provenance_arm6.py afterwards); plan_at_start is the run's start, "
                      "recovered from arm6.log where the runner printed it"),
        "drafts": drafts,
        "rows_recorded": len(rows),
        "drafts_recorded": len(drafts),
        "rows_sha256": hashlib.sha256((HERE / "rows-arm6.jsonl").read_bytes()).hexdigest(),
        "gold_sha256": hashlib.sha256((HERE / "GOLD-arm6.csv").read_bytes()).hexdigest(),
    }
    (HERE / "manifest-arm6.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                             encoding="utf-8")
    print(f"rows {len(rows)}, drafts {len(drafts)}; mechanisms "
          f"{sorted(r['mechanism'] for r in rows if r['mechanism'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
