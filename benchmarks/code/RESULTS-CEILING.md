# The ceiling of AI audit — no, self-audit does not raise accuracy; the referent does

**The owner's question was: as AI-generated data grows, can AI audit itself to raise
accuracy, and where is the limit? On this evidence the answer to the first half is no.**

A generator's own model, auditing its own code and then revising it, changed the fraction
of solutions passing a hidden test suite by **+0.89 percentage points (95% exact CI
[−3.16, +3.99], exact McNemar p = 1.0000, n = 112 instances)**. It repaired 3 of 56 wrong
solutions and broke 2 of 56 correct ones. **The preregistered kill condition fired**: the
interval contains zero, and self-audit-then-revise does not raise accuracy here.

Three further results, in the order they matter.

**1. Reading the same code more times has a ceiling, and it is low.** Unioning eight
independent readings by the shipped cross-vendor auditor lifts recall on the defect
population from 10.7% to **30.0% (33 of 110 instances)**, with a fitted asymptote of
**31.5% [21.7, 45.6]** — bought by taking false positives on correct code from 4.5% to
**16.0%**. The generator's own model saturates almost immediately and far lower: 15.5% at
one reading, **17.3% (19 of 110)** at eight, asymptote **16.6% [8.1, 26.3]**, at a
false-positive rate of **24.0%**. **The preregistered primary outcome, A(self) − A(cross)
on stratum P, is −14.9 percentage points [−32.1, −2.3]** — negative, excluding zero. In
the limit of unlimited readings the author's own model sees *less* of its own bad code
than a stranger does, and flags more good code while doing it.

**2. Repetition is not the lever; the model is, and the instructions are more.** The
`self` route is effectively deterministic — a full replicate of the closed loop returned
**byte-identical output on all 112 instances**, and eight readings find one more defect
than one reading does. Meanwhile **one reading by the strongest model available
(`gpt-6-astra`, high reasoning) recalls 30.2% at 9.7% false positives, beating eight
unioned readings of the shipped auditor on both axes** (30.0% at 16.0%). And the largest
single effect in the study came from changing what the auditor was told to look for: one
added constitution rule — *find what the visible tests do not cover* — moved flags on the
defect population from 10 of 56 to 25 of 56, **+26.8 points [12.9, 30.3], 16 discordant
instances against 1, exact McNemar p = 0.0003**, the only secondary contrast in this study
that clears a Bonferroni threshold over its twelve planned comparisons.

**3. Half the defects are invisible to every reader tried.** **57 of 110 defective
solutions (51.8% [42.6, 60.9]) were flagged by no reading of any family** — 20 readings,
three models, two vendors and one frontier route. Read by hand under a rule fixed before
the first was opened, **46 of those 57 (80.7% [68.7, 88.9]) fail only on an input class
the visible test suite never constructs**: the empty list, the negative number, the
two-digit case, the ragged input, the punctuation character. **That is the shape of the
ceiling.** A model reading a specification and a test suite has no evidence that those
classes exist, and no amount of re-reading manufactures it. The one intervention that
moved recall is the one that named the gap out loud.

**Total spend: $13.23 of a $20 budget, plus 4,427,530 tokens on a subscription-billed
route that reports no dollar cost.**

Everything below is measured. Nothing is extrapolated except where it says so.

---

## What was run

Preregistered in [`ceiling/PREREGISTRATION.md`](ceiling/PREREGISTRATION.md), committed at
`d96cdaf`, with amendments 1–2 (the `astra` family) and amendment 3 (the reporting
standard and the exact-conditional interval) at `87939d2` — **all before the first model
call of this study, including the credential probe.**

| | |
|---|---|
| audit set | study 2's, unchanged: **290 instances**; this study's scope is P + C = **260** |
| stratum P | passes every visible test, **fails a hidden one** — n = 110 |
| stratum C | passes every test — the false-positive population — n = 150 |
| ground truth | a Python interpreter raising `AssertionError` or not. **No model judges anything** |
| solutions | study 2's, byte-identical, **not regenerated** |
| generator | `anthropic:claude-haiku-4-5-20251001`, frozen |
| `cross` | `openai:gpt-5.6-terra` — the shipped cross-vendor auditor, **K = 8 draws** |
| `self` | `anthropic:claude-haiku-4-5-20251001` — the generator's own model, **K = 8** |
| `astra` | `gpt-6-astra` at high reasoning, through the Codex CLI, **K = 4** |
| flag | ≥ 1 BLOCKER finding, exactly as studies 1, 2 and 7 |
| audit path | `crossaudit.auditor.run.run_audit` — the product's real audit, unchanged |
| dates (UTC) | 2026-09-05 |
| environment | Python 3.13.5, macOS 26.6.2 arm64 |

**The `astra` prompt is the shipped auditor's prompt, byte for byte.** It is built by the
product's own `auditor.prompt.build` over the product's own deterministic-check output,
and its `prompt_sha256` was checked against study 2's committed `holistic-cross` digests:
**40 of 40 instances agree.** What differs is the model and the transport. It bypasses the
provider broker, the metered ledger and the same-vendor heterogeneity guard, so **it is a
measurement of a model, not of the product path**, and is labelled that way throughout.

