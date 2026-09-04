# EvalPlus, n = 56 — the domain hypothesis is false: in code the auditor names 8.9% of what the visible tests miss, inside the band it managed on prose

**Of 56 solutions that pass every test the developer can see and fail a hidden test —
"looks right, is wrong" — CrossAudit's shipped cross-vendor configuration named 5.
Recall 8.9% (5/56), 95% CI [3.9%, 19.3%].** The prose studies measured 2.0% under the
shipped constitution and 23.5% once the rules were rewritten from the task's rubric. **8.9%
is inside that band, not above it.** Executable acceptance criteria did not lift the
auditor's recall, so the standing explanation for the prose result — that recall is low
*because the criteria are prose judgements* — does not survive contact with a domain where
they are not.

**The audit's marginal value over the visible tests, which is the number that decides
whether the second opinion is worth paying for: `cross+checks` − `checks` = +8.9 points
of recall on that population** (5 instances against 0; McNemar exact p = 0.0625; paired
bootstrap 95% CI [1.8%, 17.9%]), bought at **2.7% of correct solutions wrongly flagged**
(4/150, CI [1.0%, 6.7%]). The deterministic layer alone finds none of them, by construction:
those solutions pass the visible suite. Everything the audit contributes on this population,
it contributes as a model reading code.

**The result that decides the `self`-vs-`cross` question is not the recall number.** The
generator grading its own work reached *higher* recall than the cross-vendor auditor —
16.1% against 10.7%, a 5.4-point gap that is not distinguishable from zero (p = 0.51) and
sits inside this study's own noise floor. It got there by flagging **20.0% of correct
solutions** against cross's 4.7% — a 15.3-point difference that is not ambiguous
(p = 0.000066, CI [8.7%, 22.7%]). Self-audit is not a cheaper auditor. It is an alarm that
fires on one correct solution in five, and in code that is the failure mode that ends a
tool's life.

**Every primary number in this study passed through no model.** Ground truth is a Python
interpreter raising `AssertionError` or not raising it, on test suites that were written
before CrossAudit existed and that no model in this study ever saw. That is the difference
between this study and studies 1–3, whose every number rests on CLEAR — a reimplementation
from a paper whose authors released no evaluation code, and whose ground truth is itself
produced by a model. Nothing here inherits that.

Whole-study spend: **$7.08** of a $15 budget.

Everything below is measured. Nothing is extrapolated.

---

## What was run

Preregistered in [`PREREGISTRATION.md`](PREREGISTRATION.md), committed before a single
solution was generated. Code frozen at **`5463717`** with `git status --porcelain` empty;
the freeze is recorded in `records/study1/manifest.json` together with the sha256 of every
file the study added.

| | |
|---|---|
| corpus | HumanEval (MIT, rev `7dce6050a7d6`, 164 rows), HumanEval+ (Apache-2.0, rev `d32357cf319e`, 164), MBPP+ (Apache-2.0, rev `b2d74c91837c`, 378) |
| problems | **540** — 542 less `HumanEval/32` and `Mbpp/590`, excluded by name before generation |
| generator | `anthropic:claude-haiku-4-5-20251001`, one call per problem, no rubric, no constitution |
| cross auditor | `openai:gpt-5.6-terra` — the product's OpenAI default and studies 1–3's auditor |
| self auditor | `anthropic:claude-haiku-4-5-20251001` — the generator's own model |
| judge | **none. There is no judge in this study.** |
| constitution | the shipped `scaffold/templates/GENERAL_AUDIT_RULES.md`, unmodified |
| settings | `max_rounds: 1`, `authority.lone_model_blocker: block`, checks profile `general` (+ `visible_tests` in the two `checks` arms) |
| audit entry point | `crossaudit.auditor.run.run_audit` — the product's real audit |
| seed | `20260904` |
| dates (UTC) | generation 2026-09-04 14:44→15:02; arms 15:04→16:20 |
| environment | harness Python 3.13.5; test executor Python 3.13.5 + numpy 2.4.0 on macOS-26.6.2-arm64; 30 s per-suite timeout |

