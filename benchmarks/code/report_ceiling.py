"""Study 8 — every number in ``RESULTS-CEILING.md``, regenerated from committed records.

No API key. No network. No model. Reads only what is committed under
``benchmarks/code/records/`` and writes ``records/ceiling/numbers.json`` (machine-readable)
and ``records/ceiling/tables.md`` (the tables the report quotes verbatim). Run it on
partial data at any point; it reports what exists and names what does not.

    python benchmarks/code/report_ceiling.py

**Unit of analysis: the instance** — one ``(batch, problem_id)`` solution. K draws over the
same instances are repeated measures on those instances, never K x n observations. Every
interval resamples **problem clusters** (68 of the 222 problems contribute two instances
each), so both instances of a problem move together.

The estimators, all preregistered:

* union recall/FP at K, averaged over **all** C(K_max, K) subsets of draws — computed
  exactly, not by sampling: an instance flagged by k of K_max draws is missed by a random
  K-subset with probability C(K_max - k, K) / C(K_max, K).
* the asymptote A of ``recall(K) = A(1 - e^{-K/tau})``, least squares. For a fixed tau the
  fit is linear in A, so the whole fit is a one-dimensional search over tau — exact, with
  no optimiser to tune and no starting point to choose.
* a zero-inflated beta-binomial MLE on the per-instance flag counts, as the preregistered
  sensitivity analysis. Reported as secondary, and its known weak identifiability said.
* exact McNemar on discordant pairs, with an exact-conditional interval for the paired
  difference (amendment 3), because a percentile bootstrap over one-signed discordances
  cannot produce a resample of the other sign.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

RECORDS = HERE / "records"
CEILING = RECORDS / "ceiling"
LOOP = CEILING / "loop"
EXPLORE_CACHE = RECORDS / "explore"

FAMILIES = ("cross", "self", "astra")
LOOP_ARMS = ("self-loop", "self-loop-rep", "cross-loop", "referent-loop")
BOOTSTRAP = 10000
BOOT_SEED = 20260908


# ---------------------------------------------------------------------------------
# small statistics, stated so they can be checked
# ---------------------------------------------------------------------------------

def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """95% Wilson score interval for a single binomial proportion."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar: a binomial sign test on the discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def _betainc_regularised(a: float, b: float, x: float) -> float:
    """I_x(a, b) by the continued fraction, good to ~1e-12 — no SciPy dependency."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(x) + b * math.log(1 - x) - lbeta)
    if x > (a + 1) / (a + b + 2):
        return 1.0 - _betainc_regularised(b, a, 1 - x)
    f, c, d = 1.0, 1.0, 0.0
    for i in range(0, 300):
        m = i // 2
        if i == 0:
            numerator = 1.0
        elif i % 2 == 0:
            numerator = (m * (b - m) * x) / ((a + 2 * m - 1) * (a + 2 * m))
        else:
            numerator = -((a + m) * (a + b + m) * x) / ((a + 2 * m) * (a + 2 * m + 1))
        d = 1.0 + numerator * d
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1.0 / d
        c = 1.0 + numerator / c
        if abs(c) < 1e-30:
            c = 1e-30
        f *= c * d
        if abs(1.0 - c * d) < 1e-14:
            break
    return front * (f - 1) / a


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact binomial interval, by inverting the beta CDF with a bisection."""
    if n == 0:
        return (0.0, 1.0)

    def invert(target: float, a: float, b: float) -> float:
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if _betainc_regularised(a, b, mid) < target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    # Lower bound: the p at which the upper tail P(X >= k) equals alpha/2, i.e.
    # I^{-1}_{alpha/2}(k, n-k+1). Upper bound: I^{-1}_{1-alpha/2}(k+1, n-k).
    low = 0.0 if k == 0 else invert(alpha / 2, k, n - k + 1)
    high = 1.0 if k == n else invert(1 - alpha / 2, k + 1, n - k)
    return (low, high)


def paired_difference_exact(b: int, c: int, n: int) -> dict:
    """The exact-conditional interval for delta = (b - c)/n (amendment 3).

    Conditioning on the n_d = b + c discordant pairs, b ~ Binomial(n_d, pi). A
    Clopper-Pearson interval for pi maps monotonically to an interval for delta, because
    delta = n_d(2 pi - 1)/n is increasing in pi. This is the right instrument when the
    discordances all point one way: a percentile bootstrap cannot then generate a
    resample of the opposite sign and returns a one-signed interval that does not
    establish exclusion of zero (CORRECTIONS.md item 4).
    """
    nd = b + c
    delta = (b - c) / n if n else 0.0
    if nd == 0:
        return {"b": b, "c": c, "n_discordant": 0, "n": n, "delta": delta,
                "ci95": None, "p_exact": 1.0,
                "note": "0 of 0 discordant pairs; no rate is quoted"}
    lo, hi = clopper_pearson(b, nd)
    return {"b": b, "c": c, "n_discordant": nd, "n": n, "delta": delta,
            "ci95": [nd * (2 * lo - 1) / n, nd * (2 * hi - 1) / n],
            "p_exact": mcnemar_exact(b, c),
            "method": "exact-conditional (Clopper-Pearson on the discordant pairs), "
                      "exact McNemar p"}


# ---------------------------------------------------------------------------------
# the substrate
# ---------------------------------------------------------------------------------

