# The ceiling of AI audit — self-audit did not raise accuracy; naming the gap did the most

> **Second version.** An independent cross-vendor review reproduced every headline number
> and then refused quotation approval, because the headline's "95% exact" interval did not
> have 95% coverage. It was right. **Every point estimate in this report is unchanged;
> every interval and every p-value has been recomputed**, the overclaims it identified are
> gone, and its findings are answered one by one in *What the review changed*. The
> withdrawn interval, its measured coverage, and a test that pins it are all kept in the
> record.

**The owner's question was: as AI-generated data grows, can AI audit itself to raise
accuracy, and where is the limit? On this evidence the answer to the first half is no.**

A generator's own model, auditing its own code and then revising it, changed the fraction
of solutions passing a hidden test suite by **+0.89 percentage points (95% problem-cluster
bootstrap CI [−3.54, +5.88]; Tango [−3.98, +6.06]; exact unconditional [−6.70, +8.48];
exact McNemar p = 1.0000; cluster sign-flip p = 1.0000; n = 112 instances from 96
problems)**. It repaired 3 of 56 wrong solutions and broke 2 of 56 correct ones. **The
preregistered kill condition fires under every one of those intervals**: all four contain
zero.

Four further results, in the order they matter.

**1. Reading the same code more times saturates, and not high.** Unioning eight independent
readings by the shipped cross-vendor auditor lifts recall on the defect population from
**10.7% [5.1, 17.4]** to **30.0% (33 of 110) [20.0, 40.7]**, while false positives on
correct code go from **4.5% [2.4, 7.0]** to **16.0% [10.1, 22.3]**. Its fitted asymptote is
31.5% [21.7, 45.6], **but that curve has not flattened** — it still gained 1.93 points from
K = 7 to K = 8, failing the preregistered flattening bar — **so 31.5% is an extrapolation
and 30.0% is the number to quote.** The generator's own model does flatten, and far lower:
**15.5% [7.1, 24.9]** at one reading, **17.3% (19 of 110) [8.3, 27.3]** at eight, asymptote
**16.6% [8.1, 26.3]**, at a false-positive rate of **24.0% [17.2, 31.2]**.

**The preregistered primary outcome, A(self) − A(cross) on stratum P, is −14.9 points, 95%
problem-cluster bootstrap CI [−32.1, −2.3]**; the model-free version, the raw difference of
union recalls at eight readings, is **−12.7 points [−25.0, −0.9]**. Both are negative and
both exclude zero. Over the readings actually taken, **the author's own model found less of
its own bad code than a stranger did, and flagged more good code doing it.** Because
`cross`'s curve is still rising, the asymptote comparison is a comparison of one fitted
extrapolation against one flattened fit, and the raw eight-reading difference is the
sturdier of the two.

**2. Repetition is not the lever; the model is one, and the instructions are a bigger one.**
The `self` route is near-deterministic — its eight draws disagree on 0 to 3 of 260
instances, and the closed-loop replicate returned **identical final solutions, flags and
outcomes on all 112 instances**. Eight readings find **two** more defects than the best
single reading (17 → 19). Meanwhile **one reading by the strongest model available
(`gpt-6-astra`, high reasoning) recalls 30.2% [19.3, 42.0] at 9.7% [5.3, 14.5] false
positives, matching eight unioned readings of the shipped auditor on recall at less than
two-thirds of the false-positive cost** (30.0% at 16.0%).

The largest effect measured anywhere in this study came from changing what the auditor was
told to look for. One added constitution rule — *find what the visible tests do not cover* —
moved flags on the defect population from 10 of 56 to 25 of 56: **+26.8 points, cluster CI
[13.6, 40.4], exact unconditional [+6.3, +43.8], McNemar p = 0.0003, cluster sign-flip
p = 0.0009** — the only contrast in this study that clears a Bonferroni threshold over the
sixteen comparisons actually computed (0.00313). **It is nevertheless an exploratory
contrast**: the preregistration named outcome contrasts, not flag contrasts.

**On accuracy rather than flags, the referent's advantage is not established.** Against its
own baseline the referent arm nets **+8.04 pp, cluster CI [1.77, 15.26], Tango [2.03,
15.27], p = 0.0225, cluster p = 0.0469** — but the exact unconditional interval, the most
conservative of the three, is **[−1.79, +17.41] and contains zero**. And the contrast that
actually isolates the referent, **referent-loop minus cross-loop, is +5.36 pp, cluster CI
[−0.88, +12.08], p = 0.1460** — it does not exclude zero. **The referent demonstrably moves
what the auditor flags; whether that converts into accuracy is not established here.** The
title says "did the most", not "works".

**3. Half the defects were flagged by no reading of any family.** **57 of 110 defective
solutions (51.8%, cluster CI [40.0, 63.3]) were flagged by no reading of any family** — 20
readings, three models, two vendors, one frontier route. Classified by hand under a rule
fixed before the first was opened, **46 of those 57 (80.7% [68.7, 88.9]) fail only on an
input class the visible test suite never constructs**: the empty list, the negative number,
the two-digit case, the ragged input, the punctuation character. **That is the shape of what
was missed.** A model shown a specification and a test suite has no evidence in front of it
that those classes exist. **This does not establish that such defects cannot be found** —
it establishes that these detectors did not find them, and that the one intervention that
named the gap moved flags more than anything else tried.

**4. The population is hidden-suite non-passes, not confirmed assertion failures.** Seven of
the 110 stratum-P instances fail because the hidden suite **did not terminate**. The
registered analysis keeps the registered population; Table 9 narrows it to the 103
instances with an observed assertion failure, and nothing moves: unions 32 / 18 / 34 against
33 / 19 / 36, residual 54 of 103 (52.4%) against 57 of 110 (51.8%).

**Total spend: $13.23 of a $20 budget, plus 4,427,530 tokens on a subscription-billed route
that reports no dollar cost.**

---

## What the review changed

An independent reviewer on a different vendor's model read the committed record at
`f7f515e`, reproduced the numbers, and returned nine findings. All nine reproduced here
before anything was altered. This section is the audit trail; the sections after it are the
corrected report.

