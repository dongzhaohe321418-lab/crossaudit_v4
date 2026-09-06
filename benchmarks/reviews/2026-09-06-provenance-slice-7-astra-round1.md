<!-- verbatim: codex exec -m gpt-6-astra, read-only, on feat/provenance-slice-7 at fe42d31; archived unedited -->

## Findings

- **P1 — E3 can shorten a numeric token and create a false pass.** `_SUBSCRIPT` rejects only ASCII continuation digits, while `_FORMULA_TOKEN` accepts Unicode digits. Consequently:
  - `Ni0.5２O`, `Ni0.5٢O`, and `Ni0.5₂O`
  - all satisfy `(0.5, "")`
  - `pair_occurrences` returns only the prefix interval `(2, 5)`
  - the real fenced interface produces no finding; E3-off produces CA-NUM-002.

  This contradicts the preregistered “not followed by a digit” rule and the claimed no-shortening property. See [numbers.py:486](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/src/crossaudit/dcl/numbers.py:486) and [PREREGISTRATION.md:29](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/benchmarks/expertlongbench/study13/PREREGISTRATION.md:29).

- **P1 — the charset test is not a formula test.** `Figure3.2`, `Table1.2`, `SampleA0.8`, `DOI10.1234`, and `version1.2` all become new empty-unit passes under E3 and block with E3 disabled. `Figure3.2` also passes through a complete `crossaudit-numbers` citation. This is precisely the “figure label / identifier” false-pass class the preregistered P1 was meant to detect; the committed rows cover only punctuated forms such as `Fig.3.2`. See [numbers.py:492](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/src/crossaudit/dcl/numbers.py:492) and [test_number_source_check.py:2262](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/tests/test_number_source_check.py:2262).

- **P1 — the integer-subscript disclosure overclaims.** `(OH)2` makes `2` citable, and `[Fe(CN)6]3−` makes `6` citable, through the pre-existing ordinary scan. Therefore the new contract and skill statements that an integer subscript “is never read” are false. The disclosure row checks only letter-glued `H2O`/`Cr2O3`, not bracket-following subscripts. See [numbers.py:1601](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/src/crossaudit/dcl/numbers.py:1601) and [PROVENANCE_NUMBERS_SKILL.md:79](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/src/crossaudit/scaffold/templates/PROVENANCE_NUMBERS_SKILL.md:79).

- **P1 — content addressing does not enforce the skill’s “quote the formula” instruction.** The interval for `0.8` is deliberately only the decimal’s characters, so a quotation of `"0.8"` passes without containing the formula context. The test pins this behavior at [test_number_source_check.py:2323](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/tests/test_number_source_check.py:2323), despite the measured 12/23 collision rate and the skill’s instruction to quote the formula.

## Verified

- Preregistration commit `e28256b` precedes all `src/` changes.
- Frozen sheet: 300 rows, all 900 line/value/unit hashes match the key.
- Live base reproduces 300/300 frozen verdicts.
- Shipped measurement reproduces R=11, W=R′=W′=0, right blocks 10/10, panel 2/97.
- All five named D64 mutations flip their stated rows.
- All eight contract and eight skill phrases occur once; deleting each defeats its phrase assertion. The integer row nevertheless does not support the sentence’s generality.
- E3 cannot satisfy a non-empty transcribed unit.
- Brackets, `·`, `−x`, and `±δ` work. Charged formulae and fully typographic/full-width decimal subscripts are refused; leading and bracket-following decimals are handled by the ordinary scan.
- No corpus prose was added: the only frozen-sheet lines copied into new text are three formula-only tokens.
- Kernel directories are untouched; `number_source` remains outside every profile; diff and worktree are clean.
- `probe.py` could not be rerun because `benchmarks/expertlongbench/data/T03MaterialSEG.jsonl` is absent and no environment override is set. The committed output agrees internally with RESULTS.
- Pytest could not be rerun because neither `.venv` nor system pytest is available; the reported 3952/4 full-suite line remains author-supplied.

**DO NOT MERGE — the single most important reason is that E3 newly accepts a strict prefix before a Unicode digit, allowing a wrong empty-unit value to pass through the real citation interface.**
