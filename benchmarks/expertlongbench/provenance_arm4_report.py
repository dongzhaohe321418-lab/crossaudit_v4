#!/usr/bin/env python3
"""Arm 4's numbers, from the run records and the gold labels (PREREGISTRATION-ARM4).

Corpus-free: reads `records.jsonl` (digests, dispositions, adjudications),
`study8/key-arm4.jsonl` (item ids and identities) and `study8/GOLD-arm4.csv`
(id, label, rule). Every rate carries the Wilson 95% score interval for a
binomial proportion of annotation rows and, beside it, a draft-clustered 95%
percentile bootstrap (10,000 resamples of the drafts, seed 20261106).

    python3 benchmarks/expertlongbench/provenance_arm4_report.py <run-dir> [--json out]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from provenance_arm1 import wilson                                  # noqa: E402
from provenance_arm3_report import disposition                      # noqa: E402

BLOCKER, ADVISORY, PASS = "BLOCKER", "ADVISORY", "PASS"
RESAMPLES = 10_000
SEED = 20261106
ARM3_UNCITED = {"A": 10.68, "B": 6.80}


def load_records(run_dir: Path) -> list[dict]:
    path = run_dir / "records.jsonl"
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


#: Which arm's key and gold this report reads; Arm 5 (`provenance_arm5.py`) reuses
#: this report with `--arm 5` — its files are `key-arm5.jsonl` / `GOLD-arm5.csv`.
ARM_SUFFIX = "arm4"


def load_labels() -> dict[tuple[str, int], tuple[str, str, str]]:
    """(instance, row) -> (kind, label, rule). Items with no located line are
    `block-no-location` and carry the label N by definition (§3)."""
    key_path = HERE / "study8" / f"key-{ARM_SUFFIX}.jsonl"
    if not key_path.exists():
        return {}
    key = {r["id"]: r for r in (json.loads(l) for l in
           key_path.read_text(encoding="utf-8").splitlines() if l.strip())}
    gold_path = HERE / "study8" / f"GOLD-{ARM_SUFFIX}.csv"
    labels: dict[str, tuple[str, str]] = {}
    if gold_path.exists():
        for line in gold_path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                i, lab, rule = (line.split(",") + ["", ""])[:3]
                labels[i.strip()] = (lab.strip(), rule.strip())
    out = {}
    for item_id, k in key.items():
        if k["kind"] == "block-no-location":
            out[(k["instance"], k["row"])] = (k["kind"], "N", "no-location")
        elif item_id in labels:
            out[(k["instance"], k["row"])] = (k["kind"], *labels[item_id])
    return out


def cluster_bootstrap(records, denom, numer, resamples=RESAMPLES):
    rng = random.Random(SEED)
    per = [[r for r in rec["rows"] if denom(r)] for rec in records]
    stats, discarded = [], 0
    n = len(per)
    if not n:
        return (0.0, 0.0, 0)
    for _ in range(resamples):
        draw = [per[rng.randrange(n)] for _ in range(n)]
        rows = [r for group in draw for r in group]
        if not rows:
            discarded += 1
            continue
        stats.append(sum(1 for r in rows if numer(r)) / len(rows))
    if not stats:
        return (0.0, 0.0, discarded)
    stats.sort()
    return (stats[int(0.025 * (len(stats) - 1))],
            stats[int(0.975 * (len(stats) - 1))], discarded)


def rate(label, records, denom, numer, indent="  "):
    rows = [r for rec in records for r in rec["rows"] if denom(r)]
    k = sum(1 for r in rows if numer(r))
    n = len(rows)
    if n == 0:
        print(f"{indent}{label}: 0 of 0 — no denominator")
        return {"k": 0, "n": 0}
    lo, hi = wilson(k, n)
    blo, bhi, dropped = cluster_bootstrap(records, denom, numer)
    print(f"{indent}{label}: {k} of {n} = {100 * k / n:.2f}%  "
          f"(95% Wilson score interval for a binomial proportion of annotation rows: "
          f"{100 * lo:.2f}–{100 * hi:.2f}%; draft-clustered 95% percentile bootstrap, "
          f"{RESAMPLES} resamples of the {len(records)} drafts: {100 * blo:.2f}–{100 * bhi:.2f}%"
          + (f", {dropped} discarded" if dropped else "") + ")")
    return {"k": k, "n": n, "wilson": [lo, hi], "bootstrap": [blo, bhi]}


def addressed(r) -> bool:
    return r["src_kind"] not in ("uncited", "governed")


def blockable(r) -> bool:
    return addressed(r) and r["severity"] != ADVISORY


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--arm", default="4", choices=["4", "5"],
                    help="whose key and gold to read (default: Arm 4's)")
    args = ap.parse_args(argv)
    global ARM_SUFFIX
    ARM_SUFFIX = f"arm{args.arm}"
    records = load_records(args.run_dir)
    ok = [r for r in records if r.get("ok") and r.get("rows") is not None
          and not r.get("analysis_error")]
    errored = [r["instance"] for r in records if r not in ok]
    labels = load_labels()
    out: dict = {"drafts": len(records), "drafts_ok": len(ok), "errored": errored}
    print(f"Arm 4 — {len(records)} drafts recorded, {len(ok)} analysed, "
          f"{len(errored)} errored (excluded, counted): {errored}")

    def label_of(r):
        return labels.get((r["instance"], r["row"]), (None, None, None))[1]

    all_rows = [r for rec in ok for r in rec["rows"]]
    blocks = [r for r in all_rows if r["severity"] == BLOCKER]
    unlabelled = [r for r in blocks if label_of(r) is None]
    print(f"rows {len(all_rows)}; blocks {len(blocks)}; passes "
          f"{sum(1 for r in all_rows if r['severity'] == PASS)}; advisory "
          f"{sum(1 for r in all_rows if r['severity'] == ADVISORY)}; "
          f"blocks without a gold label yet: {len(unlabelled)}")

    print("\n-- PRIMARY (§8g is read off this) ------------------------------")
    if unlabelled:
        print("  NOT READABLE: every block needs a gold label first")
        out["primary"] = None
    else:
        def genuine(r):     # blockable, and the location genuinely contains the pair
            return blockable(r) and (r["severity"] == PASS or label_of(r) == "C")
        prim = rate("false-blocker rate: blocks labelled C / (passes + blocks labelled C)",
                    ok, genuine, lambda r: r["severity"] == BLOCKER)
        if prim.get("n"):
            prim["disposition"] = disposition(*prim["wilson"])
            print(f"  §8g DISPOSITION: {prim['disposition']}")
        out["primary"] = prim
        # blocks by label
        for lab in ("C", "N", "?"):
            print(f"  blocks labelled {lab}: {sum(1 for r in blocks if label_of(r) == lab)}")
        # sensitivity: the pass sample's C fraction
        sample = [(k, v) for k, v in labels.items() if v[0] == "pass"]
        c_pass = sum(1 for _k, v in sample if v[1] == "C")
        if sample:
            lo, hi = wilson(c_pass, len(sample))
            print(f"  pass sample: {c_pass} of {len(sample)} labelled C "
                  f"(Wilson {100 * lo:.2f}–{100 * hi:.2f}%) — false-pass sensitivity; "
                  f"passes scaled by {c_pass / len(sample):.3f} gives denominator "
                  f"{prim.get('n', 0) - prim.get('k', 0):.0f} × that + {prim.get('k', 0)}")
            out["pass_sample"] = {"C": c_pass, "n": len(sample), "wilson": [lo, hi]}

    print("\n-- SECONDARY ---------------------------------------------------")
    out["uncited"] = rate("uncited rate over all rows", ok, lambda r: True,
                          lambda r: r["src_kind"] == "uncited")
    print(f"    Arm 3: A {ARM3_UNCITED['A']}%, B {ARM3_UNCITED['B']}%")
    out["resolved_blockable"] = rate("resolved over blockable rows", ok, blockable,
                                     lambda r: r["severity"] == PASS)
    out["resolved_addressed"] = rate("resolved over addressed rows", ok, addressed,
                                     lambda r: r["severity"] == PASS)
    out["ambiguous"] = rate("ambiguous over addressed rows", ok, addressed,
                            lambda r: r["reason"] == "ambiguous")
    out["quote_absent"] = rate("quote-absent over addressed rows", ok, addressed,
                               lambda r: r["reason"] == "quote-absent")
    out["cross_line"] = rate("quote across a line break over addressed rows", ok, addressed,
                             lambda r: r["reason"] == "quote-crosses-line")
    out["paraphrase"] = rate("of quote-absent/cross-line rows, pair present elsewhere in the file",
                             ok, lambda r: r["reason"] in ("quote-absent", "quote-crosses-line"),
                             lambda r: bool(r.get("pair_in_named_file")))
    out["unit_shortened"] = rate("unit shortened over located rows", ok,
                                 lambda r: r.get("resolved_location"),
                                 lambda r: bool(r.get("unit_shortened")))
    reasons = {}
    for r in blocks:
        reasons[r["reason"]] = reasons.get(r["reason"], 0) + 1
    print(f"  block reasons: {json.dumps(reasons, sort_keys=True)}")
    out["block_reasons"] = reasons
    versions = sorted({r.get("matcher_version", "") for r in all_rows})
    print(f"  matcher version(s) in rows: {versions}")
    out["matcher_versions"] = versions
    numbers = sum(rec.get("numbers_present", 0) for rec in ok)
    print(f"  annotation rate: {len(all_rows)} rows / {numbers} numbers present = "
          f"{100 * len(all_rows) / numbers:.1f}%" if numbers else "  annotation rate: n/a")
    costs = [rec["usage"]["all"]["cost_usd"] for rec in ok if rec.get("usage")]
    reask = sum(1 for rec in ok if rec.get("usage", {}).get("generator_role_calls", 0) > 1)
    print(f"  cost: total ${sum(costs):.4f}, per draft ${sum(costs) / max(len(costs), 1):.4f}; "
          f"malformed-envelope re-ask on {reask} of {len(ok)} drafts")
    out["cost_usd"] = sum(costs)
    out["reask_drafts"] = reask
    # adjudicator_b against the gold on labelled items
    agree = {"C": {"b_true": 0, "b_false": 0}, "N": {"b_true": 0, "b_false": 0}}
    for r in all_rows:
        lab = label_of(r)
        if lab in agree and r.get("adj_b") is not None:
            agree[lab]["b_true" if r["adj_b"] else "b_false"] += 1
    print(f"  adjudicator_b vs gold on labelled rows: {json.dumps(agree)}")
    out["adj_b_vs_gold"] = agree
    if args.json:
        args.json.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
