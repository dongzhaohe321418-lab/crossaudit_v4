#!/usr/bin/env python3
"""Agreement between the two blinded labellers, and the gold after adjudication.

Corpus-free: reads `L1.csv`, `L2.csv`, the optional `GOLD.csv` and `key.jsonl`,
all of which carry ids and labels only.

    python3 agreement.py [--disagreements]
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LABELS = ("C", "N", "?")


def read(name: str) -> dict[str, tuple[str, str]]:
    out = {}
    for line in (HERE / name).read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            i, lab, rule = (line.split(",") + ["", ""])[:3]
            out[i.strip()] = (lab.strip(), rule.strip())
    return out


def kappa(a: list[str], b: list[str]) -> tuple[float, float, float]:
    """Cohen's kappa over the observed categories, with its asymptotic SE."""
    n = len(a)
    cats = sorted(set(a) | set(b))
    obs = sum(1 for x, y in zip(a, b) if x == y) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    exp = sum((ca[c] / n) * (cb[c] / n) for c in cats)
    if exp >= 1.0:
        return float("nan"), obs, exp
    k = (obs - exp) / (1 - exp)
    se = math.sqrt(obs * (1 - obs) / (n * (1 - exp) ** 2))
    return k, obs, exp, se


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--disagreements", action="store_true")
    args = ap.parse_args(argv)

    l1, l2 = read("L1.csv"), read("L2.csv")
    key = {r["id"]: r for r in (json.loads(l) for l in
           (HERE / "key.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
    ids = sorted(key)
    assert set(ids) == set(l1) == set(l2), "label sets do not cover the corpus"

    def report(name: str, subset: list[str]) -> None:
        a = [l1[i][0] for i in subset]
        b = [l2[i][0] for i in subset]
        k, obs, exp, se = kappa(a, b)
        print(f"  {name:<28} n {len(subset):>3}   raw {obs * 100:6.2f}%   "
              f"kappa {k:6.3f}  (SE {se:.3f}, 95% {k - 1.96 * se:.3f}-{k + 1.96 * se:.3f})")

    print("L1 x L2 agreement")
    report("overall", ids)
    for kind in ("block", "pass", "panel"):
        report(kind, [i for i in ids if key[i]["kind"] == kind])

    print("\nconfusion (rows L1, cols L2)")
    conf = collections.Counter((l1[i][0], l2[i][0]) for i in ids)
    print("        " + "".join(f"{c:>6}" for c in LABELS))
    for r in LABELS:
        print(f"  L1 {r:<3}" + "".join(f"{conf.get((r, c), 0):>6}" for c in LABELS))

    dis = [i for i in ids if l1[i][0] != l2[i][0]]
    print(f"\ndisagreements: {len(dis)}")
    if args.disagreements:
        for i in dis:
            print(f"  {i}  L1 {l1[i][0]}/{l1[i][1]:<4} L2 {l2[i][0]}/{l2[i][1]:<4} "
                  f"[{key[i]['kind']}, matcher {key[i]['matcher']}]")

    gold_path = HERE / "GOLD.csv"
    if gold_path.exists():
        gold = read("GOLD.csv")
        print(f"\ngold: {collections.Counter(v[0] for v in gold.values())}")
        for kind in ("block", "pass", "panel"):
            sub = [i for i in ids if key[i]["kind"] == kind]
            c = collections.Counter(gold[i][0] for i in sub)
            print(f"  {kind:<8} n {len(sub):>3}  C {c['C']:>3}  N {c['N']:>3}  ? {c['?']:>3}")
        print("\nshipped matcher against the gold, over the whole corpus")
        cm = collections.Counter((key[i]["matcher"], gold[i][0]) for i in ids)
        print(f"  matcher PASS & gold C (right pass)  {cm[(True, 'C')]:>3}")
        print(f"  matcher PASS & gold N (WRONG pass)  {cm[(True, 'N')]:>3}")
        print(f"  matcher BLOCK & gold C (WRONG block){cm[(False, 'C')]:>3}")
        print(f"  matcher BLOCK & gold N (right block) {cm[(False, 'N')]:>3}")
        print(f"  undecided by the rule                {cm[(True, '?')] + cm[(False, '?')]:>3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
