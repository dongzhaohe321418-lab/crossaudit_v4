# Study 21 — re-rating the residual with the oracle question asked first

Preregistered on `study/residual-rerate` **before any label is written**, at the commit that
adds this file. Binding: ceiling 1 §1.5 (the residual and its categories), `RESULTS-CEILING.md`
(the residual classification: 68 instances, one rater, `timeout > unexercised-edge >
spec-misreading > wrong-algorithm > ambiguous-oracle > other`, no κ), the gap memo of
2026-09-10 (objection A2: `ambiguous-oracle` was unreachable under that precedence, and the
report's own limitations call 40 of 57 residual instances oracle-disputable),
`EXPERIMENT_RECORD.md` §9–§10.

## 0. Why

"80% of the residual is unexercised edge" is the sentence the paper's claim (2) rests on. It
was produced by one rater under a precedence that could never assign `ambiguous-oracle`
before `unexercised-edge`. If a large share of the residual is defects only the hidden
suite's oracle defines — inputs the specification does not determine — then the recall
denominator, not the auditor, is what the residual measures.

## 1. Population and material

The 68 instances of `records/ceiling/residual_classification.json` (57 in ceiling 1's
all-family residual, 11 classified for its exploratory comparison), read from the archived
residual dump (`~/Documents/Crossaudit/study-data/wt-ceiling-runs/residual/`): the
specification, the visible suite, the candidate, the dataset's canonical solution, and the
witness (the first failing hidden inputs with expected and actual values). The sheet shown
to the raters carries an opaque id and these materials only — not the prior category, not
whether the instance is in the residual.

## 2. The rule, decidable, applied in this order

1. `timeout` — the hidden suite did not terminate on the candidate.
2. `ambiguous-oracle` — for the first failing hidden input, the expected value is NOT
   determined by the specification as written: the specification is silent on that input
   class, or a reasonable reading of it allows the candidate's value. Test: can the rater
   write one sentence from the specification's own words that entails the expected value
   and excludes the candidate's? If not, ambiguous-oracle.
3. `unexercised-edge` — the specification determines the expected value, the visible suite
   never constructs an input of that class, and the candidate is wrong on it.
4. `spec-misreading` — the specification determines the value and the visible suite does
   exercise that class or a neighbouring one; the candidate misread the specification.
5. `wrong-algorithm` — the candidate's approach cannot produce the expected values in general.
6. `other`.

## 3. Raters and outcomes

Two raters, each seeing the same blind sheet: L1 the author; L2 `gpt-6-astra` through the
Codex CLI (read-only). The memo asks for a human rater who is not the author; none is
available, and that limit is stated in the results. Primary: the consensus share of
`ambiguous-oracle` among the 57 residual instances, with Wilson and the problem-cluster
bootstrap (seed 20260914, 10,000 resamples); κ over the six categories. **Kill for the
sentence "the residual is mostly unexercised edge"**: consensus `ambiguous-oracle` ≥ 30 of
57, or consensus `unexercised-edge` < 29 of 57. If the kill fires, ceiling 1's recall is
restated beside an oracle-clean denominator (P minus the consensus-ambiguous instances)
as an exploratory number. Disputed items (the raters differ) are reported as disputed and
count toward neither category.

## 4. Records

`records/rerate/L1.csv`, `L2.csv`, `key.jsonl` (id → instance), `numbers.json`; the sheet
stays in the archive (it quotes the corpus). No model call is made for anything but L2's
labels; no instance is re-run.

## Amendment 1 — rate the flagged instances too (2026-09-10, after the residual result, before any flagged label)

The residual result is known (consensus `ambiguous-oracle` 44 of 57). §3's oracle-clean
restatement treats the 53 flagged P instances as oracle-clean without checking; this amendment
checks. The 53 stratum-P instances outside the all-family residual are dumped with the same
builder (specification, visible suite, candidate, canonical, witness), shuffled into a second
blind sheet (seed 20260914; ids continue from Q069), and rated by the same two raters under §2's
rule, unchanged. L2 sees neither sheet's membership.

Secondary (now preregistered, replaces §3's exploratory line): with a_r the consensus-ambiguous
count in the residual and a_f the same among the flagged, the oracle-clean union recall of ceiling
1's all-family union is (53 − a_f) / (110 − a_r − a_f), with a problem-cluster bootstrap over the
110 P instances' (flagged, ambiguous) pairs, seed 20260914 + 10; disputed instances stay in the
denominator (counted as not ambiguous). No kill; the number is reported beside the registered
48.2% whatever it is. Both consensus-ambiguous shares (residual, flagged) are reported with both
intervals.

## Amendment 2 — 2026-09-10, after the first review; the sheets were not blind to identity

The first review found that both sheets carried the instance id inside the hidden-outcome
record (only the header line had been stripped), and that L2's second prompt named the file
"flagged". So neither rater was blind to instance identity, and L2 was not blind to the second
sheet's status; both were blind to the prior category and to per-item flag status on the first
sheet (57 residual and 11 flagged instances mixed without a marker). The results are corrected to
say exactly that. L1 cannot be re-blinded. L2 can:

**Re-blinded L2 pass.** One combined sheet of the 110 P instances (57 residual + 53 flagged),
each item carrying only the witness (first failing inputs with expected and actual values, or
the timeout flag), the specification, the visible suite, the candidate and the canonical
solution — no instance id, no benchmark name, no counts of hidden tests, no membership marker;
shuffled with seed 20260915, ids R001–R110, neutral file name; L2 = `gpt-6-astra` in a fresh
Codex session with §2's rule verbatim and no mention of residual, flagged, or sheets. Outcomes,
both reported: (i) per-instance agreement of the re-blinded L2 labels with L2's first labels
(the effect of identity and status on L2); (ii) the consensus of L1 with the re-blinded L2,
with §3's kill and Amendment 1's secondary restated on it beside the original. No rule change,
no new bars, no L1 re-rating.

Also corrected by this amendment: Amendment 1's "before any flagged label" holds for 42 of the
53 flagged instances — 11 had been rated on the first sheet (2 ambiguous, 7 edge, 2 timeout by
consensus).

## Amendment 3 — 2026-09-11, an external check of the labels, added after they were frozen

Every review of this study named the same limitation: both raters were ours. This amendment
does not add a rater. It asks whether anyone outside this project, working for their own
reasons and before we looked, had already recorded that these specifications do not settle
their expected values.

**One source qualifies as an external label set**, and the join is by task id, not by
instance, so the outcome is a **concordance, not a rate**:

1. **Richter & Papadakis, arXiv:2607.01953**, §1 footnotes 1–3, which name twelve MBPP tasks
   they manually identified as *ambiguous* (294, 102, 410, 576), *incomplete* (7, 137, 244,
   261, 278) or *contradictory* (459, 638, 639). This is the external check, and the only one.

Reported beside it, **not as a label and not counted in the concordance**:
`evalplus/eval/_special_oracle.py` (Apache-2.0), the tasks whose candidates the benchmark's
harness does not compare to the reference by equality — eight compared as sets, two given a
hand-written oracle stating the reading chosen. That file records engineering decisions and
nowhere says a specification is defective; treating it as evidence about specifications is
this study's own reading, and a shared task id does not even mean the two are discussing the
same defect. `HumanEval/32`, whose helper implements a convention the task's prompt already
supplies, is excluded outright.

**Order of events, as observed.** This study's labels were committed at `d98f0c1`
(residual), `3aa97aa` (flagged) and `e654452` (the identity-stripped pass); the earliest
external file on this machine was created after all three. Those are commit times and file
creation times, and they establish that order and nothing more. They are not proof of what a
rater knew: the fetches are untracked, and no record here can exclude prior awareness of a
public paper.

**What is computed.** `rerate/external_labels.py` transcribes both sources with their
provenance; `rerate/external_join.py` joins them to this study's frozen per-instance labels,
reduced to one label per task, and writes `records/rerate/external.json`: how many of their
tasks are in our stratum P, how many of those we call `ambiguous-oracle`, and every
disagreement with its detail.

**The join is one-sided and that is stated wherever it is used.** Neither source claims to be
exhaustive — Richter gives examples, EvalPlus wrote an oracle only where it had to — so a task
they do not name is not evidence that its specification is sound. The concordance can support
"where an outside party recorded a defective specification, this study's raters agreed", and
nothing about the *rate* of `ambiguous-oracle` in the residual. No number in §3 or Amendment 1
changes, no kill is re-evaluated, and this analysis is **post hoc** wherever it appears.
