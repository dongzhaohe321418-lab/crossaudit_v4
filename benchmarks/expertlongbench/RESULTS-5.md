# Study 5 — the premise. The cross-vendor auditor named fewer defects than the model that wrote them, and blocked twenty-four times as often

**The different-vendor auditor recalled 19.8% of the defects CLEAR found in the drafts;
the generator judging its own work recalled 31.7%. Paired difference −11.8 percentage
points (95% CI −19.2 to −4.1, exact Wilcoxon **p = 0.0115**, n = 30 instances judging
byte-identical drafts), and −13.6 pp under the deterministic mapping (CI −20.3 to −6.6,
**p = 0.0018**). Cross-vendor was worse on 17 instances, better on 3, tied on 10.** The
heterogeneity invariant is the one thing this product refuses to run without, and on this
task **it did not buy the recall the README says it buys.** It bought something else.

**What it bought is intolerance, and that result is now confirmed rather than guessed.**
Registered in advance in `PREREGISTRATION-5B.md` after the first execution suggested it:
the cross-vendor auditor gated **80.0%** of increments, the generator's own model **3.3%**
— a paired difference of **+76.7 pp**, exact McNemar **p < 0.0001**, with 23 discordant
instances all pointing the same way and none pointing back. The prediction registered
beforehand was "at least 30 pp". It came in at 77. `cross` filed **all 48** of its
findings as BLOCKER. `self` raised **more** findings — 64 — and filed **61 of them as
ADVISORY**, which gates nothing, returns nothing to the writer, and ships the draft.

> **The sentence the product can defend is not "a stranger sees more". It is "a stranger
> is less tolerant."** The same-vendor auditor sees more and forgives it. Both halves are
> significant, both were predicted in writing before this run, and both survive the noise
> floor.

**The noise floor exists now, as designed: three full replicates including generation.**
Draft CLEAR F1 across identical runs: 9.72, 10.42, 6.94 — **SD 1.84 F1 points**. Read
against it, **study 3's headline "+2.04 F1, the round-one draft did not fall" is inside
the noise and is withdrawn**, as is **study 2's "2.0% → 3.8% with a stronger auditor
model"**. The full survivor list is below.

**Spend: US$12.20** of the US$20 two-study budget, US$9.80 of it on this rerun.

---

## Two executions, and how they are kept apart

| | first execution | **confirmatory rerun** |
|---|---|---|
| frozen sha | `9656cbf` | **`c2b9cd6`** |
| preregistration | `PREREGISTRATION-5.md` | + `PREREGISTRATION-5B.md` |
| seeded / analysed | 16 / **11** | 40 / **30** |
| `cross` − `self` recall (adjudicator) | −10.3 pp, p = 0.28 | **−11.8 pp, p = 0.0115** |
| gate rate `cross` / `self` | 72.7% / 18.2% | **80.0% / 3.3%** |
| noise floor | auditor-only substitute | **three full replicates** |
| why it ended | both vendors' credit exhausted | ran to target |

**The two runs are not pooled.** Every number in this report is from the rerun alone. The
first execution is shown beside it as an independent prior attempt on a subset of the same
seeded sample, and its agreement — same sign, same magnitude, on disjoint statistics —
is evidence, not arithmetic.

The severity result was **exploratory in the first execution and is a registered secondary
outcome here**, with its statistic, its direction and two kill criteria fixed in writing
before this run. It was not promoted after the fact.

---

## What was run

| | |
|---|---|
| task | `T03MaterialSEG` — justify the key decisions in a solid-state synthesis recipe |
| corpus | `T03MaterialSEG.jsonl`, sha256 `0b525eae93aab406…`, 50 rows, CC BY-NC-SA 4.0, not redistributed here |
| sample | 40 seeded of 50, seed `20261104`; **stopped at 30 complete** |
| generator | `anthropic:claude-sonnet-4-6` — one draft per instance, every arm |
| CLEAR mapper / judge / adjudicator | `openai:gpt-5.6-terra` |
| rules | **rubric-grade**, constitution sha256 `9f1ee353ec4cb05e…` — the file study 3 used |
| settings | `max_rounds: 1`, `checks: general`, `lone_model_blocker: block`, N/A policy literal |
| code | frozen at **`c2b9cd6`**, `git status --porcelain` empty at freeze |
| environment | CPython 3.13.5, Darwin 25.6.0 arm64 |
| records | `study5/premise-A2.rows.jsonl` (120 rows), manifests, directory digests |

