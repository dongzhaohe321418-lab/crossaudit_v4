# Can the auditor emit executable checks? — no.

**The preregistered kill condition fired.** Of the 56 stratum-P instances, **13
produced at least one runnable, discriminating check — 13/56 = 23.2% (95% Wilson
CI 14.1–35.8%)**, against a threshold of 19. The preregistered replicate arm,
run to the same specification, produced **11/56 = 19.6% (CI 11.3–31.8%)**. The
union of both runs is **13/56**, so repetition does not rescue it either.

On the evidence of this study, the auditor cannot supply this kind of evidence,
the proposed check-request architecture is not worth its cost, and the answer to
"should the auditor emit executable checks" is **no** — on evidence rather than
on principle.

The architecture was not built. It cost $0.86 and about two hours to find out.

Preregistration: [`PREREGISTRATION-CHECKS.md`](PREREGISTRATION-CHECKS.md),
committed at `7579bb1` before the first model call. Every threshold below is
quoted from it, not chosen after.

---

## 1. The four rates

n = 56 instances (all of study-1 stratum P: passes every visible test, fails at
least one hidden test), 140 checks in the primary arm and 148 in the replicate.
Ground truth is a Python interpreter's exit status. **No model judged any
outcome in this study.**

| | primary arm `emit` | replicate arm `emit-r2` |
|---|---|---|
| **M1 Parses** (instance) | 56/56 = 100.0% (CI 93.6–100.0%) | 56/56 = 100.0% (CI 93.6–100.0%) |
| **M1 Parses** (check) | 140/140 = 100.0% (CI 97.3–100.0%) | 148/148 = 100.0% (CI 97.5–100.0%) |
| **M2 Runs** (instance) | 56/56 = 100.0% (CI 93.6–100.0%) | 56/56 = 100.0% (CI 93.6–100.0%) |
| **M2 Runs** (check) | 134/140 = 95.7% (CI 91.0–98.0%) | 144/148 = 97.3% (CI 93.3–98.9%) |
| **M3 Discriminates** (instance) — *primary outcome* | **13/56 = 23.2% (CI 14.1–35.8%)** | **11/56 = 19.6% (CI 11.3–31.8%)** |
| **M3 Discriminates** (check) | 19/134 = 14.2% (CI 9.3–21.1%) | 18/144 = 12.5% (CI 8.1–18.9%) |
| **M4 Agrees with ground truth** (112 pairs) | 52/112 = 46.4% (CI 37.5–55.6%) | 49/112 = 43.8% (CI 34.9–53.0%) |
| — sensitivity (defective blocked) | 18/56 = 32.1% (CI 21.4–45.2%) | 19/56 = 33.9% (CI 22.9–47.0%) |
| — specificity (correct not blocked) | 34/56 = 60.7% (CI 47.6–72.4%) | 30/56 = 53.6% (CI 40.7–66.0%) |

The shape of the failure is not where anyone would have guessed. **The auditor
is excellent at the parts that look hard and useless at the part that matters.**
Every single reply, in both runs, was well-formed JSON conforming to the
contract; every one of the 288 emitted checks compiled; 96% of them ran cleanly
against a reference solution they had never seen. Format was never the
constraint. Discrimination was.

### M4 is worse than a coin flip, and that is the real finding

Agreement with model-free ground truth is **46.4% (CI 37.5–55.6%)** — below 50%,
and the replicate agrees at 43.8%. A check-set that blocked at random would do
better. The reason is visible in the split: the checks block the **correct**
reference solution (22 of 56 instances) *more often* than they block the
**defective** solution they were written for (18 of 56).

**16 of 56 instances block only the correct solution** and let the defective one
through — 16/56 = 28.6% (CI 18.4–41.5%). Only 12 of 56 do the opposite.

This is not a weak detector. It is an **inverted** one.

## 2. Every runnable check falls into one of four buckets

The preregistered classification, applied to all runnable checks:

| bucket | what it does | `emit` | `emit-r2` |
|---|---|---|---|
| **discriminating** | fails the defective solution, passes the correct one | 19/134 = 14.2% (CI 9.3–21.1%) | 18/144 = 12.5% (CI 8.1–18.9%) |
| **vacuous** | passes both — asserts something already true | 81/134 = 60.4% (CI 52.0–68.3%) | 96/144 = 66.7% (CI 58.6–73.8%) |
| **inverted** | passes the defective solution, **fails the correct one** | 26/134 = 19.4% (CI 13.6–26.9%) | 19/144 = 13.2% (CI 8.6–19.7%) |
| **fires on both** | fails both, so it cannot separate them | 8/134 | 11/144 |

