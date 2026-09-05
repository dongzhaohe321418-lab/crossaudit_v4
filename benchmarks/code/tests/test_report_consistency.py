"""Every interval quoted in RESULTS-CEILING.md must exist in numbers.json, exactly.

The second cross-vendor review found the report quoting `[-0.88, +12.08]` where
regeneration gives `[-0.89, +12.07]`. The first version of this guard was written to catch
that and **did not**: the third review showed that mutating a prose interval by 0.01 left it
green, and that replacing the headline with `[-99.99, +99.99]` also passed. It rounded
candidates to one decimal, allowed 0.051 of slack, ignored the Unicode minus and the leading
`+`, and accepted any interval in the file regardless of which quantity the sentence was
about.

This version:

* parses `−` (U+2212) and `-` alike, and a leading `+`;
* compares **at the precision the report displays**, with **zero tolerance** — an interval
  written to two decimals must equal the stored value rounded to two decimals;
* **ties an interval to its estimand** where the sentence names one, so a number that is
  real but belongs to a different quantity is still a failure;
* is itself tested, by mutating the report in memory and requiring the check to go red.

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

MINUS = "−"

#: Intervals that appear on purpose and are NOT current results: the withdrawn
#: construction, values quoted from the three reviews, and the historical tables. Each is
#: listed with why it is allowed, so the allowance is auditable rather than a blanket.
HISTORICAL = {
    (-3.16, 3.99): "the withdrawn conditional headline (CORRECTIONS #15)",
    (3.16, -1.93): "the swapped-tail artefact, quoted in the beta-tail section",
    (12.94, 30.27): "first-version referent P flags, in the review table",
    (-1.54, 9.54): "first-version referent-cross, in the review table",
    (1.06, 11.16): "first-version referent-loop net, in the review table",
    (-1.11, 2.68): "first-version cross-loop net, in the review table",
    (3.59, 24.11): "first-version self-cross C flags, in the review table",
    (42.6, 60.9): "Wilson, printed beside the cluster interval for comparison",
    (68.7, 88.9): "Wilson, printed beside the cluster interval for comparison",
    (52.5, 70.4): "Wilson, printed beside the cluster interval for comparison",
    (0.0, 6.4): "Wilson bound quoted in the 0/56 degeneracy note",
    (-0.5388, -0.3577): "the third review's counterexample, pre-fix",
    (-0.576935, -0.290872): "the third review's counterexample, correct value",
    (-1.0, -0.8): "the third review's second counterexample",
    (0.0, 1.0): "the registered bound on A",
    (-0.88, 12.08): "the stale interval CORRECTIONS #15 withdraws, quoted there",
    (66.7, 93.1): "the second review's seed-20260908 recomputation, named as theirs",
    (-99.99, 99.99): "the mutation the third review used to show the old guard did not "
                     "bite, quoted in the round-3 audit table",
    (6.3, 43.8): "the erroneous prose value this guard caught, quoted in the round-3 "
                 "audit table as the error it found",
}

#: Spans of prose whose intervals are bound, in order, to specific numbers.json paths.
#: Binding by SPAN rather than by a preceding label: a label like "bootstrap CI" occurs in
#: several sentences about different quantities, and binding on it attached the primary
#: outcome's interval to the headline's estimand. A span is unambiguous.
BOUND_SPANS: list[tuple[str, list[tuple]]] = [
    (r"passing a hidden test suite by \*\*\+0\.89 percentage points.{0,220}?exact "
     r"McNemar",
     [("ceiling2", "arms", "self-loop", "net_primary", "ci95"),
      ("ceiling2", "arms", "self-loop", "net_primary", "tango_ci95"),
      ("ceiling2", "arms", "self-loop", "net_primary", "exact_unconditional_ci95")]),
    (r"A\(self\) − A\(cross\) on stratum P, is −14\.9 points.{0,220}?"
     r"−12\.7 points \[[^\]]*\]",
     [("ceiling1", "primary_ceiling1", "P", "ci95"),
      ("ceiling1", "primary_ceiling1", "P", "raw_diff_ci95")]),
]


def _pairs(obj, out):
    """Every [lo, hi] numeric pair anywhere in numbers.json, as percentages."""
    if (isinstance(obj, list) and len(obj) == 2
            and all(isinstance(v, (int, float)) for v in obj)):
        out.add((100 * obj[0], 100 * obj[1]))
        return
    if isinstance(obj, dict):
        for value in obj.values():
            _pairs(value, out)
    elif isinstance(obj, list):
        for value in obj:
            _pairs(value, out)


_NUM = r"[+" + MINUS + r"\-]?\d+\.\d+"
_INTERVAL = re.compile(r"\[\s*(" + _NUM + r")\s*,\s*(" + _NUM + r")\s*\]")


def _parse(token: str) -> tuple[float, int]:
    """(value, decimals displayed). Handles U+2212 and a leading '+'."""
    clean = token.replace(MINUS, "-").replace("+", "")
    return float(clean), len(clean.split(".")[1])


def _at(numbers, path):
    node = numbers
    for key in path:
        node = node[key]
    return (100 * node[0], 100 * node[1])


def _matches(quoted, stored, decimals) -> bool:
    """Equality at the precision the report displays. Zero tolerance."""
    return all(round(q, d) == round(s, d)
               for q, s, d in zip(quoted, stored, decimals))


def check_report(text: str, numbers: dict) -> list[str]:
    """Every problem found. Empty means the report's intervals are all real and correct."""
    known: set = set()
    _pairs(numbers, known)
    problems = []
    bound_spans = []

    # 1. Spans whose intervals are bound, in order, to named estimands.
    for pattern, paths in BOUND_SPANS:
        match = re.search(pattern, text, re.S)
        if match is None:
            problems.append(f"bound span not found in the report: {pattern[:60]}... — "
                            f"the sentence changed shape; update BOUND_SPANS")
            continue
        bound_spans.append((match.start(), match.end()))
        found = list(_INTERVAL.finditer(match.group(0)))
        if len(found) != len(paths):
            problems.append(f"bound span has {len(found)} intervals, expected "
                            f"{len(paths)}: {match.group(0)[:80]!r}")
            continue
        for interval, path in zip(found, paths):
            lo, dlo = _parse(interval.group(1))
            hi, dhi = _parse(interval.group(2))
            try:
                stored = _at(numbers, path)
            except (KeyError, IndexError, TypeError):
                problems.append(f"{interval.group(0)} — estimand path missing: {path}")
                continue
            if not _matches((lo, hi), stored, (dlo, dhi)):
                problems.append(
                    f"{interval.group(0)} is quoted for {'.'.join(map(str, path))} "
                    f"but that estimand is [{stored[0]:.{dlo}f}, {stored[1]:.{dhi}f}]")

    # 2. Every other interval must exist somewhere in numbers.json, at displayed precision.
    for match in _INTERVAL.finditer(text):
        if any(start <= match.start() < end for start, end in bound_spans):
            continue
        lo, dlo = _parse(match.group(1))
        hi, dhi = _parse(match.group(2))
        decimals = (dlo, dhi)
        if any(_matches((lo, hi), h, decimals) for h in HISTORICAL):
            continue
        if not any(_matches((lo, hi), k, decimals) for k in known):
            context = text[max(0, match.start() - 90):match.start()].replace("\n", " ")
            problems.append(f"{match.group(0)} is in no numbers.json interval "
                            f"(context: ...{context[-70:]})")
    return problems


