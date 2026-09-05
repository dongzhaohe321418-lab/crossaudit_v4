# Independent cross-vendor review of `fix/number-source-not-default`, round 2 (final) — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over 815ea50. Verdict: **merge** — the
docstring overclaim is corrected and the new assertion
`cfg.checks == resolve("science")` demonstrably catches the profile /
`SCIENCE_CHECKS` drift that no test had guarded. Ledger spot-checks confirmed
by execution; the 101 incidental M1 failures explained as duplicate findings
from `science_with_numbers()` listing the check twice (nonblocking P3).
Verbatim below, paths shortened.

---

The original blocking item is resolved. No files were modified; the worktree remains clean.
1. **Scope confirmed.** `f6e6621..815ea50` touches only `tests/test_number_source_check.py`. Excluding docstrings, the executable changes are exactly the `resolve` import and new equality assertion. `src/` is byte-identical to f6e6621.
2. **Mutation claim confirmed.** M1 fails at `assert cfg.checks == resolve("science")`, line 859. M3 first fails the existing membership assertion; evaluating subsequent assertions separately also fails both skill-tree assertions and both rendered-prompt assertions. The corrected docstring describes behavior the assertions detect.
3. **Ledger spot-check confirmed.** Direct execution under M2 fails these three named bodies, all passing beforehand:
   - `tests/test_check_profiles.py::test_research_profile_is_the_general_pack_plus_the_provenance_checks`
   - `tests/test_number_source_check.py::test_the_check_is_registered_and_selectable_and_in_no_profile`
   - `tests/test_number_source_check.py::test_a_project_whose_checks_read_an_annotation_ships_the_skill_that_asks_for_one`
   M4 fails `tests/test_number_source_check.py::test_an_uncited_row_is_advisory_whatever_its_own_address_says`; the value-advisory test stays green. These match the raw outputs.
4. **All 101 incidental failures explained by execution.** Each produces two identical findings. Deduplicating only `science_with_numbers()` makes all 101 pass while M1 remains active. They are not independent profile guards. Leaving the helper unchanged is acceptable for this hotfix; deduplication is a nonblocking P3 follow-up.
5. **No regression found from the first review.** Production code is unchanged, baseline probes pass, and explicit opt-in still renders the numbers instruction.
Verification limits: pytest and `.venv` remain unavailable. I executed test bodies directly; scaffold probes used in-memory filesystem/setup adapters with actual configuration loading and skill/prompt rendering, not real project creation. The normal-host full-suite gate remains required; its reported totals were not independently rerun.
**Merge — the sole blocking overclaim is corrected, and the new assertion demonstrably catches the previously undetected profile drift.**
