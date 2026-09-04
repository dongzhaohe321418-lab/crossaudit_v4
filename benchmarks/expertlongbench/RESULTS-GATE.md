# An oracle revision gate on the archived runs — the ceiling is "don't revise", and nothing visible at runtime reaches it

**An exogenous gate that rejects any revision CLEAR scores below the text it
replaces cannot lose, and on these runs it does not win either. In arms S and X
its ceiling is *exactly* the round-one draft: across 29 transitions in those two
arms, not one revision ever ended above the draft it started from. The gate's
value over simply not revising is +0.00 F1 in S (0 of 20 instances changed),
+0.00 F1 in X (0 of 20), and +10.00 F1 in R — where R is 4 scored instances of
10 assigned and 3 transitions on 2 instances carry all of it.** Of the 36
revision transitions in the three arms, **3 ended above their own round-one
draft, and all 3 are in arm R.**

**The preservation split says the damage is not the churn everyone assumed.**
Over 216 item-transitions in the three arms: **5 items fixed, 19 broken, 192
untouched.** Exactly **1 of 36** transitions both fixed and broke an item, and
**17 of 36** changed no item's correctness at all. The net F1 delta is not
hiding compensating repair. It is hiding *inertia* — most revisions move
nothing — with a one-directional tail of breakage.

**No runtime-visible signal is established as a predictor of a harmful
revision.** The strongest candidate, the number of findings in the audit that
triggered the revision, reaches AUC 0.737 pooled over the primary arms with a
clustered bootstrap interval of [0.554, 0.898], falling to [0.510, 0.969] once
the transitions that could not get worse are removed — a lower bound at chance.
Its counts are 12 of 13 harmful at two or more findings against 5 of 10 at one,
over 36 transitions from **18 unique sample ids**. And every gate built from it
loses to switching revision off: in no primary arm does any implementable proxy
beat report-only. **The honest product answer is to report rather than revise.**

Zero model calls. Every number below is arithmetic over rounds already scored on
disk. Cost $0.

---

## What this is, and the analysis rules it was built to obey

`CORRECTIONS.md` item 9 withdrew "revision is net negative" for three separate
defects. This replay is constructed so that it cannot repeat any of them:

| defect withdrawn there | what is done here |
|---|---|
| primary outcome conditioned on **revision occurred**, a post-treatment variable | The primary population is **every instance the arm scored**. Instances that never revised are carried at a delta of exactly 0, not dropped. The conditional view is computed and printed, labelled `EXPLORATORY` at every occurrence. |
| the **unit** was the instance while the word used was "revision" | Every figure names its unit. §1 is per **instance**. §2 and §3 are per **transition** — one round-k → round-k+1 step. Study 3 has 25 revised instances and **36 transitions**; both numbers appear, never interchangeably. |
| a pooled p over **heterogeneous arms** with repeated sample ids | Arms S, R and X are reported separately throughout. The one pooled line in §1 is labelled secondary and its interval comes from a bootstrap resampling **whole source sample ids**. No pooled p is computed. |

Two further guards, from `EXPERIMENT_RECORD.md` §9. Any bootstrap interval whose
sample contains no sign change is printed with `[CI DEGENERATE]` and is not read
as excluding zero — a percentile bootstrap over same-signed values cannot
resample across zero, which is the mechanism that inflated withdrawn finding 4.
And small counts are quoted as counts.

**Reproduction of the published arm figures.** This script recomputes arm F1
from `round_scores` without touching `report2.py`'s aggregation, and lands on
`RESULTS-3.md`'s numbers: round-one 19.78 → 21.81 and final 16.39 → 10.28 for
S → X, against the report's 19.8 → 21.8 and 16.4 → 10.3.

### The three gates

| name | rule | implementable? |
|---|---|---|
| **keep-best** | reject every transition with post < pre; ship the best-scoring text seen | **no** — needs CLEAR |
| **stop-first** | halt the loop the first time a revision would lower F1 | **no** — needs CLEAR |
| **report-only** | never revise; ship the round-one draft | yes, trivially |

keep-best is the more generous oracle: it assumes rejecting round 2 would not
have disturbed round 3, which is counterfactually false, since round 3 was
generated *from* round 2. stop-first makes no such assumption. **On this data
they coincide in every arm**, so the choice does not affect any conclusion
below; keep-best is quoted as the ceiling.

