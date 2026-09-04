# Preregistration — is the *structure* of the audit the lever, rather than the model?

Written and committed **before any model call this study reports**. The only calls that
preceded it were two one-word provider probes (`"Say READY."`, $0.00015 total, recorded in
Deviations) placed to prove both credentials resolve before any budget was committed.

Study 1 (`RESULTS.md`) measured the shipped architecture in code and found recall 8.9% on
the population that matters. Studies 1–3 on prose found 2.0% shipped, 3.8% when the
auditor *model* was swapped (inside a 2.6pp noise floor), and 23.5% when the *rules* were
rewritten. The model is not the lever. This study asks whether the **structure of the
audit** is.

## The internal observation this study is built on

On the same task, over the same outputs, CrossAudit's CLEAR scorer — a similar class of
model — identified **201** wrong rubric items where the shipped **holistic** auditor named
**4**. CLEAR is not a better model. It is a different *structure*: it extracts and compares
**per rubric item**, one item at a time, instead of reading everything and reporting what
stands out.

## Hypothesis, in a form that can come out false

**H1.** Holistic review has a low recall ceiling that is a property of the *architecture*,
not the model. Decomposing the audit into per-property checks and aggregating them will
raise recall on the "looks right, is wrong" population by a materially larger margin than
swapping the auditor model did.

**H1 is false if** `decomposed-cross` recall on stratum P does not exceed `holistic-cross`
recall on the same instances by more than this study's own measured noise floor.

**H0 (the null this study is built to be able to report).** Audit structure does not matter:
`decomposed-cross` recall on P ≤ `holistic-cross` recall on P.

**If H0 survives, that sentence is the first sentence of `RESULTS-2.md`, and the study is
not re-run until it flips.**

A second way H1 can fail that is *not* H0: decomposition may raise recall while raising the
false-positive rate on correct code so far that the architecture is unusable. That outcome
is a refutation of the *product* claim even though it confirms the recall mechanism, and it
is reported as such. This is why the false-positive rate is named beside the primary
outcome and not in a footnote.

## Why this harness — the methodological point

**Ground truth is a Python interpreter, not a model.** EvalPlus base tests are the
"visible" layer a developer can run; the plus-tests are hidden ground truth; the population
that matters is solutions that **pass the visible tests and fail the hidden ones** —
"looks right, is wrong". No number in this study passes through an LLM judge. Studies 1–3
cannot say that: every number in them rests on CLEAR, a reimplementation of a paper whose
authors released no evaluation code and whose ground truth is itself model-produced.

## The population

Assigned by execution alone, no model involved (unchanged from study 1):

| stratum | definition |
|---|---|
| **P** | passes **every** visible test **and** fails **at least one** hidden test — "looks right, is wrong" |
| **C** | passes every visible test and every hidden test — correct |
| **F** | fails at least one visible test |

## Primary outcome — one number, named in advance

**`decomposed-cross` recall on P minus `holistic-cross` recall on P**, paired on identical
instances. Recall = the fraction of stratum-P instances the arm flags, where "flags" means
at least one BLOCKER-severity finding. ADVISORY never gates in the product and does not
count, exactly as in study 1.

Reported with McNemar exact p, a seeded paired-bootstrap 95% interval on the difference,
and the n of the cell.

## Secondary outcomes, all named in advance

1. **False-positive rate**: fraction of stratum-C (correct) solutions each arm flags.
   `decomposed-cross` − `holistic-cross` on C, paired, same statistics. **Reported beside
   the primary outcome, not below it.**
2. **Precision**: of the instances an arm flags, the fraction that fail any test. Raw on the
   audit set and reweighted to the corpus by the known stratum sampling fractions.
3. **`two-stage` − `holistic-cross`**, on both recall and false positives.
4. **Cost per true finding**, in dollars: arm spend ÷ true-positive count.
5. **Wall time per instance**, per arm.
6. **Noise floor**: `holistic-cross` re-run against study 1's `cross` arm over the identical
   batch-1 instances. A difference smaller than this spread is not a finding.

## Arms — the architecture is the independent variable

Every arm judges **byte-identical** solutions on the same instances. Nothing is regenerated
per arm. The single manipulated variable is the *structure* of the audit.

| arm | structure | auditor model |
|---|---|---|
| `checks` | deterministic layer only (visible tests) — the floor | none |
| `holistic-cross` | shipped: one auditor reads code + rules, returns findings | `openai:gpt-5.6-terra` |
| `holistic-self` | identical structure, the generator's own model | `anthropic:claude-haiku-4-5` |
| `decomposed-cross` | enumerate checkable properties from the spec, check **each separately**, aggregate | `openai:gpt-5.6-terra` |
| `two-stage` | `holistic-self` proposes, `holistic-cross` filters | both |
| `decomposed+two-stage` | run **only if budget allows** after the others | both |

