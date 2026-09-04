# Preregistration — does the audit find what the visible tests miss, in code?

Written and committed **before any solution was generated and before any arm was run**.
The only model calls that preceded it were four probe audits on a hand-written solution to
`HumanEval/0`, placed to measure per-call cost and to prove the plumbing; they produce no
study number and are listed in Deviations.

## Hypothesis, in a form that can come out false

Studies 1–3 measured CrossAudit's auditor on a materials-science **prose** task and found
recall against ground truth of 2.0% under the shipped constitution and 23.5% once the
rules were rewritten from the task's own grading rubric. The standing explanation is that
recall is low because the acceptance criteria are *prose judgements*.

**H1.** If that explanation is right, then in a domain whose acceptance criteria are
*executable*, the same architecture should reach materially higher recall.
**H1 is false if** recall on the primary population is not materially above the 2.0%–23.5%
band measured on prose.

**H0 (the null this study is built to be able to report).** The audit adds nothing in code
that the visible tests do not already give you: `cross+checks` recall on the primary
population does not exceed `checks` recall on the same instances.

If H0 survives, that sentence is the first sentence of `RESULTS.md`.

## The population

A solution is assigned to exactly one stratum by execution, with no model involved:

| stratum | definition |
|---|---|
| **P** | passes **every** visible test **and** fails **at least one** hidden test — "looks right, is wrong" |
| **C** | passes every visible test and every hidden test — correct |
| **F** | fails at least one visible test |

**P is the population this study is about.** A test run catches F. Nothing catches P except
a reader.

## Primary outcome — one number, named in advance

**Recall on P: the fraction of stratum-P instances in the audit set that an arm flags,
where "flags" means the arm raised at least one BLOCKER finding** (model tier or
deterministic tier; ADVISORY never gates in the product and does not count here).

Reported per arm, with a Wilson 95% interval and the n of the cell.

## Secondary outcomes, all named in advance

1. **`cross+checks` recall on P minus `checks` recall on P** — the audit's marginal value
   over the visible tests. Paired on the same instances; McNemar exact p and a seeded
   paired-bootstrap 95% interval on the difference.
2. **`cross` recall on P minus `self` recall on P** — does a second vendor beat the model
   grading itself, where on prose it did not clearly.
3. **`cross+checks` recall on P minus `cross` recall on P** — what the deterministic layer
   adds to the model.
4. **False-positive cost: the fraction of stratum-C (correct) solutions an arm flags.**
   Reported as prominently as recall. In code, a tool that flags correct work stops being
   used, so this is not a footnote.
5. **Precision**: of the instances an arm flags, the fraction that fail a hidden test.
   Reported twice — raw on the audit set, and reweighted to the full corpus by the known
   stratum sampling fractions, because the audit set is stratified and the raw figure is
   therefore biased by design.
6. **Flag rate**, reweighted to the corpus.
7. **Noise floor**: `cross` run a second time over the identical audit set. A difference
   between arms smaller than this run-to-run spread is not a finding.

## Arms

Every arm judges the **same** generated solutions. Nothing is regenerated per arm.

