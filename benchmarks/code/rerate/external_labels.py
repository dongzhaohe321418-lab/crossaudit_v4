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

#: EvalPlus, `evalplus/eval/_special_oracle.py` (Apache-2.0): the tasks where the benchmark's
#: authors did not compare a candidate to the reference by equality and supplied a comparison
#: rule or a hand-written oracle instead.
#:
#: THIS IS NOT AN EXTERNAL LABEL SET AND IS NOT USED AS ONE. The file documents engineering
#: decisions; it nowhere says "this specification is defective". Reading a bespoke oracle as
#: evidence that the prose did not settle the value is OUR interpretation, and the results
#: report it separately from `RICHTER` and say so. Two further limits, both from the first
#: review of this amendment: a matching task id does not mean the source and this study are
#: talking about the same defect — EvalPlus's entry for `Mbpp/7` concerns set comparison while
#: this study's instance fails on punctuation in tokenisation — and `HumanEval/32`, whose
#: helper merely implements the coefficient convention the task's own prompt already states,
#: is excluded for that reason.
EVALPLUS_SPECIAL_ORACLE = {
    "Mbpp/2": "compared as a set: the prose does not fix the output order",
    "Mbpp/7": "compared as a set: the prose does not fix the output order",
    "Mbpp/111": "compared as a set", "Mbpp/140": "compared as a set",
    "Mbpp/232": "compared as a set", "Mbpp/249": "compared as a set",
    "Mbpp/579": "compared as a set", "Mbpp/769": "compared as a set",
    "Mbpp/581": "hand-written oracle: height read as the perpendicular distance to the apex",
    "Mbpp/558": "hand-written oracle: the two numbers zero-padded to equal length",
}

#: Both sources assert "the specification does not settle this", which is what this study's
#: `ambiguous-oracle` label asserts. Neither asserts the converse, so a task ABSENT from them
#: is not evidence of anything: Richter lists examples, not an exhaustive audit, and EvalPlus
#: wrote an oracle only where it had to. The join is therefore one-sided by construction and
#: can bound concordance, never the rate.
CONCORDANT_WITH = "ambiguous-oracle"
