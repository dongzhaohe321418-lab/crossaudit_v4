<!-- verbatim: codex exec -m gpt-6-astra, read-only, on fix/envelope-re-ask at 3fe8dd9; archived unedited -->

## Findings

1. **High — the compute repair teaches a non-executable envelope.** The shipped contract requires `host_id`, `name`, `script`, `inputs`, `outputs`, and `resources`; the new addendum instead shows `host`, `command`, and `inputs` ([generator.py:524](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/src/crossaudit/generator.py:524)). Downstream execution looks up `host_id` and reads `script` ([hpc.py:720](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/src/crossaudit/hpc.py:720)). A model following the corrective instruction therefore produces a parsable `ComputeRequest` that cannot request the intended compute job. The new test repeats the wrong schema and checks only the parser class and prompt marker, never execution ([test_format_repair.py:394](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/tests/test_format_repair.py:394)). This violates §3.5.

2. **Medium — routing by substring is not correct for every parser message.** I enumerated all reachable format-message families:

   - Compute: cardinality/files, text outside envelope, invalid JSON, non-object JSON.
   - Tool: cardinality/other envelope, text outside envelope, invalid JSON, non-object JSON.
   - File: prose, unusable legacy JSON shape, missing path, duplicate path.

   The static messages route correctly. The duplicate-path message embeds the model-provided path, however. By execution, duplicate file paths named `compute.md` and `MCP tool.md` are file-parser failures but receive compute and tool addenda respectively. The free-text dispatch at [generator.py:536](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/src/crossaudit/generator.py:536) therefore does not establish the claimed parser-wide classification.

3. **Medium — the D64 mutation claim is false.** Mutating only MCP-tool failures back to the file addendum produced **2 failures / 15 passes**, not only the named failure: both the narrated-tool test and the routing assertions at [test_format_repair.py:408](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/tests/test_format_repair.py:408) reddened. More importantly, the narrated-tool test still reached a successful `ToolRequest`; its scripted completion ignores the prompt, so the mutation proves a string assertion, not the claimed escalation behavior. Its docstring also cites nonexistent D165 instead of binding D64.

4. **Medium — the attempt record contradicts the archives and the implementation.** The eight archived attempt cycles are not all `generator_format`: **3 are `generator_format`, 5 are `answered`**. Accordingly, the all-eight claim in [ATTEMPT-1.md:3](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/benchmarks/expertlongbench/study15/ATTEMPT-1.md:3) and repeated table entry in [PROBE-envelope-fix.md:7](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/benchmarks/expertlongbench/study15/PROBE-envelope-fix.md:7) are false. ATTEMPT-1 also says prose surrounding a tool envelope will be accepted and discarded, while the implemented parser remains strict and re-asks.

5. **Low — the two four-call runs expose a second common shape.** In both, generator call 3 ended at exactly **4,096 output tokens**, followed by a fourth call under a file-envelope addendum. That is strong evidence of an output-ceiling/truncation-shaped continuation failure. The probe note reports only “one more re-ask”; the archives do not retain enough reply text to identify the exact parser denial, so it should not claim more than that inference.

6. **Low — ancillary provenance text is not exact.** The T01 prompt and all 26 rubric items are semantically complete and correctly ordered against [arXiv:2506.01241v3, Table 5 and B.1.5](https://arxiv.org/pdf/2506.01241v3), but the “only edits”/“verbatim” claim omits apostrophe normalization such as `case’s` → `case's`. Separately, the sheet-builder docstring names seed `20261107` while the executable constant is `20261108`, and its example command points to the wrong study and run directory ([arm6_sheet.py:10](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-envelope/benchmarks/expertlongbench/study15/arm6_sheet.py:10)).

## Verification

- Archives reproduce: attempt **8 records, 0 receipts, two generator calls each, $0.365085**; fix **8 records, 8 receipts, generator calls 3/3/3/3/4/4/3/3, $3.351148**.
- Conversational surfacing and strict-parser focused checks: **5 passed**.
- Generator collection is exactly 60 tests. Read-only-compatible subset: **51 passed, 9 deselected**. The full run could not start because the sandbox provides no writable temporary directory, so 60/60 remains author-supplied.
- Frozen gold reproduced: shipped `R=11, W=R′=W′=0`, right blocks `10/10`, panel `2/97`; the T03 probe reproduced its committed counts.
- The 33-instance population exactly matches corpus order and the ≤200,000-character rule; median is 159,917 characters.
- No source-specific corpus leakage found across branch commit versions. Two 50-character overlaps occur in the paper-transcribed rubric and are independently present in B.1.5; no 80-character new overlap exists.
- Protected kernel directories are untouched; worktree and `git diff --check` are clean.

**DO NOT MERGE — the single most important reason is that the new compute corrective re-ask restates the wrong schema, while its test stops at parsing and therefore falsely certifies behavior that cannot execute.**
