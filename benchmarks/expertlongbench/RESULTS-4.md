# T03MaterialSEG — the revision defect is diagnosed and the fix is built, but **the arms that would test it did not run: the OpenAI account has no credits**

**The measurement this study exists to report was not taken.** Every arm needs
`openai:gpt-5.6-terra` for the auditor, the CLEAR mapper, the judge and the
adjudicator, and that account returns

```
HTTP 429  insufficient_quota / credit_balance_exhausted
"You have no credits remaining."
```

on every request. The only other credential on this machine is the *generator's*
Anthropic key; scoring with it would mean the model under test grades its own
work, which does not measure anything. Both arms died on instance 1 of 16.
**Study spend: $0.03 of a US$12 budget** — one Anthropic generation call before
the first scoring call failed. Nothing was retried into a bill.

So this file reports what *was* measured — a diagnosis of the revision defect,
taken from study 3's own run directories with no new model calls — and states
plainly that the fix built on top of it is **unmeasured**.

Everything below is measured. Nothing is extrapolated. The one counterfactual
is labelled as one.

---

## What study 3 left on the table

> Pooled across 25 within-instance revisions, the post-revision output scored
> **11.0 CLEAR F1 below** the round-one draft it replaced, p = 0.0014, breaking
> **17** rubric items while fixing **3**.

The standing hypothesis was that the generator is handed the findings and
rewrites the whole document, losing correct content it was never asked to
touch. **The data refutes it.**

## Q1 — did the revision lose text it was not asked to touch?

Paragraph blocks of the round-one draft that reappear byte-identical in the
post-revision output, over all 25 revisions in arms S, R and X:

| | |
|---|---:|
| pre-revision paragraph blocks | 422 |
| present byte-identical after revision | 335 (**79.4%**) |
| modified in place | 72 (17%) |
| **outright deleted** | **15 (3.6%)** |
| newly added | 35 |
| mean share of round-one *characters* preserved | **0.957** |
| revisions preserving ≥ 99% of round-one characters | 10 of 25 — which still broke **7** of the 17 items |
| **Pearson r (characters preserved, revision ΔF1)** | **+0.077** |

Ten of twenty-five revisions kept essentially every byte of the earlier draft
and lost rubric items anyway. How much of the old text survives predicts the
outcome not at all.

## Q2 — what does a revision actually do?

It grows the document.

| | |
|---|---:|
| revisions that grew the deliverable | **21 of 25** (1 shrank, 3 flat) |
| mean length ratio, characters | **1.27×**, up to 2.29× |
| **Pearson r (net word growth, revision ΔF1)** | **−0.395** |
| Pearson r (number of findings, ΔF1) | −0.013 |
| Pearson r (words inserted per finding, ΔF1) | −0.006 |

Split on per-round net word growth:

| | n | mean ΔF1 | items fixed | items broken |
|---|---:|---:|---:|---:|
| grew ≤ 25% | 13 | **−6.2** | **3** | 6 |
| grew > 25% | 12 | **−16.2** | **0** | **11** |

**Every revision that grew the deliverable by more than a quarter fixed nothing
and broke eleven items. All three of the fixes any revision achieved came from
revisions under that bound.** The per-arm split agrees: arm R — the only arm
whose revisions helped (+5.83 F1, 2 fixed, 0 broken) — grew its documents 1.08×;
arm X (−14.42, 1 fixed, 14 broken) grew them 1.40×.

Normalising growth by the number of findings destroys the correlation
(−0.006), so this is not "more findings, more writing". It is the writer
expanding the artefact whatever it was asked.

## Q3 — which half of the CLEAR score did the broken items lose?