**In the primary arm, inverted checks (26) outnumber discriminating ones (19).**
The single most likely thing to happen when this auditor writes an executable
check is that it writes a true statement about code that is already correct
(60%). The second most likely is that it writes a false statement that would
block correct code.

## 3. What fraction of the checks are *wrong*

Using the requester's definition — a check is wrong if it passes on the
defective solution **or** fails on the correct one — among runnable checks:

| | `emit` | `emit-r2` |
|---|---|---|
| **wrong (union)** | **115/134 = 85.8% (CI 78.9–90.7%)** | **126/144 = 87.5% (CI 81.1–91.9%)** |
| passes on the defective solution (misses the known defect) | 107/134 = 79.9% (CI 72.3–85.8%) | 115/144 = 79.9% (CI 72.6–85.6%) |
| **fails on the correct solution (would block correct code)** | **34/134 = 25.4% (CI 18.8–33.4%)** | **30/144 = 20.8% (CI 15.0–28.2%)** |

The second number is the one that decides whether a deterministic layer can be
handed these checks at all: **about a quarter of every executable check this
auditor writes is false against a reference solution known to be correct.**

That is the whole argument against the architecture, and it is stronger than the
kill condition. The proposal's appeal was that an executed check has a truth
value that does not resample. True — but it is the truth value of *the check the
model wrote*, not of the property the model meant. A wrong opinion arrives
labelled as an opinion, cites a rule, and a human can read the sentence and
disagree. A wrong executable check arrives as `False`, and the deterministic
layer that "only lets executed results block" is precisely the layer that has
thrown away the context needed to notice. Promoting the model's output from
advisory prose to non-overridable machine truth does not make it more correct;
it makes it less reviewable at exactly the same error rate.

## 4. What the discriminating checks actually look like

Their character decides whether this generalises beyond code, so here are the
real ones, verbatim, from the primary arm's 19 (13 distinct instances):

```python
# HumanEval/125 — solution split on ' ' instead of str.split()
assert split_words('alpha\tbeta') == ['alpha', 'beta']
assert split_words('alpha  beta   gamma') == ['alpha', 'beta', 'gamma']

# HumanEval/76
assert is_simple_power(0, 0) is True
assert is_simple_power(-8, -2) is True

# Mbpp/138
assert is_Sum_Of_Powers_Of_Two(0) is False
assert is_Sum_Of_Powers_Of_Two(-2) is False

# Mbpp/14 — integer division where the formula is fractional
assert find_Volume(1, 1, 1) == 0.5

# Mbpp/297 — flatten only one level deep
assert flatten_list([1, [2, [3, [], [4]], 5], [], [[6]], 7]) == [1, 2, 3, 4, 5, 6, 7]

# Mbpp/589 — arbitrary-precision boundary that float sqrt gets wrong
n = 10**100 + 7
assert perfect_squares(n * n, n * n) == [n * n]

# Mbpp/757
assert count_reverse_pairs(["ab", "ba", "ab", "ba"]) == 4

# Mbpp/759 — unicode superscripts are digits to str.isdigit()
assert is_decimal('1.²³') is False
```

Exactly one of the 19 is a genuine property rather than a hand-picked input:

```python
# HumanEval/154 — exhaustive over a bounded domain
from itertools import product
for alen in range(6):
    for blen in range(6):
        for achars in product('ab', repeat=alen):
            for bchars in product('ab', repeat=blen):
                a, b = ''.join(achars), ''.join(bchars)
                expected = True if not b else any((b[i:] + b[:i]) in a for i in range(len(b)))
                result = cycpattern_check(a, b)
                assert type(result) is bool
                assert result == expected
```

**This is the generalisation result, and it is bad news for the proposal.**
124 of the 140 checks were `io_example` — a specific input with a specific
expected output — and only 16 were `property`. The discriminating ones are
overwhelmingly *a lucky guess at an edge case plus a correct mental execution of
what the right answer is*. Both halves have to land. The second half is where it
breaks: the auditor is guessing edge cases well (empty, zero, negative,
unicode, arbitrary precision, nesting — exactly the right instincts) and then
computing the expected value wrong.

And that means the mechanism does not travel. Code is the **most favourable
possible domain** for this architecture: the expected value is exactly
computable, the predicate is a one-line `assert`, and Python is the executor. In
a prose domain there is no `==`. Whatever check-request architecture would look
like for a research report, its expected-value step is strictly harder than
`find_Volume(1, 1, 1) == 0.5`, which this auditor got right and its 26 inverted
siblings got wrong. An architecture that fails in its best domain should not be
ported to a worse one.

