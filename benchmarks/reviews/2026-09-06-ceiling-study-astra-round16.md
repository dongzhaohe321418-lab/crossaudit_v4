# Independent cross-vendor review of the ceiling study, round 16 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over `study/ceiling` at 2851b58. Artefacts, regeneration and
splice unchanged; 29 + 22 tests pass by the reviewer's own run; five of the
six round-15 corrections verified. Verdict: **no** — the whole-table check
read the FIRST header and the FIRST occurrence of each row, so a valid decoy
table under a duplicate header, placed before the real one, hid false cells
in the real table (29 of 29 green); five smaller sentences still promised
more than a check enforces (a statistics docstring saying "the report must
say", the generator's "no optimiser that can fail to converge" and a stale
test name, "exactly" for a fit checked to a tolerance, "everywhere it
appears" for the extrapolation label, and the version banner one round
behind). Round 17 requires each header and each expected row to occur
exactly once in the report and narrows the five. Verbatim below; paths
shortened to the repository root.

---

## Round 16 findings
The claimed correction is not complete.
The requested whole-table mutations produced:
| Mutation | Result across 29 report tests |
|---|---:|
| Extra row between expected rows | Red |
| Duplicated expected row | Red |
| Correct prefix with wrong cells | Red |
| Removed row | Red |
| Second table with the same header and false cells | **Green — 29/29 pass** |
A stronger variant also passes: insert a valid decoy table before the real table, then corrupt the real table’s Tango row to `0.123 / 0.456`. All 29 report checks remain green. The parser selects the first header with `next(...)`, while cell validation uses first global row-prefix matches ([test_report_consistency.py](benchmarks/code/tests/test_report_consistency.py:1400)). This contradicts the whole-table promises in the test docstring and [RESULTS-CEILING.md](benchmarks/code/RESULTS-CEILING.md:163) and again at [line 984](benchmarks/code/RESULTS-CEILING.md:984).
### Six round-15 items
1. Only partly corrected: the four ordinary row attacks are red, but duplicate-header shadowing is green.
2. Correctly narrowed. A prose scenario substitution remains green, exactly as disclosed.
3. Correctly narrowed. Changing `0.9895` to `0.9999` leaves all 29 checks green, exactly as disclosed.
4. The module description now accurately states the bounded grid, golden-section refinement, 120 iterations, determinism, and tuning choices.
5. Correct. Both required loaders independently raise `FileNotFoundError` when their input is absent.
6. Correct. `coverage.json` contains exactly eleven method×scenario cells; `0.998`, `0.933`, and `0.897` are explicitly listed, while `0.9895` is unenforced.
### Additional promise/check mismatches
- [test_ceiling_stats.py:310](benchmarks/code/tests/test_ceiling_stats.py:310) still says “the report must say” the bootstrap under-covers. Replacing “under-covers” with “covers” leaves all 29 report tests green.
- [report_ceiling.py:506](benchmarks/code/report_ceiling.py:506) still says there is “no optimiser that can fail to converge,” although it uses golden-section optimization. [test_ceiling_stats.py:48](benchmarks/code/tests/test_ceiling_stats.py:48) likewise says exact planted data must return parameters “exactly,” but asserts tolerances on only three curves. A planted `A=0.5, τ=10000` returns approximately `A=0.1001, τ=2000`. The committed fits are safely interior, so this does not change reported estimates.
- [RESULTS-CEILING.md:569](benchmarks/code/RESULTS-CEILING.md:569) promises an unflattened asymptote is labelled as extrapolation “everywhere it appears.” Removing that label from the Limitations occurrence leaves all 29 checks green.
- The banner still says “Fifteenth version” and “Fourteen independent…reviews” at [line 3](benchmarks/code/RESULTS-CEILING.md:3), although this commit incorporates round 15 and the review branch contains fifteen prior reports.
- [report_ceiling.py:161](benchmarks/code/report_ceiling.py:161) points to a nonexistent test name; the current test is `test_replacement_intervals_cover_in_BOTH_directions`.
### Reproduction evidence
- HEAD: `2851b580c57392e8f703bc597dffe99feef8331b`
- `src/` diff: empty.
- Records diff against `645b237`: empty.
- Deviations: exactly contiguous 1–39.
- Hashes match `645b237`:
  - `numbers.json`: `412534c…8ee0`
  - `tables.md`: `d1bf2a7…649d4`
  - `coverage.json`: `92d115a…984d5`
- Intercepted regeneration attempted exactly two writes; both payloads matched the committed files.
- Splice: 11 tables, none missing, report unchanged at `6c38b55c…afff8`.
- Report suite: 29/29 passed in 2.38s.
- Statistics suite: 22/22 passed; direct equivalent harness, because `pytest` is unavailable here.
- Final worktree clean.
The six `[PENDING: ceiling r4]` placeholders must remain pending.
**No — most importantly, a duplicate coverage-table header lets a valid decoy hide false cells in the real table while all 29 report checks pass.**