| # | Finding | Reproduced | What changed |
|---|---|---|---|
| 1 | The paired interval rescaled a **conditional** Clopper–Pearson by the **observed** discordance fraction, discarding the uncertainty in that fraction. Coverage **0.416**, not 0.95 | coverage = **0.4162688657**, matching the reviewer to 10 digits | Interval replaced. Primary is now the problem-cluster bootstrap; checks are Tango's unconditional score interval and a Berger–Boos-restricted exact unconditional interval. Measured coverages: **0.416 (withdrawn) → 0.960 (Tango) → 0.998 (exact)**. A coverage test pins all three |
| 2 | Binary inference ignored problem clusters that the saturation bootstrap already respected | 112 loop instances from **96** problems; 110 P instances from **56** | Every interval is now a problem-cluster bootstrap; a cluster sign-flip permutation p sits beside every McNemar p. Reproduced the reviewer's sensitivities exactly: referent-loop 0.0225 → **0.0469**, referent-minus-cross flags 0.0003 → **0.0009** |
| 3 | "In the limit of unlimited readings" where the curve had not flattened; "cannot be seen"; the title's causal claim | cross gains **1.93 pp** from K=7 to K=8 | Extrapolation caveat now carried in the headline, Table 1 (`flat?` column) and the conclusion. "Was not flagged by any reading", never "cannot be seen". Title and headline now lead with the between-arm contrast (+5.36 pp, p = 0.146) |
| 4 | Twelve planned, **16** computed; the highlighted contrast was not among the twelve; "exactly one clears" was false | 16 `p_exact` entries enumerated | Full planned/performed/exploratory inventory in `numbers.json`; one correction family of 16; threshold 0.00313; every flag contrast labelled EXPLORATORY. Five planned mixed/astra asymptote contrasts were **not delivered** — recorded as deviation 15 |
| 5 | Timeouts inside a population described as assertion-confirmed | **7** P timeouts, 3 in the loop sample, 3 in the residual | Population renamed "hidden-suite non-passes, including timeouts"; Table 9 adds the assertion-only sensitivity (103 / 32 / 18 / 34 / residual 54), reproducing the reviewer |
| 6 | Provenance gaps; "no number had left the harness" overstated | `1a66571:tables.md` carries the swapped interval, committed 18:46:39, fixed 18:48:18 | Manifests now carry package versions, per-invocation UTC windows, base URLs, corrected sampling metadata (**the self route sends temperature 0**), the dirty-tree record and re-hashed files. The beta-bug sentence is corrected below |
| 7 | `returned_non_solution` said zero; it is 4/4/2/0. "Bias: none" unsupported | reproduced exactly | Deviations 2, 3 and 5 corrected; bias directions now stated as undetermined where they are |
| 8 | `Mbpp/305` description; "one more defect"; "byte-identical output" | self union adds **two** (17→19); `report_sha256` differs on `b1:HumanEval/35` | Classification description corrected (category unchanged); "adds two"; "identical final solutions, flags and outcomes" |
| 9 | The fitter left its registered bound `A ∈ [0,1]` | `fit_saturation(union_curve([1]*110, 8))` returned **250.4** | Constrained inside the objective, so both bootstrap paths treat the boundary identically. **No quoted estimate moved** |

**What did not change: any point estimate.** The asymptotes, the union curves, the primary
difference, the arm nets, the residual counts and the classification are identical to the
first version. What changed is what may be claimed around them.

---

## What was run

Preregistered in [`ceiling/PREREGISTRATION.md`](ceiling/PREREGISTRATION.md), committed at
`d96cdaf`, with amendments 1–2 (the `astra` family) and amendment 3 (the reporting standard)
at `87939d2` — **all before the first model call of this study, including the credential
probe.**

| | |
|---|---|
| audit set | study 2's, unchanged: **290 instances**; this study's scope is P + C = **260** |
| stratum P | passes every visible test, **does not pass the hidden suite** — n = 110 from **56 problems**, and **7 of the 110 are timeouts, not observed assertion failures** |
| stratum C | passes every test — the false-positive population — n = 150 |
| ground truth | a Python interpreter raising `AssertionError`, or failing to terminate. **No model judges anything** |
| solutions | study 2's, byte-identical, **not regenerated** |
| generator | `anthropic:claude-haiku-4-5-20251001`, frozen |
| `cross` | `openai:gpt-5.6-terra`, **K = 8 draws** — capability card `temperature: False`, so no sampling parameter is sent and the route varies run to run |
| `self` | `anthropic:claude-haiku-4-5-20251001`, **K = 8** — capability card permits temperature, so the layer sends **temperature = 0**, and the route is near-deterministic |
| `astra` | `gpt-6-astra` at high reasoning, through the Codex CLI, **K = 4** |
| flag | ≥ 1 BLOCKER finding, exactly as studies 1, 2 and 7 |
| audit path | `crossaudit.auditor.run.run_audit` — the product's real audit, unchanged |
| environment | Python 3.13.5, macOS 26.6.2 arm64; package versions in the manifests |

**The `astra` prompt is the shipped auditor's prompt, byte for byte** — built by the
product's own `auditor.prompt.build`, and its `prompt_sha256` checked against study 2's
committed `holistic-cross` digests: **40 of 40 agree**. It bypasses the provider broker, the
metered ledger and the same-vendor guard, so **it is a measurement of a model, not of the
product path**.

**Baseline check.** All 112 solutions in the ceiling-2 sample were re-executed on this
machine before any arm was scored: **112 of 112 reproduce the stratum study 2 recorded**
(`records/ceiling/baseline_reproduction.json`).

---

## Ceiling 1 — how much these readers saw

### Table 1 — the saturation curve, per family

Unit of analysis: the instance. n = 110 stratum-P instances (recall) and 150 stratum-C instances (false positives), the same instances at every K. Union rate at K is averaged over all C(K_max, K) subsets of that family's draws, exactly.

Every rate carries a 95% **problem-cluster bootstrap** interval; the P population is 110 instances from only **56 problems**, so an interval that treats instances as independent is too narrow. `flat?` says whether the curve met the preregistered flattening bar (last-step gain ≤ 1.0 point); where it did not, **A is an extrapolation** and the raw union at K_max is the number to quote.

| family | K_max | union recall on P at K=1 [95% CI] | at K_max [95% CI] | fitted asymptote A [95% CI] | union FP on C at K=1 [95% CI] | at K_max [95% CI] | last-step gain | flat? |
|---|---:|---|---|---|---|---|---:|:---:|
| `cross` | 8 | 10.7% [5.1, 17.4] | **30.0%** (33/110) [20.0, 40.7] | 31.5% [21.7, 45.6] *(extrapolation)* | 4.5% [2.4, 7.0] | **16.0%** [10.1, 22.3] | 1.93% | **no** |
| `self` | 8 | 15.5% [7.1, 24.9] | **17.3%** (19/110) [8.3, 27.3] | **16.6%** [8.1, 26.3] | 21.9% [15.5, 28.9] | **24.0%** [17.2, 31.2] | 0.23% | yes |
| `astra` | 4 | 30.2% [19.3, 42.0] | **32.7%** (36/110) [20.7, 45.0] | **32.5%** [20.5, 44.8] | 9.7% [5.3, 14.5] | **10.7%** [5.9, 16.1] | 0.23% | yes |

### Table 2 — union recall and union false positives at every K

