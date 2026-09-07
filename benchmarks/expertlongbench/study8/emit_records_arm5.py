#!/usr/bin/env python3
"""Turn the Arm 5 run directory into the committed record set (corpus-free).

One JSONL row per annotation row (`rows-arm5.jsonl`) and a manifest
(`manifest-arm5.json`), carrying every measured quantity and never corpus text:
values, units and quotes appear only as sha256 digests and lengths. The gold
label (`GOLD-arm5.csv` via `key-arm5.jsonl`) and the block mechanism
(`CONTAINMENT_RULE.md` §1's M-labels, read from the archived drafts by hand
after labelling) are joined in.

    python3 benchmarks/expertlongbench/study8/emit_records_arm5.py <run-dir>
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent

#: `(instance, row) -> mechanism` for every Arm 5 block, `CONTAINMENT_RULE.md` §1's
#: M-labels, read from the archived located lines by hand after labelling. Filled
#: after the run; the assertion below refuses to emit records while a block has none.
#: No source text in the comments (corpus licence): the shapes only.
MECHANISM: dict[tuple[str, int], str] = {
}


def main(argv=None) -> int:
    run_dir = pathlib.Path(argv[0] if argv else sys.argv[1])
    records = [json.loads(l) for l in (run_dir / "records.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    key = {(r["instance"], r["row"]): r for r in (json.loads(l) for l in
           (HERE / "key-arm5.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
    gold = {}
    for line in (HERE / "GOLD-arm5.csv").read_text(encoding="utf-8").splitlines():
        if line.startswith("A5"):
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
    (HERE / "rows-arm5.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    plan = json.loads((run_dir / "plan.json").read_text(encoding="utf-8"))
    manifest = {
        "study": "study8 / Arm 5",
        "preregistration": "benchmarks/expertlongbench/study8/PREREGISTRATION-ARM5.md",
        "plan": {k: v for k, v in plan.items() if k != "git_status"},
        "git_status_at_start": plan.get("git_status", ""),
        "drafts": drafts,
        "rows_recorded": len(rows),
        "drafts_recorded": len(drafts),
        "rows_sha256": hashlib.sha256((HERE / "rows-arm5.jsonl").read_bytes()).hexdigest(),
        "gold_sha256": hashlib.sha256((HERE / "GOLD-arm5.csv").read_bytes()).hexdigest(),
    }
    (HERE / "manifest-arm5.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                             encoding="utf-8")
    print(f"rows {len(rows)}, drafts {len(drafts)}; mechanisms "
          f"{sorted(r['mechanism'] for r in rows if r['mechanism'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
