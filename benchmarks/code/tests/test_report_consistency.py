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
    (r"to (?P<v>16\.0)% " + _IV + r"\. The shipped cross-vendor auditor's fitted",
     C1 + ("cross", "C", "union_at_kmax"),
     C1 + ("cross", "C", "union_at_kmax_block", "cluster_ci95"), ""),
    (r"auditor's fitted\s*asymptote is (?P<v>31\.5)% " + _IV, C1 + ("cross", "P", "fit", "A"),
     C1 + ("cross", "P", "fit_A_ci95"), ""),
    (r"auditor still gained (?P<v>1\.93) points " + _IV,
     C1 + ("cross", "P", "marginal_gain_last_step"),
     C1 + ("cross", "P", "last_step_gain_block", "cluster_ci95"), ""),
    (r"cross-vendor asymptote of\s*(?P<v>31\.5)% " + _IV + r" is an extrapolation", C1 + ("cross", "P", "fit", "A"),
     C1 + ("cross", "P", "fit_A_ci95"), ""),
    (r"eight-reading (?P<v>30\.0)% " + _IV + r" is the\s*number to quote",
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


def _normalise_with_map(section: str) -> tuple[str, list[int]]:
    """(normalised text, offset of each normalised character in `section`).

    The map is what lets a mutation be applied to the file the guard actually reads.
    Reconstructing the raw span by re-matching a prefix was fragile and silently produced
    no mutation for several rules, which made the generated test vacuous for them.
    """
    out, offsets = [], []
    previous_space = False
    for index, char in enumerate(section):
        if char in "*`>":
            continue
        if char.isspace():
            if previous_space or not out:
                continue
            out.append(" ")
            offsets.append(index)
            previous_space = True
            continue
        out.append(char)
        offsets.append(index)
        previous_space = False
    return "".join(out), offsets


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


#: The vocabulary that identifies a subject. Each key is a family or arm; the value is
#: (regexes that identify it in prose, the canonical phrase used when mutating to it).
#: The generated re-attribution test rewrites a rule's sentence from its own subject to
#: each of the others in turn and requires the guard to redden every time — so a new
#: binding cannot be added without its mutations existing.
FAMILY_VOCAB: dict[str, tuple[list[str], str]] = {
    "cross":         ([r"cross-vendor", r"shipped"], "shipped cross-vendor"),
    "self":          ([r"generator's own model", r"self model", r"self-auditor"],
                      "generator's own model"),
    "astra":         ([r"astra", r"frontier"], "astra"),
    "self-loop":     ([r"self-audit", r"self-loop"], "self-loop"),
    "cross-loop":    ([r"cross-loop"], "cross-loop"),
    "referent-loop": ([r"referent"], "referent-loop"),
    "residual":      ([r"residual", r"no reading of any family", r"flagged by no"],
                      "residual"),
    "primary":       ([r"A\(self\) . A\(cross\)", r"union recalls", r"union recall"],
                      "the primary outcome"),
    "timeout":       ([r"assertion failure", r"timeout"], "the assertion-only population"),
}

#: Every bound array's subject requirement: (family key, extra tokens that must also be
#: present). **No bound array may be absent from this map, and none may have an empty
#: family** — `test_every_bound_rule_declares_a_subject` enforces both. Eight rounds of
#: review kept finding rates that could be re-attributed by editing prose; requiring the
#: sentence to name its own subject, for every array without exception, is the structural
#: answer to that whole class rather than to its instances.
SUBJECT_TOKENS: dict[tuple, tuple[str, list[str]]] = {
    ("ceiling1", "families", "astra", "P", "draw1_block", "cluster_ci95"): ("astra", []),
    ("ceiling1", "families", "astra", "C", "draw1_block", "cluster_ci95"): ("astra", []),
    ("ceiling1", "families", "cross", "P", "draw1_block", "cluster_ci95"):
        ("cross", [r"one reading|lifts recall"]),
    ("ceiling1", "families", "cross", "C", "draw1_block", "cluster_ci95"):
        ("cross", [r"false positives|false-positive"]),
    ("ceiling1", "families", "cross", "P", "union_at_kmax_block", "cluster_ci95"):
        ("cross", [r"eight|number to quote"]),
    ("ceiling1", "families", "cross", "C", "union_at_kmax_block", "cluster_ci95"):
        ("cross", [r"eight|false positives|false-positive"]),
    ("ceiling1", "families", "cross", "P", "fit_A_ci95"):
        ("cross", [r"asymptote|extrapolation"]),
    ("ceiling1", "families", "cross", "P", "last_step_gain_block", "cluster_ci95"):
        ("cross", [r"flattened|gained"]),
    ("ceiling1", "families", "self", "P", "draw1_block", "cluster_ci95"):
        ("self", [r"one reading"]),
    ("ceiling1", "families", "self", "P", "union_at_kmax_block", "cluster_ci95"):
        ("self", [r"eight"]),
    ("ceiling1", "families", "self", "C", "union_at_kmax_block", "cluster_ci95"):
        ("self", [r"false-positive|false positives"]),
    ("ceiling1", "families", "self", "P", "fit_A_ci95"): ("self", [r"asymptote"]),
    ("ceiling1", "primary_ceiling1", "P", "ci95"): ("primary", [r"primary outcome"]),
    ("ceiling1", "primary_ceiling1", "P", "raw_diff_ci95"): ("primary", []),
    ("ceiling1", "residual", "all_families", "share_block", "cluster_ci95"):
        ("residual", []),
    ("ceiling1", "residual_classified", "all_families", "cluster_ci95",
     "unexercised-edge"): ("residual", [r"input class|never constructs"]),
    ("ceiling2", "arms", "self-loop", "net_primary", "ci95"): ("self-loop", []),
    ("ceiling2", "arms", "referent-loop", "net_primary", "ci95"): ("referent-loop", []),
    ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "ci95"):
        ("referent-loop", [r"cross-loop"]),
    ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "flag_discordance", "P",
     "ci95"): ("referent-loop", [r"flags|flagged"]),
    ("ceiling2", "contrasts", "referent-loop__vs__cross-loop", "flag_discordance", "all",
     "ci95"): ("referent-loop", [r"pooled"]),
    ("timeout_sensitivity", "residual_registered", "cluster_ci95"):
        ("timeout", [r"registered|110"]),
    ("timeout_sensitivity", "residual_assertion_only", "cluster_ci95"):
        ("timeout", [r"assertion|103"]),
}


