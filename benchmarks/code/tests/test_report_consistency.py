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
    (40.4, 63.6): "the duplicate residual-share interval withdrawn in deviation 26 and "
                  "CORRECTIONS #24, quoted there as the number that was wrong",
}

#: Spans of prose whose intervals are bound, in order, to specific numbers.json paths.
#: Binding by SPAN rather than by a preceding label: a label like "bootstrap CI" occurs in
#: several sentences about different quantities, and binding on it attached the primary
#: outcome's interval to the headline's estimand. A span is unambiguous.
BOUND_SPANS: list[tuple[str, list[tuple]]] = [
    # NB: BOUND_SPANS matches the RAW report text, so markdown emphasis is present here
    # and must be matched. The rate bindings below run on normalised text and must not.
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


# ---------------------------------------------------------------------------------
# Interval completeness, mechanically. Four reviews found bare rates in the opening and
# the conclusion by hand; this finds them forever.
# ---------------------------------------------------------------------------------

#: A rate in the opening or the conclusion is matched by exactly one rule below. There is
#: no context-based exemption: a number is either **bound** to the `numbers.json` array its
#: interval must come from, or **declared** as a count / exact quantity with a reason. The
#: fifth review showed why adjacency is not enough — this displacement stayed green:
#:
#:     (30.0% at 16.0% [10.1, 22.3], with the recall interval [20.0, 40.7])
#:
#: because the guard accepted the false-positive interval sitting ten characters from the
#: recall rate. Binding each rate to its own key is the only rule that rejects it, and the
#: displacement is committed below as a regression test.
_RATE = re.compile(r"(?<![\w.$])([+" + MINUS + r"\-]?\d+(?:\.\d+)?)\s*(%|pp\b|"
                   r"percentage points\b|points\b)")

#: (regex over the flattened section, value path or None, interval path or None, why).
#: The regex must capture the rate as group "v" and, for a bound rule, its interval as
#: groups "lo" and "hi". Every rate the regexes do not cover is a failure.
_IV = r"\[\s*(?P<lo>[+" + MINUS + r"\-]?\d+\.\d+)\s*,\s*(?P<hi>[+" + MINUS + r"\-]?\d+\.\d+)\s*\]"
#: Markdown emphasis may sit between a rate and its interval; it is not text.
_MD = r"[\s*]*"
C1 = ("ceiling1", "families")
RATE_RULES: list[tuple[str, tuple | None, tuple | None, str]] = [
    # ---- bound: value and interval both checked against numbers.json ----------------
    (r"from (?P<v>10\.7)% " + _IV, C1 + ("cross", "P", "draw1_block", "rate"),
     C1 + ("cross", "P", "draw1_block", "cluster_ci95"), ""),
    (r"to (?P<v>30\.0)% \(33 of 110\) " + _IV,
     C1 + ("cross", "P", "union_at_kmax"),
     C1 + ("cross", "P", "union_at_kmax_block", "cluster_ci95"), ""),
    (r"go from (?P<v>4\.5)% " + _IV, C1 + ("cross", "C", "draw1_block", "rate"),
     C1 + ("cross", "C", "draw1_block", "cluster_ci95"), ""),
    (r"to (?P<v>16\.0)% " + _IV + r"\. Its fitted",
     C1 + ("cross", "C", "union_at_kmax"),
     C1 + ("cross", "C", "union_at_kmax_block", "cluster_ci95"), ""),
    (r"fitted asymptote is (?P<v>31\.5)% " + _IV, C1 + ("cross", "P", "fit", "A"),
     C1 + ("cross", "P", "fit_A_ci95"), ""),
    (r"gained (?P<v>1\.93) points " + _IV,
     C1 + ("cross", "P", "marginal_gain_last_step"),
     C1 + ("cross", "P", "last_step_gain_block", "cluster_ci95"), ""),
    (r"so (?P<v>31\.5)% " + _IV + r" is an\s*extrapolation", C1 + ("cross", "P", "fit", "A"),
     C1 + ("cross", "P", "fit_A_ci95"), ""),
    (r"and (?P<v>30\.0)% " + _IV + r" is the number to quote",
     C1 + ("cross", "P", "union_at_kmax"),
     C1 + ("cross", "P", "union_at_kmax_block", "cluster_ci95"), ""),
    (r"far lower: (?P<v>15\.5)% " + _IV, C1 + ("self", "P", "draw1_block", "rate"),
     C1 + ("self", "P", "draw1_block", "cluster_ci95"), ""),
    (r"(?P<v>17\.3)% \(19 of 110\) " + _IV, C1 + ("self", "P", "union_at_kmax"),
     C1 + ("self", "P", "union_at_kmax_block", "cluster_ci95"), ""),
    (r"asymptote (?P<v>16\.6)% " + _IV, C1 + ("self", "P", "fit", "A"),
     C1 + ("self", "P", "fit_A_ci95"), ""),
    (r"false-positive rate of (?P<v>24\.0)% " + _IV,
     C1 + ("self", "C", "union_at_kmax"),
     C1 + ("self", "C", "union_at_kmax_block", "cluster_ci95"), ""),
    (r"stratum P, is (?P<v>" + MINUS + r"14\.9) points, 95% problem-cluster bootstrap CI " + _IV,
     ("ceiling1", "primary_ceiling1", "P", "A_self_minus_cross"),
     ("ceiling1", "primary_ceiling1", "P", "ci95"), ""),
    (r"readings, is (?P<v>" + MINUS + r"12\.7) points " + _IV,
     ("ceiling1", "primary_ceiling1", "P", "raw_union_diff_at_k_common"),
     ("ceiling1", "primary_ceiling1", "P", "raw_diff_ci95"), ""),
    (r"stranger's \(raw (?P<v>" + MINUS + r"12\.7) points " + _IV,
     ("ceiling1", "primary_ceiling1", "P", "raw_union_diff_at_k_common"),
     ("ceiling1", "primary_ceiling1", "P", "raw_diff_ci95"), ""),
    (r"recalls (?P<v>30\.2)% " + _IV, C1 + ("astra", "P", "draw1_block", "rate"),
     C1 + ("astra", "P", "draw1_block", "cluster_ci95"), ""),
    (r"recalls 30\.2% \[[^\]]*\] at (?P<v>9\.7)% " + _IV + r" false positives",
     C1 + ("astra", "C", "draw1_block", "rate"),
     C1 + ("astra", "C", "draw1_block", "cluster_ci95"), ""),
    (r"cost \((?P<v>30\.0)% " + _IV, C1 + ("cross", "P", "union_at_kmax"),
     C1 + ("cross", "P", "union_at_kmax_block", "cluster_ci95"), ""),
    (r"false-positive cost \(30\.0% \[[^\]]*\] at (?P<v>16\.0)% " + _IV + r"\)\.",
     C1 + ("cross", "C", "union_at_kmax"),
     C1 + ("cross", "C", "union_at_kmax_block", "cluster_ci95"), ""),
    (r"56: \+(?P<v>26\.8) points" + r", cluster CI " + _IV,
     ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "flag_discordance", "P",
      "delta"),
     ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "flag_discordance", "P",
      "ci95"), ""),
    (r"stratum-P flags \(\+(?P<v>26\.8) points " + _IV,
     ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "flag_discordance", "P",
      "delta"),
     ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "flag_discordance", "P",
      "ci95"), ""),
    (r"pooled P \+ C flags\s*\(\+(?P<v>19\.6) points " + _IV,
     ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "flag_discordance", "all",
      "delta"),
     ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "flag_discordance", "all",
      "ci95"), ""),
    (r"nets \+(?P<v>8\.04) pp, cluster CI " + _IV,
     ("ceiling2", "arms", "referent-loop", "net_primary", "delta"),
     ("ceiling2", "arms", "referent-loop", "net_primary", "ci95"), ""),
    (r"is \+(?P<v>5\.36) pp, cluster CI " + _IV,
     ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "delta"),
     ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "ci95"), ""),
    (r"\((?P<v>51\.8)%, cluster CI " + _IV + r"\) were flagged",
     ("ceiling1", "residual", "all_families", "share"),
     ("ceiling1", "residual", "all_families", "share_block", "cluster_ci95"), ""),
    (r"\((?P<v>80\.7)%, problem-cluster CI " + _IV,
     ("ceiling1", "residual_classified", "all_families", "shares", "unexercised-edge"),
     ("ceiling1", "residual_classified", "all_families", "cluster_ci95",
      "unexercised-edge"), ""),
    (r"54 of 103 \((?P<v>52\.4)% " + _IV,
     ("timeout_sensitivity", "residual_assertion_only", "rate"),
     ("timeout_sensitivity", "residual_assertion_only", "cluster_ci95"), ""),
    (r"57 of 110 \((?P<v>51\.8)% " + _IV + r"\)\.",
     ("timeout_sensitivity", "residual_registered", "rate"),
     ("timeout_sensitivity", "residual_registered", "cluster_ci95"), ""),
    (r"accuracy \(\+(?P<v>0\.89) pp, cluster\s+CI " + _IV,
     ("ceiling2", "arms", "self-loop", "net_primary", "delta"),
     ("ceiling2", "arms", "self-loop", "net_primary", "ci95"), ""),
    (r"higher \(24\.0% \[[^\]]*\] against (?P<v>16\.0)% " + _IV + r"\);",
     C1 + ("cross", "C", "union_at_kmax"),
     C1 + ("cross", "C", "union_at_kmax_block", "cluster_ci95"), ""),
    (r"false-positive rate was higher \((?P<v>24\.0)% " + _IV,
     C1 + ("self", "C", "union_at_kmax"),
     C1 + ("self", "C", "union_at_kmax_block", "cluster_ci95"), ""),
    (r"cost \(9\.7% \[[^\]]*\] against (?P<v>16\.0)% " + _IV + r"\);",
     C1 + ("cross", "C", "union_at_kmax"),
     C1 + ("cross", "C", "union_at_kmax_block", "cluster_ci95"), ""),
    (r"one frontier reading matched eight shipped readings on recall \((?P<v>30\.2)% "
     + _IV, C1 + ("astra", "P", "draw1_block", "rate"),
     C1 + ("astra", "P", "draw1_block", "cluster_ci95"), ""),
    (r"on recall \(30\.2% \[[^\]]*\] against (?P<v>30\.0)% " + _IV + r"\)",
     C1 + ("cross", "P", "union_at_kmax"),
     C1 + ("cross", "P", "union_at_kmax_block", "cluster_ci95"), ""),
    (r"at lower false-positive cost \((?P<v>9\.7)% " + _IV,
     C1 + ("astra", "C", "draw1_block", "rate"),
     C1 + ("astra", "C", "draw1_block", "cluster_ci95"), ""),
    (r"that (?P<v>51\.8)% " + _IV + r" of this defect population",
     ("ceiling1", "residual", "all_families", "share"),
     ("ceiling1", "residual", "all_families", "share_block", "cluster_ci95"), ""),
    (r"flagged, by more than anything else tried \(\+(?P<v>26\.8) points on "
     r"stratum-P flags, cluster CI " + _IV,
     ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "flag_discordance", "P",
      "delta"),
     ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "flag_discordance", "P",
      "ci95"), ""),
    (r"\(\+(?P<v>5\.36) pp against cross-loop, cluster CI " + _IV,
     ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "delta"),
     ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "ci95"), ""),
    # ---- declared: not estimates, so no interval is owed. Each says why. -------------
    (r'headline\'s "(?P<v>95)% exact" interval', None, None,
     "a nominal confidence level, not an estimate"),
    (r"suite by \+(?P<v>0\.89) percentage points \(95% problem-cluster", None, None,
     "bound by BOUND_SPANS, which checks all three headline intervals together"),
    (r"\+0\.89 percentage points \((?P<v>95)% problem-cluster", None, None,
     "a nominal confidence level, not an estimate"),
    # The reader sentence states its interval in prose, so it needs a prose-form rule.
    # It previously carried a DECLARATION claiming BOUND_SPANS checked it; BOUND_SPANS
    # checks the separate headline, so the reader sentence's interval was unbound and
    # could be replaced with "+1.00 to +2.00" or deleted outright with every test green.
    # The sixth cross-vendor review found that. Both mutations are now regression tests.
    (r"accuracy by \+(?P<v>0\.89) percentage points \(problem-cluster percentile "
     r"interval (?P<lo>[+" + MINUS + r"\-]?\d+\.\d+) to (?P<hi>[+" + MINUS +
     r"\-]?\d+\.\d+);",
     ("ceiling2", "arms", "self-loop", "net_primary", "delta"),
     ("ceiling2", "arms", "self-loop", "net_primary", "ci95"), ""),
    (r"0\.32 at \+(?P<v>5) points is limited", None, None,
     "a power-curve abscissa: an exact quantity from numbers.json/power, not an estimate"),
    (r"below about (?P<v>7) points would probably", None, None,
     "a rounded reading of the power curve, stated as approximate in the sentence"),
    (r"is " + MINUS + r"14\.9 points, (?P<v>95)% problem-cluster", None, None,
     "a nominal confidence level, not an estimate"),
]