**Baseline check.** All 112 solutions in the ceiling-2 sample were re-executed on this
machine before any arm was scored: **112 of 112 reproduce the stratum study 2 recorded for
them** (`records/ceiling/baseline_reproduction.json`). The "before" half of every paired
outcome is therefore not a number inherited on trust.

---

## Ceiling 1 — how much a reader can ever see

### Table 1 — the saturation curve, per family

Unit of analysis: the instance. n = 110 stratum-P instances (recall) and 150 stratum-C instances (false positives), the same instances at every K. Union rate at K is averaged over all C(K_max, K) subsets of that family's draws, exactly.

| family | K_max | union recall on P at K=1 | at K_max | fitted asymptote A [95% bootstrap CI over problems] | union FP on C at K=1 | at K_max | last-step gain on P |
|---|---:|---:|---:|---|---:|---:|---:|
| `cross` | 8 | 10.7% | **30.0%** (33/110) | **31.5%** [21.7, 45.6] | 4.5% | **16.0%** | 1.93% |
| `self` | 8 | 15.5% | **17.3%** (19/110) | **16.6%** [8.1, 26.3] | 21.9% | **24.0%** | 0.23% |
| `astra` | 4 | 30.2% | **32.7%** (36/110) | **32.5%** [20.5, 44.8] | 9.7% | **10.7%** | 0.23% |

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
exchangeable draws, a per-instance detection probability constant across draws, and a
single exponential — exact only when the detectable instances are homogeneous, and
**conservative** under heterogeneity, which is the direction a ceiling claim should err.
Three things must be said at the numbers.

**`cross`'s asymptote is an extrapolation and is labelled one.** Its marginal gain from
seven to eight draws is **1.93 points**, above the preregistered 1.0-point flatness bar.
The curve has not visibly flattened, the fit's R² is 0.968 with a maximum residual of 2.37
points, and **the honest number for `cross` is the raw union at K = 8: 30.0% (33 of 110)**.
31.5% is what the model says lies beyond it.

**`self`'s and `astra`'s asymptotes are not extrapolations.** Both gain **0.23 points** on
their last step. For those two families the fitted asymptote and the raw union at K_max
agree to within a point (16.6% vs 17.3%; 32.5% vs 32.7%), and either can be quoted.
`self`'s fit has a low R² (0.476) for an uninteresting reason: the curve is nearly flat, so
there is almost no variance for the model to explain, and the residuals are small in
absolute terms (max 0.66 points).

**The preregistered secondary estimator failed in exactly the way it was predicted to.**
The zero-inflated beta-binomial returned **π = 1.000** for both `cross` and `self` — that
is, "every defect is findable eventually" — which is what an unidentifiable mixture
returns when a Beta component with a → 0 can imitate the zero-inflated mass. §1.2 said in
advance that π would be unstable upward from eight draws. It is, it is uninformative, and
it is reported here rather than quietly dropped. For `astra`, whose per-instance counts are
nearly all 0 or 4, it returns 0.332, which agrees with the other two estimators; that
agreement is a property of near-deterministic data, not evidence that the estimator works.

**Which number a reader should trust**: the raw union at K_max, always. It is model-free
and it is a strict lower bound on the ceiling. The fitted asymptote is reported beside it
because the question asked for a limit, and it is never quoted without its interval.

### Repetition is not the lever

The three families differ enormously in what a second reading buys, and the reason is
measured, not inferred.

Every pair of this study's own complete draws, over the same 260 instances, on the same
basis — the number of instances on which two draws of one family disagree about the flag:

| family | pairwise draw-to-draw disagreement (of 260 instances) | what K readings add over 1 |
|---|---|---|
| `cross` (draws 4–8, 10 pairs) | **15 to 21** — 5.8% to 8.1% | **+19.3 points** of recall, and +11.5 of false positives |
| `astra` (draws 1–4, 6 pairs) | **4 to 7** — 1.5% to 2.7% | **+2.5 points** |
| `self` (draws 3–8, 15 pairs) | **0 to 3** — 0.0% to 1.2% | **+1.8 points** |

Corroborated outside this study's own draws: `self` disagrees with study 1's `self` arm on
**1 of 106** shared instances, across a day and a commit; and the `self-loop` /
`self-loop-rep` replicate in ceiling 2 returned **byte-identical output on all 112
instances**.

`self` runs on a model whose capability card permits `temperature`, so the provider layer
sends `temperature = 0`; `cross` runs on a reasoning model whose card carries
`temperature: False`, so no sampling parameter is sent and the route varies run to run
(D154). **The union-of-K story is therefore almost entirely a story about one route's
sampling noise.** For the two near-deterministic routes, "read it eight times" is close to
a no-op, and their ceiling is their single-draw recall.

This has a direct consequence for the product: **buying recall by re-reading only works
where the route is stochastic, and it is the most expensive way to buy it.** Eight `cross`
readings cost eight calls to reach 30.0% at 16.0% false positives. One `astra` reading
reaches 30.2% at 9.7%.

