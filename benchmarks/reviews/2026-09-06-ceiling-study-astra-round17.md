# Independent cross-vendor review of the ceiling study, round 17 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over `study/ceiling` at e62b1f8. Artefacts, regeneration, splice
and both suites reproduced; every uniqueness probe behaved as stated.
Verdict: **no** on two items: the whole-table check skipped the line after
each header blindly, so an invented row in the separator's place, a
two-column separator, reordered rows, or a changed scenario text in the
header (`+0.10` to `+0.99`, "all beneficial" to "partly") all stayed green;
and the extrapolation-label sentence named the conclusion and Table 1's
`flat?` column where the label is not read (it is checked in the headline
and Table 1's asymptote cell only). Round 18 validates the separator, the
row order and the header's true-δ text against the artefact, and rewrites
the sentence. Verbatim below; paths shortened to the repository root.

---

## Findings
1. The “whole table / every row” claim still exceeds the check. [test_report_consistency.py](benchmarks/code/tests/test_report_consistency.py:1369) promises whole-table coverage, but [line 1432](benchmarks/code/tests/test_report_consistency.py:1432) blindly skips the first line after each header.
   All 29 report tests remain green when:
   - The separator is replaced by an invented data row.
   - The separator is malformed to contain only two columns.
   - Expected rows are reordered.
   - Header truth text changes from `δ = +0.10` to `+0.99`, `δ = −0.50` to `−0.99`, or “all beneficial” to “partly beneficial”.
   Thus the test does not establish that the tables are whole or equal to the artefact as claimed here and in the report.
2. The extrapolation-location statement is incorrect. [RESULTS-CEILING.md](benchmarks/code/RESULTS-CEILING.md:573) says the label occurs in the headline, Table 1’s `flat?` column, and the conclusion.
   - The actual conclusion beginning at [line 1057](benchmarks/code/RESULTS-CEILING.md:1057) contains zero occurrences of “extrapolation”.
   - In Table 1, the literal label is in the fitted-asymptote cell; `flat?` contains `no`.
   - Removing the opening-summary occurrence leaves all 29 tests green.
   - Removing the Limitations occurrence is green, as disclosed.
   - The headline and generated Table 1 cell are enforced.
No other concrete promise/check mismatch was found in the report or three changed source files.
## Verification
- HEAD: `e62b1f84df310bdb0d9884c4c4c91c78f74fdca9`, direct child of `2851b58`.
- `src/` diff: empty.
- Ceiling-record diff: empty.
- Deviations: exactly contiguous 1–39.
- Artefact hashes match `2851b58`:
  - `numbers.json`: `412534c…8ee0`
  - `tables.md`: `d1bf2a7…649d4`
  - `coverage.json`: `92d115a…984d5`
- Intercepted regeneration attempted exactly two writes; both payloads were byte-identical.
- Intercepted splice: 11 tables, none missing; report unchanged at `7627b42…7727`.
- Independent runs: 29/29 report tests in 2.23 s; 22/22 statistics tests in 1178.18 s.
- Requested uniqueness probes:
  - Duplicate valid decoy: red.
  - Decoy plus corrupted real row: red.
  - Exact header inside a code block: red.
  - Row prefix embedded inside a sentence: green, as documented.
  - Changing the real header’s capitalization: red.
  - Appending a differently capitalized look-alike header: green; it is outside the literal prefix rule.
The six `[PENDING: ceiling r4]` placeholders must remain pending.
**No — most importantly, the purported whole-table guard blindly skips the line immediately after each header, so an invented row can replace the separator while every report check remains green.**
