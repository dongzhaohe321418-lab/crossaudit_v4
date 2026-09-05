# Independent cross-vendor review of provenance slice 1, round 2 — 2026-09-05

Reviewer: `gpt-6-astra` via Codex CLI, read-only, over `feat/provenance-slice-1`
at 57100d7 (round-2 fixes) against `fusion/evidence-authority`.

Verdict as received: **do not merge** again, narrower. Confirmed fixed:
fragment membership, malformed-annotation handling, first-prompt skill
delivery, benchmark classification, `available()`, 1,037 fixture assertion
ASTs unchanged, no scaffold P1, Arm 1 reproduces (0/365, 3/8, ablation 6/365).
Remaining: `number_source` trusts `check_units` to validate `value` and it
never does, so malformed quantities citing `#L999` pass the full science
profile; the matcher's substring fallback lets `1e3 K` annotated `1e3`/`g`
pass; and my own round-2 instruction demoted `requires: [3]` from BLOCKER to
ADVISORY, a weakening, now retracted. Verbatim below, paths shortened.

---

**Do not merge.** At `57100d7`, I reproduced previously blocked provenance inputs becoming `PASS`, plus numeric false passes. The six fixes are not sufficient.
I compared against `fusion/evidence-authority` (`e7d03c2`) and inspected the round-two diff from `5b2c99d`. No files were modified.
| Original finding | Status | Concrete probe |
|---|---|---|
| P1-1: fragment handling and missing verification | **still-present** | The named membership cases are fixed, but `results.json` with `value: null`, `unit: "K"`, and `source: "runs.csv@v3#L999"` passes the complete science profile. Base emits `CA-DATA-003`. |
| P1-2: false blockers from adding `declared` to science | **fixed-but-introduced-a-new-problem** | DOI/requirements under their original non-input keys now pass. However, `requires: [3]` changes from a base BLOCKER to a head ADVISORY, weakening an existing kernel check. |
| P1-3: numeric matching | **fixed-but-introduced-a-new-problem** | All five original examples and all 23 table rows pass their expected assertions. But source `1e3 K`, annotated as value `"1e3"` and unit `"g"`, now passes; round one rejected it. |
| P2-4: malformed annotations | **reproduced-as-fixed** | Both 5,000-digit inputs, the original unclosed fence, and a row missing `u` each produce `CA-NUM-001`, without exceptions. |
| P2-5: first-prompt skill delivery | **reproduced-as-fixed** | Parsed the shipped skill, selected against `["experiments"]`, `["work"]`, and `[]`, then rendered the generator prompt: the instruction is present. |
| P2-6: benchmark classification | **reproduced-as-fixed** | Reproduced `0/365` primary, `3/8` secondary, and `6/365` after clearing the product synonym table in memory. Draft units remain unnormalised. |
**1. Fragment rule**
The implementation performs whole-string membership first, then strips only the requested regex match. Direct base/head probes confirmed:
| Source | Head result |
|---|---|
| `runs.csv@v3#garbage` | BLOCK, `CA-DATA-003` |
| `runs.csv@v3#` | BLOCK, `CA-DATA-003` |
| `runs.csv@v3#other@evil` | BLOCK, `CA-DATA-003` |
| Declared `runs#raw.csv@v3` | PASS |
| `runs.csv@v3#L2` | Membership passes |
A 432-case differential probe found identical findings for all 398 suffixes outside the requested regex; 34 matched its permitted widening.
Two qualifications matter. Python’s `$` also matches before a final newline, and `\d` includes Unicode digits: both `#L2\n` and `#L٢` pass. These follow the supplied regex, but its meaning is broader than an ASCII fragment at the absolute string end.
Full-science compatibility is also incomplete: an **exactly declared** `runs.csv@v3#L999`, previously accepted as a revision string with an advisory, now receives a numeric BLOCKER. Whole-string precedence exists in provenance but is not respected by the new structured verifier.
**2. `results.json` verification — P1 remains**
For an ordinary numeric quantity, the compensation works:
- `#L999` against a two-line file → `CA-NUM-001`.
- `#L3` with the value on L2 → `CA-NUM-002`.
- Correct L2 containing `5 K` → no finding.
But [numbers.py:382](src/crossaudit/dcl/numbers.py:382) skips unsupported value/unit shapes with the comment “reported by units.” That assumption is false. `check_units` checks only truthiness of `unit` and `source`; it never validates `value`.
I obtained complete-science **PASS with zero findings** for `#L999` using a missing, null, object, or list value, and using a truthy object/list unit. All were blocked by base provenance. A valid numeric quantity in `myresults.json` also passes: builtin checks recognise that suffix, while `number_source` recognises only the exact basename `results.json`.
There is also a new false blocker: `{value: 0.42, unit: "1"}` citing a line literally containing `0.42 1` produces `CA-NUM-002`. Numeric unit `"1"` cannot be extracted by the matcher. Changing it to `""` instead fails `check_units`. The added structured-span test uses the empty unit and therefore does not establish full-science compatibility.
For genuinely fragment-free sources, **180 combinations produced no `number_source` findings**. The sampled existing science fixtures use those sources, so this numeric addition does not independently change their verdicts.
**3. Input existence and scaffold**
The claim that DOI, HTTPS, and dependency-style entries under `inputs` never block is **false**. [builtin.py:173](src/crossaudit/dcl/builtin.py:173) skips only lowercase HTTP(S).
| Input entry | Provenance result |
|---|---|
| `https://example.org/a@v3` | No finding |
| `http://example.org/a@v3` | No finding |
| `https://user@example.org/a@v3` | No finding |
| `doi:10.1234/example@v3` | BLOCKER |
| `python>=3.11@v3` | BLOCKER |
| `HTTPS://example.org/a@v3` | BLOCKER |
| `ftp://example.org/a@v3` | BLOCKER |
| `pkg:pypi/numpy@1.0` | BLOCKER |
Bare DOI and `python>=3.11` entries additionally violate the existing `path@revision` schema; that schema failure predates this change. The original cases under `sources` and `requires` now pass science.
**No scaffold P1 found.** I passed actual `SCIENCE_TREE` bytes through `_materialise_tree_scope`, substituting only an in-memory materialisation backend. With the shipped `experiments` scope, `TEMPLATE` is excluded, only `experiments/README.md` remains, and the verdict is `NOTHING_TO_AUDIT`. I also inspected the working-tree check’s equivalent exclusion. I did not execute disk-writing `init`.
**4. `check_declared` hardening**
Confirmed:
- Scalar `sources: runs.csv@v3`: exactly one BLOCKER when absent, none when present.
- Scalar `requires: 3`: exactly one ADVISORY, no exception.
- Thirty-two list-of-strings differential cases: identical serialised findings to base.
However, [neutral.py:101](src/crossaudit/dcl/neutral.py:101) also demotes **previously handled list entries**. `requires: [3]` previously emitted a BLOCKER for missing path `'3'`; now it emits an ADVISORY and the check permits PASS. This meets the requested shape behaviour, but contradicts the stated additive-only, never-weakened kernel rule.
**5. Fixture edits**
I sampled eight fixture-consumer files: `test_activity_stream.py`, `test_billing.py`, `test_perceived_latency.py`, `test_run_liveness_adversarial.py`, `test_tui.py`, `test_loop_integrity.py`, `test_evidence_authority.py`, and `test_source_independence.py`.
Their **1,037 assertion ASTs are unchanged**, including existing `in` comparisons. The test diff adds no skips, xfails, or commented-out assertions. Changed profile expectations remain exact equality assertions.
I executed the shared `write_increment` helper with an in-memory path implementation. It writes the declared `experiments/demo/scripts/run_demo.py`; its resulting file mapping passes science. These repairs supply genuinely absent inputs. I did not independently reproduce the claimed count of 43 affected test failures.
**6. `available()`**
Confirmed: it now imports the same builtin packs as `contracts()` before returning registered names.
The profile-membership test passes normally. Appending `unregistered-review-probe` to the science profile **in memory** makes that same test fail with:
```text
profile 'science' names unknown checks ['unregistered-review-probe']
```
**7. Numeric matcher — P1 false passes remain**
I independently executed all **23 table cases**, then the requested additions:
| Source span | Annotation | Result |
|---|---|---|
| `+5 °C` | `5`, `°C` | Match |
| `5.0 g` | `5`, `g` | Match, also in reverse |
| `1,000 K` | `1000`, `K` | Match |
| `1e3 K` | `1000`, `K` | No match |
| `−5 °C` | `-5`, `°C` | No match |
`5.0` and `5` should match under this implementation’s numeric-value contract: dropping trailing decimal zeros is explicitly documented. It does not preserve significant-figure distinctions. The skill’s exact-transcription instruction governs what the generator writes into its annotation, separately from comparison normalisation.
The unresolved problems are substantive:
- **New regression:** source `1e3 K`, annotation `"1e3", "g"` → PASS. Decimal validation rejects exponent notation, then [numbers.py:205](src/crossaudit/dcl/numbers.py:205) falls back to substring containment and ignores the unit. Round one rejected this pair.
- **Remaining sign failure:** source `−5 °C`, annotation `"5", "°C"` → PASS.
- **Remaining compound-prefix failures:** `5 mg/mL` matches `5 mg`; `5 cm-1` matches `5 cm`. These already failed semantically in round one.
- **Precision is not preserved end to end:** a raw JSON annotation value `9007199254740993.0` passes against source `9007199254740992 g`. Comparison uses strings, but `json.loads` has already rounded the numeric token through a float.
- ASCII whitespace and NBSP work. U+2003 and U+202F do not, despite the “any run of whitespace” wording.
The original malformed-input probes are fixed, with one remaining boundary: a file ending exactly in an opening ` ```crossaudit-numbers` fence, without a newline, still produces no finding because `_FENCE_OPEN` requires that newline.
**8. Arm 1**
Reproduced:
```text
instances=16 numbers=430
pair-matched=365  value-only=8  uncited=57
PRIMARY:   0/365
SECONDARY: 3/8
Synonym-table ablation PRIMARY: 6/365
```
Directly probing `draft_pairs("5 hours and 10 wt %")` preserves `"hours"` and `"wt %"`. Normalisation is used to locate candidate source lines, not to rewrite annotation units.
The value-only stratum is explicitly labelled **DERIVED**, excluded from the primary denominator, and accompanied by the reason and source-line examples. This fixes the original measurement overclaim.
**9. Skill delivery outside science**
A freshly scaffolded **general** project receives no provenance skill, so removing `applies_to` does not newly instruct ordinary general projects to annotate.
Selection itself has no check-profile gate, however. I reproduced a rendered number-annotation instruction for a custom `["source_provenance"]` configuration, which installs the combined skill without enabling `number_source`. A retained skill also selects for `["src"]` after number checking is disabled.
I classify that supported custom-configuration mismatch as **P2**: the skill asserts that checks read both fences when one will never be checked. It is misleading guidance and unnecessary output, rather than an independent blocker bypass. The combined-instruction problem existed in round one; unconditional selection broadens its delivery.
Validation: **74 focused tests passed**, with the filesystem-dependent first-project test deselected. The full suite stopped during collection because temporary directories are unwritable; I cannot confirm the team’s full-suite result. Diff checks passed, and the working tree remained clean.
**Do not merge — the most important reason is that the complete science profile still turns previously blocked, unverified `#L999` citations into PASS.**