def _sections(text: str) -> dict[str, str]:
    """The opening (before the audit trail) and the conclusion.

    These are the two places a reader meets a number without a table around it, so they
    are where every rate must be bound. The audit trail and the deviations quote withdrawn
    figures on purpose and are excluded.
    """
    opening = text.split("## What the review changed", 1)[0]
    tail = text.split("## What this study licenses, and what it does not", 1)
    conclusion = (tail[1].split("### Where this sits beside the earlier record", 1)[0]
                  if len(tail) > 1 else "")
    return {"opening": opening, "conclusion": conclusion}


def _normalise(section: str) -> str:
    """Flatten and strip markdown, so a binding pattern is written against prose.

    Emphasis, code ticks and blockquote markers carry no meaning for a number and made
    every pattern brittle: `**+26.8 points**, cluster CI [...]` needed a different regex
    from `+26.8 points [...]` for the same claim. Removing them once is more robust than
    encoding them 36 times, and it keeps the rate scan and the rule matching on identical
    offsets.
    """
    cleaned = section.replace("\n", " ")
    cleaned = re.sub(r"[*`>]", "", cleaned)
    return re.sub(r"\s+", " ", cleaned)


def _flat_sections(text: str) -> dict[str, str]:
    return {k: _normalise(v) for k, v in _sections(text).items()}


