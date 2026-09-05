"""Every interval quoted in RESULTS-CEILING.md must exist in numbers.json.

The second cross-vendor review found the report quoting `[-0.88, +12.08]` where
regeneration gives `[-0.89, +12.07]` — a stale hand-transcribed interval that survived two
rounds of checking because nothing compared the prose to the generated numbers. This test
is that comparison.

It reads the report, extracts every bracketed interval pair it can parse, and requires each
to match some interval in `numbers.json` to within display rounding. Intervals that are
deliberately historical — the withdrawn construction, the reviewer's own recomputations,
figures quoted inside the "what the review changed" table — are listed explicitly, so the
allowance is visible rather than a loose tolerance.

    python benchmarks/code/tests/test_report_consistency.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = HERE.parent
REPORT = CODE / "RESULTS-CEILING.md"
NUMBERS = CODE / "records" / "ceiling" / "numbers.json"

#: Intervals that appear in the report on purpose and are NOT current results: the
#: withdrawn construction, values quoted from the reviews, and the historical table.
HISTORICAL = {
    (-3.16, 3.99),      # the withdrawn conditional headline
    (3.16, -1.93),      # the swapped-tail artefact, quoted in the beta-tail section
    (12.94, 30.27),     # first-version referent P flags, quoted in the review table
    (-1.54, 9.54),      # first-version referent-cross
    (1.06, 11.16),      # first-version referent-loop net
    (-1.11, 2.68),      # first-version cross-loop net
    (3.59, 24.11),      # first-version self-cross C flags
    (42.6, 60.9),       # Wilson, shown for comparison
    (68.7, 88.9),       # Wilson, shown for comparison
    (52.5, 70.4),       # Wilson, shown for comparison
    (0.0, 6.4),         # Wilson bound for the 0/56 degeneracy note
    (-0.5388, -0.3577), # the reviewer's counterexample, pre-fix
    (-0.576935, -0.290872),  # the reviewer's counterexample, correct value
    (-1.0, -0.8),       # the reviewer's second counterexample
    (0.0, 1.0),         # the registered bound on A
}


def _is_pair(value):
    return (isinstance(value, list) and len(value) == 2
            and all(isinstance(v, (int, float)) for v in value))


def collect_numbers_intervals(obj, out):
    """Every [lo, hi] pair anywhere in numbers.json, as display-rounded percentages.

    Pairs are recognised wherever they occur, including nested inside a list — a list of
    per-K intervals such as ``curve_ci95`` is a list OF pairs, and an earlier version of
    this collector only looked for pairs hanging directly off a dict key, so every
    per-K interval in Table 2 looked unmatched.
    """
    if _is_pair(obj):
        lo, hi = obj
        for places in (1, 2):
            out.add((round(100 * lo, places), round(100 * hi, places)))
        return
    if isinstance(obj, dict):
        for value in obj.values():
            collect_numbers_intervals(value, out)
    elif isinstance(obj, list):
        for value in obj:
            collect_numbers_intervals(value, out)


_INTERVAL = re.compile(r"\[\s*(-?\d+\.\d+)\s*,\s*(\+?-?\d+\.\d+)\s*\]")


def test_every_quoted_interval_is_in_numbers_json():
    numbers = json.loads(NUMBERS.read_text(encoding="utf-8"))
    known: set = set()
    collect_numbers_intervals(numbers, known)
    # power values and shares also appear as bare fractions; allow their rounded forms
    text = REPORT.read_text(encoding="utf-8")

    unmatched = []
    for match in _INTERVAL.finditer(text):
        lo = round(float(match.group(1)), 2)
        hi = round(float(match.group(2).replace("+", "")), 2)
        if (lo, hi) in HISTORICAL:
            continue
        candidates = {(round(lo, 1), round(hi, 1)), (lo, hi)}
        if candidates & known:
            continue
        # allow one-decimal display of a two-decimal stored value and vice versa
        if any(abs(a - lo) <= 0.051 and abs(b - hi) <= 0.051 for a, b in known):
            continue
        unmatched.append((match.group(0), text[max(0, match.start() - 70):match.start()]
                          .replace("\n", " ")[-70:]))
    assert not unmatched, "intervals in the report that are not in numbers.json:\n" + \
        "\n".join(f"  {iv}   ...{ctx}" for iv, ctx in unmatched[:20])


def test_report_states_the_correction_threshold_once_in_prose():
    """The threshold belongs in the statistical-analysis subsection, not in 13 tables."""
    text = REPORT.read_text(encoding="utf-8")
    assert text.count("0.00313") <= 3, text.count("0.00313")


def _current_claims() -> str:
    """The report minus its audit trail and deviations.

    The "what the review changed" tables and the deviations quote earlier, withdrawn
    wording on purpose — that is the point of an audit trail. Scoping the claim checks to
    the body keeps those quotations legal while still failing if a withdrawn claim comes
    back as a live assertion.
    """
    text = REPORT.read_text(encoding="utf-8")
    body = text.split("## What was run", 1)[-1]
    body = body.split("## Deviations from the plan", 1)[0]
    # Withdrawn wording is always quoted when it is being denied ("no claim that it
    # \"never under-covers\" is made"), so quoted spans are not live assertions. Strip
    # them; what remains is what the report asserts in its own voice.
    body = re.sub(r"[\u201c\"][^\u201d\"\n]{0,200}[\u201d\"]", " ", body)
    return body.lower()


def test_report_does_not_claim_exactly_one_contrast_survives():
    for phrase in ("exactly one contrast clears",
                   "the only contrast in this study that clears",
                   "exactly one secondary contrast"):
        assert phrase not in _current_claims(), phrase


def test_report_does_not_reassert_any_withdrawn_claim():
    """Every phrase two rounds of review made this study withdraw, checked in the body."""
    for phrase in ("in the limit of unlimited readings", "cannot be seen",
                   "did not raise accuracy", "never under-covers", "0.95 nominal",
                   "byte-identical output", "bonferroni/12", "0.00417"):
        assert phrase not in _current_claims(), phrase


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except AssertionError as exc:
                failures += 1
                print("FAIL", name, exc)
    sys.exit(1 if failures else 0)
