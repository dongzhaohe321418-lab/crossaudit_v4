# Preregistration — can the auditor emit executable checks?

Written and committed **before any model call**. Study id: `checks-emit`.
Frozen against branch `fusion/evidence-authority`.

## 0. Why this exists

Every audit architecture measured in this project so far slides along one ROC
curve, because every one of them is the same kind of evidence: a model reads
text and has an opinion. Decomposition bought +9.1 recall for +8.0 false
positives. Repetition (union of two identical runs, code domain, model-free
ground truth) bought +2.4 recall for +2.3 false positives. Two-stage filtering
cut recall to 3.6% to remove 1.3 points of false positives. And the opinion does
not hold still: re-running the identical audit over the identical commit changes
the BLOCKED/PASS verdict on 6 of 20 instances (D154, `docs/DECISIONS.md`).

A proposed architecture changes the *kind* of evidence rather than its quantity:
the auditor emits declarative **check requests**, the deterministic layer
executes them, and only an executed result may block. An executed check has a
truth value that does not resample. The rung structure is unchanged — the model
proposes, code decides — and the project already ships one instance of it (A4's
`governed_source_ids` with `check_source_provenance`).

**This experiment does not build that architecture. It exists to kill it before
anyone does**, by testing its one load-bearing premise.

## 1. Hypothesis

**H1 (the premise under test).** Given the problem specification and the
solution — exactly what the shipped audit sees — the product's auditor model can
write check requests that are syntactically valid, run without erroring for
reasons of their own making, and *discriminate*: fail on a defective solution
and pass on a correct one for the same problem.

**H0.** It cannot, at a rate that would justify the architecture's cost.

The hypothesis can come out false, and the kill condition in §6 says exactly how.

## 2. Population and n

**n = 56.** The stratum-P solutions of study 1: every generated solution that
passes every *visible* test and fails at least one *hidden* test. They are the
only population where a defect is established without a model — a Python
interpreter raised `AssertionError` on a hidden input, or it did not.

- Source: `benchmarks/code/records/study1/scored.jsonl` (`stratum == "P"`), with
  solution text from the run directory whose `solution_sha256` matches the
  committed record for all 540 rows (verified before this file was written).
- Composition: 50 MBPP+, 6 HumanEval+.
- Nothing is re-generated. n is the whole stratum, not a sample, so there is no
  selection step and no seed for one.

**The correct-solution control** for each of the 56 is that problem's
**canonical reference solution** from EvalPlus (`canonical_solution` for
HumanEval, `code` + `test_imports` for MBPP). It is model-free, and study 1
already established that 540 of 542 references pass both suites in this harness
(the 2 that do not are excluded from the corpus and are not in stratum P).

## 3. The single arm

One arm, `emit`. Auditor model **`openai:gpt-5.6-terra`** — the cross-vendor
auditor of study 1, i.e. the model the product's real audit uses. Routed through
the product's own provider layer (`resilience.complete`), so the call is metered
in the project's usage ledger like any other.

Held fixed and identical to the shipped audit:

- the **task** shown is `Problem.spec`, verbatim;
- the **increment** is rendered by the product's own
  `crossaudit.auditor.prompt.render_increment` over the exact same two files the
  shipped audit's `increment_files()` builds: `work/solution/solution.py` and
  `work/solution/tests_visible.py`;
- the hidden suite never reaches any prompt. It is the ground truth and is read
  only by `execute.py`.

Varied, and this is the whole experiment:

- the system prompt asks for **check requests only** — no verdict, no finding,
  no severity, no prose. The constitution and the deterministic-check-output
  blocks of the shipped prompt are omitted, because they govern a verdict this
  arm does not ask for.

**Reply contract**, stated to the model and parsed deterministically:

    {"checks": [{"name": str,
                 "kind": "io_example" | "property",
                 "code": "<python statements>"}]}

between 1 and 5 checks. `code` is executed **after** the solution file has run,
so every name the solution binds is already in scope. A check FAILS by raising
and PASSES by returning normally. This is the most permissive executable form
available — an `io_example` is just `assert f(x) == y` — chosen deliberately so
that the architecture is not killed on a format technicality.

