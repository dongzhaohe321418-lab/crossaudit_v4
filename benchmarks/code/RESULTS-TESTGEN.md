# Study 16 — a test-generating auditor against the reading auditor: results

Preregistration `testgen/PREREGISTRATION.md` (c2b55dc, 11:42 +08:00) and Amendment 1
(d4a70d0, committed 11:52:40 +08:00); the archive's first completed call is stamped
11:52:56 and its request began about 11:52:40 — the same second as the amendment's commit.
The ordering amendment-then-call is consistent with the timestamps and is not proven by
them: git's clock is one second coarse. The preregistration itself precedes the first call
by ten minutes, and the amendment changes no hypothesis, arm, outcome or kill rule (it
corrects a count, names the executor path and two harness rules, and fixes the seed). Records:
`records/testgen/{rows.jsonl, suites.json, numbers.json}`; the generated test text is in
the run archive (`~/Documents/Crossaudit/study-data/wt-testgen-runs/`, `MANIFEST.sha256`),
not committed (Amendment 1). Harness: `testgen.py`; boundary and flag-logic tests in
`tests/test_architectures.py` and `tests/test_testgen.py`. Report: `testgen.py report`;
the exploratory numbers below come from `testgen/exploratory.py` and say so.

## 1. The preregistered decision, and what it rests on

One generation call per problem (222 problems, 290 instances, both halves; $1.77; 1,199
tests, mean 5.4 per problem, min 0, max 11; none uncompilable; one suite empty). Confirm
half, the objective of `explore/PREREGISTRATION.md` §5 (highest P-recall with C-false-
positive rate ≤ 6.7%, which at n = 74 is at most 4 instances; the kill rule of §3 allows one
more, 5):

| arm | confirm P-recall | Wilson | problem-cluster bootstrap | confirm C-FP | Wilson |
|---|---|---|---|---|---|
| `hc` (shipped, study 7 records) | 11/55 = 20.0% | 11.6–32.4% | 10.7–30.2% | 5/74 = 6.8% | 2.9–14.9% |
| `testgen` | 13/55 = 23.6% | 14.4–36.3% | 10.9–37.7% | 3/74 = 4.1% | 1.4–11.3% |
| `testgen-validated` (oracle upper bound) | 11/55 = 20.0% | 11.6–32.4% | 8.8–33.3% | 0/74 = 0.0% | 0.0–4.9% |
| `hc ∪ testgen` | 19/55 = 34.5% | 23.4–47.7% | 21.2–48.2% | 7/74 = 9.5% | 4.7–18.3% |

**H16 HOLDS by the preregistered rule of §3**: `testgen` sits within the false-positive bar
and its recall count is above `hc`'s. **The margin is two instances and it is not
evidence.** Paired on the 55 P instances, `testgen` flags 8 that `hc` does not and misses 6
that `hc` flags: Δ recall = +3.6 points, exact McNemar p = 0.79 at the instance level, and
— the cluster-aware sensitivity EXPERIMENT_RECORD §9 requires beside it — the problem-
cluster bootstrap of the difference is −10.0 to +18.2 points and the cluster sign-flip test
p = 0.81 (44 problems, 13 with a non-zero change, enumerated exactly). And the
two instances of the margin are the same problem in both batches, flagged by a test that
also fails on the canonical solution — a wrong test that happened to fail on a defective
candidate. With wrong tests removed (`testgen-validated`), recall is 11/55, `hc`'s number
exactly, at 0/74 false positives. So the reading the preregistration's §7 asks for is
mixed, and the record says which branch each finding belongs to:

* **Every false positive is a wrong test.** All three C instances `testgen` flagged are
  flagged by a test that fails on the canonical solution too (`failed_candidate` =
  `failed_canonical` in each row). The false-positive mechanism §1 named is the only one
  observed; the validated arm has none.
* **Execution finds different defects from reading, at the same rate.** On the confirm
  half, `testgen-validated` flags 7 P instances `hc` misses, `hc` flags 7 it misses, and
  4 are flagged by both. Of the 8 `testgen`-only flags, 4 are the ceiling study's
  `unexercised-edge` class, 1 `spec-misreading`, 3 outside its classified set (the ceiling
  classified 68 instances); of the 7 `validated`-only flags, 3 / 1 / 3. The residual behind
  `hc` on this half is 29 `unexercised-edge` of 44; execution reached 4 of them, 3 with a
  correct test.
