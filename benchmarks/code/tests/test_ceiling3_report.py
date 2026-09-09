"""RESULTS-CEILING3.md's figures are records/ceiling3/numbers.json's figures.

Bound (and only these): §1's table cells for the two new families (k/n, rate, Wilson,
cluster, single-draw P and C); the primary, H18a, H18c (mean-over-draws and K = 4) and
their intervals; blocked-by-none and mentioned-by-none with both intervals; the
any-finding table for `self-strong`; the mixed curve; the prompt-digest count; the cost total.
"""

from __future__ import annotations

import glob
import json
from pathlib import Path

CODE = Path(__file__).resolve().parent.parent
NUMBERS = CODE / "records" / "ceiling3" / "numbers.json"
RESULTS = CODE / "RESULTS-CEILING3.md"


def _n() -> dict:
    return json.loads(NUMBERS.read_text(encoding="utf-8"))


def _t() -> str:
    return RESULTS.read_text(encoding="utf-8")


def _row(label: str) -> list[str]:
    for line in _t().splitlines():
        if line.startswith("| " + label):
            return [c.strip() for c in line.strip("|").split("|")]
    raise AssertionError(label)


def _pct(x: float) -> str:
    return f"{100 * x:.1f}"


def test_the_new_families_table_cells_are_bound():
    n = _n()["families"]
    for label, fam in (("**`self-strong`", "self-strong"), ("**`self-frontier`", "self-frontier")):
        cells = _row(label)
        e = n[fam]
        p, c = e["P"]["union_at_kmax"], e["C"]["union_at_kmax"]
        assert cells[1].strip("*") == str(e["k_max"])
        assert cells[2] == f"**{p['k']}/{p['n']} = {_pct(p['rate'])}%**"
        assert cells[3] == f"{_pct(p['wilson95'][0])}–{_pct(p['wilson95'][1])}"
        assert cells[4] == f"{_pct(p['cluster_ci95'][0])}–{_pct(p['cluster_ci95'][1])}"
        assert cells[5] == f"{c['k']}/{c['n']} = {_pct(c['rate'])}%"
        assert cells[6] == f"{_pct(c['wilson95'][0])}–{_pct(c['wilson95'][1])}"
        assert cells[7] == f"{_pct(c['cluster_ci95'][0])}–{_pct(c['cluster_ci95'][1])}"
        assert cells[8] == f"{_pct(e['P']['single_draw_mean'])}% / {_pct(e['C']['single_draw_mean'])}%"


def test_the_contrasts_are_bound():
    n = _n(); t = _t()
    pr = n["primary_H18b_self_strong_minus_cross_P"]
    assert f"P = **{pr['difference_points']:.1f} points, cluster 95% [{pr['cluster_ci95_points'][0]:.1f}, {pr['cluster_ci95_points'][1]:.1f}]**" in t.replace("−", "-")
    assert f"{pr['a_only']} instances flagged by `self-strong`\n  only, {pr['b_only']} by `cross` only" in t
    ha = n["H18a_self_strong_minus_self_P"]
    assert f"P at K = 8 = **{ha['difference_points']:.1f} points [{ha['cluster_ci95_points'][0]:.1f}, {ha['cluster_ci95_points'][1]:.1f}]**" in t.replace("−", "-")
    assert f"sign-flip\n  p = {ha['signflip']['p']:.3f}" in t
    hc = n["H18c_frontier_minus_astra_P_k1_mean_over_draws"]
    assert f"`self-frontier` − `astra` on P = **{hc['difference_points']:.1f}\n  points [{hc['cluster_ci95_points'][0]:.1f}, {hc['cluster_ci95_points'][1]:.1f}]**".replace("-", "−").replace("−−", "−") in t or \
           f"P = **{hc['difference_points']:.1f}\n  points [{hc['cluster_ci95_points'][0]:.1f}, {hc['cluster_ci95_points'][1]:.1f}]**" in t.replace("−", "-")
    hk = n["H18c_frontier_minus_astra_P_kmax"]
    assert f"K = 4 unions: {hk['difference_points']:.1f} [{hk['cluster_ci95_points'][0]:.1f}, {hk['cluster_ci95_points'][1]:.1f}]" in t.replace("−", "-")


def test_the_never_counts_and_the_any_finding_table_are_bound():
    n = _n(); t = _t()
    nv = n["never_flagged_by_any_family"]
    assert (f"{nv['k']} of {nv['n']} defects = {_pct(nv['rate'])}% (Wilson {_pct(nv['wilson95'][0])}–{_pct(nv['wilson95'][1])}; cluster\n"
            f"  {_pct(nv['cluster_ci95'][0])}–{_pct(nv['cluster_ci95'][1])})") in t
    na = n["EXPLORATORY_any_finding_rule"]["never_any_finding_by_any_family_P"]
    assert (f"{na['k']} of {na['n']} = {_pct(na['rate'])}%** (Wilson {_pct(na['wilson95'][0])}–{_pct(na['wilson95'][1])}; cluster\n"
            f"{_pct(na['cluster_ci95'][0])}–{_pct(na['cluster_ci95'][1])})") in t
    e = n["EXPLORATORY_any_finding_rule"]["families"]["self-strong"]
    cells = _row("**`self-strong` (Sonnet)** | 8 | **")
    p, c = e["P"]["union_at_kmax"], e["C"]["union_at_kmax"]
    assert cells[2] == f"**{_pct(p['rate'])}%**" and cells[3] == f"{_pct(p['wilson95'][0])}–{_pct(p['wilson95'][1])}"
    assert cells[4] == f"{_pct(p['cluster_ci95'][0])}–{_pct(p['cluster_ci95'][1])}" and cells[5] == f"{_pct(e['P']['single_draw_mean'])}%"
    assert cells[6] == f"{_pct(c['rate'])}%" and cells[7] == f"{_pct(c['cluster_ci95'][0])}–{_pct(c['cluster_ci95'][1])}"


def test_mixed_prompt_digests_and_cost_are_bound():
    n = _n(); t = _t()
    m = n["mixed_cross_self_strong"]
    assert "`mixed` (K/2 `cross` + K/2 `self-strong`): " + ", ".join(_pct(m[f"K={k}"]) for k in (2, 4, 6, 8)) + "% at K = 2, 4, 6, 8" in t
    s2 = {}
    for line in (CODE / "records" / "study2" / "arm-holistic-cross.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line); s2[r["instance_id"]] = r.get("prompt_sha256")
    match = mism = 0
    for f in glob.glob(str(CODE / "records" / "ceiling3" / "cache" / "holistic__self-*__d?.jsonl")):
        for line in Path(f).read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("prompt_sha256") == s2.get(r["instance_id"]): match += 1
                else: mism += 1
    assert f"{match:,} of their {match + mism:,}\nreadings carry the same prompt digest" in t
    assert f"the other {mism} are the product's bounded repair prompts" in t
    total = sum(v["ledger_usd"] for v in n["reply_format_secondary"].values() if v.get("ledger_usd") is not None)
    assert f"**Cost**: ${total:.2f} from the twelve project ledgers" in t
    calls = sum(v["ledger_calls"] for v in n["reply_format_secondary"].values())
    assert f"{calls:,} calls" in t
