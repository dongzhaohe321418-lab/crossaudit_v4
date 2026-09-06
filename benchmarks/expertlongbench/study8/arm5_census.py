#!/usr/bin/env python3
"""The 2026-09-07 census behind Arm 5's choice of corpus (PREREGISTRATION-ARM5 §0).

For every public ExpertLongBench task: the median input length, the median number
of numbers in the input and in the human reference (Arm 1's `NUM` extractor), the
share of reference numbers whose value occurs in the input, and the share carrying
a unit token. Counts only; nothing from the corpus is printed.

    PYTHONPATH=src python3 benchmarks/expertlongbench/study8/arm5_census.py
"""
from __future__ import annotations

import json
import statistics as st
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from provenance_probe import pairs                                 # noqa: E402

TASKS = ["T03MaterialSEG", "T04EduPAE", "T06HealthCNG", "T07ChemMDG",
         "T08BioPDG", "T11CyberRDG", "T01LegalMDS"]


def text(x) -> str:
    if isinstance(x, list):
        return "\n".join(text(i) for i in x)
    if isinstance(x, dict):
        return "\n".join(f"{k}: {text(v)}" for k, v in x.items())
    return "" if x is None else str(x)


def main() -> int:
    data = HERE.parent / "data"
    print(f"{'task':16} {'rows':>4} {'in_chars':>9} {'in_nums':>8} {'ref_nums':>8} "
          f"{'traced%':>8} {'unit%':>6} {'ref_total':>9}")
    for t in TASKS:
        path = data / f"{t}.jsonl"
        if not path.exists():
            print(f"{t:16} (not fetched)")
            continue
        rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        in_chars, in_nums, ref_nums, traced, total, unit = [], [], [], 0, 0, 0
        for r in rows:
            inp, ref = text(r.get("input")), text(r.get("raw_human_reference"))
            ip, rp = pairs(inp), pairs(ref)
            ivals = {v for v, _ in ip}
            in_chars.append(len(inp)); in_nums.append(len(ip)); ref_nums.append(len(rp))
            for v, u in rp:
                total += 1; traced += v in ivals; unit += bool(u)
        print(f"{t:16} {len(rows):4d} {st.median(in_chars):9.0f} {st.median(in_nums):8.1f} "
              f"{st.median(ref_nums):8.1f} {100 * traced / max(1, total):8.1f} "
              f"{100 * unit / max(1, total):6.1f} {total:9d}")
    print("\nT03's raw_human_reference is null in the release (its reference is the checklist), "
          "so its reference columns read 0; T03 is the task every earlier arm ran on.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