CLEAR scores each item twice: `precision_hit` (the reference contains the
model's content for this item) and `recall_hit` (the response contains the
reference's).

| of the 17 broken items | |
|---|---:|
| lost `precision_hit` (alone or with recall) | **16** |
| lost `recall_hit` only | 1 |

Sixteen of seventeen lost the half that fails when the model writes content the
reference does not contain. That is the signature of added material, not of
removed material.

## Q4 — collateral damage, or the item it was told to fix?

`CA-RUBRIC-00N` maps 1:1 to rubric item *N* (the constitution is generated from
the rubric by `run.py:rubric_constitution`), so a finding names an item.

| | |
|---|---:|
| broken items a finding in that revision **named** | **10** |
| broken items no finding named (collateral) | 7 |
| fixed items a finding named | 1 of 3 |

The larger half of the damage is not collateral. It is the generator being told
"the deliverable does not justify the synthesis atmosphere", writing several
hundred words of plausible atmosphere chemistry, and **losing the very item it
was asked to repair**. The six broken `Atmosphere` items show it without a model
call — atmosphere keyword hits before → after the revision that broke the item:

```
adfm.202002249   6 → 23      anie.202410016   1 → 18
ange.202112688   6 → 21      celc.202200984   3 → 19
sciadv.adp3309   1 → 17      smll.202408072  19 → 22
```

## Q5 — were the 3 fixes clean, and is the damage concentrated?

The 3 fixes came from 2 revisions. One (arm R, `ange.202112688`, +23.3 F1, 13%
growth) fixed two and broke none — clean. The other (arm X, `pssb.201900312`,
10% growth) fixed one and broke one — a wash. The damage is not concentrated in
high-finding instances (r = −0.013 with finding count); it tracks growth.

## The diagnosis

> A revision keeps what is there and answers a finding **by adding prose**. The
> added prose is not supported by the source material, so it loses the item it
> was written for, and the more of it there is the worse the revision does.
> The loop had no bound on how much a repair may write.

The hole is where `repair_guard`'s own docstring said it was: code files carry a
200-line budget, documents are "never budgeted", and one line of prose is an
unbounded amount of prose.

---

## The change that is built and NOT measured

`repair.max_document_growth` (default 25%): a repair round whose staged document
grew past the bound is refused in both modes, rolled back to the audited commit,
and re-asked once with the reason; the generator is told the same number in the
revision prompt. Growth only — churn and deletion are deliberately unbounded,
because the data does not support bounding them.

**It has no benchmark number and this file will not pretend otherwise.** The
one thing that can be said without a model call is a *counterfactual replay* of
the screen over study 3's own revisions — which revisions it would have refused,
not what the re-ask would then have produced:

| | |
|---|---:|
| revision rounds over the 25% bound | 12 of 36 |
| revisions with at least one over-budget round | **12 of 25** |
| rubric items those 12 fixed / broke | **0 fixed, 11 broken** |
| rubric items the other 13 fixed / broke | 3 fixed, 6 broken (mean −6.20 F1) |

The screen would have fired on twelve revisions that between them repaired
nothing and destroyed eleven items, and left alone every revision that repaired
anything. **What those twelve would have produced on the re-ask is unknown, and
so is the effect on the final score.** The floor of the remaining 13 is −6.20 F1,
so even a perfect outcome on the refused twelve would leave the paired revision
delta negative, not at zero. The 25% threshold is also **fitted on this data**;
the arms would have been its out-of-sample test and they did not run.

## What this file licenses

**It licenses:**

1. The revision defect is **expansion, not deletion**. 79.4% of paragraphs survive
   byte-identical, 3.6% are deleted, and preservation is uncorrelated with the
   outcome (r = +0.08).
2. **Growth predicts the damage** (r = −0.40). Above 25% growth: 0 items fixed,
   11 broken. Below: all 3 of the study's fixes.
3. 16 of 17 broken items lost CLEAR's **precision** half — the model wrote what
   the reference does not contain.
4. 10 of 17 broken items were **named by the finding the revision was answering**.

**It does not license:**

- **Any claim that `repair.max_document_growth` improves anything.** It is
  unmeasured. The counterfactual above says which revisions it would have
  stopped, not what would have replaced them.
- Any claim about the merged rules split under a *general* constitution. That
  control (split code + shipped general rules, n ≈ 8, against study 3's arm S)
  was planned, budgeted and **not run**, for the same credit reason. The
  question the owner asked — whether merging the split hurt projects that have
  not written rubric-grade rules — is still open.
- Anything about tasks other than T03MaterialSEG.

## Deviations

Study 1's 1–14, study 2's 15–23 and study 3's 24–27 stand. Added:

28. **The study did not run.** `openai:gpt-5.6-terra` returns
    `insufficient_quota` / `credit_balance_exhausted` on every call, and it is
    the auditor, mapper, judge and adjudicator for every arm. Two arms of n = 16
    on a fresh seed (`20261104`), plus the n = 8 general-rules control on study
    3's seed, were launched at frozen shas — control `63ab94c`, treatment
    `21f37d5` — and each died on its first instance inside CLEAR scoring. Nothing
    was changed after the failure except this file. Spend $0.03.

29. **The first launch ran the two arms in parallel and was abandoned.** It hit
    the same 429 and was replaced by a serial chain before any instance was
    recorded; the 429 turned out to be quota, not concurrency. No arm, prompt,
    model, setting or scoring path differed between the two launches, and no
    instance from either was scored.

30. **The 25% bound is fitted on study 3's 25 revisions**, which is the same data
    Q2 reports it from. It is therefore a description of that data, not a
    validated threshold. The two arms above were its held-out test.

## To reproduce, when there are credits

```sh
export PYTHONPATH="$(git rev-parse --show-toplevel)/src"
python benchmarks/expertlongbench/fetch.py
R=benchmarks/expertlongbench/runs
# control at 63ab94c, treatment at 21f37d5, same 16 samples
python benchmarks/expertlongbench/run.py --task T03MaterialSEG --n 16 --seed 20261104 \
    --arms B --audit-rules rubric --label C-control --out "$PWD/$R/armC-control"
python benchmarks/expertlongbench/run.py --task T03MaterialSEG --n 16 --seed 20261104 \
    --arms B --audit-rules rubric --label T-scoped  --out "$PWD/$R/armT-scoped"
# the control the owner is owed: split code, shipped general rules, study 3's seed
python benchmarks/expertlongbench/run.py --task T03MaterialSEG --n 20 --seed 20260930 \
    --subset 8 --arms B --audit-rules general --label G-split-general \
    --out "$PWD/$R/armG-split-general"
```

The primary number is the paired within-instance revision delta (round-one draft
against final output), pooled per arm. Study 3's arm X read −14.42 on this
instrument; the treatment must move it toward zero without the auditor's recall
or precision falling.