### Mixing families does raise the ceiling, and it is not free

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


Read across the matched-total rows: at 8 total readings, `cross+astra` (4 each) reaches
**36.8% recall at 14.7% false positives**, against `cross` alone at 8 readings on **30.0%
at 16.0%** — more recall for fewer false alarms, the only place in this study where both
axes improve at once. Adding `self` to the mix does the opposite: every combination
containing `self` carries a false-positive rate near or above 28%, because `self`'s own
false-positive rate is 24.0% and a union inherits every member's false alarms.

**Diversity across model strength pays. Diversity across vendors at equal strength does
not pay enough to cover what it costs on correct code.** That is study 7's conclusion
reproduced with a stronger model in the mix, and it is the same curve.

---

## The residual — the shape of the ceiling

### Table 5 — the residual: stratum-P defects no draw ever flagged

| population | families | total draws | n P instances | never flagged | share [95% Wilson] |
|---|---|---:|---:|---:|---|
| broker_families_only | cross, self | 16 | 110 | **68** | 61.8% [52.5, 70.4] |
| all_families | cross, self, astra | 20 | 110 | **57** | 51.8% [42.6, 60.9] |

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


**This is the most important table in the study.** Under a rule fixed in the
preregistration before the first residual instance was opened, and applied by taking the
first category that fits:

- **`unexercised-edge` — 46 of 57 (80.7% [68.7, 88.9])**, over 27 distinct problems. The
  candidate is correct on every input class the visible suite constructs and fails only on
  a class the suite never constructs: the empty list (`Mbpp/305`, `Mbpp/559`), a
  zero-length string (`Mbpp/113`, `Mbpp/771`), a negative number (`Mbpp/99`, `Mbpp/244`),
  ragged inputs (`Mbpp/142`, `Mbpp/391`), floats where the oracle counts only integers
  (`Mbpp/294`, `Mbpp/410`), punctuation (`Mbpp/7`, `Mbpp/459`), a two-digit number
  (`Mbpp/92`).
- **`spec-misreading` — 8 of 57 (14.0% [7.3, 25.3])**, over 5 problems: the candidate
  computes a self-consistent but different function from the one the prose states, and the
  visible tests do not separate the two readings. `Mbpp/576` reads "sublist" as contiguous
  where the oracle means subsequence; `Mbpp/594` takes an absolute difference where the
  oracle means a signed one; `Mbpp/74` requires a bijection where the oracle checks one
  direction.
- **`timeout` — 3 of 57 (5.3% [1.8, 14.4])**: the hidden suite did not terminate, so no
  assertion evidence exists at all. `CORRECTIONS.md` item 4 already records that timeouts
  in this corpus are not observed assertion failures and sit uneasily inside the stated
  ground truth; they are named here rather than counted as defects an auditor missed.
- **`wrong-algorithm` — 0. `ambiguous-oracle` — 0.**

**Two of the six preregistered categories were never used, and the reason is a defect in
the rule, not a fact about the world.** The ordering puts `unexercised-edge` second and
`ambiguous-oracle` fifth, so any instance whose oracle is arguable *and* whose failure is
confined to an unexercised input class lands in `unexercised-edge`. That is most of them.
The rule was applied exactly as written; the consequence is recorded here so a reader is
not misled into thinking every EvalPlus expectation was found defensible.

**Exploratory, and labelled exploratory: in 40 of the 57 residual instances a competent
reader could defend the candidate against the specification's prose as written.**
`Mbpp/459` asks to "remove uppercase substrings" and the oracle also strips punctuation.
`Mbpp/113` asks whether a string represents an integer and the oracle answers `None` for
the empty string. `Mbpp/103` returns 0 for the Eulerian number A(0,0), which is
conventionally 1. This flag is not part of the preregistered rule; it was added after the
categories were assigned, it is a judgement of the author's, and it should be read as a
description of the corpus rather than as a measurement.

**What the frontier model adds, and what that says about the ceiling.** Eleven instances
sit in the broker-only residual but not the all-family residual — `astra` found them and
16 readings by two broker models did not. **Six of those eleven are crashes** — `IndexError`
on an empty array, `ValueError` from `math.sqrt` on a negative, `TypeError` from a complex
square root, a `ValueError` unpacking an over-long tuple. The strongest model is
disproportionately better at the most mechanically checkable defect there is: *this input
makes the program raise*. It is not disproportionately better at the rest.

**The sentence this study exists to produce.** The defects that survive every reader are
not subtle reasoning failures. They are ordinary defects on inputs nobody wrote a test
for. **A model that reads a specification and a test suite cannot see the input classes
the test suite omits, because nothing in what it is shown says they exist** — and reading
it eight more times, or with a stronger model, does not create that evidence. It has to be
supplied. The one intervention in this study that supplied it — a rule telling the auditor
to look for what the visible tests do not cover — is also the one that moved recall.

---

## Ceiling 2 — whether the loop raises accuracy