Note the arithmetic that follows from either definition: **a gate floored at the
round-one draft cannot ship anything worse than the round-one draft.** So "the
fraction of the withdrawn revision harm recovered" is **all of it, in every
arm** — and that is a property of the estimator, not evidence about the gate.
The number that decides whether to build one is `gate − report-only`.

---

## 1. The gate's effect, intention-to-treat, per arm

Unit: the instance. Population: every instance the arm scored. F1 is
sample-level CLEAR F1 ×100.

### Primary — study 3 (S, R, X). Never pooled into a headline.

| arm | assigned | scored | revised | transitions | report-only | as shipped | **oracle ceiling** |
|---|---:|---:|---:|---:|---:|---:|---:|
| **S** — shipped rules | 20 | 20 | 5 | 6 | 19.78 | 16.39 | **19.78** |
| **R** — rubric, unsplit | 10 | **4** | 4 | 7 | 4.17 | 10.00 | **14.17** |
| **X** — split | 20 | 20 | 16 | 23 | 21.81 | 10.28 | **21.81** |

| arm | ITT oracle gate − as shipped | ITT oracle gate − **report-only** |
|---|---|---|
| **S** | +3.39 F1, 4 of 20 instances improved, 0 worse `[CI DEGENERATE]` | **+0.00**, 0 of 20 instances changed |
| **R** | +4.17 F1, 1 of 4 improved, 0 worse `[CI DEGENERATE]` | **+10.00**, 2 of 4 improved |
| **X** | +11.54 F1, 12 of 20 improved, 0 worse `[CI DEGENERATE]` | **+0.00**, 0 of 20 instances changed |

Read the counts, not the bounds, in the first column: no instance in any arm can
move the wrong way under a gate that keeps the best text, so the bootstrap
cannot cross zero and its lower bound is mechanical.

**Arm R is 4 scored instances of 10 assigned.** Six were never run — the arm was
capped at 5 for budget before any score was read and its fifth died in scoring
(`RESULTS-3.md`, Deviations 24). Nothing about the six missing instances is
assumed here; arm R's ITT denominator is the 4 that exist, and that is a
weakness of the arm, not a property of the gate. Arm R is also the only arm in
which revising helped at all.

**The finding that matters is the right-hand column.** In S and X the oracle
ceiling is numerically identical to never revising, to the last digit, because
no revision in either arm ever produced a draft scoring above the one it
replaced. Only 3 of the 36 transitions in the whole of study 3 ended above their
instance's round-one draft, and all 3 are arm R's — two of them the same
instance revised twice.

### Secondary arms, reported separately, not pooled with the above

| arm | study | scored | revised | report-only | as shipped | oracle ceiling | gate − report-only |
|---|---|---:|---:|---:|---:|---:|---:|
| T — scoped revision | 4 | 16 | 11 | 14.68 | 9.47 | 17.11 | +2.43 (2 of 16) |
| C — control | 4 | 16 | 9 | 13.49 | 12.29 | 17.04 | +3.54 (2 of 16) |
| G — split, general rules | 4 | 8 | 0 | 24.50 | 24.50 | 24.50 | +0.00 (no revisions) |
| B — main n40 | 2 | 40 | 7 | 18.14 | 16.55 | 18.97 | +0.83 (2 of 40) |
| B-rubric | 2 | 10 | 5 | 3.33 | 7.78 | 7.78 | +4.44 (2 of 10) |
| B-auditor-sol | 2 | 10 | 5 | 15.83 | 11.94 | 16.39 | +0.56 (1 of 10) |

Across all nine arms, **the largest margin an unbuildable oracle wins over
simply not revising is 10.00 F1, in the 4-instance arm.** In the two arms with
20 scored instances each it is zero.

### Secondary, pooled, clustered on source sample id

Reported only in this form, and only because the primary arms are small:
44 instances over 20 unique sample ids. `keep-best − as shipped` +7.16
[+4.41, +10.14] `[CI DEGENERATE]`; `report-only − as shipped` +6.25
[+3.41, +9.52]; **`keep-best − report-only` +0.91 [+0.00, +2.15]
`[CI DEGENERATE]`**. The pooled arms differ in constitution, in what the auditor
is shown and in what the generator is shown; this line is a mixture and is not a
headline.

---

## 2. Preservation — fixed, broken, untouched, per transition

