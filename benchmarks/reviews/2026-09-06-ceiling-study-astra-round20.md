<!-- verbatim: codex exec -m gpt-6-astra, read-only, on study/ceiling at 142494e; archived unedited -->

## Finding

One promise still exceeds its check.

[RESULTS-CEILING.md:142](/Users/ericdong/Documents/Crossaudit/crossaudit_ceiling/benchmarks/code/RESULTS-CEILING.md:142) says the caveat is bound “with its polarity,” and [RESULTS-CEILING.md:1028](/Users/ericdong/Documents/Crossaudit/crossaudit_ceiling/benchmarks/code/RESULTS-CEILING.md:1028) says the test “reads the claim, not the word.” The helper/test similarly describe detecting a reversed claim at [test_report_consistency.py:1555](/Users/ericdong/Documents/Crossaudit/crossaudit_ceiling/benchmarks/code/tests/test_report_consistency.py:1555) and [test_report_consistency.py:1585](/Users/ericdong/Documents/Crossaudit/crossaudit_ceiling/benchmarks/code/tests/test_report_consistency.py:1585).

But the implementation at [test_report_consistency.py:1565](/Users/ericdong/Documents/Crossaudit/crossaudit_ceiling/benchmarks/code/tests/test_report_consistency.py:1565) remains a literal presence check plus one forbidden literal. I appended explicit retractions while retaining every required phrase:

- Headline: “is an extrapolation in wording only; the fit is actually a limit”
- Conclusion: “is an extrapolation, not a limit in wording only; the fit is actually a limit”

`caveat_offenders()` returned no offenders, and all 31 report tests remained green. Thus the narrower description at report lines 578–581 is accurate, but “reads the claim” and “with its polarity” are not. I found no other promise/check mismatch.

## Verification

- `142494e` is a direct child of `0911f42`; only the report and consistency test changed.
- Nineteen archived ceiling-review reports support the twentieth-version banner.
- Artefacts match `b624967`:
  - `numbers.json`: `412534c…8ee0`
  - `tables.md`: `d1bf2a7…649d4`
  - `coverage.json`: `92d115a…984d5`
- Intercepted regeneration attempted exactly two writes; both were byte-identical.
- Intercepted splice attempted one byte-identical report write; 11 tables, none missing.
- No `src/`, analysis, generator, splice, coverage-measurement, or statistics-test changes from `b624967`.
- Deviations are exactly contiguous 1–40.
- Requested attacks behaved correctly:
  - Headline “is not an extrapolation” → `headline`.
  - Existing conclusion line break normalized successfully.
  - Table `no` row with “not an extrapolation” → named Table 1 row.
  - Caveat moved only to Limitations → headline, conclusion, and Table 1 named.
  - Conclusion reversal and deletion → `conclusion`.
- Guarantee scan returned no offenders, including the new names and docstrings.
- Independent runs: 31/31 report tests in 2.3s; 22/22 statistics tests in 1146.66s—53/53 total.
- Worktree remained clean.

The six `[PENDING: ceiling r4]` placeholders must remain pending.

**No — the single most important reason is that an explicitly retracted extrapolation claim still passes all 31 report tests, so the report still calls a literal-phrase check a polarity/claim check.**