### The harness validates itself, without a model

Before the preregistration was written: **540 of 542 EvalPlus reference solutions pass
their own hidden suites in this harness.** The two that do not — `HumanEval/32`
(`find_zero`, numerical root finding) and `Mbpp/590` (1 failing input of 104) — are
excluded by name, because on them "fails a hidden test" would not mean "is wrong". If the
execution harness were broken this number would not be 99.6%.

### The population

Every solution is assigned to exactly one stratum by execution alone:

| stratum | definition | n of 540 | share |
|---|---|---:|---:|
| **P** | passes every visible test, fails ≥1 hidden test — **"looks right, is wrong"** | **56** | 10.4% |
| **C** | passes both | 455 | 84.3% |
| **F** | fails ≥1 visible test | 29 | 5.4% |

Base pass rate 94.6%, plus pass rate 84.3% — a 10.4-point EvalPlus drop, in line with what
EvalPlus reports for models of this class, which is a second, independent sign that the
harness is measuring what it claims to.

**P is the population the product's claim is about.** A test run catches F. Nothing catches
P except someone reading the code.

### The audit set

Auditing all 540 solutions in four model arms exceeds the budget, so the audit set was drawn
once, from the seed, **before any arm ran**, and every arm judged the identical set:

| stratum | in corpus | audited | weight of one audited instance |
|---|---:|---:|---:|
| P | 56 | **56 (all)** | 1.00 |
| C | 455 | 150 | 3.03 |
| F | 29 | **29 (all)** | 1.00 |
| total | 540 | **235** | |

Nothing was regenerated per arm. Every arm judged the same bytes.

---

## The primary outcome

**Recall on P — the fraction of "looks right, is wrong" solutions an arm flags.** A flag is
at least one BLOCKER finding, from either tier; ADVISORY never gates in the product and does
not count here.

| arm | recall on P | k/n | 95% CI (Wilson) |
|---|---:|---:|---|
| `none` | 0.0% | 0/56 | [0.0%, 6.4%] |
| `checks` | **0.0%** | 0/56 | [0.0%, 6.4%] |
| `self` | 16.1% | 9/56 | [8.7%, 27.8%] |
| `cross` | 10.7% | 6/56 | [5.0%, 21.5%] |
| **`cross+checks`** | **8.9%** | **5/56** | **[3.9%, 19.3%]** |
| `cross-replicate` | 8.9% | 5/56 | [3.9%, 19.3%] |

`checks` scores zero by construction and that is the point of the population: these
solutions pass the visible suite, so a suite runner has nothing to say about them.

## The false-positive cost, reported here rather than in a footnote

**Correct solutions (stratum C) that an arm flags.** In code this is the number that decides
adoption: a reviewer who is told twice that working code is broken stops reading the third
report.

| arm | flagged correct code | k/n | 95% CI |
|---|---:|---:|---|
| `none` | 0.0% | 0/150 | [0.0%, 2.5%] |
| `checks` | 0.0% | 0/150 | [0.0%, 2.5%] |
| **`self`** | **20.0%** | **30/150** | **[14.4%, 27.1%]** |
| `cross` | 4.7% | 7/150 | [2.3%, 9.3%] |
| **`cross+checks`** | **2.7%** | **4/150** | **[1.0%, 6.7%]** |
| `cross-replicate` | 4.0% | 6/150 | [1.8%, 8.5%] |

## Stratum F — the sanity check

Solutions that fail a visible test. If an arm cannot flag these, nothing else it says means
anything.

| arm | flagged | k/n |
|---|---:|---:|
| `checks` | 100.0% | 29/29 |
| `cross+checks` | 100.0% | 29/29 |
| `cross-replicate` | 86.2% | 25/29 |
| `cross` | 79.3% | 23/29 |
| `self` | 48.3% | 14/29 |
| `none` | 0.0% | 0/29 |

