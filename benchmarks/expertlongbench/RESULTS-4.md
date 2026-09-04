# T03MaterialSEG — **the treatment arm did not produce a single scored instance: the generator's Anthropic credit ran out mid-study.** The primary outcome is unmeasured

**The change this study exists to test has no number.** Arm T (the 25% document
growth budget) attempted all 16 instances and scored **0**, because the
generator account returned

```
HTTP 400  invalid_request_error
"Your credit balance is too low to access the Anthropic API."
```

on every call. Arm G (the split-code/general-rules control the owner is owed)
scored 0 for the same reason. The control arm, which ran first, spent the last
of the balance and itself completed only **9 of 16** instances.

So the one preregistered number this study can report is the **control's own**
paired within-instance revision delta, on **n = 4 revisions**:
**−14.81 F1, 95% CI [−44.43, +6.25], exact Wilcoxon p = 0.5000** (3 usable pairs
after 1 tie). It reproduces the *direction and size* of study 3's arm X
(−14.42) on a fresh seed and fresh samples, on an interval so wide it excludes
almost nothing. **It is a replication of the defect, not a test of the fix.**

One preregistered secondary outcome did land cleanly and is worth the run:
**the control grew its deliverable by a mean of +28.8% per committed revision
round, with 3 of 7 transitions above 25% and a maximum of +86.5%** — the
mechanism the change was built to bound, reproduced prospectively on data
gathered after the diagnosis was written down.

**Study spend $2.41** of a US$12 budget: $1.72 on the analysed run, plus $0.69
on two launches discarded before any score was read (Deviations 1 and 2).

This study conforms to `benchmarks/EXPERIMENT_RECORD.md`. Its claim was
registered in advance at `study4/PREREGISTRATION.md`; its provenance is
`study4/manifest.json`; its per-instance evidence is `study4/records.jsonl`,
40 rows, one per instance per arm, **including every failed instance**.

---

## 1. What was claimed in advance

Registered in `study4/PREREGISTRATION.md`, committed at `f8623b2` before the
first model call of the analysed run:

> The 25% document-growth budget added in `21f37d5` moves the paired
> within-instance revision delta on T03MaterialSEG **up** relative to tip
> behaviour, **without** reducing the auditor's round-one recall or its
> adjudicated precision.

**Primary outcome**: the paired within-instance revision delta in CLEAR F1
(final committed output minus round-one draft, averaged over revised instances).
**Verdict: not measured.** The arm that would answer it produced no data.

## 2. Provenance

`study4/manifest.json` carries: the frozen shas with `git status --porcelain`
empty at freeze (control `63ab94c`, treatment `21f37d5`, report tree
`f8623b2`+); the five product files the change touched; sha256 of the six
harness files, **identical across both worktrees**, so the arms could differ
only in the product; the dataset digest, row count and licence; every model id
and role; the seed and how sampling derives from it; each arm's attempt history
and UTC start/end; Python 3.13.5 on macOS-26.6.2-arm64.

Raw run directories stay gitignored. Their absolute paths and a directory-level
sha256 are in `study4/rundirs.sha256`, so the raw material can be produced on
request without publishing corpus text.

## 3. What ran, and what it produced

| arm | code | attempted | **scored** | model calls | why the gap |
|---|---|---:|---:|---:|---|
| **C** control, rubric rules | `63ab94c` | 16 | **9** | 32 | generator credit exhausted part-way |
| **T** treatment, +25% budget | `21f37d5` | 16 | **0** | 0 | generator credit exhausted before round 1 |
| **G** split code, general rules | `63ab94c` | 8 | **0** | 0 | same |

Every attempted instance is a row in `records.jsonl`, failures included, with
its error string and `calls: 0`. No instance was dropped silently.

### Arm C — the only arm with data

| | value | n |
|---|---:|---:|
| round-one draft CLEAR F1 | 20.29 | 9 |
| final output CLEAR F1 | 13.70 | 9 |
| instances revised | 4 of 9 | 9 |
| rubric items fixed / broken by revision | **1 / 4** | 4 |
| **paired revision delta (PRIMARY instrument)** | **−14.81 F1**, 95% CI **[−44.43, +6.25]**, exact Wilcoxon **p = 0.5000** | 4 (3 usable, 1 tie) |
| auditor round-one recall vs CLEAR | 11.4% (5/44) | 9 |
| auditor precision (adjudicated) | 66.7% (8/12) — 8 confirmed, 4 false positive | 12 |
| **committed growth per revision round** | mean **+28.8%**, max **+86.5%**, **3 of 7** transitions over 25% | 7 |
| exit codes | 8× `0`, 1× `11` | 9 |
| cost | $0.98 generation+audit + $0.74 CLEAR = **$1.72** ($0.191/instance) | 9 |
| tokens | 109 847 in, 44 975 out; mean wall 103 s | 9 |