## 4. The four measures, operationally

Every outcome below is produced by a Python interpreter in a subprocess. No
model judges any outcome in this study.

Execution outcome of one check against one solution, in a subprocess with a
15-second wall clock, a fresh temp cwd, and the sandbox guard of §7:

| code | meaning |
|---|---|
| `PASS` | exit 0, no sandbox violation |
| `FAIL_ASSERT` | nonzero exit, the raised exception is `AssertionError` |
| `FAIL_EXC:<Type>` | nonzero exit, some other exception |
| `TIMEOUT` | did not terminate in 15s |
| `SANDBOX` | tripped the filesystem/network/process guard |

**M1 — Parses.** The reply yields at least one check whose `code` is a string
that `compile(code, "<check>", "exec")` accepts. Reported per instance (any
check parses) and per check.

**M2 — Runs.** A check *runs* iff, against the **canonical** solution, it
terminates within 15s, trips no sandbox guard, and its outcome is `PASS` or
`FAIL_ASSERT`. Rationale: the canonical solution is correct by construction, so
any *non-assertion* exception there — an invented import, a name that does not
exist, wrong arity — is the check's own fault and not evidence about any
solution. A check that raises `AssertionError` on the canonical solution *ran*;
it is simply wrong, and M4 counts that. The exception type of every
non-runnable check is recorded.

**M3 — Discriminates (the measure that matters, and the primary outcome).**
A check *discriminates* iff it Runs, its outcome on the canonical solution is
`PASS`, **and** its outcome on the stratum-P solution is `FAIL_ASSERT`,
`FAIL_EXC:*`, or `TIMEOUT`. An exception raised by the defective solution itself
counts as a failure, because that is what the defect is. `SANDBOX` on either run
disqualifies the check.

**An instance discriminates iff at least one of its checks discriminates.**

> **Primary outcome, named in advance: the number of the 56 instances producing
> at least one runnable, discriminating check.** One number. Everything else in
> this file is secondary.

**M4 — Agrees with ground truth.** Instance verdict = BLOCK iff at least one
*runnable* check fails on the solution under test. Each instance is evaluated
against two solutions with known, model-free ground truth: the stratum-P
solution (defective) and the canonical solution (correct). Reported as
sensitivity (defective solutions blocked / 56), specificity (canonical solutions
not blocked / 56), and overall agreement over the 112 pairs.

**Secondary — wrongness of individual checks.** Among runnable checks:

- *false negative* — passes on the defective solution (contributes nothing);
- *false positive* — fails on the correct solution (would block correct code);
- *wrong* — the union of the two, which is the requester's definition.

The false-positive number is the one that decides whether a deterministic layer
can be handed these checks at all: a confidently wrong executable check is worse
than an opinion, because an opinion is auditable and an executed `False` is not.

**Secondary — safety.** Count of checks that trip the sandbox guard, by kind
(filesystem write, filesystem read outside the sandbox, network, subprocess),
plus a static scan of every generated check for the same imports. A nonzero
count is itself a finding about whether this architecture is safe to ship.

## 5. Statistics

- Every rate is reported with a **95% Wilson score interval**, and never quoted
  without it (`benchmarks/EXPERIMENT_RECORD.md` §9).
- A count small enough that its interval reaches an absurd bound is quoted as
  the count.
- **"Inside the noise floor" will not be written**, in any form, unless the
  replicate arm of §8 actually runs; without it the honest form is "run-to-run
  variation is unmeasured for this contrast".
- Comparisons made by this study: **one** primary (the M3 instance rate against
  the 1/3 threshold of §6), fixed here, before any call. The M1/M2/M4/wrongness
  /safety numbers are secondary and named here; anything not named here is
  labelled exploratory wherever it appears.

## 6. The kill condition, fixed before the run

> **Fewer than one third of the 56 instances producing at least one runnable,
> discriminating check means the auditor cannot supply this kind of evidence,
> the proposed architecture is not worth its cost, and the answer to "should the
> auditor emit executable checks" is no — on evidence rather than on principle.**

One third of 56 is 18.67. Operationally:

