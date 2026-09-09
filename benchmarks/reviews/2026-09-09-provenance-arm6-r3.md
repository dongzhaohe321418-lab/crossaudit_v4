## Findings

1. **Blocking — D166 misstates Arm 6’s adjudication.** It says one row differed between quotation and line readings ([DECISIONS.md](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7639)). Re-execution found identical outcomes under both readings: 5 blocks and 14 passes. Both M1b rows are N under both readings; the “value outside the quoted run” is also absent from its line and is seven lines away. D166 appears to have imported Arm 5’s M9b fact and directly contradicts the corrected RESULTS cell ([RESULTS-ARM6.md](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:98)).

2. **Major — the interval repair remains incomplete.** The transported Arm 5 annotation rate gives its Wilson interval but omits Arm 5’s registered draft-clustered bootstrap, 34.47–41.94% ([RESULTS-ARM6.md](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:106)). D166 likewise transports §8g, H6b, annotation, fence, and T03 rates without all registered intervals. This violates EXPERIMENT_RECORD §9 and makes RESULTS’ claim that both Arm 5 comparisons carry their intervals false.

3. **Major for future provenance, non-impacting this archive — `write_plan` can still rewrite a plan.** The added test correctly covers one resume and preserves `plan.json`, but sidecar names truncate timestamps to seconds ([provenance_arm6.py](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/provenance_arm6.py:56)). Two resumes within one second receive the same name and the latter overwrites the former. Thus “never rewrites a plan” remains broader than the tested behavior.

## Confirmed

- `study15-prereg-arm6` resolves to `081f4f0`; its preregistration blob matches `4113b9a`. The recorded timing is now accurately caveated. Amendments 1–2 precede attempt 2; Amendments 3–4 precede its resume.
- Outage chronology reproduces: six initial completions; positions 3 and 8–14; 11 records over ten instances; seven credit failures and four recorded SSL failures; partial instance 15; all 33 eventually successful.
- True-start `git_status` is genuinely unavailable and is now recorded as `NOT RECORDED`. The resume was clean, and `src/` is identical at `5b8da46` and `f4a8d6b`.
- Archive index: 4,324 files, all byte counts and digests match; `MANIFEST.sha256` has 4,323 non-self entries; its digest and the directory digest recompute exactly.
- `report-arm6.json` reproduces byte-for-byte. Matcher comparison reproduces 5 blocks/14 passes under both matchers.
- All reported Arm 6 counts and intervals reproduce independently, including 3/17, 40/87, 91/2,630, 11/33, 42/91, and 12/21.
- The 19-item verdict-free sheet reconstructs exactly: five located blocks and all 14 passes. L1/L2 agreement is 19/19, κ = 1.000.
- Q2 independently classifies 6 rendering / 6 elision / 9 not found. All three M13 rows are currency-before-value cases.
- Costs, fence distribution, unit kinds, 101 counted generator calls, and three counted 4,096-token calls reproduce.
- Records and manifest re-emit exactly in memory. No ten-word corpus overlap was found in 3,630 added lines.
- `src/`, kernel directories, both profile definitions, and `number_source` membership are byte-identical to `bd491d5`.
- Full pytest could not initialize because the enforced read-only environment has no writable temporary directory. The new test collects, and its intended single-resume behavior was executed successfully in memory.
- Worktree remained clean; no file was modified.

**not quotable** — the single most important reason is that the binding D166 decision attributes an adjudicator disagreement to Arm 6 that the archived evidence shows did not occur.
