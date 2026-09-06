# Independent cross-vendor review of the ceiling study, round 12 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over `study/ceiling` at d37d8ef. The
suite passes as claimed — "49 passed, 0 failed", counted by the reviewer —
and numbers, tables and coverage artefact reproduce byte-for-byte. Verdict:
**no** — "the normal regeneration-and-splice workflow restores the exact
sentence that caused round 11's failure": the generator `report_ceiling.py`
still emitted "Every rate carries…", so splicing the committed `tables.md`
put the failing sentence back. All eleven coverage figures are now compared
and the round-11 attacks are red; what remains is a list of sentences still
stronger than their checks (coverage prose is membership, not attribution;
underscore emphasis and footnote markers evade the guarantee scan; the six
declarations are not counts or exact quantities; tuple targets escape the
duplicate scan; two stale historical sentences; deviation 34's wording on two
rows). Round 13 fixes the generator, adds a splice-idempotence test, scans the
generator and its tables, and narrows the rest. Verbatim below; paths
shortened to the repository root.

---

**The committed suite now passes, but I still withhold approval.** The normal table-splicing workflow restores round 11’s failing sentence, and several verification claims remain stronger than their checks.
Reviewed `d37d8ef` against `044091f` and merge base `19bd1615c3d35381c37525721b6d38c5831b1ee5`, consulting rounds 1–11. No files modified, network used, or detector readings adjudicated. The `gpt-6-astra` conflict remains noted.
Below, R = [report](benchmarks/code/RESULTS-CEILING.md), C = [consistency tests](benchmarks/code/tests/test_report_consistency.py), S = [statistics tests](benchmarks/code/tests/test_ceiling_stats.py). Unless explicitly marked otherwise, locations refer to `d37d8ef`.
Execution and numerical preservation are confirmed:
- **49 passed, 0 failed:** 27 report tests in **2.03 seconds**; 22 statistics tests in **1162.66 seconds**. Direct invocation under Python 3.13.5; pytest and `.venv` were unavailable. Application and hidden suites were not rerun.
- Regeneration returned zero with credential-like variables removed, sockets disabled, bytecode disabled, and writes captured in memory.
- `numbers.json` and `tables.md` reproduce byte-for-byte and equal round 10. `coverage.json` also reproduces byte-for-byte and equals `044091f`.
- All **533 original numeric scalars outside arrays** remain unchanged.
- `src/` diff and branch-only history are empty. Deviations are exactly **1–39**, monotonically numbered.
- The latest commit changes four files; the complete merge-base diff includes `benchmarks/` and `.gitignore`.
```text
numbers.json  412534c7222569ed736cdcb84019a0ff1efdb01273ec2e555312b515463d8ee0
tables.md     c5e939aac38fc238767dfb918f8cc10b026c9231f59329f7911e5a300c6f7e2e
coverage.json 92d115a1803c21980c74d7153cfa9632d854687742b090add08f180d710984d5
```
**The R327 repair does not survive the documented workflow.** [The generator still emits “Every rate carries…”](benchmarks/code/report_ceiling.py:1306), and the unchanged `tables.md` contains it. Running `splice_tables.main()` with its output write intercepted:
- returns **0**, reporting 11 tables spliced;
- replaces “Each rate in Table 1 carries…” with the old sentence;
- produces **25 passing report tests and two failures**: `test_no_guarantee_words_outside_their_denials` and `test_the_guarantee_check_sees_quoted_wrapped_and_trailing_uses`.
Thus the committed report is green, but regenerating and splicing its tables reintroduces the known failure.
The coverage binding has improved materially. The unpatched statistics suite now compares **all eleven figures**, asserts their key set, and passes. Both coverage tables’ current cells agree with the artifact.
| In-memory coverage attack | Result |
|---|---|
| Swap beneficial/detrimental headers | **Red** |
| Change prose “Its **0.984** is coverage…” to **0.123** | **Red** |
| Change ideal-bootstrap beneficial coverage to **0.123** in artifact and table | **Red** |
| Change that same prose **0.984 → 0.997**, a real value belonging to the other scenario | **All 27 report tests green** |
| Add “The exact grid has coverage **0.12**.” | **All 27 green** |
| Add “…coverage **twelve percent**.” | **All 27 green** |
| Add “…coverage **+0.123**.” | **All 27 green** |
| Add “The exact grid contains the true parameter in **0.123 of repetitions**.” | **All 27 green** |
| Change header `Bin(112, 0.1)` to `Bin(999, 0.1)` | **All 27 green** |
| Change that header distribution to `Uniform(112, 0.1)` | **All 27 green** |
The prose check establishes **membership in a set of values**, not attribution to a method or scenario. Its scanner recognizes unsigned `0.xxx` tokens outside brackets in text fragments containing `"cover"`. The four requested alternative formulations fall outside that implementation. Header checking establishes substring order, not the full stated distribution.
I separately confirmed that mutating each formerly omitted artifact figure—or adding a twelfth figure—fails the statistics artifact comparison. Those mutation runs replayed independent binomial sums to avoid repeating expensive inversions; the complete unpatched statistics suite separately passed.
`HISTORICAL_COVERAGE` contains the three stated values with appropriate reasons: **0.998** for the historical n=40 scenario, and **0.933/0.897** for the finite bootstrap simulations. Their presence check passes. It does not bind their occurrences to those reasons.
The guarantee check now rejects all four round-11 attacks:
| In-memory text | Result |
|---|---|
| `"every rate is bound."` | **Red** |
| `Every` + newline + `rate is bound.` | **Red** |
| `A too-generic subject cannot hide.` | **Red** |
| Trailing source comment `# every rate is bound` | **Red** |
| Forbidden word inside an ordinary code span | **Red** |
| Forbidden word inside a table cell | **Red** |
| `Every[^audit] rate is bound.` with a footnote definition | **All 27 report tests green** |
| `guaran[^audit]teed` with a footnote definition | **All 27 green** |
| `Every _rate_ is bound.` | **All 27 green** |
The underscore-emphasis case directly contradicts the general description that emphasis is removed: the implementation strips asterisks and backticks, not underscores. Both declaration tables are excised to their closing delimiters; trailing text is scanned. I also verified that adding a stale allowance makes the test fail.
The ten `ALLOWED_SENTENCES` entries are listed below in source order; long entries are identified by their distinctive wording, with the [complete literal strings at C1195](benchmarks/code/tests/test_report_consistency.py:1195).
| # | Allowed sentence | Classification |
|---|---|---|
| 1 | “Eleven overclaiming sentences across the report and both test files…” followed by the withdrawn formulations and outside-section underclaim | Historical audit-trail mentions |
| 2 | “Each sentence rewritten to what its check does…” including the token-replacement wording and historical 21-test count | Historical correction account |
| 3 | “Every rate the scanner recognises in the opening and conclusion — a numeral followed by %, pp, points or percentage points — is now bound…” ending with the count/exact-quantity exception | Qualified use; exception description remains inaccurate |
| 4 | “Intervals added everywhere named, and the rule is now mechanical: a test requires every rate the scanner recognises in the opening and conclusion to be followed adjacently by an interval, or to be a count.” | Qualified use; exception description remains inaccurate |
| 5 | “A test now requires every rate the scanner recognises — a numeral followed by %, pp, points or percentage points — in those two sections to be followed adjacently by an interval, or to be a count or an exact quantity.” | Qualified use; same remaining issue |
| 6 | “Seven words — ‘every rate’, ‘cannot hide’, ‘impossible’, ‘guaranteed’, ‘all real and correct’, ‘any other family’, ‘wherever’ — fail the build…” unless the whole sentence is allowed | Mentions describing the check; enforcement claim is too broad |
| 7 | “This is a membership check, not an attribution check…” followed by the detailed six-declaration description and family-membership requirement | Qualified description; accurately distinguishes the six exceptions |
| 8 | `def check_rate_bindings…` followed by “Every rate the scanner recognises, in those two sections, bound or declared.” | Qualified docstring use |
| 9 | `def test_rates_in_the_opening_and_conclusion_are_bound_to_their_own_keys…` followed by the bound-or-count/exact-quantity sentence | Qualified docstring use; exception description remains inaccurate |
| 10 | “It does not make re-attribution impossible: see test_documented_uncovered_cases_are_green_and_that_is_the_boundary.” | Explicit denial |
None is a bare assertion of one of the seven forbidden guarantees. **That does not make every allowed sentence accurate**, particularly entries 3–6 and 9.
The duplicate scan now visits **28 Python modules** and catches the requested second annotated `RATE_RULES`. Two limits remain:
- Appending `RATE_RULES, = ([],)` leaves **the duplicate scanner green**: tuple assignment targets are ignored. This result concerns the source scanner, not execution of the reassigned module.
- Restoring the old eight-file inventory leaves both duplicate tests green. C874’s claim that its mutation test guards against returning to that inventory is unsupported.
I walked the complete round-11 sentence list. These corrections are satisfactory, using **round-11 coordinates**: R139, R178, R195, R283, R499, R928, R949–953, R1092; C16, C24–26, C35, C287/C1047, C298/C706, C873–875, C912; S108–112, S202 and S383. R177/R775 now match the canonical quotation. R164 withdraws the unrecorded count of three additional uses. R592–595 correctly says 22 tests and limits withdrawn-conditional coverage to the beneficial scenario.
The remaining excessive or insufficiently scoped statements are:
| Current location | Remaining problem |
|---|---|
| **R140, R487** | “Every estimate interval in Tables 1–7” is a cluster bootstrap remains false. Those tables contain Wilson, Tango and exact-grid estimate intervals. Say **primary** intervals. |
| **R162, R253, R815, R977–986; C1322–1335** | Prose coverage is described as bound to measurement more strongly than the membership-only scan establishes. Header descriptions also exceed the substring-order check. |
| **C1383–1384** | Signed numbers are said to be left to interval membership checking. A standalone signed coverage value is checked by neither mechanism. |
| **R164, R989–1001; C1189–1193, C1209–1211, C1235–1236, C1267–1268** | Blanket guarantee-word/normalization claims need the actual source-text and formatting limits. Footnotes and underscore emphasis evade them. |
| **R238, R255, R823–824; C293–295, C430, C459–460, C682–683; allowances 3–5 and 9** | Counts/exact quantities do not accurately describe all six exceptions. They include the separately checked empirical headline and an approximate power-curve reading. |
| **C533–538** | Calling subject-token requirements the answer to the “whole class” of re-attribution conflicts with the documented surviving grammatical and weak-vocabulary cases. |
| **R949–951; C39, C853–863** | “No top-level name twice” / coverage of plain assignments exceeds the direct-`Name` targets actually inspected. |
| **C874–882** | The committed duplicate mutation test does not test restoration of the fixed file list. |
| **C253–256** | “Quoted spans are denials, not assertions” remains an unsupported exemption in `_current_claims`. Adding `The conclusion is "did not raise accuracy".` in live analysis prose leaves all 27 report tests green. |
| **R592–597; S3–7** | The suite is still summarized as checking each estimator against brute force or its defining property. For example, the beta-binomial test checks a broad planted-π recovery range, not the likelihood or optimum. The report also credits the file with catching the coverage failure that the independent review discovered and subsequent tests pinned. |
| **R773, R1100** | “Every table…current generated output” and “every number in this file” exceed the generated material. The Table 1 wording differs from generated output, and the normal splice restores the rejected wording. |
Two further historical statements remain stale: R3 says ten reviews have read the study, and R5 says no analysis changed after round 2 despite the later canonical-seed correction.
Deviation 34 now has **21 rows—six added to the previous fifteen**, not the commit message’s seven. The requested coverage values, mixed-family seed range, round-9 sentence-count citation, and round-11 statistics count are present and supported. Two descriptions need precision:
- **R926:** round 4 corrected the claim of **24 individually enumerated events**; the total of 24 itself was correct.
- **R933:** round 8 explicitly said “eight of the nine” was correct for the numbered set. The error was describing the expanded ten-row table as nine findings with a single author exception.
The table is not exhaustive of all numerical reporting corrections—for example, the false 46-pass claim is recorded in CORRECTIONS #30 rather than here. It should be presented as a selected inventory. The swapped-tail artifact remains correctly distinguished from published prose.
The module and both current report quotations agree after normalization, including punctuation and “those two sections.” **CORRECTIONS #29’s differing quotation is acceptable as a historical snapshot**, as stipulated; it is not an identical quotation of the current contract and is not checked by the new test.
The six manuscript placeholders should remain pending.
**no — the normal regeneration-and-splice workflow restores the exact sentence that caused round 11’s failure.**
