"""Study 8's estimators, checked against brute force and against published values.

Every inferential quantity in ``RESULTS-CEILING.md`` comes out of ``report_ceiling.py``,
which implements its own regularised incomplete beta, Clopper-Pearson inversion, exact
McNemar tail, saturation fit and beta-binomial likelihood rather than depending on SciPy.
That is a reproducibility decision — a reader can read the whole of it in one file — and it
puts the burden of proof here. These tests are the proof.

    python -m pytest benchmarks/code/tests/test_ceiling_stats.py
"""

from __future__ import annotations

import itertools
import math
import random
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import report_ceiling as rc  # noqa: E402


def test_union_curve_matches_brute_force_subset_enumeration():
    """The closed form must equal explicit averaging over every C(K_max, K) subset.

    The curve is the study's primary object, and it is computed by a combinatorial
    identity rather than by enumerating subsets. If the identity is wrong every number in
    ceiling 1 is wrong, so it is checked against the thing it replaces.
    """
    rng = random.Random(7)
    for _ in range(20):
        k_max, n = rng.randint(2, 6), rng.randint(3, 12)
        flags = [[rng.random() < 0.3 for _ in range(k_max)] for _ in range(n)]
        curve = rc.union_curve([sum(f) for f in flags], k_max)
        for K in range(1, k_max + 1):
            subsets = list(combinations(range(k_max), K))
            brute = sum(sum(1 for f in flags if any(f[d] for d in s))
                        for s in subsets) / (len(subsets) * n)
            assert abs(brute - curve[K - 1]) < 1e-12


def test_saturation_fit_recovers_a_known_curve():
    """Exact data must give back exactly the parameters that made it."""
    for A, tau in ((0.42, 1.7), (0.13, 0.6), (0.85, 4.0)):
        y = [A * (1 - math.exp(-K / tau)) for K in range(1, 9)]
        fit = rc.fit_saturation(y)
        assert abs(fit["A"] - A) < 1e-5
        assert abs(fit["tau"] - tau) < 1e-4
        assert fit["r2"] > 1 - 1e-9
        assert fit["max_resid"] < 1e-6


def test_saturation_fit_underestimates_under_heterogeneity():
    """The preregistered conservatism claim, checked rather than asserted.

    §1.2 justifies the single-exponential form partly on the ground that a mixture of
    detection probabilities makes it *under*estimate the asymptote — the safe direction
    for a ceiling. That is a claim about the estimator and it is testable.
    """
    k_max = 8
    # half the population is easy (p = 0.8), half is hard (p = 0.05); nothing is
    # undetectable, so the true asymptote is 1.0.
    ks = [round(0.8 * k_max)] * 50 + [round(0.05 * k_max)] * 50
    fit = rc.fit_saturation(rc.union_curve(ks, k_max))
    assert fit["A"] < 1.0


def test_clopper_pearson_satisfies_its_defining_property():
    """Checked against the definition, not against typed constants.

    A Clopper-Pearson bound is defined by the binomial tail it inverts: at the lower
    bound P(X >= k) = alpha/2, and at the upper bound P(X <= k) = alpha/2. Both tails are
    summed here directly from the binomial pmf, which is an implementation that shares no
    code with the continued-fraction beta the estimator uses.
    """
    def upper_tail(k, n, p):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))

    def lower_tail(k, n, p):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))

    for k, n in ((3, 5), (2, 56), (11, 13), (25, 56), (1, 110)):
        low, high = rc.clopper_pearson(k, n)
        assert abs(upper_tail(k, n, low) - 0.025) < 1e-9, (k, n, low)
        assert abs(lower_tail(k, n, high) - 0.025) < 1e-9, (k, n, high)
    # the degenerate ends are exact, not approximate
    assert rc.clopper_pearson(0, 10)[0] == 0.0
    assert rc.clopper_pearson(10, 10)[1] == 1.0
    assert abs(rc.clopper_pearson(0, 10)[1] - (1 - 0.025 ** (1 / 10))) < 1e-9


def test_exact_mcnemar_matches_the_binomial_sign_test():
    assert abs(rc.mcnemar_exact(5, 0) - 0.0625) < 1e-12
    assert abs(rc.mcnemar_exact(0, 0) - 1.0) < 1e-12
    assert abs(rc.mcnemar_exact(3, 2) - 1.0) < 1e-12
    # brute force against the binomial tail
    for b, c in ((16, 1), (11, 2), (9, 3), (7, 7)):
        n = b + c
        k = min(b, c)
        expect = min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)
        assert abs(rc.mcnemar_exact(b, c) - expect) < 1e-12


