# Independent cross-vendor review of provenance slice 6, round 1 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over 4a70b83. Verdict: **do not merge** — three P1s: the label
guard missed plurals (`Figs.`, `Pages`, `Schemes`) and a colon after the
label (`Step:`); a comma with no whitespace after it read a decimal comma as
a list (`12,5 °C` gave `(12, °C)` where the base blocked it); and the
refused-notation mutation test did not redden (the mutant offers `×`, not
`Pa`). Everything else reproduced: base 300/300, shipped R 5 on the five
named rows, W 0, R′ 0, W′ 0, panel 2/97, the quotation and cross-line
behaviour, the guard, nested separators, E1 inside E2, the ablations. Round
2 widens the label list with its plurals and the colon, requires whitespace
after a comma separator, and asserts the mutation's real effect. Verbatim
below; paths shortened to the repository root.

---

Do not merge.
Findings:
- **P1 — the label guard has false-PASS holes.** `_LABEL_WORDS` claims label plurals but omits `figs`, `eqs`, `schemes`, `chapters`, `parts`, `phases`, and `stages`; `_LABEL_BEFORE` also recognizes only an optional period, not common forms such as `Step:`. Through the real fenced interface, all of these incorrectly pass with no finding:
  - `Figs. 5, 10 °C` → `(5, °C)`
  - `Step: 5, 10 mL` → `(5, mL)`
  - `Pages 5, 10 and 20 were reviewed` → `(5, were)`
  `Figs. 5, 10 °C` is `False` at the merge base and `True` here, so this is introduced by E2. See [numbers.py:310](src/crossaudit/dcl/numbers.py:310) and the narrowly sampled tests at [test_number_source_check.py:2166](tests/test_number_source_check.py:2166).
- **P1 — decimal-comma notation becomes a new false PASS.** `_LIST_TAIL` accepts a comma with no required whitespace at [numbers.py:317](src/crossaudit/dcl/numbers.py:317). Consequently, locale-formatted `12,5 °C` annotated as `(12, °C)` is `False` at e890dfe, `True` at 4a70b83, and passes the fenced interface. The requested `5,5 °C` also passes, although that exact repeated-digit case already passed at base by matching the second `5`; E2 additionally offers the first occurrence. This ambiguity is not disclosed in `RESULTS.md`.
- **P1 — the refused-notation mutation test does not redden.** Deleting the explicit stop at [numbers.py:849](src/crossaudit/dcl/numbers.py:849) leaves the asserted `(5, Pa)` result unchanged, so [test_number_source_check.py:2207](tests/test_number_source_check.py:2207) stays green. The mutant actually offers `×` and makes `(5, ×)` pass. Thus the preregistered claim that this mutation reddens is false, violating the repository’s “test must execute what it claims” rule.
Verified successfully:
- Merge-base live `contains_pair`, loaded directly from e890dfe: **300/300** against `base-verdicts.jsonl`; 166 passes; matcher blob matches.
- `measure.py --config base`: **0/0/0/0**, 10/10, panel 2/97.
- `measure.py --config shipped`: **R=5**, W=0, R′=0, W′=0; exact five named rows; 10/10; panel 2/97.
- Study 12 base differs from study 11 on exactly 14 E1 rows.
- Preregistration commit be0de4e precedes every `src/` change.
- Quote containing only `0, 20, 40` blocks with CA-NUM-002; including `wt.%` passes.
- Cross-line list quotations block with CA-NUM-002.
- `5, 10 and 20 wt.% Ni`, `5 and 10 %`, and nested separators pass.
- A superscript/power-of-ten last member blocks; `1e3` remains a valid numeral.
- `5–10, 20 °C`: `(5, °C)` blocks; `(10, °C)` passes.
- `5, 10 kg, or 20 μm`: `(5, μm)` blocks and `(5, kg)` passes.
- E5, E6, E1, and E2 named ablations redden their positive rows; E2-off leaves earlier families intact.
- Source diff is confined to E2, its contract, and its skill guidance. Kernel and frozen gold/design files are untouched; `number_source` is absent from every profile.
- `git diff --check` is clean; worktree remains clean.
I could not independently rerun pytest because this read-only worktree has no `.venv` and the available Python lacks pytest; the reported full-suite result therefore remains author-supplied.
**DO NOT MERGE — the most important reason is that E2 introduces reproducible fenced-interface false PASSes on ordinary labelled and decimal-comma text, precisely the enlarged false-PASS surface this slice needed to constrain.**