#: Tokens that must appear in the SAME SENTENCE as a rate, keyed by the interval array it
#: is bound to. A rule's anchor identifies *where* a rate sits; these identify *what the
#: sentence is about*. Without them a rate could be re-attributed by moving a clause into a
#: new sentence with a different subject — which is exactly what the seventh review did:
#:
#:     ... on recall (30.2% [...] against 30.0% [...]). The shipped auditor's eight
#:     readings operated at lower false-positive cost (9.7% [5.3, 14.5] against ...)
#:
#: leaving astra's one-reading false-positive rate attributed to the shipped auditor's
#: eight readings, with every test green. Requiring the sentence to name the family makes
#: that unbound, and red.
SUBJECT_TOKENS: dict[tuple, list[str]] = {
    ("ceiling1", "families", "astra", "P", "draw1_block", "cluster_ci95"):
        [r"astra|frontier"],
    ("ceiling1", "families", "astra", "C", "draw1_block", "cluster_ci95"):
        [r"astra|frontier"],
    ("ceiling1", "families", "cross", "P", "draw1_block", "cluster_ci95"):
        [r"cross-vendor|shipped"],
    ("ceiling1", "families", "cross", "C", "draw1_block", "cluster_ci95"):
        [r"cross-vendor|shipped"],
    ("ceiling1", "families", "cross", "P", "union_at_kmax_block", "cluster_ci95"):
        [r"cross-vendor|shipped|extrapolation", r"eight|K = 8|number to quote"],
    ("ceiling1", "families", "cross", "C", "union_at_kmax_block", "cluster_ci95"):
        [r"cross-vendor|shipped", r"eight|false positives|false-positive"],
    ("ceiling1", "families", "self", "P", "draw1_block", "cluster_ci95"):
        [r"generator's own model|self"],
    ("ceiling1", "families", "self", "P", "union_at_kmax_block", "cluster_ci95"):
        [r"generator's own model|self", r"eight"],
    ("ceiling1", "families", "self", "C", "union_at_kmax_block", "cluster_ci95"):
        [r"generator's own model|self|false-positive"],
    ("ceiling1", "families", "cross", "P", "fit_A_ci95"):
        [r"asymptote|extrapolation"],
    ("ceiling1", "families", "self", "P", "fit_A_ci95"):
        [r"asymptote"],
    ("ceiling1", "families", "cross", "P", "last_step_gain_block", "cluster_ci95"):
        [r"flattened|gained"],
}


