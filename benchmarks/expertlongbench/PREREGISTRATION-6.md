# Preregistration — study 6: the audit-stage noise floor at n = 20

Written and committed **before any model call**. `EXPERIMENT_RECORD.md` §1.

---

## 0. What already exists, so this study is not sold as the first

Two run-to-run floors have been measured on the prose line, both in study 5, and this
study is neither of them:

| existing floor | what varied | material | statistic | value |
|---|---|---|---|---|
| **study 5, first execution** | the auditor only | 11 fixed drafts, 3 passes | SD of 3 **pooled micro recalls** | **2.59 pp** (20.3 / 15.3 / 18.6; range 5.1) |
| **study 5B, rerun** | generation **and** audit | 8 instances, 3 replicates | SD of 3 draft CLEAR F1 | **1.84 F1** |

`CORRECTIONS.md` item 1 states the defect in how the first was used: it is the spread of
a **pooled rate over fixed drafts**, so it bounds auditor-side variation and nothing
else, and every use of it against a generation-changing study is invalid.

**This study is the better-powered version of the first row, and only of the first row.**
It is n = 20 rather than 11, four replicates rather than three, and it reports the spread
of the **per-instance paired contrast** with an interval instead of the standard deviation
of three pooled means. Two things it can do that 2.59 cannot: say whether 2.59
replicates, and separate auditor-stage variation from study 5B's generation-inclusive
1.84, which no single number can do.

**It does not bound any study in which generation changes.** That conflation is the exact
error `CORRECTIONS.md` item 1 records, and this file states the boundary before the run
so the report cannot quietly cross it afterwards.

---

## 1. Hypothesis, in a form that can come out false

> **H0 (what I expect to reject):** the shipped cross-vendor audit is effectively
> deterministic at round one — replaying it over byte-identical drafts moves the
> aggregate recall by less than the ~2.6 pp study 5 measured at n = 11.

> **H1:** the audit's run-to-run spread is large enough that recall differences of the
> size this project has published at n = 20 are not cleanly separable from re-running the
> same configuration.

Either can come out. The measurement is the spread; there is no arm this study wants
to win.

---

## 2. Primary outcome — one number, named now

**Round-one auditor recall against CLEAR ground truth**, per instance:

    recall_i = (rubric items CLEAR scored wrong in draft i that some finding named)
             / (rubric items CLEAR scored wrong in draft i)