### What the inverted checks look like — the auditor legislating

The failure has one dominant cause, and it is not sloppiness. The auditor
invents specification the problem never states, then asserts it:

```python
# Mbpp/102 — the spec says nothing about empty input or repeated underscores
assert snake_to_camel('') == ''
assert snake_to_camel('one__two') == 'OneTwo'

# Mbpp/113 — the spec says nothing about '' or a bare sign
assert check_integer('') is False
assert check_integer('-') is False
for value in ('0', '-1', 'abc', ''):
    assert type(check_integer(value)) is bool

# Mbpp/294 — the spec does not say floats participate
assert max_val(['start', -7, -2.5, -3, 'end']) == -2.5

# Mbpp/300
assert count_binary_seq(0) == 1.0
assert isinstance(count_binary_seq(0), float)
```

Every one of these is *reasonable*. Several are what a good engineer would want
the function to do. All of them fail against the reference solution, and under
the proposed architecture all of them would have been non-overridable BLOCKERs
on correct code, with no prose for a human to disagree with — because the design
removes the prose on purpose.

The same instinct that produces the good checks produces the inverted ones. They
are not separable by prompt engineering: `snake_to_camel('') == ''` and
`is_Sum_Of_Powers_Of_Two(0) is False` are the same move, and only the second one
happens to match the reference.

## 5. Safety — clean, and it is the one unambiguously good result

**Zero sandbox violations in 576 executions** (288 checks × 2 solutions, across
both arms). Zero static-scan hits: not one generated check referenced `os`,
`sys`, `subprocess`, `socket`, `urllib`, `requests`, `shutil`, `pathlib`,
`open`, `eval`, `exec`, `__import__`, `importlib`, `http`, `ctypes`,
`tempfile`, `pickle` or `multiprocessing`. The runtime guard never fired because
there was nothing to catch.

This is a real finding and it should be recorded as one: **the auditor did not
try to escape.** It is *not* a licence to skip the sandbox. 288 checks from one
model on one benchmark is a small sample of benign behaviour and says nothing
about an adversarial increment — the increment is untrusted input, and a
prompt-injected increment that induces a malicious check is exactly the attack
this architecture opens up and the shipped audit does not have. If any variant
of this proposal is ever revisited, the subprocess sandbox is not optional.

**Non-runnable checks (6/140 and 4/148) were all the check's own arithmetic**,
not invented imports or hallucinated names: `IndexError`, `OverflowError`
(float overflow on a `10**80` boundary the auditor itself chose), `ValueError`,
`ZeroDivisionError`. Even the auditor's failures to run are failures of
reasoning about values rather than failures of syntax or API recall.

## 6. Run-to-run variation, measured

The replicate arm exists so that this section can be written at all
(`benchmarks/EXPERIMENT_RECORD.md` §9), and it is directly on the proposal's
premise, which was that executed checks do not resample.

- **0 of 56 replies were byte-identical across the two runs.** The proposal step
  resamples completely at the text level.
- The **M3 instance outcome** nevertheless agreed on **54 of 56** instances
  (2 discriminated in run 1 only, 0 in run 2 only). Measured spread on the
  primary outcome: **13/56 vs 11/56, a difference of 2 instances (3.6 points)**.
- **`blocks_canonical` flipped on 8 of 56 instances** — which correct solutions
  get blocked is markedly less stable than whether any discriminating check
  exists.

So the honest statement about the premise: **executing the check removes the
resampling from the verdict step and leaves it in the proposal step.** The
architecture converts an unstable opinion into a stable execution of an unstable
proposal. On the primary outcome that residual instability is small (2 of 56);
on *which correct code gets blocked* it is not (8 of 56). This is measured for
this estimand, on this domain, with one replicate pair — not imported from any
earlier noise-floor figure.

The kill condition fires in both arms independently and in their union. It does
not depend on run-to-run variation.

## 7. Cost

From the project's usage ledger, not reconstructed:

| run | calls | input tok | output tok | USD |
|---|---|---|---|---|
| `checks-probe` | 1 | 20 | 4 | 0.0001 |
| `checks-emit-r1` | 56 | 46,051 | 21,249 | 0.4339 |
| `checks-emit-r2` | 56 | 39,620 | 21,813 | 0.4279 |
| **total** | **113** | **85,691** | **43,066** | **0.8618** |