**The interval is the honest headline here.** A 95% CI of [−44, +6] on four
revisions is compatible with a large harm, no effect, and a modest benefit at
once. What it does do is fail to contradict study 3, whose pooled estimate on 25
revisions was −11.01, 95% CI [−15.22, −5.67] (that interval computed here; study
3 reported the point estimate and SE only).

The **growth** row is the result that survives the small n, because it is a
property of every committed round rather than of four paired scores: under tip
behaviour, on samples drawn after the diagnosis was fixed in writing, revisions
grew the deliverable by a mean of 28.8% and nearly half the transitions exceeded
the bound the treatment would have enforced. The mechanism replicated; the
remedy went untested.

## 4. Analysis, as registered

- **Test**: exact two-sided Wilcoxon signed-rank on within-instance paired
  differences, ties dropped and counted. Paired because both numbers come from
  the same instance, generator and scorer.
- **Effect size and interval**: mean paired difference in F1 points with a BCa
  bootstrap 95% CI, 20 000 resamples, seed `20261104`.
- **Implementation validated against a published number**: on study 3's 25
  pooled revisions this code reproduces mean −11.01, SE 2.47, exact p = 0.0014,
  17 usable pairs — exactly `RESULTS-3.md`.
- **Comparisons this study made: 4**, listed by `study4/analyse.py`. Three of
  them (`round-1 draft`, `final output`, `revision delta in both arms`) returned
  n = 0 because arm T has no data. The primary outcome was named in advance, not
  selected after looking.
- **This is the fourth study over one task.** That history is part of the
  multiple-comparison picture and is stated here rather than left to a reader to
  reconstruct.
- **Noise floor: unknown.** Each arm ran once. This study cannot say what the
  same configuration does twice, so it cannot say whether −14.81 is
  distinguishable from run-to-run spread. Registered as a limitation in advance.

## 5. Exploratory — the Phase-1 diagnosis (NOT preregistered)

Computed on **study 3's** run directories, data gathered for a different
question, and chosen after looking at it. `study4/exploratory.py` regenerates
all of it. It generated the hypothesis above; it does not test it.

| | n = 25 revisions |
|---|---|
| paragraph blocks surviving byte-identical | 335 of 422 (**79.4%**); 72 modified, **15 deleted** |
| mean characters of the round-one draft preserved | 0.957 |
| r(characters preserved, revision ΔF1) | **+0.077**, 95% CI [−0.285, +0.490] |
| r(largest per-round net word growth, ΔF1) | **−0.395**, 95% CI [−0.680, −0.044] |
| r(number of findings, ΔF1) | −0.013, 95% CI [−0.599, +0.337] |
| revisions that grew the deliverable | 24 of 25 |
| broken items losing CLEAR's *precision* half | 16 of 17 |
| broken items **named by the finding being answered** | 10 of 17 |

Split at 25% growth (**a threshold fitted on this same data**): ≤ 25% → n = 13,
mean −6.20, 3 fixed, 6 broken; > 25% → n = 12, mean −16.22, **0 fixed, 11
broken**.

**Counterfactual replay** (exploratory, and not a result): the screen would have
refused 12 of study 3's 25 revisions, carrying 0 fixes and 11 breaks, and left
the 13 that carried all 3 fixes — whose mean is **−6.20 F1**. That is the floor
the treatment must beat, and **this study cannot say whether it does.** What the
12 re-asks would have written is unknown.

Only the growth correlation excludes zero, and only just. The preservation
correlation's interval spans from a moderate negative to a moderate positive: the
claim "how much of the old text survives does not predict the outcome" rests on
an interval that does not exclude a real relationship in either direction. The
qualitative facts underneath it — 15 blocks deleted out of 422, 24 of 25
revisions growing — carry more than the coefficient does.

## 6. Deviations, numbered, with the direction each could bias

1. **A first launch (parallel arms) hit `insufficient_quota` on the OpenAI side
   and was abandoned.** ~$0.03, zero instances recorded, run directory deleted.
   No bias: no data entered anything.
2. **A second launch of arm C ran 3 of 16 instances and was killed** when
   `EXPERIMENT_RECORD.md` landed, so the preregistration could be committed
   before any model call of the analysed run. $0.66, written off, run directory
   deleted rather than merged. **No score from it was read** — only dollar
   costs. No bias, but it is why the analysed run's first call is later than the
   study's first call.
