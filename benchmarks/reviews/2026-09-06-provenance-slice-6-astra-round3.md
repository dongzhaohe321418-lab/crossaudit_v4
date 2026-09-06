# Independent cross-vendor review of provenance slice 6, round 3 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over d571871. Verdict: **do not merge** — the round-2 regression
(a skill sentence dropped by a failed patch) was pinned by one phrase only,
so the other phrases could vanish with the test green; `Matrices` and
`Indices` had no rows; RESULTS said four rows and one sentence where the
table had grown by six and the skill by two sentences. Everything else
verified: the rendered skill carries every phrase, the fenced behaviour,
the four extra labels, the gold to the row, the scope. Round 4 pins every
skill phrase to a row and corrects the counts. Verbatim below; paths
shortened to the repository root.

---

## Findings
- **P1 — the round-2 regression is not fully pinned.** The new disclosure row checks only `a word outside it does not protect a number` in the rendered skill. Removing `Step 5`, `Figs. 5`, `Step: 5`, `fixed named list`, and `with their plurals` leaves that test green—reopening the exact silent-template-loss failure from round 2. `Matrices` and `Indices` also lack committed behavioral rows. See [test_number_source_check.py](<tests/test_number_source_check.py:2338>).
- **P2 — RESULTS remains inaccurate.** It says four `DISCLOSED_LIMITS` rows bind the change, but there are six E2 additions and 55 total rows. The skill also gained two grammatical sentences, not one. See [RESULTS.md](<benchmarks/expertlongbench/study12/RESULTS.md:66>).
Verified independently:
- Rendered skill contains every claimed phrase.
- Real fenced behavior: `5,12 °C` blocks; `Heat 5, 10 mL` passes.
- Appendices, Formulae, Matrices, Indices, Supplement, and `Trial #5` block.
- All 51 `E2_ROWS` and all 55 disclosure rows execute correctly.
- Benchmark reproduced exactly: base 300/300; shipped R=5, W=0, R′=0, W′=0; 10/10; panel 2/97; exact five moved rows.
- Gold files are unchanged; round-3 scope is exactly the claimed five files; worktree and `diff --check` are clean.
- Amendment 2’s outcome claims are supported.
- I could not rerun pytest because the read-only environment provides no writable temporary directory; the claimed 1,110/full-suite results remain author-supplied.
**DO NOT MERGE — the most important reason is that the exact rendered-skill regression rejected in round 2 can recur while the new disclosure test remains green.**