def _sentence_around(section: str, position: int) -> str:
    """The sentence containing `position`.

    Split on sentence-final punctuation followed by whitespace and a capital or opening
    bracket, so "9.7%" and "0.32" are never treated as boundaries.
    """
    starts = [0] + [m.end() for m in
                    re.finditer(r"(?<=[.;])\s+(?=[A-Z(\u201c\"])", section)]
    start = max(s for s in starts if s <= position)
    ends = [m.start() for m in re.finditer(r"(?<=[.;])\s+(?=[A-Z(\u201c\"])", section)
            if m.start() > position]
    return section[start:(ends[0] if ends else len(section))]


def _digit_pos(section: str, start: int) -> int:
    """The index of the first digit at or after `start`.

    Rules capture the magnitude (`\\+(?P<v>26\\.8)`) while the rate scanner captures the
    sign too (`+26.8`), so the two disagree by one character on every signed number.
    Anchoring both on the first digit is what makes them comparable.
    """
    while start < len(section) and not section[start].isdigit():
        start += 1
    return start


def check_rate_bindings(text: str, numbers: dict) -> list[str]:
    """Every rate in the opening and conclusion, bound to its own key or declared."""
    problems = []
    for name, section in _flat_sections(text).items():
        covered: dict[int, str] = {}
        for pattern, value_path, interval_path, why in RATE_RULES:
            for match in re.finditer(pattern, section):
                covered[_digit_pos(section, match.start("v"))] = pattern
                if value_path is None:
                    continue
                quoted, decimals = _parse(match.group("v"))
                try:
                    stored_value = 100 * _at_scalar(numbers, value_path)
                    stored_iv = _at(numbers, interval_path)
                except (KeyError, IndexError, TypeError) as exc:
                    problems.append(f"[{name}] path missing for {match.group('v')!r}: "
                                    f"{value_path} / {interval_path} ({exc})")
                    continue
                if round(quoted, decimals) != round(stored_value, decimals):
                    problems.append(
                        f"[{name}] {match.group('v')!r} is bound to "
                        f"{'.'.join(map(str, value_path))} = "
                        f"{stored_value:.{decimals}f}")
                lo, dlo = _parse(match.group("lo"))
                hi, dhi = _parse(match.group("hi"))
                required = SUBJECT_TOKENS.get(tuple(interval_path), [])
                if required:
                    sentence = _sentence_around(section, match.start("v"))
                    absent = [tok for tok in required
                              if not re.search(tok, sentence, re.I)]
                    if absent:
                        problems.append(
                            f"[{name}] {match.group('v')!r} is bound to "
                            f"{'.'.join(map(str, interval_path))} but its sentence does "
                            f"not identify that subject (missing {absent}): "
                            f"...{sentence.strip()[:110]}")
                if not _matches((lo, hi), stored_iv, (dlo, dhi)):
                    problems.append(
                        f"[{name}] the interval beside {match.group('v')!r} is "
                        f"[{lo}, {hi}] but {'.'.join(map(str, interval_path))} is "
                        f"[{stored_iv[0]:.{dlo}f}, {stored_iv[1]:.{dhi}f}]")
        for match in _RATE.finditer(section):
            if _digit_pos(section, match.start(1)) in covered:
                continue
            problems.append(f"[{name}] UNBOUND rate {match.group(0)!r}: no rule binds it "
                            f"to a numbers.json key and none declares it exempt "
                            f"(...{section[max(0, match.start() - 70):match.end() + 30]})")
    return problems


