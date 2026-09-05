# Study 8 — the ceiling of AI audit: what a reader can ever see, and whether the loop raises accuracy

**Committed before the first model call of this study, including the credential probe.**
Nothing below was written after seeing any result of this study.

The owner's question: *as AI-generated data grows, can AI audit itself to raise
accuracy — and where is the limit?* This study answers it in two measurements that
are deliberately kept apart, because the programme's record shows they are not the
same question:

* **Ceiling 1 — seeing.** How much of a fixed defect population can a detector family
  *ever* flag, given unlimited independent readings? The asymptote of the union-of-K
  recall curve.
* **Ceiling 2 — correcting.** Does audit-then-revise raise the fraction of solutions
  that pass a hidden test suite, net of the ones it breaks?

Ground truth throughout is a Python interpreter raising `AssertionError` or not.
**No model judges any outcome anywhere in this study.**

---

## 0. Substrate, held fixed

| | |
|---|---|
| audit set | study 2's frozen 290 instances, `records/study2/audit_set.json`, unchanged |
| stratum P | passes every visible test, **fails a hidden one** — n = 110 (b1 56, b2 54) |
| stratum C | passes every test — the false-positive population — n = 150 (b1 77, b2 73) |
| stratum F | fails a visible test — n = 30. **Not extended by this study** (deviation 1) |
| instance | a `(batch, problem_id)` pair; 222 distinct problems, **68 of which appear in both batches** |
| solutions | study 2's, byte-identical, **not regenerated** — generation variance is removed by construction |
| generator | `anthropic:claude-haiku-4-5-20251001`, frozen |
| cross route | `openai:gpt-5.6-terra` — the shipped cross-vendor auditor |
| self route | `anthropic:claude-haiku-4-5-20251001` — the generator's own model |
| flag | ≥ 1 BLOCKER finding, exactly as studies 1, 2 and 7 |
| audit path | `crossaudit.auditor.run.run_audit` — the product's real audit, unchanged |
| constitution | the shipped `GENERAL_AUDIT_RULES.md`, unchanged (except arm R, §2.2) |
| hidden suite | never reaches any prompt, any check, or any model |

Because 68 problems contribute two instances each, **every interval in this study
bootstraps over problems, not over instances**, resampling whole problem clusters.

---

## 1. Ceiling 1 — the saturation curve

### 1.1 What is run

For a *family* (a fixed detector configuration) and K independent draws over the same
instances, define

    union recall at K   = (1/|P|) · #{ i in P : at least one of the K draws flagged i }
    union FP at K       = (1/|C|) · #{ i in C : at least one of the K draws flagged i }

and average each over **all C(K_max, K) subsets of the available draws** — exhaustively,
not by sampling.

Families:

| family | detector | draws that already exist | target |
|---|---|---|---|
| `cross` | `holistic` audit, `openai:gpt-5.6-terra` | 3 complete over P∪C | **K = 8** |
| `self` | `holistic` audit, `anthropic:claude-haiku-4-5-20251001`, `generator:` unset | 1 complete + 1 partial (88 of 260) | **K = 8** |
| `mixed` | the union across families at matched total draws | — | K/2 from each, K = 2, 4, 6, 8 |

`mixed` at total K uses K/2 `cross` draws and K/2 `self` draws, averaged over all
C(K_cross, K/2) × C(K_self, K/2) combinations. Its comparator is each single family at
the same **total** K, so diversity is tested against same-model repetition at equal cost
in readings.

Existing draws are admitted on the grounds `RESULTS-2.md` and `RESULTS-EXPLORE.md`
already used: study 1's `cross`, `cross-replicate` and `self` arms carry no deterministic
layer (`dcl_blockers == 0` on every row) and audit byte-identical batch-1 solutions.
`self` draw 2 is study 1's `self` arm, complete only on batch 1; this study completes it.

### 1.2 The saturation form, chosen and justified before fitting

Let instance *i* have an unknown per-draw flag probability p_i. Then

    E[ union recall at K ] = (1/|P|) · Σ_i [ 1 − (1 − p_i)^K ]   →   Pr(p_i > 0)  as K → ∞.

**So the asymptote A is exactly the fraction of the defect population the family can
ever see, and 1 − A is the fraction it can never see, however many times it reads.**
That is the quantity this study calls the ceiling, and it is why the union-of-K curve
is the right object.

**Primary fit (preregistered): the exponential saturation form**

    recall(K) = A · (1 − e^{−K/τ}),   A ∈ [0, 1], τ > 0

