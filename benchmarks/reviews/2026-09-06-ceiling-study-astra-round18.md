# Independent cross-vendor review of the ceiling study, round 18 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over `study/ceiling` at b624967. Every separator, order, cell and
header attack of round 17 is red; artefacts, regeneration and splice
unchanged; 29 + 22 tests by the reviewer's own run. Verdict: **no** on three
items: the header's true-δ values were read header-wide, so both could sit
in one cell; the extrapolation sentence said the conclusion carried the
caveat "in other words" and it did not; the banner was a round behind.
Round 19 binds each δ to its cell, puts the caveat in the conclusion and
binds all three places with a test, and fixes the banner. Verbatim below;
paths shortened to the repository root.

---

## Findings
1. The new header check still overclaims per-scenario binding. [test_report_consistency.py](benchmarks/code/tests/test_report_consistency.py:1459) extracts δ tokens from the entire header, not their cells. This mutation leaves all 29 tests green:
   `beneficial, true δ = +0.10; true δ = −0.50 | detrimental |`
   The detrimental column contains no δ, contradicting the comment that “the true delta of each scenario” is bound to the artefact.
2. The rewritten extrapolation sentence remains partly false. [RESULTS-CEILING.md](benchmarks/code/RESULTS-CEILING.md:573) correctly describes:
   - Headline label: enforced.
   - Table 1 asymptote-cell label: enforced through the splice check and generated at [report_ceiling.py](benchmarks/code/report_ceiling.py:1337).
   - Second opening occurrence and Limitations occurrence: unchecked; deleting either leaves 29/29 green.
   But the conclusion does not carry the unflattened-curve/extrapolation caveat “in other words.” It does not discuss that fit and instead says “repetition saturates quickly.” Also, the earlier audit-trail row still falsely says the caveat is in Table 1’s `flat?` column and conclusion ([RESULTS-CEILING.md](benchmarks/code/RESULTS-CEILING.md:142)).
3. Minor bookkeeping: the report still calls itself the “Seventeenth version” with sixteen reviews ([line 3](benchmarks/code/RESULTS-CEILING.md:3)); `b624967` incorporates round 17, so both counts are one behind.
## Verification
- HEAD `b624967`, direct child of `e62b1f8`.
- Diff: only the report and report-consistency test.
- `src/` diff empty; analysis code, statistics tests, and ceiling records byte-identical.
- Artefact hashes unchanged:
  - `numbers.json`: `412534c…8ee0`
  - `tables.md`: `d1bf2a7…649d4`
  - `coverage.json`: `92d115a…984d5`
- Intercepted regeneration: two writes, both byte-identical.
- Intercepted splice: 11 tables, none missing, report unchanged at `18efff8…c627`.
- Deviations exactly contiguous 1–39.
- Requested mutations:
  - Red: separator replaced by row; two-column separator; reordered rows; `+0.99`; “partly beneficial”; extra trailing pipe; extra row cell; changed `n`; `+0.1`.
  - Green as documented: moved alignment colons.
- One- and two-hyphen delimiter cells are accepted, but this is not a defect under the [GFM table specification](https://github.github.com/gfm/#tables-extension).
- Tests:
  - Report: 29/29 passed in 2.4 s.
  - Statistics: 22/22 passed in 1179.22 s.
  - `pytest` was unavailable locally, so I executed every test function directly.
- Worktree unchanged.
The six `[PENDING: ceiling r4]` placeholders must remain pending.
**No — most importantly, the report still claims the conclusion carries the extrapolation caveat, but the conclusion contains no equivalent caveat.**