def _at_scalar(numbers, path):
    node = numbers
    for key in path:
        node = node[key]
    return node


def test_rates_in_the_opening_and_conclusion_are_bound_to_their_own_keys():
    """Every rate in the opening and conclusion is bound to the array its interval must
    come from, or explicitly declared a count/exact quantity with a reason.

    Adjacency is not acceptance. Five reviews found bare or wrongly-supported rates here;
    binding each one to its own key is what makes a fourth instance impossible.
    """
    numbers = json.loads(NUMBERS.read_text(encoding="utf-8"))
    problems = check_rate_bindings(REPORT.read_text(encoding="utf-8"), numbers)
    assert not problems, ("rates that are not bound to their own key:\n"
                          + "\n".join("  " + p for p in problems[:20]))


def _binding_problems(mutated: str) -> list[str]:
    numbers = json.loads(NUMBERS.read_text(encoding="utf-8"))
    return check_rate_bindings(mutated, numbers)


def test_the_binding_rejects_another_quantitys_interval():
    """The fifth review's counterexample, committed as a regression test.

    This displacement kept every earlier guard green, because the false-positive interval
    sat ten characters from the recall rate and adjacency was acceptance:

        (30.0% at 16.0% [10.1, 22.3], with the recall interval [20.0, 40.7])

    Binding each rate to its own key is the only rule that rejects it.
    """
    original = REPORT.read_text(encoding="utf-8")
    mutated = original.replace(
        "(30.0% [20.0, 40.7] at 16.0% [10.1, 22.3])",
        "(30.0% at 16.0% [10.1, 22.3], with the recall interval [20.0, 40.7])", 1)
    assert mutated != original, "the opening sentence changed shape; update this test"
    assert _binding_problems(mutated), \
        "the guard accepted another quantity's interval as a rate's uncertainty"


