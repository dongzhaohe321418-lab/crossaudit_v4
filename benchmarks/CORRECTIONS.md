# Corrections to the measurement record

Numbers withdrawn or restated, with the evidence for each withdrawal. This file
exists because these results are intended for publication, and a reader deciding
whether to trust the record is entitled to see what the record got wrong before
they find it themselves.

Two sources. Some items were found by re-reading this project's own reports
against the claims being made *from* them. The largest ones, including an error in
this file's own first version, were found by an independent reviewer running on a
different vendor's model over the same records. Its full report is kept verbatim
at `reviews/2026-09-05-cross-vendor.md`; every finding taken from it was
reproduced here from the archived run data before being accepted.

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

**1. The 2.6-point prose noise floor — real, but the wrong estimand.**
*This item was itself wrong when first written here, and is corrected below.*

The figure is not fabricated. Study 5 measured it: three runs of the identical
cross-vendor configuration over the identical 11 fixed drafts gave recalls of
20.3%, 15.3% and 18.6%, SD 2.59 pp, range 5.1 pp. `RESULTS-5.md` reports it
plainly and already warns that "several cannot be judged at all because the floor
measured here covers the auditor and not the generator".

The defect is what it can be used for. It is the standard deviation of a **pooled
micro recall over fixed drafts**. It therefore bounds auditor-side run-to-run
variation and nothing else. It is not the variability of the primary paired
contrast, and it is not the variability of any study in which generation changes.
Every use of it to accept or withdraw a finding from a generation-changing study
is invalid, including its use against study 2's "2.0% to 3.8%".

Two of this project's numbers are read against it correctly, and both concern the
auditor over fixed drafts. Every other use of it should be struck. What is still
missing, and is now being measured, is the run-to-run spread of the **primary
paired contrast** itself.

**How this entry came to be wrong.** It was first written here as "fabricated —
appears in no committed result", on the strength of a search of the committed
tree of one branch. Study 5 is not committed to that branch; it lives in a
scratchpad worktree. The claim was false, it was published in this file, and it
was caught by the same cross-vendor review that produced item 9. That is finding 5
below biting the person writing the corrections: **evidence scattered across
uncommitted worktrees produced a false claim about this project's own record.**
The entry is left in place, corrected, rather than quietly rewritten.

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

**10. Study 3's "+2.04 F1 — the draft did not fall."**
Withdrawn against a floor measured on its own estimand. Study 5B ran three
replicates **including generation**: draft F1 9.72, 10.42, 6.94, **SD 1.84**.
+2.04 does not clear it. This is the reassurance that made splitting the rules
look free, and it is now unsupported: the recall gain from splitting survives
easily (2% to 23.5%), but the claim that it cost the first draft nothing does
not. Whether it costs anything is unmeasured, not shown to be zero.

Study 2's "a stronger auditor model moved recall from 2.0% to 3.8%" falls to the
same floor, which is the second and better reason to withdraw it (the first,
item 5, is that the arm varied the model within one vendor).

**11. "The cross-vendor auditor sees more." — the premise itself.**
Tested at n = 30 and **not supported, in the opposite direction**. The
cross-vendor auditor recalled **19.8%** of the defects CLEAR found; the generator
judging its own work recalled **31.7%**. Paired **−11.8 pp, CI [−19.2, −4.1]**,
exact Wilcoxon p = 0.0115, and −13.6 pp under the deterministic mapping. Worse on
17 instances, better on 3. The earlier n = 10 result was not a fluke; it was this
effect underpowered.

Stated against itself, as the study's author does: this is the weakest result in
that study. −11.8 pp is smaller than 2 SD of the same statistic at n = 8, it
clears only after scaling to n = 30, and Bonferroni over the study's eleven
comparisons gives 0.127. What supports it is that all five independent estimates
of it are negative.

**What replaces it is larger and cleaner.** `cross` gated **80.0%** of increments
against `self`'s **3.3%**: +76.7 pp, McNemar **p = 2.4 × 10⁻⁷**, 23 discordant
pairs with none pointing back. `cross` filed **all 48** of its findings as
BLOCKER. `self` raised **more** findings (64), filed **61 as ADVISORY**, and was
the **most precise** arm at 82%. Both registered kill criteria cleared, and both
results clear the noise floor outright.

**The defensible sentence is "a stranger is less tolerant", not "a stranger sees
more."** The self-audit does not fail to notice; it notices and forgives. That is
a severity mechanism, and it has been sold as a recall mechanism.

**And "vendor" may be the wrong axis.** `sibling − self` = **−22.2 pp**
(p ≈ 2 × 10⁻⁵): two models from the *same* vendor differ by nearly twice what the
two vendors differ by. What the invariant appears to buy is distance from the
author, not distance from the training corpus. This is a product question, not a
measurement one, and it is open.

---

## The four headline findings, restated

Four findings were carried out of this measurement programme as its results. The
cross-vendor review reached all four. None survives in the form it was stated.

