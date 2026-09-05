#!/usr/bin/env python3
"""Measure the SHIPPED matcher against the frozen containment gold.

Study 9, preregistered in `PREREGISTRATION.md` §3. Unlike
`study8gold/simulate.py`, which re-implements `contains_pair` with each proposed
extension as a flag, this imports the shipped
`crossaudit.dcl.numbers.contains_pair` and nothing else, so what it reports is
the code that ships and not a model of it. The baseline it compares against is
the `matcher` column of the committed `study8gold/key.jsonl` — the merge base's
verdict on every one of the 300 rows, frozen before this slice existed and
verified equal to the merge base's live `contains_pair` on 300 of 300.

    PYTHONPATH=src .venv/bin/python benchmarks/expertlongbench/study9/measure.py \
        --sheet ~/Documents/Crossaudit/study-data/gold-containment/sheet.jsonl

Four quantities, `CONTAINMENT_RULE.md` §3 plus the two a narrowing needs:

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
from crossaudit.dcl.numbers import contains_pair            # noqa: E402


#: Bound once, before any configuration replaces the module attribute.
_CANDIDATES = N._unit_candidates


def _shipped(rest):
    """The shipped `_unit_candidates`: the whole spaced expression, nothing
    shorter."""
    return _CANDIDATES(rest)


def _narrowing_only(rest):
    """HALF 1 alone. The bare first token stops being a reading where a
    continuation follows, and no join replaces it — E4 is not applied."""
    cands = _CANDIDATES(rest)
    parts, _end = N._spaced_unit(rest)
    return [] if len(parts) > 1 else cands


def _e4_only(rest):
    """HALF 2 alone, which is what `study8gold/simulate.py` measured as E4: the
    join is offered as a FURTHER candidate and the bare first token survives
    beside it."""
    cands = _CANDIDATES(rest)
    parts, end = N._spaced_unit(rest)
    if len(parts) > 1:
        token, after = N.unit_token(rest)
        cands = [(token, len(rest) - len(after))] + cands
    return cands


CONFIGS = {"shipped": _shipped, "narrowing": _narrowing_only, "e4": _e4_only}

GOLD = HERE.parent / "study8gold" / "GOLD.csv"
KEY = HERE.parent / "study8gold" / "key.jsonl"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True, type=Path)
    ap.add_argument("--config", choices=sorted(CONFIGS), default="shipped",
                    help="shipped = both halves; narrowing = half 1 alone; "
                         "e4 = half 2 alone, the bare token surviving beside "
                         "the join (what study8gold/simulate.py called E4)")
    args = ap.parse_args(argv)

    N._unit_candidates = CONFIGS[args.config]

    items = [json.loads(l) for l in
             args.sheet.expanduser().read_text(encoding="utf-8").splitlines() if l.strip()]
    key = {r["id"]: r for r in (json.loads(l) for l in
           KEY.read_text(encoding="utf-8").splitlines() if l.strip())}
    gold = {}
    for line in GOLD.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            parts = line.split(",")
            gold[parts[0].strip()] = parts[1].strip()

    R, W, Rp, Wp = [], [], [], []
    for it in items:
        was, now = key[it["id"]]["matcher"], contains_pair(it["line"], it["v"], it["u"])
        if was == now:
            continue
        label = gold[it["id"]]
        if now:                                  # block -> pass
            (R if label == "C" else W).append(it)
        else:                                    # pass -> block
            (Wp if label == "C" else Rp).append(it)

    print(f"config {args.config}   items {len(items)}   "
          f"R {len(R)}   W {len(W)}   R' {len(Rp)}   W' {len(Wp)}")
    print("KILL" if (W or Wp) else "kill conditions clear (W = 0 and W' = 0)")

    right_blocks = [i for i, r in key.items() if r["kind"] == "block" and gold[i] == "N"]
    by_id = {it["id"]: it for it in items}
    still = [i for i in right_blocks
             if not contains_pair(by_id[i]["line"], by_id[i]["v"], by_id[i]["u"])]
    print(f"gold-right blocks still blocking: {len(still)}/{len(right_blocks)}")

    panel = [it for it in items if key[it["id"]]["kind"] == "panel"]
    passes = [it for it in panel if contains_pair(it["line"], it["v"], it["u"])]
    wrong = [it for it in passes if gold[it["id"]] == "N"]
    print(f"panel: {len(passes)}/{len(panel)} contained, of which gold-wrong {len(wrong)}")

    for name, rows in (("R", R), ("W", W), ("R'", Rp), ("W'", Wp)):
        for it in rows:
            print(f"  {name}  {it['id']}  {key[it['id']]['kind']:<5} "
                  f"v={it['v']!r} u={it['u']!r}  {it['line'][:90]}")
    return 1 if (W or Wp) else 0


if __name__ == "__main__":
    raise SystemExit(main())
