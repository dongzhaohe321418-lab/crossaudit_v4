# Independent cross-vendor review of provenance slice 6, round 5 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over 3998985. Verdict: **do not merge** — the decimal-comma
disclosure rows annotated the value 5 (the fixture's hard-coded value) and so
never tested `12,5`; RESULTS still said "`12,5` one number"; two phrases
("write `uncited` for a decimal-comma value", "every member states that
unit") survived deletion; the refused-notation row was paired with `(5, Pa)`,
which the stop's deletion leaves red. Verified otherwise: 51 E2 rows, 67
disclosure rows, the `12,5` behaviour, `src` unchanged in the matcher. Round
6 lets a disclosure row carry its own value, pins the four phrases with the
behaviour that tests them, and states which phrases are pinned rather than
claiming completeness. Verbatim below; paths shortened to the repository
root.

---

## Findings
- **P1 — decimal-comma disclosure rows still do not execute the claim they accompany.** Both new rows use `5,12 °C`, but the test function hardcodes the annotated value as `"5"` ([test_number_source_check.py:2350](<tests/test_number_source_check.py:2350>), [test_number_source_check.py:2377](<tests/test_number_source_check.py:2377>)). They establish only that the prefix `5` does not inherit `°C`; neither row tests whether `5,12` is “a number this checker reads.” The separate E2 row at line 2176 does test the full decimal-comma value, but it is not the behavior paired with the disclosure phrase.
- **P1 — RESULTS retains the round-four overclaim.** It still says “`12,5` one number” ([RESULTS.md:52](<benchmarks/expertlongbench/study12/RESULTS.md:52>)), although the checker returns false for `(12,5, °C)`. Amendment 2 correctly says it is not read as a number ([PREREGISTRATION.md:93](<benchmarks/expertlongbench/study12/PREREGISTRATION.md:93>)).
- **P1 — the claimed phrase/clause completeness remains false.** In-memory deletion showed:
  - Deleting the four named contract clauses reddens 1, 2, 1, and 1 rows respectively.
  - Deleting skill phrases “is not a list” or “nor a number this checker reads” reddens one row each.
  - Deleting the newly added skill instruction “write `uncited` for a decimal-comma value” reddens **zero** rows.
  - Deleting the contract outcome “every member states that unit” reddens **zero** rows.
  Therefore RESULTS’ “one per phrase in the skill and one per clause” statement ([RESULTS.md:67](<benchmarks/expertlongbench/study12/RESULTS.md:67>)) is unsupported.
- The refused-notation disclosure row uses `(5, Pa)` ([test_number_source_check.py:2359](<tests/test_number_source_check.py:2359>)), even though the test’s own mutation explanation says this result remains blocked when the stop is deleted; `(5, ×)` is the behavior that reddens ([test_number_source_check.py:2220](<tests/test_number_source_check.py:2220>)).
Verified:
- `E2_ROWS=51`; `DISCLOSED_LIMITS=67`.
- All current E2 and disclosure-row assertions pass through a read-only direct runner.
- `12,5 °C`: `(12,5, °C)` false, `(12, °C)` false, `(5, °C)` true.
- The four claimed clause examples produce the recorded outcomes.
- `git diff 900efc0..HEAD -- src` contains only the contract and skill wording changes; matcher behavior is unchanged, so the previously verified gold result is unaffected.
- I could not independently rerun pytest because this checkout has no `.venv` and system Python lacks pytest. No files were modified.
**DO NOT MERGE — the single most important reason is that the disclosure matrix and RESULTS still claim complete behavior-backed coverage while multiple semantic phrases survive deletion or are paired with behavior that does not test them, violating the repository’s no-overclaim evidence rule.**
