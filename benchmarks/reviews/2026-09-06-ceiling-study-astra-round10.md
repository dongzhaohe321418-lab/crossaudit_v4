# Independent cross-vendor review of the ceiling study, round 10 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over `study/ceiling` at 2a5b6b7. Numbers
byte-identical to round 9; 43 tests; the documented-boundary test behaves as
requested. Verdict: **yes with corrections** — every remaining overclaiming
sentence enumerated by line (generic-vocabulary, "every rate", "all real and
correct", "impossible", "labels cannot drift", "wherever"), the correction
history in deviation 34 incomplete against rounds 1–9, deviation 31 still
asserting "no published number was ever wrong", "no estimate has changed"
to be narrowed to point estimates, and two stale software-paragraph claims.
Verbatim below.

---

**The numbers reproduce, but the report still overstates what its checks enforce.** Reviewed `2a5b6b7` against merge base `19bd1615c3d35381c37525721b6d38c5831b1ee5`, consulting all nine prior reports. No files modified, network used, or detector readings adjudicated.
1. **Numerical and execution checks pass.**
   - **43 tests passed: 21 statistics + 22 report**, directly invoked under Python 3.13.5. Pytest is unavailable; application and hidden suites were not rerun.
   - Regeneration returned zero with credentials unset, sockets disabled, bytecode disabled, and output writes intercepted in memory. Both outputs were byte-identical to round 9:
   
     ```text
     numbers.json 412534c7222569ed736cdcb84019a0ff1efdb01273ec2e555312b515463d8ee0
     tables.md    c5e939aac38fc238767dfb918f8cc10b026c9231f59329f7911e5a300c6f7e2e
     ```
   
   - `src/` diff and branch-only history are empty.
   - Deviations are exactly **1–36**, monotonically numbered.
2. **The scope sentences agree substantively, but are not literally identical; broader claims remain.**
   The [module sentence](benchmarks/code/tests/test_report_consistency.py:3) uses “conclusion:” and “family. It does”; the [report sentence](benchmarks/code/RESULTS-CEILING.md:757) uses “conclusion —” and “family; it does.”
   The remaining excessive formulations are below. Locations in older review tables retain present-tense promises; they need explicit historical qualification if preserved.
   | Location | Claim exceeding the checks |
   |---|---|
   | Report lines **182, 875**; consistency-test docstring lines **21, 847–849** | Generic declarations are rejected, a “too-generic subject cannot hide,” or generated mutations catch weak vocabularies. |
   | Report lines **222, 239, 802–803**; consistency-test docstrings lines **436–437, 592, 655–656** | “Every rate” or “every percentage” is bound or explicitly exempted. The scanner recognizes particular numeral formats, not every expression of a rate. |
   | Report line **267**; consistency-test docstrings lines **16, 134** | Every bracketed/quoted interval exists in `numbers.json`, or an empty result means intervals are “all real and correct.” Recognized formats and historical allowances limit this. Membership also does not establish attribution. |
   | Consistency-test module lines **18–20** | Every registered numeral is bound to a specific interval array. Six registered declarations have no interval path; these need qualification. |
   | Consistency-test module lines **23–24** | “Re-attributing any rule’s sentence to any other family reddens.” Only the generated token-replacement mutations establish this result. |
   | Consistency-test docstring line **659** | Binding “makes a fourth instance impossible.” The documented surviving attacks contradict general closure. |
   | Report lines **237, 795–796**; statistics-test docstrings lines **263, 498–500** | Coverage labels cannot drift, or published claims are checked by the statistical tests. Those tests compute coverage; they do not read and validate these prose labels. |
   | Consistency-test docstring lines **1078–1080** | “A new numeral inserted into the opening or conclusion is UNBOUND and reddens.” A numeral need not match the rate scanner. |
   | Report lines **908–910** | The scope is stated accurately “wherever the guard is described.” The surviving statements above contradict this. |
   These are executable discrepancies:
   - Assigning the self-asymptote binding to a recognized `generic` vocabulary containing only `asymptote` leaves **all 22 report tests green**, including declaration and generated-mutation tests.
   - Inserting `[999, 1000]`, a non-rate numeral such as `123 examples`, or misusing historical `[−0.88, +12.08]` leaves both guard functions green. That historical interval is absent from `numbers.json` at its displayed precision.
   - Changing the published pre-fix exact-grid coverage from `0.997` back to `0.960` leaves **all 22 report tests green**.
   There is also an **underclaim**: report lines **164, 906–907** say “anything outside” survives or that the guard “does not police text outside” the sections. An outside-section caption containing `[999.1, 1000.1]` is rejected.
   Separately, the [software paragraph](benchmarks/code/RESULTS-CEILING.md:576) still says **15 statistics tests**, and its “coverage simulations for every interval method” exceeds the suite’s actual coverage checks.
3. **The documented-boundary test behaves as requested.**
   | Mutation | Result |
   |---|---|
   | Two-family grammatical reassignment | Green |
   | Wrong-family interval without an accompanying rate | Green |
   | Rate written in words | Green |
   | Wrong-family caption outside the sections | Green |
   | Fifth case: inserted `9.7% [5.3, 14.5]` | Red: `UNBOUND rate '9.7%'` |
   Extending `check_rate_bindings` **in memory** to reject the documented word-rate sentence makes the committed test fail, explicitly instructing the reader to **“widen the docstring and the report’s description of the guard’s scope.”**
4. **Deviation 34’s four rows match the record, but the table is incomplete and the withdrawal is inconsistent elsewhere.**
   The four numerical corrections agree with round 9, and CORRECTIONS #28 repeats them consistently. For the residual, the error was inconsistent canonical reporting: both seed-dependent intervals were valid bootstrap estimates.
   The requested exhaustive history is **not** satisfied. Omissions include:
   - **Round 1:** zero non-solution returns versus **4/4/2/0**; “one more defect” versus **two**.
   - **Rounds 1–2:** “exactly one” surviving contrast versus **two**; overstated coverage and the `0.998` figure assigned to the wrong scenario.
   - **Round 4:** pre-fix exact-grid coverage **0.960 → 0.997**, explicitly reported in [finding 1](benchmarks/reviews/2026-09-06-ceiling-study-astra-round4.md:19).
   - **Round 6:** registered union intervals **[20.0,40.5] → [20.0,40.7]**, **[8.2,27.3] → [8.3,27.3]**, and **[20.9,45.5] → [20.7,45.0]**, alongside the residual correction.
   - The numerical inventory/count corrections from rounds **5–9**, including seed ranges, attribution counts, and seven sentences versus four.
   - If committed numerical artifacts are included, round 1 also documented the pre-report swapped-tail interval **[+3.16, −1.93]**; distinguish that artifact from published prose.
   Moreover, [deviation 31](benchmarks/code/RESULTS-CEILING.md:853) still asserts **“No published number was ever wrong.”** The replacement “no estimate … has changed” in deviation 34 and CORRECTIONS #28 should say **empirical point estimate**: interval estimates changed.
5. **The corrected attribution and result sentences remain intact.**
   CORRECTIONS #25 is byte-identical to round 9: **ten findings, eight reviewer discoveries, two author discoveries, nine numbered entries**. The report’s attribution sentence, opening results after the version notice, reader sentence, and conclusion are unchanged. Applying round 9’s subject requirements to round 8’s templates reproduces **seven failing rule matches across four sentences**.
**yes with corrections**
- Make all scope descriptions consistent, including numeral formats, declarations, historical allowances, and outside-section membership checks.
- Remove guarantees about generic vocabularies, arbitrary reassignment, and prose-label protection that the tests do not enforce.
- Complete the correction history, withdraw deviation 31’s surviving assertion, and restrict unchanged-estimate claims to empirical point estimates.
- Correct the stale statistics-test count and the claim of coverage simulations for every interval method.