def test_every_quoted_interval_is_in_numbers_json():
    numbers = json.loads(NUMBERS.read_text(encoding="utf-8"))
    problems = check_report(REPORT.read_text(encoding="utf-8"), numbers)
    assert not problems, "intervals in the report that do not check out:\n" + \
        "\n".join("  " + p for p in problems[:20])


def test_the_guard_goes_red_when_an_interval_is_mutated_by_a_hundredth():
    """A test of the test. The previous guard passed all of these.

    Each mutation is applied in memory only; the file on disk is never written.
    """
    numbers = json.loads(NUMBERS.read_text(encoding="utf-8"))
    original = REPORT.read_text(encoding="utf-8")
    assert not check_report(original, numbers), "baseline must be clean"

    mutations = [
        ("[-32.1, -2.3]", "[-32.11, -2.3]"),
        (f"[{MINUS}3.54, +5.88]", f"[{MINUS}3.55, +5.88]"),
        (f"[{MINUS}3.54, +5.88]", f"[{MINUS}99.99, +99.99]"),
        ("[5.2, 17.2]", "[5.21, 17.2]"),
        ("[5.2, 17.2]", "[55.2, 77.2]"),
    ]
    checked = 0
    for before, after in mutations:
        if before not in original:
            continue
        checked += 1
        assert check_report(original.replace(before, after, 1), numbers), \
            f"guard stayed green after mutating {before!r} -> {after!r}"
    assert checked >= 4, f"only {checked} mutations were applicable; the guard is untested"


def test_the_guard_catches_a_real_interval_attached_to_the_wrong_estimand():
    """A number that exists in numbers.json but belongs to another quantity."""
    numbers = json.loads(NUMBERS.read_text(encoding="utf-8"))
    original = REPORT.read_text(encoding="utf-8")
    swapped = original.replace(f"problem-cluster\nbootstrap CI [{MINUS}3.54, +5.88]",
                               f"problem-cluster\nbootstrap CI [{MINUS}3.98, +6.06]", 1)
    if swapped == original:
        swapped = original.replace(f"bootstrap CI [{MINUS}3.54, +5.88]",
                                   f"bootstrap CI [{MINUS}3.98, +6.06]", 1)
    assert swapped != original, "the headline sentence changed shape; update this test"
    assert check_report(swapped, numbers), \
        "guard accepted the Tango interval where the cluster interval belongs"


def _current_claims() -> str:
    """The report minus its audit trail and deviations, with quoted spans removed.

    The review tables and the deviations quote withdrawn wording on purpose. Quoted spans
    are denials, not assertions. What remains is what the report says in its own voice.
    """
    text = REPORT.read_text(encoding="utf-8")
    body = text.split("## What was run", 1)[-1]
    body = body.split("## Deviations from the plan", 1)[0]
    body = re.sub(r"[“\"][^”\"\n]{0,200}[”\"]", " ", body)
    return body.lower()


def test_report_does_not_claim_exactly_one_contrast_survives():
    for phrase in ("exactly one contrast clears",
                   "the only contrast in this study that clears",
                   "exactly one secondary contrast"):
        assert phrase not in _current_claims(), phrase


def test_report_does_not_reassert_any_withdrawn_claim():
    for phrase in ("in the limit of unlimited readings", "cannot be seen",
                   "did not raise accuracy", "never under-covers", "0.95 nominal",
                   "byte-identical output", "bonferroni/12", "0.00417",
                   "could not have detected a small one",
                   "every interval in this report is roughly"):
        assert phrase not in _current_claims(), phrase


def test_report_states_the_correction_threshold_once_in_live_prose():
    """Once live, plus once in the historical correction table. Both are intended."""
    text = REPORT.read_text(encoding="utf-8")
    assert text.count("0.00313") <= 2, text.count("0.00313")
    assert _current_claims().count("0.00313") == 1, _current_claims().count("0.00313")


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except AssertionError as exc:
                failures += 1
                print("FAIL", name, str(exc)[:400])
    sys.exit(1 if failures else 0)
