"""RESULTS-TESTGEN.md says what records/testgen/numbers.json says — the figures, not the prose.

Round 1 of the review found the report drifting from its records (a cost ratio, a residual
join, an error count). Each figure quoted below is read from the results file and compared
with the number the report script wrote, so a later edit to either shows up red.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

CODE = Path(__file__).resolve().parent.parent
RESULTS = CODE / "RESULTS-TESTGEN.md"
NUMBERS = CODE / "records" / "testgen" / "numbers.json"


def _numbers() -> dict:
    return json.loads(NUMBERS.read_text(encoding="utf-8"))


def _text() -> str:
    return RESULTS.read_text(encoding="utf-8")


def _table_row(label: str) -> list[str]:
    for line in _text().splitlines():
        if line.startswith("| " + label):
            return [c.strip() for c in line.strip("|").split("|")]
    raise AssertionError(f"no table row for {label}")


def test_the_arm_table_matches_numbers_json():
    n = _numbers()["arms"]
    for label, arm in (("`hc`", "hc"), ("`testgen`", "testgen"),
                       ("`testgen-validated`", "testgen-validated"),
                       ("`hc ∪ testgen`", "hc_u_testgen")):
        cells = _table_row(label)
        p, c = n[arm]["confirm"]["P"], n[arm]["confirm"]["C"]
        assert cells[1].startswith(f"{p['k']}/{p['n']} = {100 * p['rate']:.1f}%"), (label, cells[1])
        assert cells[4].startswith(f"{c['k']}/{c['n']} = {100 * c['rate']:.1f}%"), (label, cells[4])
        lo, hi = p["wilson"]
        assert cells[2] == f"{100 * lo:.1f}–{100 * hi:.1f}%", (label, cells[2])
        blo, bhi = p["bootstrap_problem_cluster"]
        assert cells[3] == f"{100 * blo:.1f}–{100 * bhi:.1f}%", (label, cells[3])


def test_the_decision_and_paired_figures_match():
    d = _numbers()["decision"]
    t = _text()
    assert f"H16 {d['H16']} by the preregistered rule" in t
    assert f"flags {d['paired_P_testgen_only']} that `hc` does not and misses {d['paired_P_hc_only']}" in t
    assert f"McNemar p = {d['mcnemar_exact_p']:.2f}" in t
    assert f"Δ recall = +{d['delta_recall_points']:.1f} points" in t
    lo, hi = d["delta_recall_problem_cluster_bootstrap_points"]
    assert f"{lo:.1f} to +{hi:.1f} points".replace("-", "\u2212") in t   # the prose uses a minus sign
    sf = d["delta_recall_signflip"]
    assert f"sign-flip test\np = {sf['p']:.2f} ({sf['n_clusters']} problems, {sf['n_nonzero_clusters']} with a non-zero change" in t
    assert f"at most {d['fp_objective_max_instances']} instances" in t
    assert f"one\nmore, {d['fp_bar_instances']})" in t


def test_the_secondaries_match():
    s = _numbers()["secondaries"]
    t = _text()
    w = s["wrong_tests"]
    assert f"{w['unique_wrong']} of the {w['unique_classifiable']:,} unique tests" in t
    lo, hi = w["unique_wilson"]
    assert f"({100 * w['unique_rate']:.1f}%;\n  Wilson {100 * lo:.1f}–{100 * hi:.1f}%" in t
    blo, bhi = w["unique_bootstrap_problem_cluster"]
    assert f"bootstrap {100 * blo:.1f}–{100 * bhi:.1f}%" in t
    assert f"the {w['unique_unknown_canonical_timed_out']} tests of the one suite" in t
    assert f"{w['problems_with_a_wrong_test']} of\n  {s['problems_with_suite']} problems have at least one wrong test" in t
    assert f"{w['dropped_by_validation_instance_rows']} of {w['of_test_applications']:,} test applications" in t
    assert f"{s['candidate_timeouts']} candidate runs timed out" in t
    assert f"{s['candidate_died_before_collector']} other candidate\n  runs died before the collector" in t
    tg = s["confirm_P_testgen_only_by_residual_class"]
    assert (f"Of the {s['confirm_P_flagged_by_testgen_only']} `testgen`-only flags, "
            f"{tg.get('unexercised-edge', 0)} are the ceiling study's\n  `unexercised-edge` class, "
            f"{tg.get('spec-misreading', 0)} `spec-misreading`, {tg.get('unclassified', 0)} outside") in t
    vo = s["confirm_P_validated_only_by_residual_class"]
    assert (f"of the {s['confirm_P_validated_only']} `validated`-only flags, "
            f"{vo.get('unexercised-edge', 0)} / {vo.get('spec-misreading', 0)} / {vo.get('unclassified', 0)}") in t
    assert f"${s['cost_usd_per_instance_amortised']:.4f} per instance amortised" in t
    assert f"`hc`'s ${s['hc_cost_usd_per_instance_explore_leaderboard']:.4f}" in t
    assert f"{100 * s['cost_ratio_testgen_over_hc']:.0f}% of the reading auditor's cost" in t
    assert f"${s['cost_usd_generation_total']:.2f} for {s['problems_with_suite']} calls" in t
