#!/usr/bin/env python3
"""Every count in `docs/design/CONTAINMENT_RULE.md`, from the committed rows.

**Corpus-free.** It reads `study8/rows.jsonl` only — arm, disposition, class and
substratum, never a transcribed value, unit or quote (those are sha256 in the
record and are not needed here). It takes no run directory, opens no draft, and
makes no model call.

The design note re-groups Arm 3's 53 blocks by the *matcher mechanism* that
fired, which the committed `substratum` column cannot express: three of its six
classes each hold two unrelated mechanisms. That regrouping was read off the
archived drafts by hand and is carried here as `MECHANISM` — a table of row
identities and a label, no corpus text — so the note's arithmetic is
reproducible from a checkout with no corpus present.

    python3 benchmarks/expertlongbench/study8/containment_classes.py
"""
from __future__ import annotations

import collections
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent

#: `(instance, arm, row) -> mechanism`, for the 53 Arm 3 blocks. Read from the
#: archived drafts by hand (`~/Documents/Crossaudit/study-data/wt-arm3-runs/`,
#: not redistributed); the identities are the same triples `rows.jsonl` carries.
#: See CONTAINMENT_RULE.md §1 for what each label means.
MECHANISM: dict[tuple[str, str, int], str] = {
    ("10.1002/adfm.202002249", "A", 15): "M1a", ("10.1002/adfm.202002249", "A", 16): "M1a",
    ("10.1002/adfm.202002249", "B", 2): "M7",   ("10.1002/adfm.202002249", "B", 5): "M7",
    ("10.1002/adfm.202402444", "B", 6): "M5",
    ("10.1002/adfm.202402444", "B", 15): "M1a", ("10.1002/adfm.202402444", "B", 16): "M1a",
    ("10.1002/adfm.202402444", "B", 17): "M1a",
    ("10.1002/adfm.202209924", "A", 4): "M1b",  ("10.1002/adfm.202209924", "B", 4): "M1b",
    ("10.1002/advs.202406453", "A", 0): "M2",   ("10.1002/advs.202406453", "B", 0): "M9b",
    ("10.1002/aic.18378", "A", 11): "M3",       ("10.1002/aic.18378", "A", 12): "M3",
    ("10.1002/aic.18378", "A", 13): "M3",       ("10.1002/aic.18378", "A", 14): "M6",
    ("10.1002/aic.18378", "A", 19): "M2",
    ("10.1002/aic.18378", "A", 23): "M1a",      ("10.1002/aic.18378", "A", 24): "M1a",
    ("10.1002/aic.18378", "B", 8): "M11",
    ("10.1002/batt.202100174", "A", 0): "M2",
    ("10.1002/batt.202100174", "A", 2): "M1a",  ("10.1002/batt.202100174", "A", 3): "M1a",
    ("10.1002/batt.202100174", "B", 0): "M1a",  ("10.1002/batt.202100174", "B", 1): "M1a",
    ("10.1002/batt.202100174", "B", 2): "M2",
    ("10.1002/batt.202200056", "A", 7): "M2",
    ("10.1002/batt.202200056", "A", 12): "M5",  ("10.1002/batt.202200056", "A", 14): "M5",
    ("10.1002/batt.202200056", "A", 15): "M2",
    ("10.1002/batt.202200056", "B", 6): "M2",
    ("10.1002/batt.202200056", "B", 11): "M5",  ("10.1002/batt.202200056", "B", 13): "M5",
    ("10.1002/batt.202200056", "B", 14): "M2",
    ("10.1002/celc.202200772", "A", 0): "M8",   ("10.1002/celc.202200772", "B", 0): "M8",
    ("10.1002/celc.202200772", "B", 4): "M5",
    ("10.1002/chem.201905217", "A", 1): "M2",   ("10.1002/chem.201905217", "B", 0): "M2",
    ("10.1002/cjce.23950", "A", 3): "M2",       ("10.1002/cjce.23950", "B", 0): "M2",
    ("10.1002/cjce.23950", "A", 7): "M4",       ("10.1002/cjce.23950", "B", 4): "M4",
    ("10.1002/cjce.23950", "A", 11): "M9c",     ("10.1002/cjce.23950", "A", 15): "M9c",
    ("10.1002/cjce.24030", "A", 5): "M2",       ("10.1002/cjce.24030", "B", 5): "M2",
    ("10.1002/jbm.a.36681", "A", 5): "M3",      ("10.1002/jbm.a.36681", "B", 5): "M3",
    ("10.1002/smll.201800441", "B", 0): "M1b",
    ("10.1002/smll.201800441", "B", 1): "M11",
    ("10.1002/smll.201800441", "B", 4): "M7",
    ("10.1002/zaac.202200095", "B", 6): "M9a",
}