def load_instances() -> dict[str, dict]:
    rows = {}
    for line in (RECORDS / "study2/instances.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row["instance_id"]] = row
    return rows


def load_audit_set() -> list[str]:
    return json.loads(
        (RECORDS / "study2/audit_set.json").read_text(encoding="utf-8"))["instance_ids"]


def load_draws(scope: set[str]) -> dict[str, dict[int, dict[str, bool]]]:
    """``family -> draw -> instance_id -> flagged``, from every committed record.

    Reads study 1's arms, study 2's arms, study 7's cache and study 8's cache through
    ``explore.load_detector``, which is the one implementation of "where does a detector's
    record live". Nothing here re-derives a flag; the flag rule is the harness's.
    """
    import explore

    out: dict[str, dict[int, dict[str, bool]]] = {f: {} for f in FAMILIES}
    for family in FAMILIES:
        for draw in range(1, 9):
            key = ("holistic", family, draw)
            found: dict[str, dict] = {}
            for directory in (EXPLORE_CACHE, CEILING):
                explore.EXPLORE = directory
                found.update(explore.load_detector(key, scope))
            explore.EXPLORE = CEILING
            complete = {i: bool(r["flagged"]) for i, r in found.items() if i in scope}
            if len(complete) == len(scope):
                out[family][draw] = complete
            elif complete:
                out[family][f"partial-{draw}"] = complete  # recorded, never analysed
    return out


# ---------------------------------------------------------------------------------
# ceiling 1 — the saturation curve
# ---------------------------------------------------------------------------------

def counts_per_instance(draws: dict[int, dict[str, bool]], ids: list[str]) -> list[int]:
    """k_i: how many of the K_max draws flagged instance i. The whole curve is a
    function of these counts, which is why the bootstrap is cheap and exact."""
    ks = sorted(d for d in draws if isinstance(d, int))
    return [sum(1 for d in ks if draws[d].get(i)) for i in ids]


def union_curve(ks: list[int], k_max: int) -> list[float]:
    """Mean union rate at K = 1 .. K_max, averaged over all C(K_max, K) draw subsets.

    Exact. An instance flagged by k of K_max draws is missed by a random K-subset with
    probability C(K_max - k, K) / C(K_max, K); one minus that, averaged over instances, is
    the subset-averaged union rate. No subsets are enumerated and none are sampled.
    """
    n = len(ks)
    if not n:
        return []
    out = []
    for K in range(1, k_max + 1):
        total = math.comb(k_max, K)
        acc = 0.0
        for k in ks:
            miss = math.comb(k_max - k, K) / total if k_max - k >= K else 0.0
            acc += 1.0 - miss
        out.append(acc / n)
    return out


def fit_saturation(curve: list[float]) -> dict:
    """Least squares for recall(K) = A(1 - e^{-K/tau}).

    For a fixed tau the model is linear in A, so A_hat(tau) = sum(y f) / sum(f f) in closed
    form and the fit reduces to a one-dimensional search over tau. Searched on a log grid
    then refined by golden section, so there is no starting point to choose and no
    optimiser that can fail to converge.
    """
    if len(curve) < 2:
        return {"A": None, "tau": None, "r2": None, "max_resid": None,
                "note": "AUTHOR_INPUT_NEEDED: fewer than two K points"}
    Ks = list(range(1, len(curve) + 1))

    def sse(tau: float) -> tuple[float, float]:
        f = [1 - math.exp(-K / tau) for K in Ks]
        denom = sum(v * v for v in f)
        A = (sum(y * v for y, v in zip(curve, f)) / denom) if denom else 0.0
        return sum((y - A * v) ** 2 for y, v in zip(curve, f)), A

    best = min(((sse(t)[0], t) for t in (10 ** (x / 40) for x in range(-60, 121))))[1]
    lo, hi = best / 2, best * 2
    phi = (math.sqrt(5) - 1) / 2
    for _ in range(120):
        c1, c2 = hi - phi * (hi - lo), lo + phi * (hi - lo)
        if sse(c1)[0] < sse(c2)[0]:
            hi = c2
        else:
            lo = c1
    tau = (lo + hi) / 2
    residual, A = sse(tau)
    mean = sum(curve) / len(curve)
    tss = sum((y - mean) ** 2 for y in curve)
    predicted = [A * (1 - math.exp(-K / tau)) for K in Ks]
    return {"A": A, "tau": tau,
            "r2": (1 - residual / tss) if tss > 0 else None,
            "max_resid": max(abs(y - p) for y, p in zip(curve, predicted)),
            "sse": residual}


def _betabinom_logpmf(k: int, n: int, a: float, b: float) -> float:
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
            + math.lgamma(k + a) + math.lgamma(n - k + b) - math.lgamma(n + a + b)
            + math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b))


