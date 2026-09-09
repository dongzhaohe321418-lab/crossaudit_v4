<!-- verbatim: codex exec -m gpt-6-astra, read-only, on fix/envelope-re-ask at 47b7a20; archived unedited on the study branch (AGENTS.md §1.4) -->

## Findings

1. **Medium — unterminated-envelope routing is still incomplete.** `_unterminated_envelope()` tests whether a closer exists anywhere, not whether it follows the opener ([generator.py:559](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/src/crossaudit/generator.py:559>)). By execution, both reordered forms—closing marker followed by opening marker—fall through as `envelope="file"` and receive the file re-ask. The opener remains genuinely unclosed. The new test covers only the easier case where no closer exists anywhere.

2. **Medium — the compute test still overstates its executor coverage.** The extraction does land on `Manager.submit` ([hpc.py:549](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/src/crossaudit/hpc.py:549>)), but extracts only `host_id` and `script`. It does not inspect the generator-facing `submit_agent` request keys ([hpc.py:720](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/src/crossaudit/hpc.py:720>)) or keys read by `_resources`. An in-memory mutation adding `payload.get("threads")` to `_resources` left the test green, disproving its claim that any new executor-read key reddens it ([test_format_repair.py:410](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/tests/test_format_repair.py:410>)). The present example itself is correct.

3. **Low — the narrated-tool test still claims execution it does not perform.** Its name and setup comment say the clean request “then executes,” but the test stops after `generate()` returns a `ToolRequest`; no MCP executor is invoked ([test_format_repair.py:385](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/tests/test_format_repair.py:385>)). The mutation documentation itself is now accurate: mutating tool repair back to the file addendum raised a conversational `ProviderDenial` at the `generate()` call on line 398, before any assertion.

4. **Study provenance follow-up.** The probe archive was produced at `066a7a1`, while this branch subsequently changed parser behavior. The preregistration at `f9a5241` says the parser was unchanged and explicitly requires those eight instances to be rerun if review changes the fix. This is not a scope violation in the rebuilt branch, but the archived probe cannot be presented as measuring `47b7a20` without honoring that rule.

## Format-site enumeration

There are **15 actual `ProviderDenial(category="format")` constructor sites, not 14**: the prior 13 plus separate tool and compute unterminated sites. All 15 carry the expected envelope attribute, confirmed by direct execution:

- File: lines 135, 140, 316, 325, 330.
- Compute: lines 207, 212, 217, 220, 584.
- Tool: lines 236, 241, 246, 249, 581.

## Other verification

- Scope is correct: only `generator.py`, `cli/denials_zh.py`, and `test_format_repair.py`; no `benchmarks/`, docs, or packaging changes.
- All seven protected kernel directory trees are byte-identical to `d8d5210`.
- Worktree and `git diff --check` are clean.
- The four new tests and six relevant translation guards passed by direct invocation.
- The generator selection collects exactly 61 tests.
- Archives reproduce 8 failed attempt records at $0.365085 and 8 successful probe records at $3.351148, with generator-call counts `3,3,3,3,4,4,3,3`.
- The T03 probe reproduced its committed aggregate counts.
- Pytest and the full suite could not run normally because the read-only sandbox has no writable temporary directory; the reported 4,008-pass result remains author-supplied.

**DO NOT MERGE — the single most important reason is that an envelope whose closer precedes its opener is still routed to the file repair, contradicting the new guarantee that an opened-but-unclosed tool or compute envelope receives its own re-ask.**