The loop is `frozen solution → run_audit → (if BLOCKED) the product's own revision →
hidden suite`, over a frozen, paired 112-instance sample (56 P, 56 C, seed 20260907).
Generation is not repeated, so no difference between arms can be generation variance. The
revision prompt is the product's own `generator.build_prompt(...)` with
`render_findings(outcome.report)`, called as `cli/build.py` calls it on a repair round.

**The primary outcome is unconditional on whether a revision occurred.** That is not a
detail: `CORRECTIONS.md` item 9 is this project's largest retraction, and it is exactly
the error of conditioning the outcome on a consequence of the treatment.

### Table 6 — ceiling 2: the closed loop, per arm

Unit of analysis: the instance, paired before/after on the same instance. Net is unconditional on whether a revision occurred. Interval and p: exact-conditional (Clopper–Pearson on the discordant pairs) and exact McNemar.

| arm | n | audits BLOCKED (P / C) | revisions that changed the file | fixed on P | broken on C | **net change in hidden-test pass rate** [95% exact CI] | exact p |
|---|---:|---:|---:|---|---|---|---:|
| `self-loop` | 112 | 10 / 13 | 19 | 3/56 [1.8, 14.6] | 2/56 [1.0, 12.1] | **+0.89 pp** [-3.16, 3.99] (b=3, c=2) | 1.0000 |
| `self-loop-rep` | 112 | 10 / 13 | 19 | 3/56 [1.8, 14.6] | 2/56 [1.0, 12.1] | **+0.89 pp** [-3.16, 3.99] (b=3, c=2) | 1.0000 |
| `cross-loop` | 112 | 10 / 3 | 12 | 3/56 [1.8, 14.6] | 0/56 [0.0, 6.4] | **+2.68 pp** [-1.11, 2.68] (b=3, c=0) | 0.2500 |
| `referent-loop` | 112 | 25 / 10 | 35 | 11/56 [11.3, 31.8] | 2/56 [1.0, 12.1] | **+8.04 pp** [1.06, 11.16] (b=11, c=2) | 0.0225 |


**The kill condition fired.** `self-loop`'s net change is **+0.89 pp, 95% exact CI
[−3.16, +3.99], exact McNemar p = 1.0000, on 5 discordant instances (3 fixed, 2 broken)**.
The interval contains zero. On this evidence, **AI self-audit does not raise accuracy.**

`cross-loop` is also not distinguishable from zero: **+2.68 pp [−1.11, +2.68], p = 0.2500,
3 fixed and 0 broken.** Its point estimate is better and it broke nothing, but three
instances is three instances, and the interval says so.

**`referent-loop` is the one arm that moves.** **+8.04 pp [+1.06, +11.16], exact McNemar
p = 0.0225, 11 fixed and 2 broken.** It is the only arm whose interval excludes zero. It
does not clear the Bonferroni threshold over this study's twelve planned comparisons
(0.00417), and it is a **secondary** outcome; both facts are stated here rather than in a
footnote.

### What the loop's reach is, and why the ceiling binds it

### Table 7 — paired contrasts between arms

Outcome: whether the instance passes the hidden suite after one round. Unit: the instance, paired across arms. Exact McNemar on the discordant pairs; both discordant counts shown.

| contrast | n instances | discordant (b / c) | difference [95% exact CI] | exact p | Bonferroni/12 threshold |
|---|---:|---:|---|---:|---:|
| self-loop minus cross-loop, hidden-test pass after one round | 112 | 3 / 5 | -1.79 pp [-5.93, 3.64] | 0.7266 | 0.00417 |
| referent-loop minus cross-loop, hidden-test pass after one round | 112 | 9 / 3 | +5.36 pp [-1.54, 9.54] | 0.1460 | 0.00417 |
| self-loop minus self-loop-rep, hidden-test pass after one round | 112 | 0 / 0 | +0.00 pp — | 1.0000 | 0.00417 |

### Table 7b — what the arms flag, paired and split by stratum

The mechanism behind any net effect. On stratum P a flag is a defect caught; on stratum C it is a false alarm. Unit: the instance, paired across arms; exact McNemar on the discordant pairs.

| contrast | stratum | n | flagged by each | discordant (b / c) | difference [95% exact CI] | exact p |
|---|---|---:|---|---:|---|---:|
| `self-loop` vs `cross-loop` | P | 56 | 10 vs 10 | 7 / 7 | +0.00 pp [-13.48, 13.48] | 1.0000 |
| `self-loop` vs `cross-loop` | C | 56 | 13 vs 3 | 12 / 2 | +17.86 pp [3.59, 24.11] | 0.0129 |
| `referent-loop` vs `cross-loop` | P | 56 | 25 vs 10 | 16 / 1 | +26.79 pp [12.94, 30.27] | 0.0003 |
| `referent-loop` vs `cross-loop` | C | 56 | 10 vs 3 | 7 / 0 | +12.50 pp [2.26, 12.50] | 0.0156 |
| `self-loop` vs `self-loop-rep` | P | 56 | 10 vs 10 | 0 / 0 | +0.00 pp — | 1.0000 |
| `self-loop` vs `self-loop-rep` | C | 56 | 13 vs 13 | 0 / 0 | +0.00 pp — | 1.0000 |


