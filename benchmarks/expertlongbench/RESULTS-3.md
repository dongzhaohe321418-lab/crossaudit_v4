# T03MaterialSEG, n = 20 paired — splitting the rules took the auditor from 2% to 23.5% and left the first draft where it was; the loop's next defect is revision

> **Corrected 2026-09-05 — see `../CORRECTIONS.md`.** Two numbers in this report
> do not stand. The pooled **−11.01 F1 (p = 0.0014)** mixes arms S, R and X,
> whose per-arm means are −13.56, +5.83 and −14.42; its 25 observations contain
> only 18 unique sample ids, so the sign enumeration assumes an independence the
> data lack. Its unit is also mislabelled: 25 revised *instances* contain **36
> transitions**, and per transition the figure is −7.64 with 5 fixed / 19 broken,
> not 3/17. The **+24.07** is n = 4 with no interval, from differences of +16.67,
> 0, +22.22 and +57.41. The 2% → 23.5% recall change survives.

**The round-one draft did not fall: 19.8 → 21.8 CLEAR F1, paired difference
+2.04 on 20 instances (p = 0.54). The auditor's round-one recall against CLEAR
ground truth went from 2.0% (2 of 100 wrong items) to 23.5% (23 of 98) — about
twelve-fold.** Both defects study 2 measured are addressed by the same change,
and the arm that isolates the change says so directly: holding the rubric rules
fixed and varying only the code, **the split lifted the round-one draft by
+24.1 F1** (4.2 → 28.2, 3 of 4 pairs better, none worse).

**The result that does not help, first: the final output got worse.** 16.4 →
10.3 F1, paired −6.11 on 20 instances (p = 0.15). The cause is measured, not
guessed, and it is not the constitution: **the audit now fires on 16 of 20
instances instead of 5, so 80% of instances get revised instead of 25% — and on
this task a revision destroys more than it repairs.** Pooled across all three
arms, 25 revisions, mean paired **−11.01 F1** (SE 2.47), **p = 0.0014**, rubric
items fixed 3, broken 17. Study 2 saw this at p = 0.32 and called it a pattern
it could not settle. Fixing the constitution turned the auditor's silence into
findings, and the findings ran straight into a revision path that is now
demonstrably harmful.

So: **the constitution was the binding constraint on the audit, and it no longer
is. The binding constraint on the loop's output is now revision.**

Whole-study spend: **$8.44** of a $12 budget.

Everything below is measured. Nothing is extrapolated.

---

## What was run

| | |
|---|---|
| task | `T03MaterialSEG` — justify the key decisions in a solid-state synthesis recipe |
| corpus | sha256 `0b525eae93aab406…`, verified against `manifest.json` at every run start |
| sample | **20** of the task's 50, seed `20260930` (fresh), sampled after sorting by id — every arm draws the identical 20 |
| generator (every arm) | `anthropic:claude-sonnet-4-6` |
| auditor (every arm) | `openai:gpt-5.6-terra` |
| CLEAR mapper / judge / adjudicator | `openai:gpt-5.6-terra` |
| settings | `max_rounds: 3`, `checks: general`, `authority.lone_model_blocker: block`, N/A policy literal |
| code | **frozen before the run and unchanged after any score was read**: arms S and R at `dc446ae`, arm X at `3fa9b65` |

Three arms, each entered through the product's real `crossaudit.cli.build.run_loop`
in a fresh git project with a real `crossaudit.yml` and the recipe committed
inside the audited scope. They form a 2×2 with the uninteresting cell dropped —
split code with generic rules, which withholds almost nothing, because generic
rules carry almost no criteria to withhold:

| arm | n | code | what the auditor is given | what the generator is given |
|---|---:|---|---|---|
| **S** — shipped | 20 | `dc446ae` | `GENERAL_AUDIT_RULES.md` | the same file, verbatim |
| **R** — rubric, unsplit | 4 | `dc446ae` | rubric-derived rules | the same file, verbatim |
| **X** — split | 20 | `3fa9b65` | rubric-derived rules | the **brief** derived from them |

`S → X` is the product question. `R → X` holds the rules fixed and varies only
the code, so it is **the split's own effect**. `S → R` is study 2's defect,
reproduced here on this sample.

**Arm R is n = 4.** It was capped at 5 for budget before any of its scores were
read, and then its fifth instance died in CLEAR scoring on a provider SSL
failure (see Deviations 24). Every R number below rests on four pairs and is
labelled as one.

### What each side actually received, as bytes

The rubric constitution used by arms R and X is sha256 `9f1ee353ec4cb05e…`,
3343 bytes. Under the split:

| role | projection | sha256 | size |
|---|---|---|---:|
| auditor | `criteria` — the identity function | `9f1ee353ec4cb05e…`, **equal to the committed file** | 3343 B |
| generator | `brief` | `3a3e9341f213efc1…` | 1384 B |

None of the six rubric item descriptions appears in the brief. The writer is
told that `CA-RUBRIC-001…006` and `CA-CONTENT-001` exist, with their severities,
and nothing about what they require. This is checked mechanically, and a receipt
minted during arm X carries both digests in its `projections` block, the
auditor's equal to that receipt's own `inputs.constitution_sha256`.

---

## Q1 — did the auditor start naming what is wrong?

For every round, of the rubric items CLEAR scored **wrong** in that very output,
how many did **any** finding raised against it name? Round one is the number
that matters: a silent auditor at round one ends the loop and the first draft
ships.

| arm | inst | fired | findings | items wrong | named | hit | recall (all rounds) | **recall (round 1)** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **S** | 20 | 5 | 9 | 132 | 2 | 2 | 1.5% | **2.0%** (2/100) |
| **R** | 4 | 4 | 21 | 63 | 18 | 16 | 25.4% | **29.2%** (7/24) |
| **X** | 20 | 16 | 48 | 227 | 45 | 33 | 14.5% | **23.5%** (23/98) |

**Arm S reproduces study 2's headline exactly on a fresh seed: 2.0%.** Two of a
hundred wrong rubric items named, on a different sample, four months of product
work later. That is a replication, and it is the strongest evidence in this
report that the defect was real and structural rather than a sampling artefact.

**Arm X names 23.5%** — the same lever study 2 identified, now pulled without
the cost that made it unusable. The findings changed character completely:

| arm | rules cited | verdicts |
|---|---|---|
| S | `CA-CONTENT-002` ×6, `CA-CONTENT-001` ×3 | 1 confirmed, 8 about no rubric item |
| R | `CA-RUBRIC-*` ×17, `CA-CONTENT-001` ×4 | 17 confirmed, 2 false positive, 2 unmapped |
| X | `CA-RUBRIC-*` ×39, `CA-CONTENT-001` ×9 | 31 confirmed, 12 false positive, 5 unmapped |

Under the shipped rules, 8 of 9 findings are about no rubric item at all. Under
the split, 39 of 48 cite a rubric rule and 31 are confirmed against CLEAR.

### The auditor also became wrong more often, and that is not free

| arm | precision (named items that were in fact wrong) |
|---|---|
| **S** | **100%** (2/2), 95% CI 34–100% |
| **R** | 89% (16/18), CI 67–97% |
| **X** | **73%** (33/45), CI 59–84% |

Study 2's arms were all at 100% precision on tiny denominators. At a denominator
of 45 the true rate is visibly below 1: **twelve of the forty-five rubric items
arm X's auditor objected to were items CLEAR had scored correct.** An auditor
that speaks twelve times as often is wrong sometimes, and the honest statement
of the trade is: recall 2.0% → 23.5%, precision 100% → 73%. The CI on S's 100%
spans two thirds of the range, so this is a real movement in a number that was
never actually measured before, not a regression from an established 100%.

---

## Q2 — the number the poisoning destroyed, and whether it held

The round-one draft is the number study 2 said must not fall: rubric-grade rules
took it from 14.7 to 3.3 F1 because the generator was shown them.

| comparison | n | before | after | paired Δ | better/worse/tied | Wilcoxon |
|---|---:|---:|---:|---:|---|---|
| **S → X** (the product change) | 20 | 19.8 | **21.8** | **+2.04** | 6 / 5 / 9 | p = 0.537 |
| **S → R** (the poisoning, reproduced) | 4 | 22.2 | **4.2** | **−18.06** | 0 / 2 / 2 | p = 0.50 |
| **R → X** (the split alone, rules fixed) | 4 | 4.2 | **28.2** | **+24.07** | 3 / 0 / 1 | p = 0.25 |

**The draft held.** +2.04 F1 is not distinguishable from zero on 20 pairs and it
is not meant to be: the requirement was that it must not fall, and it did not.

**`S → R` reproduces the poisoning on this sample** — 22.2 → 4.2, the same shape
as study 2's 14.7 → 3.3, on four instances drawn with a different seed.

**`R → X` is the split's own effect with the rules held fixed: +24.07 F1**, three
of four pairs better and none worse. On four pairs no p-value earns anything, but
the direction, the size and the mechanism all agree, and the mechanism is
verifiable without any model call: arm R's generator was handed 3343 bytes
containing six transcribed grading criteria; arm X's was handed 1384 bytes
containing none of them.

