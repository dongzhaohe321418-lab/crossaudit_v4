# Study 16 — a test-generating auditor against the reading auditor: results

Preregistration `testgen/PREREGISTRATION.md` (c2b55dc) and Amendment 1 (d4a70d0), both
before the first model call (2026-09-09 11:52 +08:00; the run started 11:53). Records:
`records/testgen/{rows.jsonl, suites.json, numbers.json}`; the generated test text is in
the run archive (`~/Documents/Crossaudit/study-data/wt-testgen-runs/`, `MANIFEST.sha256`),
not committed (Amendment 1). Harness: `testgen.py`; boundary and flag-logic tests in
`tests/test_architectures.py` and `tests/test_testgen.py`. Report: `testgen.py report`;
the exploratory numbers below come from `testgen/exploratory.py` and say so.

## 1. The preregistered decision, and what it rests on

One generation call per problem (222 problems, 290 instances, both halves; $1.77; 1,199
tests, mean 5.4 per problem, min 0, max 11; none uncompilable; one suite empty). Confirm
half, the objective of `explore/PREREGISTRATION.md` §5 (highest P-recall with C-false-
positive rate ≤ 6.7%; bar = 5 instances of 74):

| arm | confirm P-recall | Wilson | problem-cluster bootstrap | confirm C-FP | Wilson |
|---|---|---|---|---|---|
| `hc` (shipped, study 7 records) | 11/55 = 20.0% | 11.6–32.4% | 10.7–30.2% | 5/74 = 6.8% | 2.9–14.9% |
| `testgen` | 13/55 = 23.6% | 14.4–36.3% | 10.9–37.7% | 3/74 = 4.1% | 1.4–11.3% |
| `testgen-validated` (oracle upper bound) | 11/55 = 20.0% | 11.6–32.4% | 8.8–33.3% | 0/74 = 0.0% | 0.0–4.9% |
| `hc ∪ testgen` | 19/55 = 34.5% | 23.4–47.7% | 21.2–48.2% | 7/74 = 9.5% | 4.7–18.3% |

**H16 holds by the letter of §3**: `testgen` sits within the false-positive bar and its
recall count is above `hc`'s. **The margin is two instances and it is not evidence.**
Paired on the 55 P instances, `testgen` flags 8 that `hc` does not and misses 6 that `hc`
flags (exact McNemar p = 0.79); the bootstrap intervals overlap almost entirely. And the
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
  4 are flagged by both. Of the 8 `testgen`-only flags, 3 are the ceiling study's
  `unexercised-edge` class, 1 `spec-misreading`, 4 outside its classified set (the ceiling
  classified 68 instances). The residual behind `hc` on this half is 29 `unexercised-edge`
  of 44; execution reached 3 of them.
* **The union is where the recall is — and it is not a product number yet.**
  `hc ∪ testgen` reaches 19/55 at 7/74, over the bar (the `tri_union` shape §1 warned
  of, mildly: two of the seven are `testgen`'s wrong tests). **EXPLORATORY, oracle-
  bounded:** `hc ∪ testgen-validated` is 18/55 = 32.7% (Wilson 21.8–45.9%) at `hc`'s own
  5/74 — the front would move by seven P instances if the wrong tests could be removed
  without the canonical solution. That is the study's finding, and it is conditional.

Explore half, reported once and carrying no claim (§4): `hc` 5/55 P, 0/76 C; `testgen`
10/55, 5/76; `testgen-validated` 9/55, 2/76; `hc ∪ testgen` 12/55, 5/76.

## 2. Secondaries

* **Wrong tests.** 45 of the 1,199 unique tests (3.8%) fail on the canonical solution;
  32 of 222 problems have at least one. Per instance-row (a suite is applied to every
  candidate of its problem) 70 of 1,545 test applications are dropped by validation.
* **Timeouts and errors.** 2 candidate runs timed out (flagged, as Amendment 1 says);
  1 canonical run timed out (the validated arm does not flag that row); 4 candidate runs
  died before the collector (an import the candidate lacked), counted as every test
  failed.
* **Cost.** $1.77 for 222 calls, $0.0061 per instance amortised — a tenth of `hc`'s
  per-instance figure on the explore leaderboard; the executor's cost is wall-clock only.
* **F stratum** (confirm, 15): `testgen` 13/15 = 86.7% (Wilson 62.1–96.3%).

## 3. What the preregistration said would follow, and what follows

§7's first branch ("H16 holds → a design note, then a slice") is triggered by the letter
of the rule; its second branch ("fails on false positives → validation without an
oracle") describes the evidence better, because the recall gain is entirely in the
validated union and the unvalidated arm's gain is two wrong tests. The judgement recorded
here: **the product design note waits; the next preregistered study is oracle-free
validation** — majority agreement over independent draws, or a test's agreement with the
visible suite's behaviour on the canonical-free signals the product has (the candidate
passing the visible suite) — with the seven `validated-only` instances as the recall it
must keep and the 45 wrong tests as the set it must remove, both frozen in this record.

## 4. Disclosed limits

* One model, one draw, one temperature (the adapters' default): a second draw could change
  the wrong-test set; the replicate is the oracle-free study's to run, not this one's.
* The suites are a function of the problem, so the two batches' instances of one problem
  share a suite and the bootstrap's cluster is the problem, as preregistered.
* `hc`'s records are study 7's, not re-run; the comparison is against the shipped auditor
  as it was measured then.
* The ceiling study's residual classes cover 68 instances; 4 of the 8 `testgen`-only
  flags are unclassified there.
* `testgen-validated` uses the canonical solution and is an upper bound everywhere it
  appears; no product number derives from it.
