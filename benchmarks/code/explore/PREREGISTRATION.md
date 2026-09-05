# Study 7 — an autonomous search over audit architectures, preregistered

Written and committed **before any model call this study reports.** It fixes the
grid, the split, the objective and the stopping rule. `EXPERIMENT_RECORD.md` §1
binds it; nothing below may be revised after a score is seen, and any addition is
labelled exploratory and lives in a separate grid file.

## 1. The question

Studies 1 and 2 measured six audit architectures over model-free ground truth and
found every one of them sliding along a single ROC curve: recall rises, false
positives rise with it, and filtering for precision destroys recall faster than it
removes false alarms (`docs/design/AUDIT_ARCHITECTURE.md` §1). Study 2's strongest
surviving observation was **complementarity** — of 34 stratum-P defects flagged by
either holistic or decomposed review, 18 were decomposition-only and 8
holistic-only — which is a claim that *combining* readers might leave the curve
where *replacing* one reader did not.

**Hypothesis (falsifiable):** some composition of the detectors already available
to this harness reaches higher recall on the "looks right, is wrong" population
than the shipped architecture **while holding the false-positive rate on correct
code inside the shipped architecture's own measured bound.**

**It can come out false**, and the preregistered form of "false" is stated in §5:
if nothing clears the shipped architecture by more than the measured noise floor
inside the constraint, the result of this study is that the shipped architecture
is on the Pareto front and nothing measured here improves on it.

## 2. Primary and secondary outcomes

**Primary outcome — one number, named now:** the **P-recall on the confirm half**
of the spec selected by the rule in §5.

**Secondary outcomes, all named now:**

- C-false-positive rate on the confirm half of that spec;
- the full Pareto front over (P-recall, C-false-positive rate, cost per instance)
  on the confirm half;
- F-stratum flag rate per spec (the sanity check: code that does not run);
- explore-half values of all of the above, reported for completeness and **not**
  used for any claim;
- cost per instance per spec.

Every rate travels with a 95% Wilson interval (§9 of `EXPERIMENT_RECORD.md`).
Counts small enough that the interval reaches an absurd bound are quoted as counts.

## 3. The substrate, held fixed

| | |
|---|---|
| audit set | study 2's `records/study2/audit_set.json`, unchanged: **290 instances — P 110, C 150, F 30** |
| solutions | study 2's, byte-identical; study 1's batch-1 solutions verified identical by sha256 (540/540) |
| ground truth | a hidden test suite passing or failing. **No model judges anything.** |
| stratum P | passes every visible test, fails a hidden one |
| stratum C | passes every test |
| stratum F | fails a visible test |
| flag definition | at least one BLOCKER finding from the model rung, exactly as studies 1 and 2 |
| constitution | the shipped `scaffold/templates/GENERAL_AUDIT_RULES.md`, unmodified |
| generator | `anthropic:claude-haiku-4-5-20251001` (frozen; nothing is regenerated) |