Unit of analysis: the instance; the same instances at every K, so the columns are repeated measures and not independent samples.


**`cross`** (K_max = 8, n = 110 P instances, 150 C instances)

| K | union recall on P | union FP on C | recall per FP point |
|---:|---:|---:|---:|
| 1 | 10.7% | 4.5% | — |
| 2 | 15.0% | 7.1% | 1.67 |
| 3 | 18.3% | 9.2% | 1.63 |
| 4 | 21.2% | 10.9% | 1.64 |
| 5 | 23.8% | 12.4% | 1.65 |
| 6 | 26.0% | 13.7% | 1.66 |
| 7 | 28.1% | 14.9% | 1.67 |
| 8 | 30.0% | 16.0% | 1.68 |

**`self`** (K_max = 8, n = 110 P instances, 150 C instances)

| K | union recall on P | union FP on C | recall per FP point |
|---:|---:|---:|---:|
| 1 | 15.5% | 21.9% | — |
| 2 | 15.9% | 22.6% | 0.62 |
| 3 | 16.1% | 22.9% | 0.67 |
| 4 | 16.4% | 23.2% | 0.71 |
| 5 | 16.6% | 23.4% | 0.75 |
| 6 | 16.8% | 23.6% | 0.79 |
| 7 | 17.0% | 23.8% | 0.83 |
| 8 | 17.3% | 24.0% | 0.87 |

**`astra`** (K_max = 4, n = 110 P instances, 150 C instances)

| K | union recall on P | union FP on C | recall per FP point |
|---:|---:|---:|---:|
| 1 | 30.2% | 9.7% | — |
| 2 | 32.0% | 10.2% | 3.14 |
| 3 | 32.5% | 10.5% | 2.73 |
| 4 | 32.7% | 10.7% | 2.50 |

### Table 3 — primary outcome, ceiling 1: A(self) − A(cross)

K_common = 8 draws per family. Positive means the generator's own model can ultimately see more of its own defects than a stranger can. Interval: 95% percentile bootstrap over problem clusters, both curves resampled together.

| stratum | n instances | A(cross) | A(self) | A(self) − A(cross) [95% CI] | raw union difference at K_common [95% CI] |
|---|---:|---:|---:|---|---|
| P | 110 | 31.5% | 16.6% | **-14.9%** [-32.1, -2.3] | -12.7% [-25.0, -0.9] |
| C | 150 | 18.6% | 23.4% | **4.8%** [-7.6, 14.3] | 8.0% [-0.7, 16.8] |


### Reading the fit honestly

The saturation form `recall(K) = A(1 − e^{−K/τ})` was preregistered with its assumptions:
exchangeable draws, a per-instance detection probability constant across draws, and a single
exponential — exact only when the detectable instances are homogeneous, and **conservative
under heterogeneity**, which for an asymptote is the direction to err in. `A` is now
constrained to [0, 1] **inside the objective**, so the point fit and every bootstrap path
treat the boundary identically; no quoted estimate moved when that was fixed.

**`cross`'s asymptote is an extrapolation, and the report says so wherever it appears.**
Its marginal gain from seven to eight draws is **1.93 points**, above the preregistered
1.0-point bar. R² is 0.968 with a maximum residual of 2.37 points. **The number to quote for
`cross` is the raw union at K = 8: 30.0% (33 of 110), cluster CI [20.0, 40.7].** 31.5% is
what one particular functional form says lies beyond the readings taken, and an
*under*estimating fit is a lower bound on eventual recall, not evidence of a low upper
ceiling.

**`self`'s and `astra`'s asymptotes are not extrapolations.** Both gain 0.23 points on their
last step, and for both the fitted asymptote and the raw union at K_max agree to within a
point. `self`'s low R² (0.476) reflects a nearly flat curve with almost no variance to
explain; its residuals are at most 0.66 points.

**The preregistered secondary estimator failed exactly as predicted.** The zero-inflated
beta-binomial returned **π = 1.000** for both `cross` and `self` — "everything is findable
eventually" — which is what an unidentifiable mixture returns when a Beta component with
a → 0 can imitate the zero-inflated mass. §1.2 said in advance that π would be unstable
upward from eight draws. It is, it is uninformative, and it is reported rather than dropped.

### Repetition is not the lever

Every pair of this study's own complete draws, over the same 260 instances, on the same
basis — the number of instances on which two draws of one family disagree:

| family | pairwise disagreement, of 260 instances | what K readings add over the best single draw |
|---|---|---|
| `cross` (draws 4–8, 10 pairs) | **15 to 21** | 33 of 110 unioned, against 16 for the best draw |
| `astra` (draws 1–4, 6 pairs) | **4 to 7** | 36, against 35 |
| `self` (draws 3–8, 15 pairs) | **0 to 3** | 19, against 17 |

The mechanism is in the manifests: the `self` route's capability card permits temperature,
so the provider layer sends **temperature = 0**; the `cross` route's card carries
`temperature: False`, so nothing is sent and the route samples. Corroborated outside this
study's draws: `self` disagrees with study 1's `self` arm on **1 of 106** shared instances
across a day and a commit, and the `self-loop` / `self-loop-rep` replicate produced
**identical final solutions, flags and outcomes on all 112 instances** (one audit report
differs in bytes, on `b1:HumanEval/35`, without changing its findings).

**Buying recall by re-reading only works where the route samples, and it is the expensive
way to buy it.** Eight `cross` readings reach 30.0% at 16.0% false positives; one `astra`
reading reaches 30.2% at 9.7%.

### Mixing families at matched total readings

### Table 4 — mixed families at matched total draws

Unit of analysis: the instance. Each row spends the same total number of readings; the question is whether spreading them across families beats spending them all inside one.