def fit_zibb(ks: list[int], k_max: int) -> dict:
    """Zero-inflated beta-binomial MLE; the asymptote is the mixing weight pi.

    p_i ~ pi * Beta(a, b) + (1 - pi) * delta_0, so an instance with p_i = 0 is one no draw
    can ever flag and pi is the fraction that are findable at all. Preregistered as the
    **secondary** estimator: pi and a Beta component with a -> 0 are only weakly
    separable from K_max draws, so pi is expected to be unstable upward. Nelder-Mead on
    (logit pi, log a, log b) — no SciPy.
    """
    if not ks:
        return {"pi": None, "note": "AUTHOR_INPUT_NEEDED: no instances"}

    def nll(theta: list[float]) -> float:
        pi = 1 / (1 + math.exp(-theta[0]))
        a, b = math.exp(theta[1]), math.exp(theta[2])
        if not (1e-9 < pi < 1 - 1e-12) or not (1e-6 < a < 1e6) or not (1e-6 < b < 1e6):
            return 1e18
        total = 0.0
        for k in ks:
            comp = math.exp(_betabinom_logpmf(k, k_max, a, b))
            like = pi * comp + ((1 - pi) if k == 0 else 0.0)
            total -= math.log(max(like, 1e-300))
        return total

    simplex = [[0.0, 0.0, 1.0], [1.0, 0.0, 1.0], [0.0, 1.0, 1.0], [0.0, 0.0, 2.0]]
    values = [nll(s) for s in simplex]
    for _ in range(600):
        order = sorted(range(len(simplex)), key=lambda i: values[i])
        simplex = [simplex[i] for i in order]
        values = [values[i] for i in order]
        centroid = [sum(s[d] for s in simplex[:-1]) / 3 for d in range(3)]
        worst = simplex[-1]
        refl = [centroid[d] + 1.0 * (centroid[d] - worst[d]) for d in range(3)]
        fr = nll(refl)
        if fr < values[0]:
            exp_ = [centroid[d] + 2.0 * (centroid[d] - worst[d]) for d in range(3)]
            fe = nll(exp_)
            simplex[-1], values[-1] = (exp_, fe) if fe < fr else (refl, fr)
        elif fr < values[-2]:
            simplex[-1], values[-1] = refl, fr
        else:
            con = [centroid[d] + 0.5 * (worst[d] - centroid[d]) for d in range(3)]
            fc = nll(con)
            if fc < values[-1]:
                simplex[-1], values[-1] = con, fc
            else:
                for i in range(1, 4):
                    simplex[i] = [(simplex[i][d] + simplex[0][d]) / 2 for d in range(3)]
                    values[i] = nll(simplex[i])
    best = simplex[min(range(4), key=lambda i: values[i])]
    return {"pi": 1 / (1 + math.exp(-best[0])), "a": math.exp(best[1]),
            "b": math.exp(best[2]), "nll": min(values)}


def bootstrap_asymptote(ks_by_problem: dict[str, list[int]], k_max: int,
                        reps: int, seed: int) -> tuple[list[float], list[float]]:
    """Resample **problem clusters**, refit, return the asymptote and the raw union-at-K_max.

    The instance is the unit of analysis and the problem is the cluster: 68 problems
    contribute two instances each and they move together, so the interval carries the
    dependence rather than assuming it away.
    """
    problems = sorted(ks_by_problem)
    rng = random.Random(seed)
    fitted, raw = [], []
    for _ in range(reps):
        drawn: list[int] = []
        for _ in range(len(problems)):
            drawn.extend(ks_by_problem[problems[rng.randrange(len(problems))]])
        curve = union_curve(drawn, k_max)
        fit = fit_saturation(curve)
        if fit["A"] is not None:
            fitted.append(min(1.0, max(0.0, fit["A"])))
            raw.append(curve[-1])
    return fitted, raw


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = q * (len(ordered) - 1)
    low, high = int(math.floor(index)), int(math.ceil(index))
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (index - low)


def mixed_curve(draws: dict[str, dict[int, dict[str, bool]]], families: list[str],
                ids: list[str], per_family: int) -> float | None:
    """Union rate for a subset taking ``per_family`` draws from each named family.

    Exact, by independence of the choices: an instance is missed only if every chosen
    draw misses it, and the choices in different families are independent, so the miss
    probability is the product of each family's hypergeometric miss probability.
    """
    ks_avail = {f: sorted(d for d in draws[f] if isinstance(d, int)) for f in families}
    if any(len(ks_avail[f]) < per_family for f in families):
        return None
    acc = 0.0
    for i in ids:
        miss = 1.0
        for f in families:
            total = len(ks_avail[f])
            hits = sum(1 for d in ks_avail[f] if draws[f][d].get(i))
            miss *= (math.comb(total - hits, per_family) / math.comb(total, per_family)
                     if total - hits >= per_family else 0.0)
        acc += 1.0 - miss
    return acc / len(ids)


