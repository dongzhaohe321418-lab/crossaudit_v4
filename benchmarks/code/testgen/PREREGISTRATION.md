# Study 16 — a test-generating auditor against the reading auditor

Preregistered on `study/testgen` **before any model call** and before any implementation, at the commit that adds this file. Binding: `benchmarks/code/PREREGISTRATION-2.md`
and `RESULTS-EXPLORE.md` (the objective and the frozen instances), `architectures.py`'s information
boundary (prompts take plain strings; the hidden suite is unreachable by construction, proved by
`tests/test_architectures.py`), `EXPERIMENT_RECORD.md` §9–§10, D162 (the ceiling: reading auditors
saturate at ~30% recall; 80% of the residual is `unexercised-edge`), the owner's decision of
2026-09-07 (the next study is an architecture change, not a matcher class).

## 1. Hypothesis, in a form that can come out false

**H16.** An auditor that WRITES tests from the visible specification and RUNS them against the
candidate finds defects the reading auditors do not: on the explore study's confirm half (55 P,
74 C, the same frozen instances), `testgen` reaches higher P-recall than the shipped `hc`
(20.0%, 11/55) at a false-positive rate on correct code no worse than `hc`'s (5/74) plus the
noise floor the explore study measured — i.e. it sits on or above the Pareto front `hc` is on.
It comes out false if its recall at that false-positive rate is not above `hc`'s, or if its
false positives exceed the bar however high its recall (the `tri_union` shape: recall bought
one-for-one with false alarms).

Why it might be true: the residual defects are unexercised edges, which a test reaches and a
reading does not. Why it might be false: a generated test can be wrong — an assertion that
encodes the model's misreading of the spec fails on CORRECT code, which is exactly the
false positive the constraint forbids; on this benchmark the visible spec is short and the
edges the hidden suite probes are the ones the spec is silent about.

## 2. The arms

One model (the shipped cross-vendor auditor's) writes the tests; the structure is what changes.

* **`testgen`** — one generation call per PROBLEM (tests are a function of the spec, so every
  candidate to the same problem is judged by the identical suite; cached like
  `properties_for`): given `problem.spec` and `problem.visible_tests_text()` — plain strings,
  never the `Problem` — return up to N=12 assertion tests as Python. Each test is executed
  against the candidate with `execute.run_suite` (subprocess, timeout, fresh cwd). **Flag =
  at least one generated test fails on the candidate.** Nothing reads the hidden suite.
* **`testgen-validated`** — the same suite, with every generated test first run against the
  problem's canonical solution and DROPPED if it fails there. This uses the canonical
  solution as an oracle the product does not have; it is an UPPER BOUND on what test
  generation can do when the tests are right, reported beside `testgen` and never as a
  product number.
* **`hc`** — the shipped reading auditor, from the explore records (no new calls).
* **`hc ∪ testgen`** — the union, a set operation over records (no new calls): does execution
  add to reading, or only replace it.

## 3. Primary outcome, objective and kill — the explore study's, verbatim

Highest P-recall on the confirm half among specs whose false-positive rate on correct code is
≤ 6.7% (`RESULTS-EXPLORE.md`), with the count stated beside the rate. Instance-level, with the
problem-cluster bootstrap and Wilson intervals as in the ceiling study. **KILL for H16 if
`testgen`'s recall at ≤ 6.7% FP is not above `hc`'s 11/55**, or if its FP exceeds 6.7% by
more than one instance (the explore study's own reading of the constraint at n = 74).
`testgen-validated` cannot pass or kill anything; it bounds.

## 4. Secondaries

Tests generated per problem; tests dropped by validation (the wrongness rate of generated
tests, which is the false-positive mechanism named); per-flagged-instance overlap with `hc`
and with the ceiling's residual classes (does `testgen` flag `unexercised-edge` instances);
cost per instance (one generation per problem, amortised); the explore half reported once
and carrying no claim, as before.

## 5. What is held fixed, and the boundary

Frozen instances, canonical solutions and hidden suites from `records/`; the model and its
temperature as the explore study's `hc`; the executor `execute.py` unchanged; the prompt
builder in `architectures.py` (plain strings only) with the sentinel and reachability tests
extended to the new prompt. No model output that quotes a hidden test can exist, because no
prompt holds one.

## 6. Budget, n, stopping

The confirm half's problems (≤ 129 instances across ~60 problems): one call per problem,
≈ $0.5; budget $5. Cached per problem; a stopped run reports its n.

## 7. Decision, written before the run

* H16 holds → the test-generating auditor becomes a candidate product architecture: a
  design note, then a slice with its own review (the product has an executor; the auditor's
  reply would carry tests rather than findings).
* H16 fails on false positives → the finding is "generated tests are wrong at rate X", and
  the next question is validation without an oracle (majority over draws; tests that agree
  with the visible suite) — preregistered separately.
* H16 fails on recall → execution does not reach the residual either; the ceiling stands.

## Amendment 1 — before any model call: counts, the executor path and two harness rules

Written after the code was read and before the first call.

* **n.** The confirm half is 144 instances (55 P, 74 C, 15 F) over **128 problems**, not
  "~60"; the explore half 146 over 130. One generation call per problem, both halves,
  stays within the $5 budget (the decomposer's calls cost ≈ $0.01 each). §6's "~60" was a
  guess and is corrected here, not after the run.
* **The executor path.** A generated suite is assembled with `execute.mbpp_visible`
  (solution + the benchmark's import lines + each test executed separately, per-test
  failure vector), for HumanEval and MBPP alike, and run with `execute.run_suite`
  (subprocess, 30 s wall clock, fresh cwd). `execute.py` is unchanged. A candidate whose
  run times out is FLAGGED (recorded as `candidate_timed_out`); a canonical solution that
  times out cannot validate and `testgen-validated` then does not flag (recorded).
* **Uncompilable tests are dropped before execution, and counted.** `compile()` in the
  harness process — nothing executes. A test that does not compile would fail on every
  candidate and every canonical solution alike; it is a generation failure, not a finding.
  `n_uncompilable` is a secondary outcome beside `n_dropped_by_validation`.
* **Bootstrap seed 20260909**, 10,000 replicates over problem clusters, for the primary
  rates; `report_ceiling.cluster_bootstrap_ci` unchanged.
* **The generated test text is not committed.** It is model output written against
  corpus specifications; the records carry counts, hashes and per-test failure indices,
  the text stays in the run archive (`~/Documents/Crossaudit/study-data/`), as the
  property lists did.
