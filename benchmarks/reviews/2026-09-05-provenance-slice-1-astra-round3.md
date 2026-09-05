# Independent cross-vendor review of provenance slice 1, round 3 — 2026-09-05

Reviewer: `gpt-6-astra` via Codex CLI, read-only, over `feat/provenance-slice-1`
at da8ddfe against `fusion/evidence-authority`.

Verdict as received: **do not merge**, narrower again. Everything from rounds
1–2 confirmed fixed by differential probes (216 file mappings for the shared
helpers and 96 for `check_declared`, zero differences; all 45 numeric table
cases; all malformed shapes block as base; scaffold clean). Two P1s remain
with one root cause: the unit matcher accepts a PREFIX of the token, so
`5 m-2s-1` annotated `m` passes and `1e10001` truncates to `1e1000` plus a
"unit" `1` (100/100 false passes over exponents 10000–10099). The reviewer
also confirms the six Arm 1 primary blocks are harness annotation errors
(`°C/min`, `°C/h` captured as `°C`), not verifier false blockers, and that the
report discloses this candidly while the script's label does not. Verbatim
below, paths shortened.

---

**Do not merge.** Reviewed `da8ddfe` against `fusion/evidence-authority` at `6d2622f`, read-only. The named root-cause fixes work, but new probes still turn incorrect numeric citations into complete-science PASS.
1. **Root cause 1 — reproduced-as-fixed.**
   Under the complete science profile, all seven malformed shapes—missing/null/object/list/boolean value, truthy object/list unit—retain base’s `CA-DATA-003` BLOCKER for `#L999`. Head additionally emits `CA-NUM-001`.
   - Valid `myresults.json` row citing L999 of a two-line file: `CA-NUM-001`.
   - Verbatim declared `runs.csv@v3#L999`: exactly base’s single code-version ADVISORY, including identical observation text.
   - `" 5 "` and negative zero: valid matching spans pass.
   - `"1/2"`, `"NaN"`, `"inf"`: fragment-bearing citations block; fragment-free citations preserve base behavior.
   - Empty unit: complete science still emits base’s `CA-DATA-001`.
   - All six edge shapes also preserve base findings when the source is declared verbatim as opaque.
   **No new false blocker from this gate reproduced.**
2. **Shared discovery helpers — reproduced-as-fixed.**
   Compared `results_files` and `declared_inputs` directly with the functions they replaced in `57100d7`: **216 file mappings, zero differences**, including ordering.
   Coverage included the requested basenames, three directory depths, references with/without revisions, URL schemes, blank entries, scalar/dict inputs, and multiple metadata files. Separately, **180 ordinary mappings** matched base result-file discovery and declared membership.
3. **Root cause 2 — fixed-but-new-problem.**
   Independently executed **all 45 committed numeric table cases**: all passed their assertions. Requested additional probes produced:
   | Source span | Annotation value / unit | Result |
   |---|---|---|
   | `1e3 K` | `"1e3"` / `"g"` | BLOCK, `CA-NUM-002` |
   | `−5 °C` | `"5"` / `"°C"` | BLOCK, `CA-NUM-002` |
   | `5 mg/mL` | `"5"` / `"mg"` | BLOCK, `CA-NUM-002` |
   | `5 cm-1` | `"5"` / `"cm"` | BLOCK, `CA-NUM-002` |
   | `(20°C-25°C)` | `"20"` / `"°C"` | PASS |
   | `9007199254740992 g` | `"9007199254740993.0"` / `"g"` | BLOCK, `CA-NUM-002` |
   | `1.50 g` | `"1.5"` / `"g"` | PASS |
   | `0.42 1` | `"0.42"` / `"1"` | PASS |
   | Actual U+2003 or U+202F gap | `"5"` / `"°C"` | PASS |
   The raw, unquoted JSON precision probe also blocks correctly.
   `1.50` matching `1.5` agrees with the explicitly documented decimal normalization in [quantities.py:75](src/crossaudit/dcl/quantities.py:75). Significant figures are not preserved. However, the exported [contract:480](src/crossaudit/dcl/numbers.py:480) promises literal containment with unit synonyms and does not disclose numeric canonicalization; that wording remains incomplete.
   **Two P1 findings remain:**
   - **The lookahead introduces a false pass.** Source `5 m-2s-1`, annotation `"5"` / `"m"` → complete-science PASS; base blocks. Removing **only** the lookahead in memory makes the pair fail again. `5 m2s-1` behaves identically. The guard rejects the exponent continuation, then the optional exponent lets the regex return the shorter unit `m`. [numbers.py:135](src/crossaudit/dcl/numbers.py:135)
   - **The exponent bound truncates instead of rejecting.** Source `1e10001 g`, annotation `"1e1000"` / `"1"` → complete-science PASS; base blocks. The numeric regex consumes four exponent digits and treats the remaining digit as a dimensionless unit. A contiguous sweep of exponents **10000–10099 produced 100/100 incorrect PASS results**. [numbers.py:102](src/crossaudit/dcl/numbers.py:102)
   Additional unit probes:
   | Source | Full annotation | Short annotation |
   |---|---|---|
   | `5 m-2 s-1` | `"m-2 s-1"` → BLOCK | `"m-2"` → PASS |
   | `10 kg-m` | `"kg-m"` → BLOCK | `"kg"` → PASS |
   | `3 °C-1` | `"°C-1"` → PASS | `"°C"` → BLOCK |
   | `5 g-equivalent` | `"g-equivalent"` → BLOCK | `"g"` → PASS |
   | `2 h-long` | `"h-long"` → BLOCK | `"h"` → PASS |
   The hyphenated-word cases expose the parser’s lexical boundary; interpreting `h-long` as ordinary prose can justify `h`. The compound-unit cases do not establish the promised maximal matching. Removing the lookahead leaves the spaced-compound and `kg-m` failures unchanged, so those are separate limitations.
   Also, literal `.5 g` annotated `".5"` / `"g"` blocks: normalization accepts `.5`, but source extraction cannot recognize it.
