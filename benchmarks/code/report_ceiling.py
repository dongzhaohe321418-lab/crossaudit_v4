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
import itertools
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
#: The exact unconditional interval is a check, not the primary, and it is the
#: one expensive estimator here; --no-exact-unconditional turns it off.
EXACT_UNCONDITIONAL = True


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


def tango_score_interval(b: int, c: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Tango's score interval for the paired difference delta = p_b - p_c.

    **Unconditional**: it does not condition on the number of discordant pairs, so unlike
    the withdrawn conditional construction it carries the uncertainty in how many
    discordances there are. Under H0: delta = d, the constrained MLE of the nuisance
    p_c solves dL/dq = 0 for the multinomial (b, c, rest); the score statistic is

        z(d) = (b - c - n d) / sqrt(n (2 q_hat(d) + d (1 - d)))

    whose variance term is Var(b - c) = n(p_b + p_c - (p_b - p_c)^2) under that model.
    The interval is the set of d with |z(d)| <= z_{alpha/2}, found by bisection because
    z is monotone decreasing in d. Its coverage is measured, not assumed
    (``tests/test_ceiling_stats.py::test_replacement_intervals_have_their_advertised_coverage``).
    """
    z = 1.959963984540054 if abs(alpha - 0.05) < 1e-12 else _z_for(alpha)

    def q_hat(d: float) -> float:
        # q = p_c, so the feasible set is q >= 0, q >= -d, and 2q + d <= 1, i.e.
        #     max(0, -d) <= q <= (1 - d)/2.
        # The upper bound is (1 - d)/2, NOT (1 - |d|)/2: for d < 0 the latter is far too
        # tight and truncates the nuisance range on exactly the side where p_c is large.
        # That defect made the interval wrong for detrimental differences and broke the
        # sign symmetry that test_paired_interval_is_sign_symmetric now pins.
        lo, hi = max(0.0, -d) + 1e-12, (1.0 - d) / 2 - 1e-12
        if hi <= lo:
            return max(lo, 0.0)

        def deriv(q: float) -> float:
            rest = 1.0 - 2 * q - d
            if q + d <= 0 or q <= 0 or rest <= 0:
                return float("inf")
            return b / (q + d) + c / q - 2 * (n - b - c) / rest

        if deriv(lo) < 0:
            return lo
        if deriv(hi) > 0:
            return hi
        for _ in range(200):
            mid = (lo + hi) / 2
            if deriv(mid) > 0:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    def score(d: float) -> float:
        var = n * (2 * q_hat(d) + d * (1 - d))
        if var <= 0:
            return float("inf") if (b - c - n * d) > 0 else float("-inf")
        return (b - c - n * d) / math.sqrt(var)

    point = (b - c) / n

    def solve(target: float, lo: float, hi: float) -> float:
        for _ in range(200):
            mid = (lo + hi) / 2
            if score(mid) > target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    return (solve(z, -1.0 + 1e-9, point), solve(-z, point, 1.0 - 1e-9))


def _z_for(alpha: float) -> float:
    lo, hi = 0.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        # two-sided: P(|Z| > mid) = alpha  =>  erfc(mid/sqrt2) = alpha
        if math.erfc(mid / math.sqrt(2)) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def exact_unconditional_interval(b: int, c: int, n: int, alpha: float = 0.05,
                                 grid: int = 40, gamma: float = 1e-4) -> tuple[float, float]:
    """Exact unconditional interval for delta, by inverting a maximised exact test.

    For each candidate delta the p-value is **maximised over the nuisance parameter**
    p_c on a grid, using the exact multinomial distribution of (b, c) rather than any
    normal approximation; delta is retained when that maximised p-value exceeds alpha.
    This is the standard exact-unconditional construction, **grid-approximated**: the
    supremum is taken over a finite nuisance grid (41 points) without a bound on what a
    finer grid could add, so it is not a guaranteed exact interval and this report does
    not claim it never under-covers. Its measured coverage is reported at the study's own
    n and scenario, in both the beneficial and the detrimental direction.

    Cost is bounded by pruning the (b, c) lattice to cells whose log-probability can
    matter. Reported as a **check** on the primary clustered bootstrap, never as the
    primary interval, and it ignores clustering exactly as Tango's does.
    """
    logfac = [0.0] * (n + 1)
    for i in range(1, n + 1):
        logfac[i] = logfac[i - 1] + math.log(i)
    cells = [(x, y) for x in range(n + 1) for y in range(n + 1 - x)]
    coef = {(x, y): logfac[n] - logfac[x] - logfac[y] - logfac[n - x - y] for x, y in cells}
    t_obs = b - c

    # Berger-Boos: restrict the nuisance to a (1 - gamma) confidence set built from the
    # OBSERVED discordance count, then add gamma to the maximised p-value. Without this
    # restriction the supremum runs over nuisance values the data exclude, and the
    # interval is so conservative it is uninformative (it returned +/- 20 points on
    # n = 112 before this was added).
    d_obs = b + c
    s_lo, s_hi = clopper_pearson(d_obs, n, alpha=gamma)      # for p_b + p_c = 2q + d

    def maximised_p(d: float) -> float:
        # q = p_c: feasible set max(0, -d) <= q <= (1 - d)/2, intersected with the
        # Berger-Boos confidence set for s = p_b + p_c = 2q + d. The upper bound is
        # (1 - d)/2; using (1 - |d|)/2 truncated it for negative d and drove coverage in
        # the detrimental direction to 0.075.
        lo_q = max(0.0, -d, (s_lo - d) / 2)
        hi_q = min((1.0 - d) / 2, (s_hi - d) / 2)
        if hi_q < lo_q:
            return 0.0
        best = 0.0
        for g in range(grid + 1):
            q = lo_q + (hi_q - lo_q) * g / grid
            pb, pc = q + d, q
            rest = 1.0 - pb - pc
            if pb < 0 or pc < 0 or rest < -1e-12:
                continue
            lpb = math.log(pb) if pb > 0 else float("-inf")
            lpc = math.log(pc) if pc > 0 else float("-inf")
            lre = math.log(rest) if rest > 0 else float("-inf")
            total = 0.0
            centre = n * d
            for x, y in cells:
                if abs((x - y) - centre) < abs(t_obs - centre) - 1e-9:
                    continue          # strictly less extreme than what was observed
                if (x > 0 and lpb == float("-inf")) or (y > 0 and lpc == float("-inf")):
                    continue
                if (n - x - y) > 0 and lre == float("-inf"):
                    continue
                lp = coef[(x, y)] + (x * lpb if x else 0.0) + (y * lpc if y else 0.0) \
                    + ((n - x - y) * lre if (n - x - y) else 0.0)
                if lp > -60:
                    total += math.exp(lp)
            best = max(best, min(1.0, total))
            if best + gamma > alpha:
                return best + gamma
        return best + gamma

    point = (b - c) / n

    def edge(direction: int) -> float:
        lo, hi = point, float(direction)
        for _ in range(24):
            mid = (lo + hi) / 2
            if maximised_p(mid) > alpha:
                lo = mid
            else:
                hi = mid
        return lo

    return (edge(-1), edge(1))


def cluster_bootstrap_ci(values_by_cluster: dict, reps: int, seed: int,
                         alpha: float = 0.05) -> tuple[float | None, float | None]:
    """Percentile bootstrap over whole clusters for a mean of per-instance values.

    The resampling unit is the **problem**: the 68 problems contributing two instances
    each move together, so the interval carries that dependence instead of assuming it
    away. This is the primary interval for every rate and every paired difference in
    this report.
    """
    clusters = sorted(values_by_cluster)
    if not clusters:
        return (None, None)
    rng = random.Random(seed)
    stats = []
    for _ in range(reps):
        acc, count = 0.0, 0
        for _ in range(len(clusters)):
            vals = values_by_cluster[clusters[rng.randrange(len(clusters))]]
            acc += sum(vals)
            count += len(vals)
        if count:
            stats.append(acc / count)
    return (percentile(stats, alpha / 2), percentile(stats, 1 - alpha / 2))


def signflip_p(values_by_cluster: dict, max_exact: int = 22) -> dict:
    """Cluster-level sign-flip permutation test on the per-problem totals.

    A problem contributes one number — the sum of its instances' signed changes — and the
    null flips the sign of whole problems. Enumerated exactly when there are at most
    ``max_exact`` non-zero clusters, otherwise sampled with a fixed seed and reported as
    such. This is a **sensitivity check beside** exact McNemar, not a replacement: it
    carries its own exchangeability assumption. It exists because McNemar treats
    instances as independent and, where problems repeat across batches, they are not.
    """
    totals = [sum(v) for v in values_by_cluster.values()]
    nz = [t for t in totals if t]
    observed = abs(sum(nz))
    if not nz:
        return {"p": 1.0, "n_clusters": len(totals), "n_nonzero_clusters": 0,
                "method": "no non-zero cluster; p = 1 by construction"}
    if len(nz) <= max_exact:
        hits = sum(1 for signs in itertools.product((1, -1), repeat=len(nz))
                   if abs(sum(s * t for s, t in zip(signs, nz))) >= observed)
        return {"p": hits / 2 ** len(nz), "n_clusters": len(totals),
                "n_nonzero_clusters": len(nz), "method": "exact enumeration"}
    rng = random.Random(BOOT_SEED + 7)
    reps = 200000
    hits = sum(1 for _ in range(reps)
               if abs(sum(t if rng.random() < 0.5 else -t for t in nz)) >= observed)
    return {"p": (hits + 1) / (reps + 1), "n_clusters": len(totals),
            "n_nonzero_clusters": len(nz),
            "method": f"sampled, {reps} draws, seed {BOOT_SEED + 7}"}


def paired_difference(values_by_cluster: dict, *, reps: int = None, seed: int = None,
                      exact_unconditional: bool = False) -> dict:
    """A paired binary difference, with an interval whose coverage has been measured.

    ``values_by_cluster`` maps a problem id to that problem's per-instance signed changes
    (+1 improved, -1 worsened, 0 unchanged). Everything else is derived, so no caller can
    supply a discordance count that disagrees with the clusters.

    **Primary interval: the cluster bootstrap.** **Checks: Tango's unconditional score
    interval and (optionally) an exact unconditional interval**, both of which ignore
    clustering and are labelled so. **Tests: exact McNemar, with a cluster-level
    sign-flip permutation p beside it.**

    The interval this replaces — a Clopper-Pearson interval for the direction probability
    *conditional on discordance*, rescaled by the *observed* discordance fraction — is
    retained under ``withdrawn_conditional_ci95`` with its measured coverage, because it
    was published and a reader is entitled to see what changed. Its coverage in the
    review's scenario (D ~ Binomial(112, 0.1), every discordance beneficial) is
    **0.416**, not 0.95: rescaling by the observed D discards the uncertainty in D.
    """
    reps = BOOTSTRAP if reps is None else reps
    seed = BOOT_SEED if seed is None else seed
    flat = [v for vals in values_by_cluster.values() for v in vals]
    n = len(flat)
    b = sum(1 for v in flat if v > 0)
    c = sum(1 for v in flat if v < 0)
    delta = (b - c) / n if n else 0.0
    # When every discordance points one way, a percentile bootstrap over the observed
    # values cannot produce a resample of the opposite sign, so its interval is
    # one-signed by construction and must NOT be read as excluding zero. That is
    # CORRECTIONS.md item 4, and it applies to this bootstrap exactly as it applied to
    # the construction that item withdrew. Where it fires, the unconditional intervals
    # (Tango, exact) are the ones to quote, and the report says so at the number.
    one_signed = (b == 0) != (c == 0)
    out = {
        "b": b, "c": c, "n_discordant": b + c, "n": n, "delta": delta,
        "n_clusters": len(values_by_cluster),
        "one_signed_discordance": one_signed,
        "one_signed_note": (
            "every discordant pair points the same way, so the percentile bootstrap "
            "cannot generate a resample of the opposite sign: its bound at zero is an "
            "artefact of the method, not evidence of exclusion. Quote the Tango or exact "
            "unconditional interval here." if one_signed else ""),
        "ci95": list(cluster_bootstrap_ci(values_by_cluster, reps, seed)),
        "ci95_method": ("percentile bootstrap over problem clusters, "
                        f"{reps} resamples, seed {seed} — PRIMARY"),
        "tango_ci95": list(tango_score_interval(b, c, n)) if n else None,
        "p_exact": mcnemar_exact(b, c),
        "p_signflip_cluster": signflip_p(values_by_cluster),
        "withdrawn_conditional_ci95": (
            [(b + c) * (2 * clopper_pearson(b, b + c)[0] - 1) / n,
             (b + c) * (2 * clopper_pearson(b, b + c)[1] - 1) / n] if (b + c) and n else None),
        "withdrawn_conditional_note":
            "published in the first version of this report; withdrawn — it rescales a "
            "conditional interval by the observed discordance fraction and so discards "
            "the uncertainty in that fraction. Measured coverage 0.416 where 0.95 was "
            "claimed. Retained for comparison only.",
    }
    if exact_unconditional and n:
        out["exact_unconditional_ci95"] = list(exact_unconditional_interval(b, c, n))
    if b + c == 0:
        out["note"] = "0 of 0 discordant pairs; the difference is the count 0, not a rate"
    return out


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
        # Constrained least squares: the preregistration fixes A in [0, 1], because A is
        # a fraction of a population. The unconstrained ratio can leave that box on
        # degenerate curves (a curve that is 1.0 at every K returns A = 250), and
        # clipping only the point estimate afterwards left the two bootstrap paths
        # treating the boundary differently — the asymptote path clipped, the paired
        # difference path did not. The projection happens HERE, inside the objective, so
        # every path sees the same constrained fit.
        A = min(1.0, max(0.0, A))
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
            fitted.append(fit["A"])      # already in [0, 1]: the fit is constrained
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


def mixed_instance_values(draws, families, ids, per_family) -> dict | None:
    """Per-instance probability that a matched mixed subset flags it — the quantity
    ``mixed_curve`` averages, exposed so it can be bootstrapped over problem clusters."""
    ks_avail = {f: sorted(d for d in draws[f] if isinstance(d, int)) for f in families}
    if any(len(ks_avail[f]) < per_family for f in families):
        return None
    out = {}
    for i in ids:
        miss = 1.0
        for f in families:
            total = len(ks_avail[f])
            hits = sum(1 for d in ks_avail[f] if draws[f][d].get(i))
            miss *= (math.comb(total - hits, per_family) / math.comb(total, per_family)
                     if total - hits >= per_family else 0.0)
        out[i] = 1.0 - miss
    return out


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


def clustered_mean(values: dict, ids: list[str], instances: dict, reps: int,
                   seed: int) -> dict:
    """The mean of a per-instance quantity, with a problem-cluster bootstrap interval.

    Used where the quantity is not an indicator — notably the K = 1 point of a union
    curve, which is the **average over all K_max single draws** (per instance, k_i/K_max),
    not the rate of one nominated draw.
    """
    by_problem: dict[str, list[float]] = {}
    for i in ids:
        by_problem.setdefault(instances[i]["problem_id"], []).append(float(values[i]))
    flat = [v for vs in by_problem.values() for v in vs]
    lo, hi = cluster_bootstrap_ci(by_problem, reps, seed)
    return {"n": len(ids), "n_problems": len(by_problem),
            "rate": (sum(flat) / len(flat)) if flat else 0.0,
            "cluster_ci95": [lo, hi]}


def clustered_rate(flags: dict, ids: list[str], instances: dict, reps: int,
                   seed: int) -> dict:
    """A rate with BOTH intervals: Wilson (instances independent) and the problem
    cluster bootstrap (the honest one where problems repeat across batches)."""
    by_problem: dict[str, list[int]] = {}
    for i in ids:
        by_problem.setdefault(instances[i]["problem_id"], []).append(int(bool(flags.get(i))))
    k = sum(1 for i in ids if flags.get(i))
    lo, hi = cluster_bootstrap_ci(by_problem, reps, seed)
    return {"k": k, "n": len(ids), "n_problems": len(by_problem),
            "rate": k / len(ids) if ids else 0.0,
            "wilson95": list(wilson(k, len(ids))),
            "cluster_ci95": [lo, hi],
            "note": "cluster_ci95 is the primary interval; Wilson assumes instances are "
                    "independent and they are not where a problem supplies two"}


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
            union_flags = {i: any(draws[family][d].get(i) for d in complete) for i in ids}
            entry[label] = {
                "n_instances": len(ids),
                "n_problems": len({instances[i]["problem_id"] for i in ids}),
                "union_at_kmax_block": clustered_rate(union_flags, ids, instances,
                                                      BOOTSTRAP, BOOT_SEED),
                # The K = 1 point of the curve is the mean single-draw rate over ALL
                # K_max draws, so its per-instance value is k_i/K_max — not draw 1's
                # indicator, which would be a different quantity with a different mean.
                # An interval at every K, not only the endpoints: the per-instance
                # quantity at K is the probability a random K-subset flags it, which is
                # exactly what union_curve averages.
                "curve_ci95": [
                    clustered_mean(
                        {i: 1.0 - (math.comb(len(complete) - sum(
                            1 for d in complete if draws[family][d].get(i)), K)
                            / math.comb(len(complete), K)
                            if len(complete) - sum(1 for d in complete
                                                   if draws[family][d].get(i)) >= K
                            else 0.0) for i in ids},
                        ids, instances, BOOTSTRAP, BOOT_SEED + 20 + K)["cluster_ci95"]
                    for K in range(1, len(complete) + 1)],
                "draw1_block": clustered_mean(
                    {i: sum(1 for d in complete if draws[family][d].get(i)) / len(complete)
                     for i in ids}, ids, instances, BOOTSTRAP, BOOT_SEED + 3),
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
                vals = mixed_instance_values(draws, list(combo), ids, per)
                if vals is not None:
                    entry[f"{label}_ci95"] = clustered_mean(
                        vals, ids, instances, BOOTSTRAP,
                        BOOT_SEED + 30 + per)["cluster_ci95"]
                # the same total K spent inside one family, for the comparison that matters
                for f in combo:
                    if out["families"][f]["k_max"] >= total:
                        ks = counts_per_instance(draws[f], ids)
                        kmax_f = out["families"][f]["k_max"]
                        entry[f"{label}_{f}_alone_at_{total}"] = union_curve(
                            ks, kmax_f)[total - 1]
                        # the same comparator, with the same cluster interval as
                        # everything else it is being compared against
                        entry[f"{label}_{f}_alone_at_{total}_ci95"] = clustered_mean(
                            {i: 1.0 - (math.comb(kmax_f - k, total) /
                                       math.comb(kmax_f, total)
                                       if kmax_f - k >= total else 0.0)
                             for i, k in zip(ids, ks)},
                            ids, instances, BOOTSTRAP,
                            BOOT_SEED + 50 + total)["cluster_ci95"]
            rows[str(total)] = entry
        mixed["+".join(combo)] = rows
    out["mixed"] = mixed

    # the residual: stratum-P instances no draw of any family ever flagged
    residual: dict = {}
    all_families = [f for f in FAMILIES if out["families"].get(f, {}).get("k_max")]
    for label, subset in (("broker_families_only", [f for f in all_families if f != "astra"]),
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
        never_flags = {i: (i in set(never)) for i in ids}
        residual[label] = {
            "families": subset,
            "total_draws": sum(out["families"][f]["k_max"] for f in subset),
            "n_P": len(ids), "n_never_flagged": len(never),
            "n_problems": len({instances[i]["problem_id"] for i in ids}),
            "share": len(never) / len(ids) if ids else None,
            "share_wilson95": list(wilson(len(never), len(ids))),
            "share_block": clustered_rate(never_flags, ids, instances, BOOTSTRAP,
                                          BOOT_SEED + 4),
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
            ids = r["instance_ids"]
            # The residual's own problems repeat across batches too, so a category share
            # gets the same cluster bootstrap as every other rate in this report.
            cluster = {}
            for cat in counts:
                flags = {i: ((table.get("classification", {}).get(i) or {}).get("category")
                             == cat) for i in ids}
                cluster[cat] = clustered_rate(flags, ids, instances, BOOTSTRAP,
                                              BOOT_SEED + 11)["cluster_ci95"]
            by_pop[label] = {
                "n": r["n_never_flagged"], "counts": counts,
                "n_problems": len({instances[i]["problem_id"] for i in ids}),
                "shares": {k: v / r["n_never_flagged"] for k, v in counts.items()}
                if r["n_never_flagged"] else {},
                "wilson95": {k: list(wilson(v, r["n_never_flagged"]))
                             for k, v in counts.items()},
                "cluster_ci95": cluster,
                "unclassified": missing,
                "rule_version": table.get("rule_version", "AUTHOR_INPUT_NEEDED"),
            }
        out["residual_classified"] = by_pop
    else:
        out["residual_classified"] = {
            "status": "AUTHOR_INPUT_NEEDED: records/ceiling/residual_classification.json "
                      "has not been written yet"}
    return out


def timeout_sensitivity(instances: dict, audit_set: list[str], run_dir: Path,
                        reps: int = None) -> dict:
    """Stratum P without the timeouts, as a sensitivity analysis.

    The preregistered population is "passes every visible test, fails a hidden one".
    Seven of the 110 P instances fail because the hidden suite **did not terminate**, not
    because an assertion was observed to fail. `CORRECTIONS.md` item 4 records exactly
    this for the code study and it is not fixed by ignoring it: the registered analysis
    keeps the registered population, and this table shows what changes if the population
    is narrowed to instances with an **observed assertion failure**.

    The timeout flags come from study 2's committed scoring records, re-verified on this
    machine by `baseline_reproduction.json`; no model and no new execution is involved.
    """
    scored: dict[str, dict] = {}
    for batch in ("b1", "b2"):
        path = run_dir / f"study2-inputs/scored-{batch}.jsonl"
        if not path.exists():
            return {"status": f"AUTHOR_INPUT_NEEDED: {path} not available; the timeout "
                              "sensitivity cannot be recomputed without the archived "
                              "scoring records"}
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                scored[f"{batch}:{row['problem_id']}"] = row
    P = [i for i in audit_set if instances[i]["stratum"] == "P"]
    timeouts = sorted(i for i in P if scored[i]["hidden"].get("timed_out"))
    keep = [i for i in P if i not in set(timeouts)]
    scope = set(i for i in audit_set if instances[i]["stratum"] in ("P", "C"))
    draws = load_draws(scope)
    out = {
        "definition": "stratum P restricted to instances with an OBSERVED assertion "
                      "failure; the preregistered population is every hidden-suite "
                      "non-pass, which includes timeouts",
        "n_P_registered": len(P), "n_P_assertion_only": len(keep),
        "timeout_instances": timeouts, "n_timeouts": len(timeouts),
        "families": {},
    }
    for family in FAMILIES:
        complete = sorted(d for d in draws[family] if isinstance(d, int))
        if not complete:
            continue
        union_reg = sum(1 for i in P if any(draws[family][d].get(i) for d in complete))
        union_sub = sum(1 for i in keep if any(draws[family][d].get(i) for d in complete))
        flags_sub = {i: any(draws[family][d].get(i) for d in complete) for i in keep}
        flags_reg = {i: any(draws[family][d].get(i) for d in complete) for i in P}
        out["families"][family] = {
            "k_max": len(complete),
            "union_registered": clustered_rate(flags_reg, P, instances,
                                               reps or BOOTSTRAP, BOOT_SEED + 14),
            "union_assertion_only": clustered_rate(flags_sub, keep, instances,
                                                   reps or BOOTSTRAP, BOOT_SEED + 12),
        }
    all_fams = [f for f in FAMILIES if any(isinstance(d, int) for d in draws[f])]
    never_reg = [i for i in P if not any(draws[f][d].get(i)
                                         for f in all_fams for d in draws[f]
                                         if isinstance(d, int))]
    never_sub = [i for i in keep if i in set(never_reg)]
    out["residual_registered"] = clustered_rate(
        {i: (i in set(never_reg)) for i in P}, P, instances,
        reps or BOOTSTRAP, BOOT_SEED + 15)
    out["residual_assertion_only"] = clustered_rate(
        {i: (i in set(never_reg)) for i in keep}, keep, instances,
        reps or BOOTSTRAP, BOOT_SEED + 13)
    out["timeouts_in_residual"] = sorted(set(never_reg) & set(timeouts))
    return out


def power_curve(n: int, p_c: float, alpha: float = 0.05,
                deltas=(0.02, 0.05, 0.075, 0.10, 0.125, 0.15, 0.20)) -> dict:
    """Exact power of the two-sided exact McNemar test at this study's n.

    Model, stated because a power figure without its model is meaningless: the pair
    outcomes are multinomial over (improved, worsened, unchanged) with the worsening rate
    held at ``p_c`` — the value actually observed in the primary arm — and the improving
    rate set to ``p_c + delta``. Power is summed exactly over the joint distribution of
    (b, c); no simulation and no normal approximation.

    This says what the study could and could not have detected. It is computed after the
    fact and is descriptive: it is NOT a retrospective power calculation conditioned on
    the observed effect, which would be uninformative.
    """
    logfac = [0.0] * (n + 1)
    for i in range(1, n + 1):
        logfac[i] = logfac[i - 1] + math.log(i)
    out = {}
    for delta in deltas:
        p_b = p_c + delta
        if p_b + p_c >= 1:
            continue
        rest = 1 - p_b - p_c
        total = 0.0
        for b in range(n + 1):
            for c in range(n + 1 - b):
                if mcnemar_exact(b, c) > alpha:
                    continue
                lp = (logfac[n] - logfac[b] - logfac[c] - logfac[n - b - c]
                      + (b * math.log(p_b) if b else 0.0)
                      + (c * math.log(p_c) if c else 0.0)
                      + ((n - b - c) * math.log(rest) if (n - b - c) else 0.0))
                if lp > -60:
                    total += math.exp(lp)
        out[f"{delta:.3f}"] = total
    return {"n": n, "p_c_assumed": p_c, "alpha": alpha,
            "test": "two-sided exact McNemar",
            "power_by_true_difference": out,
            "note": "the improving rate is p_c + delta; the worsening rate is held at the "
                    "value observed in the primary arm. Descriptive, computed after the "
                    "fact, and not conditioned on the observed effect."}


#: Every comparison this study computed, reconciled against the plan. The correction
#: family is "every contrast reported with a p value", and the threshold is stated once.
COMPARISON_INVENTORY = {
    "policy": "One correction family: every contrast this study reports a p value for. "
              "The two primary outcomes (A(self) - A(cross); self-loop net) were each "
              "declared singly in the preregistration before any model call and are NOT "
              "corrected. Every other contrast carries its unadjusted p AND the "
              "Bonferroni threshold over the family size below. A contrast that was not "
              "in the preregistered list of twelve is labelled EXPLORATORY at every "
              "occurrence, whatever its p.",
    "planned_twelve": [
        "A(self) - A(cross)  [PRIMARY, ceiling 1]",
        "A(mixed) - A(cross) at K = 8",
        "A(mixed) - A(self) at K = 8",
        "self-loop net vs 0  [PRIMARY, ceiling 2]",
        "cross-loop net vs 0",
        "referent-loop net vs 0",
        "self-loop - cross-loop net",
        "referent-loop - cross-loop net",
        "self-loop vs self-loop-rep (the floor, not a test)",
        "A(astra) - A(cross)",
        "A(astra) - A(self)",
        "A(mixed-with-astra) - A(mixed-without)",
    ],
    "planned_not_delivered_as_specified": [
        "The five mixed/astra asymptote contrasts (items 2, 3, 10, 11, 12) are NOT "
        "delivered as fitted contrasts with intervals. Table 4 reports raw mixed-union "
        "rates at matched total draws instead. That is a deviation (deviation 15), not a "
        "result: the mixed families' asymptote contrasts are UNMEASURED in this study.",
    ],
    "performed_with_a_p_value": [
        "self-loop net vs 0  [PRIMARY]",
        "self-loop-rep net vs 0  [replicate, not a hypothesis test]",
        "cross-loop net vs 0",
        "referent-loop net vs 0",
        "self-loop - cross-loop, final outcome",
        "referent-loop - cross-loop, final outcome",
        "self-loop - self-loop-rep, final outcome  [replicate]",
        "self-loop - cross-loop flags: P, C, pooled  [pooled is EXPLORATORY]",
        "referent-loop - cross-loop flags: P, C, pooled  [pooled is EXPLORATORY]",
        "self-loop - self-loop-rep flags: P, C, pooled  [replicate]",
    ],
    "family_size_for_correction": 16,
    "bonferroni_threshold": 0.05 / 16,
    "exploratory_not_in_the_plan": [
        "every flag contrast (P, C and pooled) — the plan named outcome contrasts, not "
        "flag contrasts, so all nine are EXPLORATORY even though the P-stratum one is "
        "the study's largest effect",
        "the conditional-on-revision net for each arm",
        "the mixed-family union rates in Table 4",
        "the timeout sensitivity analysis",
        "the residual's oracle-disputability flag",
    ],
}


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
        by_problem: dict[str, list[int]] = {}
        for r in rows:
            by_problem.setdefault(r["problem_id"], []).append(
                int(r["hidden_passed_after"]) - int(r["hidden_passed_before"]))
        flagP = {r["instance_id"]: bool(r.get("flagged")) for r in P}
        flagC = {r["instance_id"]: bool(r.get("flagged")) for r in C}
        entry = {
            "n_instances": n, "n_P": len(P), "n_C": len(C),
            "n_problems": len(by_problem),
            "flag_rate_P": clustered_rate(flagP, [r["instance_id"] for r in P],
                                          instances, BOOTSTRAP, BOOT_SEED + 5),
            "flag_rate_C": clustered_rate(flagC, [r["instance_id"] for r in C],
                                          instances, BOOTSTRAP, BOOT_SEED + 6),
            "blocked_P": sum(1 for r in P if r.get("verdict") == "BLOCKED"),
            "blocked_C": sum(1 for r in C if r.get("verdict") == "BLOCKED"),
            "n_revised": len(revised), "n_changed": len(changed),
            "n_returned_non_solution": sum(1 for r in rows if r.get("returned_non_solution")),
            "fixed_on_P": clustered_rate(
                {r["instance_id"]: (not r["hidden_passed_before"] and r["hidden_passed_after"])
                 for r in P}, [r["instance_id"] for r in P], instances,
                BOOTSTRAP, BOOT_SEED + 8),
            "broken_on_C": clustered_rate(
                {r["instance_id"]: (r["hidden_passed_before"] and not r["hidden_passed_after"])
                 for r in C}, [r["instance_id"] for r in C], instances,
                BOOTSTRAP, BOOT_SEED + 9),
            "net_primary": paired_difference(by_problem,
                                             exact_unconditional=EXACT_UNCONDITIONAL),
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
        out["arms"][arm] = entry

    # paired arm-vs-arm on the after-revision outcome, exact McNemar
    for a, b in (("self-loop", "cross-loop"), ("referent-loop", "cross-loop"),
                 ("self-loop", "self-loop-rep")):
        if a not in arm_rows or b not in arm_rows:
            continue
        shared = sorted(set(arm_rows[a]) & set(arm_rows[b]))
        clusters: dict[str, list[int]] = {}
        for i in shared:
            clusters.setdefault(arm_rows[a][i]["problem_id"], []).append(
                int(arm_rows[a][i]["hidden_passed_after"])
                - int(arm_rows[b][i]["hidden_passed_after"]))
        entry = paired_difference(clusters, exact_unconditional=EXACT_UNCONDITIONAL)
        entry["arms"] = [a, b]
        entry["label"] = f"{a} minus {b}, hidden-test pass after one round"
        # The flag rate is the mechanism behind any net effect, so it is shown paired and
        # split by stratum: on P a flag is a defect caught, on C it is a false alarm, and
        # a single pooled discordance would hide which of the two moved.
        entry["flag_discordance"] = {}
        for stratum in ("P", "C", "all"):
            ids = [i for i in shared
                   if stratum == "all" or arm_rows[a][i]["stratum"] == stratum]
            fc: dict[str, list[int]] = {}
            for i in ids:
                fc.setdefault(arm_rows[a][i]["problem_id"], []).append(
                    int(bool(arm_rows[a][i].get("flagged")))
                    - int(bool(arm_rows[b][i].get("flagged"))))
            block = paired_difference(fc, exact_unconditional=EXACT_UNCONDITIONAL)
            block.update({
                "flagged_" + a: sum(1 for i in ids if arm_rows[a][i].get("flagged")),
                "flagged_" + b: sum(1 for i in ids if arm_rows[b][i].get("flagged")),
                "only_" + a: block["b"], "only_" + b: block["c"],
                "difference": block["delta"]})
            entry["flag_discordance"][stratum] = block
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
    lines.append("Every rate carries a 95% **problem-cluster bootstrap** interval; the "
                 "P population is 110 instances from only **56 problems**, so an interval "
                 "that treats instances as independent is too narrow. `flat?` says "
                 "whether the curve met the preregistered flattening bar (last-step gain "
                 "≤ 1.0 point); where it did not, **A is an extrapolation** and the raw "
                 "union at K_max is the number to quote.\n")
    lines.append("| family | K_max | union recall on P at K=1 [95% CI] | at K_max "
                 "[95% CI] | fitted asymptote A [95% CI] | union FP on C at K=1 [95% CI] "
                 "| at K_max [95% CI] | last-step gain | flat? |")
    lines.append("|---|---:|---|---|---|---|---|---:|:---:|")
    for family in FAMILIES:
        f = c1["families"].get(family, {})
        if not f.get("k_max"):
            lines.append(f"| `{family}` | — | — | — | not run | — | — | — | — |")
            continue
        P, C = f["P"], f["C"]
        flat = "yes" if not P["asymptote_is_extrapolation"] else "**no**"
        A = (f"**{pct(P['fit']['A'])}** {ci(P['fit_A_ci95'])}"
             if not P["asymptote_is_extrapolation"]
             else f"{pct(P['fit']['A'])} {ci(P['fit_A_ci95'])} *(extrapolation)*")
        lines.append(
            f"| `{family}` | {f['k_max']} | "
            f"{pct(P['draw1_block']['rate'])} {ci(P['draw1_block']['cluster_ci95'])} | "
            f"**{pct(P['union_at_kmax'])}** ({P['union_at_kmax_count']}/{P['n_instances']}) "
            f"{ci(P['union_at_kmax_block']['cluster_ci95'])} | {A} | "
            f"{pct(C['draw1_block']['rate'])} {ci(C['draw1_block']['cluster_ci95'])} | "
            f"**{pct(C['union_at_kmax'])}** "
            f"{ci(C['union_at_kmax_block']['cluster_ci95'])} | "
            f"{pct(P['marginal_gain_last_step'], 2)} | {flat} |")
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
        lines.append("| K | union recall on P [95% cluster CI] | union FP on C "
                     "[95% cluster CI] | recall per FP point |")
        lines.append("|---:|---|---|---:|")
        for index, (r, fp) in enumerate(zip(f["P"]["curve"], f["C"]["curve"]), start=1):
            ratio = ((r - f["P"]["curve"][0]) / (fp - f["C"]["curve"][0])
                     if index > 1 and fp > f["C"]["curve"][0] else None)
            rci = f["P"]["curve_ci95"][index - 1]
            fci = f["C"]["curve_ci95"][index - 1]
            lines.append(f"| {index} | {pct(r)} {ci(rci)} | {pct(fp)} {ci(fci)} | "
                         f"{'—' if ratio is None else f'{ratio:.2f}'} |")
    if "primary_ceiling1" in c1:
        lines.append("\n### Table 3 — primary outcome, ceiling 1: A(self) − A(cross)\n")
        lines.append(f"K_common = {c1['k_common']} draws per family. Positive means the "
                     "generator's own model can ultimately see more of its own defects "
                     "than a stranger can. Interval: 95% percentile bootstrap over "
                     "problem clusters, both curves resampled together.\n")
        lines.append("| stratum | n instances | A(cross) [95% CI] | A(self) [95% CI] | "
                     "A(self) − A(cross) [95% CI] | raw union difference at K_common "
                     "[95% CI] |")
        lines.append("|---|---:|---|---|---|---|")
        for label in ("P", "C"):
            d = c1["primary_ceiling1"][label]
            fc = c1["families"]["cross"][label]["fit_A_ci95"]
            fs = c1["families"]["self"][label]["fit_A_ci95"]
            lines.append(
                f"| {label} | {d['n_instances']} | {pct(d['A_cross'])} {ci(fc)} | "
                f"{pct(d['A_self'])} {ci(fs)} | **{pct(d['A_self_minus_cross'])}** "
                f"{ci(d['ci95'])} | {pct(d['raw_union_diff_at_k_common'])} "
                f"{ci(d['raw_diff_ci95'])} |")
    if c1.get("mixed"):
        lines.append("\n### Table 4 — mixed families at matched total draws\n")
        lines.append("Unit of analysis: the instance. Each row spends the same total "
                     "number of readings; the question is whether spreading them across "
                     "families beats spending them all inside one.\n")
        lines.append("| combination | total draws | per family | union recall on P "
                     "[95% cluster CI] | union FP on C [95% cluster CI] | same total "
                     "inside one family (recall) |")
        lines.append("|---|---:|---:|---|---|---|")
        for combo, rows in c1["mixed"].items():
            for total, row in sorted(rows.items(), key=lambda kv: int(kv[0])):
                alone = "; ".join(
                    f"`{f}` {pct(row[k])} {ci(row.get(k + '_ci95'))}" for f in FAMILIES
                    for k in [f"P_{f}_alone_at_{total}"] if k in row)
                lines.append(f"| `{combo}` | {total} | {row['per_family']} | "
                             f"{pct(row['P'])} {ci(row.get('P_ci95'))} | "
                             f"{pct(row['C'])} {ci(row.get('C_ci95'))} | {alone or '—'} |")
    if c1.get("residual"):
        lines.append("\n### Table 5 — the residual: stratum-P defects no draw ever flagged\n")
        lines.append("| population | families | total draws | n P instances "
                     "(problems) | never flagged | share [95% cluster CI] | "
                     "[95% Wilson, too narrow] |")
        lines.append("|---|---|---:|---:|---:|---|---|")
        for label, r in c1["residual"].items():
            lines.append(f"| {label} | {', '.join(r['families'])} | {r['total_draws']} | "
                         f"{r['n_P']} ({r.get('n_problems', '?')}) | "
                         f"**{r['n_never_flagged']}** | "
                         f"**{pct(r['share'])}** {ci(r['share_block']['cluster_ci95'])} | "
                         f"{ci(r['share_wilson95'])} |")

    rcl = c1.get("residual_classified") or {}
    if rcl and "status" not in rcl:
        lines.append("\n### Table 5b — what the residual defects are\n")
        lines.append("Categories and their order were fixed in the preregistration "
                     "(§1.5) before the first residual instance was read; each instance "
                     "takes the first category that applies. Unit: the instance; the "
                     "primary interval is the problem-cluster bootstrap, with Wilson "
                     "shown beside it for comparison only.\n")
        lines.append("| population | n residual (problems) | category | count | share "
                     "[95% cluster CI] | [95% Wilson, too narrow] |")
        lines.append("|---|---:|---|---:|---|---|")
        for label, r in rcl.items():
            for cat, count in sorted(r["counts"].items(), key=lambda kv: -kv[1]):
                # A count small enough that its interval reaches an absurd bound is quoted
                # AS THE COUNT (EXPERIMENT_RECORD.md §9), not as a percentage.
                share = (f"**{count} of {r['n']}** — quoted as a count, not a rate"
                         if count < 6 else
                         f"**{pct(r['shares'][cat])}** {ci(r['cluster_ci95'][cat])}")
                wilson = "—" if count < 6 else ci(r["wilson95"][cat])
                lines.append(f"| {label} | {r['n']} ({r.get('n_problems','?')}) | "
                             f"`{cat}` | {count} | {share} | {wilson} |")
            if r["unclassified"]:
                lines.append(f"| {label} | {r['n']} | **unclassified** | "
                             f"{len(r['unclassified'])} | AUTHOR_INPUT_NEEDED |")

    c2 = numbers["ceiling2"]
    lines.append("\n### Table 6 — ceiling 2: the closed loop, per arm\n")
    lines.append("Unit of analysis: the instance, paired before/after on the same "
                 "instance; the resampling unit is the problem. Net is unconditional on "
                 "whether a revision occurred.\n")
    lines.append("The primary interval is the **problem-cluster bootstrap**; Tango's "
                 "unconditional score interval and the exact unconditional interval "
                 "(Berger-Boos restricted) are checks that ignore clustering. `p` is "
                 "exact McNemar (instances independent); `p_clu` is a cluster-level "
                 "sign-flip permutation test beside it. 112 instances come from **96 "
                 "problems**.\n")
    lines.append("A rate of **0/56** carries a bootstrap interval of [0.0, 0.0] for the "
                 "same reason: with no positive instance to resample, the bootstrap "
                 "cannot move. Read it as the count **0 of 56**, and its Wilson bound "
                 "[0.0, 6.4] for a rate.\n")
    lines.append("**†** — every discordant pair points the same way, so the percentile "
                 "bootstrap cannot produce a resample of the opposite sign and its bound "
                 "at zero is an artefact of the method. Read the Tango or exact "
                 "unconditional interval on that row. This is `CORRECTIONS.md` item 4 "
                 "applying to the replacement as it applied to what it replaced.\n")
    lines.append("| arm | n (problems) | BLOCKED (P / C) | changed | fixed on P | "
                 "broken on C | **net change** [95% cluster CI] | Tango CI | exact-unc. "
                 "CI | p | p_clu |")
    lines.append("|---|---:|---:|---:|---|---|---|---|---|---:|---:|")
    for arm in LOOP_ARMS:
        a = c2["arms"].get(arm, {})
        if "n_instances" not in a:
            lines.append(f"| `{arm}` | — | — | — | — | — | not run | — | — | — | — |")
            continue
        net = a["net_primary"]
        eu = ci(net.get("exact_unconditional_ci95"), 2) if net.get(
            "exact_unconditional_ci95") else "—"
        lines.append(
            f"| `{arm}` | {a['n_instances']} ({a['n_problems']}) | "
            f"{a['blocked_P']} / {a['blocked_C']} | {a['n_changed']} | "
            f"{a['fixed_on_P']['k']}/{a['fixed_on_P']['n']} "
            f"{ci(a['fixed_on_P']['cluster_ci95'])} | {a['broken_on_C']['k']}/"
            f"{a['broken_on_C']['n']} {ci(a['broken_on_C']['cluster_ci95'])} | "
            f"**{net['delta'] * 100:+.2f} pp** {ci(net['ci95'], 2)}"
            f"{' †' if net.get('one_signed_discordance') else ''} "
            f"(b={net['b']}, c={net['c']}) | {ci(net['tango_ci95'], 2)} | {eu} | "
            f"{net['p_exact']:.4f} | {net['p_signflip_cluster']['p']:.4f} |")
    if c2.get("contrasts"):
        lines.append("\n### Table 7 — paired contrasts between arms\n")
        lines.append("Outcome: whether the instance passes the hidden suite after one "
                     "round. Unit: the instance, paired across arms; resampled by "
                     "problem. Both discordant counts shown.\n")
        lines.append("| contrast | n (problems) | discordant (b / c) | difference "
                     "[95% cluster CI] | Tango CI | p | p_clu |")
        lines.append("|---|---:|---:|---|---|---:|---:|")
        for key, d in c2["contrasts"].items():
            lines.append(f"| {d['label']} | {d['n']} ({d['n_clusters']}) | "
                         f"{d['b']} / {d['c']} | "
                         f"{d['delta'] * 100:+.2f} pp {ci(d['ci95'], 2)}"
                         f"{' †' if d.get('one_signed_discordance') else ''} | "
                         f"{ci(d['tango_ci95'], 2)} | {d['p_exact']:.4f} | "
                         f"{d['p_signflip_cluster']['p']:.4f} |")
        lines.append("\n### Table 7b — what the arms flag, paired and split by stratum\n")
        lines.append("The mechanism behind any net effect. On stratum P a flag is a "
                     "defect caught; on stratum C it is a false alarm. Unit: the "
                     "instance, paired across arms; resampled by problem.\n")
        lines.append("**Every row here is EXPLORATORY**: the preregistered twelve named "
                     "outcome contrasts, not flag contrasts. They are reported because "
                     "the mechanism matters, and they are labelled at every occurrence.\n")
        lines.append("| contrast | stratum | n (problems) | flagged by each | discordant "
                     "(b / c) | difference [95% cluster CI] | Tango CI | p | p_clu |")
        lines.append("|---|---|---:|---|---:|---|---|---:|---:|")
        for key, d in c2["contrasts"].items():
            a, b = d["arms"]
            for stratum in ("P", "C"):
                f = d["flag_discordance"][stratum]
                lines.append(
                    f"| `{a}` vs `{b}` | {stratum} | {f['n']} ({f['n_clusters']}) | "
                    f"{f['flagged_' + a]} vs {f['flagged_' + b]} | "
                    f"{f['only_' + a]} / {f['only_' + b]} | "
                    f"{f['difference'] * 100:+.2f} pp {ci(f['ci95'], 2)}"
                    f"{' †' if f.get('one_signed_discordance') else ''} | "
                    f"{ci(f['tango_ci95'], 2)} | "
                    f"{f['p_exact']:.4f} | {f['p_signflip_cluster']['p']:.4f} |")
    ts = numbers.get("timeout_sensitivity", {})
    if ts and "families" in ts:
        lines.append("\n### Table 9 — sensitivity: stratum P without the timeouts\n")
        lines.append(f"The registered population is every hidden-suite non-pass, which "
                     f"**includes {ts['n_timeouts']} instances whose suite did not "
                     f"terminate**. This table narrows it to instances with an observed "
                     f"assertion failure. The registered analysis is unchanged; this is "
                     f"a sensitivity check, and it is EXPLORATORY.\n")
        lines.append(f"| family | union recall, registered P "
                     f"(n = {ts['n_P_registered']}) [95% cluster CI] | "
                     f"union recall, assertion-failure P only "
                     f"(n = {ts['n_P_assertion_only']}) [95% cluster CI] | "
                     f"[95% Wilson, too narrow] |")
        lines.append("|---|---|---|---|")
        for fam, v in ts["families"].items():
            u, s = v["union_registered"], v["union_assertion_only"]
            lines.append(f"| `{fam}` (K = {v['k_max']}) | {u['k']}/{u['n']} "
                         f"({100*u['rate']:.1f}%) {ci(u['cluster_ci95'])} | "
                         f"**{s['k']}/{s['n']}** ({100*s['rate']:.1f}%) "
                         f"{ci(s['cluster_ci95'])} | {ci(s['wilson95'])} |")
        rr, rs = ts["residual_registered"], ts["residual_assertion_only"]
        lines.append(f"| **residual (never flagged)** | {rr['k']}/{rr['n']} "
                     f"({100*rr['rate']:.1f}%) {ci(rr['cluster_ci95'])} | "
                     f"**{rs['k']}/{rs['n']}** ({100*rs['rate']:.1f}%) "
                     f"{ci(rs['cluster_ci95'])} | {ci(rs['wilson95'])} |")
        lines.append(f"\nThe {len(ts['timeouts_in_residual'])} timeouts that sit inside "
                     f"the residual are `{'`, `'.join(ts['timeouts_in_residual'])}`.")

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
    global BOOTSTRAP, EXACT_UNCONDITIONAL
    parser.add_argument("--bootstrap", type=int, default=BOOTSTRAP)
    parser.add_argument("--no-exact-unconditional", action="store_true",
                        help="skip the exact unconditional check interval (the one "
                             "expensive estimator); the primary bootstrap is unaffected")
    parser.add_argument("--run", default=str(Path.home() / "Documents/Crossaudit/"
                                             "study-data/wt-ceiling-runs"),
                        help="archived run dir, read only for the timeout sensitivity")
    args = parser.parse_args(argv)
    BOOTSTRAP = args.bootstrap
    EXACT_UNCONDITIONAL = not args.no_exact_unconditional

    instances = load_instances()
    audit_set = load_audit_set()
    numbers = {
        "study": "ceiling (study 8)",
        "preregistration": "benchmarks/code/ceiling/PREREGISTRATION.md",
        "bootstrap_reps": BOOTSTRAP, "bootstrap_seed": BOOT_SEED,
        "ceiling1": analyse_ceiling1(instances, audit_set),
        "ceiling2": analyse_ceiling2(instances),
        "timeout_sensitivity": timeout_sensitivity(instances, audit_set, Path(args.run)),
        "power": power_curve(112, 2 / 112),
        "comparison_inventory": COMPARISON_INVENTORY,
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
