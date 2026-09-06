<!-- verbatim: codex exec -m gpt-6-astra, read-only, on study/ceiling at 0911f42; archived unedited -->

## Finding

One promise still exceeds its check.

[RESULTS-CEILING.md:142](/Users/ericdong/Documents/Crossaudit/crossaudit_ceiling/benchmarks/code/RESULTS-CEILING.md:142) and [RESULTS-CEILING.md:572](/Users/ericdong/Documents/Crossaudit/crossaudit_ceiling/benchmarks/code/RESULTS-CEILING.md:572) say the conclusion’s extrapolation caveat is bound/read by a test. But [test_report_consistency.py:1562](/Users/ericdong/Documents/Crossaudit/crossaudit_ceiling/benchmarks/code/tests/test_report_consistency.py:1562) checks only whether the word `extrapolation` occurs anywhere in the conclusion.

In memory, I reversed the conclusion from:

> is an extrapolation, not a limit

to:

> is a limit, not an extrapolation

The new test and the complete 30-test report suite remained green. Thus it enforces token presence, not the claimed caveat. I found no other new promise/check mismatch.

## Verification

- HEAD `0911f423…`, direct child of `b62496701…`.
- Diff contains only `RESULTS-CEILING.md` and `test_report_consistency.py`.
- `src/`, analysis code, statistics tests, and the entire ceiling-record directory are unchanged.
- Artefacts match `b624967`:
  - `numbers.json`: `412534c…8ee0`
  - `tables.md`: `d1bf2a7…649d4`
  - `coverage.json`: `92d115a…984d5`
- Intercepted regeneration attempted exactly two writes; both were byte-identical.
- Intercepted splice: 11 tables, none missing; report unchanged at `6fe7d6f…87d0b`; conclusion caveat preserved.
- Deviations are exactly contiguous 1–39.
- Banner correctly says “Nineteenth version. Eighteen independent cross-vendor reviews.”
- Every requested mutation was red:
  - both δ values in one cell;
  - scenario cells swapped;
  - δ moved into `role`;
  - `+0.10` without `true δ =`;
  - conclusion caveat deleted;
  - headline phrase deleted;
  - extrapolation label changed in the Table 1 `no` row.
- Independent direct harnesses: 30/30 report tests and 22/22 statistics tests passed. The report suite took 2.12s. The supplied exact timings were not independently reproduced because `.venv/bin/python`/pytest is unavailable.
- Worktree remained clean.
- The six `[PENDING: ceiling r4]` placeholders must remain pending.

**No — the single most important reason is that a conclusion asserting the opposite of the required extrapolation caveat still passes every report test merely by retaining the word `extrapolation`.**