4. **`check_declared` — reproduced-as-fixed.**
   - `requires: [3]`: missing `'3'` produces base’s identical BLOCKER; committed file `3` satisfies it.
   - Scalar `requires: 3`: one entry and one BLOCKER when absent, no exception; file `3` satisfies it.
   - Dict values: keys are checked exactly as base.
   - **96 list-of-strings mappings** across all four declaration keys produced byte-identical serialized findings.
   - Scalar string declarations now produce one path check and are satisfied by that file.
5. **Existence-check scheme handling — reproduced-as-fixed.**
   Provenance skips HTTP(S), uppercase HTTPS, FTP, S3, `a.b-c://`, DOI—including uppercase—and package references. Ordinary dependency text and invalid `1bad://` still block as missing local paths.
   **General-pack `check_declared` was not widened.** Lowercase HTTP(S) skips; uppercase HTTPS, FTP, DOI and package references retain base’s identical BLOCKER findings. This is included in the differential above.
6. **Skill composition — reproduced-as-fixed for fresh composition; retained-skill item still-present.**
   For source-only, number-only, both, and resolved general checks, I parsed and selected the composed skill and rendered the actual generator prompt. Only the enabled fragments appeared, across initial selections `["experiments"]`, `["work"]`, and `[]`.
   I also exercised the actual `run_audit` prompt-construction boundary, with empty evidence supplied in memory and execution stopped before provider calls or persistence: **no skill instructions reached the auditor prompt**. The separate scope route was excluded as requested.
   Round 2’s retained-skill case remains: after number checking is disabled, an existing numbers skill still selects for `["src"]` and reaches the generator. Composition happens at scaffold time; selection has no current-check gate.
7. **Arm 1 — counts reproduced; classification fixed-but-new-problem.**
   Reproduced:
   - Primary: **6/365 = 1.64%, Wilson 0.76–3.54%**
   - Secondary: **3/8**
   - Synonym ablation: **12/365 = 3.29%, Wilson 1.89–5.66%**
   Independently inspected all six corresponding draft excerpts: four contain `°C/min`; two contain `°C/h`. The harness captured only `°C`.
   These six are **harness annotation errors, not demonstrated verifier false blockers**. The continuation diagnostic originates from the draft text; checker findings are used to identify which annotations blocked.
   The diagnostic and commit message disclose this candidly. However, the script’s primary label still says “false blockers,” and its docstring calls these annotations correct “by construction.” Those statements contradict the demonstrated extraction errors. The secondary classification remains honestly separated as DERIVED.
8. **Regex hygiene — reproduced-as-fixed for provenance; broader text-locator grammar remains.**
   Complete-science structured-source probes:
   | Fragment | Result |
   |---|---|
   | `#L2\n` | `CA-DATA-003` |
   | `#L٢` | `CA-DATA-003` |
   | `#L0`, `#L00` | `CA-NUM-001` |
   | `#L1-L1` | PASS when L1 contains the pair |
   | `#L5-L2` | `CA-NUM-001`: reversed range rejected |
   An opening fence at EOF **without a newline now emits `CA-NUM-001`**.
   Qualification: fenced-text source locators still accept trailing newline and Arabic-Indic digits. Their parser strips whitespace and retains `\d`; the ASCII/absolute-end fix applies to provenance membership, not every locator parser.
Other round-2 items reverified:
| Item | Status and probe |
|---|---|
| Malformed annotations | **reproduced-as-fixed**: 5,000-digit locator/integer, unclosed fence, missing field all produce findings without exceptions |
| Fixture repairs | **reproduced-as-fixed**: 1,037 assertion ASTs unchanged across the eight previously reviewed consumers; actual fixture writer executed against an in-memory path backend produces an increment passing science |
| `available()` | **reproduced-as-fixed**: registry guard passes; inserting an unknown science check in memory makes it fail |
| Scaffold exclusion | **reproduced-as-fixed**: shipped tree through `_materialise_tree_scope` leaves only `experiments/README.md`; verdict `NOTHING_TO_AUDIT` |
| Unicode test evidence | **fixed-but-new-problem**: rows labelled U+2003/U+202F actually contain U+0020. My independent probes used the real Unicode characters and passed |
Validation: **119 focused tests passed, one filesystem-dependent test deselected**, using `--noconftest` and no pytest cache. The full suite stopped during collection because no temporary directory is writable; I cannot confirm its reported full-suite result. Diff checks passed. No files were modified.
**Do not merge — the most important reason is that malformed numeric extraction still converts base-blocked, incorrect citations into complete-science PASS.**