Round-one deltas, `S → X`, sorted: −27.8, −11.1, −8.3, −8.3, −2.8, then nine
exact zeros, then +7.4, +8.3, +16.7, +22.2, +22.2, +22.2.

---

## The result that does not help — the final output

| comparison | n | before | after | paired Δ | better/worse/tied | Wilcoxon |
|---|---:|---:|---:|---:|---|---|
| **S → X** | 20 | 16.4 | **10.3** | **−6.11** | 3 / 8 / 9 | p = 0.149 |
| S → R | 4 | 22.2 | 10.0 | −12.22 | 0 / 2 / 2 | p = 0.50 |
| R → X | 4 | 10.0 | 18.1 | +8.06 | 2 / 0 / 2 | p = 0.50 |

Arm X's final output is 6.1 F1 below arm S's, on a difference that is not
statistically distinguishable from zero at n = 20. It is also entirely explained
by something already measured:

### Revision, now significant

Pooled over every revision in every arm — legitimate to pool, because each pair
is a within-instance before/after with the same generator and the same scorer:

| | |
|---|---:|
| revisions measured | **25** (of 44 arm-B instances) |
| mean paired Δ F1 (post − pre) | **−11.01** |
| standard error | 2.47 |
| better / worse / unchanged | 1 / **16** / 8 |
| rubric items **fixed** | **3** |
| rubric items **broken** | **17** |
| two-sided Wilcoxon signed-rank | **p = 0.0014**, exact, 17 usable pairs |

| arm | revised | mean Δ F1 | items fixed | items broken |
|---|---:|---:|---:|---:|
| **S** | 5/20 (25%, CI 11–47%) | −13.56 | 0 | 3 |
| **R** | 4/4 (100%, CI 51–100%) | **+5.83** | **2** | **0** |
| **X** | 16/20 (80%, CI 58–92%) | −14.42 | 1 | 14 |

Study 2 reported −3.40 at p = 0.32 on 17 revisions and said the item counts told
a story the p-value could not. On 25 revisions the p-value now tells it too:
**p = 0.0014, seventeen items broken against three fixed.**

Arm X's final score is that mechanism applied more often. Its auditor fires on
16 of 20 instances instead of 5, so it triggers 16 revisions instead of 5, at a
mean of −14.42 F1 each. **The split did not make revision worse; it made the
loop revise more, and revision was already bad.** Arm S's own five revisions
averaged −13.56 with zero items fixed and three broken.

### The one place arm R beat arm X, and what it suggests

Arm R's four revisions averaged **+5.83** and broke nothing, where arm X's
sixteen averaged −14.42. Both arms had the same rubric-grade findings; they
differ in what the generator saw *while revising*. Arm R's generator, revising,
had the cited rule's full criterion in front of it. Arm X's had the finding and
the brief.

That is a hypothesis on four revisions against sixteen, not a result, and it
points at a concrete next change: **the brief is the right thing to hand a
writer at round one, and the cited rule's criterion may be the right thing to
add at revision time**, where there is no longer a blank page to pattern-match
into headings. It is directly testable and it is the obvious follow-on.

---

## Cost and behaviour

| | arm S | arm R | arm X |
|---|---:|---:|---:|
| instances | 20 | 4 | 20 |
| mean rounds | 1.30 | 2.75 | 2.15 |
| mean wall time / instance | 58 s | 204 s | 122 s |
| generation + audit | $1.27 | $0.89 | $2.72 |
| CLEAR scoring (every round) | $1.09 | $0.59 | $1.89 |
| **total** | **$2.36** | **$1.48** | **$4.60** |
| per instance | $0.118 | $0.369 | $0.230 |

**Whole-study spend $8.44 of a $12 budget.** Arm X costs 1.95× arm S per
instance and 2.1× the wall time, because an auditor that finds things sends work
back. That is the price of the recall, and on this task the loop currently
spends it badly.

---

## What this run does and does not license

**It licenses:**

1. **The round-one draft did not fall.** +2.04 F1 paired on 20 instances,
   p = 0.54. The requirement was that it must not fall.
2. **The auditor's round-one recall went from 2.0% to 23.5%** — 2 of 100 wrong
   rubric items named, to 23 of 98, on the same 20 samples.
3. **Arm S independently reproduces study 2's 2.0%** on a fresh seed. The defect
   was structural.
4. **The split is what saved the draft.** Rules held fixed, code varied:
   +24.07 F1 on the round-one draft, 3 of 4 better, 0 worse.
5. **Revision harms this task, and now significantly.** 25 revisions, −11.01 F1,
   p = 0.0014, 17 items broken to 3 fixed.

**It does not license:**

- **The claim that the change improves the final output. It does not, here.**
  −6.11 F1 paired, p = 0.15, and the mechanism (more revisions × harmful
  revisions) is measured rather than speculative.