def _subject_regexes(path) -> list[str]:
    """Every regex the sentence around a rate bound to `path` must match."""
    family, extra = SUBJECT_TOKENS[tuple(path)]
    return ["|".join(FAMILY_VOCAB[family][0])] + list(extra)


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
                required = (_subject_regexes(interval_path)
                            if tuple(interval_path) in SUBJECT_TOKENS else None)
                if required is None:
                    problems.append(
                        f"[{name}] {match.group('v')!r} is bound to "
                        f"{'.'.join(map(str, interval_path))}, which declares no subject "
                        f"tokens — every bound array must declare them")
                elif required:
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


def test_the_binding_rejects_the_round_eight_reattributions():
    """The eighth review's three edits, committed as fixed tests.

    All three left every test green when they were found: the loop-net arrays carried no
    subject requirement at all, and the asymptote rules accepted generic words. They are
    kept alongside the generated mutation set because a named regression is easier to read
    than a generated one, and because they are the cases that motivated the rule.
    """
    original = REPORT.read_text(encoding="utf-8")
    cases = [
        ("Self-audit changed accuracy by +0.89",
         "Cross-loop changed accuracy by +0.89"),
        ("The shipped cross-vendor auditor's fitted\nasymptote is",
         "Its fitted curve provides a comparison. The self model's fitted asymptote is"),
        ("the `self-loop` arm — the generator's own model\nauditing and revising its own "
         "code — produced no measurable gain",
         "the cross-loop arm produced no measurable gain"),
    ]
    for before, after in cases:
        mutated = original.replace(before, after, 1)
        assert mutated != original, f"the report changed shape: {before[:48]!r}"
        assert _binding_problems(mutated), \
            f"a re-attribution survived the guard: {after[:60]!r}"


