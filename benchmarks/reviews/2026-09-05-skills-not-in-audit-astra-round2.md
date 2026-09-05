# Independent cross-vendor review of `fix/skills-not-in-audit`, round 2 — 2026-09-05

Reviewer: `gpt-6-astra`, read-only, over 223a6f1. Verdict: **do not merge**,
narrower. Case-variant and symlinked directories now refused at the loader;
property test with positive controls confirmed; no false refusal through a
symlinked root. Remaining: the constitution guard accepts `SKILLS/` and
`work/../skills/` spellings at config load; `--lang zh run` narrates the
walk-back in English; a regular file named `skills` is audited while the
refusal text says it is invisible. Verbatim below.

---

**Do not merge.** Reviewed `223a6f1ac087d85d891176b89d40e7660c2cbaf1` against `fusion/evidence-authority`, including the round-1 report. No files modified.
Validation limit: this session cannot create temporary files. Fresh repositories, the 13 test functions, and mutations were exercised with **in-memory filesystem, Git, and controller-storage adapters**, retaining production loading, filtering, checks, prompt construction, and receipt verification. These results do not replace a normal-host suite run.
| Round-1 finding | Status | Probe and result |
|---|---|---|
| 1. Case-insensitive loading | **reproduced-as-fixed** | `SKILLS/house.md` makes the loader raise `ConfigDenial`, explicitly naming `SKILLS` and instructing a rename to `skills`. |
| 2. Symlinked guidance directory | **reproduced-as-fixed** | `skills -> work/guidance` is refused before guidance loading. Target-only work remains auditable. Fresh-commit behavior differs from the requested expectation; details below. |
| 3. Constitution overlap | **fixed-but-new-problem** | Canonical and `./skills` spellings are denied, but uppercase and traversal spellings still pass config load. The strict committed-file reader provides a later denial; I did **not** reproduce an auditor-prompt bypass through those aliases. |
| 4. False-premise grep test | **reproduced-as-fixed** | All ten checks executed; filtered guidance produced no findings, positive controls produced findings, and removing the filter reddened the test. The module’s opening docstring still repeats the false premise. |
| 5. Behavior/copy | **still-present** | Guidance-only refusal translates correctly, but a fresh `crossaudit --lang zh run` still narrates walk-back in English. |
| 6. Generator mutation overclaim | **reproduced-as-fixed** | Empty loading and suppressed generator guidance both redden the test. Filtering `materialise` leaves it green, now honestly documented; the receipt-digest test catches that mutation. |
The requested path probes produced these results:
| Input | Observed behavior |
|---|---|
| `SKILLS/house.md` | Loader refuses. Root-scope and changed-path audits retain it as ordinary work. **The sentinel is present in the auditor’s work input**, so literal “absent from auditor prompt” is false. No generator prompt is constructed after loader refusal. |
| Fresh commit containing `skills -> work/guidance` and its target | Loader refuses. `cmd_run` selects the bare `skills` entry alongside the target, then raises `IntegrityDenial: increment contains a symlink: skills`. **No auditor call occurs.** |
| Subsequent target-only edit | Loader refuses; `cmd_run` reaches the auditor with `work/guidance/house.md`. Sentinel present **as work**, not loaded guidance. |
| Regular file named `skills` | Loader refuses. Root-scope filtering drops it, but `cmd_run` audits it. This contradicts the new refusal’s assertion that it is never audited and “would be invisible.” |
| `skills/house.md` symlinked file | Loader raises `ConfigDenial: refusing a symlinked skill: house.md`. |
| `work/skills/house.md` | Not loaded as guidance; retained and audited as ordinary work. |
| `./skills` | Canonical directory loads normally; `_is_house_skill("./skills/house.md")` is true. Separately, explicitly passing `directory="./skills"` to `house_dir` returns `None`; shipped callers use the default. |
| Project root reached through a symlink | Loads canonical guidance successfully in the adapter. **No P1 false refusal reproduced.** Real-host checks also confirm resolution equivalence through `/tmp`, and `house_dir(/var, "log")` accepts a real child through the symlinked root. |
**This host is case-insensitive:** the existing `src/crossaudit/skills.py` and `src/crossaudit/SKILLS.py` both exist and `samefile()` returns true.
The configuration matrix is incomplete at [config.py:295](src/crossaudit/config.py:295):
| Constitution value | Config load |
|---|---|
| `skills/house.md` | Refused |
| `./skills/house.md` | Refused |
| `SKILLS/house.md` | **Accepted** |
| `work/../skills/house.md` | **Accepted** |
`PurePosixPath.parts` neither folds case nor collapses `..`. To distinguish this from an actual auditor exposure, I also exercised the real committed-file reader against existing repository files: canonical spelling succeeds; equivalent traversal and uppercase spellings raise `IntegrityDenial`.
For the property test, the ten registered checks were `complete`, `complete-strict`, `convergence`, `declared`, `internal`, `parseable`, `provenance`, `schema`, `source_provenance`, and `units`. Using identical broken-link/TODO bytes:
- Filter enabled: **zero findings under `skills/`**.
- Positive control: `complete` reports advisory `CA-FILE-004`; `complete-strict` reports blocker `CA-FILE-004`; `internal` reports advisory `CA-FILE-003`.
- Filter removed: those same three findings appear against `skills/house.md`.
The other seven checks produce no findings on those bytes; I am not claiming independent positive controls for them.
All 13 test functions passed under the adapters. Mutation outcomes, in file order:
| Test | In-memory mutation | Result |
|---|---|---|
| Root scope | Remove house exclusion | Red |
| Explicit root | Exclude only for implicit scopes | Red |
| Generator handoff | Empty loader; suppress guidance block | Both red |
| Similar/nested names | Substring; any-component exclusion | Both red |
| Skills digest | Empty `_skills_manifest` | Red |
| Legacy receipt | Verify against newly derived scope | Red |
| All-check property | Remove house exclusion | Red |
| Explicit-SHA run | Remove skills prefix | Red |
| Plain-run walk-back | Replace catalogue call with raw current English | **Green — mutation survives** |
| Case-variant denial | Return `None` instead of refusal | Red |
| Case-insensitive premise | **No mutation specified in its docstring** | Baseline passes |
| Directory symlink | Restore old per-file-only checks | Red |
| Constitution overlap | Remove first-component guard | Red |
Restoring the *old* “ledger bookkeeping” sentence does redden the walk-back test, but through its English assertion. Its Chinese half only calls `i18n.t()` directly; it never executes the mutated command in Chinese. See [test line 443](tests/test_skills_are_not_audited.py:443).
Copy verification:
- Guidance-only refusal: actual CLI denial handling produced the expected Chinese sentence; English names house guidance correctly.
- `run.walked_back`: both catalogue entries exist. However, fresh `main(["--lang", "zh", "run"])` emits English because `cmd_run` never initializes the requested language before [the catalogue call](src/crossaudit/cli/main.py:1709). Pre-setting `i18n` to Chinese translates that line, while subsequent run narration remains English.
- Console [line 3764](src/crossaudit/console/page.py:3764) and [line 5006](src/crossaudit/console/page.py:5006): executed the extracted JavaScript objects in Node; the summary resolves to the updated English and Chinese strings. This was not a browser walkthrough.
- Both legacy Chinese denial entries still translate. The translation, slot-preservation, and **non-orphan gate tests all pass directly**.
- [Test module line 16](tests/test_skills_are_not_audited.py:16) still falsely says no deterministic check reads skill bytes and references the removed grep test.
Diff verification confirms no changes in `auditor/`, `broker/`, `ledger/`, `policy/`, `dcl/`, `receipt/`, or `controller/`. `git diff --check` passes.
**“2757 passed, 8 skipped” remains unverified.** Normal pytest stopped before collection because capture needed temporary storage. Capture-free collection also failed: 2 temporary-directory errors, with 2688 tests collected.
**Do not merge — the most important reason is that configuration load still accepts two expressly forbidden constitution aliases, leaving the requested separation guard incomplete.**
