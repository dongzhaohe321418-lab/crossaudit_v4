# Study 4 — preregistration

Written and committed **before any model call of the analysed run**, per
`benchmarks/EXPERIMENT_RECORD.md` §1. Nothing below may change once a score has
been read; if it does, the change is recorded as a numbered deviation in
`RESULTS-4.md` and the study restarts.

Two things must be disclosed here rather than in the deviations, because they
bear on what "before the run" means:

1. **This is not the first launch.** An earlier launch of arm C at the same
   frozen shas, same seed, same samples, ran 3 of 16 instances and was killed
   before this file existed. **No score from it was read** — the only figures
   looked at were dollar costs — and its run directory is deleted, not merged.
   Its $0.66 is reported as spend and written off. The analysed run starts from
   nothing.
2. **The design below was already fixed and committed** before that earlier
   launch, in `0524161` (`RESULTS-4.md`, "To reproduce"): the same two arms, the
   same n, the same seed, the same frozen shas and the same primary outcome.
   This file formalises that commitment in the required shape; it does not
   change it.

## Hypothesis

Stated so it can come out false:

> The 25% document-growth budget added in `21f37d5` moves the paired
> within-instance revision delta on T03MaterialSEG **up** relative to tip
> behaviour, **without** reducing the auditor's round-one recall or its
> adjudicated precision.

It is false if the treatment's paired revision delta is not above the control's,
or if either auditor measure falls.

## Primary outcome — one number, named in advance

**The paired within-instance revision delta in CLEAR F1**: for each instance
where the loop revised at least once, the CLEAR F1 of the final committed output
minus the CLEAR F1 of the round-one draft, averaged over the revised instances
of that arm. Reported per arm with a 95% confidence interval and an exact
two-sided Wilcoxon signed-rank p, and as a between-arm difference.

Study 3's arm X read **−14.42** on this instrument; the pooled figure over its
three arms was **−11.01** (SE 2.47, p = 0.0014). The direction that would
support the hypothesis is *upward*.

## Secondary outcomes, named in advance

1. Rubric items **fixed** and **broken** by revision, per arm.
2. Auditor **round-one recall** against CLEAR ground truth (of the rubric items
   CLEAR scored wrong in the round-one output, how many any finding named).
3. Auditor **precision** — adjudicated findings confirmed ÷ (confirmed +
   false positive).
4. **Final output** CLEAR F1, per arm and paired between arms.
5. **Round-one draft** CLEAR F1, per arm and paired between arms — it must not
   move, since neither arm changes what the writer sees on a blank page.
6. **Committed document growth** per round transition, per arm — the quantity
   the change acts on. The treatment must show no committed transition above
   25%; the control is expected to show several.
7. Cost and rounds per instance, per arm.

Anything not on this list that ends up in the report is labelled **exploratory**.
That includes, already and by name, the **counterfactual replay** of the growth
screen over study 3's revisions, and every Phase-1 correlation reported from
study-3 data (they were computed after those runs, on data gathered for a
different question).

## Arms

| arm | product code | constitution | what differs |
|---|---|---|---|
| **C — control** | `63ab94c` | rubric-derived | tip behaviour; no document growth budget exists |
| **T — treatment** | `21f37d5` | rubric-derived, **byte-identical** | `repair.max_document_growth = 0.25` (default), plus the sentence stating it in the revision prompt |
| **G — split + general** | `63ab94c` | shipped `GENERAL_AUDIT_RULES.md` | answers a separate owner question; compared against study 3's arm S |

Held fixed across C and T: the task, the corpus, the seed and therefore the
sample; generator `anthropic:claude-sonnet-4-6`; auditor, mapper, judge and
adjudicator `openai:gpt-5.6-terra`; `max_rounds: 3`, `checks: general`,
`authority.lone_model_blocker: block`, N/A policy literal; and the benchmark
harness itself — `run.py`, `clear.py`, `adjudicate.py`, `provider.py` and
`tasks.py` are sha256-identical in the two worktrees, verified before launch and
recorded in `manifest.json`.

C and T differ in exactly the five product files `21f37d5` touched. G differs
from C only in its constitution.

## n, and why

- **C and T: n = 16 each**, the identical 16 samples, seed `20261104`, drawn
  from the task's 50 after sorting by id. Chosen from budget: study 3's
  comparable arm cost $0.230/instance, and 16 + 16 + 8 fits US$12 with headroom
  for the treatment's extra rounds. Study 3 revised 16 of 20 instances under
  these rules, so n = 16 is expected to yield roughly 13 revisions per arm — the
  unit the primary outcome is measured on.
- **G: n = 8**, the first 8 by id of study 3's seed `20260930` sample, so it
  pairs instance-for-instance with study 3's arm S.

n is **not** a power calculation. Study 3's revision deltas had SD ≈ 12 F1;
13 pairs detects a shift of roughly 10 F1 at 80% power, which is the size of the
defect being attacked but leaves smaller true effects undetectable. Stated here
so it is not discovered afterwards.

## Stopping rule

- **Budget US$12 total** across all arms, measured from the usage ledger. If the
  running total reaches $12 the study stops where it is and reports the n each
  arm reached.
- Order: C, then T, then G. If the budget runs out before G, G is reported as
  not run.
- A provider failure is retried up to 4 times per arm with `--resume`, which
  decides only which seeded samples still need running. A retry is a numbered
  deviation.
- **No arm is extended, shortened, or re-run because of a number it produced.**

## Analysis, fixed in advance

- **Test**: exact two-sided Wilcoxon signed-rank on within-instance paired
  differences, ties dropped and the dropped count reported. Paired because both
  numbers come from the same instance, same generator, same scorer; non-parametric
  because n is small and the deltas are not normal.
- **Effect size**: the mean paired difference in F1 points, with a 95% CI (BCa
  bootstrap, 20 000 resamples, seed `20261104`).
- **Every p is reported exactly**, never as a threshold.
- **n is reported for every cell**, including cells that shrank.
- **The total number of comparisons the study makes is reported**, and this
  study is the fourth over the same task, which is stated where the primary
  outcome is.
- **Noise floor**: this study runs each arm once and therefore *cannot* estimate
  run-to-run spread. That is a limitation, recorded in advance, not a result.

## Artefacts this study must leave on disk

`benchmarks/expertlongbench/study4/` — `PREREGISTRATION.md` (this file),
`manifest.json`, `records.jsonl` (one row per instance per arm, derived values
and hashes only), `rundirs.sha256`. `RESULTS-4.md` carries the analysis,
deviations and limitations. No corpus text and no model output is committed.