* **The union is where the recall is — and it is not a product number yet.**
  `hc ∪ testgen` reaches 19/55 at 7/74, over the bar (the `tri_union` shape §1 warned
  of, mildly: two of the seven are `testgen`'s wrong tests). **EXPLORATORY, oracle-
  bounded:** `hc ∪ testgen-validated` is 18/55 = 32.7% (Wilson 21.8–45.9%) at `hc`'s own
  5/74 — the front would move by seven P instances if the wrong tests could be removed
  without the canonical solution. That is the study's finding, and it is conditional.

Explore half, reported once and carrying no claim (§4): `hc` 5/55 P, 0/76 C; `testgen`
10/55, 5/76; `testgen-validated` 9/55, 2/76; `hc ∪ testgen` 12/55, 5/76.

## 2. Secondaries

* **Wrong tests.** 45 of the 1,188 unique tests whose canonical run completed (3.8%;
  Wilson 2.8–5.0%; problem-cluster bootstrap 2.5–5.2%) fail on the canonical solution;
  the 11 tests of the one suite whose canonical run timed out are unclassifiable. 32 of
  the 221 classifiable problems have at least one wrong test (one problem unknown). Per instance-row (a suite is applied to every
  candidate of its problem) 70 of 1,545 test applications are dropped by validation.
* **Timeouts and errors.** 2 candidate runs timed out (flagged, as Amendment 1 says);
  1 canonical run timed out (the validated arm does not flag that row); 2 other candidate
  runs died before the collector — an assertion the candidate itself embeds at module
  level failed on import — counted as every test failed.
* **Cost.** $1.77 for 222 calls, $0.0061 per instance amortised, against `hc`'s $0.0069
  on the explore leaderboard — 88% of the reading auditor's cost, about 12% less, not the
  order of magnitude a per-problem call might suggest (the suite is amortised over only
  1.3 instances per problem); the executor's cost is wall-clock only.
* **F stratum** (confirm, 15): `testgen` 13/15 = 86.7% (Wilson 62.1–96.3%).

## 3. What the preregistration said would follow, and what follows

H16 HOLDS, and §7's first branch is the one the preregistration committed to: "a design
note, then a slice with its own review". **What follows here departs from that branch,
and is labelled as a post-hoc deviation, not as a reading of the rule**: the recall gain
the rule counts is two instances flagged by wrong tests, while the gain that would matter
is in the validated union, which uses an oracle the product lacks. So the design note is
deferred, and the next preregistered study is oracle-free validation — majority agreement
over independent draws, or a test's agreement with the visible suite's behaviour on the
signals the product has (the candidate passing the visible suite) — with the seven
`validated-only` instances as the recall it must keep and the 45 wrong tests as the set it
must remove, both frozen in this record. The deviation is the author's judgement after
seeing the result; a reader who holds to §7 as written is entitled to the design note
first, and nothing in the record prevents writing it.

## 4. Disclosed limits

* One model, one draw, one temperature (the adapters' default): a second draw could change
  the wrong-test set; the replicate is the oracle-free study's to run, not this one's.
* The suites are a function of the problem, so the two batches' instances of one problem
  share a suite and the bootstrap's cluster is the problem, as preregistered.
* `hc`'s records are study 7's, not re-run; the comparison is against the shipped auditor
  as it was measured then.
* The ceiling study's residual classes cover 68 instances; 3 of the 8 `testgen`-only
  flags are unclassified there.
* `tests/test_testgen_report.py` binds figures in this file to `records/testgen/numbers.json`,
  `rows.jsonl`, `suites.json` and `testgen/exploratory.py`'s printed lines. **What it binds
  is exactly the list in that test module's docstring, and nothing else**; a figure not on
  that list is checked by the reviewer, not by the test. The list, at this commit: §1's
  table (six cells per arm); the decision line (HOLDS, 8/6, McNemar, Δ, its bootstrap, the
  sign-flip p, the 4-then-5 bar); "the same problem in both batches"; "All three C
  instances"; the residual counts (8 → 4/1/3, 7 → 3/1/3, 29 of 44, 68 classified); the
  overlap 7/7/4; the exploratory union with its Wilson and `hc`'s 5/74; "two of the seven";
  the explore-half line; the suite totals (222, 290, $1.77, 1,199 from `suites.json`, mean,
  min, max, one empty); the wrong-test figures (45 of 1,188, its intervals, 11 unknown, 32
  of 221, one problem unknown, 70 of 1,545); the timeout and pre-collector counts; the cost
  figures ($0.0061, `hc`'s $0.0069, "12% less", 1.3 instances per problem); the F stratum
  line.
* `testgen-validated` uses the canonical solution and is an upper bound everywhere it
  appears; no product number derives from it.
