"""Study 4's analysis, reading only the committed records.jsonl.

Every test, effect size and interval named in PREREGISTRATION.md is computed
here. Exact p values, a CI beside every effect, n for every cell, and a count of
every comparison the study made.
"""
from __future__ import annotations

import json
import math
import random
import statistics as st
import sys
from collections import defaultdict
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOT_SEED = 20261104
BOOT_N = 20000

COMPARISONS: list[str] = []


def wilcoxon_exact(xs):
    """Two-sided exact signed-rank. Ties (zeros) dropped; count returned."""
    dropped = sum(1 for x in xs if x == 0)
    xs = [x for x in xs if x != 0]
    n = len(xs)
    if n == 0:
        return 1.0, 0, dropped
    order = sorted(range(n), key=lambda i: abs(xs[i]))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(xs[order[j + 1]]) == abs(xs[order[i]]):
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    total = sum(ranks)
    w = min(sum(ranks[i] for i in range(n) if xs[i] > 0),
            sum(ranks[i] for i in range(n) if xs[i] < 0))
    if n <= 22:
        hit = sum(1 for signs in product((0, 1), repeat=n)
                  if min(s := sum(ranks[i] for i in range(n) if signs[i]), total - s) <= w)
        return hit / (2 ** n), n, dropped
    mu, sd = n * (n + 1) / 4, math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    z = (w - mu) / sd
    return 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2)))), n, dropped


def bca(xs, stat=st.mean, alpha=0.05):
    """BCa bootstrap CI. Returns (lo, hi) or (nan, nan) when n < 3."""
    n = len(xs)
    if n < 3:
        return float("nan"), float("nan")
    rng = random.Random(BOOT_SEED)
    theta = stat(xs)
    boots = sorted(stat([xs[rng.randrange(n)] for _ in range(n)]) for _ in range(BOOT_N))
    prop = sum(1 for b in boots if b < theta) / BOOT_N
    if prop in (0.0, 1.0):
        lo_i = int(alpha / 2 * BOOT_N)
        hi_i = min(BOOT_N - 1, int((1 - alpha / 2) * BOOT_N))
        return boots[lo_i], boots[hi_i]

    def phi_inv(p):                      # Acklam-free: bisection on erf
        lo, hi = -8.0, 8.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < p:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    def phi(z):
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))

    z0 = phi_inv(prop)
    jack = [stat(xs[:i] + xs[i + 1:]) for i in range(n)]
    jbar = st.mean(jack)
    num = sum((jbar - j) ** 3 for j in jack)
    den = 6 * (sum((jbar - j) ** 2 for j in jack) ** 1.5)
    a = num / den if den else 0.0
    out = []
    for q in (alpha / 2, 1 - alpha / 2):
        zq = phi_inv(q)
        adj = phi(z0 + (z0 + zq) / (1 - a * (z0 + zq)))
        out.append(boots[min(BOOT_N - 1, max(0, int(adj * BOOT_N)))])
    return out[0], out[1]


def report_paired(label, xs, *, primary=False):
    COMPARISONS.append(label)
    if not xs:
        print(f"  {label}: n=0 — no pairs")
        return
    p, usable, dropped = wilcoxon_exact(xs)
    lo, hi = bca(list(xs))
    tag = "  <-- PRIMARY OUTCOME" if primary else ""
    print(f"  {label}: n={len(xs)}  mean {100*st.mean(xs):+.2f} F1  "
          f"95% CI [{100*lo:+.2f}, {100*hi:+.2f}]  "
          f"better/worse/tied {sum(1 for x in xs if x>0)}/{sum(1 for x in xs if x<0)}/{dropped}  "
          f"exact Wilcoxon p={p:.4f} (n={usable} usable){tag}")


