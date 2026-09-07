#!/usr/bin/env python3
"""Arm 5 secondary 13 (PREREGISTRATION-ARM5 §5): what the containment extensions did
on a real generator's output.

Every located row of the Arm 5 run is re-adjudicated by `contains_pair` from the
matcher Arm 4 ran (`numbers.py` at blob 8dfd07d9…, the merge of slice 3), loaded
from git into memory, beside the shipped matcher's verdict. Counts only.

    PYTHONPATH=<worktree>/src python3 benchmarks/expertlongbench/study8/arm5_matcher_diff.py \\
        --runs ~/Documents/Crossaudit/study-data/wt-arm5-runs/arm5
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import types
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent.parent / "src"))

import provenance_arm3 as arm3                                     # noqa: E402
import provenance_arm4 as arm4                                     # noqa: E402
from run import OUTPUT_PATH                                        # noqa: E402
from crossaudit.dcl import numbers as shipped                      # noqa: E402

ARM4_BLOB = "8dfd07d9c17031a839513db732bc0d760d3ea50a"


def load_blob_module(blob: str):
    src = subprocess.run(["git", "cat-file", "-p", blob], cwd=str(HERE),
                         capture_output=True, text=True, check=True).stdout
    mod = types.ModuleType("numbers_arm4")
    mod.__package__ = "crossaudit.dcl"
    exec(compile(src, f"numbers.py@{blob[:12]}", "exec"), mod.__dict__)
    return mod


def main(argv=None) -> int:
    from crossaudit.config import load as load_cfg

    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True, type=Path)
    args = ap.parse_args(argv)
    old = load_blob_module(ARM4_BLOB)
    tally = Counter()
    for proj_dir in sorted((args.runs / "instances").iterdir()):
        project = proj_dir / "project"
        if not (project / "crossaudit.yml").exists():
            continue
        cfg = load_cfg(project / "crossaudit.yml")
        sha = arm3.science_commit(project)
        if not sha:
            continue
        files = arm3.audited_increment(project, sha, cfg)
        draft = files.get(OUTPUT_PATH, b"").decode("utf-8", "replace")
        for ann in arm3.fence_rows(draft):
            v, u = str(ann.get("v", "")), str(ann.get("u", ""))
            loc = arm4.located_line(files, ann)
            if loc is None:
                tally["no located line"] += 1
                continue
            # The contract reads the QUOTATION (the pair must lie inside the quoted run,
            # read in its own line: `_pair_in_quote`), not the whole located line. The
            # first review found the line-level count one higher — a row whose line
            # states the pair outside the quotation — so both are tallied and the
            # quotation-level one is the contract's.
            quote = ann["src"]["quote"]
            body = arm3._decode(files, loc[0])
            def under(mod):
                located, _ = mod._quote_span(body, quote)
                return located is not None and mod._pair_in_quote(located, v, u)
            now_q, before_q = under(shipped), under(old)
            tally[f"quotation: shipped {'pass' if now_q else 'block'} / arm4-matcher {'pass' if before_q else 'block'}"] += 1
            now = shipped.contains_pair(loc[1], v, u)
            before = old.contains_pair(loc[1], v, u)
            tally[f"line: shipped {'pass' if now else 'block'} / arm4-matcher {'pass' if before else 'block'}"] += 1
    located = sum(n for k, n in tally.items() if k.startswith("quotation:"))
    print(f"located rows {located} (each tallied once per reading); no located line {tally['no located line']}")
    for k, n in sorted(tally.items()):
        if k != "no located line":
            print(f"  {k}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