The mechanism is visible in the flag columns. `referent-loop` flags **25 of 56** defective
solutions where `cross-loop` flags **10** — 16 instances it catches that the shipped
configuration misses, against 1 in the other direction, **+26.8 points [12.9, 30.3],
p = 0.0003**. It pays **7 additional false alarms on correct code, 0 in the other
direction, +12.5 points [2.3, 12.5], p = 0.0156**. That is the whole trade, and it is the
same trade ceiling 1 measures: recall and false positives move together, and the referent
moves recall faster than it moves false positives — the only lever in this programme's
history that does.

`self-loop` and `cross-loop` flag the **same number** of defects (10 of 56 each) but not
the same ones: 7 discordant instances in each direction. **The self-auditor and the
stranger see equally much and see different things.** Where they differ sharply is on
correct code, where `self` flags 13 of 56 against `cross`'s 3 — **+17.9 points
[3.6, 24.1], p = 0.0129.** A self-audit is not blind. It is noisy.

### The loop's noise floor, and what it does not bound

`EXPERIMENT_RECORD.md` §9 forbids the phrase "inside the noise floor" without a replicate
on the same estimand. The replicate was run, and it produced something more informative
than a spread: **`self-loop` and `self-loop-rep` are byte-identical on all 112 instances**
— the same flags, the same revised solutions, the same hidden-test outcomes, 0 discordant
pairs on both strata. The measured spread is **0.00 pp**.

**That number must not be read as "the loop is stable to 0.00 pp."** It says the
`anthropic` route at `temperature = 0` returns the same bytes for the same prompt within
minutes. It bounds nothing about a different day, a different route version, or a route
that samples. **Run-to-run variation of the closed loop across time remains unmeasured**,
and no sentence in this report claims otherwise. The 6.4-point single-draw detection floor
from study 7 is a different estimand and is not quoted against any loop result here.

---

## Statistical analysis

**Unit of analysis: the instance** — one `(batch, problem_id)` solution. K draws over the
same instances are repeated measures on those instances, never K × n independent
observations; no `n` in this report means a row, a draw or a detector-instance. Every
bootstrap resamples **problem clusters**: 68 of the 222 distinct problems contribute two
instances each and move together.

**Union curves** are averaged over all C(K_max, K) subsets exactly, by the identity that an
instance flagged by k of K_max draws is missed by a random K-subset with probability
C(K_max − k, K)/C(K_max, K). No Monte Carlo. Checked against explicit enumeration of every
subset on 20 randomised cases (`tests/test_ceiling_stats.py`).

**The saturation fit** is least squares on the K = 1 … K_max points; for fixed τ the model
is linear in A, so the fit reduces to a one-dimensional search over τ with no starting
point and no optimiser that can fail. Goodness of fit (R², maximum residual) and the raw
union at K_max are reported beside every asymptote.

**Tests.** Paired binary outcomes — flagged/not flagged, passes/fails after revision — use
**exact McNemar**, a two-sided binomial sign test on the discordant pairs, because the
pairs are the same instances under two conditions and the discordant counts are too small
for the asymptotic χ². Both discordant counts are printed wherever a difference is. The
interval for a paired difference is **exact-conditional**: conditioning on the n_d
discordant pairs, b ~ Binomial(n_d, π), and a Clopper–Pearson interval for π maps
monotonically to an interval for δ = (b − c)/n. This replaces the percentile bootstrap for
these contrasts, because a bootstrap over discordances that all point one way cannot
produce a resample of the other sign and returns a one-signed interval that does not
establish exclusion of zero — a defect this project has already published and withdrawn
(`CORRECTIONS.md` item 4). Single proportions carry 95% Wilson intervals. The difference of
fitted asymptotes keeps a **95% percentile bootstrap over problem clusters** (10,000
resamples, seed 20260908), both families resampled together so the difference stays paired.

**Multiple comparisons.** Two primary outcomes, one per ceiling, each declared singly in
the preregistration before any model call, neither corrected. **Twelve planned comparisons
in total**; every secondary contrast carries its unadjusted exact p with the
Bonferroni-over-twelve threshold **p = 0.00417** beside it. Exactly one secondary contrast
clears it: `referent-loop` − `cross-loop` on stratum-P flags, p = 0.0003. This project has
now run eight studies over two tasks, and that history is part of the multiple-comparison
picture; no per-study correction undoes it.

**Exclusions.** Listed in full under *Deviations*, with the direction of each possible
bias. No instance was excluded on the basis of its outcome.

**Software.** No SciPy, NumPy or statistics package is used for any inferential quantity.
The regularised incomplete beta, the Clopper–Pearson inversion, the exact McNemar tail, the
saturation fit and the beta-binomial likelihood are implemented in `report_ceiling.py` in
the standard library, and `tests/test_ceiling_stats.py` checks each against brute force or
against its defining property — the Clopper–Pearson bounds against the binomial tails they
invert, summed from the pmf with no shared code. **That test caught a real defect in this
study**: the first implementation inverted the wrong beta tail and returned every paired
interval with its bounds swapped and one bound of the wrong sign. No number had left the
harness.

