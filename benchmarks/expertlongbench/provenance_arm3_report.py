"""Study 8's numbers, from the Arm 3 records. No model, no key, no network.

Reads `records-b*.jsonl` (which carry digests of the transcribed values, units
and quotes, never the text) and prints the preregistered outcomes for both
contracts: the §8g disposition per arm, the resolved fractions against the
design's simulated ceilings, the paired comparison, the block classification,
and cost.

Every interval names its method and the quantity it covers
(`benchmarks/EXPERIMENT_RECORD.md` §10). The Wilson interval — the one §8g is
read against — comes from the Arm 1 harness, unchanged, so all three arms share
the estimator as well as the corpus.

Usage:  python3 benchmarks/expertlongbench/provenance_arm3_report.py <run-dir>
"""
from __future__ import annotations

import argparse
import collections
import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from provenance_arm1 import wilson                                  # noqa: E402

BLOCKER, ADVISORY, PASS = "BLOCKER", "ADVISORY", "PASS"
RESAMPLES = 10_000
SEED = 20261104
ARMS = ("A", "B")

#: The design's simulated ceilings (`PROVENANCE_ADDRESSING.md` §3), quoted so the
#: measurement stands beside its prediction.
CEILING = {
    "A": {"blockable": 82.0, "addressed": 82.0},
    "B": {"blockable": 85.5, "addressed": 77.6},
}


# ------------------------------------------------------------------ predicates

def addressed(r) -> bool:
    """The row named a location — it is not `uncited` and not `governed:`."""
    return r["src_kind"] not in ("uncited", "governed")


def blockable(r) -> bool:
    """The rows the contract can block. B's ambiguous rows route where `uncited`
    routes — advisory, carried to the auditor, never blocking — so they are out
    of the gate's denominator, stated before the run (design §3.5)."""
    return r["severity"] != ADVISORY


def resolved(r) -> bool:
    return r["severity"] == PASS


def blocked(r) -> bool:
    return r["severity"] == BLOCKER


def correct_a(r) -> bool:
    """Adjudicator A: the named location genuinely contains the transcribed pair,
    by a deterministic re-read resolved independently of the verifier."""
    return bool(r["adj_a"])


def correct_b(r) -> bool:
    return bool(r["adj_b"])


# ------------------------------------------------------------------ statistics

def cluster_bootstrap(records, denom, numer, resamples=RESAMPLES):
    """95% percentile bootstrap over DRAFTS, because rows within a draft are not
    independent. Returns (low, high, discarded)."""
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


def rate(label, records, denom, numer, indent=""):
    rows = [r for rec in records for r in rec["rows"] if denom(r)]
    k = sum(1 for r in rows if numer(r))
    n = len(rows)
    if n == 0:
        print(f"{indent}{label}: 0 of 0 — no denominator")
        return None
    lo, hi = wilson(k, n)
    print(f"{indent}{label}: {k} of {n} = {100 * k / n:.2f}%  "
          f"(95% Wilson score interval for a binomial proportion of annotation "
          f"rows: {100 * lo:.2f}–{100 * hi:.2f}%)")
    blo, bhi, dropped = cluster_bootstrap(records, denom, numer)
    print(f"{indent}    draft-clustered 95% percentile bootstrap for the same "
          f"proportion, {RESAMPLES} resamples of the {len(records)} drafts: "
          f"{100 * blo:.2f}–{100 * bhi:.2f}%"
          + (f" ({dropped} resamples discarded for an empty denominator)"
             if dropped else ""))
    return k, n, lo, hi


def disposition(lo, hi) -> str:
    """`PROVENANCE_CHECKS.md` §8g, verbatim: kill if the lower bound exceeds 2%;
    pass only if the upper bound is below 5%; anything between is inconclusive."""
    if lo > 0.02:
        return "KILL"
    if hi < 0.05:
        return "PASS"
    return "INCONCLUSIVE"


def exact_binom_two_sided(b: int, c: int) -> float:
    """Exact two-sided p for b successes of b+c under p=1/2 (McNemar exact on the
    discordant pairs; identical to the exact paired sign test)."""
    from math import comb

    n = b + c
    if n == 0:
        return 1.0
    total = 2 ** n
    obs = comb(n, b)
    return min(1.0, sum(comb(n, k) for k in range(n + 1)
                        if comb(n, k) <= obs) / total)


