<!-- verbatim: codex exec -m gpt-6-astra, read-only, on fix/envelope-re-ask at a1937c9; archived unedited on the study branch -->

**One finding — Low:** The [regression-test docstring](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/tests/test_format_repair.py:502) still overclaims: moving the scan before `parse_work_reply` denies **two**, not five, accepted replies.

Executed both mutations independently in memory:

- **Scan first, blanking retained:** cases 1–3 still return `Work`; cases 4–5 deny. The exact test fails at line 528.
- **Remove blanking, parser order retained:** all five accepted replies still return `Work`; the duplicate-path reply changes from file/duplicate denial to tool/unclosed denial. The new assertion correctly fails at line 537.

Change “the five accepted replies” to “the two replies with stray openers outside file blocks.”

All 19 fixture-free format-repair tests and three translation checks passed by direct execution. `src/` is unchanged since `932076c`; scope and diff checks are clean. Full pytest remains blocked by unavailable writable temporary storage, so `4009 passed, 4 skipped` remains author-reported. No files were modified.

**DO NOT MERGE — the remaining mutation claim contradicts execution, violating the repository’s explicit no-overclaim rule.**