| combination | total draws | per family | union recall on P | union FP on C | same total inside one family (recall) |
|---|---:|---:|---:|---:|---|
| `cross+self` | 2 | 1 | 21.3% | 24.6% | `cross` 15.0%; `self` 15.9% |
| `cross+self` | 4 | 2 | 25.1% | 26.9% | `cross` 21.2%; `self` 16.4% |
| `cross+self` | 6 | 3 | 28.2% | 28.5% | `cross` 26.0%; `self` 16.8% |
| `cross+self` | 8 | 4 | 30.7% | 29.9% | `cross` 30.0%; `self` 17.3% |
| `cross+self` | 10 | 5 | 32.9% | 31.1% | — |
| `cross+self` | 12 | 6 | 34.8% | 32.2% | — |
| `cross+self` | 14 | 7 | 36.6% | 33.2% | — |
| `cross+self` | 16 | 8 | 38.2% | 34.0% | — |
| `cross+self+astra` | 3 | 1 | 37.5% | 29.7% | `cross` 18.3%; `self` 16.1%; `astra` 32.5% |
| `cross+self+astra` | 6 | 2 | 40.6% | 31.3% | `cross` 26.0%; `self` 16.8% |
| `cross+self+astra` | 9 | 3 | 42.3% | 32.4% | — |
| `cross+self+astra` | 12 | 4 | 43.6% | 33.4% | — |
| `cross+astra` | 2 | 1 | 31.3% | 11.2% | `cross` 15.0%; `astra` 32.0% |
| `cross+astra` | 4 | 2 | 34.0% | 12.6% | `cross` 21.2%; `astra` 32.7% |
| `cross+astra` | 6 | 3 | 35.6% | 13.7% | `cross` 26.0% |
| `cross+astra` | 8 | 4 | 36.8% | 14.7% | `cross` 30.0% |
| `self+astra` | 2 | 1 | 36.5% | 28.3% | `self` 15.9%; `astra` 32.0% |
| `self+astra` | 4 | 2 | 38.5% | 29.5% | `self` 16.4%; `astra` 32.7% |
| `self+astra` | 6 | 3 | 39.2% | 30.1% | `self` 16.8% |
| `self+astra` | 8 | 4 | 39.5% | 30.5% | `self` 17.3% |


At 8 total readings, `cross+astra` (4 each) reaches **36.8% recall at 14.7% false
positives**, against `cross` alone at 8 readings on **30.0% at 16.0%** — the only place here
where both axes improve together. Every combination containing `self` carries a
false-positive rate near or above 28%, because a union inherits every member's false alarms
and `self`'s own rate is 24.0%.

**These mixed-family rows are raw union rates, not the fitted asymptote contrasts the
preregistration named** (deviation 15). Five planned comparisons — the mixed and `astra`
asymptote differences — were **not delivered as specified and are unmeasured in this
study**. The rows below are descriptive and exploratory.

---

## What no reading flagged

### Table 5 — the residual: stratum-P defects no draw ever flagged

| population | families | total draws | n P instances (problems) | never flagged | share [95% cluster CI] | [95% Wilson, too narrow] |
|---|---|---:|---:|---:|---|---|
| broker_families_only | cross, self | 16 | 110 (56) | **68** | **61.8%** [50.9, 72.7] | [52.5, 70.4] |
| all_families | cross, self, astra | 20 | 110 (56) | **57** | **51.8%** [40.0, 63.3] | [42.6, 60.9] |

### Table 5b — what the residual defects are

Categories and their order were fixed in the preregistration (§1.5) before the first residual instance was read; each instance takes the first category that applies. Unit: the instance. Intervals are 95% Wilson on the residual denominator.

| population | n residual | category | count | share [95% Wilson] |
|---|---:|---|---:|---|
| broker_families_only | 68 | `unexercised-edge` | 55 | 80.9% [70.0, 88.5] |
| broker_families_only | 68 | `spec-misreading` | 8 | 11.8% [6.1, 21.5] |
| broker_families_only | 68 | `timeout` | 5 | 7.4% [3.2, 16.1] |
| all_families | 57 | `unexercised-edge` | 46 | 80.7% [68.7, 88.9] |
| all_families | 57 | `spec-misreading` | 8 | 14.0% [7.3, 25.3] |
| all_families | 57 | `timeout` | 3 | 5.3% [1.8, 14.4] |


Under a rule fixed in the preregistration before the first residual instance was opened, and
applied by taking the first category that fits:

- **`unexercised-edge` — 46 of 57 (80.7% [68.7, 88.9])**, over 27 distinct problems. The
  candidate is correct on every input class the visible suite constructs and fails only on
  a class it never constructs: the empty list (`Mbpp/305`, `Mbpp/559`), a zero-length string
  (`Mbpp/113`, `Mbpp/771`), a negative number (`Mbpp/99`, `Mbpp/244`), ragged inputs
  (`Mbpp/142`, `Mbpp/391`), floats where the oracle counts only integers (`Mbpp/294`,
  `Mbpp/410`), punctuation (`Mbpp/7`, `Mbpp/459`), a two-digit number (`Mbpp/92`).
- **`spec-misreading` — 8 of 57 (14.0% [7.3, 25.3])**, over 5 problems: the candidate
  computes a self-consistent but different function from the one the prose states, and the
  visible tests do not separate the two readings.
- **`timeout` — 3 of 57 (5.3% [1.8, 14.4])**: the suite did not terminate, so no assertion
  evidence exists. These sit **inside** the residual and inside stratum P; Table 9 is the
  sensitivity analysis that removes them.
- **`wrong-algorithm` — 0. `ambiguous-oracle` — 0.**

**Two of the six preregistered categories were never used, and that is a defect in the rule,
not a fact about the world.** The ordering puts `unexercised-edge` second and
`ambiguous-oracle` fifth, so any instance whose oracle is arguable *and* whose failure is
confined to an unexercised input class lands in `unexercised-edge`. The rule was applied as
written; the consequence is recorded so no reader concludes that every EvalPlus expectation
was found defensible.

**Exploratory, and labelled exploratory: in 40 of the 57 residual instances a competent
reader could defend the candidate against the specification's prose as written.** This flag
is not part of the preregistered rule, it was added after the categories were assigned, and
it is a judgement of the author's.

**What the frontier model added.** Eleven instances sit in the broker-only residual but not
the all-family residual — `astra` flagged them and 16 readings by two broker models did not.
**Six of those eleven are crashes**: `IndexError` on an empty array, `ValueError` from
`math.sqrt` on a negative, `TypeError` from a complex square root, a `ValueError` unpacking
an over-long tuple. The strongest model was disproportionately better at the most
mechanically checkable defect there is — *this input makes the program raise* — and not
disproportionately better at the rest.

**The sentence this study supports.** The defects no reader here flagged are not subtle
reasoning failures; they are ordinary defects on inputs nobody wrote a test for. **A model
shown a specification and a test suite has no evidence in front of it that the omitted input
classes exist**, and eight more readings did not manufacture that evidence. Whether such
evidence can be supplied is a separate question, and the one manipulation in this study that
supplied it moved flags by 26.8 points. **That is a demonstration about instructions, not a
proof about what models can reason about.**

---

## Ceiling 2 — whether the loop raised accuracy

The loop is `frozen solution → run_audit → (if BLOCKED) the product's own revision → hidden
suite`, over a frozen, paired 112-instance sample (56 P, 56 C, seed 20260907, **96 distinct
problems**). Generation is not repeated. The revision prompt is the product's own.

**The primary outcome is unconditional on whether a revision occurred** — `CORRECTIONS.md`
item 9 is this project's largest retraction and it is exactly the error of conditioning on a
consequence of the treatment.

### Table 6 — ceiling 2: the closed loop, per arm

Unit of analysis: the instance, paired before/after on the same instance; the resampling unit is the problem. Net is unconditional on whether a revision occurred.

