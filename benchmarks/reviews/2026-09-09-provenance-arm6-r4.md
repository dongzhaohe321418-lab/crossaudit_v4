## Findings

1. **Blocking — D166’s central causal account is unsupported.** D166 says a sentence quotation is “the thing the skill asks for” ([DECISIONS.md](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7625>)). The frozen run skill instead requires the **shortest run from one line** containing the pair ([skill-S.md](/Users/ericdong/Documents/Crossaudit/study-data/wt-arm6-runs/arm6/skill-S.md:96)). The archive establishes 40 cross-line outputs and the preregistered H6b failure, but it does not establish D166/RESULTS’ stronger attribution that this was the contract’s shape rather than generator noncompliance. Only 12/40 Q1 quotations even end with sentence punctuation. RESULTS repeats this unsupported attribution ([RESULTS-ARM6.md](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:69>), [RESULTS-ARM6.md](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:88>)).

2. **Major — D166’s interval repair is inaccurate and incomplete.** Its Arm 6 annotation bootstrap is given as 1.45–5.80% ([DECISIONS.md](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7615>)). Independent resampling of the archived 33 drafts at seed 20261108 gives **1.48–5.82%**, exactly matching committed `arm6_rates.py`. RESULTS’ rounded 1.5–5.8% is correct. D166’s assertion that every rate carries both intervals is also false: 27.7%, 0.54%, and 6/21 are quoted later without Wilson or clustered-bootstrap intervals ([DECISIONS.md](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7623>), [DECISIONS.md](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7636>)).

3. **Major if intended as a completed fact — D166 overstates future gold work.** It calls the 40 Q1 quotations “gold rows” re-labelled on joined text ([DECISIONS.md](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7627>)). The archive contains no joined-text labels: Q1 rows remain no-location/N by definition and were excluded from the 19-item sheet. RESULTS more accurately calls them “first candidates” ([RESULTS-ARM6.md](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:139>)).

## Reproduced

- Preregistration `081f4f0` precedes the first model call by about 1.18 seconds. Amendments 1–2 precede attempt 2; Amendments 3–4 precede its resume.
- Outage handling matches the record: initial positions 3 and 8–14; 11 outage records over 10 instances; 1 SSL plus 7 credit failures before stopping and 3 SSL failures after resumption; partial instance 15 retained; all affected instances eventually succeeded.
- The historical resume did rewrite `plan.json`, as RESULTS now admits. `plan-start.json` preserves the recovered original. Current `write_plan` preserves the first plan and assigns distinct sequential sidecars within one second; both tests collect and the behavior reproduced in memory.
- `report-arm6.json` reproduced byte-for-byte. Matcher comparison reproduced 5 blocks/14 passes under both matchers and both quotation/line readings.
- Independent rates reproduced: §8g 3/17, H6b 40/87, Q1 pair-elsewhere 26/40, Q2 12/21, unit-bearing 42/91, annotation 91/2,630, and fence 11/33.
- Arm 5’s added annotation interval is correct: Wilson 35.38–40.94%, bootstrap 34.47–41.94%.
- The sheet reconstructs exactly: 19 verdict-free items, five located blocks plus all 14 passes; text equals the quoted run; L1/L2 agreement 19/19, κ = 1.000.
- All three M13 rows are currency-before-value cases. The outside-value row lacks the value in both quotation and line; the nearest occurrence is seven lines away.
- Q2 reproduces as 6 rendering, 6 elision, 9 not found using whitespace folding, typography normalization for rendering, and the unnormalized folded 40-character prefix for elision.
- Costs reproduce: $13.4095 total, $9.2310 generator, $4.1785 auditor, $0.3440 outages. There are 101 generator calls and three 4,096-token outputs.
- All 33 archived `file_read` result hashes match complete source-file results; none exceeded 512 KiB.
- Archive manifest: 4,324 files; all 4,323 non-self checks pass; directory count, bytes, and digest match the archive index.
- Rows and manifest re-emit exactly. A ten-word scan across both corpora and all 3,678 added lines found zero overlap.
- `src/`, `tests/`, kernel directories, profiles, and `number_source` membership are unchanged from `bd491d5`. Worktree remained clean.
- Pytest still cannot initialize under the enforced read-only environment because no writable temporary directory exists; both new tests collect successfully.

**not quotable** — the single most important reason is that D166 attributes the cross-line result to a sentence-quotation requirement that the frozen skill does not contain, so the proposed reader-facing causal conclusion is not established by the archive.
