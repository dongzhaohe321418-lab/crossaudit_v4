# Independent cross-vendor review of provenance slice 1, round 4 — 2026-09-05

Reviewer: `gpt-6-astra`, read-only, over `feat/provenance-slice-1` at 331f2ee.

Verdict as received: **do not merge**, one defect left. Every round-3
counterexample fixed; the 10000–10099 sweep blocks 100/100; 216 and 96-case
differentials unchanged; 1,044 assertion ASTs unchanged; Arm 1 unchanged with
honest labels. Remaining: the unit scanner is an allowlist, so any character
outside it ends the token and a prefix passes — `5 kg.m` annotated `kg`,
`5 wt %/s` annotated `wt %`, `5 °Cβ` annotated `°C`. Also fence `at` accepts
`#L0` and `#L5-L2`; structured sources still stripped; `!`/`?` missing as
boundaries (prose regression). Fix: enumerate boundaries, everything else is
token. Verbatim below, paths shortened.

---

**Do not merge.** Reviewed `331f2ee` against `fusion/evidence-authority` at `8ba3818`, read-only. The named round-3 counterexamples are fixed, but previously unreported prefix citations still produce **complete-science PASS where base blocks**.
No files were modified.
**The remaining findings**
1. **P1 — Whole-token enforcement remains incomplete.** In [numbers.py:221](src/crossaudit/dcl/numbers.py:221), a non-sentence period falls through to the character allowlist, which excludes periods. Thus *every* period terminates the token. The percent extension at [numbers.py:247](src/crossaudit/dcl/numbers.py:247) also consumes just the percent character without checking its continuation.
   | Source | Annotation value / unit | Result |
   |---|---|---|
   | `5 kg.m` | `"5"` / `"kg"` | **PASS** |
   | `5 kg.m` | `"5"` / `"kg.m"` | `CA-NUM-002` |
   | `5 wt %/s` | `"5"` / `"wt %"` | **PASS** |
   | `5 wt %/s` | `"5"` / `"wt %/s"` | `CA-NUM-002` |
   | `5 °Cβ` | `"5"` / `"°C"` | **PASS** |
   I reproduced the short annotations through structured `results.json` citations under **all resolved science checks: zero findings**. Base emits `CA-DATA-003`. These are newly reported counterexamples, **not regressions introduced after round 3**: the short annotations also satisfy `da8ddfe`.
