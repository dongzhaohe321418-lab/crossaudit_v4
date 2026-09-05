"""Study 8's estimators, checked against brute force and against published values.

Every inferential quantity in ``RESULTS-CEILING.md`` comes out of ``report_ceiling.py``,
which implements its own regularised incomplete beta, Clopper-Pearson inversion, exact
McNemar tail, saturation fit and beta-binomial likelihood rather than depending on SciPy.
That is a reproducibility decision — a reader can read the whole of it in one file — and it
puts the burden of proof here. These tests are the proof.

    python -m pytest benchmarks/code/tests/test_ceiling_stats.py
"""

from __future__ import annotations

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


def test_paired_difference_interval_is_ordered_and_covers_the_point():
    """The bug this file exists to have caught: a swapped beta tail.

    An interval whose bounds are the wrong way round, or that does not contain its own
    point estimate, is a defect that survives every eyeball check because both numbers
    look plausible. It does not survive this.
    """
    for b, c, n in ((3, 2, 112), (3, 0, 112), (11, 2, 112), (0, 4, 56), (16, 1, 56)):
        d = rc.paired_difference_exact(b, c, n)
        low, high = d["ci95"]
        assert low <= high
        assert low <= d["delta"] <= high
    # no discordant pairs: a count, never a rate (EXPERIMENT_RECORD §9)
    none = rc.paired_difference_exact(0, 0, 56)
    assert none["ci95"] is None
    assert none["n_discordant"] == 0


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