def test_paired_difference_intervals_are_ordered_and_contain_the_point():
    """Every interval a reader sees must be ordered and must contain its own estimate.

    An interval whose bounds are the wrong way round, or that excludes its own point
    estimate, survives every eyeball check because both numbers look plausible. It does
    not survive this — which is how the swapped beta tail was caught.
    """
    shapes = [
        {"p1": [1], "p2": [1], "p3": [1], "p4": [-1], "p5": [-1]},      # b=3, c=2
        {"p1": [1], "p2": [1], "p3": [1]},                               # b=3, c=0
        {f"p{i}": [0] for i in range(20)},                               # no discordance
        {"p1": [1, 1], "p2": [-1], "p3": [1], "p4": [0, 0]},             # clustered
    ]
    for clusters in shapes:
        d = rc.paired_difference(clusters, reps=400, seed=1)
        for key in ("ci95", "tango_ci95"):
            interval = d[key]
            if interval is None or interval[0] is None:
                continue
            lo, hi = interval
            assert lo <= hi, (key, d)
            assert lo - 1e-9 <= d["delta"] <= hi + 1e-9, (key, d)
        assert d["b"] + d["c"] == sum(1 for v in
                                      [x for vs in clusters.values() for x in vs] if v)
        if d["b"] + d["c"] == 0:
            assert "note" in d and d["p_exact"] == 1.0


def test_paired_difference_derives_its_counts_from_the_clusters():
    """No caller can hand in a discordance count that disagrees with the data."""
    d = rc.paired_difference({"a": [1, -1], "b": [1], "c": [0]}, reps=200, seed=2)
    assert (d["b"], d["c"], d["n"], d["n_clusters"]) == (2, 1, 4, 3)
    assert abs(d["delta"] - 0.25) < 1e-12


def test_zibb_recovers_a_planted_ceiling():
    """The secondary estimator must find a ceiling that is really there."""
    rng = random.Random(11)
    k_max = 8
    ks = []
    for _ in range(400):
        if rng.random() < 0.4:            # 40% findable, p ~ 0.5
            ks.append(sum(1 for _ in range(k_max) if rng.random() < 0.5))
        else:                              # 60% never findable
            ks.append(0)
    fit = rc.fit_zibb(ks, k_max)
    assert 0.3 < fit["pi"] < 0.55


def test_wilson_matches_an_independent_implementation():
    """A second, differently written Wilson, to catch a transcription slip in the first."""
    z = 1.959963984540054
    for k, n in ((11, 56), (0, 56), (31, 110), (14, 150), (80, 110)):
        p = k / n
        centre = (p + z * z / (2 * n)) / (1 + z * z / n)
        spread = (z / (1 + z * z / n)) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
        low, high = rc.wilson(k, n)
        assert abs(low - max(0.0, centre - spread)) < 1e-12
        assert abs(high - min(1.0, centre + spread)) < 1e-12


# ---------------------------------------------------------------------------------
# Coverage. The defect these exist to prevent from recurring silently.
# ---------------------------------------------------------------------------------

def _scenario_coverage(interval_fn, n=112, q=0.1, beneficial=True):
    """Exact coverage in the cross-vendor review's scenario, either direction.

    D ~ Binomial(n, q); every discordance points the same way. Beneficial means b = D,
    c = 0 and the true difference is +q; detrimental means b = 0, c = D and it is -q.
    Summed exactly over the binomial, not simulated.

    **Both directions are checked** because the first replacement covered 0.96 going one
    way and 0.075 going the other: it bounded the nuisance by (1 - |delta|)/2 instead of
    (1 - delta)/2, which is only correct for a non-negative difference.
    """
    truth = q if beneficial else -q
    covered = 0.0
    for D in range(n + 1):
        weight = math.comb(n, D) * q ** D * (1 - q) ** (n - D)
        if weight < 1e-15:
            continue
        b, c = (D, 0) if beneficial else (0, D)
        lo, hi = interval_fn(b, c, n)
        if lo is not None and lo <= truth <= hi:
            covered += weight
    return covered


