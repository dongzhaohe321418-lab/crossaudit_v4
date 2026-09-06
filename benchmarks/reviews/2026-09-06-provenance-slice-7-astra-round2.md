<!-- verbatim: codex exec -m gpt-6-astra, read-only, on feat/provenance-slice-7 at 1141248; archived unedited -->

## Findings

- **P1 — a new left-side Unicode-digit shortening pass was introduced.** Removing `_glued_to_letter` means the ASCII-only negative lookbehind in `_SUBSCRIPT` can start after a non-ASCII decimal digit. By execution:

  - `Ni２0.5O`
  - `Ni٢0.5O`
  - `Ni२0.5O`

  all return `True` for `(0.5, "")`; E3-off returns `False`; quoting the full token passes the fenced interface. Thus `0.5` is accepted as a suffix of the numeric run preceding it, contrary to the glued-to-a-letter and no-shortening rules. The element parser does not prevent this because Unicode decimal digits are excluded from `_LETTER_RUNS`. See [numbers.py:486](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/src/crossaudit/dcl/numbers.py:486), [numbers.py:510](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/src/crossaudit/dcl/numbers.py:510), and [numbers.py:547](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/src/crossaudit/dcl/numbers.py:547).

- **P1 — `_LETTER_RUNS` is not actually a letter-run parser.** `[^\W\d_]+` includes numeric characters that Python’s `\d` excludes. Consequently `LiNi0.5O₂`, `LiNi0.5O²`, and `LiNi0.5(OH)₂` are red, while the equivalent ASCII/full-width/Arabic-decimal digit forms are green. This contradicts the declared formula charset’s “digits of any script” and the contract/skill’s broader “digits” wording. A real `isalpha()` run splitter plus an explicit immediate-letter guard is needed.

- **P2 — Amendment 1 and RESULTS overstate what replaced the letter guard.** The claim that the element parse carries “glued to a letter” is false. `_formula_subscripts("CuSO4·0.5H2O", …)` yields the entire token even though the decimal follows `·`; `pair_occurrences` also yields the ordinary digit interval, so a fenced citation quoting only `0.5` passes. RESULTS’ claim that `x²0.5` was the only independent reach of the letter guard is also disproved by `Ni２0.5O`. See [PREREGISTRATION.md:136](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/benchmarks/expertlongbench/study13/PREREGISTRATION.md:136) and [RESULTS.md:82](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/benchmarks/expertlongbench/study13/RESULTS.md:82).

- **P3 — stale and duplicated source text remains.** The E3 comment still says an integer subscript “is never read” and describes a nonexistent letter guard at [numbers.py:474](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/src/crossaudit/dcl/numbers.py:474). `_ELEMENTS` is also defined twice, at lines 444 and 502.

## Round-one closure and adversarial checks

- Right-side `Ni0.5２O`, `Ni0.5٢O`, and `Ni0.5₂O`: red as claimed.
- `Figure3.2`, `Table1.2`, `SampleA0.8`, `DOI10.1234`, `version1.2`, `pH7.4`, and `x²0.5`: red.
- `(OH)2`, `Co(NO3)2·6H2O`, and `[Fe(CN)6]3−`: ordinary-scan passes as claimed; contract and skill wording is corrected.
- Intended letter-glued fenced case: quoting `0.8` alone blocks; quoting `LiNi0.8Co0.2O2` passes.
- Bracketed formula: parentheses must also be quoted; sentence-final punctuation may be included or omitted.
- Symbol-spellable strings: `BaNaNa1.2` and `CoIn1.2` pass; `Nice1.2` is red. This is a syntactic element parse, not proof of chemical intent.
- Charges attached to tokens are red; `x/y/z/δ` variables are green, `ε` is red.
- `Co0.5`, `CO0.5`, and `Cl0.5` pass; `CL0.5` is red, consistent with the case-sensitive “any parse” rule.

## Measurements and repository checks

- Gold reproduced: `R=11`, `W=R′=W′=0`, right blocks `10/10`, panel `2/97`.
- Probe reproduced: P1 `17/0`; P2 `0/3910` and `0/2205`; P3 `12/23`.
- E3-focused selection: **51 passed**.
- Read-only-compatible portion of the focused file: **1154 passed, 30 deselected**. The remaining 30 require writable `tmp_path`; the full-suite line in RESULTS could not be independently rerun in this read-only sandbox.
- All 13 disclosure rows behaved as recorded. Their 12 unique contract phrases and 12 unique skill phrases each occur once, so deleting any listed phrase reddens its assertion.
- No corpus prose line was copied; only the previously disclosed formula-only frozen-sheet token matched.
- `auditor/`, `broker/`, `ledger/`, `policy/`, `receipt/`, and `controller/` are unchanged; only `dcl/numbers.py` changed among audit-core areas.
- `number_source` is in no profile; diff check and worktree are clean.

**DO NOT MERGE — the single most important reason is that E3 now accepts `0.5` from `Ni２0.5O` and equivalent mixed-script numeric runs, creating exactly the wrong unit-free prefix pass the guard is supposed to prevent.**