| arm | who judges | vendor vs. generator |
|---|---|---|
| `cross` | `openai:gpt-5.6-terra` — the shipped configuration | **different** |
| `self` | `anthropic:claude-sonnet-4-6` — the generator itself | same vendor, same weights |
| `sibling` | `anthropic:claude-opus-4-8` | same vendor, different model |
| `none` | nothing | — |

The drafts are poor, which is what makes the auditors' job measurable: mean CLEAR F1
**15.4**, accuracy 13.3, **156 of 180 rubric items wrong**. An arm naming everything wrong
would score 100% on a denominator of 156. The best arm named 50.

### The arms judged the same bytes — proven, not asserted

For **all 30 instances** the harness's audit prompt digest equalled the digest the
**product's own audit** recorded for the same commit (30/30). The three judging arms then
received those identical bytes; the only thing that varied was which model read them. Had
one digest differed the run was void by its own preregistered rule.

Data quality was total: **30 of 30 instances complete, every arm answering on every
instance, zero replies rejected by the rule validator, zero provider errors.** Nothing was
dropped after its scores were seen.

### The heterogeneity bypass lives in the benchmark, not the product

`self` and `sibling` cannot exist while `config.heterogeneity` runs, and the guard is
inside `crossaudit.auditor.run.run_audit`. **`src/` was not modified.** `premise.py` does
not call `run_audit`; it calls the same product functions in the same order —
`_materialise_tree_scope`, `_committed_constitution`, `_committed_task`, `run_checks`,
`prompt.build`, `resilience.complete`, `parse_reply`, `validate_reply` — and skips the one
guard. The 30/30 digest equality is what makes that substitution checkable.

### Rubric-grade rules, said out loud

The constitution is generated from the task's own rubric, **not** the shipped general one.
Under the general rules the auditor is near-silent — 2.0% recall in studies 2 and 3 — and
all four arms would have looked identical **because none of them would have said
anything**. Every number here describes a configuration a user must opt into.

---

## The primary outcome

Recall for an arm on an instance is *(rubric items CLEAR scored wrong that some finding of
that arm named) ÷ (rubric items CLEAR scored wrong in that draft)*. Effect = mean paired
difference in percentage points; CI = 20 000-resample percentile bootstrap over instances;
p = exact two-sided Wilcoxon signed-rank, ties dropped.

| comparison | mapping | n | A | B | **effect** | 95% CI | b/w/t | exact p | pairs used |
|---|---|---:|---:|---:|---:|---|---|---:|---:|
| **`cross` − `self`** | adjudicator | **30** | 19.8% | 31.7% | **−11.8 pp** | −19.2, −4.1 | 3/17/10 | **0.0115** | 20 |
| `cross` − `self` | rule | 30 | 19.2% | 32.7% | **−13.6 pp** | −20.3, −6.6 | 2/17/11 | **0.0018** | 19 |
| `cross` − `sibling` | adjudicator | 30 | 19.8% | 10.5% | +9.3 pp | +2.6, +16.2 | 14/3/13 | 0.0173 | 17 |
| `cross` − `sibling` | rule | 30 | 19.2% | 10.5% | +8.7 pp | +2.3, +14.9 | 14/3/13 | 0.0173 | 17 |
| `sibling` − `self` | adjudicator | 30 | 10.5% | 31.7% | −21.2 pp | −26.5, −15.4 | 2/25/3 | 1.6 × 10⁻⁵ † | 27 |
| `sibling` − `self` | rule | 30 | 10.5% | 32.7% | −22.2 pp | −27.8, −16.2 | 2/25/3 | 1.9 × 10⁻⁵ † | 27 |

† The two `sibling` − `self` rows retain 27 usable pairs, above the 20 at which this
implementation enumerates exactly, so those two p values alone are a normal approximation
with a continuity correction. **Every other p in this report is exact.**

**The row in bold was named before either run and is negative under both mappings, with
intervals excluding zero.** The first execution's −10.3 pp at n = 10 was not a fluke of a
small sample; it was the same effect underpowered.