**A model reading code that does not run misses a fifth of it; the same model, shown the
test result, misses none.** `cross` (79.3%) against `cross+checks` (100%) on the same
instances is the clearest thing in this study, and it is an argument for the deterministic
layer, not for the audit. The `self` arm's 48.3% is worse than a coin flip on code its own
model wrote and cannot run.

## Corpus level, reweighted

Raw rates on a stratified sample are biased by the design, so these are reweighted by the
known sampling fractions above. Precision counts a flag as correct if the solution fails
*any* test, visible or hidden.

| arm | flag rate | precision |
|---|---:|---:|
| `none` | 0.0% | — |
| `checks` | 5.4% | **100.0%** |
| `self` | 21.1% | 20.2% |
| `cross` | 9.3% | 57.7% |
| `cross+checks` | 8.5% | 73.7% |
| `cross-replicate` | 8.9% | 62.2% |

Four in five of the self-arm's flags are wrong. Roughly one in four of the shipped
configuration's are.

---

## The three preregistered comparisons

All paired on the identical instances. McNemar exact (binomial on the discordant pairs);
95% intervals from a seeded paired bootstrap, 10,000 resamples.

### 1. `cross+checks` − `checks` — the audit's marginal value

| | on P (recall) | on C (false positives) |
|---|---|---|
| difference | **+8.9 points** | +2.7 points |
| n | 56 | 150 |
| discordant | 5 vs 0 | 4 vs 0 |
| exact p | **0.0625** | 0.125 |
| 95% CI | **[1.8%, 17.9%]** | [0.7%, 5.3%] |

**This is the number the study exists for.** Adding a cross-vendor reader on top of the test
run finds about **one in eleven** of the defects the tests cannot see, and mislabels about
**one in thirty-seven** correct solutions. p = 0.0625 is the smallest two-sided value
5-versus-0 discordant pairs can produce; the effect is real in sign and small in size, and
its lower interval bound (+1.8 points) is above the noise floor measured below.

### 2. `cross` − `self` — does a different vendor beat the model grading itself?

| | on P (recall) | on C (false positives) |
|---|---|---|
| difference | −5.4 points (self higher) | **−15.3 points (self worse)** |
| n | 56 | 150 |
| discordant | 6 self-only vs 3 cross-only | — |
| exact p | 0.51 | **0.000066** |
| 95% CI | [−16.1%, 5.4%] | [−22.7%, −8.7%] |

**On recall, cross does not beat self, and the difference is inside the noise floor.** On
false positives it is not close. The honest statement is not "cross-vendor finds more" — it
is "cross-vendor finds a comparable amount and is four times as likely to be right when it
speaks". Note that the product **refuses to run the `self` configuration at all**
(`run_audit` denies a same-vendor generator/auditor pair); this arm exists only because the
study bypassed that gate, and the false-positive column is the strongest evidence in this
repository that the gate is earning its keep.

### 3. `cross+checks` − `cross` — what the deterministic layer adds to the model

| | on P | on C |
|---|---|---|
| difference | −1.8 points | −2.0 points |
| n | 56 | 150 |
| exact p | 1.0 | 0.25 |
| 95% CI | [−8.9%, 5.4%] | [−4.7%, 0.0%] |

On P — where the visible tests pass — showing the auditor a passing test result changes
nothing measurable, as it should, and the small negative sign is inside the noise floor.
On stratum F it is the whole story (79.3% → 100%). The deterministic layer's value is
concentrated exactly where it can act, which is the correct shape for it to have.

### The noise floor

`cross`, run a second time over the identical 235 instances with everything else fixed:

| population | absolute difference between the two runs | disagreements | n |
|---|---:|---:|---:|
| P | 1.8 points | 3 | 56 |
| C | 0.7 points | 7 | 150 |

**A difference smaller than about 2 points on P is not a finding in this study.** That
disqualifies comparison 3 (1.8 points) and the recall half of comparison 2 (5.4 points is
larger, but its interval spans zero). It does not disqualify comparison 1, whose 8.9 points
is roughly five times the floor.