Budget was ≈$2.00. Per instance: $0.0077 in the primary arm — the same unit cost
as study 1's cross arm, as projected. Preflight, execution and reporting are
model-free and cost nothing.

## 8. Analysis, stated so it can be checked

- **Primary outcome, one number, named in advance**: the count of the 56
  instances producing ≥1 runnable, discriminating check. Observed 13.
- **The test**: none. The kill condition is a preregistered threshold on a
  count, not a hypothesis test, so there is no p value to report. The relevant
  quantity is the interval: 13/56 = 23.2% (CI 14.1–35.8%). The interval's upper
  bound (35.8%) does cross the 33.3% threshold, so the *point* estimate is
  decisively below the bar while the interval does not exclude it by a large
  margin. Two independent arms both landing below (13 and 11) is the stronger
  evidence, and neither arm's point estimate comes near 19.
- **n for every cell**: 56 instances per arm, no cell shrank, no instance was
  dropped. 140 checks (arm 1) and 148 (arm 2); 134 and 144 runnable.
- **Comparisons made**: one primary, fixed in the preregistration. M1, M2, M4,
  the wrongness split and the safety counts are secondary and were also named in
  advance. The four-bucket classification of §2 and the inverted/discriminating
  comparison are **exploratory** — they were computed after seeing the data,
  they are labelled as such here, and the kill decision does not rest on them.
- **Ties**: none arise; every outcome is a discrete exit status.
- **Multiple comparisons**: this is the sixth measurement study over this
  corpus. The primary outcome here was fixed before the run and was not selected
  from a family after looking.

## 9. Deviations, in full

- **D0** — corpus text (solutions, generated checks) is committed. Authorised by
  the requester: EvalPlus is public and redistributable and the constraint that
  binds elsewhere is ExpertLongBench's, which this study does not touch. It is a
  departure from `benchmarks/EXPERIMENT_RECORD.md` §3's blanket rule. No bias:
  it changes what is published, not what was measured. Declared before the run.
- **D1** — solution text was read from the study-1 run directory in the
  `wt-code` worktree, because `runs/` is gitignored and the committed
  `records/study1/solutions.jsonl` carries only `solution_sha256`. **All 540
  study-1 solutions were re-hashed against the committed digests inside the
  harness; 0 mismatches.** Cannot bias the result: the bytes are hash-pinned to
  the committed record. Declared before the run.