def test_the_binding_rejects_a_stripped_interval():
    original = REPORT.read_text(encoding="utf-8")
    mutated = original.replace("30.0% (33 of 110) [20.0, 40.7]", "30.0% (33 of 110)", 1)
    assert mutated != original
    assert _binding_problems(mutated), "the guard stayed green with an interval removed"


def test_the_binding_rejects_two_intervals_swapped_between_rates():
    """Both intervals are real and both belong to the sentence — but to the other rate.

    Nothing that checks only "is this interval in numbers.json" can catch this.
    """
    original = REPORT.read_text(encoding="utf-8")
    mutated = original.replace(
        "**10.7% [5.1, 17.4]** to **30.0% (33 of 110) [20.0, 40.7]**",
        "**10.7% [20.0, 40.7]** to **30.0% (33 of 110) [5.1, 17.4]**", 1)
    assert mutated != original, "the opening sentence changed shape; update this test"
    problems = _binding_problems(mutated)
    assert len(problems) >= 2, f"swapping two intervals produced {len(problems)} problems"


def test_the_binding_rejects_a_wrong_value_with_a_right_interval():
    """A rate mistyped beside its own correct interval."""
    original = REPORT.read_text(encoding="utf-8")
    mutated = original.replace("to **30.0% (33 of 110) [20.0, 40.7]**",
                               "to **31.0% (33 of 110) [20.0, 40.7]**", 1)
    assert mutated != original
    assert _binding_problems(mutated), "the guard accepted a rate that is not its key"


