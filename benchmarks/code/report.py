"""Turn the arms' JSONL into the preregistered numbers. Frozen before any score was seen.

Every statistic here is named in PREREGISTRATION.md. Anything a reader finds in RESULTS.md
that is not produced by this file is labelled exploratory there.

    python benchmarks/code/report.py --run benchmarks/code/runs/<run-id>
"""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

BOOTSTRAP_SEED = 20260904
BOOTSTRAP_N = 10_000


# ---------------------------------------------------------------------------------
# intervals and tests
# ---------------------------------------------------------------------------------

def wilson(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval. Behaves at 0 and at n, which normal approximation does not."""
    if n == 0:
        return (0.0, 1.0)
    phat = successes / n
    denom = 1 + z * z / n
    centre = (phat + z * z / (2 * n)) / denom
    half = z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def _binom_cdf(k: int, n: int, p: float) -> float:
    total = 0.0
    for i in range(0, k + 1):
        total += math.comb(n, i) * p ** i * (1 - p) ** (n - i)
    return total


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar. b = only-A-flagged, c = only-B-flagged, ties ignored."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = 2 * _binom_cdf(k, n, 0.5)
    return min(1.0, p)


def paired_bootstrap_ci(pairs: list[tuple[int, int]], seed: int = BOOTSTRAP_SEED,
                        draws: int = BOOTSTRAP_N) -> tuple[float, float]:
    """Percentile interval on (mean b) - (mean a), resampling *instances*, not flags."""
    if not pairs:
        return (0.0, 0.0)
    rng = random.Random(seed)
    n = len(pairs)
    diffs = []
    for _ in range(draws):
        total = 0
        for _ in range(n):
            a, b = pairs[rng.randrange(n)]
            total += b - a
        diffs.append(total / n)
    diffs.sort()
    return (diffs[int(0.025 * draws)], diffs[min(draws - 1, int(0.975 * draws))])


# ---------------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------------

@dataclass
class Study:
    arms: dict[str, dict[str, dict]]      # arm -> problem_id -> row
    scored: dict[str, dict]               # problem_id -> evaluate.py row
    strata_full: dict[str, int]           # stratum -> size in the full 540
    audit_set: list[str]
    cost: dict[str, float]


def load(run_dir: Path) -> Study:
    scored = {}
    for line in (run_dir / "scored.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            scored[row["problem_id"]] = row
    strata_full: dict[str, int] = {}
    for row in scored.values():
        strata_full[row["stratum"]] = strata_full.get(row["stratum"], 0) + 1
    audit_set = json.loads((run_dir / "audit_set.json").read_text(encoding="utf-8"))["problem_ids"]

    arms: dict[str, dict[str, dict]] = {}
    for path in sorted(run_dir.glob("arm-*.jsonl")):
        name = path.stem[len("arm-"):].replace("_", "+") if path.stem.endswith("_checks") \
            else path.stem[len("arm-"):]
        rows = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                rows[row["problem_id"]] = row
        arms[name] = rows
    cost_path = run_dir / "cost.json"
    cost = json.loads(cost_path.read_text(encoding="utf-8")) if cost_path.exists() else {}
    return Study(arms=arms, scored=scored, strata_full=strata_full,
                 audit_set=audit_set, cost=cost)


def flagged(row: dict) -> bool:
    return bool(row.get("ok")) and bool(row.get("flagged"))


def usable(arm_rows: dict[str, dict], ids: list[str]) -> list[str]:
    """Instances this arm actually produced a verdict for. A failed call is not a pass."""
    return [pid for pid in ids if pid in arm_rows and arm_rows[pid].get("ok")]


# ---------------------------------------------------------------------------------
# the numbers
# ---------------------------------------------------------------------------------

def rate(arm_rows: dict[str, dict], ids: list[str]) -> tuple[int, int, tuple[float, float]]:
    ok = usable(arm_rows, ids)
    hits = sum(1 for pid in ok if flagged(arm_rows[pid]))
    return hits, len(ok), wilson(hits, len(ok))


def stratum_ids(study: Study, stratum: str) -> list[str]:
    return [pid for pid in study.audit_set
            if study.scored[pid]["stratum"] == stratum]


def weights(study: Study) -> dict[str, float]:
    """Corpus weight of one audited instance in each stratum."""
    out = {}
    for stratum in ("P", "C", "F"):
        sampled = len(stratum_ids(study, stratum))
        out[stratum] = (study.strata_full.get(stratum, 0) / sampled) if sampled else 0.0
    return out


def reweighted(study: Study, arm_rows: dict[str, dict]) -> dict[str, float]:
    """Corpus-level flag rate and precision, correcting for the stratified draw."""
    w = weights(study)
    flag_mass = wrong_flag_mass = total_mass = 0.0
    for pid in usable(arm_rows, study.audit_set):
        stratum = study.scored[pid]["stratum"]
        weight = w[stratum]
        total_mass += weight
        if flagged(arm_rows[pid]):
            flag_mass += weight
            if stratum in ("P", "F"):
                wrong_flag_mass += weight
    return {
        "flag_rate": flag_mass / total_mass if total_mass else 0.0,
        "precision": wrong_flag_mass / flag_mass if flag_mass else float("nan"),
    }


def compare(study: Study, a: str, b: str, ids: list[str]) -> dict:
    """Paired comparison of two arms on the same instances."""
    rows_a, rows_b = study.arms.get(a, {}), study.arms.get(b, {})
    both = [pid for pid in ids
            if pid in rows_a and rows_a[pid].get("ok")
            and pid in rows_b and rows_b[pid].get("ok")]
    pairs = [(int(flagged(rows_a[pid])), int(flagged(rows_b[pid]))) for pid in both]
    only_a = sum(1 for x, y in pairs if x and not y)
    only_b = sum(1 for x, y in pairs if y and not x)
    diff = (sum(y for _, y in pairs) - sum(x for x, _ in pairs)) / len(pairs) if pairs else 0.0
    return {
        "a": a, "b": b, "n": len(pairs), "diff": diff,
        "only_a": only_a, "only_b": only_b,
        "p_mcnemar_exact": mcnemar_exact(only_a, only_b),
        "ci95": paired_bootstrap_ci(pairs),
    }


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--json", default="", help="also write the numbers as json")
    args = parser.parse_args(argv)

    study = load(Path(args.run))
    arm_order = [a for a in ("none", "checks", "self", "cross", "cross+checks",
                             "cross-replicate") if a in study.arms]
    P = stratum_ids(study, "P")
    C = stratum_ids(study, "C")
    F = stratum_ids(study, "F")

    out: dict = {"strata_full": study.strata_full,
                 "audit_set": {"P": len(P), "C": len(C), "F": len(F),
                               "total": len(study.audit_set)},
                 "weights": weights(study), "arms": {}, "comparisons": [],
                 "cost": study.cost}

    print("=" * 78)
    print("PRIMARY — recall on P (passes every visible test, fails a hidden test)")
    print("=" * 78)
    print(f"{'arm':<16}{'recall':>9}{'k/n':>12}{'95% CI':>22}")
    for arm in arm_order:
        hits, n, ci = rate(study.arms[arm], P)
        print(f"{arm:<16}{pct(hits / n) if n else '—':>9}{f'{hits}/{n}':>12}"
              f"{f'[{pct(ci[0])}, {pct(ci[1])}]':>22}")

    print()
    print("=" * 78)
    print("FALSE-POSITIVE COST — correct solutions (stratum C) flagged")
    print("=" * 78)
    print(f"{'arm':<16}{'FP rate':>9}{'k/n':>12}{'95% CI':>22}")
    for arm in arm_order:
        hits, n, ci = rate(study.arms[arm], C)
        print(f"{arm:<16}{pct(hits / n) if n else '—':>9}{f'{hits}/{n}':>12}"
              f"{f'[{pct(ci[0])}, {pct(ci[1])}]':>22}")

    print()
    print("=" * 78)
    print("stratum F (fails a visible test) — flagged")
    print("=" * 78)
    for arm in arm_order:
        hits, n, ci = rate(study.arms[arm], F)
        print(f"{arm:<16}{pct(hits / n) if n else '—':>9}{f'{hits}/{n}':>12}"
              f"{f'[{pct(ci[0])}, {pct(ci[1])}]':>22}")

    print()
    print("=" * 78)
    print("corpus-level, reweighted by stratum sampling fraction")
    print("=" * 78)
    print(f"{'arm':<16}{'flag rate':>12}{'precision':>12}")
    for arm in arm_order:
        w = reweighted(study, study.arms[arm])
        prec = "—" if w["precision"] != w["precision"] else pct(w["precision"])
        print(f"{arm:<16}{pct(w['flag_rate']):>12}{prec:>12}")
        out["arms"][arm] = {
            "recall_P": rate(study.arms[arm], P),
            "fp_C": rate(study.arms[arm], C),
            "flag_F": rate(study.arms[arm], F),
            "reweighted": w,
        }

    print()
    print("=" * 78)
    print("PREREGISTERED COMPARISONS on P (paired, McNemar exact, bootstrap CI)")
    print("=" * 78)
    named = [("checks", "cross+checks"), ("self", "cross"), ("cross", "cross+checks")]
    for a, b in named:
        if a not in study.arms or b not in study.arms:
            continue
        c = compare(study, a, b, P)
        out["comparisons"].append(c)
        print(f"{b} − {a}: {pct(c['diff'])}  n={c['n']}  "
              f"only-{a}={c['only_a']} only-{b}={c['only_b']}  "
              f"p={c['p_mcnemar_exact']:.4g}  "
              f"95% CI [{pct(c['ci95'][0])}, {pct(c['ci95'][1])}]")
    for a, b in named:
        if a not in study.arms or b not in study.arms:
            continue
        c = compare(study, a, b, C)
        c["population"] = "C"
        out["comparisons"].append(c)
        print(f"[false positives] {b} − {a}: {pct(c['diff'])}  n={c['n']}  "
              f"p={c['p_mcnemar_exact']:.4g}  "
              f"95% CI [{pct(c['ci95'][0])}, {pct(c['ci95'][1])}]")

    if "cross-replicate" in study.arms:
        print()
        print("=" * 78)
        print("NOISE FLOOR — cross vs an identical re-run")
        print("=" * 78)
        for label, ids in (("P", P), ("C", C)):
            c = compare(study, "cross", "cross-replicate", ids)
            c["population"] = f"noise-{label}"
            out["comparisons"].append(c)
            print(f"stratum {label}: |Δ| = {pct(abs(c['diff']))}  n={c['n']}  "
                  f"disagreements={c['only_a'] + c['only_b']}  "
                  f"p={c['p_mcnemar_exact']:.4g}  "
                  f"95% CI [{pct(c['ci95'][0])}, {pct(c['ci95'][1])}]")

    if study.cost:
        print()
        print("cost by arm (from the product's usage ledger):")
        for key, value in sorted(study.cost.items()):
            # Display only. cost.json rows are {usd, calls, input, output}; this line
            # was written expecting a bare float and crashed after every statistic above
            # was already computed. Fixed post-run; it changes no number (deviation 13).
            usd = value["usd"] if isinstance(value, dict) else value
            print(f"  {key:<20} ${usd:.4f}")

    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2, default=list) + "\n",
                                   encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