2. **P2 — Locator hardening is incomplete.** Fence `at: "#L0"` and `at: "#L5-L2"` both produce complete-science PASS. [_at_line()](src/crossaudit/dcl/numbers.py:312) checks syntax but neither validates positivity nor retains the range end. Structured sources still undergo `.strip()` at [numbers.py:464](src/crossaudit/dcl/numbers.py:464); malformed whitespace locators pass `number_source` alone, although `provenance` blocks them in the complete profile.
3. **The requested exponent cutoff is not implemented.** `1e999999 g`, annotated `"1e999999"` / `"g"`, **passes**, rather than emitting `CA-NUM-001`. The bound permits six exponent digits. Allocation behavior is fixed: the key is `1e999999`, without expanding zeros.
**Round-3 disposition**
| Round-3 item | Status | Probe/evidence |
|---|---|---|
| Malformed structured-value gate | **reproduced-as-fixed** | Missing/null/object/list/boolean values and invalid units retain base blockers; head adds numeric findings. |
| Opaque sources and fragment-free compatibility | **reproduced-as-fixed** | 20 shape cases produced identical direct provenance findings to base; numeric checking preserved opaque precedence. |
| Shared discovery helpers | **reproduced-as-fixed** | 216 mappings compared with round 3: zero differences, including ordering. |
| Numeric extraction | **fixed-but-new-problem** | Named counterexamples fixed; surviving prefix acceptances detailed above. |
| Numeric canonicalization disclosure | **reproduced-as-fixed** | Exported contract explicitly discloses decimal/exponent equivalence and lost precision significance. |
| `check_declared` | **reproduced-as-fixed** | 96 list mappings matched base exactly. Scalar `3`, `[3]`, dictionary keys and scalar revisioned paths block when absent and pass when present. |
| Existence-check schemes | **reproduced-as-fixed** | Focused scheme tests passed; general-pack scheme behavior also matched base in the differential. |
| Fresh skill composition | **reproduced-as-fixed** | Actual generator prompts contain precisely the enabled fragments. |
| Retained skills | **reproduced-as-fixed for keyed files; still-present for old generated files** | New `requires_check` files gate correctly. Round-3 `skills/provenance.md`, lacking the key, remains selected with `checks=[]`. |
| Auditor separation | **reproduced-as-fixed** | Intercepted three actual `run_audit` prompt hand-offs before providers/persistence: no skill instructions. |
| Arm 1 labels/counts | **reproduced-as-fixed** | Primary, secondary and ablation reproduced; corrected labels rendered. |
| Locator grammar | **still-present in part** | ASCII/exact fence syntax fixed; invalid `at` semantics and structured-source stripping remain. |
| Malformed annotations | **reproduced-as-fixed** | Executed 5,000-digit locator/integer, unclosed-fence and missing-field tests without escaping exceptions. |
| Fixture repairs | **reproduced-as-fixed** | Actual fixture writer, using an in-memory path backend, produced a science-PASS increment. All 1,044 assertion ASTs counted across eight consumers match round 3. |
| `available()` | **reproduced-as-fixed** | Registry check succeeds normally and detects an injected unknown science check. |
| Scaffold exclusion | **reproduced-as-fixed** | Actual `_materialise_tree_scope` with in-memory materialization leaves only `experiments/README.md`; verdict `NOTHING_TO_AUDIT`. |
| Unicode test evidence | **reproduced-as-fixed** | Current committed rows contain actual U+2003/U+202F/U+00A0; independent U+2003/U+202F probes pass. |
Numeric tables below use actual fenced annotations through `run_checks(..., ["number_source"])`. “BLOCK” means `CA-NUM-002` unless specified.
**Requested numeric probes**
| Source | Value / unit | Result |
|---|---|---|
| `5 m-2s-1` | `"5"` / `"m"` | BLOCK |
| `5 m2s-1` | `"5"` / `"m"` | BLOCK |
| `10 kg-m` | `"10"` / `"kg"` | BLOCK |
| `5 g-equivalent` | `"5"` / `"g"` | BLOCK |
| `2 h-long` | `"2"` / `"h"` | BLOCK |
| `1e10001 g` | `"1e1000"` / `"1"` | BLOCK |
| `(20°C-25°C)` | `"20"` / `"°C"` | PASS |
| `5 mol/(L·s)` | `"5"` / `"mol/(L·s)"` | PASS |
| `5 mol/(L·s)` | `"5"` / `"mol/(L"` | BLOCK |
| `5 m-2 s-1` | `"5"` / `"m-2 s-1"` | BLOCK |
| `5 m-2 s-1` | `"5"` / `"m-2"` | PASS |
| `1,000 K` | `"1000"` / `"K"` | PASS |
| `1,000 K` | `"1"` / `"K"` or `""` | BLOCK |
| `.5 g` | `".5"` / `"g"` | PASS |
The contiguous **10000–10099 sweep blocks all 100 truncated annotations**. The committed sweep also verifies that the real values still match.
For `m-2 s-1`, whitespace ends the token at `m-2`. That agrees with the explicit scanner boundary contract. The shipped instruction to transcribe the unit “in full” does not explain that a spaced compound unit is unsupported.
Timed whole-check probes, with `tracemalloc`:
| Value and matching source | Result | Elapsed | Peak traced allocation |
|---|---|---:|---:|
| `1e999999` | **PASS** | 0.119 ms | 6,650 bytes |
| `1e1000000` | `CA-NUM-001` | 0.082 ms | 3,641 bytes |
| `1e9999999` | `CA-NUM-001` | 0.070 ms | 3,641 bytes |
**Ordinary prose and boundaries**
| Source | Annotation/result | Assessment against the stated contract |
|---|---|---|
| `(5 °C)` | `5 / °C` PASS | Correct: unopened closing parenthesis ends token. |
| `5 °C, then` | `5 / °C` PASS | Correct comma boundary. |
| `5 °C.` | `5 / °C` PASS | Correct sentence boundary. |
| `5 °C. Then` | `5 / °C` PASS | Correct sentence boundary. |
| `5 °C: then` | `5 / °C` PASS | Correct colon boundary. |
| `5 °C¹` | `°C` BLOCK; `°C¹` PASS | Superscript belongs to the lexical token. Defensible as an exponent; cannot distinguish a footnote marker. |
| `5 °C/25 °C` | First `5 / °C` BLOCK; `5 / °C/25` PASS; `25 / °C` PASS | Slash is inside the token. Mechanically consistent, but does not interpret a slash-separated pair. |
| `5 °C—` | `5 / °C` PASS | Sensible prose result, but em dash is an additional undocumented boundary. |
| `5 ± 1 °C` | `5 / °C` BLOCK; `1 / °C` PASS | Shared trailing unit is not propagated. Defensible under adjacency-only matching. |
| `5 °C ± 1` | `5 / °C` PASS | Correct whitespace boundary. |
| `5 %`, `5%` | `5 / %` PASS | Both correct. |
| `a 5 g-sample` | `g` BLOCK; `g-sample` PASS | Matches the requested lexical rule, although the physical unit is `g`. |
| `2 h-long` | `h` BLOCK; `h-long` PASS | Same limitation, intentionally enforced by this fix. |
I also found a **new ordinary-prose blocker introduced since round 3**: `5 °C!` and `5 °C?` previously matched `°C`; both now block. The checker requires `°C!` or `°C?`. This follows the supplied exhaustive boundary rule, which omits `!` and `?`, but it is an ordinary-prose usability regression.
**Ranges**
| Source | Observed behavior |
|---|---|
| `20°C-25°C` | Both `20 / °C` and `25 / °C` PASS. |
| `20-25 °C` | `20 / °C` BLOCK; `25 / °C` PASS. No shared-unit propagation. |
| `20 °C - 25 °C` | Both endpoints PASS. |
| `1-2 h` | `1 / h` BLOCK; `2 / h` PASS. |
| `pH 7-8` | Both values PASS with empty unit; both BLOCK with unit `pH`, which precedes the numbers. |
The range hyphen is not mistaken for a negative sign: `-25`, `-2` and `-8` block in those respective ranges.
**Other false-PASS probes and numeric equivalence**
- Arabic-Indic/fullwidth **annotation values** produce `CA-NUM-001`. ASCII annotations against corresponding Unicode source digits produce `CA-NUM-002`.
- `10⁵ g` does not match either `10 / g` or `100000 / g`.
- `5×10³ g` does not match either `5 / g` or `5000 / g`.
- However, empty-unit annotations **`10 / ""` against `10⁵ g` and `5 / ""` against `5×10³ g` pass**. Unsupported numeric notation can still satisfy a numeric prefix when the annotation omits its unit. Both behaviors predate this round.
- `5e3 g` versus `5000 / g`, `-0 g` versus `0 / g`, and `0.50` versus `0.5 / ""` all PASS. These equivalences agree with the updated exported contract’s numeric canonicalization.
**Every requested locator parser**
Here `001`/`003` abbreviate `CA-NUM-001`/`CA-DATA-003`. Structured fragments were attached to a declared `path@revision`; source lines contained the matching pair.
| Malformed locator | Fence `at` | Fence `src` | Results `source`: number check alone | Results: provenance + number |
|---|---|---|---|---|
| `#L١١` | 001 | 001 | No finding | 003 |
| `#L11\n` | 001 | 001 | No finding | 003 |
| ` #L11` | 001 | 001 | No finding | 003 |
| `#L3\n` | 001 | 001 | No finding | 003 |
| `#L0` | **PASS** | 001 | 001 | 001 |
| `#L5-L2` | **PASS** | 001 | 001 | 001 |
A separate probe with whitespace before the entire structured source also confirms stripping.
**40 well-formed fence locators**—single lines/ranges, relative/root paths, short/full SHA pins—produce identical serialized findings to round 3. **Another 40 structured locators** also match exactly.
**Skills compatibility and hand-off**
The sole production `select()` caller is [cli/build.py:794](src/crossaudit/cli/build.py:794); it passes `cfg.checks`. Existing two-argument calls and three-/four-argument `Skill` construction remain valid.
I exercised 24 selections across source-only, number-only, both, general, empty and unknown check lists, rendering the actual generator prompt. The number fragment follows `number_source`; `crossaudit-sources` follows `source_provenance`. `checks=None` preserves all otherwise scope-matching skills.
Twenty hand-written skills without front matter produced identical bodies, scopes, rendered guidance and manifests to round 3 across 16 selection combinations each. Ungated skills were never removed. Consequently, the old generated combined skill also remains ungated; there is no migration.
Three actual `run_audit` hand-offs were intercepted after prompt construction, with empty tool evidence and execution stopped before provider calls or persistence. None contained house-skill instructions.
**Arm 1 and validation**
The executed harness reproduced:
- Primary: **6/365 = 1.64%, Wilson 0.76–3.54%**.
- Secondary: **3/8**.
- Synonym ablation: **12/365 = 3.29%, Wilson 1.89–5.66%**.
The output now says “blocked, of pair-matched citations,” identifies an upper bound, and reports **6 of 6 harness-annotation errors**. Independent rereading found four `°C/min` and two `°C/h` draft excerpts. No measurement count moved.
The full-suite attempt used the requested command with bytecode/cache writes disabled and capture disabled. It stopped with **two collection errors** because temporary directories are unavailable. I cannot confirm **2892 passed, 8 skipped**.
Focused execution produced **158 passed, 1 deselected, 12 filesystem-fixture errors**. The deselected test creates a fresh project. The 12 errors are existing skills tests requiring `tmp_path`; all **15 existing skills test functions additionally passed with an in-memory Path backend**, which does not substitute for host filesystem validation.
Diff checks passed. Broker, ledger and policy are unchanged; the auditor change is an additive display-name entry. The unresolved base-BLOCK-to-science-PASS cases prevent an additive-only correctness sign-off.
**Do not merge — the single most important reason is that incorrect prefix citations still pass the complete science profile.**
