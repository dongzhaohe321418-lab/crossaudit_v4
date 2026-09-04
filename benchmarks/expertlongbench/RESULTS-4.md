# T03MaterialSEG — **the growth budget does not repair the revision defect. It bounded growth exactly as designed and the revision delta got worse: −7.58 F1 against the control's −2.14**

> **Withdrawn 2026-09-05 — see `../CORRECTIONS.md`.** This report's primary
> outcome conditions on a post-treatment variable: it keeps only instances where
> the loop revised, while the treatment itself decides whether a revision is
> committed. The arms therefore hold different subsets (control 9 revised,
> treatment 11, only 7 in both), and the headline's "16 paired instances" is not
> true of that statistic. Recomputed over all 16 assigned pairs the effect is
> **−4.01 F1, 95% CI [−16.54, +8.33], p = 0.68** — not distinguishable from zero,
> against the **−19.60** below. Read everything here as exploratory.

**The preregistered hypothesis is false, in the direction opposite to the
prediction.** The 25% document-growth budget was supposed to move the paired
within-instance revision delta *up*. On 16 paired instances it moved it *down*:

| | paired revision delta | 95% CI | exact p | n |
|---|---:|---|---:|---:|
| **C — control**, tip behaviour | **−2.14 F1** | [−19.75, +10.74] | 0.8750 | 9 revisions (4 usable) |
| **T — treatment**, +25% budget | **−7.58 F1** | [−15.91, +2.78] | 0.2109 | 11 revisions (8 usable) |
| between arms (unpaired means) | **−5.44 F1** | | | |
| **paired on the 7 instances revised in BOTH arms** | **−19.60 F1** | **[−39.37, −1.19]** | 0.1562 | 7 (1 better, 6 worse) |

The mechanism did what it was built to do, and that is what makes the result
informative rather than a bug report. **The screen bound growth perfectly**: 0 of
13 committed revision rounds in arm T exceeded 25% (max **+22.4%**), against 4
of 14 in the control (max **+86.5%**); mean word churn fell from 42.3% to 19.1%.
**The bound held and the work got worse.**

**It does not beat the −6.20 floor my own exploratory replay predicted — it lands
just below it, at −7.58.** The replay said the revisions the screen leaves alone
average −6.20; the treatment reproduced that number rather than improving on it,
which is the outcome the replay's most pessimistic reading allowed and the one I
did not expect.

**The gain is not hidden audit silence — there is no gain to hide.** Auditor
round-one recall went *up*, 19.0% → 21.2%; adjudicated precision went *down*,
84.6% → 69.0%. Final output F1 fell 12.29 → 9.47 (paired −2.82, CI [−12.05,
+3.85], p = 0.703). Round-one drafts are indistinguishable, as they must be
(+1.19, p = 0.939): neither arm changes what the writer sees on a blank page.

**The honest caveat is larger than the effect.** Arm C's own primary number
moved from **−14.81** (at n = 9, before the arm was completed) to **−2.14** (at
n = 16), and study 3's comparable arm read **−14.42**. The control estimate
wanders across a 13-point range depending on which instances are in it. The
between-arm difference is of the same order as that instability, and this study
ran each arm once, so it cannot separate them. **Read the direction, not the
magnitude.**

**Study spend $8.18** of US$12: $7.49 on the analysed arms, $0.69 on two
launches discarded before any score was read.

Preregistered at `study4/PREREGISTRATION.md` (`f8623b2`), before the analysed
run's first model call. Provenance `study4/manifest.json`; evidence
`study4/records.jsonl`, 40 rows, one per instance per arm. Conforms to
`benchmarks/EXPERIMENT_RECORD.md`.

---

## 1. The claim, as registered

> The 25% document-growth budget added in `21f37d5` moves the paired
> within-instance revision delta on T03MaterialSEG **up** relative to tip
> behaviour, **without** reducing the auditor's round-one recall or its
> adjudicated precision.