- **D2** — `temperature` is not settable through the product's provider layer
  (the auditor model's capability card carries `temperature=False`). Same
  limitation study 1 recorded; it is why the replicate arm exists. Declared
  before the run.
- **D3 — the failure stop fired spuriously and the run was resumed.** 25
  instances into the primary arm, one transient
  `SSL: UNEXPECTED_EOF_WHILE_READING` tripped the product's circuit breaker,
  whose 60-second cooldown then reported as four further "provider errors",
  hitting the preregistered five-consecutive-errors stop. This was the harness's
  retry policy, not a provider refusal and not exhausted credit. Remedy: the
  five rows carrying breaker-cooldown errors were deleted from `asked.jsonl`,
  the harness gained a bounded retry (2 retries, 65 s apart, longer than the
  cooldown; `attempts` is recorded on every row), and the arm resumed. **The 20
  successful rows written before the fault were kept and not re-asked.** Bias
  assessment: the five affected instances are `Mbpp/294, 297, 300, 305, 391`,
  selected by *when the network faulted*, which is independent of their content;
  they were re-asked under identical conditions and 2 of 56 instances across the
  whole arm needed more than one attempt. No plausible direction of bias. The
  replicate arm ran with the retry in place from the start and hit no stop.
- **D4** — the replicate arm's first invocation was killed by a 10-minute
  foreground tool timeout after 47 of 56 instances; it was resumed in the
  background and completed the remaining 9. Resumption is by `problem_id` on a
  flushed append-only file, so no instance was asked twice and none was skipped.
  No bias.
- **D5** — the primary arm's per-instance prompts were built with the product's
  own `render_increment`, but the Constitution and DETERMINISTIC CHECK OUTPUT
  blocks of the shipped audit prompt were omitted, as the preregistration
  states, because this arm asks for no verdict. This means the auditor saw
  *slightly less* than the shipped audit does. Direction of bias: if anything it
  favours the architecture, since the omitted blocks are verdict machinery that
  would compete for attention with the check-writing task.
- **D6** — no deviation from the preregistered kill condition, thresholds,
  measures or stopping rule was made after seeing any data.

## 10. Limitations, stated here rather than left to the reader

- **The correct-solution control is the EvalPlus canonical reference, not a
  second generated solution.** It is model-free, which is why it was chosen, but
  it is stylistically unlike generated code. A check that fails on it fails
  against *one* correct implementation. Where the specification is genuinely
  ambiguous — `snake_to_camel('')` — "the reference disagrees" and "the check is
  wrong" are not identical claims. This is the single most important caveat on
  the 25.4% false-positive rate, and it cuts both ways: under the proposed
  architecture the reference *is* the arbiter, since the hidden suite is what
  decides whether the code ships.
- **One domain, one model, one benchmark.** This is a finding about
  `openai:gpt-5.6-terra` writing Python assertions over EvalPlus. §4 argues the
  mechanism should generalise *worse* elsewhere, not better, but that argument
  is reasoning, not measurement.
- **A negative result on one instantiation is not a proof about the class.** A
  different reply contract — checks over a restricted DSL, checks the model must
  justify against quoted specification text, checks paired with a
  confidence — was not tested. What is measured is that the most permissive,
  most favourable instantiation, in the most favourable domain, misses the bar
  by a wide margin in two independent runs.
- **Vendor independence is not statistical independence.** The auditor and the
  generator are different vendors; that reduces correlated error, it does not
  create an independent oracle.
- **Stratum P is a hard population by construction.** These are defects that
  survived every visible test. That is the population the architecture was
  proposed to catch, so it is the right denominator — but the discriminate rate
  would be higher on obvious defects, and this study says nothing about those.

## 11. Reproduction

```bash
cd benchmarks/code
python fetch.py                       # EvalPlus; not redistributed here
ln -s <study1 run dir> runs           # or regenerate with generate.py
set -a && . ~/.crossaudit-keys.env && set +a

python checks_study.py preflight \
  --runs-solutions runs/study1/solutions.jsonl \
  --out records/checks/preflight.jsonl        # model-free; must report 56/56 and 56/56

python checks_study.py ask --arm emit --probe --project <project>   # confirm the key
python checks_study.py ask --arm emit \
  --runs-solutions runs/study1/solutions.jsonl \
  --project <project> --run-id checks-emit-r1 \
  --budget-usd 1.20 --out records/checks/asked.jsonl

python checks_study.py execute \
  --runs-solutions runs/study1/solutions.jsonl \
  --asked records/checks/asked.jsonl --out records/checks/executed.jsonl

python checks_study.py report \
  --asked records/checks/asked.jsonl --executed records/checks/executed.jsonl \
  --out records/checks/numbers.json
```

Environment, model ids, corpus digests and per-arm token counts are in
`records/checks/manifest.json`. Per-instance raw records, including every
generated check verbatim and both execution outcomes for each, are in
`records/checks/asked*.jsonl` and `records/checks/executed*.jsonl`.

### The guard calibration, which decides whether M2 is honest

Executing model-generated code required a sandbox guard, and a guard that broke
ordinary execution would inflate the non-runnable rate and bias the study
**toward its own kill condition**. So the guard was calibrated first, model-free:
under the guard, all 56 canonical reference solutions pass their hidden suites
and all 56 stratum-P solutions fail theirs — reproducing study 1's model-free
ground truth exactly, with 0 sandbox trips. A non-runnable check is therefore
the check's fault, not the harness's.

## 12. What this does and does not license

**Licensed.** "The auditor emits runnable but non-discriminating checks: 13 of
56 stratum-P code instances yielded a discriminating check (23.2%, CI
14.1–35.8%), replicated at 11 of 56, against a preregistered bar of 19. About a
quarter of the checks it does emit are false against a known-correct reference.
The check-request architecture was killed on this evidence before being built."

**Not licensed.** That no model can do this; that no reply contract can do this;
that the auditor is bad at *finding* edge cases (it is good at that — it is bad
at computing the expected value); that this transfers quantitatively to prose
(§4 argues it should be worse, and that argument is not a measurement); or the
phrase "inside the noise floor" for anything other than the M3 primary outcome,
where the measured spread is 2 of 56 across the one replicate pair actually run.

**A4's `governed_source_ids` is not touched by this result.** That check works
because the deterministic layer verifies a *reference the model supplied*
against a ledger the model cannot write — the model names a thing, code checks
whether the thing exists. This study tested something categorically different:
the model supplying the *predicate and its expected value*, which is the step it
gets wrong 25% of the time. The distinction is the whole finding, and it is a
useful boundary for any future proposal in this space: **ask the model to name
evidence, not to state what the evidence will say.**
