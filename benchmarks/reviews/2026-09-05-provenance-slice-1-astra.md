# Independent cross-vendor review of provenance slice 1 — 2026-09-05

Reviewer: `gpt-6-astra` via Codex CLI, read-only, over `feat/provenance-slice-1`
(5b2c99d) against `fusion/evidence-authority` (0dcf36f). Commissioned per D153
because the slice touches `dcl/`, which is kernel and additive-only.

Verdict as received: **do not merge** — three P1 (two of them kernel
weakenings), three P2, and explicit negative findings on the seven mutation
guards, span scoping, path escape, `computed:`, D155 wording and the TUI fix.
The two kernel P1s were reproduced in the main session before being accepted.
The report is kept verbatim below, paths shortened. Fixes are on the same
branch and go back for a second review.

---

**Do not merge.** Comparing `feat/provenance-slice-1` (`5b2c99d`) against `fusion/evidence-authority` (`0dcf36f`), I reproduced a weakening of the existing provenance check, backward-compatibility failures, and false blockers.
1. **P1 — Fragment stripping lets previously blocked sources pass and breaks valid existing filenames.**  
   [builtin.py:163](src/crossaudit/dcl/builtin.py:163)
   With declared input `runs.csv@v3`, sources `runs.csv@v3#garbage`, `runs.csv@v3#`, `runs.csv@v3#other@evil`, and `runs.csv@v3#L999` previously produced `CA-DATA-003`; all now pass the complete science check set, even when the input has only two lines.
   The promised compensating check does not exist: [numbers.py:262](src/crossaudit/dcl/numbers.py:262) skips `results.json`, so `number_source` never validates these fragments.
   Conversely, a committed file named `runs#raw.csv`, declared and cited as `runs#raw.csv@v3`, passed before and now blocks because its source becomes `runs`. This violates both non-weakening and backward compatibility.
2. **P1 — Adding `declared` to science introduces false blockers beyond missing inputs.**  
   [profiles.py:36](src/crossaudit/dcl/profiles.py:36), [neutral.py:90](src/crossaudit/dcl/neutral.py:90)
   `check_declared` examines **every YAML file**, interpreting `inputs`, `sources`, `requires`, and `depends_on` as collections of filenames.
   A previously passing science increment with its actual input present now blocks for legitimate metadata such as `sources: [doi:10.1234/example]` or `requires: [python>=3.11]`. A scalar `sources: runs.csv@v3` is iterated character by character and generates bogus missing-file findings. `requires: 3` raises `TypeError`.
   Ordinary list entries containing `path@rev` work correctly: line 92 removes the revision before checking existence. That does not establish compatibility for the other keys and shapes newly subjected to this check.
3. **P1 — The numeric matcher both blocks exact citations and accepts different numbers.**  
   [numbers.py:76](src/crossaudit/dcl/numbers.py:76), [numbers.py:113](src/crossaudit/dcl/numbers.py:113)
   Reproduced through `run_checks`:
   | Source span | Annotation | Actual result |
   |---|---|---|
   | `-5 °C` | `-5`, `°C` | BLOCKER |
   | `-5 °C` | `5`, `°C` | PASS |
   | `9007199254740992 g` | `9007199254740993`, `g` | PASS |
   | `5  °C` | `5`, `°C` | BLOCKER |
   | `5 mg/mL` | `5`, `mg/mL` | BLOCKER |
   The number regex omits signs; conversion to `float` merges distinct integers; unit extraction permits only one intervening space and cannot consume compound units. These contradict the advertised literal-pair verification and produce non-overridable blockers on correct transcriptions.
4. **P2 — Malformed annotations can crash the check or disappear without findings.**  
   [numbers.py:226](src/crossaudit/dcl/numbers.py:226), [numbers.py:269](src/crossaudit/dcl/numbers.py:269)
   A locator containing `#L` followed by 5,000 digits raises an uncaught `ValueError`. A JSON body containing a 5,000-digit integer does likewise; only `JSONDecodeError` is caught. Both exceptions escape `run_checks` instead of producing a finding.
   Separately, [the fence regex at line 60](src/crossaudit/dcl/numbers.py:60) silently ignores an opening `crossaudit-numbers` fence without a closing fence. [Row validation at line 198](src/crossaudit/dcl/numbers.py:198) also accepts a missing `u`, treating it as unitless. A declared row can therefore evade the unit check by omitting that required field.
