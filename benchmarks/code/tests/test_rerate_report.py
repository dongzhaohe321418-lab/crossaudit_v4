"""RESULTS-RERATE.md's figures are the records' figures.

Bound, and only these: the spliced table block (byte for byte against records/rerate/tables.md);
the consensus ambiguous-oracle and unexercised-edge counts on the residual and the kill's
firing; the agreement count and κ; the prior-category split of the consensus-ambiguous
instances; Amendment 1's secondary and the post-hoc category split, the flagged-sheet agreement and the retest; the label files'
row counts and label vocabulary; and that the report script reproduces numbers.json.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import report_rerate as rr  # noqa: E402

RESULTS = (HERE / "RESULTS-RERATE.md").read_text(encoding="utf-8")
FLAT = " ".join(RESULTS.split())   # soft wraps joined, for sentences that may wrap anywhere
NUMBERS = json.loads((HERE / "records" / "rerate" / "numbers.json").read_text(encoding="utf-8"))
TABLES = (HERE / "records" / "rerate" / "tables.md").read_text(encoding="utf-8")


def test_tables_are_spliced_byte_for_byte():
    block = RESULTS.split("<!-- tables:begin -->\n", 1)[1].split("<!-- tables:end -->", 1)[0]
    assert block == TABLES


def test_report_reproduces_numbers():
    fresh = rr.build()
    assert json.dumps(fresh, sort_keys=True) == json.dumps(NUMBERS, sort_keys=True)
    assert rr.render_tables(NUMBERS) == TABLES


def test_kill_and_counts_are_quoted_from_numbers():
    k = NUMBERS["kill"]
    assert k["fires"] is True
    assert f"consensus `ambiguous-oracle` is {k['ambiguous']} of 57" in FLAT
    assert f"consensus `unexercised-edge` is {k['edge']} of 57" in FLAT
    prior = NUMBERS["prior_classification_of_consensus_ambiguous"]
    assert f"Of the {k['ambiguous']}, ceiling 1's classification had called {prior['unexercised-edge']} `unexercised-edge` and {prior['spec-misreading']} `spec-misreading`" in FLAT


def test_agreement_is_quoted_from_numbers():
    a = NUMBERS["agreement"]
    assert f"Agreement {a['agree']} of {a['n']} with κ {a['kappa']:.3f} on the residual sheet" in FLAT


def test_the_secondary_and_the_post_hoc_split_are_quoted_from_numbers():
    e = NUMBERS["oracle_clean_secondary"]
    assert f"consensus is {e['a_f']} `ambiguous-oracle`" in RESULTS
    assert f"the oracle-clean denominator is {e['P_clean']} instances, of which {e['flagged_clean']} were flagged — union recall {e['recall']:.1f}% [{e['cluster_ci'][0]:.1f}, {e['cluster_ci'][1]:.1f}] against the registered {e['union_recall_registered']:.1f}%" in FLAT
    bc = NUMBERS["recall_by_consensus_category_POST_HOC"]
    ue, am = bc["unexercised-edge"], bc["ambiguous-oracle"]
    assert f"of the {ue['n']} P instances both raters call spec-determined-and-unexercised, the twenty draws flagged {ue['count']}; of the {am['n']} both call oracle-defined, {am['count']}." in FLAT
    af, rt = NUMBERS["agreement_flagged"], NUMBERS["retest_on_the_11_overlapping_instances"]
    assert f"{af['agree']} of {af['n']} with κ {af['kappa']:.3f} on the flagged sheet" in FLAT
    assert rt["n"] == 11 and rt["L1_same"] == rt["L2_same"] == 11


def test_label_files_are_complete_and_in_vocabulary():
    for name, n in (("L1.csv", 68), ("L2.csv", 68), ("L1-flagged.csv", 53), ("L2-flagged.csv", 53)):
        with open(HERE / "records" / "rerate" / name, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == n
        assert {r["label"] for r in rows} <= set(rr.CATEGORIES)
        assert len({r["id"] for r in rows}) == n


def test_no_percentage_in_prose_is_quoted_without_the_tables():
    prose = re.sub(r"<!-- tables:begin -->.*<!-- tables:end -->", "", RESULTS, flags=re.S)
    rates = re.findall(r"\d+\.\d%", prose)
    assert set(rates) <= {"69.0%", "48.2%"}, rates
