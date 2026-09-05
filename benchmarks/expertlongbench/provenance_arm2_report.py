"""Study 7's numbers, from the Arm 2 records. No model, no key, no network.

Reads `records-b*.jsonl` (which carry digests of the transcribed values, never
the text) and prints the preregistered outcomes: the primary and its §8g
disposition, the two adjudicators' agreement, the block classification, the
generator's annotation behaviour, the hyphen stratum, and cost per draft.

Every interval names its method and the quantity it covers (EXPERIMENT_RECORD
§10). The Wilson interval — the one §8g is read against — comes from the Arm 1
harness, unchanged, so the two arms share the estimator as well as the corpus.

Usage:  python3 benchmarks/expertlongbench/provenance_arm2_report.py <run-dir> [--pooled]
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from provenance_arm1 import wilson                                  # noqa: E402

BLOCKER = "BLOCKER"
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20261104


def load(run_dir: Path, batches: list[int]) -> list[dict]:
    out = []
    for b in batches:
        path = run_dir / f"records-b{b}.jsonl"
        if not path.exists():
            continue
        out += [json.loads(line) for line in
                path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return out


def cluster_bootstrap(records: list[dict], denom, numer,
                      resamples: int = BOOTSTRAP_RESAMPLES) -> tuple:
    """95% percentile bootstrap over DRAFTS, because rows within a draft are not
    independent (EXPERIMENT_RECORD §10). Returns (low, high, discarded)."""
    rng = random.Random(BOOTSTRAP_SEED)
    per = [[r for r in rec["rows"] if denom(r)] for rec in records]
    stats, discarded = [], 0
    n = len(per)
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
    lo = stats[int(0.025 * (len(stats) - 1))]
    hi = stats[int(0.975 * (len(stats) - 1))]
    return (lo, hi, discarded)


def rate_line(label: str, k: int, n: int, records=None, denom=None, numer=None):
    if n == 0:
        print(f"{label}: 0 of 0 — no denominator")
        return
    lo, hi = wilson(k, n)
    print(f"{label}: {k} of {n} = {100 * k / n:.2f}%  "
          f"(95% Wilson score interval for a binomial proportion of annotation "
          f"rows: {100 * lo:.2f}–{100 * hi:.2f}%)")
    if records is not None:
        blo, bhi, dropped = cluster_bootstrap(records, denom, numer)
        print(f"    draft-clustered 95% percentile bootstrap for the same "
              f"proportion, {BOOTSTRAP_RESAMPLES} resamples of the "
              f"{len(records)} drafts: {100 * blo:.2f}–{100 * bhi:.2f}%"
              + (f" ({dropped} resamples discarded for an empty denominator)"
                 if dropped else ""))
    return lo, hi


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--batches", default="1,2")
    args = ap.parse_args(argv)
    run_dir = Path(args.run_dir)
    batches = [int(b) for b in args.batches.split(",") if b.strip()]
    records = load(run_dir, batches)
    ok = [r for r in records if r.get("ok") and r.get("rows") is not None]
    rows = [r for rec in ok for r in rec["rows"]]

    print(f"instances: {len(records)} recorded, {len(ok)} usable "
          f"(batches {batches})")
    bad = [r["instance"] for r in records if r not in ok]
    if bad:
        print(f"  dropped: {bad}")
    dis = [r for r in records if r.get("ledger_agrees") is not True]
    print(f"  the loop's own ledger agrees with the re-run check on "
          f"{len(records) - len(dis)}/{len(records)} instances"
          + (f"; disagreements: {[r['instance'] for r in dis]}" if dis else ""))
    man = [r for r in records if r.get("manifest_agrees") is not True]
    print(f"  the receipt's own increment manifest agrees with the "
          f"reconstruction on {len(records) - len(man)}/{len(records)}"
          + (f"; disagreements: {[r['instance'] for r in man]}" if man else ""))
    print()

    # ---------------------------------------------------------------- primary
    a_pos = [r for r in rows if r.get("adj_a") is True]
    print("PRIMARY — of annotation rows whose src span genuinely contains the "
          "transcribed pair\n  (adjudicator A: a deterministic re-read, the "
          "check's own contains_pair), the fraction BLOCKED:")
    bounds = rate_line("  false-blocker rate",
                       sum(1 for r in a_pos if r["severity"] == BLOCKER),
                       len(a_pos), ok,
                       lambda r: r.get("adj_a") is True,
                       lambda r: r["severity"] == BLOCKER)
    if bounds:
        lo, hi = bounds
        verdict = ("KILL" if lo > 0.02 else "PASS" if hi < 0.05
                   else "INCONCLUSIVE")
        print(f"  §8g disposition (kill if the Wilson lower bound exceeds 2%; "
              f"pass only if the upper bound is below 5%): {verdict}")
    print()

    # ------------------------------------------------- sensitivity, not an objective
    b_pos = [r for r in rows if r.get("adj_b") is True]
    print("SENSITIVITY (preregistered §5; NOT a second objective and the §8g "
          "disposition is not read off it)")
    rate_line("  blocked, of adjudicator-B-positive rows",
              sum(1 for r in b_pos if r["severity"] == BLOCKER), len(b_pos),
              ok, lambda r: r.get("adj_b") is True,
              lambda r: r["severity"] == BLOCKER)
    grid = {(a, b): 0 for a in (True, False) for b in (True, False)}
    for r in rows:
        if r.get("adj_a") is None:
            continue
        grid[(bool(r["adj_a"]), bool(r["adj_b"]))] += 1
    total = sum(grid.values())
    agree = grid[(True, True)] + grid[(False, False)]
    print(f"  adjudicator agreement on the {total} rows carrying a resolvable "
          f"locator: {agree}/{total}"
          + (f" = {100 * agree / total:.1f}%" if total else ""))
    print(f"    A+/B+ {grid[(True, True)]}   A+/B- {grid[(True, False)]}   "
          f"A-/B+ {grid[(False, True)]}   A-/B- {grid[(False, False)]}")
    print()

    # ------------------------------------------------------------- secondaries
    blocks = [r for r in rows if r["severity"] == BLOCKER]
    print("SECONDARIES")
    kinds = {}
    for r in rows:
        kinds[r["locator_kind"]] = kinds.get(r["locator_kind"], 0) + 1
    print(f"  rows written: {len(rows)} over {len(ok)} drafts "
          f"({len(rows) / len(ok):.1f} per draft)" if ok else "  rows: 0")
    unc = kinds.get("uncited", 0)
    rate_line("  uncited rate", unc, len(rows))
    print(f"  locator kinds: " + ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))
    correct = [r for r in blocks if r["class"] != "verifier false blocker"]
    rate_line("  correct blocks (a generator error or a contract stratum), "
              "of all blocks", len(correct), len(blocks))
    print(f"  block rate over ALL rows: {len(blocks)} of {len(rows)}"
          + (f" = {100 * len(blocks) / len(rows):.1f}%" if rows else ""))
    print()
    print("  block classification (§10):")
    classes = {}
    for r in blocks:
        classes[r["class"]] = classes.get(r["class"], 0) + 1
    for name, count in sorted(classes.items(), key=lambda kv: -kv[1]):
        print(f"    {count:4d}  {name}")
    print()

    print("  annotation coverage per draft (numbers present by the Arm 1 probe's "
          "NUM extractor):")
    per_draft = []
    for rec in ok:
        present = rec.get("numbers_present", 0)
        written = len(rec["rows"])
        per_draft.append((rec["instance"], written, present,
                          written / present if present else 0.0))
    for inst, written, present, frac in per_draft:
        print(f"    {inst:44s} {written:3d} / {present:3d} = {100 * frac:5.1f}%")
    tot_w = sum(w for _i, w, _p, _f in per_draft)
    tot_p = sum(p for _i, _w, p, _f in per_draft)
    print(f"    pooled: {tot_w} / {tot_p} = "
          f"{100 * tot_w / tot_p:.1f}%" if tot_p else "")
    fracs = [f for _i, _w, _p, f in per_draft]
    if fracs:
        print(f"    per-draft mean {100 * statistics.mean(fracs):.1f}%, "
              f"median {100 * statistics.median(fracs):.1f}%, "
              f"min {100 * min(fracs):.1f}%, max {100 * max(fracs):.1f}%")
    print()

    short = [r for r in rows if r.get("unit_shortened")]
    print(f"  unit-shortening (a transcribed unit that is a strict prefix of the "
          f"whole unit token at an occurrence of its value): {len(short)} of "
          f"{len([r for r in rows if r.get('resolved')])} rows with a resolvable "
          f"locator")
    for r in short:
        print(f"    {r['instance']} at {r['at']} src {r['src']} "
              f"[{r['disposition']}]")
    print()

    hy = [r for r in blocks if r["class"] == "hyphenated-word case"]
    print(f"  hyphen stratum (D157's open product dial): {len(hy)} block(s)")
    for r in hy:
        print(f"    {r['instance']} at {r['at']} src {r['src']}")
    print()

    at_bad = [r for r in rows if r.get("at_valid") is False]
    print(f"  rows whose `at` (the line in the generator's OWN artefact) is "
          f"outside that artefact: {len(at_bad)} of {len(rows)}")
    src_ok_at_bad = [r for r in at_bad if r.get("adj_a") is True]
    print(f"    of those, {len(src_ok_at_bad)} name a src span that DOES "
          f"contain the pair")
    print()

    print("  cost and tokens per draft (from the product's usage ledger):")
    tot = 0.0
    for rec in records:
        u = rec.get("usage", {})
        allu, gen, aud = u.get("all", {}), u.get("generator", {}), u.get("auditor", {})
        tot += float(allu.get("cost_usd", 0.0))
        print(f"    {rec['instance']:44s} ${allu.get('cost_usd', 0):.4f} "
              f"(gen ${gen.get('cost_usd', 0):.4f} in/out "
              f"{gen.get('input', 0)}/{gen.get('output', 0)} calls "
              f"{gen.get('calls', 0)}; aud ${aud.get('cost_usd', 0):.4f}) "
              f"{rec.get('wall_s', 0):.0f}s")
    if records:
        print(f"    total ${tot:.4f} over {len(records)} instances = "
              f"${tot / len(records):.4f} each")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