5. **P2 — The shipped skill is absent from a new project’s first generator prompt.**  
   [PROVENANCE_SKILL.md:2](src/crossaudit/scaffold/templates/PROVENANCE_SKILL.md:2), [cli/build.py:794](src/crossaudit/cli/build.py:794)
   A newly scaffolded science project has no current work after `TEMPLATE` is excluded. Skill selection falls back to `["experiments"]`, but the skill matches `experiments/`. I reproduced zero selected skills for both `["experiments"]` and `["work"]`.
   Consequently, the first generation receives no provenance skill, and an unannotated document passes `number_source` vacuously—the exact instruction-delivery failure the design says this slice must prevent.
6. **P2 — The benchmark reproduces numerically, but its “false blocker” classification overclaims.**  
   [provenance_arm1.py:119](benchmarks/expertlongbench/provenance_arm1.py:119)
   Reproduced exactly:
   ```text
   instances=16 numbers=430 traceable=373 uncited=57
   FALSE BLOCKERS 3/373 = 0.80% (95% Wilson 0.27–2.34%)
   ```
   However, the denominator comprises **365 normalized pair matches plus eight value-only matches**, not 373 established literal-pair citations. Finding the same numeric value does not establish that the unit merely has another rendering.
   One counted “false blocker” is `1 %` against a source stating a `1.01:1` molar ratio. That percentage is derived, and the design explicitly routes converted/computed values to `uncited`. The other two failures concern shared-unit prose, `106 and 25 μm`. The script therefore does not establish that all three are false blockers under the stated literal-containment contract.
   It also normalizes draft units before constructing annotations ([line 59](benchmarks/expertlongbench/provenance_arm1.py:59)), rather than preserving the exact draft transcription it claims to test.
**The seven mutation guards are not vacuous.** I ran their baselines and in-memory mutations.
| Guard | Result |
|---|---|
| Wrong line, line 67 | Changing the good citation to L12 fails the good-control assertion. |
| Synonyms, line 86 | Removing the table fails the baseline assertion; its inline mutation produces `CA-NUM-002`. |
| Span versus file, line 102 | Widening `_span` before the test fails line 113. The inline GREEN at line 117 checks the **same wrong-line fixture after mutation**. |
| Existence, line 123 | Removing the existence guards fails with `KeyError`; the docstring’s claim that all fixtures go GREEN is inaccurate. |
| Uncited/unannotated, line 145 | Making `uncited` blocking fails; adding an advisory only for unannotated content also fails. |
| Profile membership, line 165 | Removing `number_source` from either profile fails. |
| Missing science input, line 182 | Removing `declared` fails the missing-input assertion. |
There is also a minor documentation error at [test_number_source_check.py:110](tests/test_number_source_check.py:110): it says L11 and L12 both contain `950 °C`; L12 contains `25 °C`. The executable fixture and assertions are correct.
**Other requested results:**
- **No-`#` compatibility:** no difference found; 70 differential cases produced identical findings. Empty-path `@v3#L2` newly passes standalone provenance, but science’s existing schema check still blocks the empty path.
- **Span and scope:** no whole-file fallback found. Wrong-line matches block. `../` and absolute out-of-scope locators blocked in my probes. Resolution reads only mapping entries; it never opens filesystem paths. Committed symlinks remain refused by [gitio.py:340](src/crossaudit/gitio.py:340).
- **Synonyms:** no asymmetry found across all seven mappings in both directions. The probe and product mappings have identical keys, values, and Unicode characters; their source formatting differs.
- **`uncited` / `computed:`:** valid `uncited` rows remain advisory. No `computed:` bypass found; wrong spans still block.
- **Science scaffold:** `SCIENCE_CHECKS` matches the science profile.
- **TUI fixture:** no weakening found in [test_tui.py:529](tests/test_tui.py:529). It adds the missing input and preserves the scope/scaffold assertions and deliberately broken out-of-scope file.
- **D155 wording:** no instruction asking the generator to judge source support or state expected source contents found. It requests transcription and locations.
- **Auditor isolation:** no new skill-instruction channel into the auditor was added. However, “never by any path” is **not enforced by the existing architecture**: an audit scope including `skills/` passes those bytes through [cli/main.py:280](src/crossaudit/cli/main.py:280) into [prompt.py:86](src/crossaudit/auditor/prompt.py:86). I reproduced the complete skill in the auditor prompt as untrusted increment data. This exposure predates the branch.
- **Benchmark availability:** reproduction used the local gitignored corpus and external archived drafts. Committed files alone do not contain those inputs.
Validation: **27 focused tests passed** using `--noconftest`, with bytecode and pytest cache writes disabled. Normal pytest encountered 27 shared-fixture setup errors because temporary directories are unwritable. The full suite and TUI execution were therefore not completed. `git diff --check` passed. No files were modified.
