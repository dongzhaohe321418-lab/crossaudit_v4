<!-- verbatim: codex exec -m gpt-6-astra, read-only, on feat/provenance-slice-7 at d734b50; archived unedited -->

Two record findings remain; the implementation blocker is closed.

- **Medium — RESULTS misattributes test evidence.** [RESULTS.md:70](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/benchmarks/expertlongbench/study13/RESULTS.md:70>) says “After the round-4 build” before reporting 1214 passes. Round 4 recorded 1208; 1214 belongs to round 5.
- **Low — §5’s skill-phrase inventory omits `not Roman numerals`.** That phrase is pinned for both contract and skill by [test_number_source_check.py:2561](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov7/tests/test_number_source_check.py:2561>), but appears only in RESULTS’ contract list.

Verified:

- Unicode sweep: all 680 `Nd` characters plus the 20 explicit sub/superscript digits pass in formula context; none is non-digit. The remaining 108 `isdigit()` characters are category `No` and are refused. All seven named examples match their claimed outcomes.
- The old counts reproduce: 1,114 numeric-but-not-digit characters, 1,023 former passes.
- All five withdrawn-figure sites have the promised correction or pointer.
- All §5-listed phrases occur once, map to passing behavior rows, and deletion defeats their assertions.
- Gold, probe, and all 900 sheet hashes reproduce exactly.
- Read-only tests: 163 focused tests passed; 1,184 passed with the 30 temporary-directory tests deselected. The full-suite line remains author-supplied because this environment has no writable temporary directory.
- No corpus prose detected, kernel directories unchanged, `number_source` absent from all four profiles, SyntaxWarning fixed, worktree clean.

**DO NOT MERGE — the single most important reason is that RESULTS attributes round 5’s 1214-pass evidence to round 4, leaving the study record factually false despite the correct implementation.**