### Comparison count

Six preregistered comparisons (three arm pairs × two populations), plus the two noise-floor
comparisons. The primary outcome was named in the preregistration before any model was
called and is not one of the six. Every other number in this file is descriptive.

---

## Exploratory — do the flags name the actual bug?

**Labelled exploratory: this was not preregistered, it was done after the scores were seen,
and the adjudication is the author's own rather than blind.** The preregistered flag counts
any BLOCKER on a defective instance, so recall as reported is an **upper bound** — a flag
about an unrelated matter still counts.

Re-running the `cross+checks` audit on its five stratum-P flags, three reproduced (which is
consistent with the noise floor above) and the observation text of all three names the
defect the hidden tests actually catch:

- `HumanEval/125` — "the implementation only detects the literal space character … inputs
  containing other whitespace such as tabs or newlines are not split as required". The
  hidden suite fails 70 of 811 inputs on exactly that.
- `HumanEval/76` — "`is_simple_power(4, -2)` returns False … although `(-2)**2 == 4`".
  4 of 904 hidden inputs.
- `Mbpp/759` — "the docstring states … 'Optional digits before the decimal point', but the
  implementation returns False when `integer_part == ''`". 7 of 114.

So the qualitative picture is the opposite of a false-positive problem on this population:
**when the shipped configuration fires on a "looks right, is wrong" solution, it appears to
be naming the real defect, in reviewable prose. It just does not fire often.** The binding
constraint in code, as on prose, is recall.

---

## What it cost

From the product's own usage ledger, not reconstructed.

| arm | spend | calls | input / output tokens |
|---|---:|---:|---|
| generation (540 solutions) | $0.7107 | 540 | 111,606 / 119,809 |
| `cross+checks` | $1.6410 | 235 | 398,739 / 42,913 |
| `cross` | $1.7759 | 235 | 392,657 / 52,949 |
| `cross-replicate` | $1.7120 | 235 | 391,228 / 48,903 |
| `self` | $1.1856 | 443 | 826,598 / 71,791 |
| `checks`, `none` | $0.0000 | 0 | — |
| exploratory re-read (5 audits) | ~$0.05 | 5 | — |
| **total** | **$7.08** | 1,693 | |

Per instance: `cross+checks` $0.0070, `cross` $0.0076, `self` $0.0027 (the `self` arm's 443
calls include 196 duplicates from a harness fault — see deviation 6 — so its per-instance
figure is computed over the 235 that were kept). Scoring is free: the hidden tests cost
nothing to run and 540 solutions were scored on both suites in 40 seconds.

**Reading the whole 540-solution corpus in the shipped configuration would cost about
$3.80.** That is the price of finding roughly one in eleven of the defects the tests miss.

---

## Deviations from the plan, numbered, with the direction of each bias

1. **Four probe audits before the freeze**, on a hand-written wrong solution to
   `HumanEval/0`, to measure per-call cost and prove the plumbing. They produce no study
   number and are not in any arm's record. No bias.
2. **The generator's first pass hit provider rate limits.** 190 of 540 calls returned
   `ProviderDenial: … cooling down` when running 6-way concurrent. Rows whose call failed
   were dropped and the frozen `generate.py` was re-invoked (it resumes by problem id) from
   a shell driver outside the frozen code, at concurrency 1 with 75-second waits. **No
   study parameter changed.** The circuit breaker is per-route and global, so which problems
   failed is independent of their content; no bias is expected in either direction.
3. **The auditor arms hit repeated `SSL: UNEXPECTED_EOF_WHILE_READING` failures** through
   the local proxy, which tripped the same breaker. Handled the same way, with the same
   argument. Two other studies were running against the same credentials throughout.
4. **`cross` reached 235/235 only after retries**; an earlier interim read of this arm at
   205/235 showed 11.8% recall on 51 usable P instances against the final 10.7% on 56. The
   final figure is the one reported; the interim is disclosed because it was seen.
