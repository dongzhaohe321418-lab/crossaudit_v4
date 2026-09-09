"""Post-hoc numbers for RESULTS-TESTGEN.md, labelled EXPLORATORY wherever they appear.

Not preregistered: the union of the shipped auditor with the ORACLE-VALIDATED arm (an
upper bound, since the product has no canonical solution), and the unique-test view of the
wrong-test rate. Reads the committed records only; changes nothing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import explore  # noqa: E402

rows = [json.loads(l) for l in (HERE.parent / "records/testgen/rows.jsonl").read_text().splitlines() if l.strip()]
suites = json.loads((HERE.parent / "records/testgen/suites.json").read_text())


def block(sub, flag):
    k = sum(1 for r in sub if flag(r)); n = len(sub)
    lo, hi = explore.wilson(k, n)
    return f"{k}/{n} = {100*k/n:.1f}% (Wilson {100*lo:.1f}–{100*hi:.1f}%)"


for half in ("confirm", "explore"):
    sub = [r for r in rows if r["half"] == half]
    P = [r for r in sub if r["stratum"] == "P"]; C = [r for r in sub if r["stratum"] == "C"]
    print(f"[{half}] hc ∪ testgen-validated (EXPLORATORY, oracle-bounded):",
          "P", block(P, lambda r: r["hc_flagged"] or r["flagged_validated"]),
          "C", block(C, lambda r: r["hc_flagged"] or r["flagged_validated"]))
    print(f"[{half}] validated-only P (not hc):", sum(1 for r in P if r["flagged_validated"] and not r["hc_flagged"]),
          " hc-only P:", sum(1 for r in P if r["hc_flagged"] and not r["flagged_validated"]),
          " both:", sum(1 for r in P if r["hc_flagged"] and r["flagged_validated"]))
    print(f"[{half}] testgen flags that only a WRONG test produced (P / C):",
          sum(1 for r in P if r["flagged_testgen"] and not r["flagged_validated"] and not r["canonical_unusable"]),
          "/", sum(1 for r in C if r["flagged_testgen"] and not r["flagged_validated"] and not r["canonical_unusable"]))

# unique tests: one suite per problem; a test wrong on the canonical is wrong once
wrong_by_problem = {}
for r in rows:
    if not r["canonical_unusable"]:
        wrong_by_problem.setdefault(r["problem_id"], set()).update(r["failed_canonical"])
n_unique = sum(s["n_tests"] for s in suites.values())
n_wrong = sum(len(v) for v in wrong_by_problem.values())
print(f"unique tests {n_unique} over {len(suites)} problems; wrong on the canonical {n_wrong} "
      f"= {100*n_wrong/n_unique:.1f}%; problems with ≥1 wrong test "
      f"{sum(1 for v in wrong_by_problem.values() if v)}/{len(suites)}")
print("suites with zero tests:", sum(1 for s in suites.values() if s["n_tests"] == 0),
      " tokens out mean:", round(sum(s["output_tokens"] for s in suites.values()) / len(suites)))
