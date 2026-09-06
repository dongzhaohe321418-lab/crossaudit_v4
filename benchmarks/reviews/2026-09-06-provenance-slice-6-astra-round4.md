# Independent cross-vendor review of provenance slice 6, round 4 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over 900efc0. Verdict: **do not merge** — the newly pinned skill
sentence "`12,5` is one number" promised a reading the checker does not
give (it reads `12,5` neither as a list nor as a number), and RESULTS'
"one per phrase in the contract and in the skill" was false for four
contract clauses. Everything else verified: all thirteen skill phrases
redden when deleted, 51 E2 rows, 62 disclosure rows, `src` unchanged since
d571871, the gold to the row. Round 5 rewords the sentence in the skill and
the contract, and pins the contract's clauses. Verbatim below; paths
shortened to the repository root.

---

## Findings
- **P1 — the new decimal-comma row does not execute the claim it pins.** The skill says `` `12,5` is one number`` at [PROVENANCE_NUMBERS_SKILL.md:72](<src/crossaudit/scaffold/templates/PROVENANCE_NUMBERS_SKILL.md:72>), but the paired disclosure row tests `5,12 °C` against `(5, °C)` at [test_number_source_check.py:2350](<tests/test_number_source_check.py:2350>). Direct behavior is:
  - `(12,5, °C)` → false
  - `(12, °C)` → false
  - `(5, °C)` → true
  The existing E2 table explicitly records that the module does **not** read `12,5` as a number at [test_number_source_check.py:2176](<tests/test_number_source_check.py:2176>). Thus phrase deletion reddens, but the associated behavior does not establish—and contradicts—the phrase’s literal promise.
- **P2 — RESULTS overstates contract coverage.** Its “one per phrase in the contract and in the skill” assertion at [RESULTS.md:67](<benchmarks/expertlongbench/study12/RESULTS.md:67>) is false. Deleting any of these exact E2 contract clauses left all 62 disclosure rows green:
  - “only the last member carries a unit expression”
  - “provided every member … is a bare number”
  - “(`12,5` is one number)”
  - “refused notation on a member stops the list”
Verified:
- All 13 E2 skill phrases—including the seven requested new phrases—have rows, baseline correctly, and redden when their exact rendered phrase is deleted in memory.
- `E2_ROWS`: 51; `DISCLOSED_LIMITS`: 62, comprising 49 pre-slice plus 13 E2 rows.
- Contract gained one sentence; skill gained two.
- `git diff d571871..900efc0 -- src` is empty.
- Gold rerun reproduced base 300/300 and shipped R=5, W=0, R′=0, W′=0, 10/10 right blocks, panel 2/97.
- Amendments 1–2 otherwise match the recorded behavior.
- Pytest was not independently rerun because this read-only worktree has no `.venv`; no files were modified.
**DO NOT MERGE — the most important reason is that the newly “pinned” `12,5` sentence still promises behavior the checker explicitly does not provide, violating the repository’s test-evidence and no-overclaim invariants.**
