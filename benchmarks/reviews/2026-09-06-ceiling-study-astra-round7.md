# Independent cross-vendor review of the ceiling study, round 7 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over `study/ceiling` at 6073d0d. Both
generated files byte-identical to round 6. Verdict: **yes with corrections**,
three narrow items: the binding still ignores a sentence's subject (a rate can
be re-attributed to another family in prose and stay bound to the original
array); one hand-written seed explanation contradicts the instrument; "six of
nine" should read eight and "every defect" should be narrowed; eleven
duplicated function definitions remain in the test file. Verbatim below.

---

**The numerical checks pass, but corrections remain.** Reviewed `6073d0d` against merge base `19bd1615c3d35381c37525721b6d38c5831b1ee5`, after reading all six reports. No files modified, network used, or detector readings adjudicated.
1. **The family-binding claim is still too strong.** Both reader-sentence mutations—`+1.00 to +2.00` and `omitted;`—turn red. The original fabricated “eight-reading cost 9.7%” insertion also turns red.
   However, this replacement in the existing conclusion leaves **all 15 report tests green**, including uniqueness and liveness:
   ```text
   Before: 30.0% [20.0, 40.7]) at lower false-positive cost
   After:  30.0% [20.0, 40.7]). The shipped auditor's eight readings operated at lower false-positive cost
   ```
   The unchanged continuation supplies `(9.7% [5.3, 14.5] against 16.0% [10.1, 22.3])`. The [cost rule](benchmarks/code/tests/test_report_consistency.py:381) still binds Astra’s one-reading interval without checking the subject or reading count. It matches once, so uniqueness does not catch this.
   Conversely, inserting the **correct** sentence “The shipped auditor’s one-reading recall starts from 10.7% [5.1, 17.4]” fails uniqueness despite passing value/interval checks. **That is acceptable as a strict editing guard** requiring an explicit binding for each occurrence; it is not evidence that repeated prose is false.
2. **Seed measurement is correct; one explanation remains contradictory.** Both the committed instrument and independent full-regeneration instrumentation reproduce **34 distinct seeds over 205 constructions**, exactly matching both manifests. `+7 = 20260915` is consumed by the pooled self−cross sign-flip: **25 nonzero clusters, 200,000 draws, p = 0.12373938130309349**.
   But both manifests retain the [statement](benchmarks/code/ceiling/finalise_manifests.py:287) that `+1 = 20260909` “does not appear in observed_seeds.” It does. Correct that wording.
3. **The nine attribution-table rows are correct; surrounding summaries are not.** The six reports support reviewer attribution for **15, 17, 20, 21, 22, 23, 26, 27**, with **24** recorded as author-discovered. Change [“Six of the nine”](benchmarks/code/RESULTS-CEILING.md:162) to **eight**. Also narrow [“Every defect in this study’s statistical machinery”](benchmarks/CORRECTIONS.md:533) to the listed items: the beta-tail defect was fixed at `7dc2620`, before round 1.
The `RATE_RULES` block is deduplicated. **Eleven identical function definitions remain duplicated**, including four test functions; these do not add distinct tests.
All remaining requested checks pass:
- **36 distinct tests passed: 21 statistics + 15 report**, directly invoked under Python 3.13.5. Application and hidden suites were not rerun.
- Deviations are exactly **1–30**, monotonically numbered.
- `src/` diff and branch-only history against the merge base are empty.
- All **99 generated table lines** occur in the report.
- With credential-like variables unset, sockets disabled, bytecode disabled, and writes intercepted in memory, regeneration returned zero and reproduced:
```text
numbers.json 412534c7222569ed736cdcb84019a0ff1efdb01273ec2e555312b515463d8ee0
tables.md    c5e939aac38fc238767dfb918f8cc10b026c9231f59329f7911e5a300c6f7e2e
```
**Both files are byte-identical to round 6.** `tables.md` did not change: this revision changes narrative, checks, and manifests, not the numerical inputs or table generator.
**May these numbers be quoted in a paper — yes with corrections. The single most important reason for retaining that condition is that the claimed family-aware verification still accepts a false attribution of a rate and its interval.**
