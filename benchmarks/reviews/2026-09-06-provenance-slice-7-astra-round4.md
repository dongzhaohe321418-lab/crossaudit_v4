<!-- verbatim: codex exec -m gpt-6-astra, read-only, on feat/provenance-slice-7 at 8faa0ce; archived unedited -->

Two findings remain.

- **High — the charset still fails open for non-digit numeric symbols.** [`_formula_charset`](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/src/crossaudit/dcl/numbers.py:502) accepts `str.isnumeric()`, while the contract and skill promise “digits” and formula syntax ([contract](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/src/crossaudit/dcl/numbers.py:1699), [skill](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/src/crossaudit/scaffold/templates/PROVENANCE_NUMBERS_SKILL.md:82)). The Unicode sweep found 1,114 numeric-but-not-digit characters; 1,023 create actual E3 passes after `Ni0.5O`. Through the fenced interface, `Ni0.5OⅧ`, `Ni0.5O⑧`, `Ni0.5O⑴`, and `Ni0.5O𐄇` all pass. These include Roman, enclosed, and ancient numerals—not formula digits. The existing `Ni0.5O½` green row explicitly enshrines the mismatch. `str.isdigit()` would retain the named subscript/superscript cases while excluding these examples.

- **Low — CORRECTIONS #32 is not literally exact about its annotations.** It says “the three design passages carry a dated note” ([CORRECTIONS.md](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/benchmarks/CORRECTIONS.md:356)). There is one dated block in `PROVENANCE_CHECKS.md` §6; its two earlier false presentations remain locally unmarked, while the two `CONTAINMENT_RULE.md` references are undated inline parentheticals. The substantive diagnosis and reproduced figures are otherwise correct.

The four named round-3 findings are closed:

- The marker predicate matched `isalpha()` exactly across Unicode; the four named marker cases block through the fenced interface, and the charset mutant passes.
- P2 reproduces independently: 26 sources, 190 rows, 190 unique quote-selected owner lines, no exact/normalized location differences, 186 matcher-traceable pairs, and exactly 5/930 plus 3/930 under base and shipped. Quote location does not call the matcher; `contains_pair` only determines traceability and scores draws.
- `Ni0.5.` passes; `Fe1.2.3` and `Ni.0.5O` block; the version mutant passes.
- RESULTS §4 now states the period exception correctly.

Also verified: P1/P3 and gold measurements reproduce; all 900 frozen-sheet hashes match; 70 E3 tests and all 83 disclosure tests pass with repository `conftest` disabled; the 14 E3 disclosure rows cover 13 unique contract and skill phrases; no archive prose is committed; kernel directories are untouched; `number_source` is absent from all four profiles. The full suite could not be independently run because this read-only environment has no writable temporary directory, so §7’s `3995 passed` remains author-supplied. Worktree stayed clean.

**DO NOT MERGE — the single most important reason is that `str.isnumeric()` admits more than a thousand non-digit symbols into formula-shaped tokens, creating new unit-free passes beyond the documented rule.**