Unit: the **transition**. An item is "right" when CLEAR records both
`precision_hit` and `recall_hit` for it (CLEAR's per-item accuracy). The recall
axis alone is attribution — did the draft cover the reference item at all. The
precision axis alone is whether what it said about that item was correct.

### Primary arms

| arm | transitions | axis | fixed | broken | untouched | of |
|---|---:|---|---:|---:|---:|---:|
| **S** | 6 | accuracy | 0 | 3 | 33 | 36 |
| | | recall | 2 | 4 | 30 | 36 |
| | | precision | 0 | 5 | 31 | 36 |
| **R** | 7 | accuracy | 3 | 1 | 38 | 42 |
| | | recall | 2 | 3 | 37 | 42 |
| | | precision | 4 | 2 | 36 | 42 |
| **X** | 23 | accuracy | 2 | 15 | 121 | 138 |
| | | recall | 4 | 17 | 117 | 138 |
| | | precision | 4 | 17 | 117 | 138 |
| **S+R+X** | **36** | **accuracy** | **5** | **19** | **192** | **216** |
| | | recall | 8 | 24 | 184 | 216 |
| | | precision | 8 | 24 | 184 | 216 |

The 5/19 accuracy split reproduces the corrected per-transition figure in
`CORRECTIONS.md`, as does the per-transition mean delta of **−7.64 F1** (per
arm: **S −11.30**, **R +3.33**, **X −10.03**; the arms are not pooled for any
inference, and no pooled p is offered).

### What the F1 delta was hiding — and it is not what was assumed

The hypothesis behind this metric was that a revision fixes one item and breaks
another, netting to zero and looking harmless. **That is not what happens here.**

| | S | R | X | S+R+X |
|---|---:|---:|---:|---:|
| transitions that fixed **and** broke an item | 0 of 6 | 0 of 7 | 1 of 23 | **1 of 36** |
| transitions that changed **no** item's correctness | 3 of 6 | 4 of 7 | 10 of 23 | **17 of 36** |

Compensating churn is essentially absent — one transition in thirty-six. The
real shape is that **17 of 36 revisions rewrote the document and moved no item's
correctness at all**, and the remainder are close to one-directional: 19 breaks
against 5 fixes. So the F1 delta is not concealing hidden repair that a gate
could preserve. There is very little repair to preserve.

Two further readings the F1 delta does not give:

- **Both axes degrade together.** On the recall (attribution) axis, 24 broken
  against 8 fixed; on precision, 24 against 8. The revisions are not trading
  coverage for correctness in either direction; they lose both.
- **The untouched majority is overwhelmingly untouched-and-wrong.** Of the 192
  accuracy-untouched item-transitions, 181 were wrong before and wrong after.
  Only 11 were right and stayed right. The loop is revising documents whose
  items it is not reaching, which is consistent with the auditor recall figures
  in `RESULTS-3.md` and is a separate defect from the gate question.

Secondary arms, accuracy axis: T 3 fixed / 6 broken over 13 transitions;
C 4 / 5 over 14; B 2 / 6 over 8; B-rubric 2 / 0 over 7; B-auditor-sol 0 / 2 over
8; G has no transitions.

---

## 3. Is the gate implementable? — no signal in the run records reaches it

The gate in §1 reads the CLEAR score of a draft that the product, at runtime,
has not scored and cannot score. A shippable gate would have to predict
`post_f1 < pre_f1` from what a running loop can see. This section asks whether
anything in the run records does.

**What is actually available.** The findings carry `round`, `rule`, `severity`,
`tier`, `state`, `verdict`, `artifact`. In these runs **severity, tier, state
and verdict have no variance whatever**: all 181 findings across all nine arms
are `BLOCKER` / `model` / `alleged` / `BLOCKED`. Finding severity is therefore
not a candidate predictor here — not because it was tested and failed, but
because it is constant. What remains is the round index, the number of findings
in the triggering audit, which rules fired, the length of the text being
revised, and how much the revision grew it.

### Discrimination, primary arms pooled with an instance-clustered bootstrap

AUC is P(signal higher on a harmful transition than on a non-harmful one); 0.5
is a coin. 36 transitions, 17 harmful, from 18 unique sample ids.

| signal | AUC | 95% CI | harmful vs not |
|---|---:|---|---|
| findings in the triggering audit | 0.737 | [0.554, 0.898] | 2.35 vs 1.42 |
| distinct rules in that audit | 0.737 | [0.554, 0.898] | collinear with the above |
| growth in characters, % | 0.718 | [0.516, 0.879] | +28.4% vs +10.0% |
| round index of the new draft | 0.322 | [0.180, 0.523] | 2.12 vs 2.47 |
| length of the text being revised | 0.245 | [0.115, 0.404] | 6090 vs 7590 chars |
| checklist size | — | constant within the task | — |
| *(reference, not runtime-visible)* pre-revision CLEAR F1 | 0.898 | [0.792, 0.990] | 0.30 vs 0.07 |

The last row is the confound that disqualifies the rest at face value. **A draft
already at F1 = 0 cannot be made worse.** 13 of the 36 transitions start from
zero and are guaranteed non-harmful by arithmetic, so any signal that merely
tracks "this draft is bad" scores well without predicting anything. Removing
them leaves 23 harm-possible transitions, of which **17 are harmful** — a base
rate that is itself the finding.

| signal, harm-possible transitions only (n = 23) | AUC | 95% CI |
|---|---:|---|
| findings in the triggering audit | 0.804 | **[0.510, 0.969]** |
| growth in characters, % | 0.735 | [0.188, 0.957] |
| round index of the new draft | 0.225 | [0.000, 0.554] |
| length of the text being revised | 0.500 | [0.241, 1.000] |

**The finding count is the only candidate, and it is not established.** Its
interval's lower bound sits at 0.510 — chance — once the floor effect is
removed. As counts: two or more findings, **12 of 13** transitions harmful; one
finding, **5 of 10**. Three or more findings, **7 of 7** — against a base rate
of 17 of 23. Per rule, nothing separates: the harmful share runs from
`CA-RUBRIC-003` at 9 of 13 to `CA-RUBRIC-006` at 4 of 8, with `CA-RUBRIC-002`
appearing once.

**And the direction makes it useless even if it were real.** The signal says
*reject the revision precisely when the audit found the most to fix*. A gate
keyed on it is operationally close to switching revision off wherever the audit
has anything substantive to say — which is report-only, reached by a longer
route and at the price of a generation call.

**The growth signal must not be re-promoted.** `CORRECTIONS.md` item 6 already
withdrew a 25% growth threshold, fitted on 25 observations and falsified on 16
held out. This replay finds the same suggestive direction — 9 of 10
harm-possible transitions that grew the text by more than 25% were harmful —
and the same failure to generalise: as a gate it is worth +0.00 F1 in arm T and
+2.24 F1 [−5.94, +11.11] in arm C, the two arms where the threshold was
falsified.

### What proxy gates actually buy, ITT per arm

Each gate uses only runtime-visible signals and halts the loop on rejection,
because what the loop would have produced after a rejection was never generated
and cannot be replayed.

| gate (arm F1, ITT delta vs as-shipped) | **S** | **R** | **X** |
|---|---|---|---|
| as shipped | 16.39 | 10.00 | 10.28 |
| **oracle keep-best (ceiling)** | **19.78** | **14.17** | **21.81** |
| never revise (report-only) | **19.78** `+3.39` | 4.17 `−5.83` | **21.81** `+11.54` |
| reject if ≥2 findings | 18.94 `+2.56` | 10.00 `+0.00` | 20.01 `+9.73` |
| reject if ≥3 findings | 16.39 `+0.00` | 10.00 `+0.00` | 16.95 `+6.68` |
| reject if text grew >25% | 16.39 `+0.00` | 14.17 `+4.17` | 20.01 `+9.73` |
| allow one revision only | 16.39 `+0.00` | 10.42 `+0.42` | 9.72 `−0.56` |

**In no primary arm does any implementable proxy beat report-only.** The best of
them, "reject if ≥2 findings", captures 9.73 of the 11.54 F1 that switching
revision off recovers in arm X, and 2.56 of 3.39 in arm S — it approaches
report-only from below and costs a generation call per instance to do it. In
arm R, where revision helped, `≥2 findings` and report-only diverge in the way
that matters — report-only gives up 5.83 F1 — but that arm is 4 scored
instances of 10 assigned and cannot settle it.

Secondary arms do not change the picture. Against report-only, instance by
instance, `≥2 findings` is ahead on 2 instances and behind on 1 of C's 16, ahead
on 1 and behind on none of B-auditor-sol's 10, ahead on 1 and behind on 1 of T's
16, ahead on 1 and behind on 2 of B's 40, and identical on all 10 of B-rubric's.
That is 5 instances moved in one direction and 4 in the other, out of 92.

---

## The answer to the question that was asked

External work predicts most revision harm is recoverable by an exogenous gate —
SEAL's 11 of 12 improved, RARR's F1_AP 57.0 against 17.1 ungated. On these runs:

1. **An oracle gate recovers all of the withdrawn revision harm, in every arm,
   by construction.** A gate floored at the round-one draft cannot ship worse
   than the round-one draft. Conditional on revising, it returns +13.56 F1 in S
   and +14.42 in X — exactly the magnitudes `CORRECTIONS.md` records as those
   arms' withdrawn per-instance means. That is an identity, not a result.
2. **It buys nothing over not revising.** +0.00 F1 in S, +0.00 in X, +10.00 in
   the 4-instance arm R. The entire measured benefit of gating on this task is
   the benefit of switching revision off.
3. **A shippable proxy would have to predict something no record here contains.**
   Finding severity is constant; the round index points the wrong way; length
   growth was already fitted and falsified once; the finding count survives with
   an interval that reaches chance and a direction that collapses into
   report-only.

**So the gate is not implementable, and on this task it would not be worth
implementing if it were. Report rather than revise.**

## What this does not license

- **One task, one vendor pair, one corpus.** `T03MaterialSEG`, generator
  `anthropic:claude-sonnet-4-6`, auditor and CLEAR roles `openai:gpt-5.6-terra`.
  Nothing here transfers to code, to another task in ExpertLongBench, or to
  another model pair. The code vertical has model-free ground truth and its
  revision behaviour is untouched by this analysis.
- **Run-to-run variation for this contrast is not measured.** The prose noise
  floor recorded in study 5 is a property of the auditor over *fixed* drafts and
  cannot bound a comparison in which generation changes (`CORRECTIONS.md` item
  1). A replicate arm for the paired prose contrast is being measured
  separately; no figure from it is quoted here, and the phrase "inside the noise
  floor" is not used.
- **CLEAR is a reimplementation.** Every F1 here is the project's scorer, whose
  mapper coerces malformed replies to `"N/A"`, and whose raw replies for these
  runs were not retained. No absolute is comparable to the ExpertLongBench
  leaderboard.
- **The oracle's own definition is generous.** keep-best treats round 3 as
  available after rejecting round 2, which is counterfactually false. It
  coincides with stop-first on this data, so no conclusion turns on it, but a
  study where they diverge must use stop-first.
- **The harmful/non-harmful label is CLEAR-defined and floor-limited.** 13 of 36
  transitions could not have been harmful. Any future predictor must be
  evaluated on the harm-possible subset, where n falls to 23 over 18 sample ids.
- **Arm R decides nothing.** 4 scored of 10 assigned, and it is both the only
  arm where revision helped and the only arm where the gate beats report-only.
  Whether a rubric constitution without the split makes revision safe is an open
  question this data cannot answer, and it is the cheapest follow-up here: the
  six unrun instances of arm R.

## Reproduction

```sh
python benchmarks/expertlongbench/gate_analysis.py \
  --out benchmarks/expertlongbench/records/gate \
  <study-data>/wt-control-runs/armS-shipped \
  <study-data>/wt-control-runs/armR-rubric \
  <study-data>/wt-split-runs/armX-split \
  <study-data>/wt-revision-runs/armT-scoped \
  <study-data>/wt-ctlrev-runs/armC-control \
  <study-data>/wt-ctlrev-runs/armG-split-general \
  <study-data>/wt-study2-runs/main-n40 \
  <study-data>/wt-study2-runs/bprime-rubric \
  <study-data>/wt-study2-runs/bsecond-auditor
```

No API key, no model call, no network. The run directories hold ExpertLongBench
derivatives (CC BY-NC-SA 4.0, non-commercial, no redistribution) and are not
committed. What is committed is derived records only — sample ids, per-round
scores, per-item fixed/broken counts, finding counts, rule ids and character
*lengths*:

- `records/gate/transitions.jsonl` — 86 transitions, one row each
- `records/gate/instances.jsonl` — 144 instances, one row each
- `records/gate/arms.json` — per-arm plan, settings, models, corpus and
  constitution digests, and which assigned instances were never run
- `records/gate/analysis-output.txt` — the script's full console output, so
  every figure quoted above can be found without rerunning it