| arm | auditor | deterministic layer | increment shown |
|---|---|---|---|
| `none` | — | — | — |
| `checks` | — | `general` + `visible_tests` | — |
| `self` | `anthropic:claude-haiku-4-5-20251001` (the generator's own model) | `general` | solution + visible test source |
| `cross` | `openai:gpt-5.6-terra` | `general` | solution + visible test source |
| `cross+checks` | `openai:gpt-5.6-terra` | `general` + `visible_tests` | solution + visible test source |
| `cross-replicate` | `openai:gpt-5.6-terra` | `general` | identical to `cross` — the noise floor |

Held fixed across every model arm: the constitution (the shipped
`scaffold/templates/GENERAL_AUDIT_RULES.md`, unmodified), the committed task (the
problem's own specification, which is what `CA-TASK-001` grades against), the increment,
the audit entry point (`crossaudit.auditor.run.run_audit`), `max_rounds: 1`,
`authority.lone_model_blocker: block`.

Varied: the auditor model, and whether the visible suite's *execution result* is in the
deterministic-check block of the prompt.

**The `self` arm is a configuration CrossAudit refuses to run.** `run_audit` raises
`ConfigDenial` on a same-vendor generator/auditor pair. The arm is obtained by leaving
`generator:` unset in its project config, so the heterogeneity gate has nothing to compare.
This is a deliberate bypass of a product guarantee, for measurement only.

## Corpus

EvalPlus, chosen because it was built for exactly this structure — the base suites are too
weak, and the plus suites are the ground truth they miss.

* HumanEval (MIT) — the visible suite, `openai/openai_humaneval`.
* HumanEval+ (Apache-2.0) — the hidden suite, `evalplus/humanevalplus`, 164 problems.
* MBPP+ (Apache-2.0) — `evalplus/mbppplus`, 378 problems. Carries both halves: `test_list`
  (the three assertions the prompt shows the model) and `test` (the hidden suite).

542 problems total. **Excluded before generation: `HumanEval/32` and `Mbpp/590`** — the two
whose own *reference* solutions fail their own hidden suites in this harness (numerical
tolerance), where "fails a hidden test" would not mean "is wrong". The other 540 references
pass, which is this harness's validation. **540 problems enter the study.**

The corpus is not committed. `manifest_corpus.json` pins per-file sha256, revision, row
count and licence.

## Generator

`anthropic:claude-haiku-4-5-20251001`, one solution per problem, one call, plain
"write this function" prompt, no rubric and no constitution.

Chosen before any score, for one reason stated in advance: a frontier generator puts too
few solutions in stratum P to measure recall on it inside the budget, and **P, not the
generator, is the object of study**. The bias this introduces is named in the report: a
small model's wrong-but-plausible code may be more obviously wrong than a frontier model's,
which biases auditor recall **upward**.

## Intended n and the audit set

Auditing all 540 solutions in four model arms exceeds the budget, so the audit set is a
stratified sample drawn **once**, from seed `20260904`, **before any arm runs**, and shared
by every arm — so no arm can influence which instances it sees:

* **all** of stratum P (the primary population), capped at 200;
* **150** of stratum C, or all of it if smaller — sized to bound the false-positive rate to
  roughly ±8 points at 95%;
* **80** of stratum F, or all of it if smaller.

n for every cell is reported, including cells that shrink because a call failed.

## Stopping rule

Whole-study budget **US$15**. Arms run in this order so that the three that answer the
primary question complete first if money runs short:

    cross+checks → checks → none → cross → self → cross-replicate

An arm stops early if its own spend passes its cap; the instances it reached are reported
with their n and the shortfall is a numbered deviation. `cross-replicate` is dropped
entirely if total spend passes $12 before it starts, and its absence is reported.

## Analysis, fixed in advance

* Proportions with **Wilson 95% intervals**; the interval is reported beside every rate.
* Arm-vs-arm differences on P are **paired** (same instances): **McNemar exact** (binomial
  on the discordant pairs) plus a **seeded paired-bootstrap 95% interval** (10,000
  resamples, seed `20260904`) on the difference in proportions. Exact p, never a threshold.
* Corpus-level precision and flag rate are **reweighted** by stratum sampling fraction.
* **Comparison count**: the three named arm-vs-arm differences on P (secondaries 1–3), plus
  the three false-positive comparisons. Six. The primary outcome was named here, before any
  score, and is not selected from among them.
* Anything not in this file that appears in the results is labelled **exploratory**.

## What this study cannot do

* One generator. A finding about `claude-haiku-4-5`'s errors is not a finding about all code.
* Two Python benchmarks of short, self-contained functions. Not a repository.
* Cross-vendor is not independence: two frontier models share training data and conventions.
* The audit is measured at **round one only**. Whether revision helps is a different study,
  and study 3 already found that on prose it hurts.
