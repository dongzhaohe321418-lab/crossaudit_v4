# EvalPlus, n = 110 — decomposition raised recall 9.1 points and the false-positive rate 8.0; the gain is uncertain and the cost is not

**Primary outcome, preregistered: `decomposed-cross` − `holistic-cross`, recall on the
"looks right, is wrong" population = +9.1 points** (23.6%, 26/110, against 14.5%, 16/110;
McNemar exact **p = 0.0755**; paired bootstrap 95% CI **[+0.0, +18.2]**). **Beside it, the
column that decides adoption: the same change cost +8.0 points of false positives on
correct code** (11.3%, 17/150, against 3.3%, 5/150; exact **p = 0.0042**; CI
**[+3.3, +13.3]**).

**Those two numbers are not equally certain, and the asymmetry is the result.** The recall
gain is about 3.4× this study's measured noise floor and its interval's lower bound sits on
zero; at n = 110 this design has 0.75 power against a 10-point effect, so p = 0.076 is
roughly what a real 9-point effect looks like here — the study can see the sign and cannot
pin the magnitude. The false-positive increase has no such ambiguity. **Decomposition buys
recall that this study cannot confirm, at a price it can.**

**Precision fell from 69.8% to 41.8%, and the flags decomposition *adds* over holistic
review are 19.1% correct** — four in five of the extra alarms are wrong. That is the number
a reviewer experiences, and it is computed population-weighted, so it is not an artefact of
the stratified sample.

**The finding that survives both of the above: the two architectures are complementary, not
ordered.** Of 34 stratum-P defects flagged by either, **18 were found only by decomposition,
8 only by holistic review, and 8 by both**. Structure does not simply raise or lower a
threshold — **it changes which defects are visible at all.** Their union reaches 30.9%
recall against the shipped architecture's 14.5%. This is the strongest support in the study
for the hypothesis that the audit's structure, not its model, is the lever; it is also the
result that a single-architecture product cannot exploit without paying the false-positive
bill measured above.

**Every primary number in this study passed through no model.** Ground truth is a Python
interpreter raising `AssertionError` or not, on suites written before CrossAudit existed
that no model in this study ever saw. The population that matters is solutions that **pass
the visible tests and fail the hidden ones**; no LLM judge stands between the code and the
score. Studies 1–3 cannot say this — every number in them rests on CLEAR, a reimplementation
of a paper whose authors released no evaluation code and whose ground truth is itself
model-produced.

Whole-study spend: **$14.37** of a $20 budget.

Everything below is measured. Nothing is extrapolated.

---

## What was run

Preregistered in [`PREREGISTRATION-2.md`](PREREGISTRATION-2.md), committed before any model
call this study reports. Code frozen at **`9038400`** with `git status --porcelain` empty;
the freeze is recorded in `records/study2/manifest.json`.

| | |
|---|---|
| corpus | HumanEval (MIT, rev `7dce6050a7d6`), HumanEval+ (Apache-2.0, `d32357cf319e`), MBPP+ (Apache-2.0, `b2d74c91837c`) |
| problems | **540** — 542 less `HumanEval/32` and `Mbpp/590`, excluded by name before generation |
| generator | `anthropic:claude-haiku-4-5-20251001`, no rubric, no constitution |
| cross auditor | `openai:gpt-5.6-terra` |
| self auditor | `anthropic:claude-haiku-4-5-20251001` — the generator's own model |
| judge | **none. There is no judge in this study.** |
| constitution | the shipped `scaffold/templates/GENERAL_AUDIT_RULES.md`, unmodified |
| audit entry point | `crossaudit.auditor.run.run_audit` for the holistic arms — the product's real audit |
| seed | `20260905` |
| dates (UTC) | generation 2026-09-04 17:46→17:54; arms 18:03→20:03 |
| environment | Python 3.13.5, macOS-26.6.2-arm64, 30 s per-suite timeout |

### The population, and why n is 110

Assigned by execution alone. Study 1's entire P stratum is 56 instances, which the
preregistration's simulation showed has only **0.36 power** against a 10-point difference —
auditing it again would not have answered the question. P is ~10% of generated solutions,
so more P instances require more *solutions*, not more problems.

An **instance** is a `(batch, problem_id)` pair. Batch 1 is study 1's committed solution
set, **reused byte-identically**; batch 2 is a second pass of the frozen generator over the
same 540 problems. The preregistered rule — pool batches until P ≥ 100 or three batches —
stopped at two.

