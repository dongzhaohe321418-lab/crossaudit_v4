# Independent cross-vendor review of provenance slice 1, round 7 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over 6ea38ba (rebased onto f91f8bb).
Verdict: **do not merge yet**, two P2s: annotation-skill creation writes into
the skills directory before `house_dir()` validates it, so under an alias it
writes into the rejected destination and then raises; and two tests overstate
their coverage (both creation-path labels reach one helper; the structured
exponent sweep samples four points). Exponent fix, pruning through
`house_dir()`, coexistence, the eight-commit rebase, all round-6 behaviour,
the four differentials and Arm 1 confirmed. Verbatim below, paths shortened.

---

**Do not merge yet.** Reviewed `6ea38ba` against merge base `f91f8bb`, read-only. The exponent defect is fixed, but creation still writes through an alias before rejecting it.
1. **P2 — Directory validation happens after writes.** At [wizard.py:217](src/crossaudit/cli/wizard.py:217), `annotation_skills_owned()` calls `write_tree()` before pruning invokes `house_dir()`.
   With `skills -> work/guidance`, memory-backed execution of the production helper produced:
   ```
   write work/guidance/provenance-numbers.md
   write work/guidance/provenance-sources.md
   raise ConfigDenial
   ```
   The legacy file survives, as claimed, but creation has already written into the rejected destination. The case-insensitive `SKILLS/` simulation behaves identically. Validate the directory before writing annotation skills, and test that rejection leaves the destination unchanged. This reproduction used an in-memory filesystem; no physical files were written.
2. **P2 — The regression tests overstate their coverage.**
   - [The “both creation paths” test](tests/test_number_source_check.py:1334) maps both labels to `wizard.annotation_skills_owned()`. Every initial project is created through the console helper; the legacy file is added afterward. It exercises real-git helper integration, but cannot detect removal of the CLI caller’s invocation. Inject the legacy file before each actual creation path reaches the helper.
   - [The structured exponent test](tests/test_number_source_check.py:1558) samples `[1, 5, 23, 100]`, rather than sweeping 1–100 as claimed. My independent contiguous sweep passes, but the committed regression should retain that coverage.
The remaining requested checks confirmed:
| Probe | Result |
|---|---|
| Canonical numbers | `1e+5`, `1e5`, and `100000` have equal keys; `1e-5` differs. |
| Exponents 1–100, both interfaces | Per interface: **200 correct blocks, 400 equivalent-value passes, 100 negative-self passes**, under complete science. |
| Four requested `results.json` cases | **BLOCK, BLOCK, PASS, PASS**, respectively. |
| Old-tuple mutation | Per interface: **100 false passes in each direction**, plus **100 false blockers in each equivalence direction**. |
| Pruning itself | Uses only the directory returned by `house_dir()`; rejects aliases without deleting the legacy file. All three pinned digests match. Canonical tracked/untracked ownership and absent-file behavior pass in memory. |
| Skills coexistence | Hand-written skill plus numbers selected for `checks=["number_source"]`; all three for `None`. Malformed directories refuse loading before reading any skill, in memory-backed execution. Both front-matter keys parse. |
| Rebase | Exactly **eight commits**. `house_dir()` and `load()` ASTs match base. Protected directories are unchanged except the auditor display-name addition. |
| Round-6 behavior | Signed notation, complete prose-boundary sweep, four-line `at` bounds, spaced-unit behavior table, and structured-prefix regressions remain correct. |
| Differentials | **216 helper, 96 declaration, 40 fenced, 40 structured** cases: zero differences against git-loaded round 6. Declaration cases also match base. These are reconstructed corpora, not preserved historical probe inputs. |
| Arm 1 | **7/365**, **3/8**, and synonym ablation **13/365**, unchanged. |
Focused execution: **375 passed, 25 filesystem-dependent cases deselected**, with `--noconftest` and writes disabled. Actual git staging/committing and physical alias behavior remain unverified here. The fresh-project test is unchanged from round 6 but was not rerun. The **3173/8** full-suite claim remains for the second host. `git diff --check` passes; the checkout remains clean.
**Do not merge — the most important reason is that annotation-skill creation writes through a directory alias before the boundary validator rejects it.**