5. **The `self` arm bypasses a product guarantee.** `run_audit` raises `ConfigDenial` on a
   same-vendor generator/auditor pair. The arm was obtained by leaving `generator:` unset in
   its project config. This is a deliberate bypass for measurement, and it is the only arm
   that could not be run as a customer would run it.
6. **The `self` arm double-ran.** A backgrounded retry driver and a foreground invocation
   overlapped, producing 413 rows over 217 distinct problems. Duplicates were resolved by a
   rule fixed before the rows were inspected: **keep the first occurrence per problem id**.
   The 196 duplicate calls cost about $0.53 and are included in the total. Because the
   keep-first rule is independent of the outcome, no bias in either direction; had the rule
   been "keep the flag" or "keep the pass" it would have been.
7. **The `visible_tests` deterministic check is study-supplied.** CrossAudit's `general`
   profile checks that files parse, that declared paths exist, that links resolve and that
   no placeholder is left; it ships **no** test-runner check. A code project would supply
   one, and this is that check, registered through the product's own DCL registry. Because
   it is registered directly rather than through the `plugins:` entry-point mechanism, its
   source is **not** covered by `dcl_source_digest`. Its behaviour is trivial (report the
   already-computed visible result as a BLOCKER when the suite fails), and it produced
   exactly 29 findings — one per stratum-F instance, and none anywhere else, which is the
   only behaviour it can correctly have.
8. **Every model arm sees the visible test source in the increment**, not only the two
   `checks` arms. The single manipulated variable is therefore whether the suite's
   *execution result* is in the prompt, not whether the tests exist. This makes `cross`
   stronger than the brief's description of it, which biases comparison 3
   (`cross+checks` − `cross`) **downward**; it does not affect the primary comparison
   (`cross+checks` − `checks`), where the deterministic result is the only difference.
9. **The generator is a small model, chosen before any score** so that stratum P would be
   large enough to measure. A small model's wrong-but-plausible code is plausibly more
   obviously wrong than a frontier model's, which biases the reported recall **upward** —
   that is, the true figure for frontier-generated code is more likely below 8.9% than
   above it. This is the single largest threat to the headline and it points against the
   product.
10. **Two problems excluded** (`HumanEval/32`, `Mbpp/590`) before generation, by name, for
    the reason given above. Both are stratum-P-shaped, so excluding them slightly *reduces*
    the primary population; it cannot inflate recall.
11. **Temperature and seed are not controllable.** CrossAudit's provider layer takes
    temperature from the model's capability card and exposes no seed, so a re-run will not
    reproduce byte-identically. The `cross-replicate` arm exists precisely to quantify what
    that costs: 3 disagreements in 56 on P.
12. **The audit set is stratified, not a simple random sample.** Raw precision and flag rate
    on it are biased by design; both are reported reweighted, with the weights stated.
    Recall on P and the false-positive rate on C are unbiased within their strata and are
    reported raw.
13. **One post-run edit to frozen code**, after scores were seen: `report.py`'s final
    `print` of the cost table expected a float and received a dict, crashing *after* every
    statistic had been computed and printed. The fix touches that one display line and
    changes no number. It is recorded here rather than quietly amended.
14. **`cross-replicate` was run as `--arm cross` into a separate output file**, since
    `audit.py`'s arm list is frozen and does not contain that name. Its rows therefore carry
    `"arm": "cross"`; the report keys the arm off the file name. Same code path, same
    configuration, different run id and project.

## Limitations, stated here rather than left to the reader

- **A model-judged ground truth is not ground truth, and this study has none.** Recall,
  precision, the false-positive rate and the stratum assignment are all decided by test
  execution. The only model outputs in the measurement are the audits being measured.
  Studies 1–3 cannot say this: every number in them rests on CLEAR, a reimplementation of a
  paper whose authors released no evaluation code, whose mapper and judge were substituted,
  and whose only external validation is that it puts frontier models in roughly the band
  the paper puts them in.