**Primary outcome**: the paired within-instance revision delta in CLEAR F1.
**Verdict: falsified on the first clause.** The delta moved down, by 5.44 F1
between arm means and by 19.60 F1 paired on the instances both arms revised.
The second clause held for recall (up) and failed for precision (down).

## 2. What ran

| arm | product code | constitution | n attempted | **n scored** | model calls |
|---|---|---|---:|---:|---:|
| **C** control | `63ab94c` | rubric-derived | 16 | **16** | 62 |
| **T** treatment | `21f37d5` | rubric-derived, byte-identical | 16 | **16** | 66 |
| **G** split + general | `63ab94c` | shipped `GENERAL_AUDIT_RULES.md` | 8 | **8** | 16 |

Zero failed instances in the analysed run. The benchmark harness (`run.py`,
`clear.py`, `adjudicate.py`, `provider.py`, `tasks.py`, `stats.py`) is
sha256-identical across the two worktrees, recorded in `manifest.json`, so C and
T differ only in the five product files `21f37d5` touched.

## 3. Results

### 3.1 Per arm

| | arm C | arm T | arm G |
|---|---:|---:|---:|
| n scored | 16 | 16 | 8 |
| round-one draft F1 | 13.49 | 14.68 | 24.50 |
| final output F1 | **12.29** | **9.47** | 24.50 |
| instances revised | 9 / 16 | 11 / 16 | **0 / 8** |
| rubric items fixed / broken | 3 / 4 | 3 / **6** | 0 / 0 |
| **paired revision delta** | **−2.14** [−19.75, +10.74] | **−7.58** [−15.91, +2.78] | — |
| auditor round-one recall | 19.0% (16/84) | 21.2% (18/85) | **0.0%** (0/37) |
| auditor precision (adjudicated) | 84.6% (22/26) | 69.0% (20/29) | — (0 findings) |
| committed revision rounds | 14 | 13 | 0 |
| — mean per-round growth | +21.6% | **+14.6%** | — |
| — max per-round growth | **+86.5%** | **+22.4%** | — |
| — rounds over the 25% bound | **4** | **0** | — |
| mean word churn per revision | 42.3% | **19.1%** | — |
| exit codes | 14×`0`, 2×`11` | 13×`0`, 3×`11` | 8×`0` |
| cost | $3.35 ($0.209/inst) | $3.46 ($0.217/inst) | $0.68 ($0.085/inst) |

The bound is **per repair round**, not cumulative. Arm T's largest round-one-to-
final growth is +30.8% across two bounded rounds, which is correct behaviour and
worth stating so the "0 over 25%" row is not misread.

### 3.2 The instances revised in both arms — the sharpest comparison

| instance | arm C Δ | arm T Δ | T − C |
|---|---:|---:|---:|
| `adfm.201000591` | −25.0 | **0.0** | **+25.0** |
| `adfm.202002249` | 0.0 | −16.7 | −16.7 |
| `cnma.202200403` | **+40.0** | −25.0 | **−65.0** |
| `jbm.a.36681` | 0.0 | −25.0 | −25.0 |
| `smll.201800441` | 0.0 | −16.7 | −16.7 |
| `zaac.202200095` | 0.0 | −22.2 | −22.2 |
| `sciadv.adj5431` | 0.0 | −16.7 | −16.7 |

Six of seven worse. **Five of the six are instances where the control's revision
was a harmless no-op (Δ = 0.0) and the treatment's bounded revision destroyed an
item.** That is the mechanism of the negative result: the budget did not turn bad
revisions into good ones, it turned *inert* ones into small damaging ones.

### 3.3 Where the change did work, exactly as designed