The primary interval is the **problem-cluster bootstrap**; Tango's unconditional score interval and the exact unconditional interval (Berger-Boos restricted) are checks that ignore clustering. `p` is exact McNemar (instances independent); `p_clu` is a cluster-level sign-flip permutation test beside it. 112 instances come from **96 problems**.

**†** — every discordant pair points the same way, so the percentile bootstrap cannot produce a resample of the opposite sign and its bound at zero is an artefact of the method. Read the Tango or exact unconditional interval on that row. This is `CORRECTIONS.md` item 4 applying to the replacement as it applied to what it replaced.

| arm | n (problems) | BLOCKED (P / C) | changed | fixed on P | broken on C | **net change** [95% cluster CI] | Tango CI | exact-unc. CI | p | p_clu |
|---|---:|---:|---:|---|---|---|---|---|---:|---:|
| `self-loop` | 112 (96) | 10 / 13 | 19 | 3/56 [0.0, 14.5] | 2/56 [0.0, 9.1] | **+0.89 pp** [-3.54, 5.88] (b=3, c=2) | [-3.98, 6.06] | [-6.70, 8.48] | 1.0000 | 1.0000 |
| `self-loop-rep` | 112 (96) | 10 / 13 | 19 | 3/56 [0.0, 14.5] | 2/56 [0.0, 9.1] | **+0.89 pp** [-3.54, 5.88] (b=3, c=2) | [-3.98, 6.06] | [-6.70, 8.48] | 1.0000 | 1.0000 |
| `cross-loop` | 112 (96) | 10 / 3 | 12 | 3/56 [0.0, 13.8] | 0/56 [0.0, 0.0] | **+2.68 pp** [0.00, 7.14] † (b=3, c=0) | [-0.73, 7.58] | [-4.46, 9.64] | 0.2500 | 0.5000 |
| `referent-loop` | 112 (96) | 25 / 10 | 35 | 11/56 [8.9, 31.7] | 2/56 [0.0, 9.1] | **+8.04 pp** [1.77, 15.26] (b=11, c=2) | [2.03, 15.27] | [-1.79, 17.41] | 0.0225 | 0.0469 |


**The kill condition fires.** `self-loop`'s net change is **+0.89 pp**, and every interval
contains zero: cluster bootstrap **[−3.54, +5.88]**, Tango **[−3.98, +6.06]**, exact
unconditional **[−6.70, +8.48]**; McNemar p = 1.0000, cluster sign-flip p = 1.0000. On this
evidence, **AI self-audit did not raise accuracy.**

`cross-loop` is also not distinguishable from zero: **+2.68 pp**, Tango **[−0.73, +7.58]**,
exact unconditional **[−4.46, +9.64]**, p = 0.2500. Its cluster-bootstrap interval reads
[0.00, 7.14], but all three of its discordant instances point the same way, so a percentile
bootstrap **cannot** produce a negative resample and that lower bound at zero is an artefact
of the method — the same pathology `CORRECTIONS.md` item 4 records, now applying to the
replacement. The unconditional intervals are the ones to read on that row.

**`referent-loop` is the only arm whose primary interval excludes zero**: **+8.04 pp,
cluster CI [1.77, 15.26]**, Tango [2.03, 15.27], p = 0.0225, cluster sign-flip p = 0.0469.
**But its exact unconditional interval, [−1.79, +17.41], contains zero**, it is a
**secondary** outcome, and it does not clear the correction threshold over the sixteen
comparisons computed. Against the arm it should be compared with — `cross-loop`, which holds
the vendor fixed and changes only the constitution — the contrast is **+5.36 pp, cluster CI
[−0.88, +12.08], p = 0.1460**, which does not exclude zero.

### What the loop's reach is

### Table 7 — paired contrasts between arms

Outcome: whether the instance passes the hidden suite after one round. Unit: the instance, paired across arms; resampled by problem. Both discordant counts shown.

| contrast | n (problems) | discordant (b / c) | difference [95% cluster CI] | Tango CI | p | p_clu | Bonferroni/16 |
|---|---:|---:|---|---|---:|---:|---:|
| self-loop minus cross-loop, hidden-test pass after one round | 112 (96) | 3 / 5 | -1.79 pp [-7.83, 4.39] | [-7.79, 3.81] | 0.7266 | 0.7812 | 0.00313 |
| referent-loop minus cross-loop, hidden-test pass after one round | 112 (96) | 9 / 3 | +5.36 pp [-0.89, 12.07] | [-0.82, 12.36] | 0.1460 | 0.1826 | 0.00313 |
| self-loop minus self-loop-rep, hidden-test pass after one round | 112 (96) | 0 / 0 | +0.00 pp [0.00, 0.00] | [-3.32, 3.32] | 1.0000 | 1.0000 | 0.00313 |

### Table 7b — what the arms flag, paired and split by stratum

The mechanism behind any net effect. On stratum P a flag is a defect caught; on stratum C it is a false alarm. Unit: the instance, paired across arms; resampled by problem.

**Every row here is EXPLORATORY**: the preregistered twelve named outcome contrasts, not flag contrasts. They are reported because the mechanism matters, and they are labelled at every occurrence.

| contrast | stratum | n (problems) | flagged by each | discordant (b / c) | difference [95% cluster CI] | p | p_clu | Bonferroni/16 |
|---|---|---:|---|---:|---|---:|---:|---:|
| `self-loop` vs `cross-loop` | P | 56 (41) | 10 vs 10 | 7 / 7 | +0.00 pp [-15.52, 16.07] | 1.0000 | 1.0000 | 0.00313 |
| `self-loop` vs `cross-loop` | C | 56 (55) | 13 vs 3 | 12 / 2 | +17.86 pp [5.45, 30.36] | 0.0129 | 0.0129 | 0.00313 |
| `referent-loop` vs `cross-loop` | P | 56 (41) | 25 vs 10 | 16 / 1 | +26.79 pp [13.56, 40.35] | 0.0003 | 0.0009 | 0.00313 |
| `referent-loop` vs `cross-loop` | C | 56 (55) | 10 vs 3 | 7 / 0 | +12.50 pp [5.17, 21.82] † | 0.0156 | 0.0156 | 0.00313 |
| `self-loop` vs `self-loop-rep` | P | 56 (41) | 10 vs 10 | 0 / 0 | +0.00 pp [0.00, 0.00] | 1.0000 | 1.0000 | 0.00313 |
| `self-loop` vs `self-loop-rep` | C | 56 (55) | 13 vs 13 | 0 / 0 | +0.00 pp [0.00, 0.00] | 1.0000 | 1.0000 | 0.00313 |


The mechanism is in the flag columns, and **every row of Table 7b is exploratory**: the
preregistration named outcome contrasts, not flag contrasts.

