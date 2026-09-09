<!-- verbatim: codex exec -m gpt-6-astra, read-only, on fix/envelope-re-ask at f3f115b (the branch as it then was, carrying study material; since split — the code to fix/envelope-re-ask, the study files here); archived unedited -->

## Findings

1. **High — branch scope violates AGENTS.md §1.4.** The base-to-head diff modifies ten files under `benchmarks/`; the hard invariant permits only `src/` and `tests/`. No explicit scope exception is recorded.

2. **Medium — partial tool/compute envelopes still receive the file repair.** Both parsers return `None` unless the closing marker is present ([generator.py:202](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/src/crossaudit/generator.py:202), [generator.py:230](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/src/crossaudit/generator.py:230)). An unterminated MCP or HPC envelope therefore falls through as `envelope="file"` and gets the file addendum. An obeying scripted model reproduced a two-call conversational denial. This contradicts the “envelope the reply attempted” promise in code and [ATTEMPT-1.md:29](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/benchmarks/expertlongbench/study15/ATTEMPT-1.md:29).

3. **Medium — the compute test still does not execute the executor.** [test_format_repair.py:409](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/tests/test_format_repair.py:409) compares the example with a hard-coded key list. It passed even after `Manager.submit_agent` was replaced with an always-failing stub. The current schema is correct, but the test does not prove its stated executor contract under §3.5.

4. **Low — the mutation docstring names assertions that never execute.** With tool failures mutated to the file addendum, `generate()` raises at line 400; tracing confirmed none of lines 401–406 ran. The mutation does kill the test behaviorally, but neither the “first assertion” nor the re-ask assertions redden as [claimed](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/tests/test_format_repair.py:385), and the outer loop is not executed.

## Verification

- Compute example and current executor keys agree.
- All **13**, not 14, actual `category="format"` constructor sites carry an envelope attribute.
- Archive aggregates reproduce: 3 `generator_format` + 5 `answered`; 8 fixed receipts; call counts `3,3,3,3,4,4,3,3`; both four-call runs have 4,096 output tokens on call three.
- Attempt/probe wording, strict-parser statement, ceiling inference, apostrophe note, registered seed, and study-15 paths are corrected.
- Frozen gold reproduced `R=11`, `W=R′=W′=0`, right blocks `10/10`, panel `2/97`; the T03 probe reproduced its committed counts.
- The 33-item population exactly matches corpus order and the cap; median 159,917 characters.
- The three new behavioral checks passed by direct execution; the tool-to-file mutation produced the expected denial.
- The 60-test generator selection collects exactly 60 tests. Pytest execution and the full suite could not run because this sandbox has no writable temporary directory; `f3f115b` has no `src/` or `tests/` difference from the author-tested `cd0b0d5`.
- Worktree and `git diff --check` are clean; protected kernel directories are untouched.

**DO NOT MERGE — the single most important reason is that the branch violates the repository’s hard `src/`-and-`tests/` scope invariant.**