def analyse_ceiling1(instances: dict, audit_set: list[str]) -> dict:
    scope = [i for i in audit_set if instances[i]["stratum"] in ("P", "C")]
    draws = load_draws(set(scope))
    P = [i for i in scope if instances[i]["stratum"] == "P"]
    C = [i for i in scope if instances[i]["stratum"] == "C"]
    out: dict = {"unit_of_analysis": "instance (batch, problem_id); intervals resample "
                                    "problem clusters",
                 "n_P": len(P), "n_C": len(C), "families": {}}

    for family in FAMILIES:
        complete = sorted(d for d in draws[family] if isinstance(d, int))
        partial = sorted(str(d) for d in draws[family] if not isinstance(d, int))
        if not complete:
            out["families"][family] = {"k_max": 0, "partial_draws": partial,
                                       "note": "not run"}
            continue
        k_max = len(complete)
        entry: dict = {"k_max": k_max, "draws_used": complete, "partial_draws": partial}
        for label, ids in (("P", P), ("C", C)):
            ks = counts_per_instance(draws[family], ids)
            curve = union_curve(ks, k_max)
            fit = fit_saturation(curve)
            zibb = fit_zibb(ks, k_max)
            by_problem: dict[str, list[int]] = {}
            for i, k in zip(ids, ks):
                by_problem.setdefault(instances[i]["problem_id"], []).append(k)
            boot_A, boot_raw = bootstrap_asymptote(by_problem, k_max, BOOTSTRAP, BOOT_SEED)
            flat = (curve[-1] - curve[-2]) if len(curve) >= 2 else None
            single = sum(1 for k in ks if k > 0)  # instances any draw ever flagged
            entry[label] = {
                "n_instances": len(ids),
                "curve": [round(v, 6) for v in curve],
                "counts_k": {str(k): ks.count(k) for k in range(0, k_max + 1)},
                "union_at_kmax": curve[-1],
                "union_at_kmax_count": single,
                "union_at_kmax_wilson95": list(wilson(single, len(ids))),
                "draw1_rate": curve[0],
                "fit": fit,
                "fit_A_ci95": [percentile(boot_A, 0.025), percentile(boot_A, 0.975)],
                "raw_kmax_ci95": [percentile(boot_raw, 0.025), percentile(boot_raw, 0.975)],
                "zibb_secondary": zibb,
                "marginal_gain_last_step": flat,
                "asymptote_is_extrapolation": (flat is not None and flat > 0.01),
                "bootstrap_reps": len(boot_A),
            }
        entry["exchange_rate_recall_per_fp"] = (
            (entry["P"]["union_at_kmax"] - entry["P"]["draw1_rate"]) /
            (entry["C"]["union_at_kmax"] - entry["C"]["draw1_rate"])
            if entry["C"]["union_at_kmax"] > entry["C"]["draw1_rate"] else None)
        out["families"][family] = entry

    # Primary outcome: A(self) - A(cross), bootstrapped on the same problem clusters so
    # the two curves are resampled together and the difference keeps its pairing.
    ready = [f for f in ("cross", "self") if out["families"].get(f, {}).get("k_max")]
    k_common = (min(out["families"]["cross"]["k_max"], out["families"]["self"]["k_max"])
                if len(ready) == 2 else 0)
    out["k_common"] = k_common
    if k_common < 2:
        out["primary_ceiling1_status"] = (
            "AUTHOR_INPUT_NEEDED: fewer than two complete draws in one of the two "
            f"families (K_common = {k_common}); the asymptote is not estimable yet")
    if len(ready) == 2 and k_common >= 2:
        diff = {}
        for label, ids in (("P", P), ("C", C)):
            by_problem: dict[str, list[tuple[int, int]]] = {}
            for i in ids:
                kc = sum(1 for d in range(1, k_common + 1) if draws["cross"][d].get(i))
                ksf = sum(1 for d in range(1, k_common + 1) if draws["self"][d].get(i))
                by_problem.setdefault(instances[i]["problem_id"], []).append((kc, ksf))
            point = {}
            for name, index in (("cross", 0), ("self", 1)):
                ks = [pair[index] for v in by_problem.values() for pair in v]
                point[name] = fit_saturation(union_curve(ks, k_common))["A"]
            problems = sorted(by_problem)
            rng = random.Random(BOOT_SEED + 1)
            deltas, raw_deltas = [], []
            for _ in range(BOOTSTRAP):
                kc_s, ks_s = [], []
                for _ in range(len(problems)):
                    for pair in by_problem[problems[rng.randrange(len(problems))]]:
                        kc_s.append(pair[0])
                        ks_s.append(pair[1])
                cc, cs = union_curve(kc_s, k_common), union_curve(ks_s, k_common)
                ac, a_s = fit_saturation(cc)["A"], fit_saturation(cs)["A"]
                if ac is not None and a_s is not None:
                    deltas.append(a_s - ac)
                    raw_deltas.append(cs[-1] - cc[-1])
            diff[label] = {
                "A_cross": point["cross"], "A_self": point["self"],
                "A_self_minus_cross": (point["self"] - point["cross"]),
                "ci95": [percentile(deltas, 0.025), percentile(deltas, 0.975)],
                "raw_union_diff_at_k_common": (
                    union_curve([p[1] for v in by_problem.values() for p in v], k_common)[-1]
                    - union_curve([p[0] for v in by_problem.values() for p in v],
                                  k_common)[-1]),
                "raw_diff_ci95": [percentile(raw_deltas, 0.025),
                                  percentile(raw_deltas, 0.975)],
                "k_common": k_common, "n_instances": len(ids),
                "bootstrap_reps": len(deltas),
            }
        out["primary_ceiling1"] = diff

    # mixed: equal draws from each family at matched total K
    mixed: dict = {}
    for combo in (("cross", "self"), ("cross", "self", "astra"), ("cross", "astra"),
                  ("self", "astra")):
        available = [f for f in combo if out["families"].get(f, {}).get("k_max")]
        if len(available) != len(combo):
            continue
        per_max = min(out["families"][f]["k_max"] for f in combo)
        rows = {}
        for per in range(1, per_max + 1):
            total = per * len(combo)
            entry = {"total_draws": total, "per_family": per}
            for label, ids in (("P", P), ("C", C)):
                entry[label] = mixed_curve(draws, list(combo), ids, per)
                # the same total K spent inside one family, for the comparison that matters
                for f in combo:
                    if out["families"][f]["k_max"] >= total:
                        ks = counts_per_instance(draws[f], ids)
                        entry[f"{label}_{f}_alone_at_{total}"] = union_curve(
                            ks, out["families"][f]["k_max"])[total - 1]
            rows[str(total)] = entry
        mixed["+".join(combo)] = rows
    out["mixed"] = mixed

    # the residual: stratum-P instances no draw of any family ever flagged
    residual: dict = {}
    all_families = [f for f in FAMILIES if out["families"].get(f, {}).get("k_max")]
    for label, subset in (("three_families_all_P", [f for f in all_families if f != "astra"]),
                          ("all_families", all_families)):
        if not subset:
            continue
        ids = P
        never = []
        for i in ids:
            hit = any(draws[f][d].get(i)
                      for f in subset for d in draws[f] if isinstance(d, int))
            if not hit:
                never.append(i)
        residual[label] = {
            "families": subset,
            "total_draws": sum(out["families"][f]["k_max"] for f in subset),
            "n_P": len(ids), "n_never_flagged": len(never),
            "share": len(never) / len(ids) if ids else None,
            "share_wilson95": list(wilson(len(never), len(ids))),
            "instance_ids": sorted(never),
        }
    out["residual"] = residual

    # The hand classification (§1.5), if it has been made. Categories only — no corpus
    # text — and the rule was fixed in the preregistration before the first instance was
    # read. Unclassified residual instances are counted and named, never quietly dropped.
    path = CEILING / "residual_classification.json"
    if path.exists():
        table = json.loads(path.read_text(encoding="utf-8"))
        by_pop = {}
        for label, r in residual.items():
            counts: dict[str, int] = {}
            missing = []
            for iid in r["instance_ids"]:
                cat = (table.get("classification", {}).get(iid) or {}).get("category")
                if cat is None:
                    missing.append(iid)
                else:
                    counts[cat] = counts.get(cat, 0) + 1
            by_pop[label] = {
                "n": r["n_never_flagged"], "counts": counts,
                "shares": {k: v / r["n_never_flagged"] for k, v in counts.items()}
                if r["n_never_flagged"] else {},
                "wilson95": {k: list(wilson(v, r["n_never_flagged"]))
                             for k, v in counts.items()},
                "unclassified": missing,
                "rule_version": table.get("rule_version", "AUTHOR_INPUT_NEEDED"),
            }
        out["residual_classified"] = by_pop
    else:
        out["residual_classified"] = {
            "status": "AUTHOR_INPUT_NEEDED: records/ceiling/residual_classification.json "
                      "has not been written yet"}
    return out