def main(path=None):
    rows = [json.loads(l) for l in (Path(path) if path else HERE / "records.jsonl").read_text().splitlines() if l.strip()]
    arms = defaultdict(dict)
    for r in rows:
        arms[r["arm"]][r["instance_id"]] = r
    print(f"records: {len(rows)} rows, arms {sorted(arms)}\n")

    for arm in sorted(arms):
        rs = list(arms[arm].values())
        print(f"=== arm {arm} (n={len(rs)}) ===")
        r1 = [r["per_round"]["1"]["f1"] for r in rs if "1" in r["per_round"]]
        fin = [r["final"]["f1"] for r in rs]
        print(f"  round-1 draft F1 {100*st.mean(r1):.2f} (n={len(r1)})   "
              f"final F1 {100*st.mean(fin):.2f} (n={len(fin)})")
        revs = [r["revision"]["delta_f1"] for r in rs if r.get("revision")]
        fixed = sum(len(r["revision"]["items_fixed"]) for r in rs if r.get("revision"))
        broken = sum(len(r["revision"]["items_broken"]) for r in rs if r.get("revision"))
        print(f"  revised {len(revs)}/{len(rs)}   items fixed {fixed}  broken {broken}")
        report_paired(f"arm {arm} PAIRED REVISION DELTA", revs, primary=True)
        named = sum(x["n_wrong_and_named"] for r in rs for x in (r["audit_recall"] or []) if x["round"] == 1)
        wrong = sum(x["n_items_wrong"] for r in rs for x in (r["audit_recall"] or []) if x["round"] == 1)
        print(f"  auditor round-1 recall {named}/{wrong} = {100*named/max(wrong,1):.1f}%")
        tp = sum(1 for r in rs for a in (r["adjudications"] or []) if a.get("verdict") == "confirmed")
        fp = sum(1 for r in rs for a in (r["adjudications"] or []) if a.get("verdict") == "false_positive")
        print(f"  auditor precision {tp}/{tp+fp} = {100*tp/max(tp+fp,1):.1f}%  (confirmed {tp}, false-positive {fp})")
        g = [v for r in rs for v in (r["committed_growth"] or {}).values() if v is not None]
        if g:
            print(f"  committed round transitions {len(g)}  mean growth {100*st.mean(g):+.1f}%  "
                  f"max {100*max(g):+.1f}%  over 25%: {sum(1 for v in g if v > 0.25)}")
        ec = defaultdict(int)
        for r in rs:
            ec[r["exit_code"]] += 1
        print(f"  exit codes {dict(sorted(ec.items(), key=lambda kv: (kv[0] is None, kv[0])))}")
        cg = sum(r["cost_usd"]["generation_and_audit"] or 0 for r in rs)
        cs = sum(r["cost_usd"]["clear_scoring"] or 0 for r in rs)
        ti = sum(r["tokens"]["input"] or 0 for r in rs)
        to = sum(r["tokens"]["output"] or 0 for r in rs)
        print(f"  cost ${cg:.2f} + ${cs:.2f} = ${cg+cs:.2f}  (${(cg+cs)/max(len(rs),1):.3f}/instance)  "
              f"tokens in {ti} out {to}  mean wall {st.mean([r['wall_s'] for r in rs]):.0f}s\n")

    if "C" in arms and "T" in arms:
        print("=== C -> T, paired on the same instances ===")
        common = sorted(set(arms["C"]) & set(arms["T"]))
        print(f"  instances in both arms: {len(common)}")
        for label, key in (("round-1 draft", lambda r: r["per_round"].get("1", {}).get("f1")),
                           ("final output ", lambda r: r["final"]["f1"])):
            xs = [key(arms["T"][s]) - key(arms["C"][s]) for s in common
                  if key(arms["C"][s]) is not None and key(arms["T"][s]) is not None]
            report_paired(label, xs)
        both = [s for s in common if arms["C"][s].get("revision") and arms["T"][s].get("revision")]
        xs = [arms["T"][s]["revision"]["delta_f1"] - arms["C"][s]["revision"]["delta_f1"] for s in both]
        report_paired("revision delta, instances revised in BOTH arms", xs)

    print(f"\ncomparisons this study made: {len(COMPARISONS)}")
    for c in COMPARISONS:
        print(f"  - {c}")


if __name__ == "__main__":
    main(*sys.argv[1:])
