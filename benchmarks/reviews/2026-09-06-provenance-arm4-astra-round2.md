# Independent cross-vendor review of Study 8 Arm 4, round 2 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over c18a367. Verdict: **needs revision** — the corpus removal
and the history rewrite are confirmed (no excerpt reachable, no unreachable
object, no reflog entry), M10 is correctly distinguished from E6, D161 ruling
2 claims only what was measured, and every number recomputes to four
decimals; three items remain: the 1 of 189 projection carried the Wilson
interval of 1 of 190, D161 still said the false-pass class "did not return",
and the handbook's copy of the `uncited` comparison was missed. Round 3 fixes
the three. Verbatim below; paths shortened to the repository root.

---

## Second-review verdict: Needs revision
The primary Arm 4 result independently recomputes, and the corpus-removal/M10 corrections are substantially correct. The report is still not quotable because one projection uses the wrong Wilson denominator and two round-1 overclaims remain in the surrounding record.
### Findings
1. **Major — projection intervals are incorrect.**
   [RESULTS-ARM4.md:69](benchmarks/expertlongbench/RESULTS-ARM4.md:69) correctly derives the projected counts from the same 189-row estimand, but:
   - 3/189: Wilson **0.54–4.56%**, not 0.54–4.57%.
   - 1/189: Wilson **0.09–2.94%**, not 0.09–2.92%.
   The printed 0.09–2.92% is exactly the interval for **1/190**, reused from the unit-shortening secondary.
2. **Major — the 50-pass sensitivity remains overgeneralized.**
   [D161:7323](docs/DECISIONS.md:7323) still says the pre-slice-3 false-pass class “did not return.” Only 50 of 180 passes were labelled. The supported statement is that none was observed in the 50-row sample, with a Wilson-compatible non-C rate up to 7.14%.
3. **Major — RESTART retains the false `uncited` comparison.**
   [RESTART.md:318](docs/RESTART.md:318) still says 7.77% was “not above Arm 3.” It exceeds Arm 3 B’s 6.80%; it lies between A and B. Consequently, [CORRECTIONS #31](benchmarks/CORRECTIONS.md:329) overstates that this wording—and the false-pass wording—was fully corrected.
### Corpus and history check
Confirmed for the named Arm 4 surfaces:
- Current prose uses shapes rather than source excerpts.
- `rows-arm4.jsonl`, `manifest-arm4.json`, and `key-arm4.jsonl` contain no raw `text`, `quote`, `v`, `u`, draft, prompt, or content fields—only hashes, lengths, identifiers, classifications, and metadata.
- The CSVs contain IDs, labels, and rule codes only.
- The abandoned `ba6920e` object is absent.
- It appears in no reflog.
- `git fsck --no-reflogs --unreachable` reports zero unreachable objects.
- Every reachable history entry for the Arm 4 result/record files begins with corrected commit `db52293`; no earlier excerpt-bearing version is reachable.
Thus no Arm 4 corpus excerpt remains reachable in the specified committed surfaces. Direct comparison against the licensed corpus was necessarily unavailable.
### Independent recomputation
| Outcome | Recomputed |
|---|---:|
| Rows / drafts | 206 / 26 |
| Dispositions | 180 PASS, 10 BLOCKER, 16 ADVISORY |
| Primary | **9/189 = 4.7619%** |
| Primary Wilson | **2.5252–8.8010%** |
| Primary clustered bootstrap | **1.0000–9.8266%** |
| `uncited` | 16/206 = 7.7670%; Wilson 4.8372–12.2431%; bootstrap 2.7473–13.8122% |
| Resolved/blockable | 180/190 = 94.7368%; Wilson 90.5842–97.1164%; bootstrap 89.6040–98.7952% |
| Absent / cross-line / ambiguous | each 0/190; Wilson upper 1.9818%; bootstrap 0–0 |
| Unit shortened | 1/190 = 0.5263%; Wilson 0.0930–2.9206%; bootstrap 0–1.6854% |
The manifest also confirms 600 numbers, total cost $1.983395—generator $1.541220, auditor $0.442175—and 13/26 re-asked drafts.
### M10 and E6
M10 is correctly distinguished from E6.
- The rows contain exactly two M10 records, both C-labelled blockers: [rows 190–191](benchmarks/expertlongbench/study8/rows-arm4.jsonl:190).
- E6 is a comparison-time rendering fold for superscripts and U+2212, as defined in [CONTAINMENT_RULE.md:83](docs/design/CONTAINMENT_RULE.md:83).
- M10 fails earlier: U+2013 is a scanner boundary and is absent from `_EXPONENT_TAIL`. A comparison fold therefore cannot repair it.
D161 ruling 2 is appropriately limited: it does not license M10 and requires a separate extension, dedicated gold rows, and W = 0 before shipping.
**May this report be quoted as the Arm 4 result? No.** The single most important reason is that its 1/189 projection is reported with the Wilson interval for 1/190, leaving a denominator-level numerical error in the report.
