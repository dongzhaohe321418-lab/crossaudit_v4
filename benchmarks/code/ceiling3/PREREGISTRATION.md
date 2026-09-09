# Study 18 — ceiling 3: does the ceiling belong to the auditor model, or to auditing?

Preregistered on `study/ceiling3` **before any model call**, at the commit that adds this
file. Binding: `ceiling/PREREGISTRATION.md` §0 (the substrate, unchanged), §1.1–§1.2 (the
union-of-K curve and the saturation form, unchanged), §1.5 (the residual rule), Amendments
3–5 (intervals for paired binary contrasts), `RESULTS-CEILING.md` (frozen at b88ce74; D162),
`EXPERIMENT_RECORD.md` §9–§10, D153.

## 0. Why this study

Ceiling 1 measured three auditor families on the same frozen instances: the shipped
cross-vendor auditor (`openai:gpt-5.6-terra`, K = 8: union recall 30.0% [20.0, 40.7] at
16.0% FP), the generator's own small model (`anthropic:claude-haiku-4-5`, K = 8: 17.3%
[8.3, 27.3] at 24.0% FP, flattened) and a frontier model through a subscription route
(`gpt-6-astra`, K = 4). Two of the three are one vendor's models, and the third-vendor
family is the smallest model in the set, so ceiling 1 cannot say whether **the low
same-vendor ceiling is a vendor effect or a model-size effect**, nor whether **the ~30%
figure is a property of auditing by reading or of one vendor's models**. The owner's aim
is a general statement about the ceiling of AI audit; this study adds the missing axis
cheaply, on the same instances, with the same protocol, so the curves are commensurable.

## 1. What is run

Two new families through the product's provider broker, on ceiling 1's scope (stratum P,
n = 110; stratum C, n = 150; the frozen study-2 solutions; the shipped constitution; the
same prompt path `crossaudit.auditor.run.run_audit`):

| family | detector | draws |
|---|---|---|
| `self-strong` | `holistic` audit, `anthropic:claude-sonnet-4-6`, `generator:` unset (the same deliberate same-vendor bypass ceiling 1's `self` used, confined to the harness) | **K = 8** |
| `self-frontier` | `holistic` audit, `anthropic:claude-opus-4-8`, same bypass | **K = 4** (budget) |

The existing `cross`, `self` and `astra` draws are read, never re-run. Everything is
cached per `(kind, route, draw, instance)` in `records/ceiling3/cache/` by the same loop
(`explore.run_detector`); a cached reading is never bought twice.

## 2. Hypotheses, each falsifiable, with the sign fixed now

* **H18a (model size, not vendor).** Union recall at K = 8 on P for `self-strong` exceeds
  `self`'s 17.3% by more than its problem-cluster bootstrap interval allows: the
  difference `self-strong` − `self` at K = 8, 95% cluster bootstrap, excludes zero and is
  positive. If it does not, the low same-vendor ceiling is not explained by model size and
  the vendor-effect reading of ceiling 1 stands.
* **H18b (the ~30% is not one vendor's number).** The difference `self-strong` − `cross`
  at K = 8 on P, 95% cluster bootstrap, **includes zero**. This is a hypothesis of
  equivalence and is read as such: it comes out false if the interval excludes zero in
  either direction, and "includes zero" is reported with the interval's width, never as
  "no difference". A wide interval that includes zero is "not distinguishable at this n",
  and the report says so.
* **H18c (the frontier point).** `self-frontier` at K = 1 (mean over its draws) against
  `astra` at K = 1: the difference on P, with its interval; and `self-frontier`'s K = 4
  union against `astra`'s K = 4 union. No direction is predicted; both are reported.

**Primary outcome: the difference of union recalls at K = 8 on stratum P,
`self-strong` − `cross`**, with the 10,000-resample problem-cluster bootstrap (seed
20260910) — the raw union difference, which `RESULTS-CEILING.md` found sturdier than the
fitted-asymptote contrast when a curve has not flattened. The fitted asymptotes (§1.2's
form, constrained A ∈ [0, 1]) and the flattening test (the K = 7 → 8 gain against ceiling
1's bar) are secondary.

## 3. Secondary outcomes, named in advance

Union FP on C at every K for the new families, in the same table as recall; the
recall-to-FP exchange rate K = 1 → K_max; single-draw recall and FP; the `mixed` union
across families at matched total draws (`cross` + `self-strong`, K/2 each) against each
alone; the residual of the strongest family under §1.5's rule (the classification is
re-run by the same script on the same categories); per-family cost per reading from the
ledger; the fraction of P instances flagged by **no** family across all draws of all five
families — the one number that speaks to "the ceiling of AI audit" rather than of one
auditor.

## 4. What this study can and cannot license

It can say whether the ~30% ceiling moves with the auditor's vendor and size on this
substrate. It cannot say anything about the generator axis (all solutions are Haiku's),
the task axis (function-level code with short specifications) or the human baseline; those
are the next stages of the programme, each with its own preregistration:
stage B regenerates the instances with a stronger generator (`claude-sonnet-4-6`) and
re-executes the hidden suites; stage C is a benchmark with long specifications.

## 5. Budget, ladder, stopping

Ceiling 1's Haiku draws cost $0.87–1.51 each over 260 instances; Sonnet's list price is
about four times Haiku's, Opus's about twenty. Ladder, set by budget alone: `self-strong`
draws 1–4, then `self-frontier` draw 1, then `self-strong` 5–8, then `self-frontier` 2–4,
while cumulative spend is below **$120**; the run stops at the cap and reports the K
reached, with K_common = min over the families compared. One instance = one `run_id`,
priced from the ledger exactly.

## 6. Boundary

Unchanged from ceiling 1: the hidden suite reaches no prompt, check or model
(`tests/test_architectures.py`); the audit path is the product's; the same-vendor bypass is
the harness's and `src/` is not touched.

## Amendment 1 — 2026-09-09, after `self-strong` draw 1 and before draw 2 ran

**What was seen.** Draw 1 of `self-strong` completed (260 of 260, $2.26; one SSL
transport failure re-run) with **0 of 110 P flagged and 3 of 150 C flagged**; median
reply 49 output tokens in about 4 s. Because that is far below every family in ceiling 1,
the author stopped the run at the start of draw 2 (no draw-2 reading had landed) to rule
out a harness fault before spending further. A probe outside the caches (`ceiling3-probe`,
three P instances the shipped auditor flags, the identical prompt bytes via
`ceiling.astra_prompt`, both Anthropic models) showed the readings are genuine: Sonnet 4.6
mostly returns a terse, well-formed `{"verdict": "PASS", "findings": []}`; on one of the
three it wrote a long prose analysis before any JSON; Haiku 4.5 on the same bytes wrote
BLOCKER findings. Both vendors run at the product's default reasoning setting for the
auditor role (`reasoning_effort` unset in the benchmark's `crossaudit.yml` template).

**What changes: nothing in the design.** The ladder is set by budget alone (§5) and the
run resumes at draw 2 as planned; a near-zero single-draw family is exactly the kind of
result the union curve must be measured for, not assumed. **What is added:** (1) the
three probe replies are archived with the run (`probe/`), outside the caches, and are not
readings; (2) a secondary outcome — the share of `self-strong` and `self-frontier` replies
that were prose rather than the JSON the validator expects, from the harness's
`invalid_reason` and re-ask counts in the ledger — so that "the model sees nothing" and
"the model does not answer in the product's format" can be told apart in the report;
(3) the report states the reasoning setting per vendor beside every family.