Routes: `cross` = `openai:gpt-5.6-terra` (the shipped cross-vendor auditor);
`self` = `anthropic:claude-haiku-4-5-20251001` (the generator's own model);
`cheap-cross` = `openai:gpt-5.6-luna`, the cheap tier of the cross-vendor vendor.
The cheap tier of the *self* vendor is `claude-haiku-4-5` itself, which is already
the `self` route, so there is no separate cheap-self detector to run.

## 4. The grid, fixed before any spend

`benchmarks/code/explore/GRID.json`, committed with this file. **15 specs.** A
spec is `{detectors: [{kind, model, draw}...], aggregate}` with
`kind ∈ {holistic, decomposed}` and `draw` an integer so repeats of the same
configuration are distinct detectors.

Ten of the fifteen are set operations over records that already exist and cost
**nothing**. Five require new draws, priced in §7.

Specs, in the order they are scored:

1. `hc` — holistic-cross ×1 — **the shipped architecture, the reference**
2. `hs` — holistic-self ×1
3. `dc` — decomposed-cross ×1
4. `hc_u_hs` — union of 1 and 2
5. `hc_u_dc` — union of 1 and 3
6. `hs_u_dc` — union of 2 and 3
7. `tri_union` — union of 1, 2 and 3
8. `tri_majority` — majority of 1, 2 and 3
9. `tri_unanimous` — unanimous of 1, 2 and 3
10. `hc_x2` — holistic-cross draws 1–2, union
11. `hc_x3` — holistic-cross draws 1–3, union
12. `hc_x3_maj` — holistic-cross draws 1–3, majority
13. `dc_x2` — decomposed-cross draws 1–2, union
14. `cheap_hc` — cheap-tier holistic-cross ×1
15. `cheap_hc_x3` — cheap-tier holistic-cross draws 1–3, union

`checks` (the deterministic layer alone) is not a spec: it flags 0/110 on stratum
P by construction — those solutions pass the visible suite — and it is not a
detector of the kinds this grid ranges over. It is reported as context, not scored.

### Where each detector's records come from

| detector | source | instances covered |
|---|---|---|
| holistic / cross / draw 1 | `records/study2/arm-holistic-cross.jsonl` | 290 — free |
| holistic / cross / draw 2 | `records/study1/arm-cross.jsonl` | 106 free; **184 to run** |
| holistic / cross / draw 3 | `records/study1/arm-cross-replicate.jsonl` | 106 free; **184 to run** |
| holistic / self / draw 1 | `records/study2/arm-holistic-self.jsonl` | 290 — free |
| decomposed / cross / draw 1 | `records/study2/arm-decomposed-cross.jsonl` | 290 — free |
| decomposed / cross / draw 2 | `records/study2/arm-decomposed-replicate.jsonl` | 290 — free |
| holistic / cheap-cross / draws 1–3 | none | **290 each to run** |

Study 1's `cross` and `cross-replicate` arms are admitted as draws 2 and 3 of the
same detector because `RESULTS-2.md` already treats study 1's `cross` and study 2's
`holistic-cross` as replicate draws of one architecture over byte-identical batch-1
solutions (7/56 vs 6/56, 1.8 points apart), and both carry no deterministic layer
(`dcl_blockers == 0` on every row, verified). The solutions are verified
byte-identical by sha256. **A detector that has a record is never re-run.**

## 5. Selection, preregistered

The 290 instances are split into an **explore** half and a **confirm** half by
`random.Random(20260906)`, stratified on `(stratum, batch)` so both halves carry
proportionate P, C and F from both generation batches. The split is computed once,
written to `records/explore/split.json`, and committed.

Every spec is scored on **both** halves.

> **Selection happens on the explore half. Every reported claim is on the confirm
> half.**
>
> **Best = the highest P-recall on the confirm half among specs whose
> C-false-positive rate on the confirm half is ≤ 6.7%.**

6.7% is the shipped architecture's own upper 95% Wilson bound from study 1
(4/150 correct solutions flagged, CI [1.0%, 6.7%]). In code, false positives are
the number that ends a tool's life; the constraint is the product's, not a
statistical convenience.

The explore half's role is honest search, not evidence: it is where the shape of
the grid is inspected and where a spec would be dropped if it were obviously
broken. **No number from the explore half appears in a claim.**

The full Pareto front over (recall ↑, false positives ↓, cost ↓) on the confirm
half is reported beside the selection, so a reader who weighs the constraint
differently can choose.

### The noise floor, fixed now

**1.8 points on P and 0.7 points on C**, from study 1's `cross-replicate` arm —
the same configuration run twice over the same bytes. A difference smaller than
that is not a finding, whatever else is true of it. This floor is quoted against
the estimand it was measured on: an auditor re-reading fixed solutions, which is
exactly what every spec in this grid does. Nothing is regenerated in this study.

### The stated null

If no spec's confirm-half P-recall exceeds `hc`'s by more than 1.8 points while
satisfying the ≤ 6.7% constraint, the study's result is: **the shipped
architecture is on the Pareto front and nothing measured here improves on it.**
That is a result, it is reported as the headline, and no second objective is
constructed to avoid it.

## 6. The loop

`benchmarks/code/explore.py`, committed with this file. It reads the grid, and for
each spec and each instance: if every detector's record exists — in study 1's
records, study 2's records, or the loop's own cache at
`records/explore/cache/` — it composes the aggregate from them; otherwise it runs
the missing detector **once**, caches it keyed by `(kind, model, draw, instance)`,
and composes. A detector with a cached record is never re-run. That cache is what
makes the loop resumable and what bounds the spend.

It writes one JSONL row per `(spec, instance)` to `records/explore/rows.jsonl` and
appends one row per spec to `records/explore/leaderboard.jsonl`. It is idempotent:
re-running skips specs already on the leaderboard unless `--force`.

Generated code is executed only through `execute.py`'s sandbox, and in this study
nothing is generated: no solution is written and no candidate code is run at all.
Every instance's stratum was fixed by study 2's execution and is read from
`records/study2/instances.jsonl`.

## 7. Cost, and the stopping rule

Priced from study 2's measured per-instance costs and the published rate card:
`gpt-5.6-terra` $0.0069/instance holistic; `gpt-5.6-luna` bills at 0.4× terra's
rates, projecting ≈ $0.0028/instance.

| work | calls | projected |
|---|---:|---:|
| holistic-cross draw 2, the 184 uncovered instances | 184 | $1.27 |
| holistic-cross draw 3, the 184 uncovered instances | 184 | $1.27 |
| cheap-cross draws 1–3, 290 instances each | 870 | $2.40 |
| credential probe | 2 | < $0.01 |
| **projected total** | **1,240** | **≈ $4.95** |

**Budget: $15.00.** **Stopping rule: the grid is exhausted, or cumulative spend
reaches $15.00, whichever comes first.** The loop polls the project's usage ledger
and halts on the cap. If it halts early, the specs that could not be scored are
named in the report as unscored rather than dropped silently.

Detectors are run in the order P, then C, then F within each detector, and the
free specs are scored first, so an early halt truncates a secondary outcome rather
than the primary one.

## 8. Analysis

- Rates with 95% Wilson intervals; paired comparisons against `hc` by exact
  McNemar on the discordant pairs, since every spec judges the identical instances.
- Comparison count stated in the report. **The primary outcome is one number
  chosen by the rule in §5 before any spec was scored**, but the grid contains 15
  specs and the selection ranges over all of them; the report states this and does
  not present the selected spec's interval as if it were the only comparison made.
- This project has now run six studies over two tasks. That history is part of the
  multiple-comparison picture and the report says so.

## 9. Limitations known before the run

- **One corpus, one generator, one vendor pair.** Everything `RESULTS-2.md` lists
  as a limitation is inherited unchanged.
- **The composition is over verdicts, not evidence.** A union of detectors here
  unions their *flags*; it does not merge or deduplicate findings. A product would
  have to show a reviewer the union of the findings, which is a different and
  larger cost than the model spend priced above.
- **Vendor independence is not statistical independence.** Two draws of the same
  model are less independent still; a ×3 union of one route is three correlated
  reads.
- **Cost per instance is model spend only.** It excludes the reviewer's time,
  which is what a false positive actually costs.

## 10. Phase 2 — the condition, and the fact that it has already failed

A separate agent pre-tested whether the auditor can emit *executable* checks — an
assertion the DCL runs — rather than an opinion. Its preregistered kill condition
was: fewer than one third of the 56 stratum-P solutions producing a runnable,
discriminating check ends the proposal.

**It fired, and it is recorded here before this study spends anything.** 13 of 56
(23.2%, 95% CI [14.1%, 35.8%]) against a bar of 19; the replicate arm gave 11 of
56 and the union of both runs is still 13. Format was never the constraint — 288
of 288 checks compiled and 96% ran clean, with zero sandbox trips. The failure is
at the only step that matters: the checks block the **correct** reference solution
more often (22 of 56) than the defective solution they were written for (18 of
56), and inverted checks outnumber discriminating ones 26 to 19. The auditor picks
the edge case well and computes the expected value wrong, and it invents
specification the problem never stated and then asserts it.

**So there is no phase 2, and this grid is the whole study.** No exec-check
adjudication grid is built, no spec is added, and the report says this plainly.

What that result frames, and what this study must be read against: the shipped
rung structure *"the model names evidence and code verifies the evidence exists"*
— A4's `governed_source_ids` paired with `check_source_provenance` — survives.
*"The model states what the evidence will say"* does not. **This grid only varies
who looks and how their findings are combined. It never asks a model to supply a
truth value**, so every spec in it is on the surviving side of that line, and the
ground truth every spec is scored against remains a hidden test suite passing or
failing.
