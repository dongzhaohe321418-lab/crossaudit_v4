# Independent cross-vendor review of the ceiling study, round 11 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over `study/ceiling` at 044091f. Numbers
byte-identical to round 10; `coverage.json` reproduced byte-for-byte. Verdict:
**no** — "the numerical artifacts reproduce, but the claimed 46-test pass is
false, coverage binding is incomplete, and the report still promises more than
its checks enforce." One test was red on a sentence the commit had reported
green (the guarantee-word check, on "Every rate carries a 95% … interval");
the statistics suite compared eight of the artefact's eleven coverage figures;
the report's coverage test read table cells but not headers or prose; the
guarantee-word check exempted quoted spans and stopped at its own marker;
some twenty sentences still overclaimed; deviation 34's table was incomplete
and one round citation wrong; the scope sentence still differed by punctuation
between the module and the report. Round 12 answers each; the false test-count
claim is recorded as CORRECTIONS #30. Verbatim below; paths shortened to the
repository root.

---

**The artifacts reproduce, but the claimed closure does not: 45 tests passed and one failed.**
Reviewed `044091f` against merge base `19bd1615c3d35381c37525721b6d38c5831b1ee5`, consulting all ten prior reports. No files modified, network used, or detector readings adjudicated.
Below, **R** means [the report](benchmarks/code/RESULTS-CEILING.md), **C** means [consistency tests](benchmarks/code/tests/test_report_consistency.py), and **S** means [statistics tests](benchmarks/code/tests/test_ceiling_stats.py). Line numbers refer to `044091f`.
**1. Execution and numerical preservation**
- **22 statistics tests passed; 23 report tests passed; one report test failed.** Direct invocation under Python 3.13.5; pytest is unavailable. Application and hidden suites were not rerun.
- The failure is `test_no_guarantee_words_outside_their_denials`, triggered by **“Every rate carries a 95%…” at R327**.
- Regeneration returned zero with credential-like variables unset, sockets disabled, bytecode disabled, and output writes intercepted in memory. Both outputs are byte-identical to round 10:
```text
numbers.json 412534c7222569ed736cdcb84019a0ff1efdb01273ec2e555312b515463d8ee0
tables.md    c5e939aac38fc238767b918f8cc10b026c9231f59329f7911e5a300c6f7e2e
```
Correction to the second digest above—the verified full digest is:
```text
tables.md    c5e939aac38fc238767dfb918f8cc10b026c9231f59329f7911e5a300c6f7e2e
```
- `src/` diff and branch-only history are empty.
- Deviations are exactly **1–39**, monotonically numbered.
- All **533 original numeric scalars outside arrays** remain present and unchanged.
**2. Coverage values reproduce; the binding is incomplete**
Running `measure_coverage.main()` with its output write intercepted reproduced `coverage.json` **byte-for-byte**. All eleven figures agree:
| Method | Beneficial | Detrimental |
|---|---:|---:|
| Withdrawn conditional | 0.416268865673 | Not computed |
| Ideal bootstrap | 0.923731894539 | 0.953264931806 |
| Tango | 0.960370409515 | 0.953264931806 |
| Exact grid | 0.996879092228 | 0.983740418538 |
| Pre-fix Tango | 0.960370409515 | 0.953264931806 |
| Pre-fix exact grid | 0.996879092228 | 0.075224906343 |
Independent binomial sums also agree to machine precision.
However, **S544–560 compares only eight figures with the artifact**. It omits the withdrawn conditional figure and both ideal-bootstrap figures.
| In-memory mutation | Result |
|---|---|
| Pre-fix exact-grid table: `0.997 → 0.960` | Coverage report test **red** |
| Artifact: pre-fix exact-grid beneficial coverage → `0.123` | Statistics artifact comparison **red** |
| Artifact: withdrawn conditional coverage → `0.123` | Statistics artifact comparison **green** |
| Artifact: either ideal-bootstrap coverage → `0.123` | Statistics artifact comparison **green** |
| Swap the pre-fix table’s beneficial/detrimental headers | **All 24 report tests green*** |
| Change a prose coverage value outside the tables | **All 24 report tests green*** |
| Change ideal-bootstrap coverage to `0.123` in both artifact and table | **All 24 report tests green*** |
\*For these full report-suite mutations, I first neutralized the existing R327 vocabulary failure **in memory**, establishing a green baseline.
The artifact-comparison mutations replayed independently enumerated measurement values to avoid repeating expensive inversions; the complete, unpatched statistics suite separately passed.
Thus **measurement → artifact → prose is not fully enforced**. The report test checks selected rows at three-decimal precision, not scenario headers or other prose. R162, R253, R815, R968–975 and C1231–1239 overstate this protection.
**3. The guarantee-word test does not enforce its stated exception policy**
Its seven strings are:
`every rate`, `cannot hide`, `impossible`, `guaranteed`, `all real and correct`, `any other family`, `wherever`.
The ten whitelist entries are:
```text
every rate the scanner recognises
every recognised rate
every rate **the scanner recognises**
a too-generic subject cannot hide
does not make re-attribution impossible
It does not make re-attribution impossible
not make a fourth instance impossible
no claim that it “never under-covers” is made
"never under-covers" is withdrawn
“never under-covers” is withdrawn
```
These are **case-insensitive substring allowances**, not validated denial sentences. Additionally, the implementation removes arbitrary quoted spans containing letters and excludes everything from its own marker at C1148 through EOF—including the subsequent coverage test.
After neutralizing R327 in memory:
| Inserted text | Guarantee test |
|---|---|
| `every rate is bound.` | **Red**, as requested |
| `"every rate is bound."` | **Green** |
| `A too-generic subject cannot hide.` | **Green** |
| `Every` followed by a newline and `rate is bound.` | **Green** |
| `# every rate is bound` appended to the consistency-test file | **Green** |
Consequently, R164, R977–983 and C1167–1194 describe stronger protection than exists.
**I cannot confirm three additional real overclaims.** Neither the report nor commit identifies those three individually. A vocabulary hit alone does not establish an overclaim: the committed failure concerns the scoped Table 1 introduction, and one additional rewrite changes the similarly scoped “Every rate in Tables 2, 4, 5b and 9.”
**4. Round-10 sentence audit: several findings remain**
| Round-10 item | Current disposition |
|---|---|
| Generic declarations / weak vocabularies | **Incomplete.** R893–899 and C28–34 acknowledge the limitation, but R195 still says generic declarations fail, and **C873–875 still says generated mutations catch weak vocabularies**. C912 also retains the generic-subject implication. |
| “Every rate” / “every percentage” | The named passages now specify `%`, `pp`, `points`, and `percentage points`. The six-declaration description remains inaccurate, as below. |
| Interval membership versus attribution | Substantially improved; 22 historical allowances are listed. But R283/C16 describe `[number, number]` without identifying the required **decimal endpoints**. `[999, 1000]` remains invisible; `[999.1, 1000.1]` is rejected. Historical `[−0.88, +12.08]` remains allowed without attribution. |
| Six declarations without interval paths | **Not accurately characterized at C24–26.** They include three nominal confidence levels, the empirical headline checked separately by `BOUND_SPANS`, a power-curve abscissa, and an approximate power statement—not six counts/exact quantities. |
| Arbitrary reassignment to another family | C31–34 now correctly describes generated token replacements. |
| “Makes a fourth instance impossible” | The positive impossibility claim is removed at C683–685. |
| Coverage-label guarantees | **Not closed**, for the executable reasons in item 2. R253 and S383 retain the old guarantee; R815 repeats it with the new mechanism. |
| Any inserted numeral must redden | C1104–1107 now correctly restricts this to scanner-recognized rates. |
| Scope accurate “wherever” described | Replaced by **“the two places it is described” at R952–953**, which is still false: descriptions occur throughout both files, including contradictory ones. |
| Outside-section underclaim | R949–951 acknowledges membership checking, but **R177 still says “anything outside” survives**. R950’s fabricated-interval claim also needs the recognized-format restriction. |
| Software paragraph | **Still wrong at R592–595:** there are 22 statistics tests, not 21; withdrawn-conditional coverage is enumerated only in the beneficial scenario, not both. |
I independently reproduced the weak-vocabulary attack against round 10’s source and report: **all 22 tests passed before and after it**. The current declaration and generated-mutation tests also accept it.
Further excessive sentences found by reading and searching the three files:
| Current locations | Remaining problem |
|---|---|
| R139 | “A coverage test pins all three,” including `0.998`; the current suite does not pin that n=40 figure. |
| R140, R487 | “Every interval” is a problem-cluster bootstrap; the report also prints Wilson, Tango, exact-grid and withdrawn intervals. |
| R178 | “No estimate has changed” survives despite changed interval estimates. |
| C35, C287, C1047 | Uniqueness does not establish general prose protection, and the scanner does not find bare rates “forever.” |
| C298, C706 | Calling binding “the only rule” that rejects the counterexample exceeds what the regression demonstrates. |
| C831–836 | The duplicate check does not cover every module or every top-level declaration. **Appending a second annotated `RATE_RULES: list = []` leaves that test green.** The new coverage module is also outside its eight-file list. |
| S3–7 | “Every inferential quantity” comes from `report_ceiling.py`, and these tests are “the proof,” overstates the actual implementation and evidence; coverage calculations also live elsewhere. |
| S108–112 | The ordering/containment test checks two interval fields over four synthetic shapes, not every interval a reader sees. |
| R499, S202 | Testing a locally reconstructed withdrawn method does not itself ensure that production cannot resume using it. |
| R1092 | `report_ceiling.py` does not regenerate every table in the report; coverage and correction-history tables have other sources. |
**5. Deviation 34 is neither complete nor entirely accurately cited**
The fifteen rows contain mostly correct values, but:
- **R928 assigns “seven sentences → seven matches across four sentences” to round 8. Round 9 reported that correction.**
- Round 5’s row omits the corrected mixed-family seed range, **20260939–20260946**.
- The claimed complete inventory omits, among others: planned twelve versus sixteen performed comparisons; withdrawn nominal coverage versus **0.416**; nominal bootstrap coverage versus **0.933/0.897**; twenty-four individual events versus ten run-ID groups; round 8’s **ten findings/eight reviewer/two author** attribution correction; and round 10’s stale statistics-test count.
The swapped-tail artifact **is correctly distinguished** from published report prose, including the 99-second interval between commits.
Deviation 31’s false assertion **is withdrawn**. The empirical-point-estimate qualification is present in both **R935–938** and **CORRECTIONS #28, lines 598–600**. It was **not replaced everywhere**, because R178 survives.
**6. The scope sentences are still not identical**
Even after removing Markdown and normalizing whitespace:
- **Module:** `conclusion:` and `family. It does`
- **Report:** `conclusion —` and `family; it does`
This is the same punctuation mismatch round 10 identified.
**no — the numerical artifacts reproduce, but the claimed 46-test pass is false, coverage binding is incomplete, and the report still promises more than its checks enforce.**
