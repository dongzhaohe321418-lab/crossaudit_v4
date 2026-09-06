#!/usr/bin/env python3
"""Arm 5's labelling sheet and key (PREREGISTRATION-ARM5 §3).

The sheet is the ONLY thing a labeller sees: an opaque id, the located line, the
transcribed value and unit. No verdict, no reason, no instance. It carries
corpus text and is written into the archive, never the repository. The KEY —
ids and identities only — is committed beside this file as `key-arm5.jsonl`.

Items: every BLOCK whose quotation the shipped rule locates on one line (a
block with no located line — quote absent, across a line break, unresolved —
has nothing to label and is N by definition, counted in the key as
`no-location`), and a sample of 50 PASSES drawn with seed 20261106.

    PYTHONPATH=<worktree>/src python3 benchmarks/expertlongbench/study8/arm5_sheet.py \\
        --runs ~/Documents/Crossaudit/study-data/wt-arm5-runs/arm5 \\
        --out  ~/Documents/Crossaudit/study-data/wt-arm5-runs/sheet
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent.parent / "src"))

import provenance_arm3 as arm3                                     # noqa: E402
import provenance_arm4 as arm4                                     # noqa: E402
from run import OUTPUT_PATH                                        # noqa: E402
from crossaudit.dcl.framework import BLOCKER                       # noqa: E402

PASS_SAMPLE = 50
SEED = 20261107


def main(argv=None) -> int:
    from crossaudit.config import load as load_cfg

    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)

    blocks, passes, unlocated = [], [], []
    for proj_dir in sorted((args.runs / "instances").iterdir()):
        project = proj_dir / "project"
        if not (project / "crossaudit.yml").exists():
            continue
        stem, _arm = proj_dir.name.rsplit("__", 1)
        instance = stem.replace("__", "/")
        cfg = load_cfg(project / "crossaudit.yml")
        sha = arm3.science_commit(project)
        if not sha:
            continue
        files = arm3.audited_increment(project, sha, cfg)
        draft = files.get(OUTPUT_PATH, b"").decode("utf-8", "replace")
        for row_no, ann in enumerate(arm3.fence_rows(draft)):
            severity, rule, reason = arm4.verify_shipped(files, ann, draft)
            if reason in ("uncited", "governed"):
                continue
            v, u = str(ann.get("v", "")), str(ann.get("u", ""))
            loc = arm4.located_line(files, ann)
            item = {"instance": instance, "row": row_no, "v": v, "u": u,
                    "severity": severity, "reason": reason}
            if severity == BLOCKER:
                if loc is None:
                    unlocated.append(item)
                else:
                    blocks.append({**item, "text": loc[1]})
            elif severity == "PASS" and loc is not None:
                passes.append({**item, "text": loc[1]})
    rng = random.Random(SEED)
    sample = sorted(rng.sample(passes, min(PASS_SAMPLE, len(passes))),
                    key=lambda i: (i["instance"], i["row"]))
    items = [dict(i, kind="block") for i in blocks] + [dict(i, kind="pass") for i in sample]
    rng.shuffle(items)
    sheet, key = [], []
    for n, item in enumerate(items, 1):
        item_id = f"A5{n:04d}"
        sheet.append({"id": item_id, "text": item["text"], "v": item["v"], "u": item["u"]})
        key.append({"id": item_id, "instance": item["instance"], "row": item["row"],
                    "kind": item["kind"], "reason": item["reason"]})
    (args.out / "sheet-arm5.jsonl").write_text(
        "".join(json.dumps(i, ensure_ascii=False) + "\n" for i in sheet), encoding="utf-8")
    (HERE / "key-arm5.jsonl").write_text(
        "".join(json.dumps(k) + "\n" for k in key)
        + "".join(json.dumps({"id": f"A5U{n:03d}", "instance": i["instance"], "row": i["row"],
                              "kind": "block-no-location", "reason": i["reason"]}) + "\n"
                  for n, i in enumerate(unlocated, 1)), encoding="utf-8")
    print(f"blocks with a located line {len(blocks)}; blocks with none {len(unlocated)}; "
          f"passes {len(passes)}, sampled {len(sample)}; sheet items {len(sheet)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