`holistic-cross` and `decomposed-cross` both run **without** the deterministic layer, so the
primary comparison isolates model-audit architecture alone. On stratum P this changes
nothing by construction — those solutions pass the visible suite, so the deterministic layer
is silent there (study 1 measured `checks` recall on P at exactly 0/56). `checks` is
reported separately as the floor.

Held fixed across every model arm: the constitution (shipped `GENERAL_AUDIT_RULES.md`,
unmodified), `max_rounds: 1`, the increment the audit sees (solution + visible test source),
the audit set, and the solutions.

### `two-stage`, defined precisely before it is run

Two numbers, both preregistered:

- **`two-stage-union`**: flagged if `holistic-self` **or** `holistic-cross` raised a BLOCKER.
  Derived from arms already run; costs nothing extra.
- **`two-stage-filtered`**: `holistic-self`'s BLOCKER findings are shown to
  `openai:gpt-5.6-terra`, which returns keep/drop per finding. Flagged if ≥1 finding
  survives. Only instances where `holistic-self` proposed something need a filter call.

## The leakage guard — the thing that would make this study worthless

The decomposition **must** be derived from the task specification and the visible artefact.
If any part of the hidden suite reached the decomposer, directly or indirectly, the recall
number would be meaningless.

**Preregistered information boundary:**

- **The decomposer sees `problem.spec` and nothing else** — not the candidate solution, not
  the visible tests, not the hidden tests. The property list is therefore a function of the
  *problem* alone, computed once per problem and shared by every instance of it. This is the
  same shape as CLEAR's rubric, which is per-task rather than per-output.
- **The per-property checker sees** the property, the solution, and the visible test source —
  exactly the increment `holistic-cross` sees, plus one property. Never the hidden suite.
- **A committed test proves the hidden suite is unreachable from that code path**, by
  constructing a problem whose `_hidden_test` raises on attribute access and asserting the
  whole decompose-and-check path completes; plus a sentinel test asserting no hidden-suite
  byte appears in any prompt. Both must pass before any arm runs.

## n, and why that n

The primary comparison is paired and binary, so power comes from the **discordant** pairs.
Study 1 measured the run-to-run noise floor on P directly: `cross` re-run over the identical
56 instances disagreed on **3**, a discordance rate of δ = 0.054.

Modelling a true architectural effect Δ as decomposed-only flips at rate Δ, plus symmetric
noise at δ/2 in each direction, and testing with the two-sided exact McNemar at α = 0.05
(40,000 simulations, seeded):

| n on P | power at Δ = 10pp | at 15pp | at 20pp |
|---:|---:|---:|---:|
| 56 | 0.355 | 0.657 | 0.856 |
| 112 | **0.745** | 0.955 | 0.996 |
| 168 | 0.910 | 0.996 | 1.000 |

**Study 1's entire P stratum is n = 56, which has only 0.36 power at 10pp.** Auditing it
again would not answer the question. P is 10.4% of generated solutions, so more P instances
require more *generated* solutions, not more problems — the corpus is only 540.

**Preregistered rule:** generate additional batches of solutions over the same 540 problems
with the same generator and prompt, pooling stratum-P instances across batches, **until
P ≥ 100 or three batches exist, whichever comes first**. An instance is a
`(batch, problem_id)` pair. Batch 1 is study 1's committed solution set, reused byte-identically.
This rule depends only on execution outcomes and **never on any audit score**.

Target **n_P ≈ 112** (power 0.745 at 10pp, 0.955 at 15pp). Caps on the other strata,
which serve secondary outcomes: **C = 150** (a false-positive interval of about ±5pp),
**F = 30** (a sanity check only — an arm that cannot flag code that does not run means
nothing). Drawn once from seed **20260905**, before any arm runs.

Pooling two solutions to the same problem means two instances share a specification. They
are different solution bytes with different defects, and the pairing is per instance, so
McNemar remains valid; the mild dependence is recorded as a limitation.

## Stopping rule

**Budget US$20**, spend reported as it accrues. Arms run in this order so that the primary
comparison survives running out of money: **`checks` → `holistic-cross` → `decomposed-cross`
→ `holistic-self` → `two-stage` → `decomposed+two-stage`**. An arm that cannot finish is
reported with the n it reached, and the primary comparison is restricted to instances both
arms completed.

## Comparison count, declared in advance

**Six** preregistered comparisons: three arm pairs (`decomposed-cross` − `holistic-cross`,
`two-stage` − `holistic-cross` in its two forms) × two populations (P and C). The primary
outcome is one of them and is named above. Every other number in the report is descriptive.
This project has now run four studies over two tasks; that history is part of the
multiple-comparison picture and is stated in the report.

## What will not happen

Nothing changes after a score is seen. If something must change, the study **restarts** and
says so. If decomposition does not beat holistic review, that is the first sentence of the
results and it is not re-run until it flips.