- **KILL fires iff the M3 instance count is ≤ 18** (18/56 = 32.1% < 33.3%).
- **KILL does not fire iff the count is ≥ 19** (19/56 = 33.9%).

If KILL fires it is the headline of the report, stated first and without hedging.

**Not-killed is not the same as proven.** Clearing this bar says the auditor can
write *some* discriminating checks; it says nothing about whether the
architecture is net-positive. The false-positive rate is reported next to the
primary either way.

## 7. Safety — executing model-generated code

Non-negotiable, and preregistered so that a shortcut taken under time pressure
would be visible as a deviation:

1. Every check runs in a **subprocess**, via `execute._run` — the harness's
   existing sandbox: a fresh `TemporaryDirectory` as cwd, captured stdout/stderr,
   a hard `subprocess.run(timeout=...)` wall clock. It is reused, not
   reimplemented.
2. **Nothing generated is ever executed in the session's own interpreter.** No
   `exec`, no `eval`, no import of generated code in the harness process.
3. A **guard preamble** is prepended to every executed program (in the new
   harness file, *not* by modifying `execute.py`):
   - `socket.socket` / `socket.create_connection` raise — this closes every
     Python network path, since `urllib`, `http.client` and `requests` all go
     through `socket`;
   - `subprocess.Popen`, `os.system`, `os.popen`, `os.execv*` raise;
   - `builtins.open` is wrapped: a path resolving outside the temp cwd and
     outside the Python installation prefix raises. Reads within the Python
     prefix stay open so that `import` continues to work.
   - each trip writes a marker to stderr before raising, so the harness records
     it as `SANDBOX` rather than as a check failure.
4. The timeout is **15 seconds** per check per solution.

## 8. Stopping rule

- Run all 56 instances of the `emit` arm.
- **Budget stop**: halt the arm if its ledger spend passes **$1.20**. Study 1's
  cross arm cost $1.776 over 235 calls ($0.0076/call), so 56 calls project to
  ~$0.42 and this cap should not bind.
- **Failure stop**: halt if five consecutive instances raise a provider error.
- **Credential probe first**: one cheap call, confirmed to succeed, before any
  spending. Two studies in this repository have died mid-run on exhausted
  provider credit. No key is ever printed.
- **Replicate arm** `emit-r2`, identical in every respect, runs **only if** the
  `emit` arm completes for ≤ $0.80 and total study spend stays under $2.00. It
  is the only thing that would license a noise-floor statement about *this*
  estimand, and if it does not run, §5 forbids one.
- Instances that error irrecoverably are recorded with their error and counted
  in the denominator as non-parsing. The denominator is 56 in every rate unless
  stated otherwise at the number.

## 9. What gets committed

`RESULTS-CHECKS.md`, the harness, `records/checks/manifest.json`, and one JSONL
row per instance carrying the raw reply hash, every generated check verbatim,
both execution outcomes per check, tokens, cost, wall time and prompt sha256.

Committing generated check text and solution text is explicitly authorised for
this study by the requester: EvalPlus is public and redistributable, and the
corpus constraint binding elsewhere in this repository is ExpertLongBench's,
which this study does not touch. This is a departure from
`benchmarks/EXPERIMENT_RECORD.md` §3's blanket rule and is recorded as
deviation D0 rather than taken silently — the character of the generated checks
is the finding, so hashes alone would not carry it.

## 10. Deviations known at write time

- **D0** — corpus text is committed, authorised as above.
- **D1** — the solution text is read from the study-1 run directory at
  `/private/tmp/.../wt-code/benchmarks/code/runs/study1/solutions.jsonl`, which
  is outside this worktree, because `runs/` is gitignored and the committed
  `records/study1/solutions.jsonl` carries only `solution_sha256`. All 540
  solutions were verified byte-identical to the committed hashes before this
  file was written; the verification is re-run inside the harness and recorded
  in the manifest. Cannot bias the result: the bytes are hash-pinned.
- **D2** — `temperature` cannot be set through the product's provider layer;
  the adapters take it from the model's capability card, and the auditor model's
  card carries `temperature=False`. This is the same limitation study 1 recorded
  and is the reason the replicate arm of §8 exists at all.