def test_withdrawn_conditional_interval_undercovers_as_the_review_found():
    """The critical defect, pinned to the number an independent reviewer computed.

    The published interval took a Clopper-Pearson interval for the direction probability
    *conditional on discordance* and rescaled it by the *observed* discordance fraction
    D/n. That throws away the uncertainty in D. Its coverage in this scenario is 0.416,
    not the advertised 0.95, and this test exists so that the method cannot come back.
    """
    def withdrawn(b, c, n):
        nd = b + c
        if nd == 0:
            return (None, None)
        lo, hi = rc.clopper_pearson(b, nd)
        return (nd * (2 * lo - 1) / n, nd * (2 * hi - 1) / n)

    coverage = _scenario_coverage(withdrawn)
    assert abs(coverage - 0.4162688657) < 1e-9, coverage
    assert coverage < 0.5


def test_replacement_intervals_cover_in_BOTH_directions():
    """Coverage at the study's own n, going both ways, pinned to measured values."""
    tango = lambda b, c, n: rc.tango_score_interval(b, c, n)          # noqa: E731
    exact = lambda b, c, n: rc.exact_unconditional_interval(b, c, n)  # noqa: E731

    beneficial_tango = _scenario_coverage(tango)
    detrimental_tango = _scenario_coverage(tango, q=0.5, beneficial=False)
    assert abs(beneficial_tango - 0.9603704095) < 1e-6, beneficial_tango
    assert detrimental_tango >= 0.94, detrimental_tango

    beneficial_exact = _scenario_coverage(exact)
    detrimental_exact = _scenario_coverage(exact, q=0.5, beneficial=False)
    assert abs(beneficial_exact - 0.9968790922) < 1e-6, beneficial_exact
    # before the nuisance-bound fix this was 0.0752249063
    assert detrimental_exact >= 0.95, detrimental_exact
    # and neither is achieved by being uselessly wide
    lo, hi = rc.tango_score_interval(3, 2, 112)
    assert (hi - lo) < 0.25


def test_paired_interval_is_sign_symmetric():
    """Swapping b and c must negate and reverse every interval.

    This exposes a wrong nuisance bound in one line: the defect was invisible in the
    beneficial direction and catastrophic in the other, and asymmetry is its fingerprint.
    """
    for b, c, n in ((20, 70, 112), (3, 2, 112), (11, 2, 112), (0, 4, 56), (16, 1, 56)):
        for fn in (rc.tango_score_interval,
                   lambda x, y, m: rc.exact_unconditional_interval(x, y, m, grid=20)):
            lo, hi = fn(b, c, n)
            rlo, rhi = fn(c, b, n)
            assert abs(lo - (-rhi)) < 1e-6, (b, c, lo, rhi)
            assert abs(hi - (-rlo)) < 1e-6, (b, c, hi, rlo)


def test_the_known_nuisance_bound_counterexamples():
    """The two counterexamples the second review supplied, pinned."""
    lo, hi = rc.tango_score_interval(20, 70, 112)
    assert abs(lo - (-0.576935)) < 1e-5 and abs(hi - (-0.290872)) < 1e-5, (lo, hi)
    lo, hi = rc.exact_unconditional_interval(0, 40, 40, grid=20)
    assert abs(lo - (-1.0)) < 1e-9 and abs(hi - (-0.8)) < 1e-6, (lo, hi)


def test_ideal_bootstrap_coverage_is_measured_not_assumed():
    """The PRIMARY interval under-covers at this n, and the number is pinned.

    An infinite-resample percentile bootstrap in the review's scenario covers 0.924, not
    0.95. The report states that; this test stops the claim drifting back up.
    """
    def ideal(b, c, n, alpha=0.05):
        p = (b + c) / n
        cum, lo, hi = 0.0, None, None
        for k in range(n + 1):
            cum += math.comb(n, k) * p ** k * (1 - p) ** (n - k)
            if lo is None and cum >= alpha / 2:
                lo = k
            if hi is None and cum >= 1 - alpha / 2:
                hi = k
        return (lo / n, (hi if hi is not None else n) / n)

    coverage = _scenario_coverage(ideal)
    assert abs(coverage - 0.9237318945) < 1e-6, coverage
    assert coverage < 0.95, "the bootstrap under-covers here; the report must say so"


