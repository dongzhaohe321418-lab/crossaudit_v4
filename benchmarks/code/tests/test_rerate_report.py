"""RESULTS-RERATE.md's figures are the records' figures.

Bound, and only these: the spliced table block (byte for byte against records/rerate/tables.md);
the consensus ambiguous-oracle and unexercised-edge counts on the residual and the kill's
firing; the agreement count and κ; the prior-category split of the consensus-ambiguous
instances; the registered and oracle-clean recalls in the exploratory table; the label files'
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
    assert f"consensus `ambiguous-oracle` is {k['ambiguous']} of 57" in RESULTS
    assert f"consensus\n`unexercised-edge` is {k['edge']} of 57" in RESULTS
    prior = NUMBERS["prior_classification_of_consensus_ambiguous"]
    assert f"Of the {k['ambiguous']}, ceiling 1's classification had\ncalled {prior['unexercised-edge']} `unexercised-edge` and {prior['spec-misreading']} `spec-misreading`" in RESULTS


def test_agreement_is_quoted_from_numbers():
    a = NUMBERS["agreement"]
    assert f"agreed on {a['agree']} of {a['n']} with κ {a['kappa']:.3f}" in RESULTS


def test_exploratory_recalls_are_quoted_from_numbers():
    e = NUMBERS["exploratory_oracle_clean"]
    assert f"the {e['union_recall_oracle_clean']:.1f}% moves; the registered {e['union_recall_registered']:.1f}% is the quotable recall" in RESULTS


def test_label_files_are_complete_and_in_vocabulary():
    for name in ("L1.csv", "L2.csv"):
        with open(HERE / "records" / "rerate" / name, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == 68
        assert {r["label"] for r in rows} <= set(rr.CATEGORIES)
        assert len({r["id"] for r in rows}) == 68


def test_no_percentage_in_prose_is_quoted_without_the_tables():
    prose = re.sub(r"<!-- tables:begin -->.*<!-- tables:end -->", "", RESULTS, flags=re.S)
    rates = re.findall(r"\d+\.\d%", prose)
    assert set(rates) <= {"80.3%", "48.2%"}, rates