def test_the_analysis_files_contain_no_duplicate_definitions():
    """No module may define the same name twice at top level.

    A duplicate silently overrides its twin, so a check can appear to exist while a stale
    copy is what actually runs. This file has had that defect twice — once in the rule
    table, once across eleven functions — and both times it was found by review rather
    than by the suite. The check is committed so it cannot be a third time.
    """
    import ast
    import collections

    offenders = {}
    for name in ("tests/test_report_consistency.py", "tests/test_ceiling_stats.py",
                 "report_ceiling.py", "ceiling/finalise_manifests.py",
                 "ceiling/splice_tables.py", "loop.py", "ceiling.py",
                 "residual_dump.py"):
        path = CODE / name
        if not path.exists():
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        counts = collections.Counter(
            node.name for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)))
        counts.update(
            target.id for node in tree.body if isinstance(node, ast.Assign)
            for target in node.targets if isinstance(target, ast.Name))
        duplicated = {k: v for k, v in counts.items() if v > 1}
        if duplicated:
            offenders[name] = duplicated
    assert not offenders, f"duplicate top-level definitions: {offenders}"


def test_every_bound_rule_declares_a_subject():
    """No bound array may omit its subject tokens, and none may be generic.

    Eight rounds of review each found a rate that could be re-attributed by editing prose,
    and each was fixed as an instance. This is the rule that closes the class: a binding
    without a declared, family-specific subject is a defect in the guard itself.
    """
    undeclared, generic = [], []
    for _pattern, value_path, interval_path, _why in RATE_RULES:
        if interval_path is None:
            continue
        key = tuple(interval_path)
        if key not in SUBJECT_TOKENS:
            undeclared.append(".".join(map(str, key)))
            continue
        family, _extra = SUBJECT_TOKENS[key]
        if not family or family not in FAMILY_VOCAB or not FAMILY_VOCAB[family][0]:
            generic.append(".".join(map(str, key)))
    assert not undeclared, ("bound arrays with no subject declaration:\n"
                            + "\n".join("  " + u for u in sorted(set(undeclared))))
    assert not generic, ("bound arrays whose subject is empty or unknown:\n"
                         + "\n".join("  " + g for g in sorted(set(generic))))


def _reattribute(section_text: str, sentence: str, frm: str, to: str) -> str:
    """That sentence, with every token of family `frm` replaced by family `to`'s phrase."""
    mutated = sentence
    for token in FAMILY_VOCAB[frm][0]:
        mutated = re.sub(token, FAMILY_VOCAB[to][1], mutated, flags=re.I)
    return section_text.replace(sentence, mutated, 1)


