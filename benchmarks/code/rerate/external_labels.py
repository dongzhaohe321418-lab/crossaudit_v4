"""Study 21 Amendment 3 — the third-party material this study's labels are checked against,
transcribed with its provenance so anyone can re-derive the join.

**One of these is an external label set and the other is not.** `RICHTER` is a published list
of task specifications its authors judged defective, and it alone is the external check.
`EVALPLUS_SPECIAL_ORACLE` is a list of engineering decisions in a benchmark's test harness;
reading it as evidence about specifications is THIS STUDY'S interpretation, and it is reported
separately and labelled as such wherever it appears. Neither labels an instance — both are
per task — which is why the join is by task id and why the outcome is a concordance, not a rate.

On chronology: this study's labels were committed at d98f0c1, 3aa97aa and e654452, and the
earliest external file on this machine was created after all three. Those are commit times and
untracked-file creation times. They establish that order and nothing else; they cannot show
what a rater knew, and neither source is private.
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

#: `RICHTER` asserts "this specification is defective", which is what this study's
#: `ambiguous-oracle` label asserts; that is the concordance. `EVALPLUS_SPECIAL_ORACLE` asserts
#: nothing about specifications at all, and is joined only so the reader can see what this
#: study's own reading of it would give. Neither asserts the converse, so a task ABSENT from
#: either is not evidence of anything: Richter gives examples, not an exhaustive audit, and
#: EvalPlus wrote an oracle only where its harness needed one. The join is one-sided by
#: construction and can bound concordance, never the rate.
CONCORDANT_WITH = "ambiguous-oracle"
