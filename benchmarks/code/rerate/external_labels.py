"""Study 21 Amendment 3 — the external, third-party specification labels this study is
checked against, transcribed with their provenance so anyone can re-derive the join.

Neither source was consulted before this study's own labels were committed; the git history
fixes that order (`records/rerate/L1.csv` at d98f0c1, `L1-flagged.csv` at 3aa97aa, both before
the first external file was fetched). Neither source was produced for this study, and neither
labels an instance: both label the TASK's specification, which is why the join is by task id
and why the outcome is a concordance, not a rate.
"""

from __future__ import annotations

#: Richter & Papadakis, "Underspecification does not imply Incoherence: The Risks of Semantic
#: Collapse in Coding Models", arXiv:2607.01953, §1 footnotes 1-3, verbatim:
#:   "Examples of Ambiguity: MBPP/294, MBPP/102, MBPP/410, MBPP/576"
#:   "Incompletness: MBPP/7, MBPP/137, MBPP/244, MBPP/261, MBPP/278"
#:   "Contradictions: MBPP/459, MBPP/638, MBPP/639"
#: Their unit is the task description; all three classes assert a defect in the prose.
RICHTER = {
    "Mbpp/294": "ambiguity", "Mbpp/102": "ambiguity", "Mbpp/410": "ambiguity",
    "Mbpp/576": "ambiguity",
    "Mbpp/7": "incompleteness", "Mbpp/137": "incompleteness", "Mbpp/244": "incompleteness",
    "Mbpp/261": "incompleteness", "Mbpp/278": "incompleteness",
    "Mbpp/459": "contradiction", "Mbpp/638": "contradiction", "Mbpp/639": "contradiction",
}

#: EvalPlus, `evalplus/_special_oracle.py` (Apache-2.0), the tasks for which the benchmark's
#: own authors could not test the candidate against the reference implementation and wrote a
#: bespoke oracle instead. Each entry is an engineering record that the prose did not settle
#: the expected value. `set_eq` are the tasks whose output ORDER the prose leaves open; the
#: rest carry a hand-written oracle whose docstring states the interpretation chosen.
EVALPLUS_SPECIAL_ORACLE = {
    "Mbpp/2": "set_eq", "Mbpp/7": "set_eq", "Mbpp/111": "set_eq", "Mbpp/140": "set_eq",
    "Mbpp/232": "set_eq", "Mbpp/249": "set_eq", "Mbpp/579": "set_eq", "Mbpp/769": "set_eq",
    "Mbpp/581": "interpretation chosen: height is the perpendicular distance to the apex",
    "Mbpp/558": "interpretation chosen: the two numbers are zero-padded to equal length",
    "HumanEval/32": "interpretation chosen: the polynomial's coefficient convention",
}

#: Both sources assert "the specification does not settle this", which is what this study's
#: `ambiguous-oracle` label asserts. Neither asserts the converse, so a task ABSENT from them
#: is not evidence of anything: Richter lists examples, not an exhaustive audit, and EvalPlus
#: wrote an oracle only where it had to. The join is therefore one-sided by construction and
#: can bound concordance, never the rate.
CONCORDANT_WITH = "ambiguous-oracle"
