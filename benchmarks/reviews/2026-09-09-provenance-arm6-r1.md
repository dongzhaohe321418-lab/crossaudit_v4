Not quotable yet. The headline results reproduce, but several publication-blocking record and prose defects remain.

### Findings

1. **Blocking — attempt 2’s original plan was overwritten.** The archived log contains two plans:

   - 10:44:36 UTC, code `5b8da46`
   - 10:57:33 UTC, code `f4a8d6b`

   Six counted records predate the surviving [`plan.json`](/Users/ericdong/Documents/Crossaudit/study-data/wt-arm6-runs/arm6/plan.json). The runner preserves an existing plan only with `--only`; an ordinary same-directory resume rewrites it ([provenance_arm6.py:117](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/provenance_arm6.py:117)). Consequently, `manifest-arm6.json` records the second start’s clean status, not the actual start status required by EXPERIMENT_RECORD §2.

   The two logged plans have identical population, models, settings, skill, contract, corpus and matcher hashes; the intervening code changes only add amendments/emitter material. This makes bias unlikely, but it does not restore the lost start-state provenance.

   Additionally, cited preregistration commit `081f4f0` is not an ancestor of `eaee0d6` and is contained by no branch or tag. Its preregistration blob is byte-identical to reachable commit `4113b9a`, but a normal clone of this branch would not retain `081f4f0`.

2. **Major — the outage chronology contradicts Amendment 4 and the archive.** [RESULTS lines 16–20](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:16) says the run paused at instance 12 and resumed “the next day.” Amendment 4 says instances 13 and 14 also failed and instance 15 had begun; the archive confirms that partial directory. Resumption events occurred later on September 7 UTC—not the next day.

   The remaining outage claims reproduce: 11 records over 10 unique instances, seven credit failures and four SSL failures, followed by successful completion of all 33 instances; outage cost $0.343992.

3. **Major — preregistered secondaries and intervals are missing.** The preregistration inherits separate quote-absent/cross-line splits by whether the pair appears elsewhere and requires Wilson plus draft-clustered bootstrap intervals for every rate. RESULTS substitutes a combined 38/61 figure and omits its bootstrap. Independent results are:

   - Q1 pair elsewhere: 26/40 = 65.00%; Wilson 49.51–77.87%; bootstrap 32.26–100.00%.
   - Q2 pair elsewhere: 12/21 = 57.14%; Wilson 36.55–75.53%; bootstrap 0.00–100.00%.
   - Quote-absent rate: 21/87 = 24.14%; Wilson 16.36–34.10%; bootstrap 2.22–47.30%.
   - Resolved over addressed rows: 14/87 = 16.09%; Wilson 9.83–25.22%; bootstrap 4.00–33.33%.

   The pass sensitivity and unit-shortening rates also omit their computed bootstrap intervals; the five value-shape shares omit both registered intervals. The inherited generator/auditor cost split is absent: $9.230979 versus $4.178503.

4. **Major — the “value outside the quoted run” mechanism is misstated.** [RESULTS line 64](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:64) says the quotation ends one token before the value and the line-level reading would call it stated. The selected line contains no matching numeral; both shipped and Arm 4 line-level matchers return false. The numeral exists elsewhere in the named file, with the nearest matching line seven lines away. The quotation adjudicator’s N label is unaffected.

5. **Additional report errors.**

   - The 42 unit-bearing rows are 27 currency-unit, seven percent-unit and **eight day-unit** rows—not only currency and percent as [line 80](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:80) states.
   - Eleven drafts contain a fence, but their parsed row counts range from **0 to 22**, not 1 to 22 ([lines 73–75](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:73)).
   - RESULTS cites decision record D166, but no D166 exists at this commit.

### Confirmed

- Primary: 3/17 = 17.65%; Wilson 6.19–41.03%; bootstrap 0–60%, seven discarded; **KILL**.
- H6b: 40/87 = 45.98%; Wilson 35.90–56.40%; bootstrap 26.15–60.98%; **fails**.
- Annotation, fence and unit-bearing rates and their printed intervals reproduce.
- Q2 classification reproduces as 6 rendering / 6 elision / 9 not found using normalized exact containment followed by the raw 40-character-prefix test.
- The five located block mechanisms reproduce: three M13 currency-before-value rows, one value-in-words row, and one quotation-adjudicator N row.
- The reported value shapes reproduce as 3 years, 2 day durations, 7 amounts, 5 counts and 2 percentages.
- Matcher comparison is 5 blocks / 14 passes under both matchers.
- The sheet reconstructs exactly: 19 items, `id/text/v/u` only, all text/value/unit hashes match the run, all 14 passes are included, and seeded ordering reproduces.
- L1/L2 agree 19/19, κ = 1.000. All 12 rule-code differences are L1 R1 versus L2 R3 on empty-unit rows. Per instruction, I did not re-label.
- 91 rows, 66 blocks, 14 passes, 11 advisories; $13.409482 counted spend; 101 generator calls with three exactly at 4,096 tokens.
- All 4,322 archive checksum entries verify. Re-emitted rows and manifest reconstruct byte-for-byte.
- No source-specific corpus prose appears in RESULTS or other study additions. Longer overlaps are confined to the independently paper-transcribed task rubric; no 80-character overlap exists.
- `src/`, `tests/`, kernel directories and profile membership are unchanged.
- Relevant verifier/benchmark tests: 116 passed. The full suite could not start because the enforced read-only environment provides no writable temporary directory.
- No files were modified.

**not quotable** — the single most important reason is that the original attempt-2 plan was overwritten, so the committed manifest does not preserve or prove the run’s actual frozen start state.