fitted by unweighted least squares to the K = 1 … K_max subset-averaged union recall
points. Chosen over the alternatives for three stated reasons: it has exactly one
interpretable asymptote; it is exact when the detectable p_i are homogeneous; and under
heterogeneity it is **conservative** — a mixture of exponentials rises faster early and
flattens later than any single exponential, so a single-exponential fit to a
heterogeneous population **under**estimates A. A ceiling reported this way is therefore
a floor on the true ceiling, which is the direction an honest ceiling claim should err.

**Reported beside it, always, never instead of it:**

1. **The raw union recall at K_max.** Model-free, and a strict lower bound on A. If the
   fitted A and the raw K_max value differ by more than 5 percentage points, the report
   says which a reader should trust and why, at the number.
2. **A zero-inflated beta-binomial MLE** on the per-instance flag counts k_i out of
   K_max: p_i ~ π·Beta(a,b) + (1−π)·δ₀, asymptote Â = π. It uses every instance's count
   rather than the averaged curve and it accommodates heterogeneity. It is **secondary**,
   for one reason stated in advance: π and a Beta component with a → 0 are only weakly
   distinguishable from 8 draws, so the ZIBB asymptote is expected to be unstable upward.
   If the two estimators disagree the report says so and prefers the conservative one.
3. **A flatness diagnostic**: the marginal gain from K_max − 1 to K_max draws. **If that
   gain exceeds 1.0 percentage point, the asymptote is labelled an extrapolation** in the
   headline sentence and everywhere it is quoted, not only in a limitations section.
4. **Fit quality**: R² and the maximum absolute residual over the K = 1 … K_max points.

### 1.3 Primary outcome — one number

**A(`self`) − A(`cross`)**: the difference of fitted asymptotes, with a 95% percentile
bootstrap interval from 10,000 resamples of **problem clusters** (both instances of a
problem move together), refitting the curve inside each resample.

The sign convention is fixed here so it cannot be chosen later: **positive means the
generator's own model can ultimately see more of its own defects than a stranger can.**

### 1.4 Secondary outcomes, named in advance

* A(`cross`) and A(`self`) individually, each with a bootstrap interval.
* A(`mixed`) at K = 8 total, against A(`cross`) and A(`self`) at K = 8.
* **Union FP on stratum C at every K, for every family** — reported in the same table as
  recall, never in a separate one. A ceiling reached at a false-positive rate the product
  cannot live with is not a usable ceiling and the report must say so at the number.
* The recall-to-FP exchange rate: Δ union recall / Δ union FP from K = 1 to K = K_max.
* Per-family single-draw recall and FP (K = 1), for continuity with studies 1, 2 and 7.

### 1.5 The residual — the classification rule, written before looking

The **residual set** is every stratum-P instance that **no draw of any family in this
study ever flagged**. It is classified by hand from the hidden-test failure record, the
visible tests, the candidate solution and the canonical solution. The rule below is
fixed now; the first residual instance is not read until this file is committed.

Categories, **assigned by taking the first that applies, in this order**:

1. **`timeout`** — the hidden run did not terminate inside the harness timeout, or failed
   on a resource limit, so no assertion evidence exists. (Named because
   `CORRECTIONS.md` item 4 records that 4 of study 1's 56 P instances are timeouts and
   that this contradicts the stated ground truth.)
2. **`unexercised-edge`** — the solution is correct on every *input class* the visible
   suite exercises and fails only on an input class the visible suite omits entirely
   (empty, zero, negative, duplicate, boundary, very large, non-ASCII).
3. **`spec-misreading`** — the solution computes a self-consistent but *different*
   function from the one the specification's prose states (wrong tie-break, wrong
   rounding, wrong inclusive/exclusive bound, wrong ordering), and the visible tests do
   not separate the two readings.
4. **`wrong-algorithm`** — the approach is incorrect in general, not only at an edge, and
   is right on the visible cases by coincidence.
5. **`ambiguous-oracle`** — the hidden suite's expectation is itself arguable on the
   specification as written; a competent reader could defend the candidate. (EvalPlus is
   known to contain some of these, and a ceiling built on them is not a ceiling on audit.)
6. **`other`** — described individually, one line each.

Recorded per residual instance: instance id, benchmark, category, the failing input class
in one phrase, and the number of hidden-test inputs failed. **If a category holds a stable
share of the residual that no model-reading-text ever finds, that is the shape of the
ceiling, and it is the report's most important sentence.**

