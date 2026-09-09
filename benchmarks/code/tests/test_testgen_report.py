"""RESULTS-TESTGEN.md says what records/testgen/numbers.json says — the figures, not the prose.

Round 1 of the review found the report drifting from its records (a cost ratio, a residual
join, an error count). Each figure quoted below is read from the results file and compared
with the number the report script wrote, so a later edit to either shows up red.

WHAT IS BOUND — this list is the claim RESULTS §4 makes, and the tests below check exactly
it: §1's table (six cells per arm); the decision line (HOLDS, 8/6, McNemar, Δ, its
bootstrap, the sign-flip p, the 4-then-5 bar); "the same problem in both batches"; "All
three C instances"; the residual counts (8 → 4/1/3, 7 → 3/1/3, 29 of 44, 68 classified);
the overlap 7/7/4; the exploratory union with its Wilson and hc's 5/74; "two of the seven";
the explore-half line; the suite totals (222, 290, $1.77, 1,199 from suites.json, mean,
min, max, one empty); the wrong-test figures (45 of 1,188, its intervals, 11 unknown, 32 of
221, one problem unknown, 70 of 1,545); the timeout and pre-collector counts; the cost
figures ($0.0061, hc's $0.0069, "12% less", 1.3 instances per problem); the F stratum line.
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


def _rows() -> list[dict]:
    return [json.loads(l) for l in (CODE / "records" / "testgen" / "rows.jsonl").read_text().splitlines() if l.strip()]


WORDS = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
         8: "eight", 9: "nine"}


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
        clo, chi = c["wilson"]
        assert cells[5] == f"{100 * clo:.1f}–{100 * chi:.1f}%", (label, cells[5])


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
    # the two-instance margin: both testgen-only-and-not-validated P rows share a problem
    rows = _rows()
    margin = [r for r in rows if r["half"] == "confirm" and r["stratum"] == "P"
              and r["flagged_testgen"] and not r["flagged_validated"]]
    arms = _numbers()["arms"]
    assert len(margin) == arms["testgen"]["confirm"]["P"]["k"] - arms["testgen-validated"]["confirm"]["P"]["k"] == 2
    assert len({r["problem_id"] for r in margin}) == 1
    assert "two instances of the margin are the same problem in both batches" in t


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
    # bound in its substantive sentence, not merely anywhere in the file (round 5)
    assert (f"${s['cost_usd_per_instance_amortised']:.4f} per instance amortised, against `hc`'s "
            f"${s['hc_cost_usd_per_instance_explore_leaderboard']:.4f}\n  on the explore leaderboard") in t
    assert f"{100 * s['cost_ratio_testgen_over_hc']:.0f}% of the reading auditor's cost" in t
    assert f"${s['cost_usd_generation_total']:.2f} for {s['problems_with_suite']} calls" in t


def test_the_explore_half_line_the_f_stratum_and_the_suite_totals_match():
    n = _numbers()
    t = _text()
    e = {arm: n["arms"][arm]["explore"] for arm in n["arms"]}
    assert (f"`hc` {e['hc']['P']['k']}/{e['hc']['P']['n']} P, {e['hc']['C']['k']}/{e['hc']['C']['n']} C; "
            f"`testgen`\n{e['testgen']['P']['k']}/{e['testgen']['P']['n']}, {e['testgen']['C']['k']}/{e['testgen']['C']['n']}; "
            f"`testgen-validated` {e['testgen-validated']['P']['k']}/{e['testgen-validated']['P']['n']}, "
            f"{e['testgen-validated']['C']['k']}/{e['testgen-validated']['C']['n']}; "
            f"`hc ∪ testgen` {e['hc_u_testgen']['P']['k']}/{e['hc_u_testgen']['P']['n']}, "
            f"{e['hc_u_testgen']['C']['k']}/{e['hc_u_testgen']['C']['n']}.") in t
    f = n["arms"]["testgen"]["confirm"]["F"]
    lo, hi = f["wilson"]
    assert f"**F stratum** (confirm, {f['n']}): `testgen` {f['k']}/{f['n']} = {100 * f['rate']:.1f}% (Wilson {100 * lo:.1f}–{100 * hi:.1f}%)" in t
    s = n["secondaries"]
    tp = s["tests_per_problem"]
    suites = json.loads((CODE / "records" / "testgen" / "suites.json").read_text(encoding="utf-8"))
    n_tests = sum(v["n_tests"] for v in suites.values())
    assert (f"({s['problems_with_suite']} problems, {n['n_rows']} instances, both halves; "
            f"${s['cost_usd_generation_total']:.2f}; {n_tests:,}\ntests, mean {tp['mean']:.1f} per problem, "
            f"min {tp['min']}, max {tp['max']}; none uncompilable; {'one' if tp['zero'] == 1 else tp['zero']} suite empty)") in t
    assert s["uncompilable_total"] == 0


def test_the_overlap_counts_and_the_exploratory_union_match_the_records():
    """The 7/7/4 overlap and the oracle-bounded union are computed here from rows.jsonl, as
    testgen/exploratory.py computes them, and compared with the prose."""
    rows = [json.loads(l) for l in (CODE / "records" / "testgen" / "rows.jsonl").read_text().splitlines() if l.strip()]
    conf_p = [r for r in rows if r["half"] == "confirm" and r["stratum"] == "P"]
    conf_c = [r for r in rows if r["half"] == "confirm" and r["stratum"] == "C"]
    v_only = sum(1 for r in conf_p if r["flagged_validated"] and not r["hc_flagged"])
    h_only = sum(1 for r in conf_p if r["hc_flagged"] and not r["flagged_validated"])
    both = sum(1 for r in conf_p if r["hc_flagged"] and r["flagged_validated"])
    t = _text()
    assert (f"`testgen-validated` flags {v_only} P instances `hc` misses, `hc` flags {h_only} it misses, and\n"
            f"  {both} are flagged by both.") in t
    up = sum(1 for r in conf_p if r["hc_flagged"] or r["flagged_validated"])
    uc = sum(1 for r in conf_c if r["hc_flagged"] or r["flagged_validated"])
    import math
    z = 1.959963984540054
    def wilson(k, n):
        p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
        h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return max(0.0, c - h), min(1.0, c + h)
    lo, hi = wilson(up, len(conf_p))
    assert (f"`hc ∪ testgen-validated` is {up}/{len(conf_p)} = {100 * up / len(conf_p):.1f}% "
            f"(Wilson {100 * lo:.1f}–{100 * hi:.1f}%) at `hc`'s own\n  {uc}/{len(conf_c)}") in t


def test_the_residual_counts_the_error_counts_and_the_cost_reading_are_bound():
    n = _numbers()
    s = n["secondaries"]
    t = _text()
    nh = s["confirm_P_not_flagged_by_hc_by_residual_class"]
    total_not_hc = sum(nh.values())
    tg = s["confirm_P_testgen_only_by_residual_class"]
    vo = s["confirm_P_validated_only_by_residual_class"]
    assert (f"The residual behind\n  `hc` on this half is {nh['unexercised-edge']} `unexercised-edge` of {total_not_hc}; "
            f"execution reached {tg['unexercised-edge']} of them, {vo['unexercised-edge']} with a\n  correct test.") in t
    assert f"{s['canonical_unusable_rows']} canonical run timed out" in t
    assert f"{s['candidate_timeouts']} candidate runs timed out" in t
    assert f"{s['candidate_died_before_collector']} other candidate\n  runs died before the collector" in t
    less = round(100 * (1 - s["cost_ratio_testgen_over_hc"]))
    assert f"about {less}% less" in t
    per_problem = n["n_rows"] / s["problems_with_suite"]
    assert f"over only\n  {per_problem:.1f} instances per problem" in t
    c = n["arms"]["testgen"]["confirm"]["C"]
    assert f"All {WORDS[c['k']]} C instances `testgen` flagged" in t
    union_c = n["arms"]["hc_u_testgen"]["confirm"]["C"]["k"]
    rows = _rows()
    testgen_only_fp = [r for r in rows if r["half"] == "confirm" and r["stratum"] == "C"
                       and r["flagged_testgen"] and r["hc_flagged"] is False]
    assert all(not r["flagged_validated"] for r in testgen_only_fp)   # each is a wrong test
    assert f"{WORDS[len(testgen_only_fp)]} of the {WORDS[union_c]} are `testgen`'s wrong tests" in t
    assert f"({WORDS[s['canonical_unusable_rows']]} problem unknown)" in t
    assert f"classified {s['confirm_P_residual_classes_available']} instances)" in t
    w = s["wrong_tests"]
    assert f"{w['dropped_by_validation_instance_rows']} of {w['of_test_applications']:,} test applications" in t
    w = s["wrong_tests"]
    problems_classifiable = s["problems_with_suite"] - s["canonical_unusable_rows"]
    assert f"{w['problems_with_a_wrong_test']} of\n  the {problems_classifiable} classifiable problems have at least one wrong test" in t


def test_exploratory_py_prints_what_the_prose_quotes():
    """The exploratory script is run, and its lines are compared with the prose."""
    import subprocess, sys
    out = subprocess.run([sys.executable, str(CODE / "testgen" / "exploratory.py")],
                         capture_output=True, text=True, check=True).stdout
    t = _text()
    conf_union = [l for l in out.splitlines() if l.startswith("[confirm] hc ∪ testgen-validated")][0]
    k_n, pct = conf_union.split("P ")[1].split(" = ")[0], conf_union.split(" = ")[1].split("%")[0]
    assert f"`hc ∪ testgen-validated` is {k_n} = {pct}%" in t
    overlap = [l for l in out.splitlines() if l.startswith("[confirm] validated-only P")][0]
    nums = [int(x) for x in overlap.replace(":", " ").split() if x.isdigit()]
    assert f"`testgen-validated` flags {nums[0]} P instances `hc` misses, `hc` flags {nums[1]} it misses, and\n  {nums[2]} are flagged by both." in t
    uniq = [l for l in out.splitlines() if l.startswith("unique tests")][0]
    import re
    m = re.search(r"unique tests (\d+) over (\d+) problems; (\d+) unclassifiable .*; wrong on the canonical (\d+)/(\d+) = ([\d.]+)%; problems with ≥1 wrong test (\d+)/(\d+)", uniq)
    assert m, uniq
    total, n_problems, unknown, wrong, classifiable, pct, wp, cp = m.groups()
    assert f"{wrong} of the {int(classifiable):,} unique tests" in t
    assert f"({pct}%;" in t
    assert f"the {unknown} tests of the one suite" in t
    assert f"{wp} of\n  the {cp} classifiable problems" in t
    uc = conf_union.split("C ")[1].split(" = ")[0]
    assert f"at `hc`'s own\n  {uc}" in t
    wrong_only = [l for l in out.splitlines() if l.startswith("[confirm] testgen flags that only a WRONG test produced")][0]
    p_only, c_only = [int(x) for x in wrong_only.split(":")[1].replace("/", " ").split()]
    assert f"All {WORDS[c_only]} C instances" in t and p_only == 2
