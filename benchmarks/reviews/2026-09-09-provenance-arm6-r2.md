## Second-review findings

1. **Blocking — true-start provenance is still incomplete.**  
   The first plan block in `arm6.log` is byte-identical to `plan-start.json`, and the stable plan fields match. However, that logged block contains no `git_status`. The emitter converts the missing field to `""`, falsely presenting an unknown status as clean ([emit_records_arm6.py](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/study15/emit_records_arm6.py:85)). This does not satisfy the explicit clean-tree proof required by [EXPERIMENT_RECORD §2](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/EXPERIMENT_RECORD.md:26).

   The archive’s higher-level `MANIFEST.json` is also stale: 4,324 files exist, but it records 4,323; `plan-start.json` is unlisted, and its recorded digest for `MANIFEST.sha256` no longer matches. The newer per-file manifest itself verifies all 4,323 listed entries, and the original log remains correctly anchored, but the archive inventory is not current.

2. **Major — the revised outage chronology has an off-by-one error.**  
   [RESULTS](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:23) says positions 3 and 7–14 failed before the stop. The plan and records show positions **3 and 8–14**. The remaining chronology is correct: six completed drafts, eight initial outage records, a partial fifteenth directory, same-day resume, three later transport failures, 11 records over ten instances, and eventual success for all 33.

3. **Major — the M1b correction remains factually wrong.**  
   The value is indeed absent from the quoted run and its nearest matching line is seven lines away; both quotation and line readings therefore return N. But the parenthetical claiming that the quotation’s line “holds no numeral” is false: that line contains two other single-digit numerals ([RESULTS](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:88)).

4. **Major — preregistration timing is misstated.**  
   `4113b9a` is reachable and its preregistration blob is byte-identical to `081f4f0`. But its commit time, 18:44:36 +08:00, follows attempt 1 and the probe. Only the unreachable `081f4f0`, committed at 14:12:02, precedes the first recorded call at 14:12:03. Thus the statement that `4113b9a` preceded “any model call” is false; it preceded attempt 2 only.

5. **Major — “every rate below carries its intervals” is still false.**  
   The T03 comparison “4 of 398” and the Arm 5 annotation rate “38.1%” are quoted without their registered intervals ([RESULTS](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:53), [RESULTS](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:96)). D164 ruling 5 and EXPERIMENT_RECORD §9 apply when earlier rates travel into later prose.

6. **Additional completeness issues.**  
   D166 still does not exist; calling it “drafted” does not create a reviewable decision record. The runner now preserves an existing plan and writes a separate resume plan, but this new behavior has no regression test.

## Confirmed

- `report-arm6.json` reproduces exactly.
- Independent recomputation confirms the primary, H6b, annotation, fence, unit-bearing, Q2-pair, Wilson, and draft-clustered bootstrap results.
- The sheet reconstructs exactly: 19 verdict-free `id/text/v/u` items, five located blocks, and all 14 seeded passes.
- L1/L2 agree 19/19, κ = 1.000.
- Matcher comparison is 5 blocks and 14 passes under both matchers.
- Q2 independently classifies as 6 rendering, 6 elision, and 9 not found.
- All three M13 rows are currency-before-value C rows.
- Counts, costs, unit kinds, value shapes, fence distribution, 101 generator calls, and three 4,096-token calls reproduce.
- Records and manifest re-emit byte-for-byte.
- No ten-word corpus overlap was found in added text; committed records contain no quotation or draft fields.
- Relative to `bd491d5`, `src/`, `tests/`, audit-core directories, and profile membership are unchanged.
- Pytest could not execute because the enforced read-only environment provides no writable temporary directory.
- No files were modified.

**not quotable** — the single most important reason is that the true-start `git status --porcelain` evidence was never recovered, while the manifest currently represents that missing evidence as a clean status.