**1. "Revision is net negative."** Withdrawn (item 9). The unconditional effect
is −4.01 F1, CI [−16.54, +8.33]. A second defect compounds it: `report2.py`
records one first-to-final delta per *revised instance* while calling it a
revision, so multi-round changes collapse. Study 3 has 25 revised instances but
**36 transitions**; per transition the figure is −7.64, not −11.01, and the
fixed/broken split is 5/19, not 3/17. And the pooled `p = 0.0014` is not valid
evidence: arms S, R and X change the constitution, the auditor's context and the
revision prompt, and their per-arm means are **−13.56, +5.83 and −14.42**. Pooling
them yields a configuration-weighted mixture, and the 25 observations contain only
18 unique sample ids, so the sign enumeration assumes an independence the data do
not have. **Surviving claim: none.** The direction is suggestive; the number, the
unit and the inference are all withdrawn.

**2. "The constitution, not the model, is the recall bottleneck."** Not
established as causal. The comparison sets shipped B's 4/201 over 40 instances
against 10-instance arms, and **every draft in those arms differs byte-for-byte
from shipped B's**. Arm B′ also changes the generator prompt. No confidence
interval or paired test was supplied for the recall contrast. The micro rates
reproduce; the attribution does not. **Surviving claim: on ten matched instances,
recall differed markedly across rules conditions, on drafts that also differed.**
The clean version of this experiment — re-auditing identical frozen drafts under
each condition — has not been run and is cheap.

**3. "The constitution poisons the generator" (+24.07 F1).** n = 4, no confidence
interval. The four differences are **+16.67, 0, +22.22, +57.41**. One instance
supplies most of the effect. The point estimate reproduces; the uncertainty was
never stated and is extreme. **Surviving claim: a hypothesis worth a real n.**

**4. "Cross-vendor's value is low false positives, not higher recall."** The
false-positive half is the strongest thing here and is not withdrawn. The recall
half is: the +8.9-point advantage rests on **five discordant pairs that all point
one way**, so a percentile bootstrap cannot generate a negative resample and
mechanically returns a positive lower bound. Exact McNemar gives **p = 0.0625**.
The interval [1.8%, 17.9%] does not establish exclusion of zero, and "real in
sign" is not supported. Four of the 56 stratum-P cases are also **timeouts rather
than observed assertion failures**, which contradicts the stated ground truth and
moves recall from 5/56 to 5/52. **Surviving claim: cross-vendor audit flags fewer
correct solutions, which is the number that decides adoption; its recall advantage
is not established.**

## What the review did not find

Stated because negative findings are results, and these were the two that most
threatened the programme:

- **CLEAR's core algorithm is correct.** The full-checklist denominator, the
  precision and recall directions, the per-sample harmonic F1 and the sample-level
  aggregation all match the paper's procedure. No chain-of-thought reaches the
  extractor or comparator. The reimplementation risk that `EXPERIMENT_RECORD.md`
  §6 names as permanent is smaller than feared, though it remains real: the
  scorer does silently coerce malformed mapper replies to `"N/A"` instead of
  rejecting them, and the raw replies were not retained, so the realised impact
  cannot now be measured. Retain them from here on.
- **No hidden-test leakage in the code study.** Not through prompts, imports,
  fixtures, caches, or the generated solutions' filesystem behaviour. The
  population reproduces exactly: C = 455, P = 56, F = 29. Every arm count and
  McNemar p regenerates from the committed records. The weaker claim that
  should replace the report's wording is "not present in runtime prompts or tool
  inputs", since HumanEval+ and MBPP+ predate the models and pretraining
  contamination cannot be excluded by runtime isolation.
- **No p-value was copied from an unrelated comparison.**

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

**12. "The code noise floor is 1.8 points on P."**
Restated. 1.8 was the difference between one specific pair of draws (study 1's
`cross` and `cross-replicate`) — the narrowest of what turned out to be three
pairwise comparisons. Three full draws of the shipped architecture over all 290
instances (`records/explore/`) give a **widest pair of 6.4 points at n = 110 and
9.1 on the confirm half at n = 55** (11, 7 and 6 of 55). The stratum-C column,
on which the adoption constraint is written, is stable at 5, 5, 4 of 74. Every
statement in this record that reads an effect against "1.8 points" should be
re-read against 6.4 at n = 110; the ones in `RESULTS-2.md` (+9.1 recall) and
`RESULTS-EXPLORE.md` (`tri_union`, `hc_u_dc`) survive it, the rest do not.

**13. "The self-audit sees more than the stranger" — restated again, and now with a
measured ceiling on the other side.**
Item 11 withdrew "the cross-vendor auditor sees more" on the strength of a prose study at
n = 30 in which the generator judging its own work recalled **31.7%** against the
cross-vendor auditor's **19.8%**, and replaced it with "a stranger is less tolerant".

Study 8 measures the same contrast on code, against model-free ground truth, with eight
independent readings per family over 110 defective solutions, and the ordering at the
ceiling is **the other way round**: the generator's own model reaches **17.3% (19/110)**
union recall at eight readings, fitted asymptote **16.6%, 95% CI [8.1, 26.3]**; the
cross-vendor auditor reaches **30.0% (33/110)**, fitted asymptote **31.5% [21.7, 45.6]**.
The preregistered primary outcome **A(self) − A(cross) = −14.9 points, 95% bootstrap CI
[−32.1, −2.3]** over problem clusters, and the model-free raw difference at eight readings
is **−12.7 points [−25.0, −0.9]**.

