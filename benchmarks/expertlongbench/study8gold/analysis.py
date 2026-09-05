#!/usr/bin/env python3
"""Every number in RESULTS-GOLD.md, from the committed labels and key.

Needs the sheet (archive-only, carries corpus text) because the extension
simulation must re-read the located text. It prints nothing from it.

    PYTHONPATH=src python3 analysis.py \
        --sheet ~/Documents/Crossaudit/study-data/gold-containment/sheet.jsonl
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import math
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent.parent / "src"))
import simulate as S                                                # noqa: E402

_cc = importlib.util.spec_from_file_location(
    "cc", HERE.parent / "study8" / "containment_classes.py")
CC = importlib.util.module_from_spec(_cc); _cc.loader.exec_module(CC)

#: Arm 3's own denominators (RESULTS-ARM3 §1, §3).
N_RESOLVABLE, N_BLOCK, N_PASS = 401, 53, 348
BOOT, SEED = 10000, 20260906


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d * 100, (c + h) / d * 100)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True, type=pathlib.Path)
    args = ap.parse_args(argv)

    sheet = {json.loads(l)["id"]: json.loads(l)
             for l in args.sheet.read_text(encoding="utf-8").splitlines() if l.strip()}
    key = {r["id"]: r for r in (json.loads(l) for l in
           (HERE / "key.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
    gold = {l.split(",")[0]: l.split(",")[1]
            for l in (HERE / "GOLD.csv").read_text(encoding="utf-8").splitlines() if l.strip()}
    hit = lambda i, e: S.contains_pair(sheet[i]["line"], sheet[i]["v"], sheet[i]["u"], e)

    blocks = [i for i in key if key[i]["kind"] == "block"]
    passes = [i for i in key if key[i]["kind"] == "pass"]
    panel = [i for i in key if key[i]["kind"] == "panel"]
    mech = {i: CC.MECHANISM.get((key[i]["instance"], key[i]["arm"], key[i]["row"]))
            for i in blocks}

    print("=== 1. the gold, by stratum ===")
    for name, sub in (("block", blocks), ("pass", passes), ("panel", panel)):
        c = collections.Counter(gold[i] for i in sub)
        print(f"  {name:<6} n {len(sub):>3}   C {c['C']:>3}   N {c['N']:>3}   ? {c['?']:>3}")

    print("\n=== 2. the 53 blocks, by mechanism (CONTAINMENT_RULE §1) ===")
    t = collections.Counter((mech[i], gold[i]) for i in blocks)
    for m in sorted({m for m, _ in t}, key=lambda m: -sum(v for (k, _), v in t.items() if k == m)):
        print(f"  {m:<4} wrong block (gold C) {t.get((m, 'C'), 0):>2}   right block (gold N) "
              f"{t.get((m, 'N'), 0):>2}   {CC.DISPOSITION[m][0]}")

    print("\n=== 3. the shipped matcher against the gold ===")
    cm = collections.Counter((key[i]["matcher"], gold[i]) for i in key)
    print(f"  right pass  {cm[(True, 'C')]:>3}    WRONG pass  {cm[(True, 'N')]:>3}")
    print(f"  right block {cm[(False, 'N')]:>3}    WRONG block {cm[(False, 'C')]:>3}")
    wp = [i for i in passes if key[i]["matcher"] and gold[i] == "N"]
    lo, hi = wilson(len(wp), len(passes))
    print(f"  wrong passes in the pass stratum {len(wp)}/{len(passes)} = "
          f"{len(wp) / len(passes) * 100:.2f}% [{lo:.2f}, {hi:.2f}]")

    print("\n=== 4. R and W per extension, with the kill applied ===")
    print(f"  {'extension':<30} {'new':>4} {'R':>4} {'W':>4} {'R-W':>5}  verdict")
    for name, ext in S.SETS.items():
        newly = [i for i in key if hit(i, ext) and not key[i]["matcher"]]
        R = sum(1 for i in newly if key[i]["kind"] == "block" and gold[i] == "C")
        W = sum(1 for i in newly if gold[i] == "N")
        unk = sum(1 for i in newly if gold[i] == "?")
        v = "KILLED" if W else ("undecided" if unk else "licensed")
        print(f"  {name:<30} {len(newly):>4} {R:>4} {W:>4} {R - W:>5}  {v}")

    print("\n=== 5. the negative panel: coincidental containment, line-scoped ===")
    for name, ext in [("shipped", frozenset())] + list(S.SETS.items()):
        h = [i for i in panel if hit(i, ext)]
        bad = [i for i in h if gold[i] == "N"]
        lo, hi = wilson(len(h), len(panel))
        lo2, hi2 = wilson(len(bad), len(panel))
        print(f"  {name:<30} contains {len(h):>2}/{len(panel)} = {len(h) / len(panel) * 100:5.2f}% "
              f"[{lo:.2f}, {hi:.2f}]   wrong {len(bad)} = {len(bad) / len(panel) * 100:.2f}% "
              f"[{lo2:.2f}, {hi2:.2f}]")

    print("\n=== 6. block rate over the 401 resolvable rows, and how much of it is wrong ===")
    for name, ext in [("shipped matcher (contains_pair only)", frozenset())] + list(S.SETS.items()):
        rem = [i for i in blocks if not hit(i, ext)]
        lo, hi = wilson(len(rem), N_RESOLVABLE)
        print(f"  {name:<30} {len(rem):>2}/{N_RESOLVABLE} = {len(rem) / N_RESOLVABLE * 100:5.2f}% "
              f"[{lo:.2f}, {hi:.2f}]   wrong blocks among them {sum(1 for i in rem if gold[i] == 'C')}")

    print("\n=== 7. PROVENANCE_CHECKS §6's estimand: of rows that DO trace, the fraction blocked ===")
    print("  numerator: wrong blocks, scaled from the block census.")
    print("  denominator: those, plus the gold-C fraction of the pass sample scaled to 348.")
    print(f"  draft-clustered percentile bootstrap, {BOOT} resamples of the 48 draft-arms.")
    drafts = sorted({(key[i]["instance"], key[i]["arm"]) for i in blocks + passes})
    by: dict = {d: [] for d in drafts}
    for i in blocks + passes:
        by[(key[i]["instance"], key[i]["arm"])].append(i)

    def rate(ids, ext):
        b = [i for i in ids if key[i]["kind"] == "block"]
        p = [i for i in ids if key[i]["kind"] == "pass"]
        if not b or not p:
            return None
        wrongb = sum(1 for i in b if not hit(i, ext) and gold[i] == "C")
        num = wrongb * N_BLOCK / len(b)
        den = num + sum(1 for i in p if gold[i] == "C") / len(p) * N_PASS
        return num / den * 100 if den else None

    rng = random.Random(SEED)
    everything = blocks + passes
    for name, ext in [("shipped matcher", frozenset()),
                      ("wave 1 = E4+E5+E6", S.SETS["wave 1 = E4+E5+E6"]),
                      ("wave 1+2 = +E1+E2", S.SETS["wave 1+2 = +E1+E2"]),
                      ("all = +E3", S.SETS["all = +E3"])]:
        # Scope: `contains_pair` alone. The two 80-character-cap blocks are not
        # containment blocks at all — the matcher passes their located text —
        # so they never appear in a numerator here (D159 ruling 1 removes them).
        ext2, pool = ext, everything
        pt = rate(pool, ext2)
        boot = []
        for _ in range(BOOT):
            rs = []
            for _ in drafts:
                rs.extend(x for x in by[rng.choice(drafts)] if x in set(pool))
            r = rate(rs, ext2)
            if r is not None:
                boot.append(r)
        boot.sort()
        lo, hi = boot[int(.025 * len(boot))], boot[int(.975 * len(boot))]
        print(f"  {name:<30} {pt:5.2f}%  [{lo:.2f}, {hi:.2f}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