- **The claim that the auditor's precision is unharmed.** 100% (2/2) → 73%
  (33/45). The denominators are not comparable and the new number is the first
  one large enough to mean anything, but the direction is down and 12 confirmed
  false positives is the honest count.
- **Any conclusion from arm R at n = 4** beyond direction and size.
- Anything about tasks other than T03MaterialSEG, or about a generic
  constitution: arm X's benefit comes from rubric-grade rules the split makes
  *safe to write*, and this study does not measure the split under generic rules
  (see the dropped 2×2 cell).

**Do not re-run this study hoping for a different number.** If the configuration
changes, the study restarts and says so here.

---

## Deviations from CLEAR

Study 1's list 1–14 and study 2's 15–23 stand, except where a number below
replaces one. Items 1, 2, 4, 5, 6, 7, 8, 9, 10, 13, 14, 16, 18, 19, 22 apply
unchanged. Changed and added:

3″. **The judge still shares a vendor with the auditor.** Unchanged and still
   unfixed for want of a third credential. The bias points in the audited arm's
   favour; arm X's final score still lost.

11″. **Sample 20 of 50, seed `20260930`.** A fresh seed and a smaller draw than
   study 2's 40, so the overlap with study 2's sample is partial. This is not an
   independent corpus — it is the same 50 rows — but it is an independent draw,
   which is what makes arm S's reproduction of 2.0% worth stating.

17′. **Deviation 17 is discharged.** Study 2 recorded that `run_loop` passed the
   constitution into `generator.build_prompt`, making arm B′ a test of two
   changes at once, and said "the clean experiment needs a product change
   first." That product change is `3fa9b65` and this study is the clean
   experiment: arms R and X differ in code only.

24. **Arm R stopped at 4 instances of an intended 5, and arm X was resumed once.**
   Both were the same environmental failure: `[SSL: UNEXPECTED_EOF_WHILE_READING]`
   exhausting all configured routes inside CLEAR scoring, through the machine's
   HTTP proxy. Arm R died on its fifth instance and was **not** resumed, so it is
   reported at n = 4. Arm X died after 15 of 20 recorded instances and was
   resumed with `--resume` (study 2's Deviation 21b mechanism: it decides which
   seeded samples still need running and touches no arm, prompt, model, setting
   or scoring path). The code was not modified; the frozen sha `3fa9b65` is the
   same before and after. The first 15 instances' records predate the resume byte
   for byte. **No score was read between the crash and the resume.**

25. **Arm R's cap to n = 5 was a budget decision taken before its scores were
   read.** Three-round instances cost more than study 2's per-instance figures
   projected, and capping the optional arm was the only way to hold arms S and X
   at n = 20 inside US$12.

26. **The 2×2 is incomplete by design.** Split code with generic rules is not
   run. Generic rules carry almost no acceptance criteria, so the brief withholds
   almost nothing from the writer and the cell would measure close to arm S at
   the cost of a fifth of the budget. The consequence is stated in the licence
   section: this study measures the split *together with* the rubric-grade rules
   it exists to make safe.

27. **`brief_projection` is a pure function of the committed rulebook and is not
   validated against human judgement.** Which rules describe the deliverable's
   shape and which grade its content is declared in the file, by a reserved id
   (`CA-TASK-001`) or an explicit `<!-- brief -->` marker. The rubric
   constitution marks none, so arm X's writer received the preamble and a roster
   of rule ids. A differently-marked rulebook would produce a different brief and
   is not measured here.

---

## To reproduce

```sh
export PYTHONPATH="$(git rev-parse --show-toplevel)/src"
python benchmarks/expertlongbench/fetch.py
R=benchmarks/expertlongbench/runs
# arm S and arm R at dc446ae; arm X at 3fa9b65
python benchmarks/expertlongbench/run.py --task T03MaterialSEG --n 20 --seed 20260930 \
    --arms B --label S-shipped --out "$PWD/$R/armS-shipped"
python benchmarks/expertlongbench/run.py --task T03MaterialSEG --n 20 --seed 20260930 \
    --subset 5 --arms B --audit-rules rubric --label R-rubric-shipped \
    --out "$PWD/$R/armR-rubric"
python benchmarks/expertlongbench/run.py --task T03MaterialSEG --n 20 --seed 20260930 \
    --arms B --audit-rules rubric --label X-split --out "$PWD/$R/armX-split"
python benchmarks/expertlongbench/report2.py "$R/armS-shipped" "$R/armR-rubric" "$R/armX-split"
```

`--out` must be absolute. It will not reproduce byte-identically: the provider
layer exposes no seed and temperature comes from the model's capability card.