### 1.6 Ladder and stopping rule for ceiling 1

K_max is set by **budget alone** and never by any outcome. The leaderboard is not
consulted while deciding whether to extend.

1. Complete `self` draw 2 (172 instances), then run `cross` draws 4–5 and `self` draws
   3–5, giving **K = 5 in both families**. This is the floor of the study.
2. Then extend one draw at a time, alternating `cross`, `self`, `cross`, …, while
   cumulative ceiling-1 spend is below **$13.00** and K < 8.
3. Report at the K reached. If K_cross ≠ K_self, the head-to-head and `mixed` analyses
   use K_common = min(K_cross, K_self), and each family's own K_max is reported separately.

---

## 2. Ceiling 2 — the closed loop

### 2.1 What is run

One `generate → audit → revise once` cycle per instance, scored model-free.

* **Generation is not repeated.** Every arm starts from study 2's frozen solution for that
  instance, so no difference between arms can be generation variance — the confound
  `CORRECTIONS.md` item 2 withdrew a headline over.
* **Audit** is `run_audit`, the product's real audit, on the same increment the detection
  study shows it: `work/solution/solution.py` and `work/solution/tests_visible.py`.
* **Revise** happens **iff the audit returns a BLOCKED verdict** — which is what the
  product does. This is deliberate: the loop's reach is bounded by its recall, and
  pretending otherwise would measure a product that does not exist. Where the audit does
  not block, the revised solution **is** the original, and the instance still counts in
  the denominator.
* The revision prompt is **the product's own**: `crossaudit.generator.GENERATOR_SYSTEM`
  with `crossaudit.generator.build_prompt(..., findings=render_findings(outcome.report))`,
  called exactly as `cli/build.py` calls it on a repair round. No new prompt is written.
* The revised `work/solution/solution.py` is scored against the **hidden** suite through
  `execute.py`'s subprocess sandbox. Nothing is executed in the harness interpreter.

### 2.2 Arms

