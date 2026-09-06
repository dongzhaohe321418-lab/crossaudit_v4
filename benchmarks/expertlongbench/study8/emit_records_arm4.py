#!/usr/bin/env python3
"""Turn the Arm 4 run directory into the committed record set (corpus-free).

One JSONL row per annotation row (`rows-arm4.jsonl`) and a manifest
(`manifest-arm4.json`), carrying every measured quantity and never corpus text:
values, units and quotes appear only as sha256 digests and lengths. The gold
label (`GOLD-arm4.csv` via `key-arm4.jsonl`) and the block mechanism
(`CONTAINMENT_RULE.md` §1's M-labels, read from the archived drafts by hand
after labelling) are joined in.

    python3 benchmarks/expertlongbench/study8/emit_records_arm4.py <run-dir>
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent

#: `(instance, row) -> mechanism`, for the 10 Arm 4 blocks. Read from the
#: archived located lines by hand; the identities are the key's. M10 is new in
#: this arm: an en-dash (U+2013) exponent tail, which the scanner reads as a
#: boundary — not M9c, whose rendering fold happens at comparison time.
MECHANISM: dict[tuple[str, int], str] = {
    # No source text in these comments (corpus licence): the shapes only.
    ("T03MaterialSEG-10.1002/zaac.201800357", 3): "M10",   # a unit whose negative exponent is an EN DASH
    ("T03MaterialSEG-10.1002/zaac.201800357", 4): "M10",   # the same, second unit on the same line
    ("T03MaterialSEG-10.1002/zaac.201800357", 5): "M3",    # two numerals joined by a word, one trailing unit
    ("T03MaterialSEG-10.1002/pssb.201900312", 0): "M2",    # a range, first endpoint annotated
    ("T03MaterialSEG-10.1002/pssb.201900312", 2): "M2",    # a range
    ("T03MaterialSEG-10.1002/pssb.201900312", 4): "M2",    # a range
    ("T03MaterialSEG-10.1002/ange.202300209", 4): "M2",    # a range
    ("T03MaterialSEG-10.1002/cssc.201000245", 7): "M2",    # a range (a length)
    ("T03MaterialSEG-10.1002/adfm.202309656", 11): "M4",   # a hyphen joining the unit to the next word
    ("T03MaterialSEG-10.1002/adfm.202309656", 0): "M1b",   # the value is not on the located line
}


def main(argv=None) -> int:
    run_dir = pathlib.Path(argv[0] if argv else sys.argv[1])
    records = [json.loads(l) for l in (run_dir / "records.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    key = {(r["instance"], r["row"]): r for r in (json.loads(l) for l in
           (HERE / "key-arm4.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
    gold = {}
    for line in (HERE / "GOLD-arm4.csv").read_text(encoding="utf-8").splitlines():
        if line.startswith("A4"):
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
            out["mechanism"] = MECHANISM.get((r["instance"], r["row"]), "")
            rows.append(out)
    for r in rows:
        assert r["severity"] != "BLOCKER" or r["mechanism"], (r["instance"], r["row"])
    (HERE / "rows-arm4.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
    manifest = {
        "study": "study8 / Arm 4",
        "preregistration": "benchmarks/expertlongbench/study8/PREREGISTRATION-ARM4.md",
        "plan": {k: v for k, v in plan.items() if k != "git_status"},
        "git_status_at_start": plan.get("git_status", ""),
        "drafts": drafts,
        "rows_recorded": len(rows),
        "drafts_recorded": len(drafts),
        "rows_sha256": hashlib.sha256((HERE / "rows-arm4.jsonl").read_bytes()).hexdigest(),
        "gold_sha256": hashlib.sha256((HERE / "GOLD-arm4.csv").read_bytes()).hexdigest(),
    }
    (HERE / "manifest-arm4.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                             encoding="utf-8")
    print(f"rows {len(rows)}, drafts {len(drafts)}; mechanisms "
          f"{sorted(r['mechanism'] for r in rows if r['mechanism'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