3. **The generator account exhausted its credit mid-study**, after arm C's 9th
   scored instance. This is the reason arms T and G have no data and arm C is
   n = 9 of 16. **Direction of bias: unknown and possibly non-random.** The 7
   lost arm-C instances are the *last 7 by id* of the seeded draw, not a random
   subset, so arm C's numbers are a sample of the first 9 by id and not an
   unbiased sample of 16.
4. **Arm C was retried twice with `--resume`.** Both retries failed for reason 3.
   `--resume` rewrites `plan.json`, so that file's `started_utc` is the last
   attempt's; the true attempt history is in `manifest.json.arms.C.attempts`
   (first call `20260904T142912Z`). No bias — a retry only decides which seeded
   samples still need running.
5. **The primary outcome is reported at n = 4 revisions**, far below the ~13 the
   preregistration expected from n = 16. The stopping rule was budget; what
   stopped it was a credential. Reported as registered rather than pooled with
   study 3 to reach a nicer n, which would be a different claim.
6. **The 25% bound is fitted on study 3's data** (§5). Arms C and T were its
   held-out test; the test did not run.
7. **A concurrent unrelated benchmark (`premise.py`) was running on the same two
   credentials** during this study. It did not touch these run directories or
   ledgers, but it competed for the same balance and plausibly accelerated
   deviation 3.
8. **An arithmetic error of mine was corrected mid-study**, before any study-4
   score was read: the block-preservation figure was published as 299/422 (71%)
   and is 335/422 (79.4%). Direction: the correction *strengthens* the claim it
   supports, which is why it is flagged here rather than quietly amended.

## 7. Limitations

- **The CLEAR scorer is a reimplementation from the paper.** The authors
  released no evaluation code, so it has never been diffed against theirs. Every
  F1 in this file, including the primary outcome's instrument, inherits that.
- **The outcome is model-judged.** The mapper, judge and adjudicator are
  `openai:gpt-5.6-terra`, the same model as the auditor. −14.81 F1 is a
  *model-judged* difference, said in the same sentence as the number.
- **Vendor independence is not statistical independence.** The generator and
  auditor come from different vendors, which reduces correlated error; it does
  not make either an independent oracle.
- **One task is one task.** Everything here is about T03MaterialSEG.
- **n = 9 scored instances, 4 revisions.** No conclusion about the treatment is
  available at any n, because the treatment produced nothing.

## 8. Cost, from the usage ledger

| | generation + audit | CLEAR scoring | total | per instance |
|---|---:|---:|---:|---:|
| arm C (9 scored) | $0.98 | $0.74 | **$1.72** | $0.191 |
| arm T (0 scored) | $0.00 | $0.00 | $0.00 | — |
| arm G (0 scored) | $0.00 | $0.00 | $0.00 | — |
| discarded launches 1–2 | | | **$0.69** | — |
| **study total** | | | **$2.41** of $12.00 | |

Tokens for arm C: 109 847 in, 44 975 out, 32 model calls plus CLEAR scoring.
All figures are read from the ledger, not reconstructed.

## 9. Reproduction

Needs credit on **both** accounts — that is the whole lesson of this run.

```sh
git checkout 21f37d5                       # treatment product code
export PYTHONPATH="$(git rev-parse --show-toplevel)/src"
set -a && . ~/.crossaudit-keys.env && set +a
export CROSSAUDIT_OPENAI_KEY="$CROSSAUDIT_AUDITOR_KEY"
export CROSSAUDIT_ANTHROPIC_KEY="$CROSSAUDIT_GENERATOR_KEY"
export https_proxy=http://127.0.0.1:7897
python benchmarks/expertlongbench/fetch.py     # corpus, not redistributed here
R=benchmarks/expertlongbench/runs
# control at 63ab94c, treatment at 21f37d5, the identical 16 samples
python benchmarks/expertlongbench/run.py --task T03MaterialSEG --n 16 --seed 20261104 \
    --arms B --audit-rules rubric --label C-control --out "$PWD/$R/armC-control"
python benchmarks/expertlongbench/run.py --task T03MaterialSEG --n 16 --seed 20261104 \
    --arms B --audit-rules rubric --label T-scoped  --out "$PWD/$R/armT-scoped"
python benchmarks/expertlongbench/run.py --task T03MaterialSEG --n 20 --seed 20260930 \
    --subset 8 --arms B --audit-rules general --label G-split-general \
    --out "$PWD/$R/armG-split-general"
python benchmarks/expertlongbench/study4/emit_record.py C=... T=... G=...
python benchmarks/expertlongbench/study4/analyse.py
```

Budget the credit first: at $0.191/instance measured here, the three arms cost
about $7.60, and the run is worthless if either account empties part-way — as it
did.