| arm | auditor | reviser | differs by |
|---|---|---|---|
| `self-loop` | `anthropic:claude-haiku-4-5` (the generator's own model) | the generator | — |
| `self-loop-rep` | identical to `self-loop`, second draw | the generator | **nothing** — the replicate |
| `cross-loop` | `openai:gpt-5.6-terra` | the generator | the auditor's vendor |
| `referent-loop` | `openai:gpt-5.6-terra` | the generator | one added constitution rule |

`referent-loop` adds exactly one rule to the constitution and changes nothing else:

> ### CA-COVER-001
> **BLOCKER.** The increment's visible test suite is shown to you. It is not a
> specification and it is not complete. Identify the behaviour the specification requires
> that the visible tests **do not exercise** — the input classes they never construct —
> and judge the solution on those. A defect the visible tests would not catch is the
> defect this rule exists to find.

The referent — what the auditor is told to look for — is the only lever in this
programme's history ever measured to move recall by more than a few points
(`AUDIT_ARCHITECTURE.md` §1, the split-rules result), which is why it is the third arm.

**`self-loop` and `self-loop-rep` leave `generator:` unset** so the product's same-vendor
gate has nothing to compare against — the identical deliberate bypass studies 1, 2 and 7
recorded, confined to the harness. `src/` is not touched.

### 2.3 Sample

**56 P and 56 C**, drawn as **28 from each of the four (stratum, batch) cells**, by
`random.Random(20260907).shuffle` over sorted instance ids within each cell. Drawn and
committed before the first audit of this ceiling. Every arm sees the identical 112
instances, so every contrast is paired.

n = 56 P is the brief's ceiling ("all 56 if budget allows"); 56 C matches it so the
breakage rate is estimated on the same footing as the repair rate.

### 2.4 Primary outcome — one number

**The net change in hidden-test pass rate for `self-loop`, over the whole 112-instance
sample, unconditional on whether a revision occurred:**

    net = ( #{was failing, now passes} − #{was passing, now fails} ) / 112

**Unconditional is not a detail.** `CORRECTIONS.md` item 9 is this project's largest
retraction and it is exactly this error: study 4 conditioned its primary outcome on
"the loop revised at least once", which is a consequence of the treatment, and
manufactured a −19.6 effect where the unconditional estimate was −4.0 with an interval
spanning zero. The conditional figure is computed here too and is labelled
**exploratory** at every occurrence.

Interval: 95% percentile bootstrap over **problem clusters**, 10,000 resamples. Inference
on the paired binary counts is **exact McNemar** on the discordant pairs (fixed/broken),
because `CORRECTIONS.md` item 4 records that a percentile bootstrap over discordant pairs
that all point one way mechanically returns a one-signed interval and cannot be read as
excluding zero.

### 2.5 Secondary outcomes, named in advance

* The two components of the net, always printed side by side and never separately:
  **fixed rate on P** (was wrong, now right) and **broken rate on C** (was right, now wrong).
* The same net, fixed rate and broken rate for `cross-loop` and `referent-loop`.
* `self-loop` − `cross-loop` net difference, paired.
* `referent-loop` − `cross-loop` net difference, paired — the referent's effect with the
  vendor held fixed.
* The audit's flag rate in each arm on P and C, which bounds the loop's reach.
* **The loop's own noise floor**: `self-loop` vs `self-loop-rep`, the replicate
  `EXPERIMENT_RECORD.md` §9 requires for this estimand. Until it is measured, no sentence
  in this report may say "inside the noise floor" about any loop result. The single-draw
  detection floor (6.4 points at n = 110) does **not** bound this estimand and is not
  quoted against it.

### 2.6 Kill condition, registered

**If `self-loop`'s net change is ≤ 0, or its 95% interval contains 0, or its magnitude is
inside the `self-loop` / `self-loop-rep` replicate spread, then on this evidence AI
self-audit does not raise accuracy — and the report's first sentence says so.**

This condition can only be evaluated after both `self-loop` and its replicate have run.

### 2.7 Stopping rule for ceiling 2

Budget cap **$5.00**, including the replicate. Ceiling 2 runs **first**, before ceiling 1,
because it carries the kill condition. If the cap binds before all four arms complete,
the arms are completed in the order `self-loop`, `self-loop-rep`, `cross-loop`,
`referent-loop`, and any arm that did not finish is reported as not run rather than as a
partial rate.

---

## 3. Study-wide

### 3.1 Budget and stopping rule

**$20.00 total model spend**, from the projects' own usage ledgers, never reconstructed
except where a figure is marked reconstructed at the figure.

    ceiling 2 (four arms)          $5.00
    ceiling 1 (the draw ladder)   $13.00
    reserve (probes, retries)      $2.00

The study stops at the budget or at completion of the ladder, whichever comes first.
No arm is added and no arm is dropped on the strength of a result.

### 3.2 The comparisons this study makes, counted in advance

Two primary outcomes, one per ceiling, declared above. Every other number is secondary or
exploratory and is labelled at the sentence, not in a footnote.

Planned comparisons: (1) A(self) − A(cross); (2) A(mixed) − A(cross) at K = 8;
(3) A(mixed) − A(self) at K = 8; (4) `self-loop` net vs 0; (5) `cross-loop` net vs 0;
(6) `referent-loop` net vs 0; (7) `self-loop` − `cross-loop`; (8) `referent-loop` −
`cross-loop`; (9) `self-loop` vs `self-loop-rep` (the floor, not a hypothesis test).
**Nine planned comparisons.** No correction is applied to the two primaries, which are
declared singly in advance; every secondary contrast is reported with its unadjusted exact
p **and** the Bonferroni-over-nine threshold stated beside it, so a reader can apply either.

This project has now run eight studies over two tasks. That history is part of the
multiple-comparison picture and is stated in the report's limitations, as
`EXPERIMENT_RECORD.md` §4 requires.

### 3.3 Reproducibility standard for this study

Above `EXPERIMENT_RECORD.md`, because this branch is intended for publication:

* **Every number in `RESULTS-CEILING.md` regenerates from committed records with no API
  key and no network**, via `python benchmarks/code/report_ceiling.py`. A number that
  exists only in a transcript does not exist. The report generator is written before the
  first arm finishes and is run on partial data throughout.
* **The manifest records, per draw**: model id, route, the sampling parameters, the
  reasoning-effort setting, the SYSTEM prompt sha256 and the SYSTEM prompt text (it is
  corpus-free), the audit prompt sha256 per instance, the frozen audit-set digest, the
  harness commit sha, `git status --porcelain` at freeze, the Python version and the
  versions of every package a measurement depends on, and UTC start and end per arm.
* **The manifest states which of those a re-run must match exactly** (audit set digest,
  model ids, prompt shas, flag definition) **and which do not matter** (worker count,
  wall-clock, machine).
* Every draw is cached by `(kind, model, draw, instance)`. **A cached draw is never
  re-run.** One JSONL row per (arm, draw, instance).
* No corpus text, no model finding prose and no prompt embedding corpus text is
  committed. EvalPlus is redistributable, so candidate and revised **solutions** may be
  committed; findings prose may not, because it quotes the corpus.
* Run directories are archived to `~/Documents/Crossaudit/study-data/wt-ceiling-runs/`
  with a sha256 manifest, and the digest is committed.

### 3.4 What this study cannot license, stated now

* One corpus of short self-contained Python functions is not a repository.
* One generator is one generator; a ceiling measured for `claude-haiku-4-5`'s output is
  not a ceiling for all generated code.
* Vendor independence is not statistical independence.
* The asymptote is a fitted quantity. **There is no purely statistical way to separate
  "never findable" from "findable with very small probability" out of 8 draws**, which is
  why §1.5's hand classification of the residual — model-free evidence about what the
  never-found defects *are* — is load-bearing and is not an appendix.

---

## Amendment 1 — 2026-09-05 — the `astra` family (frontier model through the Codex CLI)

Added at the owner's request before any `astra` call, as a dated amendment rather than an
edit to the text above. **The primary outcomes and the kill condition are unchanged.**

A fourth detector family, `astra`: the identical holistic audit prompt the shipped
`holistic-cross` detector uses — identical constitution, identical specification,
identical solution, identical instructions, nothing added — issued to `gpt-6-astra` at
`model_reasoning_effort="high"` through the Codex CLI:

    codex exec -m gpt-6-astra -c 'model_reasoning_effort="high"' \
        --sandbox read-only --skip-git-repo-check - < prompt.txt

parsed by the same finding parser and cached as `(holistic, gpt-6-astra, draw, instance)`.
Target **K = 4**, priced by measuring the first 20 instances and extrapolating before
committing to the full set; if the full set is unaffordable it runs on the confirm half of
study 7's committed split and that is recorded as a deviation.

**What it is for.** It tests whether the ceiling is *model-strength-limited*. If the
strongest available model's asymptote sits with the others, the ceiling is in the task
and not in the model, and no amount of model progress moves it. If it sits well above,
the ceiling is in the model, and the product's recommendation changes.

**What it is not.** This route bypasses the product's provider broker and its
heterogeneity guard entirely: no config, no same-vendor gate, no metered ledger. It is
therefore **a measurement of a model, not of the product path**, and every number derived
from it is labelled that way. It is run from an empty scratch directory outside the
worktree, read-only and stdin-only, so nothing it might read can reach the solutions or
the hidden tests by path; the prompt carries everything it may see.

Its draws join `mixed` at matched total draws, and the §1.5 residual becomes "flagged by
no draw of any of the **four** families".

**Status when amendment 1 was written: not run.** The installed Codex CLI
(`codex-cli 0.150.1`) refused `gpt-6-astra` with `400 — The 'gpt-6-astra' model requires a
newer version of Codex`. See amendment 2.

---

## Amendment 2 — 2026-09-05 — `astra` is enabled

The Codex CLI was upgraded to **0.153.4** and the amendment-1 invocation now answers. The
`astra` family runs as amendment 1 specifies. **The primary outcomes and the kill
condition are unchanged, and no other arm changes.** Three points are fixed here, before
the first `astra` call, because they were open in amendment 1:

1. **Cost is not metered in dollars on this route.** `codex exec` bills a subscription and
   reports only a token count per call. The per-call token counts are recorded in the
   manifest and totalled in the report; **`astra` therefore consumes none of the $20 API
   budget and is reported in tokens, with any dollar figure marked reconstructed at
   published rates and never mixed into the ledger totals.** Every other arm's spend is
   read from the product's own usage ledger as before.
2. **Wall clock, not money, is `astra`'s binding constraint**, so the ladder is: price 20
   instances first; then run draw 1 over as much of the audit set as the measured rate
   allows; extend to K = 4 only while the study's other work is complete. If the full 290
   instances are unaffordable in wall clock, the family runs on **the confirm half of
   study 7's committed split** (`records/explore/split.json`, 55 P and 74 C), recorded as
   a numbered deviation.
3. **The residual is then reported twice, both stated**: over all 110 P instances for the
   three broker families, and over whatever population `astra` covers for the
   four-family version. Neither is presented as the other.

`codex exec` prints a token-usage line and a skills-budget warning around the reply; both
are stripped before the finding parser sees anything, and the stripping rule is a fixed
regular expression committed with the harness, not a judgement call made per reply.
