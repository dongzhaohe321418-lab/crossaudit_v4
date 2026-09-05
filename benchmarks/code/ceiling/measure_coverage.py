"""Measure every coverage figure the report quotes, and commit it as an artefact.

The tenth cross-vendor review found that the report's coverage tables could be edited
freely: nothing read them. The statistics tests measure coverage, but they compare against
constants written beside them, and the report's prose was checked by nobody.

This closes the chain. One script measures every figure; `records/ceiling/coverage.json` is
the artefact; `test_ceiling_stats.py` asserts its own measurements equal the artefact, and
`test_report_consistency.py` asserts the report's tables equal the artefact. Prose is then
bound to a measurement rather than to a hand-typed constant.

Exact enumeration over the binomial — no simulation, so the numbers are reproducible to
machine precision and this script is deterministic.

    python benchmarks/code/ceiling/measure_coverage.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CODE))
sys.path.insert(0, str(CODE / "tests"))

import report_ceiling as rc  # noqa: E402
import test_ceiling_stats as pins  # noqa: E402  (the pre-fix estimators live there)

N = 112


def ideal_bootstrap(b: int, c: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """The infinite-resample percentile bootstrap, enumerated rather than simulated."""
    p = (b + c) / n
    cumulative, lo, hi = 0.0, None, None
    for k in range(n + 1):
        cumulative += math.comb(n, k) * p ** k * (1 - p) ** (n - k)
        if lo is None and cumulative >= alpha / 2:
            lo = k
        if hi is None and cumulative >= 1 - alpha / 2:
            hi = k
    span = (lo / n, (hi if hi is not None else n) / n)
    return span if b >= c else (-span[1], -span[0])


def withdrawn(b: int, c: int, n: int) -> tuple[float | None, float | None]:
    discordant = b + c
    if discordant == 0:
        return (None, None)
    lo, hi = rc.clopper_pearson(b, discordant)
    return (discordant * (2 * lo - 1) / n, discordant * (2 * hi - 1) / n)


def coverage(interval_fn, n: int, q: float, beneficial: bool) -> float:
    truth = q if beneficial else -q
    total = 0.0
    for drawn in range(n + 1):
        weight = math.comb(n, drawn) * q ** drawn * (1 - q) ** (n - drawn)
        if weight < 1e-15:
            continue
        b, c = (drawn, 0) if beneficial else (0, drawn)
        lo, hi = interval_fn(b, c, n)
        if lo is not None and lo <= truth <= hi:
            total += weight
    return total


METHODS = {
    "withdrawn_conditional": withdrawn,
    "ideal_bootstrap": ideal_bootstrap,
    "tango": lambda b, c, n: rc.tango_score_interval(b, c, n),
    "exact_grid": lambda b, c, n: rc.exact_unconditional_interval(b, c, n),
    "tango_prefix": pins.prefix_tango,
    "exact_grid_prefix": pins.prefix_exact,
}

SCENARIOS = {
    "beneficial": {"q": 0.1, "beneficial": True,
                   "description": "D ~ Binomial(112, 0.1), every discordance beneficial, "
                                  "true delta = +0.10"},
    "detrimental": {"q": 0.5, "beneficial": False,
                    "description": "C ~ Binomial(112, 0.5), every discordance "
                                   "detrimental, true delta = -0.50"},
}


def main() -> int:
    out: dict = {
        "n": N,
        "method": "exact enumeration over the binomial; no simulation",
        "scenarios": {k: v["description"] for k, v in SCENARIOS.items()},
        "coverage": {},
    }
    for name, fn in METHODS.items():
        out["coverage"][name] = {}
        for scenario, spec in SCENARIOS.items():
            if name == "withdrawn_conditional" and scenario == "detrimental":
                continue          # the withdrawn method is quoted for one scenario only
            value = coverage(fn, N, spec["q"], spec["beneficial"])
            out["coverage"][name][scenario] = value
            print(f"  {name:24s} {scenario:12s} {value:.12f}", flush=True)
    path = CODE / "records" / "ceiling" / "coverage.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