**Preregistration.** `benchmarks/code/ceiling/PREREGISTRATION.md` at `d96cdaf`, amendment 3
at `87939d2`, both before the first model call including the credential probe.

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
dollar budget and no dollar figure for it is mixed into the ledger totals. **4,427,530
tokens** over 1,040 readings, a mean of 4,257 tokens per audit. Any dollar equivalent a
reader wants would be reconstructed at published rates and is deliberately not stated here.

The ceiling-2 figure **includes the discarded work**: two 8-instance pilots and one full
four-arm run destroyed by the provider's circuit breaker (deviations 3 and 4). That money
was spent, and a study that reports only the spend of the runs it kept is under-reporting
its cost. Of a $20 budget, **$13.23 spent**; the ceiling-1 ladder stopped because it
exhausted its preregistered K = 8, not because it hit its $13.00 cap ($9.52 used).

---

## Deviations from the plan, numbered, with the direction of each bias

Every departure, including the boring ones. A study that reports no deviations is a study
that was not watched closely enough.

**1. Stratum F is not extended.** New draws cover P (110) and C (150) — 260 of 290. F is a
sanity check, not an outcome of either ceiling. The pre-existing draws still cover it.
*Bias: none on either primary outcome.*

**2. The reviser is shown the solution alone, not the whole working tree.** An 8-instance
pilot found that with the visible test file in `current`, the reviser answered test-file
findings by **rewriting the tests** — 3 of 3 revisions returned the solution byte-identical
and a modified `tests_visible.py`. Scoring a solution against a suite its own author just
rewrote measures nothing, and editing the contract is the "make a check disappear" move the
product's generator system prompt forbids. From that point `current` is
`work/solution/solution.py` alone; **the audit increment is unchanged**, so the audit prompt
stays byte-identical to studies 1, 2 and 7's. Non-solution files returned are discarded and
counted (`returned_non_solution`; the count is 0 in every arm after the change). The
pilot's 8 rows were discarded, not merged. *Bias: this makes the loop look better than the
alternative configuration, by removing a failure mode.*

**3. The first full run of ceiling 2 was destroyed by the provider's circuit breaker and
was discarded entirely.** The provider layer opens a breaker after three consecutive route
failures and cools down for 60 s, during which every queued instance fails immediately —
study 7 recorded the same failure as its deviation 3. In that run 21 of 112 `self-loop`
audits, 93 of 112 `self-loop-rep`, 109 of 112 `cross-loop` and 107 of 112 `referent-loop`
failed with `ProviderDenial: … cooling down`. `loop.py` had no retry passes; it now has
bounded ones, and **a failed audit is never cached** — it is still missing and a later pass
retries it. Every arm was re-run from scratch; the discarded rows are archived outside the
repository under `discarded-breaker-run/`. *Bias: none on the reported numbers, which come
only from the re-run. The spend is counted.*

**4. Two 8-instance pilots of `self-loop` were run and discarded** — the first exposed
deviation 2, the second validated the fix. Neither contributes a row. Archived under
`pilot-discarded/`; spend counted.

**5. Eight `cross-loop` revisions died inside a breaker cooldown and were repaired.** A
revision killed by the provider is indistinguishable in the record from a revision that
decided to change nothing, which biases the arm's net **downward**. A targeted repair mode
re-issued only those eight, reusing the cached audit report so the audit draw is untouched;
all eight then succeeded. `revise_one` now carries bounded retries. Every arm's final
`revise_ok` is `True` or `None` (not blocked); no failed revision survives in any reported
number. *Bias: without the repair, `cross-loop` would have been understated.*

**6. Cost attribution was corrected mid-study** by stamping every `run_id` with a
per-invocation timestamp; the ledger is read back on `run_id`, and a re-run would otherwise
have inherited the earlier call's cost. Only the discarded pilots were affected. Per-row
costs are the ledger's figure for that call alone; the study total is the ledger's own sum
and therefore includes discarded work.

