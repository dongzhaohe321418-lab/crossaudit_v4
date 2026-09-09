## Tenth-review verdict

No findings. Round 9’s sole remaining defect is fixed.

- Both RESULTS §3 and D166 ruling 4 now report 22/33 = 66.67%, Wilson 49.61–80.25%, clustered bootstrap 51.52–81.82%. `arm6_rates.py` prints the same result, and an independent recomputation agrees.
- The report re-emits exactly: 33 drafts, 91 rows, 66 blockers, 14 passes, 11 advisories. §8g remains 3/17 → KILL; H6b remains 40/87 → fails.
- All other rates, intervals, value shapes, matcher comparison, Q2 classification (6/6/9), costs, call counts, and the three 4,096-token calls reproduce.
- The 19-item verdict-free sheet reconstructs exactly; it contains five located blocks and all 14 passes. L1/L2 agree 19/19, κ = 1.000. All five mechanism labels match the archive.
- Preregistration and amendment chronology holds. Outage handling matches the amendments: 11 records over 10 instances, all set aside and re-run. The historical `plan.json` overwrite remains accurately disclosed; `plan-start.json` preserves the recovered original.
- Archive checksums and index pass. Rows, manifest, and report re-emit exactly. All 33 complete `file_read` hashes match.
- A fresh scan of 4,077 added lines found zero ten-word and zero 80-character overlaps with either corpus. `src/`, root tests, audit-core paths, profiles, and the `number_source` blob are unchanged from `bd491d5`.
- Full pytest remains unavailable because the enforced read-only environment has no writable temporary directory; the focused Arm 6/verifier/profile selection collected all 1,228 tests. The worktree remained clean.

**quotable — the single most important reason is that the last unsupported rate now carries both preregistered intervals everywhere it is quoted, while the complete Round 9 evidence continues to reproduce.**

**Reader sentence:** “On hard-wrapped legal documents, the one-line provenance rule went unmet for 40 of 87 addressed rows (45.98%; 95% Wilson 35.90–56.40%; draft-clustered 95% bootstrap 26.15–60.98%), and this run cannot determine whether the rule or the generator was at fault.”