`ange.202112688` is the case the whole change was built for. Under the control
the revision grew the document **+110.1%** and the score fell **90.9 → 40.0**, a
−50.9 F1 loss — the single worst revision in the study. Under the treatment the
screen refused it, the loop stopped at round one, and the draft's **57.1 F1 was
kept intact**. Two more arm-T instances ended the same way (`adfm.202002249`,
`smll.202408072`; 3 × exit `11` against the control's 2).

So the change prevents the catastrophic case and creates a diffuse one. On this
task and this n, the diffuse cost is larger than the catastrophic benefit.

### 3.4 Arm G — the control the owner was owed

**Merging the rules split did not measurably hurt projects that have not written
rubric-grade rules, and did not help them either.** Paired on the same 8
instances against study 3's arm S (shipped code, same general rules):

| | arm S (study 3, `dc446ae`) | arm G (study 4, `63ab94c`) | paired Δ |
|---|---:|---:|---|
| round-one draft F1 | 26.74 | 24.50 | −2.23, CI [−11.11, +7.14], p = 0.6875 |
| final output F1 | 26.74 | 24.50 | −2.23, CI [−11.11, +7.14], p = 0.6875 |
| audit fired on | 1 / 8 | **0 / 8** | |
| round-one recall | 0.0% (0/36) | **0.0%** (0/37) | |

Draft and final are identical within each arm because **neither arm revised
anything**: under general rules the audit is silent, before the split and after
it. The −2.23 F1 difference has a CI spanning zero on n = 8 and cannot exclude a
moderate harm in either direction. The plain answer to the question: **no
evidence of harm; the audit was already near-silent and remains so.**

## 4. Analysis, as registered

- **Test**: exact two-sided Wilcoxon signed-rank on within-instance paired
  differences, ties dropped and counted.
- **Effect size**: mean paired difference in F1 with a BCa bootstrap 95% CI,
  20 000 resamples, seed `20261104`.
- **Implementation validated against a published number**: on study 3's 25
  pooled revisions it reproduces mean −11.01, SE 2.47, exact p = 0.0014, 17
  usable pairs — exactly `RESULTS-3.md`.
- **Comparisons this study made: 6**, enumerated by `study4/analyse.py`. The
  primary outcome was named in advance. §3.2 and §3.3 are readings of the
  primary outcome's own rows, not new tests.
- **This is the fourth study over one task.** Four studies, one dataset, one
  domain; that is part of the multiple-comparison picture.
- **Noise floor — measured this time, and it is the dominant term.** The same
  control configuration read **−14.42** (study 3, n = 20), **−14.81** (this
  study at n = 9) and **−2.14** (this study at n = 16). A between-arm difference
  of 5.44 F1 sits well inside that spread. **No causal claim about the
  magnitude is licensed. The direction — the treatment is not better — is what
  this study supports, and it is supported by 6 of 7 paired instances moving the
  same way.**

## 5. Exploratory — the Phase-1 diagnosis (NOT preregistered)

Computed on **study 3's** run directories, data gathered for a different
question and chosen after looking at it. `study4/exploratory.py` regenerates it.
It generated the hypothesis; this study tested it, and the test came out
negative.

| | n = 25 revisions |
|---|---|
| paragraph blocks surviving byte-identical | 335 of 422 (79.4%); 72 modified, 15 deleted |
| r(characters preserved, ΔF1) | +0.077, 95% CI [−0.285, +0.490] |
| r(largest per-round net word growth, ΔF1) | −0.395, 95% CI [−0.680, −0.044] |
| r(number of findings, ΔF1) | −0.013, 95% CI [−0.599, +0.337] |
| broken items losing CLEAR's precision half | 16 of 17 |
| broken items named by the finding being answered | 10 of 17 |

Split at 25% growth, **fitted on that same data**: ≤ 25% → n = 13, mean −6.20,
3 fixed, 6 broken; > 25% → n = 12, mean −16.22, 0 fixed, 11 broken.

**What the held-out test says about it.** The correlation was real and the
threshold separated study 3's revisions cleanly, and *neither fact transferred*.
Arm T is the counterfactual replay's optimistic reading made real — every
revision under the bound — and it scored −7.58, marginally worse than the −6.20
the replay predicted for exactly that population. The correlation was between
growth and damage in observational data; the intervention shows growth was not
the thing to cut. **A screen fitted on 25 observations, with an interval that
barely excluded zero, did not survive contact with a fresh 16.** That is the
most transferable finding here and it is about method, not about revision.

## 6. Deviations, numbered, with the direction each could bias

Deviations 1–8 are as filed in the previous revision of this file and stand.
New:

9. **The generator account exhausted its credit mid-study**, after arm C's 9th
   scored instance, voiding arms T and G entirely. Credit was restored and the
   arms re-run from empty run directories. **No score from the voided attempts
   entered anything** — arms T and G had produced none. Bias: none from the
   voided data; see 10 for the consequence to arm C.
10. **Arm C was completed to its preregistered n = 16 after its n = 9 numbers
    were known** (−14.81). The 7 added instances are the ones the credit failure
    killed; which instances they are is fixed by the seed and could not be
    chosen, and their scores could not be seen in advance. `--resume` skips any
    *recorded* instance including failures, so the 7 unscored rows were removed
    from `results.json` and their directories moved to
    `_failed_before_completion/` before resuming; `results.before-completion.json.bak`
    preserves the prior state. **Direction of bias: this is the deviation most
    open to challenge.** Completing a registered n after seeing a partial result
    is defensible — leaving it at n = 9 would have kept a non-random gap (the
    last 7 by id) — but a reader is entitled to both numbers, so both are given:
    arm C reads **−14.81 at n = 9** and **−2.14 at n = 16**. The treatment is
    worse than the control on *either*, so the conclusion does not turn on this
    choice.
11. **Arm T ran before arm C's completion**, so the two arms' calls are not
    interleaved in time (T 15:44–16:37 UTC, C's completion 16:49–17:14). A
    provider-side drift between those windows would confound the comparison and
    cannot be ruled out.
12. **Arm G is n = 8 and compared against a study-3 arm**, so it is a
    cross-study comparison with different code for the *harness's* surrounding
    months, not a within-study arm. Its paired instances are identical, but its
    control was measured under study 3's conditions.
13. **The 25% bound remains fitted on study 3's data** (§5). This study is its
    held-out test and it failed.

## 7. Limitations

- **The CLEAR scorer is a reimplementation from the paper.** No evaluation code
  was released, so it has never been diffed against the authors'. Every F1 here
  inherits that, including the primary outcome's instrument.
- **The outcome is model-judged.** Mapper, judge and adjudicator are
  `openai:gpt-5.6-terra`, the same model as the auditor. "−7.58 F1" is a
  *model-judged* difference.
- **Run-to-run spread exceeds the effect** (§4). This is the limitation that
  most constrains what may be said.
- **Vendor independence is not statistical independence.** Different vendors
  reduce correlated error; neither model is an independent oracle.
- **One task is one task.** Everything here is T03MaterialSEG.
- **n = 16 per arm, 9–11 revisions per arm.** The preregistration noted this
  detects roughly a 10 F1 shift; smaller true effects are invisible here.

## 8. Cost, from the usage ledger

| | generation + audit | CLEAR scoring | total | per instance |
|---|---:|---:|---:|---:|
| arm C (16) | $1.93 | $1.41 | **$3.35** | $0.209 |
| arm T (16) | $2.20 | $1.26 | **$3.46** | $0.217 |
| arm G (8) | $0.36 | $0.32 | **$0.68** | $0.085 |
| discarded launches (deviations 1, 2) | | | **$0.69** | — |
| **study total** | | | **$8.18** of $12.00 | |

Tokens: arm C 215 093 in / 89 236 out; arm T 240 189 in / 101 729 out; arm G
45 142 in / 15 851 out. Mean wall per instance: C 113 s, T 129 s, G 43 s. All
read from the ledger, not reconstructed.

## 9. What this licenses

**It licenses:**

1. **The growth budget does not repair the revision defect on this task.** Six
   of seven paired instances moved the wrong way; the arm mean moved 5.44 F1 the
   wrong way; it does not beat the −6.20 floor.
2. **The screen itself works.** 0 of 13 revision rounds over the bound against
   the control's 4 of 14; churn halved. The negative result is about the idea,
   not the implementation.
3. **Bounding growth converts inert revisions into damaging ones** (§3.2) while
   preventing the rare catastrophe (§3.3).
4. **The audit was not silenced**: recall 19.0% → 21.2%.
5. **The rules split did not measurably harm general-rules projects** (§3.4),
   on n = 8 with a CI that cannot exclude a moderate effect.
6. **The instrument's run-to-run spread is large** — the same control reads
   −14.42, −14.81 and −2.14 — and any future study on it needs replicate arms.

**It does not license:**

- Any claim about the *size* of the treatment's harm. The CI on the paired
  sub-analysis is [−39.37, −1.19] on n = 7, and the noise floor is comparable.
- Any claim that revision is now understood. Study 3's diagnosis said growth
  predicts damage; cutting growth did not cut damage. **The cause is still open.**
- Anything about tasks other than T03MaterialSEG, or about `repair.max_document_growth`
  on deliverables that are not expert prose.

## 10. What was done about it

**`repair.max_document_growth` now defaults to 0 — off (`c5e3920`).** The study
says the 0.25 default is not earned, so it was withdrawn rather than shipped
with a caveat. The knob and `DEFAULT_MAX_DOCUMENT_GROWTH = 0.25` remain, because
the one effect the study does establish is real: the screen prevented this
study's single worst revision (§3.3). A project whose failure mode is the
catastrophic rewrite can switch it on; a default should not be a setting the
project's own benchmark calls a net loss. The measured artefact `21f37d5` is
untouched, so this file's numbers still describe code that exists.

The open problem is the mechanism §3.2 exposes: revisions that change the document at all, at any size, break correct
items more often than they fix wrong ones — in arm T, 3 fixed against 6 broken
under a bound that worked. That points at *whether to revise*, not at *how much
to write*, and it is a different change from this one — one this study does not
attempt and does not pre-judge.

## 11. Reproduction

```sh
export PYTHONPATH="$(git rev-parse --show-toplevel)/src"
set -a && . ~/.crossaudit-keys.env && set +a
export CROSSAUDIT_OPENAI_KEY="$CROSSAUDIT_AUDITOR_KEY"
export CROSSAUDIT_ANTHROPIC_KEY="$CROSSAUDIT_GENERATOR_KEY"
export https_proxy=http://127.0.0.1:7897
python benchmarks/expertlongbench/fetch.py         # corpus, not redistributed here
R=benchmarks/expertlongbench/runs
git checkout 63ab94c   # control product code
python benchmarks/expertlongbench/run.py --task T03MaterialSEG --n 16 --seed 20261104 \
    --arms B --audit-rules rubric --label C-control --out "$PWD/$R/armC-control"
python benchmarks/expertlongbench/run.py --task T03MaterialSEG --n 20 --seed 20260930 \
    --subset 8 --arms B --audit-rules general --label G-split-general \
    --out "$PWD/$R/armG-split-general"
git checkout 21f37d5   # treatment product code
python benchmarks/expertlongbench/run.py --task T03MaterialSEG --n 16 --seed 20261104 \
    --arms B --audit-rules rubric --label T-scoped --out "$PWD/$R/armT-scoped"
python benchmarks/expertlongbench/study4/emit_record.py C=... log:C=... T=... G=...
python benchmarks/expertlongbench/study4/analyse.py
python benchmarks/expertlongbench/study4/exploratory.py
```

Budget about $7.50 of *generator* balance for the three arms at the measured
per-instance cost, and check it before starting: this study lost two launches to
an account emptying mid-run.
