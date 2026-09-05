# Independent cross-vendor review of provenance slice 1, round 8 (final) — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over e56ae79 against f91f8bb. Verdict:
**merge**. Validation-before-write confirmed with snapshot mutations; both
creation paths proven by caller mutations (4/4 split each way); 241 exponent
cases with the old-tuple mutation failing 100/100 per sweep; all round-6/7
behaviour and the four differentials unchanged; Arm 1 unchanged. Suite
3272/8 re-run on a second host before merge. Verbatim below.

---

**Merge recommended.** Reviewed `e56ae79` against `f91f8bb`, including the round-7 report found in the integration worktree. No files modified; no remaining blocking finding in the requested scope.
| Verification | Result |
|---|---|
| Validation before writes | All three cases—`skills -> work/guidance`, `SKILLS/`, and regular-file `skills`—raise `ConfigDenial` with identical before/after tree snapshots in memory-backed execution. Moving validation after writing fails both directory-alias snapshots; the file case fails with `FileExistsError` instead. |
| Both creation paths | Baseline: **8/8 pass**. Removing the CLI invocation: **4 CLI fail / 4 console pass**; removing the console invocation reverses that split. Captured stacks prove the injection spy executes inside `wizard.run()` and `projects.create_project()`. |
| Rename-independent assertion | [The test](tests/test_number_source_check.py:1391) checks filesystem/index absence, a clean tree, and `D\t skills/provenance.md`—without the space—through `git log --no-renames … -3`. Its deletion assertion therefore does not depend on default rename detection or `R054`. This was confirmed by inspection, not a physical Git reproduction. |
| Exponent coverage | **241 exponent-related collected cases**, including **100 fenced and 100 structured parameters**, with both mismatch directions exercised inside each case. The old-tuple mutation fails **100/100 in each sweep**. Independent complete-science sweeps produce, per interface, **200 correct blocks, 400 equivalent-value passes, and 100 negative-self passes**. |
| Round-7 confirmations | Pruning through `house_dir()`, pinned digests, skills coexistence, and both front-matter keys reconfirmed. Round-6 signed notation, prose boundaries, four-line `at` bounds, spaced-unit behavior, and structured-prefix regressions remain correct. Reconstructed differentials: **216 helper / 96 declaration / 40 fenced / 40 structured**, zero differences against round 6; declarations also match base. |
| Rebase and kernel | Exactly **nine commits** above `f91f8bb`; `house_dir()` and `load()` ASTs match base. Broker, ledger, policy, receipt, and controller directories are unchanged; auditor adds only the display-name entry. DCL contains the substantive reviewed changes and is not included in that unchanged-directory claim. |
Focused execution: **471 passed, 28 filesystem-dependent cases deselected**. Filesystem and creation-path mutations used in-memory filesystem/Git substitutes; physical staging and frozen-app behavior remain unverified here. The reported **3272 passed / 8 skipped** remains for the second host and manager’s merge gate.
Before relying on `number_source`, know that it verifies declared span containment, not annotation coverage or scientific correctness; empty units impose no constraint, spaced units stop at the first token, and reported precision is normalized away.
For the owner, the hyphen dial remains strict: `g-sample` and `h-long` block shortened units to prevent compound-unit truncation, accepting false blockers on grammatical attachments unless you explicitly choose advisory treatment.
Arm 1 remains **7/365 primary, 3/8 secondary, and 13/365 without synonyms**; inspecting the seven draft locations confirms extractor truncations, so it remains regression evidence rather than a general verifier false-blocker measurement.
**Merge — the single most important reason is that the last write-before-validation defect is closed, and the regression test detects its reintroduction.**
