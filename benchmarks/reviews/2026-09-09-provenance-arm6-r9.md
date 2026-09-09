## Ninth-review verdict

**Not quotable.** The three Round 8 defects are repaired, and the substantive Arm 6 record reproduces. One remaining interval-reporting defect violates the binding “every rate with its intervals” rule.

### Remaining finding

The complement of the fence rate is restated without either registered interval:

- [RESULTS-ARM6.md:123](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:123>): “no fence two times in three.”
- [DECISIONS.md:7656](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7656>): “Two summaries in three carried no annotation fence.”

That rate is 22/33 = 66.67%; Wilson 49.61–80.25%; draft-clustered bootstrap 51.52–81.82%. Although the complementary 11/33 fence rate is fully intervalled elsewhere, EXPERIMENT_RECORD §9 applies wherever a rate is quoted.

### Verified

- The reproducer now consistently says “prefix match”; execution yields Q2 = 6 rendering / 6 prefix match / 9 not found.
- The added 1/6 rate reproduces: 16.67%; Wilson 3.01–56.35%; bootstrap 0–100%, 413 discarded. RESULTS §2 and D166 ruling 3 carry both intervals.
- RESULTS §5 now explicitly marks the claimed pre-commit scan ordering as unaudited. A fresh scan found zero ten-word and zero 80-character corpus overlaps.
- Preregistration/amendment chronology and outage handling reproduce. The historical resume overwrote `plan.json`, as RESULTS discloses; `plan-start.json` reconstructs it from the log, while current `write_plan` preserves first plans.
- Report reproduces exactly: 33 drafts, 91 rows, 66 blockers, 14 passes, 11 advisories.
- §8g reproduces at 3/17 = 17.65%, Wilson 6.19–41.03%, bootstrap 0–60% → KILL.
- H6b reproduces at 40/87 = 45.98%, Wilson 35.90–56.40%, bootstrap 26.15–60.98% → fails.
- All other Round 8 rates, matcher results, sheet construction, κ, mechanisms, costs, call counts, file-read hashes, archive integrity, and code/profile immutability reproduce.
- Full pytest cannot initialize without a writable temporary directory; the Arm 6/verifier selection collects 1,228 tests.
- Worktree remained clean; no files were modified.

**not quotable — the single most important reason is that the 22/33 no-fence rate is still quoted twice without its Wilson and draft-clustered intervals.**
