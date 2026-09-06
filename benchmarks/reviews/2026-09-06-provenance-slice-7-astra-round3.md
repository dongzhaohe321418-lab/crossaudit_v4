<!-- verbatim: codex exec -m gpt-6-astra, read-only, on feat/provenance-slice-7 at efd38ff; archived unedited -->

Four findings remain at `efd38ff`:

- **P1 — the marker guard still mistakes Unicode numbers for letters.** [`_FORMULA_TOKEN`](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/src/crossaudit/dcl/numbers.py:498) retains `[^\W\d_]` after `−`/`±`. Consequently `Ni0.5O−₂`, `Ni0.5O−²`, `Ni0.5O−Ⅷ`, and `Ni0.5±₂` satisfy `(0.5, "")` through the real fenced interface; E3-off produces CA-NUM-002. These violate the stated “letter, never before a digit” restriction. An exhaustive Unicode sweep found **1,151 numeric characters** accepted after `−` in `Ni0.5O−<character>`. The letter-run fix exposed this remaining use of the old classification.

- **P1 — P2’s zero collision rate is guaranteed by construction.** [`probe.py:89`](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/benchmarks/expertlongbench/study13/probe.py:89) defines *every* matching line as an owner, excludes all owners, then tests the remaining lines with the identical matcher. Every sampled hit must therefore be false. Executing `p2_rates` on `Ni0.5O`, `Co0.5O`, and an unrelated line reports `0/1`: the other formula is excluded. The reproduced `0/3910` and `0/2205` cannot support RESULTS §2’s collision-rate assurance or the preregistered 5% kill condition. Sampling must exclude independently identified source locations, rather than every matching location.

- **P2 — sentence-final formula support misses decimals ending the token.** [`_SUBSCRIPT`](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/src/crossaudit/dcl/numbers.py:491) rejects the trailing period before punctuation stripping runs. `Ni0.5` and `Ni0.5,` pass; `Ni0.5.` yields no interval and blocks even when fully quoted. `(Ni0.5).` passes. The committed sentence-final example ends in an integer subscript and misses this boundary.

- **P3 — RESULTS still overstates the ordinary scanner.** [RESULTS §4](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/benchmarks/expertlongbench/study13/RESULTS.md:98) says it reads after “any character that is not a word character.” A period is an exception: `Ni.0.5O` refuses `(0.5, "")`. The joiner example is correct; the generalization needs qualification.

The named round-2 regressions are fixed by execution:

- Left-side mixed-script digits and `x²0.5` block; deleting the letter guard makes the stated rows pass.
- Subscript/superscript digits elsewhere pass; deleting only the digit guard makes `Ni0.5₂O` pass.
- `BaNaNa1.2`/`CoIn1.2` pass, `Nice1.2` blocks. Middle-dot and bracket-following decimals yield ordinary digit intervals only.
- The E3 source comment is corrected, `_ELEMENTS` has one definition, and the three named guards exist.

Additional verification:

- Combining marks and joiners produce no E3 readings; their immediate-before-decimal ordinary passes are pre-existing. `ℓ`, `Å`, and ligatures are refused by the element parse.
- Bracketed citations require the brackets. Tested formulae ending in integer subscripts accept sentence punctuation with or without that punctuation quoted.
- All **14 disclosure rows** pass; deleting each of the **13 unique contract phrases and 13 skill phrases** reddens its actual test.
- Gold, baseline, probe and panel counts reproduce; all **900 frozen-sheet hashes** verify. P2 has the validity defect above.
- **1,170 tests passed**, with conftest disabled and 30 temporary-directory tests deselected. The full suite failed during collection because this read-only sandbox has no writable temporary directory; its reported green run remains author-supplied.
- No copied corpus prose detected; kernel directories unchanged; `number_source` absent from all four resolved profiles; diff check and worktree clean. No files modified.

**DO NOT MERGE — the most important reason is that Unicode numeric characters still bypass the marker’s letter-only restriction and create new passes through the real citation interface.**