#: The disposition each mechanism carries in CONTAINMENT_RULE.md §2, and the
#: wave it ships in (0 = never, or already ruled elsewhere).
DISPOSITION = {
    "M1a": ("(b) decimals only / (c) integers", 3),
    "M1b": ("(c) words, (a) wrong quote", 0),
    "M2":  ("(b) E1", 2),
    "M3":  ("(b) E2", 2),
    "M4":  ("(a) + skill sentence", 0),
    "M5":  ("(b) E4", 1),
    "M6":  ("(b) E5", 1),
    "M7":  ("(a)", 0),
    "M8":  ("(a)", 0),
    "M9a": ("(a)", 0),
    "M9b": ("(c)", 0),
    "M9c": ("(b) E6", 1),
    "M11": ("D159 ruling 1", 0),
}
#: Rows the skill changes could plausibly move (§5's last sentence): the
#: generator's own re-notations, not the matcher's readings.
SKILL_REACHABLE = ("M7", "M8")


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for a binomial proportion, in percent."""
    p = k / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((centre - half) / denom * 100, (centre + half) / denom * 100)


def main(argv=None) -> int:
    rows = [json.loads(line) for line in
            (HERE / "rows.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    resolvable = [r for r in rows if r["resolved_location"]]
    blocks = [r for r in rows if r["severity"] == "BLOCKER"]
    n = len(resolvable)

    print(f"rows {len(rows)}   resolvable {n}   pass {n - len(blocks)}   block {len(blocks)}")
    print(f"arms {dict(collections.Counter(r['arm'] for r in rows))}")

    print("\nsubstratum (committed, exploratory) x arm")
    subs = collections.Counter((r["substratum"], r["arm"]) for r in blocks)
    for name in sorted({s for s, _ in subs}):
        a, b = subs.get((name, "A"), 0), subs.get((name, "B"), 0)
        print(f"  {name:<28} A {a:>2}  B {b:>2}  total {a + b:>2}")

    print("\nmechanism (CONTAINMENT_RULE.md §1) x arm")
    missing = [r for r in blocks
               if (r["instance"].split("-", 1)[1], r["arm"], r["row"]) not in MECHANISM]
    if missing:
        print(f"  !! {len(missing)} blocks have no mechanism label", file=sys.stderr)
        return 1
    mech = collections.Counter(
        (MECHANISM[(r["instance"].split("-", 1)[1], r["arm"], r["row"])], r["arm"])
        for r in blocks)
    for name in sorted({m for m, _ in mech}, key=lambda m: -sum(
            v for (k, _), v in mech.items() if k == m)):
        a, b = mech.get((name, "A"), 0), mech.get((name, "B"), 0)
        disp, wave = DISPOSITION[name]
        print(f"  {name:<4} A {a:>2}  B {b:>2}  total {a + b:>2}   {disp:<34} wave {wave}")

    print("\nfalse-blocker rate over resolvable rows, by wave (§5)")
    by_wave = collections.Counter(
        DISPOSITION[MECHANISM[(r["instance"].split("-", 1)[1], r["arm"], r["row"])]][1]
        for r in blocks)
    remaining, seen = len(blocks), []
    stages = [("shipped matcher", None), ("+ D159 ruling 1 (cap)", "cap")]
    for label, tag in stages:
        if tag == "cap":
            remaining -= sum(1 for r in blocks if MECHANISM[
                (r["instance"].split("-", 1)[1], r["arm"], r["row"])] == "M11")
        lo, hi = wilson(remaining, n)
        print(f"  {label:<24} {remaining:>2}/{n} = {remaining / n * 100:5.2f}%  [{lo:.2f}, {hi:.2f}]")
    for wave in (1, 2, 3):
        remaining -= by_wave.get(wave, 0)
        seen.append(wave)
        lo, hi = wilson(remaining, n)
        print(f"  {'+ wave ' + str(wave):<24} {remaining:>2}/{n} = {remaining / n * 100:5.2f}%  [{lo:.2f}, {hi:.2f}]")
    skill = sum(1 for r in blocks if MECHANISM[
        (r["instance"].split("-", 1)[1], r["arm"], r["row"])] in SKILL_REACHABLE)
    remaining -= skill
    lo, hi = wilson(remaining, n)
    print(f"  {'+ skill fixes M7, M8':<24} {remaining:>2}/{n} = {remaining / n * 100:5.2f}%  [{lo:.2f}, {hi:.2f}]")

    print("\nadjudicator agreement (§3): adj_a is the containment rule, adj_b the")
    print("naive substring test; every disagreement falls on a blocked row.")
    agree = collections.Counter(
        (r["arm"], r["adj_a"], r["adj_b"], r["severity"]) for r in resolvable)
    for key in sorted(agree, key=str):
        print(f"  arm {key[0]}  adj_a {str(key[1]):<5} adj_b {str(key[2]):<5} {key[3]:<8} {agree[key]:>3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