**7. `self` draw 2 is study 1's `self` arm, and it covered batch 1 only** — 88 of the 260
in-scope instances came from that arm (2026-09-04, at study 1's commit); the other 172 were
run here. This is the heterogeneity study 7 recorded as its deviation 2 for `cross` draws 2
and 3, admitted on the same grounds: no deterministic layer on any row, byte-identical
batch-1 solutions. *Bias: either direction. The determinism result is measured on both this
across-day pair (1 disagreement in 106) and the within-minutes loop replicate (0 in 112),
and they agree.*

**8. `astra` was preregistered as amendment 1 while the installed Codex CLI refused the
model (`0.150.1`), and enabled as amendment 2 when it was upgraded (`0.153.4`).** Amendment
1 was written and committed before any `astra` call; the family ran under it unchanged.

**9. The first 20-instance `astra` pricing batch was discarded** because its token counts
were not captured: `codex exec` writes its banner and token line to **stderr**, and the
harness was reading stdout. The readings themselves were correct — stdout carries the JSON
reply and nothing else, which is why the prompt-byte check passed — but a reading with no
cost record is not a record this study will publish. Deleted and re-run inside draw 1.
*Bias: none.*

**10. `astra` bypasses the product entirely**, and every number from it is labelled a
measurement of a model rather than of the product path. No broker, no metered ledger, no
same-vendor gate. Its prompt bytes were proved identical to the shipped auditor's (40 of 40).

**11. The same-vendor bypass is inherited and used**, as in studies 1, 2 and 7: the `self`
family and both `self-loop` arms leave `generator:` unset so the product's same-vendor gate
has nothing to compare against. That is a deliberate bypass of a product guarantee, for
measurement only, confined to the harness. **`src/` is not touched by this study.**

**12. Transient provider failures cost wall-clock throughout and changed no result.** Both
routes threw intermittent SSL and "provider unreachable" errors that opened the breaker and
cost whole passes; every affected instance was retried and landed. Final coverage is
**260 of 260 on all 20 draws**, and every arm of ceiling 2 covers all 112 instances. The
`.failed.jsonl` files record every refused reading with its reason.

**13. Two preregistered residual categories were never assigned** (`wrong-algorithm`,
`ambiguous-oracle`), because the rule's ordering places `unexercised-edge` ahead of
`ambiguous-oracle` and absorbs the disputable-oracle cases. The rule was applied as
written; the consequence is stated at the table and an exploratory second flag records how
many residual instances have a disputable oracle (40 of 57).

**14. The astra manifest's `spend_usd_cumulative` counts only broker calls.** `astra` makes
none, so its rows contribute $0.00 and 4,427,530 tokens. This is correct, not a gap, and is
noted because a reader comparing `spend_usd_cumulative` to the number of readings would
otherwise think readings were lost.

---

## Limitations, stated by the author

- **One corpus of short, self-contained Python functions is not a repository.** Every number
  here is about HumanEval+/MBPP+ solutions of a few dozen lines with one entry point.
- **One generator is one generator.** A ceiling for `claude-haiku-4-5`'s defects is not a
  ceiling for generated code.
- **Vendor independence is not statistical independence.** Cross-vendor reduces correlated
  error; it does not create an independent oracle.
- **The asymptote is a fitted quantity, and no arithmetic separates "never findable" from
  "findable with very small probability" out of eight draws.** That is why the residual is
  read by hand, and why the hand reading — not the fit — carries the claim about what the
  ceiling is made of.
- **`astra` measures a model, not the product.** The comparison of models is fair; it is
  not a statement about what CrossAudit does today.
- **Round one only.** Every loop arm revises once. A loop that revises until the auditor
  passes it would have a different profile and this study says nothing about it.
- **The corpus's own oracle is disputable in most of the residual.** 40 of 57 residual
  instances have an expectation a competent reader could argue with (exploratory). A
  "defect an auditor missed" is, in those cases, partly a disagreement about the
  specification. This weakens any reading of the residual as pure auditor failure, and it
  strengthens the operational point: what the auditor lacks is the *referent*.
- **The loop's run-to-run variation across time is unmeasured.** The replicate returned
  byte-identical output, which measures route determinism, not stability.
- **Eight studies over two tasks.** One author, one harness, overlapping assumptions.
  Per-study preregistration does not undo that.
- **The `self` arms bypass a product guarantee.** CrossAudit refuses a same-vendor pair;
  the study needs it as a control. Every `self` number is a number about a configuration
  the product will not ship.

---

## What this study licenses, and what it does not

**It licenses**: that on this corpus, a generator's own model auditing and revising its own
code produced no measurable gain in hidden-test accuracy (+0.89 pp, CI [−3.16, +3.99]);
that its detection ceiling under unlimited re-reading is **below** a cross-vendor
stranger's (−14.9 points, CI [−32.1, −2.3]) while its false-positive rate is higher; that
re-reading saturates quickly and, on a deterministic route, almost immediately; that one
reading by a frontier model beats eight by the shipped auditor on both recall and false
positives; and that **about half of this defect population is invisible to every reader
tried**, dominated by inputs the visible tests never construct.

**It does not license** the claim that no audit can find those defects. It shows that
*models reading the specification and the visible tests* do not, over 20 readings and three
models. The one manipulation that changed the referent moved recall by 26.8 points, which
is direct evidence that the limit measured here is a limit of **what the auditor is shown
and told**, not a limit of what a model can reason about.

**It does not license** shipping `referent-loop` on the strength of +8.04 pp. That is a
secondary outcome on 13 discordant instances that does not clear this study's own
multiple-comparison threshold, and it costs 7 additional false alarms on 56 correct
solutions. It licenses running that arm again, larger, as a primary outcome.

**It does not license** replacing the shipped auditor with `astra`. The comparison bypasses
the broker and the heterogeneity guard, it is one model on one corpus, and this study
measured no cost for it in dollars.

### Where this sits beside the earlier record

`CORRECTIONS.md` item 11 withdrew "the cross-vendor auditor sees more" and replaced it with
"a stranger is less tolerant", on prose, at n = 30, where the self-audit recalled 31.7%
against cross's 19.8%. **On code, with model-free ground truth and eight draws each, the
ordering is the other way round at the ceiling**: `self` 17.3% raw / 16.6% fitted against
`cross` 30.0% raw / 31.5% fitted. The two results are not in contradiction — different
task, different ground truth, different estimand (single-draw recall against an asymptote)
— and the honest summary is that **the direction of the self/cross recall gap is
task-dependent and has now gone both ways**, while the false-positive half has gone the
same way every time: the self-auditor flags more correct work (24.0% against 16.0% here,
and 13 of 56 against 3 of 56 in the loop).

Study 7 concluded that the architecture is not the lever. This study adds: **the number of
readings is not the lever either, and the model is a lever but a smaller one than the
referent.**

---

## Reproduction

```sh
export PYTHONPATH="$(git rev-parse --show-toplevel)/src"
# credentials: CROSSAUDIT_ANTHROPIC_KEY and CROSSAUDIT_OPENAI_KEY (or the role fallbacks
# CROSSAUDIT_AUDITOR_KEY / CROSSAUDIT_GENERATOR_KEY, which the harness mirrors onto the
# vendor variables). The corpus is not redistributed:
python benchmarks/code/fetch.py

# ceiling 2 — the closed loop, four arms over one frozen 112-instance sample
python benchmarks/code/loop.py --probe --run <run-dir>
python benchmarks/code/loop.py --run <run-dir> --workers 3 --budget-usd 5
python benchmarks/code/loop.py --run <run-dir> --repair-revisions

# ceiling 1 — the saturation ladder, and the astra family
python benchmarks/code/ceiling.py --plan
python benchmarks/code/ceiling.py --run <run-dir> --check-prompt   # prompt bytes, no cost
python benchmarks/code/ceiling.py --run <run-dir> --budget-usd 13 --workers 3
python benchmarks/code/ceiling.py --run <run-dir> --astra --astra-draws 4

# every number in this file, from committed records, with no key and no network
python benchmarks/code/report_ceiling.py
python benchmarks/code/residual_dump.py --run <run-dir> --population all_families
```

Both loops are resumable and idempotent: a detector or an arm with a cached record is never
re-run. **Running `report_ceiling.py` now, against the committed records, costs $0.00 and
regenerates every table in this file**, plus `records/ceiling/numbers.json` and
`records/ceiling/tables.md`, from which the tables above are copied verbatim.

It will **not** reproduce byte-identically from an empty cache: the `cross` route sends no
temperature and varies run to run — the section "Repetition is not the lever" quantifies
exactly how much — while `self` and `astra` are, on this evidence, near-deterministic.

### What a re-run must match, and what does not matter

Recorded in `records/ceiling/manifest_ceiling1.json` and `manifest_loop.json`.

**Must match exactly:** the audit-set digest (`records/study2/audit_set.json`), the instance
digest (`records/study2/instances.jsonl`), the three corpus revisions pinned in
`manifest_corpus.json`, the model ids, the auditor SYSTEM prompt sha256 (its full text is in
the manifest — it is corpus-free), the constitution sha256, the referent rule's sha256 and
text, the flag rule (≥ 1 BLOCKER), and the two seeds (20260907 for the loop sample, 20260908
for the bootstrap).

**Does not matter:** the worker count, wall-clock time, the machine and OS, the order the
ladder ran in, the scratch directory path, and how many retry passes a run needed to get
around the provider's circuit breaker.

### The committed record

`benchmarks/code/records/ceiling/`:

| file | one row per |
|---|---|
| `cache/holistic__<family>__d<K>.jsonl` | detector × instance — flag, rules cited, finding digests, cost or tokens |
| `cache/*.failed.jsonl` | a reading the provider refused, with the reason |
| `loop/<arm>.jsonl` | arm × instance — audit, verdict, revision, before/after hidden outcome |
| `loop/solutions-<arm>.jsonl` | arm × instance — **the revised solution itself** |
| `loop_sample.json` | the frozen 112-instance sample and its seed |
| `residual_classification.json` | the hand classification: category, input class, exploratory flag |
| `numbers.json`, `tables.md` | every computed quantity; the rendered tables |
| `manifest_ceiling1.json`, `manifest_loop.json` | provenance, prompts, environment, spend |
| `baseline_reproduction.json` | the model-free re-execution check of the frozen baseline |

The revised solutions are committed because EvalPlus is redistributable and because
ceiling 2's primary outcome re-scores from them with no key and no network. **No finding
prose is committed** — it quotes the corpus — and no prompt embedding corpus text is. The
run directories, which do contain audit reports and solution bytes, are archived outside the
repository at `~/Documents/Crossaudit/study-data/wt-ceiling-runs/` — **178 files**, with a
per-file manifest at `MANIFEST.sha256` whose own sha256 is
`e5ef7227567c4fc44268624c73623eaf0eae8d44d8b423aa322c335a3aa6acbc`.
