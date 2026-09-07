<!-- verbatim: codex exec -m gpt-6-astra, read-only, on fix/envelope-re-ask at 96451b4; archived unedited on the study branch (AGENTS.md §1.4) -->

## Findings

1. **High — valid file replies can now be misclassified as unterminated tool/compute envelopes.** `_unterminated_envelope()` scans the entire raw reply before `parse_work_reply()` runs ([generator.py:559](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/src/crossaudit/generator.py:559>), [generator.py:582](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/src/crossaudit/generator.py:582>)). It therefore treats marker text inside a valid output-file body as a protocol envelope.

   By execution, the base parse sequence returned a `Work` with byte-preserved content for files containing:

   - A literal `<<<CROSSAUDIT-MCP-TOOL>>>` opener.
   - The reordered tool closer/opener pair.
   - A literal `<<<CROSSAUDIT-HPC-JOB>>>` opener.

   HEAD instead denied them as tool/tool/compute format failures. This is a backward-compatibility regression for previously valid generated file content, with no regression test.

2. **Medium — the compute test still promises broader mutation coverage than it provides.** Its docstring says every request key read by the three functions is offered and that any new key read in them reddens the test ([test_format_repair.py:423](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/tests/test_format_repair.py:423>)). The regex only recognizes literal `request/payload.get("key")` and `["key"]` forms ([test_format_repair.py:442](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/tests/test_format_repair.py:442>)).

   `_resources` already dynamically reads `partition`, `account`, and `qos` through `payload.get(key)` ([hpc.py:516](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/src/crossaudit/hpc.py:516>)); those keys are absent from the example and invisible to the test. An in-memory mutation adding `"threads"` to that loop produced:

   - `reader_saw_threads=False`
   - `same_test_assertion_passes=True`

   The helper also says it stops at “same or lower indentation,” while its regex only matches the exact captured indentation ([test_format_repair.py:411](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/tests/test_format_repair.py:411>)). A lower-indentation mutation confirmed it captured the following class.

## Verification

- The three real source cuts are correct: `submit_agent` lines 720–767, `submit` 549–664, `_resources` 506–529.
- Their literal extracted keys exactly equal the example’s offered keys.
- All four plain/reordered marker cases route through `_parse_reply` to the correct envelope and matching `repair_addendum`.
- All four new tests passed by direct invocation; the three denial-translation guards passed.
- The narrated-tool name and comment now accurately stop at returning `ToolRequest`.
- AST enumeration found exactly **15** format-denial constructor sites; all carry `envelope=`.
- Amendment 2 requires all 33 instances under the merged product, excludes the probe from the rate, and `arm6-seed-unused/` exists with its note.
- T03 probe reproduced `430/365/8/57` and `596/2150`; frozen gold reproduced `R=11`, `W=R′=W′=0`, right blocks `10/10`, panel `2/97`.
- Scope is only the three claimed `src/`/`tests/` files; protected kernel directories are unchanged; worktree and `git diff --check` are clean.
- I could not independently reproduce the reported full suite because the read-only environment has no writable temporary directory; pytest fails in the autouse fixture. The reported `4008 passed, 4 skipped` remains author-supplied.

**DO NOT MERGE — the single most important reason is that the new unterminated-envelope detector scans valid output-file contents and turns replies accepted at the base into format denials, violating the hard backward-compatibility invariant.**