These two results are not in contradiction — different task, different ground truth, and a
different estimand (a single-draw recall against an asymptote over eight draws). What must
change is the summary sentence carried out of item 11. **The direction of the self/cross
recall gap is task-dependent and has now gone both ways**, and neither direction should be
quoted as a property of self-audit. The false-positive half has gone the same way every
time and is not withdrawn: the self-auditor flags more correct work — **24.0% against
16.0%** at eight readings in study 8, and **13 of 56 against 3 of 56** in its closed-loop
arms (+17.9 points [3.6, 24.1], exact McNemar p = 0.0129).

**14. "AI self-audit raises accuracy" was never measured until now, and it does not.**
The programme has measured what auditors *notice* seven times and what the loop *achieves*
once, in a study whose primary outcome was later withdrawn for conditioning on a
post-treatment variable (item 9). Study 8 measures it unconditionally: over a frozen paired
sample of 112 instances, the generator's own model auditing and then revising its own code
changed the fraction passing a hidden test suite by **+0.89 points, 95% exact CI
[−3.16, +3.99], exact McNemar p = 1.0000** — 3 of 56 wrong solutions repaired, 2 of 56
correct ones broken. The preregistered kill condition fired. **No claim that self-audit
raises accuracy is supported by this programme's evidence**, and any planning document that
assumes it should be re-read against `benchmarks/code/RESULTS-CEILING.md`.

What did move: adding one rule to the constitution telling the auditor to find what the
visible tests do not cover raised flags on defective code from 10 of 56 to 25 of 56
(**+26.8 points [12.9, 30.3], p = 0.0003**) and the loop's net accuracy to **+8.04 points
[1.06, 11.16], p = 0.0225**. That is a **secondary** outcome that does not clear the
study's own Bonferroni threshold over twelve planned comparisons (0.00417), and it costs 7
additional false alarms on 56 correct solutions. It licenses a larger confirmatory run, not
a default change.

**15. Study 8's "95% exact" paired intervals — withdrawn, and the method replaced.**
The first committed version of `benchmarks/code/RESULTS-CEILING.md` reported every paired
binary difference with an interval built by taking a Clopper–Pearson interval for the
direction probability **conditional on the discordant pairs** and rescaling it by the
**observed** discordance fraction D/n. Conditioning is legitimate for McNemar's test. It is
not legitimate for an interval on the unconditional risk difference, because D/n is itself
an estimate and its uncertainty is thrown away.

An independent cross-vendor reviewer found this, and it reproduces exactly: enumerating
D ~ Binomial(112, 0.1) with every discordance beneficial gives that construction a coverage
of **0.4162688657**, not 0.95. The headline `self-loop` interval **[−3.16, +3.99] is
withdrawn**, as is every other paired interval in that version.

**What replaces them** (preregistration amendment 4): the problem-cluster percentile
bootstrap as primary, with Tango's unconditional score interval and a Berger–Boos-restricted
exact unconditional interval as checks. Measured coverages 0.960 and 0.998. The headline
becomes **+0.89 pp, cluster CI [−3.54, +5.88], Tango [−3.98, +6.06], exact unconditional
[−6.70, +8.48]**.

**No point estimate changed, and no conclusion changed.** The kill condition fires under the
withdrawn interval and under all three replacements. This entry exists because the interval
was published, not because the finding moved.

Two further corrections to that report, from the same review, both reproduced before being
accepted:

- **"Exactly one secondary contrast clears the correction threshold" was false.** The
  preregistration planned twelve comparisons; **sixteen** were computed, the highlighted
  contrast was not among the twelve, and a second contrast also cleared the threshold. The
  report now carries a full planned/performed/exploratory inventory, a single correction
  family of sixteen, and labels every flag contrast exploratory. **Five planned comparisons —
  the mixed and `astra` asymptote contrasts — were never delivered and are unmeasured.**
- **"The referent raises accuracy" was overstated.** +8.04 pp is the referent arm against its
  own baseline; its exact unconditional interval contains zero. The contrast that isolates
  the referent, against `cross-loop`, is **+5.36 pp, CI [−0.88, +12.08], p = 0.146**. What
  survives is that the referent **moved what the auditor flagged** (+26.8 points on
  stratum-P flags, exploratory), not that it raised accuracy.

**16. "No number had left the harness" — false, by 99 seconds.**
`RESULTS-CEILING.md`'s first version said a swapped Clopper–Pearson tail was caught before
any number escaped. `git show 1a66571:benchmarks/code/records/ceiling/tables.md` carries the
headline interval as **[+3.16, −1.93]**, committed at 18:46:39; the fix landed at 18:48:18.
An erroneous number was in a committed results artefact for that interval. It never reached
prose — the report was first committed at 20:55:51 — but the claim as written was wrong and
is corrected in that report's deviations.
