## Findings

1. **Blocking — the unsupported causal conclusion remains.** RESULTS correctly says the run cannot distinguish a bad rule from generator noncompliance ([RESULTS-ARM6.md:71](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:71>)), but later concludes unconditionally that the line rule “is the wrong shape” ([RESULTS-ARM6.md:145](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:145>)). D166’s title makes the same unqualified claim ([DECISIONS.md:7599](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7599>)). The archive establishes that the one-line instruction went unmet in 40/87 addressed rows; it does not establish which side caused that outcome.

2. **Major — the interval repair remains incomplete.** RESULTS says every Arm 6 rate carries Wilson and draft-clustered intervals ([RESULTS-ARM6.md:9](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:9>)), but 12/40 carries Wilson only ([RESULTS-ARM6.md:73](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:73>)). Its independently recomputed clustered interval is **0–60%, five discarded**. D166 repeats the all-intervals assertion while explicitly presenting 27.7% and 0.54% with Wilson only, and gives 6/21 rendering only its Wilson interval ([DECISIONS.md:7609](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7609>), [DECISIONS.md:7623](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7623>), [DECISIONS.md:7645](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7645>)). The 6/21 clustered interval is **0–100%, 128 discarded**.

3. **Minor — D166 says the redesign “is preregistered as its own slice,” but no separate redesign preregistration exists at HEAD.** Arm 6 §8 prospectively requires such a slice; it does not constitute that slice’s completed preregistration ([DECISIONS.md:7636](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7636>)).

## Verified

- The annotation bootstrap is correctly repaired to **1.48–5.82%**.
- The 40 Q1 rows are now correctly called unlabelled candidates, not completed gold.
- Independent punctuation rule: trailing whitespace removed, terminal `.`, `?`, or `!` counted. Result: **12/40**. Adding Unicode sentence marks or stripping closing quotation/bracket characters still gives 12/40, so reasonable rule choice does not matter.
- Preregistration precedes attempt 1’s recorded start by 1.174 seconds; Amendments 1–2 precede attempt 2; Amendments 3–4 precede resumption.
- Outages reproduce: positions 3 and 8–14 initially; 11 records over 10 instances; one SSL plus seven credit failures before stopping and three SSL failures after resumption; partial instance 15 retained; every affected instance ultimately completed.
- Report JSON reproduces byte-for-byte. Counts reproduce: 33 drafts, 91 rows, 66 blocks, 14 passes, 11 advisory; §8g 3/17; H6b 40/87; annotation 91/2,630; fence 11/33; unit-bearing 42/91; Q1 pair-elsewhere 26/40; Q2 pair-elsewhere 12/21.
- Matcher comparison remains 5 blocks/14 passes under both matchers and both readings.
- Sheet reconstruction is exact: 19 verdict-free items, five located blocks plus all 14 passes; text equals the archived quotation; κ=1.000.
- Mechanisms reproduce: three M13 currency-before-value rows are C; both M1b rows are N; the outside-value row also lacks the value on its located line, with the nearest matching line seven lines away.
- Q2 independently reproduces as **6 rendering / 6 elision / 9 not found**.
- Costs reproduce: $13.4095 counted, $9.2310 generator, $4.1785 auditor, $0.3440 outages. There are 101 generator calls and three 4,096-token outputs.
- All 33 `file_read` result hashes match complete source results; none exceeded 512 KiB.
- Archive integrity passes: 4,324 files, all 4,323 non-self checks, byte count and directory digest.
- Rows and manifest re-emit exactly. A fresh ten-word scan over both corpora and all 3,722 added lines found zero overlap.
- `src/`, `tests/`, audit-core directories and profile files are unchanged from `bd491d5`; `number_source` membership is unchanged.
- The full suite still cannot initialize because the enforced environment provides no writable temporary directory. Both Arm 6 plan tests collect, and their two same-second sidecars/preserved-first-plan behavior reproduced in memory.
- Worktree remained clean; no file was modified.

**not quotable** — the single most important reason is that the reader-facing conclusion still says the one-line rule is the wrong shape even though the archive cannot distinguish that inference from generator noncompliance.
