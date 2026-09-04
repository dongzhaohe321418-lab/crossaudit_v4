# Corrections to the measurement record

Numbers withdrawn or restated, with the evidence for each withdrawal. This file
exists because these results are intended for publication, and a reader deciding
whether to trust the record is entitled to see what the record got wrong before
they find it themselves.

Nothing here was found by an outside reader. Every item was found by re-reading
this project's own committed reports against the claims being made *from* them.

---

## The shape of the failure

The committed reports are, with one exception, careful: they state confidence
intervals, they name their n, and several of them correct earlier reports in this
same line. `RESULTS.md` gives the confirmation rate as "100% (1/1), 95% CI
[20.7%, 100.0%]". `RESULTS-3.md` records the auditor's precision falling from
"100% (2/2)" to 73% and says so in those words.

The failure was **downstream of the reports**, in the layer where results get
summarised into headline claims — planning documents, decision records, and the
working conversation. In that layer the intervals were dropped, and a
one-in-one measurement travelled as "100%". One figure was not merely stripped of
its interval but **invented outright** (item 5).

The lesson is recorded in `EXPERIMENT_RECORD.md` §4, which already requires an
effect size with an interval beside every p. The rule needs to bind wherever a
number is *quoted*, not only where it is first computed.

---

## Withdrawn

**1. The 2.6-point prose noise floor — fabricated.**
No such figure appears in any committed result. A search of `benchmarks/` and
`docs/` returns nothing. It appears to be a misreading of `+2.69 F1`, which is the
**arm B − arm A paired difference** from `RESULTS.md` — an effect estimate, not a
precision estimate. The two are not interchangeable, and using one as the other
inverts the reasoning it was used for.

The deeper problem it concealed: **no prose study has ever run a replicate arm.**
The string `replicate` occurs zero times in `RESULTS.md`, `RESULTS-2.md` and
`RESULTS-3.md`. Every statement of the form "X made no difference, it is inside
the noise floor" made about the prose line is therefore **currently
unfalsifiable**. A dedicated measurement is now running to replace this with a
real number.

The only replicate arm this project has ever run is the code study's
(`feat/study-code`), which measures **1.8 points on stratum P and 0.7 on stratum
C**. Those figures are real, and they license claims about the *code* line only.

**2. The arm-A-versus-arm-B comparison, in both directions.**
`+2.69 F1` (p = 0.67, 7 non-tied pairs) then `−1.19 F1` (p = 0.447, 18 usable
pairs). It changed sign between studies, and it is confounded: arm B's generator
sees a different prompt entirely. It measures generation variance. It should not
be quoted as evidence for the audit's value **or** against it.

**3. Confirmation rate 100%, false-positive rate 0%.**
1/1 in study 1, 23/23 in study 2. Both reports gave the intervals; the summaries
did not. `RESULTS-3.md` supersedes both at **73%**, on one task and one vendor
pair.

**4. "The auditor's precision is 100%" as a product property.**
It was 2/2 and 4/4. Already corrected in `RESULTS-3.md` to 73%; the withdrawal is
recorded here because the "100%" form outlived the report that retired it.

**5. "Changing the auditor model does nothing."**
The arm varied the model **within one vendor**, on n = 10, because the second
credential was occupied by the generator. What that licenses is "a stronger model
from the same vendor did not help on ten samples". The cross-vendor negative this
was taken to establish **has never been run**.

**6. Study 4's −6.20 replay floor and the 25% growth threshold.**
Fitted on 25 observations, falsified on 16 held out. Already withdrawn in effect:
the default is 0, and `repair.max_document_growth` does not exist on
`fusion/evidence-authority` at all.

**7. Study 1's +4.55 on the eleven untouched instances.**
The report itself calls this framing and variance. It should not appear in any
summary.

**8. Any CLEAR absolute placed beside the ExpertLongBench leaderboard.**
The scorer is a reimplementation; the comparison is not licensed.

**9. Study 4's primary outcome is conditioned on a post-treatment variable.**
This is the most serious item here, and unlike the others it was **not** found by
this project. An independent reviewer from a different vendor found it; the
recomputation below was then reproduced independently before it was accepted.

The preregistration names the primary outcome as the revision delta "for each
instance **where the loop revised at least once**". But the treatment is a change
to the revision scope rules, and it therefore helps decide whether a revision
happens at all. Conditioning the analysis on that event selects on a consequence
of the treatment, which opens a path between the arms that has nothing to do with
the effect being estimated. Selecting on a post-treatment variable is a
recognised way to manufacture an effect where none exists.

The size of the difference it makes:

| analysis | n | effect |
|---|---|---|
| as published, conditioned on both arms revising | 7 | **−19.60 F1** |
| unconditional, all paired instances | 16 | **−4.01 F1**, 95% bootstrap CI [−16.54, +8.33] |

The unconditional estimate is not distinguishable from zero. **"Revision is net
negative" is withdrawn as a finding.** What survives is the descriptive
observation that where a revision did occur it was often harmful, which is a
different and much weaker claim, and cannot carry a change to a shipped default.

This is why the proposed report-not-revise default was correctly stopped before
it shipped. The evidence for it was an artefact of the analysis.

---

## Withdrawn framing

Four prose studies have run over **one task, one 50-row corpus, one
generator/auditor vendor pair**, drawing from the same 50 rows. Nothing in the
prose line is an independent replication at the corpus level. The
multiple-comparison clause in `EXPERIMENT_RECORD.md` §4 applies to the line as a
whole, not to each study as if it were the first.

---

## What no correction touches

**No shipped default rests on a withdrawn number.** This was checked, not assumed.
`authority.lone_model_blocker` remains at the conservative `block`, and D144
states in terms that the default "moves when finding-states produce a confirmation
rate, not before". The strictness dials were sequenced the same way. Where the
summaries drifted, the decision discipline held: the project declined to set
defaults on the numbers now being withdrawn.

**The code study survives intact.** It has model-free ground truth (tests that
pass or fail), a measured noise floor, and a false-positive population. Its
finding — that cross-vendor audit's value is low false-positive rate rather than
higher recall — is not affected by anything above.


## On how item 9 was found

Every other item on this list was found by this project re-reading its own
reports. Item 9, the largest, was not: it came from a reviewer at a different
vendor, reading the same committed records, after several same-vendor review
passes over the same study had missed it. The recomputation was then reproduced
here from the archived run directories before the finding was accepted, which is
the only reason it appears as fact rather than as a claim.

That is this project's own thesis, tested on the project itself, with the project
as the thing found wanting. It belongs in the record as evidence, not as an
embarrassment: a same-vendor reviewer sharing the authors' assumptions did not
see the assumption. A reviewer that did not share it did.

## Standing

Withdrawal is not retraction of the line of work. Every number here was produced
by a study that recorded enough about itself to be checked, which is why it could
be checked. The record is what the corrections are made of.
