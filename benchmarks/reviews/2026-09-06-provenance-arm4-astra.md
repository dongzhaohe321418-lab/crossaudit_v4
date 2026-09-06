# Independent cross-vendor review of Study 8 Arm 4, round 1 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over `fusion/evidence-authority` at ba6920e (a commit since
rewritten out of the unpushed history; its corrected form is db52293).
Verdict: **not quotable yet** — the headline recomputes exactly (9 of 189,
Wilson 2.53–8.80%, KILL; every secondary to four decimals), the estimand and
the pass-sample sensitivity match the preregistration, the sample is exactly
the corpus minus Arm 3's plan, the harness is the shipped path — but the
results file, the emitter's comments, D161 and the handbook quoted short
source phrases, against the corpus licence and the commit's own "not
committed" sentence; the two en-dash rows were filed under E6, whose licence
is a comparison-time fold and does not transfer to a tokenisation change; and
six smaller sentences overclaimed (`uncited` "not above Arm 3", "not in
question", "copied bytes every time", "—" for zero-event bootstraps, rule-code
disagreements silently resolved, an untracked directory at run start
unreported). Round 2 removes every excerpt and rewrites history, files the
en-dash rows as a new class M10, and narrows each sentence (CORRECTIONS #31).
Verbatim below; paths shortened to the repository root.

---

No — the report should not yet be quoted as the final Arm 4 result. The headline arithmetic is correct, but the commit violates its corpus-free requirement and overstates that the en-dash failures belong to an already licensed E6 class.
## Findings
1. **Blocking: Arm 4 corpus text was committed.**
The machine-readable artifacts are corpus-free: I recursively inspected every string field in `rows-arm4.jsonl`, `manifest-arm4.json`, and `key-arm4.jsonl`; the CSVs contain only IDs, labels, and rule codes.
But exact source excerpts appear in:
- [RESULTS-ARM4.md:53](benchmarks/expertlongbench/RESULTS-ARM4.md:53)
- [emit_records_arm4.py:25](benchmarks/expertlongbench/study8/emit_records_arm4.py:25)
- [DECISIONS.md:7326](docs/DECISIONS.md:7326)
- `docs/RESTART.md` also repeats Arm 4 excerpts.
These include the actual ranges, list, en-dash units, and hyphenated phrase. That contradicts the binding “never corpus text” rule and the claim that the corpus was “not redistributed and not committed” at [RESULTS-ARM4.md:127](benchmarks/expertlongbench/RESULTS-ARM4.md:127).
2. **Major: the en-dash cases are not the already-licensed E6.**
The original M9c/E6 class concerns two different Unicode renderings normalized at comparison time. These two Arm 4 rows are explicitly byte-identical. They fail earlier because U+2013 is treated as a token boundary and is absent from `_EXPONENT_TAIL`.
That is a new lexical/tokenization class, requiring a new rule and safety measurement. Therefore these claims exceed the evidence:
- “E6, licensed” at [RESULTS-ARM4.md:55](benchmarks/expertlongbench/RESULTS-ARM4.md:55)
- “8 of 9 … extensions D160 already licensed” at [RESULTS-ARM4.md:61](benchmarks/expertlongbench/RESULTS-ARM4.md:61)
- the equivalent D161 claim at [DECISIONS.md:7329](docs/DECISIONS.md:7329)
D161 ruling 2 is safer: it requires another W=0 evaluation before landing. But the new behavior should not inherit E6’s previous licence merely by extending the label.
3. **The numerical result itself recomputes correctly.**
From `rows-arm4.jsonl`, grouped by its 26 instance IDs and using the coded seed and percentile indices:
| Outcome | Recomputed |
|---|---|
| Rows | 206 |
| Dispositions | 180 PASS, 10 BLOCKER, 16 ADVISORY |
| Advisory | 16/16 `uncited` |
| Primary | 9/189 = 4.7619% |
| Wilson | 2.5252–8.8010% |
| Draft bootstrap | 1.0000–9.8266% |
| §8g | **KILL** |
| `uncited` | 16/206 = 7.7670%; Wilson 4.8371–12.2432%; bootstrap 2.7473–13.8122% |
| Resolved/blockable | 180/190 = 94.7368%; Wilson 90.5841–97.1164%; bootstrap 89.6040–98.7952% |
| Absent/cross-line/ambiguous | each 0/190; Wilson 0–1.9818% |
| Unit shortened | 1/190 = 0.5263%; Wilson 0.0930–2.9206%; bootstrap 0–1.6854% |
| Mechanisms | 5×M2, 1×M3, 2×M9c-as-recorded, 1×M4, 1×M1b |
| Matcher | the claimed blob in all 206 rows |
The coded zero-event bootstraps are 0–0; RESULTS substitutes “—”, despite preregistering a bootstrap beside every rate.
The 600-number annotation denominator, cost, and re-ask count cannot be derived from `rows-arm4.jsonl` alone. From the manifest they are correct:
- 206/600 = 34.3%
- total $1.983395; generator $1.541220, auditor $0.442175
- 13/26 re-asked
- 26/26 `ok`, 26/26 `manifest_agrees`
- 10 shipped-check blocks
4. **The estimand and sensitivity match the preregistration.**
The report implements the preregistered denominator exactly: all passes plus C-labelled blocks, excluding uncited/governed/advisory rows. The “passes taken as containing” choice was explicitly preregistered at [PREREGISTRATION-ARM4.md:85](benchmarks/expertlongbench/study8/PREREGISTRATION-ARM4.md:85), not introduced post hoc.
The reconstructed seeded sample matches `key-arm4.jsonl` exactly: all 10 blocks plus precisely the expected 50 of 180 passes. All sampled passes are C, so the preregistered point sensitivity leaves the denominator at 189.
However, “the false-pass class did not reappear on this text” overgeneralizes 50 sampled passes to all 180. The supported statement is “no false pass was observed in the 50-row sample”; its Wilson interval permits up to 7.14% non-C.
5. **Harness/path checks pass, subject to archive limits.**
Static verification found:
- shipped skill hash exactly `9914e629…`;
- `dcl.describe(["number_source"])` hash exactly `eb1f0cc1…`;
- matcher blob exactly `8dfd07d9…` at both `a17109e` and run commit `43ac13d`;
- harness uses `_row_findings`, which `check_number_source` calls per row;
- its per-row total equals the recorded full-check total;
- the 26 Arm 4 IDs and 24 Arm 3 IDs are disjoint, duplicate-free, and union to 50;
- the excluded-ID list is byte-for-byte the Arm 3 plan list.
The sheet builder exposes only `id`, located text, `v`, and `u`, with no verdict, reason, instance, or kind at [arm4_sheet.py:81](benchmarks/expertlongbench/study8/arm4_sheet.py:81). Thus its format is blinded. Without the archived sheet and invocation transcript, actual L2 process blinding cannot be independently proved.
6. **Agreement is correct on labels, but not on rule citations.**
C/N/? agreement is 60/60 and κ = 1.000: both label sets contain 59 C and 1 N.
But L1 and L2 disagree on the cited rule for seven items. For example, compare [L1-arm4.csv:5](benchmarks/expertlongbench/study8/L1-arm4.csv:5) with [L2-arm4.csv:5](benchmarks/expertlongbench/study8/L2-arm4.csv:5). GOLD silently adopts L1’s rule codes. Therefore “60 of 60 agree; no adjudication was needed” is accurate only for class labels, not the required `label,rule` output.
## Other overclaims
- “`uncited` … not above Arm 3’s” in [D161:7332](docs/DECISIONS.md:7332) is literally false relative to Arm 3 B: 7.77% exceeds 6.80%. “Not materially above” in RESULTS lacks a preregistered materiality threshold.
- “The addressing half … is not in question” is stronger than 0/190 with a 1.98% Wilson upper bound.
- “The generator copied bytes it could see, every time” establishes a mental/process claim; the records establish only that all 190 addressed quotations were found.
- Claims that the deleted first attempt made no API call cannot be independently checked from committed records.
- The run began with `git_status_at_start: "?? scratchpad/"`, contrary to the bound clean-freeze standard, and RESULTS does not report this deviation.
- The 0.53% value is properly called a projection and said to license nothing. It is not a measurement, but it also depends on the unlicensed en-dash scanner change.
**May this report be quoted as the Arm 4 result? No.** The single most important reason is that the supposedly corpus-free commit directly redistributes licensed Arm 4 corpus excerpts. The core statistical conclusion—**9/189, Wilson 2.53–8.80%, KILL**—does independently recompute.