- **Two Python benchmarks of short, self-contained functions are not a repository.** These
  problems have no build, no dependencies, no cross-file invariants, no history and no
  reviewers. The defects a real code auditor must catch — a race, a migration that drops a
  column, an API contract broken three files away — are not in this corpus at all. This
  study says what the audit does on unit-sized pure functions and nothing beyond that.
- **One generator.** A finding about `claude-haiku-4-5`'s errors is a finding about that
  model's errors.
- **Vendor independence is not statistical independence.** `gpt-5.6-terra` and
  `claude-haiku-4-5` share training data, architecture and human-feedback conventions.
  Cross-vendor reduces correlated error; it does not create an independent oracle, and the
  8.9% must not be read as if it did.
- **Round one only.** Whether revision then improves the code is a separate question, and
  study 3 found that on prose revision made things measurably worse.
- **`p = 0.0625` on 5-versus-0 discordant pairs is the floor of what McNemar can return
  at that sample size**, not a marginal result that a few more instances would settle
  either way. It means the sign is reliable and the magnitude is not yet pinned down.

## What this run does and does not license

**It does not license** the claim that code is the domain where CrossAudit's audit works.
Recall on the population the product's claim is about is 8.9%, inside the prose band. The
hypothesis this study was built to test came out false.

**It does not license** the claim that the audit is worthless in code either. +8.9 points
over the visible tests, at 2.7% false positives on correct work, is a real effect above the
noise floor, and the exploratory read of the findings suggests that when it fires it is
naming the actual bug in language a reviewer can check.

**It does license** three concrete statements about the product:

1. **The deterministic layer is where the certainty is.** `checks` has 100% precision and
   catches 100% of stratum F. `cross` alone misses a fifth of code that does not even run;
   shown the test result it misses none.
2. **The same-vendor refusal is earning its keep.** Self-audit flags 20% of correct
   solutions — 4× cross-vendor — for recall that is not distinguishably better.
3. **The binding constraint in code is recall, and it is the same constraint as on prose.**
   Study 2 named the constitution as the cause on prose and study 3 fixed it there. In code
   the auditor already has the acceptance criteria — `CA-TASK-001` grades the solution
   against the problem's own specification, which is what four of the five stratum-P flags
   cited — and recall is still under 10%. **The constitution was not the whole story.**

**Do not re-run this study hoping for a different number.** If the configuration changes,
the study restarts and says so here.

---

## Reproduction

```sh
export PYTHONPATH="$(git rev-parse --show-toplevel)/src"
# credentials: CROSSAUDIT_ANTHROPIC_KEY and CROSSAUDIT_OPENAI_KEY, or the role fallbacks
python benchmarks/code/fetch.py                       # ~1 min; corpus is not committed
python benchmarks/code/evaluate.py --canonical --out runs/canonical.jsonl   # harness check
python benchmarks/code/generate.py --project <a crossaudit project> \
    --out runs/study1/solutions.jsonl --exclude "HumanEval/32,Mbpp/590" --run-id code-gen-1
python benchmarks/code/evaluate.py --solutions runs/study1/solutions.jsonl \
    --out runs/study1/scored.jsonl
python benchmarks/code/plan.py --run runs/study1
for arm in cross+checks checks none cross self; do
  python benchmarks/code/audit.py --arm "$arm" --scored runs/study1/scored.jsonl \
    --solutions runs/study1/solutions.jsonl --audit-set runs/study1/audit_set.json \
    --out "runs/study1/arm-$arm.jsonl" --scratch /tmp/arms --run-id "code-$arm-1"
done
python benchmarks/code/report.py --run runs/study1
```

It will not reproduce byte-identically (deviation 11). The `cross-replicate` arm measures
how much that matters: 3 flags of 56 changed.

The committed record is `benchmarks/code/records/study1/` — one JSONL row per instance per
arm, with outcome vectors, verdicts, rule ids, finding hashes, tokens, cost and time, and
no corpus text, no generated code and no prompt that embeds either. The full run directory,
which does contain those, stays on disk at
`benchmarks/code/runs/study1/` and is gitignored.