`referent-loop` flags **25 of 56** defective solutions where `cross-loop` flags **10** — 16
instances it catches that the shipped configuration misses against 1 the other way, **+26.8
points, cluster CI [13.6, 40.4], p = 0.0003, cluster sign-flip p = 0.0009**, the only
contrast here that clears Bonferroni over 16 (0.00313). It pays **7 additional false alarms
on correct code against 0 the other way, +12.5 points [5.2, 21.8], p = 0.0156**. That is the
trade, and it is the same trade ceiling 1 measures.

`self-loop` and `cross-loop` flag the **same number** of defects (10 of 56 each) and not the
same ones: 7 discordant instances each way. **The self-auditor was not blind; it was
noisy** — on correct code it flags 13 of 56 against `cross`'s 3, **+17.9 points [5.5, 30.4],
p = 0.0129**.

### The loop's replicate, and what it does not bound

`EXPERIMENT_RECORD.md` §9 forbids "inside the noise floor" without a replicate on the same
estimand. The replicate was run and produced something more informative than a spread:
`self-loop` and `self-loop-rep` returned **identical final solutions, flags and hidden-test
outcomes on all 112 instances**, 0 discordant pairs on both strata. (One audit *report*
differs in bytes, on `b1:HumanEval/35`, without changing its findings — so "byte-identical
output", as the first version said, was too strong.)

**That zero must not be read as "the loop is stable to 0.00 pp."** It says the `anthropic`
route at temperature 0 returns the same bytes for the same prompt within minutes. It bounds
nothing about a different day, a different route version, or a sampling route. **Run-to-run
variation of the closed loop across time remains unmeasured.**

---

## Statistical analysis

**Unit of analysis: the instance; the resampling and permutation unit: the problem.** The
loop's 112 instances come from **96 problems**; stratum P's 110 instances come from only
**56**. Where problems repeat across generation batches their instances are not independent,
so **every interval in this report is a percentile bootstrap over whole problem clusters**
(10,000 resamples, seed 20260908) and **every McNemar p is accompanied by a cluster-level
sign-flip permutation p**. Wilson intervals are still printed where they were, marked as too
narrow. K draws over the same instances are repeated measures, never K × n observations.

**The interval that was withdrawn, and why.** The first version reported a Clopper–Pearson
interval for the direction probability *conditional on the discordant pairs*, rescaled by the
*observed* discordance fraction D/n. Conditioning is legitimate for McNemar's test; it is not
legitimate for an interval on the unconditional risk difference, because D/n is itself
estimated and its uncertainty is discarded. Enumerating D ~ Binomial(112, 0.1) with every
discordance beneficial gives that construction a coverage of **0.4162688657** where 0.95 was
claimed. It is retained in `numbers.json` as `withdrawn_conditional_ci95` with that number
attached, and `tests/test_ceiling_stats.py` pins it so the method cannot return silently.

**What replaced it, with measured coverage in the same scenario:**

| method | role | measured coverage |
|---|---|---|
| conditional × observed D/n | **withdrawn** | **0.416** |
| problem-cluster percentile bootstrap | **primary** | 0.95 nominal by simulation; widens under clustering, as it must |
| Tango's unconditional score interval | check | **0.960** |
| exact unconditional, Berger–Boos restricted (γ = 10⁻⁴) | check | **0.998** (conservative by construction) |

**One caveat travels with the bootstrap.** Where every discordant pair points the same way,
a percentile bootstrap cannot generate a resample of the opposite sign, so a bound at zero
is an artefact. Rows where this fires are marked **†** and the unconditional intervals are
quoted instead.

**Union curves** are averaged over all C(K_max, K) subsets exactly, by the identity that an
instance flagged by k of K_max draws is missed by a random K-subset with probability
C(K_max − k, K)/C(K_max, K). Checked against explicit enumeration of every subset on 20
randomised cases.

**The saturation fit** is least squares on the K = 1 … K_max points, with **A constrained to
[0, 1] inside the objective**; for fixed τ the model is linear in A, so the fit reduces to a
one-dimensional search over τ. Goodness of fit and the raw union at K_max are reported beside
every asymptote, and an asymptote from a curve that has not flattened is labelled an
extrapolation everywhere it appears.

**Multiple comparisons.** Two primary outcomes, each declared singly in the preregistration
before any model call, are **not** corrected. **The preregistration planned twelve
comparisons; sixteen were computed.** The correction family is "every contrast reported with
a p value", size **16**, Bonferroni threshold **0.00313**, stated once and applied
everywhere. **Five planned comparisons — the mixed and `astra` asymptote contrasts — were not
delivered as specified** and are recorded as unmeasured (deviation 15). Every flag contrast
is **exploratory**, because the plan named outcome contrasts. The full
planned / performed / exploratory inventory is machine-readable in
`numbers.json → comparison_inventory`. Exactly one contrast clears the corrected threshold:
`referent-loop` − `cross-loop` on stratum-P flags, p = 0.0003, and it is exploratory.

**Software.** No SciPy or NumPy is used for any inferential quantity; the regularised
incomplete beta, the Clopper–Pearson inversion, the exact McNemar tail, Tango's score
interval, the exact unconditional inversion, the cluster bootstrap, the sign-flip test, the
saturation fit and the beta-binomial likelihood are implemented in `report_ceiling.py` in
the standard library. `tests/test_ceiling_stats.py` (15 tests) checks each against brute
force or against its defining property, **including coverage simulations for every interval
method**. Two real defects have been caught by that file: a swapped beta tail, and the
coverage failure above.

**Preregistration.** `benchmarks/code/ceiling/PREREGISTRATION.md` at `d96cdaf`, amendment 3
at `87939d2`, both before the first model call including the credential probe.

---

## Sensitivity: the population definition

### Table 9 — sensitivity: stratum P without the timeouts

The registered population is every hidden-suite non-pass, which **includes 7 instances whose suite did not terminate**. This table narrows it to instances with an observed assertion failure. The registered analysis is unchanged; this is a sensitivity check, and it is EXPLORATORY.

| family | union recall, registered P (n = 110) | union recall, assertion-failure P only (n = 103) [95% Wilson] |
|---|---:|---|
| `cross` (K = 8) | 33/110 (30.0%) | **32/103** (31.1%) [22.9, 40.5] |
| `self` (K = 8) | 19/110 (17.3%) | **18/103** (17.5%) [11.3, 25.9] |
| `astra` (K = 4) | 36/110 (32.7%) | **34/103** (33.0%) [24.7, 42.6] |
| **residual (never flagged)** | 57/110 (51.8%) | **54/103** (52.4%) [42.9, 61.8] |

The 3 timeouts that sit inside the residual are `b1:Mbpp/267`, `b2:Mbpp/267`, `b2:Mbpp/765`.


---

## What it cost

### Table 8 — what it cost

From the product's own usage ledgers, per call, not reconstructed. The `astra` route bills a subscription and reports only tokens, so it consumes none of the dollar budget and is quoted in tokens.

| part | model spend | astra tokens |
|---|---:|---:|
| ceiling1 | $9.5238 | 4,427,530 |
| ceiling2 | $3.7083 | — |
| **total** | **$13.2321** | 4,427,530 |


`astra` bills a subscription and reports only a token count, so it consumes none of the
dollar budget: **4,427,530 tokens over 1,040 readings**, a mean of 4,257 per audit. No
dollar equivalent is stated.

The ceiling-2 figure **includes the discarded work** — two 8-instance pilots and one full
four-arm run destroyed by the provider's circuit breaker (deviations 3 and 4). That money
was spent. Of a $20 budget, **$13.23 spent**; the ceiling-1 ladder stopped because it
exhausted its preregistered K = 8, not because it hit its $13.00 cap ($9.52 used). Per-run
UTC windows, marked with which invocation supplied the committed rows, are in
`manifest_loop.json → arm_windows_utc` and `manifest_ceiling1.json → draw_windows_utc`.

---

## Deviations from the plan, numbered, with the direction of each bias

**1. Stratum F is not extended.** New draws cover P (110) and C (150) — 260 of 290. F is a
sanity check, not an outcome. *Bias: none on either primary outcome.*

**2. The reviser is shown the solution alone, not the whole working tree.** An 8-instance
pilot found that with the visible test file in `current`, the reviser answered test-file
findings by rewriting the tests — 3 of 3 revisions returned the solution byte-identical and
a modified `tests_visible.py`. From that point `current` is the solution alone; the **audit**
increment is unchanged, so audit prompts stay byte-identical to studies 1, 2 and 7's.

*Correction and honest labelling.* The first version said non-solution files "are discarded
and counted (the count is 0 in every arm after the change)". **That is false**: the counts
are **self-loop 4, self-loop-rep 4, cross-loop 2, referent-loop 0**, and all ten touched the
test file. They were discarded, so no reported outcome used them, but they show the reviser
still reached for the test file about 9% of the time it revised. And this change is
**outcome-informed protocol adaptation on reused instances**: the configuration was altered
after observing pilot behaviour on 8 instances that are part of the 112 later analysed. It
removes a failure mode and so plausibly favours the loop, but *the direction is not
established*, and a preregistered configuration would not have needed the change.

**3. The first full run of ceiling 2 was destroyed by the provider's circuit breaker and
discarded entirely.** Failed audits: **21 of 112 `self-loop`, 93 `self-loop-rep`, 109
`cross-loop`, 107 `referent-loop`**. `loop.py` had no retry passes; it now has bounded ones,
and a failed audit is never cached. Every arm was re-run from scratch.

*Correction.* The first version said "bias: none". **That is not established.** A complete
re-run avoids selecting on which instances happened to succeed, which is the main hazard,
but neutrality also requires that the failures were unrelated to the instances' potential
outcomes. The failures were provider-side cooldowns, which is *consistent* with
independence and does not prove it. **Direction of bias: undetermined.** The discarded rows
are archived and were not used.

**4. Two 8-instance pilots of `self-loop` were run and discarded.** The first exposed
deviation 2, the second validated the fix. Spend counted.

**5. Eight `cross-loop` revisions died inside a breaker cooldown and were repaired.** A
targeted repair re-issued only those eight, reusing the cached audit report so the audit
draw is untouched; all eight then succeeded, in a separate invocation recorded in the
manifest. *Correction:* the first version said a failed revision "necessarily biases the
arm's net downward". **Too strong** — a revision that had succeeded could equally have
broken a correct solution. What is certain is that a provider-killed revision is recorded
identically to a revision that changed nothing, which is a fidelity defect regardless of
direction. **Direction: undetermined; the repair removes the ambiguity.**

**6. Cost attribution was corrected mid-study** by stamping every `run_id` with a
per-invocation timestamp. Only the discarded pilots were affected.

**7. `self` draw 2 is study 1's `self` arm, and it covered batch 1 only** — 88 of the 260
in-scope instances; the other 172 were run here. Same heterogeneity study 7 recorded as its
deviation 2. *Bias: either direction; the determinism result is corroborated on both this
across-day pair and the within-minutes replicate.*

**8. `astra` was preregistered as amendment 1 while the Codex CLI refused the model
(`0.150.1`), and enabled as amendment 2 when it was upgraded (`0.153.4`).**

**9. The first 20-instance `astra` pricing batch was discarded** because `codex exec` writes
its token line to **stderr** and the harness read stdout. Re-run inside draw 1.

**10. `astra` bypasses the product entirely** — no broker, no metered ledger, no same-vendor
gate. Prompt bytes proved identical to the shipped auditor's (40 of 40).

**11. The same-vendor bypass is inherited and used**, as in studies 1, 2 and 7. **`src/` is
not touched by this study.**

**12. Transient provider failures cost wall-clock throughout and changed no result.** Final
coverage is **260 of 260 on all 20 draws**, and every ceiling-2 arm covers all 112 instances.

**13. Two preregistered residual categories were never assigned** (`wrong-algorithm`,
`ambiguous-oracle`), because the rule's ordering absorbs disputable-oracle cases into
`unexercised-edge`. Applied as written; consequence stated at the table.

**14. The `astra` manifest's `spend_usd_cumulative` counts only broker calls.** `astra` makes
none, so its rows contribute $0.00 and 4,427,530 tokens.

**15. Five planned comparisons were not delivered as specified.** Preregistration §3.2 and
amendment 3 §5 name the `mixed` and `astra` **asymptote** contrasts (planned items 2, 3, 10,
11, 12). Table 4 reports **raw union rates at matched total draws** instead, with no fitted
contrast and no interval. **Those five comparisons are unmeasured in this study**, and the
mixed-family rows are descriptive and exploratory. Found by the cross-vendor review.

**16. The published interval method was replaced after publication.** The first committed
version of this report used a conditional-times-observed-D construction with 0.416 coverage.
It was found by the cross-vendor review, reproduced, withdrawn, and replaced. All point
estimates are unchanged. **Erroneous numbers did enter a committed artefact**: see below.

**17. Provenance was completed after the runs.** Package versions, per-invocation UTC
windows, provider base URLs, corrected sampling metadata and re-hashed analysis files were
added by `ceiling/finalise_manifests.py` from the ledgers and the installed environment. Both
manifests were originally written mid-run and recorded dirty working trees; the clean freezes
are `d96cdaf`/`87939d2` for the plan and the finalisation commit for the analysis.

### The beta-tail defect, stated exactly

The first version said a swapped Clopper–Pearson tail was "caught by my own tests" and that
"no number had left the harness". **The second half is wrong.** The swapped interval was
written into a committed artefact: `git show 1a66571:benchmarks/code/records/ceiling/tables.md`
contains the headline as `[+3.16, −1.93]`, committed at **18:46:39**, and the fix landed at
**18:48:18** — **99 seconds later**. The erroneous numbers existed in a committed results file
for that interval. They never reached the report, which was first committed at 20:55:51, after
the fix. The correct statement is: **an erroneous number entered a committed artefact for 99
seconds and was corrected before any prose quoted it.**

---

## Limitations

- **One corpus of short, self-contained Python functions is not a repository.**
- **One generator is one generator.**
- **Vendor independence is not statistical independence.**
- **The asymptote is a fitted quantity, and `cross`'s is an extrapolation from a curve that
  is still rising.** No arithmetic separates "never findable" from "findable with very small
  probability" out of eight draws. The residual classification describes what was missed by
  these readers; it establishes nothing about what is findable in principle.
- **`astra` measures a model, not the product.**
- **Round one only.** Every loop arm revises once.
- **The population is hidden-suite non-passes.** Seven of 110 P instances are timeouts. The
  sensitivity analysis moves nothing, but the label matters.
- **The corpus's own oracle is disputable in most of the residual** — 40 of 57, exploratory.
- **The loop's run-to-run variation across time is unmeasured.** The replicate measured route
  determinism, not stability.
- **Deviation 2 is outcome-informed protocol adaptation** on instances that are also in the
  analysed sample.
- **Nine studies over two tasks**, one author, one harness, overlapping assumptions.
- **The `self` arms bypass a product guarantee** the product refuses to ship.

---

## What this study licenses, and what it does not

**It licenses**: that on this corpus, a generator's own model auditing and revising its own
code produced no measurable gain in hidden-test accuracy (+0.89 pp, every interval spanning
zero); that over eight readings each, its union recall was **below** a cross-vendor
stranger's (raw −12.7 points [−25.0, −0.9]) while its false-positive rate was higher; that
repetition saturates quickly, and on a temperature-0 route almost immediately; that one
frontier reading matched eight shipped readings on recall at lower false-positive cost; and
that **51.8% of this defect population was flagged by no reading of any family**, dominated
by inputs the visible tests never construct.

**It does not license** the claim that those defects cannot be found. It shows that these
detectors, over 20 readings, did not find them.

**It does not license** "the referent works". It licenses "**the referent moved what the
auditor flagged, by more than anything else tried** (+26.8 points on stratum-P flags,
exploratory, clearing the corrected threshold), **and whether that converts into accuracy is
not established**" (+5.36 pp against `cross-loop`, p = 0.146). It licenses running that arm
again, larger, as a primary outcome.

**It does not license** replacing the shipped auditor with `astra`, nor any statement about
the mixed-family asymptotes, which were planned and not measured.

### Where this sits beside the earlier record

`CORRECTIONS.md` item 11 withdrew "the cross-vendor auditor sees more" and replaced it with
"a stranger is less tolerant", on prose, at n = 30, where self-audit recalled 31.7% against
cross's 19.8%. **On code, with model-free ground truth and eight readings each, the ordering
at eight readings is the other way round**: `self` 17.3% against `cross` 30.0%. Different
task, different ground truth, different estimand. The honest summary is that **the direction
of the self/cross recall gap is task-dependent and has now gone both ways**, while the
false-positive half has gone the same way every time: the self-auditor flags more correct
work (24.0% against 16.0% here; 13 of 56 against 3 of 56 in the loop).

Study 7 concluded that the architecture is not the lever. This study adds: **the number of
readings is not the lever either; the model is one; and the instructions moved flags more
than either — without a demonstrated effect on accuracy.**

---

## Reproduction

```sh
export PYTHONPATH="$(git rev-parse --show-toplevel)/src"
python benchmarks/code/fetch.py            # the corpus is not redistributed

# ceiling 2 — the closed loop, four arms over one frozen 112-instance sample
python benchmarks/code/loop.py --probe --run <run-dir>
python benchmarks/code/loop.py --run <run-dir> --workers 3 --budget-usd 5
python benchmarks/code/loop.py --run <run-dir> --repair-revisions

# ceiling 1 — the saturation ladder, and the astra family
python benchmarks/code/ceiling.py --plan
python benchmarks/code/ceiling.py --run <run-dir> --check-prompt   # prompt bytes, no cost
python benchmarks/code/ceiling.py --run <run-dir> --budget-usd 13 --workers 3
python benchmarks/code/ceiling.py --run <run-dir> --astra --astra-draws 4

# every number in this file, from committed records, no key and no network
python benchmarks/code/report_ceiling.py
python benchmarks/code/ceiling/finalise_manifests.py --run <run-dir>
python benchmarks/code/residual_dump.py --run <run-dir> --population all_families

# the statistics, including the coverage simulations
python -m pytest benchmarks/code/tests/test_ceiling_stats.py
```

`report_ceiling.py` regenerates every table here for $0.00. It reads the archived run
directory only for the timeout sensitivity (Table 9); without it that table says
`AUTHOR_INPUT_NEEDED` and nothing else changes. It will not reproduce byte-identically from
an empty *detector* cache: the `cross` route samples. `--no-exact-unconditional` skips the
one expensive check interval.

### What a re-run must match, and what does not matter

**Must match exactly:** the audit-set and instance digests, the three corpus revisions in
`manifest_corpus.json`, the model ids, the auditor SYSTEM prompt sha256, the constitution
sha256, the referent rule's sha256 and text, the flag rule (≥ 1 BLOCKER), the temperature
each route sends, and the seeds (20260907 sample, 20260908 bootstrap).

**Does not matter:** worker count, wall-clock, machine, ladder order, scratch path, retry
passes.

### The committed record

`benchmarks/code/records/ceiling/`: `cache/holistic__<family>__d<K>.jsonl` (detector ×
instance), `cache/*.failed.jsonl`, `loop/<arm>.jsonl` (arm × instance),
`loop/solutions-<arm>.jsonl` (**the revised solutions themselves**), `loop_sample.json`,
`residual_classification.json`, `numbers.json`, `tables.md`, `manifest_ceiling1.json`,
`manifest_loop.json`, `baseline_reproduction.json`.

The revised solutions are committed because EvalPlus is redistributable and ceiling 2's
primary outcome re-scores from them with no key and no network. **No finding prose is
committed.** Run directories are archived at
`~/Documents/Crossaudit/study-data/wt-ceiling-runs/` — **178 files**, `MANIFEST.sha256`
digest `e5ef7227567c4fc44268624c73623eaf0eae8d44d8b423aa322c335a3aa6acbc`.
