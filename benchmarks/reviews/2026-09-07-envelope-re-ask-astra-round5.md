<!-- verbatim: codex exec -m gpt-6-astra, read-only, on fix/envelope-re-ask at 932076c; archived unedited on the study branch (AGENTS.md §1.4) -->

## Finding

1. **Medium — the marker-in-file regression test still makes a false mutation claim.** Its docstring says removing `FILE_BLOCK.sub(...)` makes the three valid-file cases deny ([test_format_repair.py:495](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/tests/test_format_repair.py:495>)). In-memory, I removed that exact statement and ran the exact test: **it still passed**. Since `_parse_reply` now returns immediately when the file parser succeeds ([generator.py:591](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/src/crossaudit/generator.py:591>)), the unterminated scan is never reached for those three replies.

   The blanking remains behaviorally important but unpinned: for duplicate file blocks containing a tool opener, HEAD correctly preserves the duplicate-file denial with `envelope="file"`; without blanking, it becomes the unrelated “tool envelope was opened and never closed” denial. A parser-refused case like this would test the claimed mutation. The present claim violates §3.5 by certifying a mutation it does not detect.

## Verification

- All five base-compatibility replies produced exactly equal `Work` at `d8d5210` and HEAD, including byte-identical file bodies.
- A valid file followed by an unterminated tool opener returns `Work`; with `NOTES:`, the stray opener is retained in `notes`. This matches the parser-first docstrings.
- A file containing an opener and followed by another unterminated opener also returns the same `Work` as base.
- `_function_source(hpc.py, "send_file")` stopped before the lower-indentation `def ssh_aliases`.
- Adding `threads` to `_resources`’ dynamic key loop was not detected and left the assertion passing; adding literal `payload.get("threads")` inside `submit` was detected and failed with `threads` missing. The narrowed compute-test docstring is accurate.
- The 37 unique `CROSSAUDIT` string literals had zero base/HEAD accept-versus-deny differences; nine differed only in denial text.
- All five focused no-fixture regression tests passed by direct execution.
- Exactly **15** format-denial constructor sites exist: five file, five tool, five compute; every site supplies `envelope=`.
- Scope is exactly the three claimed files. All seven protected kernel subtree hashes match base; worktree and `git diff --check` are clean.
- I could not independently run the full suite because the read-only environment has no usable temporary directory. Collection reached 3,936 tests before two import-time temporary-directory errors; the reported `4009 passed, 4 skipped` remains author-supplied.
- No files were modified.

**DO NOT MERGE — the single most important reason is that the regression test claims to kill removal of file-block blanking, but that exact mutation leaves the test green, creating the false assurance prohibited by §3.5.**