**And the largest effect in the table is not about vendors at all.** `sibling` − `self` is
−22.2 pp at p ≈ 2 × 10⁻⁵: two models from the *same* vendor differ from each other by
nearly twice what the two vendors differ by. Whatever governs recall here, the vendor
boundary is not it — which is the deeper problem for an invariant defined on vendors.

### Pooled over items

| arm | recall | item precision | fired | **gate rate** |
|---|---|---|---|---|
| `cross` | 18.6% (29/156) [13, 25] | 72.5% (29/40) [57, 84] | 24/30 (80.0%) | **24/30 (80.0%)** |
| `self` | **32.1%** (50/156) [25, 40] | **82.0%** (50/61) [71, 90] | 29/30 (96.7%) | **1/30 (3.3%)** |
| `sibling` | 9.6% (15/156) [6, 15] | 60.0% (15/25) [41, 77] | 19/30 (63.3%) | 11/30 (36.7%) |
| `none` | 0.0% (0/156) [0, 2] | n/a | 0/30 | 0/30 |

Wilson intervals. **Precision did not collapse under same-vendor judging — it was the
highest of the three arms** (82.0%, interval clear of `sibling`'s). The same-vendor
auditor is not compensating for volume with noise: it named more items *and* was right
about a larger fraction of them.

---

## Secondary outcome S1 — gate rate (registered in `PREREGISTRATION-5B.md`)

The proportion of instances on which an arm raised at least one BLOCKER. This is the
quantity that decides whether work is stopped.

| comparison | n | A | B | effect | 95% CI | discordant b/c | exact McNemar p |
|---|---:|---:|---:|---:|---|---|---:|
| **`cross` − `self`** | 30 | **80.0%** | **3.3%** | **+76.7 pp** | +60.0, +90.0 | **23/0** | **2.4 × 10⁻⁷** |
| `cross` − `sibling` | 30 | 80.0% | 36.7% | +43.3 pp | +26.7, +60.0 | 13/0 | 2.4 × 10⁻⁴ |
| `sibling` − `self` | 30 | 36.7% | 3.3% | +33.3 pp | +16.7, +50.0 | 10/0 | 1.95 × 10⁻³ |

**23 discordant pairs, every one in the same direction.** The registered prediction was
≥ 30 pp; observed 76.7 pp.

### Secondary outcome S2 — blocking recall

Recall restricted to BLOCKER findings — the ones that actually stop an increment.

| comparison | mapping | n | A | B | effect | 95% CI | exact p |
|---|---|---:|---:|---:|---:|---|---:|
| **`cross` − `self`** | adjudicator | 30 | 19.8% | **1.3%** | **+18.5 pp** | +12.4, +24.9 | **3.8 × 10⁻⁶** |
| `cross` − `self` | rule | 30 | 19.2% | 1.3% | +17.8 pp | +12.1, +23.7 | **3.8 × 10⁻⁶** |
| `cross` − `sibling` | adjudicator | 30 | 19.8% | 7.5% | +12.3 pp | +5.9, +18.8 | 0.0020 |

### The severity mix, which is the whole story in one table

| arm | findings | BLOCKER | ADVISORY | gated |
|---|---:|---:|---:|---:|
| `cross` | 48 | **48** | **0** | 24/30 |
| `self` | **64** | 3 | **61** | **1/30** |
| `sibling` | 27 | 19 | 8 | 11/30 |

`cross` has never, in 48 findings across 30 instances, filed an advisory. `self` found
*more* real defects than `cross` — 50 correctly named items against 29 — and blocked once
in thirty. **S3, also registered in advance (`self` total recall ≥ `cross` while `cross`
gate rate > `self`), is confirmed on both clauses.**

### Both kill criteria were cleared

Registered beforehand: the severity finding dies if the gate-rate difference is smaller
than two standard deviations of its own run-to-run spread, or if its sign is wrong.
Measured against the three replicates below: the paired gate-rate difference was
**+87.5, +62.5, +87.5 pp** across replicates, SD 14.43, so **2 SD = 28.9 pp against an
observed +76.7 pp.** Sign correct in every replicate and in both executions. **Confirmed,
not merely unrefuted.**

---

## The noise floor, as the design asked for it

Three replicates of the identical configuration — **including generation** — over the same
8 instances, varying nothing the harness controls. The provider layer exposes no seed and
temperature comes from the model's capability card, so what varies is provider
nondeterminism: exactly the variance every published delta in this project has been read
against without being measured.

| quantity (n = 8 per replicate) | rep 1 | rep 2 | rep 3 | mean | **SD** |
|---|---:|---:|---:|---:|---:|
| **draft CLEAR F1** | 9.72 | 10.42 | 6.94 | 9.03 | **1.84** |
| `cross` recall (%) | 24.4 | 18.2 | 31.1 | 24.6 | 6.47 |
| `self` recall (%) | 33.3 | 38.6 | 35.6 | 35.8 | 2.66 |
| `sibling` recall (%) | 6.7 | 9.1 | 13.3 | 9.7 | 3.37 |
| `cross` **gate rate** (%) | 87.5 | 62.5 | 100.0 | 83.3 | 19.09 |
| `self` **gate rate** (%) | 0.0 | 0.0 | 12.5 | 4.2 | 7.22 |
| `sibling` gate rate (%) | 37.5 | 25.0 | 12.5 | 25.0 | 12.50 |

The right floor for a *paired* statistic is the run-to-run spread of **that paired
statistic**, not of the two arm means separately — pairing cancels much of the
per-instance variation. Computed directly per replicate:

| paired statistic | rep 1 | rep 2 | rep 3 | SD | 2 SD (n = 8) | 2 SD scaled to n = 30 | observed (n = 30) | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `cross` − `self` recall, adjudicator | −3.7 | −20.4 | −1.7 | 10.28 | 20.55 | 10.61 | **−11.8** | survives at n = 30 |
| `cross` − `self` recall, rule | −7.9 | −20.8 | −4.2 | 8.74 | 17.49 | 9.03 | **−13.6** | survives at n = 30 |
| `cross` − `self` **blocking recall** | +25.0 | +17.7 | +29.6 | 5.99 | 11.98 | 6.19 | **+17.8** | **survives outright** |
| `cross` − `self` **gate rate** | +87.5 | +62.5 | +87.5 | 14.43 | 28.87 | 14.91 | **+76.7** | **survives outright** |
| `sibling` − `self` recall, rule | −26.7 | −29.8 | −22.5 | 3.66 | 7.32 | 3.78 | **−22.2** | **survives outright** |

**Stated plainly and against my own headline: the primary outcome, −11.8 pp, is
_smaller_ than two standard deviations of the same statistic measured at n = 8 (20.6 pp).**
It clears the bar only after scaling the floor to the n = 30 at which the effect was
measured (10.6 pp), and that scaling assumes the run-to-run spread is per-instance noise
rather than a run-level shift — which the three replicates cannot distinguish at n = 3.
**The primary outcome is therefore the *weakest* of this study's results, not the
strongest**, and the honest support for it is that **all five independent estimates of it
are negative** — the first execution (−10.3), the main run (−11.8), and every replicate
(−3.7, −20.4, −1.7). The sign is stable; the magnitude is not.

The severity results need no such caveat: they clear two SD of the raw n = 8 floor
outright.

### Which of this project's published numbers survive

Recall deltas are read against the recall floor at the n they were measured at; F1 deltas
against SD 1.84 F1 (n = 8), scaled by √(8/n).

| claim | delta | floor at its own n | **verdict** |
|---|---|---|---|
| Study 2: recall 2.0% → 3.8%, "a stronger auditor model" (n = 10) | +1.8 pp | 2 SD ≈ 11.6 pp | **WITHDRAWN — inside the noise** |
| Study 3: round-one draft **+2.04 F1**, "the draft did not fall" (n = 20) | +2.04 F1 | 2 SD ≈ 2.32 F1 | **WITHDRAWN — inside the noise** |
| Study 3: auditor recall 2.0% → 23.5% (n = 20) | +21.5 pp | 2 SD ≈ 8.2 pp | **survives** |
| Study 3: audit fires 5/20 → 16/20 (n = 20) | +55 pp | 2 SD ≈ 24.1 pp | **survives** |
| Study 3: precision 100% → 73% | −27 pp | 2 SD ≈ 6 pp | survives (its 100% rested on 2 observations) |
| Study 3: final output **−6.11 F1** (n = 20) | −6.11 F1 | 2 SD ≈ 2.32 F1 | survives, *approximately* — see caveat |
| Study 3: revision **−11.01 F1** (25 revisions) | −11.01 F1 | 2 SD ≈ 2.1 F1 | survives, *approximately* — see caveat |
| Study 3: split alone **+24.07 F1** (n = 4) | +24.07 F1 | 2 SD ≈ 5.2 F1 | **survives** |
| This study: `cross` − `self` recall (n = 30) | −11.8 pp | 2 SD ≈ 10.6 pp | survives, narrowly |
| This study: gate rate +76.7 pp (n = 30) | +76.7 pp | 2 SD ≈ 28.9 pp | **survives outright** |

**Two withdrawals.** Study 2's stronger-auditor-model result and study 3's "the round-one
draft did not fall" both sit inside the run-to-run spread of the very quantity they
report. Neither should be cited again. Note the second withdrawal cuts *against* a change
this project shipped: "+2.04, the draft held" was the reassurance that made the split-rules
change safe, and it was never distinguishable from re-running the same configuration.

**Caveat on the two marked *approximately*.** This floor is measured on the **round-one
draft** under a single-round configuration. Study 3's −6.11 and −11.01 are final-output and
post-revision quantities produced by a three-round loop, whose variance includes revision
steps this design does not run. Their deltas are large enough that a floor several times
this one would not reach them, but they are judged by extrapolation, not by measurement,
and a three-round replicate study is the honest way to settle them.

---

## Analysis, stated so it can be checked

- **Tests.** Recall: exact two-sided Wilcoxon signed-rank on paired per-instance
  differences (exact by enumeration at n ≤ 20 pairs after ties are dropped; the surviving
  count is the "pairs used" column). Gate rate: **exact McNemar**, the paired test for a
  binary outcome observed twice on the same instance, computed as the two-sided binomial
  tail on discordant pairs. **The Wilcoxon is exact everywhere except the two
  `sibling` − `self` rows**, whose 27 usable pairs exceed this implementation's
  enumeration limit of 20 and fall back to a normal approximation with a continuity
  correction; both are flagged at the table. Pairing throughout because every arm judges
  the same draft.
  Non-parametric because recall on a 6-item rubric takes seven discrete values and piles
  up on zero.
- **Effect sizes.** Mean paired difference with a 20 000-resample percentile bootstrap over
  instances, seeded `20261104`, so the interval is a deterministic function of the
  committed rows. Rates carry Wilson intervals.
- **n per cell.** 40 seeded → 30 complete → 30 paired for every comparison. No cell shrank:
  every arm answered on every instance.
- **Comparisons.** **11 preregistered** (6 recall, 1 gate rate, 4 blocking recall). The
  primary was named before either execution. No multiplicity correction is applied; the
  two results the report leads with have p = 0.0115 and p = 2.4 × 10⁻⁷, and a Bonferroni
  factor of 11 would leave both below 0.05 — 0.127 for the primary, which is why the
  primary is presented as the weakest result and the noise-floor caveat above is given
  more weight than its p value.
- **This is the sixth study over the same task and the same 50 rows, and the second
  execution of this one.** That is the multiple-comparison picture, and it is why the
  registered-in-advance secondary matters more than the p on the primary.

## Cost

From the product's own usage ledger.

| | main run (30) | rep 1 | rep 2 | rep 3 | **rerun total** |
|---|---:|---:|---:|---:|---:|
| generation + the loop's own audit | $1.65 | $0.49 | $0.47 | $0.49 | $3.10 |
| CLEAR ground truth | $1.28 | $0.36 | $0.34 | $0.36 | $2.34 |
| judging (three arms) | $2.29 | $0.64 | $0.62 | $0.65 | $4.20 |
| adjudication + preflight | $0.02 | $0.05 | $0.04 | $0.06 | $0.17 |
| **total** | **$5.24** | **$1.54** | **$1.47** | **$1.55** | **$9.80** |

Per judging arm over the 30 instances: `cross` $0.43 (mean 14.1 s), `self` $0.53 (11.6 s),
`sibling` $1.33 (11.1 s), `none` $0.00. Generation averaged 52.7 s.

**Whole-study spend across both executions: US$12.20**, plus about US$1.60 in discarded
trial runs — roughly **US$13.80 of the US$20** two-study budget. Input-token counts are on
every JSONL row but are **not comparable across vendors**: the OpenAI adapter reports far
fewer prompt tokens than the prompt contains, which is caching or a different accounting
convention, so no per-token claim is made.

---

## Deviations, numbered and complete

Deviations 1–14 of the first execution are recorded in this file's history at `55939da`
and still stand for that run. For the confirmatory rerun:

1. **`--target-complete` was recorded in the manifest but never reached the loop.** The
   value was parsed and written into the plan, but the edit passing it into `_execute`
   silently failed to match its call site, so the stopping rule never fired. **I stopped
   the run by hand at exactly 30 complete instances** — the count the preregistration
   named, and the same instances the rule would have taken, being the first 30 complete in
   seeded order. Fixed at `13349ad` after the run so the published reproduction command
   works. **Bias:** none. The stop was at the preregistered count on the preregistered
   ordering; the only difference is that a human enforced it rather than the code.
2. **The main run was interrupted once by the harness and resumed.** The first invocation
   recorded 27 complete instances; a `--resume` added 3 more. Same frozen sha, no arm,
   prompt, model or setting touched, no score read between the two invocations.
3. **One instance's generation was paid for and discarded** when I stopped the process
   mid-instance at the 30-complete mark. Cost a few cents; it is absent from every arm
   equally and is not in the analysed set.
4. **Zero instance attrition.** 30 of 30 attempted instances completed, every arm answered
   on every one, and no reply was rejected by the rule validator. The first execution's
   31% attrition was the Anthropic credit failure, not the design.
5. **The CLEAR judge shares a vendor with the `cross` arm.** `openai:gpt-5.6-terra` both
   judged the drafts and, as `cross`, audited them; there is no third funded vendor.
   **Bias: in `cross`'s favour**, and `cross` still lost the primary outcome, which
   strengthens the headline. It correspondingly weakens any reading of `self`'s recall
   advantage as *large* — the true gap could be smaller than −11.8 pp. It cannot easily
   explain the gate-rate result, which is about severity labels rather than content.
6. **`sibling` is `claude-opus-4-8`**, nominally stronger and more expensive than the
   generator. A "same vendor, different model" arm cannot also hold capability fixed with
   two vendors available. **Bias:** unclear; `sibling` had the *lowest* recall of the
   three arms, so a capability story does not explain the data.
7. **Temperature and seed are not settable.** The adapters take temperature from the
   model's capability card and `resilience.complete` exposes no seed. The study cannot set
   determinism, only measure the resulting spread — which is what the noise floor is.
8. **The provider-echoed model id was not captured.** `Reply.raw` is empty at this seam
   under sealed retention, so `provider_model_echoed` is `""` on every row. The requested
   id is recorded; a silent alias resolution by a provider would not be visible here.
9. **`max_rounds: 1`.** This study judges a draft and does not revise it, so there is no
   round two anywhere in the data and `none`'s "final output" is identical to every other
   arm's. The final-output comparison `none` was meant to anchor is **degenerate by
   construction** and is not reported; what `none` establishes is that an unjudged draft
   has 0% of its defects named, on 156 wrong items.
10. **The noise floor is n = 8 per replicate, three replicates.** Three points is a poor
    estimator of a standard deviation, and the interval on an SD from n = 3 is very wide.
    The floor should be read as an order of magnitude, which is why the primary outcome's
    verdict above is stated as narrow and caveated rather than clean.
11. **The floor is single-round.** It does not cover revision, so study 3's final-output
    and revision deltas are judged against it by extrapolation. Flagged at the table.

## Limitations

- **The CLEAR scorer is a reimplementation from the paper.** The authors released no
  evaluation code, so it has never been diffed against theirs. The only external check is
  that it places frontier models roughly where the paper places them on this task. **Every
  number here inherits that.**
- **A model-judged ground truth is not ground truth.** "Wrong" means
  `openai:gpt-5.6-terra` judged the draft and the human reference not mutually contained
  on that rubric item. Every recall and precision figure is against a model's opinion, and
  the same model supplied one of the four arms.
- **Vendor independence is not statistical independence.** Two models from different
  vendors share training data, architecture and human-feedback conventions. Cross-vendor
  auditing reduces *correlated* error; it does not create an independent oracle. This
  matters most for the negative result: the finding is **not** "independence does not
  help", it is **"this vendor boundary did not raise recall on this task"** — a smaller
  claim, and the one the data supports.
- **One task is one task.** Sixth study on T03MaterialSEG; none repeated elsewhere.
- **Two vendors, three models, one generator, one seed.** "Cross-vendor" here is exactly
  `anthropic → openai`. A different pair could behave differently.
- **The measured configuration is not the shipped default**: rubric-grade rules, one
  round, no revision.
- **Severity labels are not calibrated against anything.** This study measures that the
  arms *label* differently, and that `cross`'s labels stop work. It does **not** measure
  which labelling produces better final documents — that needs the revision path, which
  study 3 measured as harmful.

## What this run does and does not license

**It licenses:**

1. **The cross-vendor auditor names fewer real defects than the same-vendor one** on this
   task: −11.8 pp (p = 0.0115) and −13.6 pp (p = 0.0018), n = 30, with all five
   independent estimates negative.
2. **The cross-vendor auditor gates 80.0% of increments against the same-vendor auditor's
   3.3%** — +76.7 pp, McNemar p < 10⁻⁶, 23 discordant pairs all one way, predicted in
   advance and clearing both registered kill criteria.
3. **Same-vendor judging did not harm precision**; `self` had the highest at 82.0%.
4. **Two models from one vendor differ by more than the two vendors do** (−22.2 pp,
   p ≈ 2 × 10⁻⁵), so vendor is not the axis that governs recall.
5. **The run-to-run floor**: draft CLEAR F1 SD 1.84, recall SD 2.7–6.5 pp, gate rate SD
   7–19 pp, at n = 8.
6. **Study 2's 2.0% → 3.8% and study 3's +2.04 F1 are withdrawn** as inside that floor.

**It does not license:**

- **"Cross-vendor auditing is useless."** It is measured as not-better-at-recall on one
  task with one vendor pair, while being the only arm that reliably stops work. If the
  point of the invariant is that something gets blocked, it is doing that and the
  same-vendor arms are not.
- **"Same-vendor auditing is safe."** `self` gated once in thirty. An auditor that files
  real defects as advice does not gate, and a gate that never closes is not an audit. This
  study measured what each arm *said*, not what shipping on its verdict would produce.
- **Any statement about the final output.** No arm revised anything.
- **A confident magnitude for the primary effect.** Its interval excludes zero and its
  sign is stable across five estimates, but it clears the measured noise floor only after
  a scaling assumption that n = 3 replicates cannot test.
- **Anything about the shipped general constitution**, or about tasks other than
  T03MaterialSEG.

**Do not re-run this study hoping for a different number.** It has now been run twice,
preregistered both times, and the second run confirmed the first. If the configuration
changes, the study restarts and says so here.

---

## Reproduction

Requires `CROSSAUDIT_ANTHROPIC_KEY` and `CROSSAUDIT_OPENAI_KEY` (or the role-named
fallbacks in `~/.crossaudit-keys.env`), both funded, and network access to both vendors.
The preflight refuses to start a run that cannot finish.

```sh
git checkout c2b9cd6                      # the frozen sha; tree clean at freeze
export PYTHONPATH="$(git rev-parse --show-toplevel)/src"
export https_proxy=http://127.0.0.1:7897  # if your network needs it
python benchmarks/expertlongbench/fetch.py --tasks T03MaterialSEG   # CC BY-NC-SA 4.0,
                                          # not redistributed by this repository
R="$PWD/benchmarks/expertlongbench/runs"

# the main run: 40 seeded, stop at 30 complete, judged four ways
# (--target-complete needs the fix at 13349ad; at c2b9cd6 it parses but does not stop)
python benchmarks/expertlongbench/premise.py --n 40 --seed 20261104 \
    --target-complete 30 --verify-prompt --label premise-A2 --out "$R/premise-A2"

# the noise floor: the identical configuration, three times, same 8 instances
for k in 1 2 3; do
  python benchmarks/expertlongbench/premise.py --n 40 --seed 20261104 --subset 8 \
      --label premise-B2-rep$k --out "$R/premise-B2-rep$k"
done

python benchmarks/expertlongbench/premise_report.py "$R/premise-A2"
python benchmarks/expertlongbench/premise_report.py "$R"/premise-B2-rep{1,2,3}
```

`--out` must be absolute. It will not reproduce byte-identically: the provider layer
exposes no seed and temperature comes from the model's capability card — which is the
thing the noise floor measures.