def load_spend() -> dict:
    """Study spend, from the committed manifests. Never reconstructed, never guessed."""
    out: dict = {}
    for name, path in (("ceiling1", CEILING / "manifest_ceiling1.json"),
                       ("ceiling2", CEILING / "manifest_loop.json")):
        if path.exists():
            m = json.loads(path.read_text(encoding="utf-8"))
            all_ledgers = (m.get("spend_usd_ceiling2_all_ledgers") or {}).get("usd")
            out[name] = {
                "spend_usd": (all_ledgers if all_ledgers is not None
                              else m.get("spend_usd_cumulative", m.get("spend_usd_total"))),
                "calls": (m.get("spend_usd_ceiling2_all_ledgers") or {}).get("calls"),
                "astra_tokens": m.get("astra_tokens_cumulative"),
                "note": m.get("astra", {}).get("bypasses") if name == "ceiling1" else None,
            }
        else:
            out[name] = {"spend_usd": None,
                         "note": f"AUTHOR_INPUT_NEEDED: {path.name} not written"}
    return out


# ---------------------------------------------------------------------------------
# ceiling 2 — the closed loop
# ---------------------------------------------------------------------------------

def load_arm(arm: str) -> list[dict]:
    path = LOOP / f"{arm}.jsonl"
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def analyse_ceiling2(instances: dict) -> dict:
    out: dict = {"unit_of_analysis": "instance; paired before/after on the same instance",
                 "arms": {}, "contrasts": {}}
    arm_rows: dict[str, dict[str, dict]] = {}
    for arm in LOOP_ARMS:
        rows = load_arm(arm)
        if not rows:
            out["arms"][arm] = {"note": "not run"}
            continue
        by_id = {r["instance_id"]: r for r in rows}
        arm_rows[arm] = by_id
        n = len(rows)
        fixed = [r for r in rows if not r["hidden_passed_before"] and r["hidden_passed_after"]]
        broken = [r for r in rows if r["hidden_passed_before"] and not r["hidden_passed_after"]]
        P = [r for r in rows if r["stratum"] == "P"]
        C = [r for r in rows if r["stratum"] == "C"]
        revised = [r for r in rows if r["revised"]]
        changed = [r for r in rows if r["changed"]]
        entry = {
            "n_instances": n, "n_P": len(P), "n_C": len(C),
            "flag_rate_P": {"k": sum(1 for r in P if r.get("flagged")), "n": len(P)},
            "flag_rate_C": {"k": sum(1 for r in C if r.get("flagged")), "n": len(C)},
            "blocked_P": sum(1 for r in P if r.get("verdict") == "BLOCKED"),
            "blocked_C": sum(1 for r in C if r.get("verdict") == "BLOCKED"),
            "n_revised": len(revised), "n_changed": len(changed),
            "n_returned_non_solution": sum(1 for r in rows if r.get("returned_non_solution")),
            "fixed_on_P": {"k": len(fixed), "n": len(P),
                           "wilson95": list(wilson(len(fixed), len(P)))},
            "broken_on_C": {"k": len(broken), "n": len(C),
                            "wilson95": list(wilson(len(broken), len(C)))},
            "net_primary": paired_difference_exact(len(fixed), len(broken), n),
            "pass_rate_before": {"k": sum(1 for r in rows if r["hidden_passed_before"]),
                                 "n": n},
            "pass_rate_after": {"k": sum(1 for r in rows if r["hidden_passed_after"]),
                                "n": n},
            "audit_cost_usd": round(sum(float(r.get("audit_cost_usd") or 0.0)
                                        for r in rows), 6),
            "revise_cost_usd": round(sum(float(r.get("revise_cost_usd_apportioned") or 0.0)
                                         for r in rows), 6),
        }
        # exploratory, labelled: conditioned on a post-treatment variable (CORRECTIONS #9)
        cond = [r for r in rows if r["changed"]]
        cf = sum(1 for r in cond if not r["hidden_passed_before"] and r["hidden_passed_after"])
        cb = sum(1 for r in cond if r["hidden_passed_before"] and not r["hidden_passed_after"])
        entry["conditional_on_change_EXPLORATORY"] = {
            "n": len(cond), "fixed": cf, "broken": cb,
            "net": ((cf - cb) / len(cond)) if cond else None,
            "warning": "conditions on a post-treatment variable; exploratory only"}
        # bootstrap over problem clusters, secondary (amendment 3)
        by_problem: dict[str, list[int]] = {}
        for r in rows:
            delta = int(r["hidden_passed_after"]) - int(r["hidden_passed_before"])
            by_problem.setdefault(r["problem_id"], []).append(delta)
        problems = sorted(by_problem)
        rng = random.Random(BOOT_SEED + 2)
        nets = []
        for _ in range(BOOTSTRAP):
            vals = []
            for _ in range(len(problems)):
                vals.extend(by_problem[problems[rng.randrange(len(problems))]])
            nets.append(sum(vals) / len(vals))
        entry["net_bootstrap_secondary_ci95"] = [percentile(nets, 0.025),
                                                 percentile(nets, 0.975)]
        out["arms"][arm] = entry

    # paired arm-vs-arm on the after-revision outcome, exact McNemar
    for a, b in (("self-loop", "cross-loop"), ("referent-loop", "cross-loop"),
                 ("self-loop", "self-loop-rep")):
        if a not in arm_rows or b not in arm_rows:
            continue
        shared = sorted(set(arm_rows[a]) & set(arm_rows[b]))
        only_a = sum(1 for i in shared
                     if arm_rows[a][i]["hidden_passed_after"]
                     and not arm_rows[b][i]["hidden_passed_after"])
        only_b = sum(1 for i in shared
                     if arm_rows[b][i]["hidden_passed_after"]
                     and not arm_rows[a][i]["hidden_passed_after"])
        entry = paired_difference_exact(only_a, only_b, len(shared))
        entry["arms"] = [a, b]
        entry["label"] = f"{a} minus {b}, hidden-test pass after one round"
        # The flag rate is the mechanism behind any net effect, so it is shown paired and
        # split by stratum: on P a flag is a defect caught, on C it is a false alarm, and
        # a single pooled discordance would hide which of the two moved.
        entry["flag_discordance"] = {}
        for stratum in ("P", "C", "all"):
            ids = [i for i in shared
                   if stratum == "all" or arm_rows[a][i]["stratum"] == stratum]
            fa = sum(1 for i in ids if arm_rows[a][i].get("flagged")
                     and not arm_rows[b][i].get("flagged"))
            fb = sum(1 for i in ids if arm_rows[b][i].get("flagged")
                     and not arm_rows[a][i].get("flagged"))
            entry["flag_discordance"][stratum] = {
                "n": len(ids), "only_" + a: fa, "only_" + b: fb,
                "flagged_" + a: sum(1 for i in ids if arm_rows[a][i].get("flagged")),
                "flagged_" + b: sum(1 for i in ids if arm_rows[b][i].get("flagged")),
                "difference": (fa - fb) / len(ids) if ids else None,
                "ci95": paired_difference_exact(fa, fb, len(ids))["ci95"],
                "p_exact": mcnemar_exact(fa, fb)}
        out["contrasts"][f"{a}__vs__{b}"] = entry

    if "self-loop" in out["arms"] and "self-loop-rep" in out["arms"]:
        a = out["arms"]["self-loop"]
        b = out["arms"]["self-loop-rep"]
        if "net_primary" in a and "net_primary" in b:
            out["loop_noise_floor"] = {
                "self-loop_net": a["net_primary"]["delta"],
                "self-loop-rep_net": b["net_primary"]["delta"],
                "spread_pp": abs(a["net_primary"]["delta"] - b["net_primary"]["delta"]) * 100,
                "self-loop_flagged_P": a["flag_rate_P"], "rep_flagged_P": b["flag_rate_P"],
                "note": "the replicate EXPERIMENT_RECORD.md §9 requires for this estimand; "
                        "two runs bound nothing tightly, and that is stated at the number",
            }
    return out