under the **adjudicator (model) mapping** — the mapping every published prose recall
number in this project uses (study 2's 2.0%, study 3's 23.5%, study 5's 19.8%), which is
what makes this floor usable against them. The deterministic **rule mapping** is computed
on the same findings and reported beside it as a sensitivity check; it removes the
adjudicator's own nondeterminism from the estimate.

**The primary quantity is the run-to-run spread of the aggregate recall at n = 20**, i.e.
of the pooled micro rate `Σ_i hit_i / Σ_i wrong_i` — the statistic study 3 reported as
23.5% (23/98) and study 5 reported as 2.59 pp of spread. It is reported four ways, all
named here:

1. **range** = max − min across the K replicates. *This is the kill statistic (§6).*
2. **SD** across the K replicates, and 2·SD, for comparability with 2.59 and with the
   "2 SD of the floor" bar the project already uses.
3. **mean absolute paired difference of the aggregate**, over all K(K−1)/2 replicate
   pairs, with a 95% percentile bootstrap CI resampled **over instances**.
4. **mean absolute paired per-instance difference**,
   `mean over (i, pairs) of |recall_i^(a) − recall_i^(b)|`, with a 95% percentile
   bootstrap CI over instances. This is the quantity a *paired* n = 20 contrast moves by,
   and it is the thing 2.59 was wrongly used as.

A single point estimate of a noise floor is not useful, so no single one of these is "the
noise floor" on its own; the report leads with 1 and 4 together.

## 3. Secondary outcomes, also named now

All per replicate, all over the same 20 instances, all with the same spread statistics:

- **adjudicated item precision** — of the rubric items an audit named, the fraction CLEAR
  had in fact scored wrong (Wilson interval per replicate);
- **findings emitted per audit** (total, and BLOCKER / ADVISORY split);
- **gate rate** — instances on which at least one BLOCKER was raised;
- **blocker-only recall** — recall restricted to BLOCKER findings;
- **the full per-instance paired difference distribution**, printed instance by instance
  and not summarised away, including how many instances are identical across all four
  replicates and how many move by more than 20 pp;
- **run-level shift versus per-instance noise** — an exact two-sided Wilcoxon signed-rank
  on each replicate pair's per-instance differences. Study 5 said n = 3 replicates could
  not distinguish "the run drifted" from "instances are noisy"; six pairs at n = 20 can
  put a p on it.

## 4. Arms, and what is held fixed

**One arm, replicated.** There is no comparison arm: the study measures a variance, not
a difference.

| | |
|---|---|
| arm | `cross` — `openai:gpt-5.6-terra`, the shipped auditor configuration |
| replicates | **K = 4**, labelled `noise-rep1..4` |
| what varies between replicates | **nothing the harness controls.** The provider layer exposes no seed and temperature comes from the model's capability card. What varies is provider nondeterminism. |

Held fixed, and checked rather than asserted:

| held fixed | how it is checked |
|---|---|
| the 20 drafts | sha256 per draft, recorded; `run_rejudge` refuses a draft whose digest does not match |
| CLEAR ground truth | **not recomputed.** Read back from study 3's `armB.round1.score.json`; 98 wrong items of 120, reproduced exactly by `noise_source.py` |
| the constitution | rubric-grade, sha256 `9f1ee353ec4cb05e…` — byte-equal to study 3's and study 5's; `noise_source.py` aborts if it has drifted |
| the corpus | sha256 `0b525eae93aab406…`, verified at every run start |
| **the audit prompt** | the digest is computed **offline, before any model call**, and stored in the source record; every replicate reports `prompt_digest_matches_source` per instance. A mismatch is a deviation, reported, and that instance is excluded |
| checks profile / N/A policy / rounds | `general` / literal / one round |

## 5. n, and why this n

**n = 20 instances, 98 wrong rubric items, K = 4 replicates.**

- **20** is not a power calculation. It is *the entire arm-X sample of study 3* — the
  exact drafts, the exact ground truth, and the exact denominator (98) on which the
  23.5% this floor is meant to judge was computed. A floor measured on other material at
  another n would have to be transported to that claim by assumption; this one does not.
- **K = 4** because K = 2 yields one difference and no interval on the spread, and K = 3
  (study 5's choice) yields three, from which an SD is an unstable estimate — study 5's
  own Deviation 10 says so. K = 4 yields **6 pairwise comparisons** and 6 × 20 = 120
  paired per-instance observations, and at the measured per-replicate cost it fits the
  budget. K > 4 was not chosen because the budget is the binding constraint, not the
  estimator.

## 6. The kill condition, stated before the run

> **If the spread of the aggregate round-one recall exceeds ~8 recall points, then no
> prose recall experiment at n = 20 in this plan is interpretable.**

Operationalised, so it cannot be argued about afterwards:

**KILL fires iff `range = max − min` of the pooled micro round-one recall across the four
replicates, under the adjudicator mapping, exceeds 8.0 percentage points.**

Range, not SD, because "spread" in the brief means what a reader means by it, and a range
cannot be softened by a modelling choice. SD, 2·SD and the bootstrap intervals are
reported alongside; they do not decide the kill.

**If KILL fires it is the headline of the report**, stated in the first sentence, in those
terms, and it is not framed as a partial success. It is a legitimate result: it says this
line of measurement needs a larger n or a different estimand, and it retires every n = 20
recall claim resting on the current design.

A second, non-kill verdict is registered here too, because it is the reason the study was
commissioned: **study 3's +21.5 pp (2.0% → 23.5%) survives iff 21.5 > 2·SD of this floor.**
Study 5 judged it against 2·SD ≈ 8.2 pp derived at n = 8; this study re-judges it at the
n it was measured at.

## 7. Stopping rule

- Four replicates, **or** US$2.00 of measured spend, whichever comes first. Spend is read
  from the product's own usage ledger after each replicate; a replicate is not started if
  the ledger says it cannot be paid for.
- A replicate that cannot complete all 20 instances is **excluded from the aggregate
  spread statistics** (1–3 above), which require a common denominator, and reported as a
  deviation with its own n. The per-instance analysis (4) then uses the instances every
  included replicate covers.
- No instance is dropped after its numbers are seen. The exclusion rules above are the
  only ones, and they are mechanical.

## 8. Analysis, fixed now

- **Intervals:** 20 000-resample percentile bootstrap, resampling **instances** (the unit
  of independence), seed `20260930`, so every interval is a deterministic function of the
  committed rows. Rates carry Wilson intervals.
- **Tests:** exact two-sided Wilcoxon signed-rank on paired per-instance differences,
  ties dropped, exact by enumeration at ≤ 20 usable pairs.
- **Multiplicity:** this is the seventh study on `T03MaterialSEG` and the same 50 rows.
  Six replicate-pair Wilcoxons are run; they are secondary and are reported with their
  count. The primary outcome is a spread, not a test, and has no p value.
- **No p value decides the kill.** §6 does.

## 9. Method, and what is reused rather than rebuilt

The replay is `premise.py --rejudge`, **unchanged**, with `--arms cross`. That is the same
code path study 5's 2.59 pp was measured with, which is what makes the two numbers
comparable rather than merely adjacent. `adjudicate.py` is used unchanged for the model
mapping. The only new executable code is:

- `noise_source.py` — presents study 3's archived arm-X run in the shape `--rejudge`
  reads, recomputes and pins the audit prompt digest offline, and refuses to proceed if
  the seeded sample, the corpus or the constitution has moved;
- `noise_report.py` — arithmetic over the committed JSONL rows. No model calls.

**Known and recorded in advance:** `premise.judge_once` is the product's audit path with
`heterogeneity()` removed and nothing else removed — study 5 proved 30/30 prompt-digest
equality with the product's own `run_audit` on the same commits. For this study's single
`cross` arm that guard would pass anyway, so the removal changes nothing here; it is
listed because a difference from `run_audit` exists and must not be discovered later.

## 10. Licence constraint

The ExpertLongBench corpus is CC BY-NC-SA 4.0, non-commercial, no redistribution. Drafts
and prompts quote it and live only under the gitignored `runs/`. What is committed is
ids, digests, scores and counts.

## 11. What this study will not be allowed to claim

- Not "the first prose noise floor". It is the better-powered audit-only one (§0).
- Not a bound on any study in which generation varies.
- Nothing about tasks other than `T03MaterialSEG`, about the shipped general
  constitution, about vendor pairs other than `anthropic → openai`, or about rounds after
  the first.

---

**Frozen at the commit that carries this file.** `git status --porcelain` at freeze and
the per-file digests are recorded in each replicate's `manifest.json`.