def test_cluster_bootstrap_covers_and_widens_with_clustering():
    """The primary interval, simulated in BOTH directions.

    Nominal-ish when instances are independent, and wider — not narrower — when instances
    are paired inside problems. A method that ignored the clusters would look *tighter*
    here, which is the error being guarded against. The detrimental direction is exercised
    too, because the first replacement was correct one way and 0.075 the other and nothing
    in this suite would have noticed.
    """
    rng = random.Random(4)
    reps, boot = 300, 250
    measured = {}
    for sign in (+1, -1):
        independent_width = None
        for clustered in (False, True):
            covered, widths = 0, []
            for _ in range(reps):
                by_problem = {}
                if clustered:                      # 56 problems x 2 correlated instances
                    for pid in range(56):
                        v = sign if rng.random() < 0.10 else 0
                        by_problem[str(pid)] = [v, v]
                else:                              # 112 independent instances
                    for pid in range(112):
                        by_problem[str(pid)] = [sign if rng.random() < 0.10 else 0]
                lo, hi = rc.cluster_bootstrap_ci(by_problem, boot, rng.randrange(10 ** 6))
                widths.append(hi - lo)
                if lo <= sign * 0.10 <= hi:
                    covered += 1
            rate = covered / reps
            measured[(sign, clustered)] = rate
            # Measured, not nominal: about 0.93 independent and 0.90 clustered here. The
            # report quotes these as measured and says the bootstrap under-covers.
            assert 0.87 <= rate <= 0.99, (sign, clustered, rate)
            if clustered:
                assert sum(widths) / len(widths) > independent_width * 1.2
            else:
                independent_width = sum(widths) / len(widths)
    # symmetric in sign, as a percentile bootstrap on symmetric data must be
    for clustered in (False, True):
        assert abs(measured[(+1, clustered)] - measured[(-1, clustered)]) < 0.06, measured


def test_ideal_bootstrap_coverage_differs_by_scenario():
    """The two scenarios give DIFFERENT bootstrap coverage, and the report must not
    reuse one number for the other.

    The third review found the report quoting 0.924 — the beneficial `Bin(112, 0.1)`
    figure — as the detrimental `Bin(112, 0.5)` coverage, which is 0.953.
    """
    def ideal(b, c, n, alpha=0.05):
        p = (b + c) / n
        cum, lo, hi = 0.0, None, None
        for k in range(n + 1):
            cum += math.comb(n, k) * p ** k * (1 - p) ** (n - k)
            if lo is None and cum >= alpha / 2:
                lo = k
            if hi is None and cum >= 1 - alpha / 2:
                hi = k
        span = (lo / n, (hi if hi is not None else n) / n)
        return span if b >= c else (-span[1], -span[0])

    beneficial = _scenario_coverage(ideal)
    detrimental = _scenario_coverage(ideal, q=0.5, beneficial=False)
    assert abs(beneficial - 0.9237318945) < 1e-6, beneficial
    assert abs(detrimental - 0.9532649318) < 1e-6, detrimental
    assert abs(beneficial - detrimental) > 0.02, "the two scenarios are not interchangeable"


def test_exact_grid_endpoint_rounding_is_declared():
    """The exact grid's coverage depends on inward endpoint rounding, and that is stated.

    At (0, 44, 112) the grid test ACCEPTS delta = -0.5, but bisection returns a lower
    endpoint of -0.499999993614, which excludes it. The reported 0.984 is coverage of the
    RETURNED intervals; literal acceptance would give 0.9895. The report says so.
    """
    lo, hi = rc.exact_unconditional_interval(0, 44, 112)
    assert lo > -0.5, lo                      # excluded by ~6.4e-9
    assert abs(lo - (-0.4999999936)) < 1e-8, lo


def test_signflip_matches_brute_force_on_the_real_shape():
    """The cluster-level test, against explicit enumeration."""
    got = rc.signflip_p({"a": [1], "b": [1], "c": [-1], "d": [1, 1]})
    totals = [1, 1, -1, 2]
    obs = abs(sum(totals))
    want = sum(1 for s in itertools.product((1, -1), repeat=4)
               if abs(sum(x * y for x, y in zip(s, totals))) >= obs) / 16
    assert abs(got["p"] - want) < 1e-12
    assert got["method"] == "exact enumeration"


def test_fit_saturation_respects_its_registered_bound():
    """A in [0, 1] is a registered constraint, enforced inside the objective so every
    bootstrap path treats the boundary identically."""
    assert rc.fit_saturation(rc.union_curve([1] * 110, 8))["A"] == 1.0
    assert 0.0 <= rc.fit_saturation(rc.union_curve([0] * 110, 8))["A"] <= 1.0