def sign_flip(diffs, resamples=RESAMPLES):
    """A draft-clustered randomisation test on the paired per-instance
    difference: each draft's whole difference keeps or flips its sign together,
    which is the cluster. Returns (mean, p, lo, hi) with a percentile bootstrap
    interval on the mean over the same clusters."""
    rng = random.Random(SEED)
    if not diffs:
        return (0.0, 1.0, 0.0, 0.0)
    observed = statistics.fmean(diffs)
    extreme = 0
    for _ in range(resamples):
        flipped = [d if rng.random() < 0.5 else -d for d in diffs]
        if abs(statistics.fmean(flipped)) >= abs(observed) - 1e-12:
            extreme += 1
    boot = []
    for _ in range(resamples):
        draw = [diffs[rng.randrange(len(diffs))] for _ in range(len(diffs))]
        boot.append(statistics.fmean(draw))
    boot.sort()
    return (observed, (extreme + 1) / (resamples + 1),
            boot[int(0.025 * (len(boot) - 1))], boot[int(0.975 * (len(boot) - 1))])


# ------------------------------------------------------------------ the report

def load(run_dir: Path, batches) -> list[dict]:
    out = []
    for b in batches:
        path = run_dir / f"records-b{b}.jsonl"
        if not path.exists():
            continue
        out += [json.loads(line) for line in
                path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return out


def arm_section(arm: str, records: list[dict]) -> dict:
    print(f"\n{'=' * 78}\nARM {arm} — {len(records)} drafts\n{'=' * 78}")
    rows = [r for rec in records for r in rec["rows"]]
    print(f"annotation rows written                 {len(rows)}")
    print(f"  named a location (addressed)          "
          f"{sum(1 for r in rows if addressed(r))}")
    print(f"  blockable (advisory routing removed)  "
          f"{sum(1 for r in rows if blockable(r))}")
    print(f"  PASS / BLOCKER / ADVISORY             "
          f"{sum(1 for r in rows if resolved(r))} / "
          f"{sum(1 for r in rows if blocked(r))} / "
          f"{sum(1 for r in rows if r['severity'] == ADVISORY)}")
    print(f"  drafts with at least one blocker      "
          f"{sum(1 for rec in records if any(blocked(r) for r in rec['rows']))}"
          f" of {len(records)}")

    print("\n-- PRIMARY (§8g is read off this) ------------------------------")
    print("Of the BLOCKABLE rows whose named location genuinely contains the "
          "transcribed\npair (adjudicator A, deterministic re-read), the "
          "fraction this arm BLOCKS:")
    primary = rate("  false-blocker rate", records,
                   lambda r: blockable(r) and correct_a(r), blocked)
    out = {"arm": arm}
    if primary:
        k, n, lo, hi = primary
        out["primary"] = {"k": k, "n": n, "lo": lo, "hi": hi,
                          "disposition": disposition(lo, hi)}
        print(f"  §8g DISPOSITION: {out['primary']['disposition']}")

    print("\n-- sensitivity, not a second objective -------------------------")
    rate("  over adjudicator B's denominator", records,
         lambda r: blockable(r) and correct_b(r), blocked, indent="")
    rate("  including advisory-routed ambiguous rows", records,
         correct_a, blocked, indent="")
    agree = collections.Counter(
        (bool(r["adj_a"]), bool(r["adj_b"])) for r in rows
        if r["resolved_location"])
    print(f"  A/B agreement on rows with a resolvable location: "
          f"{agree[(True, True)] + agree[(False, False)]} of {sum(agree.values())} "
          f"(A+B+ {agree[(True, True)]}, A+B- {agree[(True, False)]}, "
          f"A-B+ {agree[(False, True)]}, A-B- {agree[(False, False)]})")

    print("\n-- SECONDARY: rows the verifier resolves and the pair is in ----")
    for label, pred, key in (
            ("  over BLOCKABLE rows", blockable, "blockable"),
            ("  over ADDRESSED rows", addressed, "addressed")):
        got = rate(label, records, pred, resolved)
        if got:
            k, n, lo, hi = got
            out.setdefault("resolved", {})[key] = {"k": k, "n": n}
            print(f"      simulated ceiling {CEILING[arm][key]:.1f}%  "
                  f"(measured − predicted = "
                  f"{100 * k / n - CEILING[arm][key]:+.1f} points)")

    print("\n-- SECONDARY: the generator's behaviour ------------------------")
    rate("  uncited rate (all rows)", records, lambda r: True,
         lambda r: r["src_kind"] == "uncited")
    if arm == "B":
        rate("  ambiguous rate (addressed rows)", records, addressed,
             lambda r: r["reason"] == "ambiguous")
        rate("  paraphrase rate (addressed rows)", records, addressed,
             lambda r: r["reason"] == "quote-absent"
             and bool(r["pair_in_named_file"]))
        rate("  quote absent AND pair not in the file", records, addressed,
             lambda r: r["reason"] == "quote-absent"
             and not r["pair_in_named_file"])
        lens = [r["quote_len"] for r in rows if r["quote_len"]]
        if lens:
            print(f"  quote length: mean {statistics.fmean(lens):.0f}, median "
                  f"{statistics.median(lens):.0f}, max {max(lens)} "
                  f"(cap 80; {sum(1 for x in lens if x > 80)} over)")
    rate("  unit written shorter than the source's", records,
         lambda r: r["resolved_location"], lambda r: bool(r["unit_shortened"]))
    ann = [(len(rec["rows"]), rec.get("numbers_present", 0)) for rec in records]
    pooled_rows = sum(a for a, _ in ann)
    pooled_nums = sum(b for _, b in ann)
    if pooled_nums:
        print(f"  annotation rate: {pooled_rows} / {pooled_nums} = "
              f"{100 * pooled_rows / pooled_nums:.1f}% pooled")
    print(f"  outline-replaced source files: "
          f"{sum(len(rec.get('outlined_paths', [])) for rec in records)} over "
          f"{len(records)} drafts")
    numbered = sum(1 for rec in records
                   if any(c["numbered"] for c in rec.get("gutter", [])))
    print(f"  drafts whose prompt carried a gutter: {numbered} of {len(records)}")

    print("\n-- BLOCK CLASSIFICATION (preregistered §10) --------------------")
    classes = collections.Counter(r["class"] for r in rows if blocked(r))
    for name in ("verifier wrong", "malformed row", "outline-replaced file",
                 "unparsed notation", "ambiguous", "paraphrase",
                 "generator wrong file", "generator wrong line/quote"):
        print(f"  {name:<32} {classes.get(name, 0)}")
    extra = set(classes) - {"verifier wrong", "malformed row",
                            "outline-replaced file", "unparsed notation",
                            "ambiguous", "paraphrase", "generator wrong file",
                            "generator wrong line/quote"}
    for name in sorted(extra):
        print(f"  {name:<32} {classes[name]}  (UNPREREGISTERED CLASS)")
    out["classes"] = dict(classes)

    print("\n-- COST (the product's own usage ledger) -----------------------")
    costs = [rec["usage"]["all"]["cost_usd"] for rec in records if "usage" in rec]
    gen = [rec["usage"]["generator"]["cost_usd"] for rec in records if "usage" in rec]
    aud = [rec["usage"]["auditor"]["cost_usd"] for rec in records if "usage" in rec]
    inp = [rec["usage"]["generator"]["input"] for rec in records if "usage" in rec]
    outp = [rec["usage"]["generator"]["output"] for rec in records if "usage" in rec]
    calls = [rec["usage"].get("generator_role_calls", 0) for rec in records
             if "usage" in rec]
    if costs:
        print(f"  per draft: mean ${statistics.fmean(costs):.4f}, median "
              f"${statistics.median(costs):.4f}, total ${sum(costs):.4f}")
        print(f"    generator ${sum(gen):.4f}   auditor ${sum(aud):.4f}")
        print(f"  generator tokens: input mean {statistics.fmean(inp):.0f}, "
              f"output mean {statistics.fmean(outp):.0f}")
        print(f"  malformed-envelope re-ask: {sum(1 for c in calls if c > 1)} of "
              f"{len(calls)} drafts placed more than one generator call "
              f"(total generator calls {sum(calls)})")
        out["cost"] = {"total": sum(costs), "mean": statistics.fmean(costs),
                       "gen": sum(gen), "aud": sum(aud),
                       "reask_drafts": sum(1 for c in calls if c > 1),
                       "input_mean": statistics.fmean(inp),
                       "output_mean": statistics.fmean(outp)}
    fails = [rec["instance"] for rec in records if not rec.get("ok")]
    if fails:
        print(f"  INSTANCES THAT DID NOT COMPLETE: {fails}")
    bad = [rec["instance"] for rec in records if rec.get("manifest_agrees") is False]
    print(f"  receipt manifest agrees with the reconstructed increment: "
          f"{sum(1 for rec in records if rec.get('manifest_agrees'))} of "
          f"{len(records)}" + (f"  MISMATCH: {bad}" if bad else ""))
    return out


def paired_section(by_arm: dict[str, list[dict]]) -> None:
    print(f"\n{'=' * 78}\nA vs B — paired by instance\n{'=' * 78}")
    index = {arm: {rec["instance"]: rec for rec in recs}
             for arm, recs in by_arm.items()}
    shared = sorted(set(index["A"]) & set(index["B"]))
    print(f"complete pairs: {len(shared)}")
    if not shared:
        return

    def frac(rec, denom):
        rows = [r for r in rec["rows"] if denom(r)]
        return (sum(1 for r in rows if resolved(r)) / len(rows)) if rows else None

    for label, denom in (("BLOCKABLE", blockable), ("ADDRESSED", addressed)):
        pairs = [(frac(index["A"][i], denom), frac(index["B"][i], denom))
                 for i in shared]
        pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
        if not pairs:
            continue
        diffs = [a - b for a, b in pairs]
        wins_a = sum(1 for d in diffs if d > 0)
        wins_b = sum(1 for d in diffs if d < 0)
        ties = sum(1 for d in diffs if d == 0)
        p = exact_binom_two_sided(wins_a, wins_b)
        mean, pflip, lo, hi = sign_flip(diffs)
        print(f"\nresolved fraction over {label} rows, {len(pairs)} pairs")
        print(f"  A mean {100 * statistics.fmean(a for a, _ in pairs):.1f}%   "
              f"B mean {100 * statistics.fmean(b for _, b in pairs):.1f}%")
        print(f"  instances where A > B: {wins_a}; B > A: {wins_b}; tied: {ties}")
        print(f"  exact McNemar on the discordant pair directions (identical to "
              f"the exact paired sign test): p = {p:.4f}")
        print(f"  draft-clustered sign-flip randomisation on the paired "
              f"difference (A−B): mean {100 * mean:+.1f} points, p = {pflip:.4f}")
        print(f"  paired percentile bootstrap 95% interval for the mean paired "
              f"difference (A−B), {RESAMPLES} resamples of the "
              f"{len(diffs)} instances: {100 * lo:+.1f} to {100 * hi:+.1f} points")

    print("\nfalse-blocker rate, side by side (the §8g quantity)")
    for arm in ARMS:
        rows = [r for rec in by_arm[arm] for r in rec["rows"]
                if blockable(r) and correct_a(r)]
        k = sum(1 for r in rows if blocked(r))
        n = len(rows)
        if n:
            lo, hi = wilson(k, n)
            print(f"  arm {arm}: {k} of {n} = {100 * k / n:.2f}%  "
                  f"(95% Wilson: {100 * lo:.2f}–{100 * hi:.2f}%)  "
                  f"→ {disposition(lo, hi)}")
        else:
            print(f"  arm {arm}: 0 of 0 — no denominator")

    cost = {arm: sum(rec["usage"]["all"]["cost_usd"] for rec in by_arm[arm]
                     if "usage" in rec) for arm in ARMS}
    print(f"\nspend: arm A ${cost['A']:.4f}, arm B ${cost['B']:.4f}, "
          f"total ${sum(cost.values()):.4f}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--batches", default="1,2")
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args(argv)

    batches = [int(b) for b in args.batches.split(",") if b.strip()]
    records = load(args.run_dir, batches)
    if not records:
        print(f"no records under {args.run_dir}")
        return 2
    by_arm = {arm: [r for r in records if r["arm"] == arm] for arm in ARMS}
    summary = {arm: arm_section(arm, by_arm[arm]) for arm in ARMS if by_arm[arm]}
    paired_section(by_arm)
    if args.json:
        args.json.write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