# ---------------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------------

def pct(x: float | None, places: int = 1) -> str:
    return "—" if x is None else f"{100 * x:.{places}f}%"


def ci(pair, places: int = 1) -> str:
    if not pair or pair[0] is None:
        return "—"
    return f"[{100 * pair[0]:.{places}f}, {100 * pair[1]:.{places}f}]"


def tables(numbers: dict) -> str:
    lines: list[str] = []
    c1 = numbers["ceiling1"]
    lines.append("<!-- generated by report_ceiling.py; do not hand-edit -->\n")
    lines.append("### Table 1 — the saturation curve, per family\n")
    lines.append(f"Unit of analysis: the instance. n = {c1['n_P']} stratum-P instances "
                 f"(recall) and {c1['n_C']} stratum-C instances (false positives), the "
                 f"same instances at every K. Union rate at K is averaged over all "
                 f"C(K_max, K) subsets of that family's draws, exactly.\n")
    lines.append("| family | K_max | union recall on P at K=1 | at K_max | "
                 "fitted asymptote A [95% bootstrap CI over problems] | union FP on C at "
                 "K=1 | at K_max | last-step gain on P |")
    lines.append("|---|---:|---:|---:|---|---:|---:|---:|")
    for family in FAMILIES:
        f = c1["families"].get(family, {})
        if not f.get("k_max"):
            lines.append(f"| `{family}` | — | — | — | not run | — | — | — |")
            continue
        P, C = f["P"], f["C"]
        lines.append(
            f"| `{family}` | {f['k_max']} | {pct(P['draw1_rate'])} | "
            f"**{pct(P['union_at_kmax'])}** ({P['union_at_kmax_count']}/{P['n_instances']}) | "
            f"**{pct(P['fit']['A'])}** {ci(P['fit_A_ci95'])} | {pct(C['draw1_rate'])} | "
            f"**{pct(C['union_at_kmax'])}** | {pct(P['marginal_gain_last_step'], 2)} |")
    lines.append("")
    lines.append("### Table 2 — union recall and union false positives at every K\n")
    lines.append("Unit of analysis: the instance; the same instances at every K, so the "
                 "columns are repeated measures and not independent samples.\n")
    for family in FAMILIES:
        f = c1["families"].get(family, {})
        if not f.get("k_max"):
            continue
        lines.append(f"\n**`{family}`** (K_max = {f['k_max']}, "
                     f"n = {f['P']['n_instances']} P instances, "
                     f"{f['C']['n_instances']} C instances)\n")
        lines.append("| K | union recall on P | union FP on C | recall per FP point |")
        lines.append("|---:|---:|---:|---:|")
        for index, (r, fp) in enumerate(zip(f["P"]["curve"], f["C"]["curve"]), start=1):
            ratio = ((r - f["P"]["curve"][0]) / (fp - f["C"]["curve"][0])
                     if index > 1 and fp > f["C"]["curve"][0] else None)
            lines.append(f"| {index} | {pct(r)} | {pct(fp)} | "
                         f"{'—' if ratio is None else f'{ratio:.2f}'} |")
    if "primary_ceiling1" in c1:
        lines.append("\n### Table 3 — primary outcome, ceiling 1: A(self) − A(cross)\n")
        lines.append(f"K_common = {c1['k_common']} draws per family. Positive means the "
                     "generator's own model can ultimately see more of its own defects "
                     "than a stranger can. Interval: 95% percentile bootstrap over "
                     "problem clusters, both curves resampled together.\n")
        lines.append("| stratum | n instances | A(cross) | A(self) | A(self) − A(cross) "
                     "[95% CI] | raw union difference at K_common [95% CI] |")
        lines.append("|---|---:|---:|---:|---|---|")
        for label in ("P", "C"):
            d = c1["primary_ceiling1"][label]
            lines.append(
                f"| {label} | {d['n_instances']} | {pct(d['A_cross'])} | "
                f"{pct(d['A_self'])} | **{pct(d['A_self_minus_cross'])}** "
                f"{ci(d['ci95'])} | {pct(d['raw_union_diff_at_k_common'])} "
                f"{ci(d['raw_diff_ci95'])} |")
    if c1.get("mixed"):
        lines.append("\n### Table 4 — mixed families at matched total draws\n")
        lines.append("Unit of analysis: the instance. Each row spends the same total "
                     "number of readings; the question is whether spreading them across "
                     "families beats spending them all inside one.\n")
        lines.append("| combination | total draws | per family | union recall on P | "
                     "union FP on C | same total inside one family (recall) |")
        lines.append("|---|---:|---:|---:|---:|---|")
        for combo, rows in c1["mixed"].items():
            for total, row in sorted(rows.items(), key=lambda kv: int(kv[0])):
                alone = "; ".join(
                    f"`{f}` {pct(row[k])}" for f in FAMILIES
                    for k in [f"P_{f}_alone_at_{total}"] if k in row)
                lines.append(f"| `{combo}` | {total} | {row['per_family']} | "
                             f"{pct(row['P'])} | {pct(row['C'])} | {alone or '—'} |")
    if c1.get("residual"):
        lines.append("\n### Table 5 — the residual: stratum-P defects no draw ever flagged\n")
        lines.append("| population | families | total draws | n P instances | "
                     "never flagged | share [95% Wilson] |")
        lines.append("|---|---|---:|---:|---:|---|")
        for label, r in c1["residual"].items():
            lines.append(f"| {label} | {', '.join(r['families'])} | {r['total_draws']} | "
                         f"{r['n_P']} | **{r['n_never_flagged']}** | "
                         f"{pct(r['share'])} {ci(r['share_wilson95'])} |")

    rcl = c1.get("residual_classified") or {}
    if rcl and "status" not in rcl:
        lines.append("\n### Table 5b — what the residual defects are\n")
        lines.append("Categories and their order were fixed in the preregistration "
                     "(§1.5) before the first residual instance was read; each instance "
                     "takes the first category that applies. Unit: the instance. "
                     "Intervals are 95% Wilson on the residual denominator.\n")
        lines.append("| population | n residual | category | count | share [95% Wilson] |")
        lines.append("|---|---:|---|---:|---|")
        for label, r in rcl.items():
            for cat, count in sorted(r["counts"].items(), key=lambda kv: -kv[1]):
                lines.append(f"| {label} | {r['n']} | `{cat}` | {count} | "
                             f"{pct(r['shares'][cat])} {ci(r['wilson95'][cat])} |")
            if r["unclassified"]:
                lines.append(f"| {label} | {r['n']} | **unclassified** | "
                             f"{len(r['unclassified'])} | AUTHOR_INPUT_NEEDED |")

    c2 = numbers["ceiling2"]
    lines.append("\n### Table 6 — ceiling 2: the closed loop, per arm\n")
    lines.append("Unit of analysis: the instance, paired before/after on the same "
                 "instance. Net is unconditional on whether a revision occurred. "
                 "Interval and p: exact-conditional (Clopper–Pearson on the discordant "
                 "pairs) and exact McNemar.\n")
    lines.append("| arm | n | audits BLOCKED (P / C) | revisions that changed the file | "
                 "fixed on P | broken on C | **net change in hidden-test pass rate** "
                 "[95% exact CI] | exact p |")
    lines.append("|---|---:|---:|---:|---|---|---|---:|")
    for arm in LOOP_ARMS:
        a = c2["arms"].get(arm, {})
        if "n_instances" not in a:
            lines.append(f"| `{arm}` | — | — | — | — | — | not run | — |")
            continue
        net = a["net_primary"]
        lines.append(
            f"| `{arm}` | {a['n_instances']} | {a['blocked_P']} / {a['blocked_C']} | "
            f"{a['n_changed']} | {a['fixed_on_P']['k']}/{a['fixed_on_P']['n']} "
            f"{ci(a['fixed_on_P']['wilson95'])} | {a['broken_on_C']['k']}/"
            f"{a['broken_on_C']['n']} {ci(a['broken_on_C']['wilson95'])} | "
            f"**{net['delta'] * 100:+.2f} pp** {ci(net['ci95'], 2)} "
            f"(b={net['b']}, c={net['c']}) | {net['p_exact']:.4f} |")
    if c2.get("contrasts"):
        lines.append("\n### Table 7 — paired contrasts between arms\n")
        lines.append("Outcome: whether the instance passes the hidden suite after one "
                     "round. Unit: the instance, paired across arms. Exact McNemar on "
                     "the discordant pairs; both discordant counts shown.\n")
        lines.append("| contrast | n instances | discordant (b / c) | difference "
                     "[95% exact CI] | exact p | Bonferroni/12 threshold |")
        lines.append("|---|---:|---:|---|---:|---:|")
        for key, d in c2["contrasts"].items():
            lines.append(f"| {d['label']} | {d['n']} | {d['b']} / {d['c']} | "
                         f"{d['delta'] * 100:+.2f} pp {ci(d['ci95'], 2)} | "
                         f"{d['p_exact']:.4f} | 0.00417 |")
        lines.append("\n### Table 7b — what the arms flag, paired and split by stratum\n")
        lines.append("The mechanism behind any net effect. On stratum P a flag is a "
                     "defect caught; on stratum C it is a false alarm. Unit: the "
                     "instance, paired across arms; exact McNemar on the discordant "
                     "pairs.\n")
        lines.append("| contrast | stratum | n | flagged by each | discordant (b / c) | "
                     "difference [95% exact CI] | exact p |")
        lines.append("|---|---|---:|---|---:|---|---:|")
        for key, d in c2["contrasts"].items():
            a, b = d["arms"]
            for stratum in ("P", "C"):
                f = d["flag_discordance"][stratum]
                lines.append(
                    f"| `{a}` vs `{b}` | {stratum} | {f['n']} | "
                    f"{f['flagged_' + a]} vs {f['flagged_' + b]} | "
                    f"{f['only_' + a]} / {f['only_' + b]} | "
                    f"{f['difference'] * 100:+.2f} pp {ci(f['ci95'], 2)} | "
                    f"{f['p_exact']:.4f} |")
    spend = numbers.get("spend", {})
    lines.append("\n### Table 8 — what it cost\n")
    lines.append("From the product's own usage ledgers, per call, not reconstructed. The "
                 "`astra` route bills a subscription and reports only tokens, so it "
                 "consumes none of the dollar budget and is quoted in tokens.\n")
    lines.append("| part | model spend | astra tokens |")
    lines.append("|---|---:|---:|")
    for part in ("ceiling1", "ceiling2"):
        s = spend.get(part, {})
        usd = s.get("spend_usd")
        tok = s.get("astra_tokens")
        lines.append(f"| {part} | {'AUTHOR_INPUT_NEEDED' if usd is None else f'${usd:.4f}'}"
                     f" | {'—' if not tok else f'{tok:,}'} |")
    total = sum(v.get("spend_usd") or 0.0 for v in spend.values())
    lines.append(f"| **total** | **${total:.4f}** | "
                 f"{sum(v.get('astra_tokens') or 0 for v in spend.values()):,} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    global BOOTSTRAP
    parser.add_argument("--bootstrap", type=int, default=BOOTSTRAP)
    args = parser.parse_args(argv)
    BOOTSTRAP = args.bootstrap

    instances = load_instances()
    audit_set = load_audit_set()
    numbers = {
        "study": "ceiling (study 8)",
        "preregistration": "benchmarks/code/ceiling/PREREGISTRATION.md",
        "bootstrap_reps": BOOTSTRAP, "bootstrap_seed": BOOT_SEED,
        "ceiling1": analyse_ceiling1(instances, audit_set),
        "ceiling2": analyse_ceiling2(instances),
        "spend": load_spend(),
    }
    CEILING.mkdir(parents=True, exist_ok=True)
    (CEILING / "numbers.json").write_text(
        json.dumps(numbers, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rendered = tables(numbers)
    (CEILING / "tables.md").write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
