"""What combining K identical audit runs buys — from study 6's committed rows.

No model call. Reproduces every number cited in docs/design/AUDIT_ARCHITECTURE.md
§3 and §5 from ``study6/noise-rep*.rows.jsonl`` alone.

Two results, and the second qualifies the first:

* Union of K runs raises pooled recall substantially (22.4 -> 38.8 at K=4).
* Findings raised on EVERY run are correct far less often than the rest
  (45% against 88%, Fisher exact p = 0.0014). Unanimity marks a reflex.

Read with the base rate in view: 98 of 120 rubric items in this sample are
wrong, so a randomly named item is 81.7% likely to be correct-to-flag. The
apparent precision rise under union is dilution against that base rate, and
the code harness (model-free truth) shows union buying recall at a
proportional false-positive cost instead. The recall gain is real in both
domains; the precision gain is not. See the design doc.
"""
from __future__ import annotations

import glob
import itertools
import json
import math
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


def load_replicates() -> tuple[list[str], list[str], dict[str, dict[str, dict]]]:
    reps: dict[str, dict[str, dict]] = defaultdict(dict)
    for path in sorted(glob.glob(os.path.join(HERE, "noise-rep*.rows.jsonl"))):
        rep = os.path.basename(path).split(".")[0].split("-fill")[0]
        for line in open(path):
            row = json.loads(line)
            audit = row.get("audit") or {}
            prev = reps[rep].get(row["instance_id"])
            # A successful audit supersedes a failed one whatever the file
            # order: the fill passes sort BEFORE the main pass alphabetically.
            if prev is None or (audit.get("ok") and not (prev.get("audit") or {}).get("ok")):
                reps[rep][row["instance_id"]] = row
    order = sorted(reps)
    instances = sorted(set.intersection(*(set(v) for v in reps.values())))
    return order, instances, reps


def named_items(row: dict, rubric: set[str]) -> set[str]:
    out: set[str] = set()
    for finding in row.get("findings") or []:
        out |= set(finding.get("items_rule_mapping") or [])
    return out & rubric


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    def p(a, b, c, d):
        return math.comb(a + b, a) * math.comb(c + d, c) / math.comb(a + b + c + d, a + c)
    obs = p(a, b, c, d)
    total = 0.0
    for x in range(0, min(a + b, a + c) + 1):
        y, z = a + b - x, a + c - x
        w = c + d - z
        if min(y, z, w) < 0:
            continue
        q = p(x, y, z, w)
        if q <= obs + 1e-12:
            total += q
    return total


def main() -> None:
    order, instances, reps = load_replicates()
    wrong: dict[str, set[str]] = {}
    named: dict[str, dict[str, set[str]]] = defaultdict(dict)
    for inst in instances:
        per = (reps[order[0]][inst].get("clear") or {}).get("per_item", {})
        wrong[inst] = {k for k, v in per.items() if not v.get("correct")}
        for rep in order:
            named[rep][inst] = named_items(reps[rep][inst], set(per))
    n_wrong = sum(len(wrong[i]) for i in instances)
    n_items = sum(len((reps[order[0]][i].get("clear") or {}).get("per_item", {})) for i in instances)
    print(f"instances {len(instances)}   wrong items {n_wrong}/{n_items} "
          f"(base rate {100 * n_wrong / n_items:.1f}%)\n")

    def score(sel):
        hit = sum(len(sel[i] & wrong[i]) for i in instances)
        tot = sum(len(sel[i]) for i in instances)
        return 100 * hit / n_wrong, (100 * hit / tot if tot else float("nan")), tot

    print(f"{'strategy':22s} {'recall%':>8s} {'prec%':>7s} {'flags':>6s}")
    for rep in order:
        r, p, t = score(named[rep])
        print(f"{'single ' + rep[-4:]:22s} {r:8.1f} {p:7.1f} {t:6d}")
    for k in (2, 3, 4):
        for threshold, label in ((1, "union"), (k, "unanimous")):
            vals = []
            for combo in itertools.combinations(order, k):
                sel = {i: {x for x in set().union(*(named[r][i] for r in combo))
                           if sum(x in named[r][i] for r in combo) >= threshold}
                       for i in instances}
                vals.append(score(sel))
            m = [sum(v[j] for v in vals) / len(vals) for j in range(3)]
            print(f"{label + f'-of-{k}':22s} {m[0]:8.1f} {m[1]:7.1f} {m[2]:6.1f}")

    # precision by how many of the K runs named the item
    tally: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    for inst in instances:
        per = (reps[order[0]][inst].get("clear") or {}).get("per_item", {})
        count: dict[str, int] = defaultdict(int)
        for rep in order:
            for x in named[rep][inst]:
                count[x] += 1
        for x, j in count.items():
            tally[j][1] += 1
            if not per[x].get("correct"):
                tally[j][0] += 1
    print(f"\n{'named in j of K runs':22s} {'correct':>8s} {'total':>6s} {'prec%':>7s}")
    for j in sorted(tally):
        w, t = tally[j]
        print(f"{j:22d} {w:8d} {t:6d} {100 * w / t:7.1f}")
    k = len(order)
    w4, t4 = tally[k]
    wo = sum(tally[j][0] for j in tally if j < k)
    to = sum(tally[j][1] for j in tally if j < k)
    p = fisher_two_sided(w4, t4 - w4, wo, to - wo)
    print(f"\nunanimous {w4}/{t4} = {100 * w4 / t4:.0f}%  vs  not {wo}/{to} = {100 * wo / to:.0f}%"
          f"   Fisher exact two-sided p = {p:.4f}")


if __name__ == "__main__":
    main()
