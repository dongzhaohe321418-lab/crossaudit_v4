#!/usr/bin/env python3
"""Measure the SHIPPED matcher against the frozen containment gold — study 14 (M10).

Imports the shipped `crossaudit.dcl.numbers.contains_pair` and nothing else; the
baseline is `study14/base-verdicts.jsonl`, the merge base's own verdict on every
gold item, frozen before this slice touched `src/`. The ablation switches M10 off by
monkeypatching its named hook — `_dash_exponent` — never by re-implementing the matcher.

    PYTHONPATH=src .venv/bin/python benchmarks/expertlongbench/study14/measure.py \
        --sheet ~/Documents/Crossaudit/study-data/gold-containment/sheet.jsonl \
        --config {shipped|base}

    R   blocks -> passes that the gold labels C   (wrong blocks removed)
    W   blocks -> passes that the gold labels N   (wrong passes added; KILL if > 0)
    R'  passes -> blocks that the gold labels N   (wrong passes removed)
    W'  passes -> blocks that the gold labels C   (wrong blocks added; KILL if > 0)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent.parent / "src"))

from crossaudit.dcl import numbers as N                     # noqa: E402

GOLD = HERE.parent / "study8gold" / "GOLD.csv"
KEY = HERE.parent / "study8gold" / "key.jsonl"
BASE = HERE / "base-verdicts.jsonl"


def configure(name: str) -> None:
    if name == "base":
        import re
        N._dash_exponent = lambda text, i, start: None   # M10 off


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True, type=Path)
    ap.add_argument("--config", choices=["shipped", "base"], default="shipped")
    ap.add_argument("--rows", action="store_true", help="print every moved row")
    args = ap.parse_args(argv)
    configure(args.config)

    gold = {}
    for line in GOLD.read_text(encoding="utf-8").splitlines():
        if line.startswith("G"):
            i, lab, *_ = line.split(",")
            gold[i] = lab.strip()
    key = {json.loads(l)["id"]: json.loads(l) for l in
           KEY.read_text(encoding="utf-8").splitlines() if l.strip()}
    base = {}
    for l in BASE.read_text(encoding="utf-8").splitlines():
        if l.strip() and '"id"' in l:
            r = json.loads(l); base[r["id"]] = r["base"]
    sheet = [json.loads(l) for l in args.sheet.read_text(encoding="utf-8").splitlines()
             if l.strip()]
    assert len(sheet) == len(base) == len(gold) == 300, (len(sheet), len(base), len(gold))

    R = W = Rp = Wp = 0
    right_blocks_still = right_blocks = 0
    panel_contained = panel_wrong = 0
    moved = []
    for it in sheet:
        i = it["id"]
        head = N.contains_pair(it["line"], it["v"], it["u"])
        was = base[i]
        lab = gold[i]
        kind = key[i]["kind"]
        if kind == "block" and lab == "N":
            right_blocks += 1
            right_blocks_still += (not head)
        if kind == "panel":
            panel_contained += head
            panel_wrong += (head and lab == "N")
        if head and not was:
            if lab == "C": R += 1
            elif lab == "N": W += 1
            moved.append(("R" if lab == "C" else "W", i, kind, it["u"]))
        elif was and not head:
            if lab == "N": Rp += 1
            elif lab == "C": Wp += 1
            moved.append(("R'" if lab == "N" else "W'", i, kind, it["u"]))
    print(f"config {args.config}   items {len(sheet)}   R {R}   W {W}   R' {Rp}   W' {Wp}")
    print("kill conditions clear (W = 0 and W' = 0)" if W == 0 and Wp == 0 else "KILL")
    print(f"gold-right blocks still blocking: {right_blocks_still}/{right_blocks}")
    print(f"panel: {panel_contained}/{sum(1 for k in key.values() if k['kind'] == 'panel')} "
          f"contained, of which gold-wrong {panel_wrong}")
    if args.config == "base":
        print("base check: head == frozen base on", sum(
            1 for it in sheet if N.contains_pair(it["line"], it["v"], it["u"]) == base[it["id"]]), "of 300")
    for kind, i, k, u in moved:
        print(f"  {kind:2s} {i} {k} u={u!r}")
    arm4 = Path("~/Documents/Crossaudit/study-data/wt-arm4-runs/sheet/sheet-arm4.jsonl").expanduser()
    if arm4.exists():
        rows = [json.loads(l) for l in arm4.read_text(encoding="utf-8").splitlines() if l.strip()]
        m10 = [r for r in rows if r["id"] in M10_IDS]
        assert all("\u2013" in r["u"] for r in m10), "the M10 rows carry the en dash in the unit"
        hits = sum(N.contains_pair(r["text"], r["v"], r["u"]) for r in m10)
        print(f"Arm 4 M10 rows (archive, counts only): {hits} of {len(m10)} pass")
    else:
        print("Arm 4 archive not present; M10 rows not re-measured")
    return 0


#: Arm 4's two M10 rows, by the sheet's ids (`study8/emit_records_arm4.py`: zaac.201800357
#: rows 3 and 4; the units are `L·h–1` and `K·min–1`, transcribed byte for byte).
M10_IDS = frozenset({"A40015", "A40050"})


if __name__ == "__main__":
    raise SystemExit(main())