def test_the_binding_rejects_a_tampered_reader_sentence():
    """The sixth review's two counterexamples, committed.

    The reader sentence states its interval in prose, and a declaration used to claim
    BOUND_SPANS checked it. BOUND_SPANS checks the separate headline, so this sentence's
    interval was unbound: it could be replaced with a fabricated range, or deleted, with
    all twelve tests green. It is the single sentence the report asks a reader to carry
    away, which makes it the worst possible thing to leave unchecked.
    """
    original = REPORT.read_text(encoding="utf-8")
    for before, after in (
            ("percentile interval " + MINUS + "3.54 to +5.88",
             "percentile interval +1.00 to +2.00"),
            ("percentile interval " + MINUS + "3.54 to +5.88;",
             "percentile interval omitted;")):
        mutated = original.replace(before, after, 1)
        assert mutated != original, f"the reader sentence changed shape: {before!r}"
        assert _binding_problems(mutated), \
            f"the guard stayed green after {after!r}"


def test_the_binding_rejects_a_reused_label_on_the_wrong_family():
    """The sixth review's insertion, committed.

    A rule anchored on "cost (" bound this sentence to *astra's one-reading* array, when
    the shipped auditor's eight-reading value is 16.0% [10.1, 22.3]. A label that occurs
    for more than one family or reading count must match on family and reading count.
    """
    original = REPORT.read_text(encoding="utf-8")
    insertion = ("The shipped auditor's eight-reading false-positive cost "
                 "(9.7% [5.3, 14.5]) was lower still. ")
    anchor_text = "**It does not license** the claim that those defects cannot be found."
    assert anchor_text in original, "the conclusion changed shape; update this test"
    mutated = original.replace(anchor_text, insertion + anchor_text, 1)
    assert _binding_problems(mutated), \
        "a false claim bound itself to another family's array and passed"


def test_the_binding_rejects_a_rate_moved_under_a_new_subject():
    """The seventh review's edit, committed.

    Splitting one sentence into two and giving the second a different subject left
    astra's one-reading false-positive rate attributed to the shipped auditor's eight
    readings, with all fifteen tests green: the rule's anchor still matched, and it
    matched only once, so the uniqueness check was silent too. A rate is now unbound
    unless its own sentence names the family the array belongs to.
    """
    original = REPORT.read_text(encoding="utf-8")
    mutated = original.replace(
        "30.0% [20.0, 40.7]) at lower false-positive cost",
        "30.0% [20.0, 40.7]). The shipped auditor's eight readings operated at lower "
        "false-positive cost", 1)
    assert mutated != original, "the conclusion changed shape; update this test"
    problems = _binding_problems(mutated)
    assert problems, "a rate was re-attributed to another family and passed"
    assert any("astra" in p for p in problems), problems[:2]


def test_no_binding_rule_matches_more_than_once():
    """Each rule identifies one occurrence. A second match means new prose slipped under
    an existing rule's anchor — which is how the reused-label counterexample got in.

    **This is deliberately a strict editing guard, and it has a known cost**: writing the
    same correct sentence twice fails it. That is accepted rather than loosened. A report
    that states a result twice should bind each statement separately, so that moving or
    editing one cannot silently borrow the other's guarantee; the seventh review noted the
    trade-off and it is taken knowingly.
    """
    sections = _flat_sections(REPORT.read_text(encoding="utf-8"))
    multiple = []
    for pattern, _value, _interval, _why in RATE_RULES:
        hits = sum(len(re.findall(pattern, section)) for section in sections.values())
        if hits > 1:
            multiple.append(f"{hits} matches: {pattern[:70]}")
    assert not multiple, ("binding rules matching more than once:\n"
                          + "\n".join("  " + m for m in multiple))


def test_every_bound_rule_actually_fires():
    """A rule that matches nothing is a rule that guards nothing.

    Without this, deleting a sentence would silently retire its binding and the guard
    would still pass.
    """
    text = REPORT.read_text(encoding="utf-8")
    sections = _flat_sections(text)
    dead = []
    for pattern, value_path, _interval_path, _why in RATE_RULES:
        if not any(re.search(pattern, section) for section in sections.values()):
            dead.append(pattern[:70])
    assert not dead, ("binding rules that match nothing in the report:\n"
                      + "\n".join("  " + d for d in dead))


# ---------------------------------------------------------------------------------
# Interval completeness, mechanically. Four reviews found bare rates in the opening and
# the conclusion by hand; this finds them forever.
# ---------------------------------------------------------------------------------



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