def test_generated_reattribution_mutations_all_redden():
    """For EVERY binding rule, rewrite its sentence's subject to each other family in turn
    and require the guard to redden.

    The structural replacement for eight rounds of hand-written counterexamples: the
    mutations are generated from the rule table, so a new binding cannot be added without
    its re-attribution mutations existing. Four properties are asserted:

    1. the unmutated report is clean, so mutations mean something;
    2. every bound rule yields at least one mutation — a rule cannot pass by being
       unmutatable, which is how a too-generic subject would hide;
    3. every mutation reddens;
    4. enough mutations are generated that the table has not quietly shrunk.
    """
    numbers = json.loads(NUMBERS.read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    assert not check_rate_bindings(report, numbers), \
        "the unmutated report must be clean before mutations mean anything"

    survived, unmutatable, total = [], [], 0
    for pattern, _value_path, interval_path, _why in RATE_RULES:
        if interval_path is None:
            continue
        label = ".".join(map(str, interval_path))
        family, _extra = SUBJECT_TOKENS[tuple(interval_path)]
        made_one = False
        for raw_section, section_start in _raw_sections(report).values():
            clean, offsets = _normalise_with_map(raw_section)
            match = re.search(pattern, clean)
            if match is None:
                continue
            lo, hi = _sentence_bounds(clean, match.start("v"))
            raw_lo = section_start + offsets[lo]
            raw_hi = section_start + offsets[hi - 1] + 1
            raw_sentence = report[raw_lo:raw_hi]
            for other in FAMILY_VOCAB:
                if other == family:
                    continue
                mutated = raw_sentence
                for token in FAMILY_VOCAB[family][0]:
                    mutated = re.sub(token, FAMILY_VOCAB[other][1], mutated, flags=re.I)
                if mutated == raw_sentence:
                    continue
                made_one = True
                total += 1
                candidate = report[:raw_lo] + mutated + report[raw_hi:]
                if not check_rate_bindings(candidate, numbers):
                    survived.append(f"{label} survived re-attribution to {other!r}")
            break
        if not made_one:
            unmutatable.append(f"{label}: its sentence contains no token of its declared "
                               f"family {family!r}, so no re-attribution can be generated")
    assert not unmutatable, ("bindings whose subject cannot be mutated:\n"
                             + "\n".join("  " + u for u in sorted(set(unmutatable))))
    assert total > 100, f"only {total} mutations generated; the rule table changed shape"
    assert not survived, ("re-attribution mutations the guard accepted:\n"
                          + "\n".join("  " + s for s in sorted(set(survived))[:15]))


def _raw_sections(text: str) -> dict[str, tuple[str, int]]:
    """Each analysed section as (raw text, its offset in the whole report)."""
    out = {}
    opening = text.split("## What the review changed", 1)[0]
    out["opening"] = (opening, 0)
    marker = "## What this study licenses, and what it does not"
    if marker in text:
        start = text.index(marker)
        rest = text[start:]
        end = rest.find("### Where this sits beside the earlier record")
        out["conclusion"] = (rest[:end if end != -1 else len(rest)], start)
    return out


def _sentence_bounds(clean: str, position: int) -> tuple[int, int]:
    """[start, end) of the sentence containing `position` in normalised text."""
    boundaries = [m.end() for m in
                  re.finditer(r"(?<=[.;])\s+(?=[A-Z(\u201c\"])", clean)]
    start = max([0] + [b for b in boundaries if b <= position])
    after = [b for b in boundaries if b > position]
    return start, (after[0] if after else len(clean))


def _raw_sentence(report: str, flattened_sentence: str) -> str | None:
    """The raw (un-normalised) span of the report corresponding to a flattened sentence.

    Matching is done on a distinctive prefix, then extended to the same word count, so a
    mutation can be applied to the file the guard actually reads.
    """
    words = [w for w in flattened_sentence.split() if w]
    if len(words) < 4:
        return None
    probe = re.escape(words[0]) + r"[\s*`>]*" + r"[\s*`>]*".join(
        re.escape(w) for w in words[1:4])
    match = re.search(probe, report)
    if match is None:
        return None
    tail = report[match.start():]
    end = 0
    seen = 0
    for token in re.finditer(r"\S+", tail):
        seen += 1
        end = token.end()
        if seen >= len(words):
            break
    return tail[:end]


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



def test_the_attribution_counts_match_the_attribution_table():
    """The prose counts beside the attribution table are derived from the table.

    They drifted once already — the table listed ten rows while the sentence said nine and
    "the single exception". A count written beside a table it does not read is a count
    that will drift again.
    """
    corrections = (CODE.parent / "CORRECTIONS.md").read_text(encoding="utf-8")
    section = corrections.split("**25. Who found what, corrected.**", 1)[1]
    section = section.split("**26.", 1)[0]
    rows = [line for line in section.splitlines()
            if line.startswith("| ") and "found by" not in line and "---" not in line]
    reviewer = [r for r in rows if "cross-vendor review" in r]
    author = [r for r in rows if "**the author**" in r]
    numbered = [r for r in rows if not r.startswith("| — ")]
    assert len(rows) == len(reviewer) + len(author), rows
    assert len(numbered) == 9, f"{len(numbered)} numbered rows, prose says nine"
    assert len(reviewer) == 8, f"{len(reviewer)} reviewer rows, prose says eight"
    assert len(author) == 2, f"{len(author)} author rows (item 24 and the beta tail)"
    assert "Eight of the nine numbered corrections" in section, \
        "the sentence no longer states the count the table shows"


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