| batch | P | C | F |
|---|---:|---:|---:|
| b1 (study 1's, reused) | 56 | 455 | 29 |
| b2 (generated for this study) | 54 | 455 | 31 |
| **pooled population** | **110** | **910** | **60** |

**Batch 2 independently reproduces batch 1's strata** (C: 455 and 455; P: 56 and 54), which
is a second sign the harness measures what it claims to.

### The audit set

Drawn once from the seed, before any arm ran; every arm judged the identical set.

| stratum | population | audited | weight |
|---|---:|---:|---:|
| P | 110 | **110 (all)** | 1.00 |
| C | 910 | 150 | 6.07 |
| F | 60 | 30 | 2.00 |
| total | 1,080 | **290** | |

Nothing was regenerated per arm. **Every arm judged the same bytes.**

---

## The leakage guard — what the decomposer saw

The decomposed arm's number would be worthless if the hidden suite reached it. Stated
exactly:

- **The decomposer saw `problem.spec` and nothing else** — for HumanEval the function stub
  and its docstring, for MBPP the natural-language prompt plus the three visible
  assertions. **Not** the candidate solution, **not** the visible test source, **not** the
  hidden suite. The property list is therefore a function of the *problem*, computed once
  per problem (222 decompositions for 290 instances) and shared by every candidate.
- **The per-property checker saw** the specification, the candidate solution, the visible
  test source, and **one** property — exactly the increment `holistic-cross` receives, plus
  that property.
- **No prompt in any arm contained any part of the hidden suite.**

This is enforced structurally rather than by discipline: every prompt builder in
`architectures.py` takes **plain strings** and never a `Problem`, and the hidden suite lives
on `Problem._hidden_test`. A function that never receives the object cannot reach the
attribute.

`tests/test_architectures.py` proves it two ways, and both pass:

1. **the sentinel test** — a problem whose hidden suite is a unique string; that string
   appears in none of the six prompts the architectures build;
2. **the reachability test** — a problem whose `_hidden_test` **raises on access**; the
   whole decompose-and-check path runs to completion anyway. Absence of a string could be a
   coincidence of one fixture. A path that completes when the attribute is a landmine
   cannot reach the attribute.

A third test asserts the builders **reject** a `Problem` with `TypeError`, so the boundary
cannot be crossed by a future edit without the tests failing.

---

## Recall on P — the primary population

A flag is at least one BLOCKER finding; ADVISORY never gates in the product and does not
count, exactly as in study 1.

| arm | recall on P | k/n | 95% CI (Wilson) |
|---|---:|---:|---|
| `checks` | 0.0% | 0/110 | [0.0%, 3.4%] |
| **`holistic-cross`** (shipped) | **14.5%** | 16/110 | [9.2%, 22.3%] |
| `holistic-self` | 15.5% | 17/110 | [9.9%, 23.4%] |
| **`decomposed-cross`** | **23.6%** | **26/110** | **[16.7%, 32.4%]** |
| `two-stage-union` | 24.5% | 27/110 | [17.5%, 33.4%] |
| `two-stage-filtered` | 3.6% | 4/110 | [1.4%, 9.0%] |
| `decomposed-replicate` | 26.4% | 29/110 | [19.0%, 35.3%] |

`checks` scores zero by construction — these solutions pass the visible suite, so a suite
runner has nothing to say about them. That is the point of the population.

## The false-positive cost, reported here rather than in a footnote

| arm | flagged correct code | k/n | 95% CI |
|---|---:|---:|---|
| `checks` | 0.0% | 0/150 | [0.0%, 2.5%] |
| **`holistic-cross`** | **3.3%** | 5/150 | [1.4%, 7.6%] |
| `holistic-self` | 22.0% | 33/150 | [16.1%, 29.3%] |
| **`decomposed-cross`** | **11.3%** | **17/150** | **[7.2%, 17.4%]** |
| `two-stage-union` | 24.7% | 37/150 | [18.5%, 32.1%] |
| `two-stage-filtered` | 2.0% | 3/150 | [0.7%, 5.7%] |
| `decomposed-replicate` | 12.7% | 19/150 | [8.3%, 18.9%] |

## Stratum F — the sanity check

| arm | flagged | k/n |
|---|---:|---:|
| `checks` | 100.0% | 30/30 |
| `two-stage-union` | 96.7% | 29/30 |
| `holistic-cross` | 90.0% | 27/30 |
| `decomposed-cross` | 80.0% | 24/30 |
| `holistic-self` | 50.0% | 15/30 |

**Decomposition is *worse* than holistic review on code that does not even run** (80.0% vs
90.0%). Splitting the specification into properties and checking each in isolation removes
the reading in which a whole implementation is obviously broken. This is the clearest
qualitative cost of the architecture and it was not anticipated in the preregistration.

## Corpus level, reweighted

Reweighted by the known sampling fractions. A flag counts as correct if the solution fails
any test.

| arm | flag rate | precision |
|---|---:|---:|
| `checks` | 5.6% | **100.0%** |
| `holistic-cross` | 9.3% | **69.8%** |
| `decomposed-cross` | 16.4% | **41.8%** |
| `holistic-self` | 22.9% | 19.0% |
| `two-stage-union` | 28.7% | 27.5% |
| `two-stage-filtered` | 4.8% | 65.1% |

### The marginal precision of decomposition's extra flags

The comparison that matters is not the average but the margin — of the alarms decomposition
adds over holistic review, how many are right? Population-weighted:

| | weighted count |
|---|---:|
| flags decomposition **adds**, correct | 20.0 |
| flags decomposition **adds**, wrong | 84.9 |
| **marginal precision of the added flags** | **19.1%** |
| flags decomposition **loses**, correct | 16.0 |
| flags decomposition **loses**, wrong | 12.1 |

**Four in five of the extra alarms are false, and decomposition also loses 16 weighted true
findings that holistic review caught.** It is not a strictly better reader; it is a
different one.

---

## The six preregistered comparisons

Paired on identical instances. McNemar exact (binomial on the discordant pairs); 95%
intervals from a seeded paired bootstrap, 10,000 resamples, resampling instances.

### 1 & 2. `decomposed-cross` − `holistic-cross` — **the primary outcome**

| | on P (recall) | on C (false positives) |
|---|---|---|
| difference | **+9.1 points** | **+8.0 points** |
| rates | 23.6% vs 14.5% | 11.3% vs 3.3% |
| n | 110 | 150 |
| discordant | 18 decomposed-only vs 8 holistic-only | 14 vs 2 |
| exact p | **0.0755** | **0.0042** |
| 95% CI | **[+0.0, +18.2]** | **[+3.3, +13.3]** |

**This is the number the study exists for, and it does not clear the 0.05 line.** The point
estimate is 3.4× the noise floor measured below and the sign is consistent across both
generation batches independently (b1: 13/56 vs 7/56; b2: 13/54 vs 9/54), so the effect is
very unlikely to be nothing. But the interval's lower bound is zero, and this design has
0.75 power at 10 points — **the honest statement is that decomposition probably raises
recall by something like 9 points and this study cannot establish it.** The false-positive
increase, on the same instances at larger n, is established.

### 3 & 4. `two-stage-union` − `holistic-cross`

| | on P | on C |
|---|---|---|
| difference | **+10.0 points** | **+21.3 points** |
| n | 110 | 150 |
| discordant | 11 union-only vs 0 | 32 vs 0 |
| exact p | **0.00098** | **4.7 × 10⁻¹⁰** |
| 95% CI | [+4.5, +16.4] | [+15.3, +28.0] |

Taking the union of the two holistic arms is the **only** intervention in this study that
raises recall significantly. It does so by flagging a quarter of all correct code. It is a
demonstration that recall is available if false positives are free, and they are not.

### 5 & 6. `two-stage-filtered` − `holistic-cross`

| | on P | on C |
|---|---|---|
| difference | **−10.9 points** | −1.3 points |
| rates | 3.6% vs 14.5% | 2.0% vs 3.3% |
| n | 110 | 150 |
| discordant | 1 filtered-only vs 13 holistic-only | 2 vs 4 |
| exact p | **0.0018** | 0.6875 |
| 95% CI | [−17.3, −4.5] | [−4.7, +2.0] |

**The filter is not selective; it is simply destructive.** Showing the cross-vendor model
the self-vendor model's 65 proposals, it kept few enough that recall collapsed to 3.6% —
below the shipped architecture and barely above the deterministic floor — while the
false-positive rate improved by an amount indistinguishable from zero. A triage stage that
removes ten points of recall to remove one point of false positives is a bad trade in
either direction.

### The noise floor

`decomposed-cross` run a second time over the identical 290 instances:

| population | rates | disagreements | points apart |
|---|---|---:|---:|
| P | 26/110 vs 29/110 | 5 | **2.7** |
| C | 17/150 vs 19/150 | 8 | 1.3 |

And the holistic architecture measured across studies, on the 56 batch-1 instances study 1
audited byte-identically a day earlier:

| | rates | disagreements | points apart |
|---|---|---:|---:|
| `holistic-cross` (this study) vs study 1's `cross` | 7/56 vs 6/56 | 5 | 1.8 |
| study 1's internal replicate | 6/56 vs 5/56 | 3 | 1.8 |

**A difference smaller than about 3 points on P is not a finding in this study.** The
primary effect (9.1) is above it; the two-stage recall collapse (−10.9) is far above it.
That the shipped architecture reproduces to within 1.8 points across two studies, two
run dates and two independent samples is the strongest evidence that these arms are
measuring a stable property rather than sampling noise.

### Comparison count

**Six** preregistered comparisons (three arm pairs × two populations); the primary outcome
is one of them and was named before any model was called. The exploratory section below is
labelled and excluded from that count. Every other number in this file is descriptive. This
project has now run five studies over two tasks, and that history is part of the
multiple-comparison picture: the prose studies motivated this one, and this one's primary
hypothesis was formed after seeing the CLEAR-vs-holistic contrast described in the
preregistration.

---

## Exploratory — can filtering fix decomposition's false positives?

**Labelled exploratory: this arm's composition was fixed after the scores were seen.** The
preregistration listed `decomposed+two-stage` as conditional on budget but did not define
which stage proposes. Given the result above, the question worth the money was whether a
filter recovers decomposition's precision, so the decomposed arm's VIOLATED findings were
shown to the same cross-vendor model for keep/drop.

| | on P | on C |
|---|---|---|
| `decomposed+two-stage` | 21.8% (24/110) | 11.3% (17/150) |
| `decomposed-replicate` (its input) | 26.4% (29/110) | 12.7% (19/150) |
| difference | −4.5 points (p = 0.0625) | −1.3 points (p = 0.5) |

**Filtering did not fix the false positives.** It removed 5 true findings and 2 false ones.
Consistent with comparison 5, the filter behaves like a small uniform tax on findings rather
than a discriminator — which suggests the second model cannot tell the first model's good
findings from its bad ones on this material, and that is the same recall ceiling appearing
in a different place.

## Exploratory — where the violations come from

Of 1,407 property checks in the decomposed arm:

| category | violated / checks | rate |
|---|---:|---:|
| behaviour | 67 / 572 | 11.7% |
| contract | 29 / 303 | 9.6% |
| boundary | 21 / 293 | 7.2% |
| edge_case | 7 / 233 | 3.0% |
| error_handling | 1 / 6 | 16.7% |

The categories the brief expected to carry the gain — edge cases and boundaries — fire
least often. Mean 4.85 properties per instance.

---

## What it cost

From the product's own usage ledger, not reconstructed.

| arm | spend | calls | $/instance | $/true finding | s/instance |
|---|---:|---:|---:|---:|---:|
| `checks` | $0.0000 | 0 | — | — | 0.00 |
| `holistic-cross` | $2.0028 | 290 | $0.0069 | **$0.047** | 4.87 |
| `holistic-self` | $0.8241 | 302 | $0.0028 | $0.026 | 3.09 |
| **`decomposed-cross`** | **$5.4430** | **1,641** | **$0.0186** | **$0.108** | 8.41 |
| `two-stage-filtered` | $0.3194 | 65 | $0.0011 | $0.017 | 0.90 |
| `decomposed-replicate` | $4.3894 | 1,412 | $0.0151 | $0.078 | 5.34 |
| `decomposed+two-stage` | $0.4242 | 75 | $0.0015 | $0.009 | 1.28 |
| generation (batch 2, 540) | $0.7133 | 540 | — | — | — |
| probes + smoke | $0.2520 | 44 | — | — | — |
| **total** | **$14.3682** | 4,369 | | | |

**Decomposition costs 2.7× per instance and 2.3× per true finding.** It is 5.7 model calls
per instance against holistic review's one.

---

## Deviations from the plan, numbered, with the direction of each bias

1. **Base branch.** The brief specified branching from `fusion/evidence-authority`, but the
   code harness does not exist there — it lives on `feat/study-code` (`270169c`), a direct
   descendant whose merge-base with `fusion/evidence-authority` is that branch's tip. The
   worktree was branched from `feat/study-code` so that `benchmarks/code/` was present. No
   study parameter differs; no bias.
2. **Two provider probes before the preregistration** (`"Say READY."`, $0.00015) to prove
   both credentials resolved before committing budget. They produce no study number.
3. **A 3-instance smoke test before the arms** ($0.2519), on instances that are in the audit
   set, whose flags were therefore seen before the arms ran. Two harness changes followed
   it: per-property concurrency (deviation 4) and stratum ordering (deviation 5). **Neither
   can change any instance's verdict.** The smoke rows were discarded and all three
   instances were re-audited from scratch inside the real arms. No bias.
4. **The per-property checks run 4-way concurrent within one instance.** The properties are
   independent by construction — that is the architecture — and no call sees another's
   prompt or reply; results are reassembled in the original property order. Wall time only.
5. **Each arm processes P, then C, then F.** The preregistered stopping rule is a budget, so
   this guarantees that running out of money truncates a secondary outcome rather than the
   primary. Each instance is audited independently, so order cannot change a result.
6. **`holistic-cross` and `decomposed-cross` carry no deterministic layer**, as
   preregistered, so the primary comparison isolates audit architecture. On stratum P this
   is immaterial — `checks` flags 0/110 there by construction — but it means
   `holistic-cross` is **not** identical to study 1's shipped `cross+checks` arm, and the
   F-stratum numbers are lower than the shipped configuration's for that reason.
7. **The decomposed replicate reused the cached property lists**, so it measures the
   run-to-run variance of the *checking* stage only, not of the decomposer. This
   **understates** total variance for that architecture, which makes the noise floor a
   floor rather than an estimate, and therefore makes the primary effect's margin over it
   look larger than a full re-decomposition might.
8. **`decomposed+two-stage`'s composition was chosen after scores were seen** and is
   labelled exploratory throughout; it is excluded from the six preregistered comparisons.
9. **A mid-study recording change**: the decomposed arm began storing VIOLATED evidence text
   in the gitignored run directory so the combined arm had something to filter. It touches
   no verdict — `aggregate()` reads only the verdict field — and applies only to the
   replicate. `export2.py` drops it from the committed record.
10. **`holistic-self` made 302 calls for 290 instances**: 12 provider-layer retries after
    malformed replies. Three instances still ended with `invalid_reason` (`Mbpp/92` in both
    batches, `Mbpp/388` in b2) and are counted as not flagged, which lowers that arm's
    recall slightly.
11. **Two instances decomposed to zero properties** and are counted as not flagged. That is
    the conservative direction: it can only **lower** the decomposed arm's recall.
12. **One of 1,407 check replies was unparseable** and was treated as UNCLEAR, which does
    not flag — again conservative for the decomposed arm.
13. **Batch 2 was generated to reach n**, following the preregistered pooling rule, which
    stopped at two batches because P = 110 ≥ 100. The rule reads execution outcomes only and
    never an audit score.
14. **Temperature and seed are not controllable.** CrossAudit's provider layer takes
    temperature from the model's capability card and exposes no seed, so no run reproduces
    byte-identically. The replicate arm quantifies what that costs.
15. **The `self` arm bypasses a product guarantee.** `run_audit` raises `ConfigDenial` on a
    same-vendor generator/auditor pair; the arm leaves `generator:` unset. A deliberate
    bypass for measurement, inherited from study 1.
16. **Two problems excluded** (`HumanEval/32`, `Mbpp/590`) before generation, by name,
    because their reference solutions fail their own hidden suites. Inherited from study 1.
17. **Another study ran against the same credentials throughout.** No rate-limit failure
    occurred in this study; generation ran 3-way concurrent and every arm completed with
    zero errored rows.

## Limitations, stated here rather than left to the reader

- **The primary outcome is underpowered and says so.** 0.75 power at 10 points, an observed
  effect of 9.1, p = 0.076. This study establishes the sign and the false-positive cost; it
  does not establish the recall magnitude. Confirming it needs roughly n = 200 on P, which
  means two or three more generation batches.
- **Pooled instances are not fully independent.** 110 P instances come from fewer distinct
  problems, so two instances can share a specification. The pairing is per instance so
  McNemar remains valid, but the effective n is somewhat below 110.
- **One decomposer prompt is one decomposer prompt.** A different enumeration prompt — more
  properties, stricter thresholds, a different VIOLATED bar — would move both columns. This
  study measures *a* decomposition, not decomposition in general, and the aggregation rule
  (any VIOLATED is a BLOCKER) is the most sensitive one available.
- **Two Python benchmarks of short, self-contained functions are not a repository.** No
  build, no dependencies, no cross-file invariants, no history. The defects a real auditor
  must catch — a race, a migration that drops a column, an API contract broken three files
  away — are not in this corpus.
- **One generator.** A finding about `claude-haiku-4-5`'s errors is a finding about that
  model's errors, and a small model's wrong-but-plausible code is plausibly more obviously
  wrong than a frontier model's — which biases every recall figure here **upward**.
- **Vendor independence is not statistical independence.** `gpt-5.6-terra` and
  `claude-haiku-4-5` share training data, architecture and human-feedback conventions.
- **Round one only.** Whether revision then improves the code is a separate question, and
  study 3 found that on prose revision made things measurably worse.

## What this run does and does not license

**It does not license** the claim that decomposition fixes CrossAudit's recall. The primary
outcome is +9.1 points at p = 0.076 with an interval touching zero, and the same change
triples the false-positive rate on correct code with p = 0.0042. Shipping decomposition as
the default audit would, on this evidence, make the product noticeably noisier for a recall
gain it has not demonstrated.

**It does not license** the claim that structure is irrelevant either — that reading is
contradicted by the disjointness. Holistic and decomposed review flagged **largely different
defects** (18 / 8 / 8), and their union reaches 30.9% against 14.5%. Swapping the auditor
*model* on prose moved recall 2.0% → 3.8%. Changing the *structure* here moved which defects
were found at all. **The lever is real; this study has not found the setting that pays.**

**It does license** four statements:

1. **The binding constraint is still recall, and it is still not the model.** Four
   architectures, two vendors, and the best single arm finds a quarter of what the tests
   miss.
2. **Decomposition trades precision for recall at a bad exchange rate.** Marginal precision
   of its extra flags is 19.1%; it is also *worse* than holistic review on code that does
   not run (80.0% vs 90.0%).
3. **A second model filtering a first model's findings does not work here.** It removed ten
   points of recall for one point of false positives, and filtering the decomposed arm
   removed five true findings and two false ones. The second reader cannot tell the first
   reader's good findings from its bad ones.
4. **The complementarity is the finding worth pursuing.** Two architectures that overlap on
   8 of 34 defects are not two attempts at the same thing. Whatever raises this product's
   recall is more likely to look like combining structurally different readers under a
   precision constraint than like replacing one reader with a better one.

**Do not re-run this study hoping for a different number.** If the configuration changes,
the study restarts and says so here.

---

## Reproduction

```sh
export PYTHONPATH="$(git rev-parse --show-toplevel)/src"
# credentials: CROSSAUDIT_ANTHROPIC_KEY and CROSSAUDIT_OPENAI_KEY, or the role fallbacks
python benchmarks/code/fetch.py                        # ~1 min; corpus is not committed
# batch 1 is study 1's committed solutions, reused byte-identically:
cp runs/study1/{solutions,scored}.jsonl runs/study2/   # renamed -b1
python benchmarks/code/generate.py --project <a crossaudit project> \
    --out runs/study2/solutions-b2.jsonl --exclude "HumanEval/32,Mbpp/590" \
    --run-id arch-gen-b2 --workers 3
python benchmarks/code/evaluate.py --solutions runs/study2/solutions-b2.jsonl \
    --out runs/study2/scored-b2.jsonl
python benchmarks/code/pool.py --run runs/study2
pytest benchmarks/code/tests/test_architectures.py     # the leakage guard must pass first
for arm in checks holistic-cross decomposed-cross holistic-self; do
  python benchmarks/code/audit2.py --run runs/study2 --arm "$arm" \
    --out "runs/study2/arm-$arm.jsonl" --scratch /tmp/arms --run-id "arch-$arm"
done
python benchmarks/code/audit2.py --run runs/study2 --arm two-stage-filter \
    --out runs/study2/arm-two-stage-filter.jsonl --scratch /tmp/arms \
    --propose-from runs/study2/arm-holistic-self.jsonl --run-id arch-two-stage
python benchmarks/code/report2.py --run runs/study2 --json-out runs/study2/numbers.json
python benchmarks/code/export2.py --run runs/study2 --records benchmarks/code/records/study2
```

It will not reproduce byte-identically (deviation 14). The replicate arm measures how much
that matters: 5 flags of 110 changed.

The committed record is `benchmarks/code/records/study2/` — one JSONL row per instance per
arm with the stratum, the flag, per-property verdict vectors, rule ids, finding and property
hashes, tokens, cost and time, plus `properties_shape.json` giving each problem's property
count, categories and hashes. **No corpus text, no generated solutions, no finding prose,
and no prompt that embeds any of them.** The full run directory, which does contain those,
stays on disk at `benchmarks/code/runs/study2/` and is gitignored.
