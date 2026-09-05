# Independent cross-vendor review of the ceiling study, round 5 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over `study/ceiling` at 273a405. Verdict:
**yes with corrections**, all written: three bare estimates in the opening
exempted by context matching, and the completeness guard accepts a
neighbouring rate's interval (counterexample supplied); a manifest block still
says a retained field was removed; seed-inventory ranges wrong (K 1–8, not
8–16); deviation 18 pairs two methods' coverages unlabelled. Everything
numerical reproduces: 29 tests, pre-fix estimator table, 300 arrays
byte-identical, 533 scalars, six new intervals, regeneration byte-identical.
Verbatim below, paths shortened.

---

**The numbers reproduce, but the intended-final corrections are not fully closed.** Reviewed `273a405` against merge base `19bd1615c3d35381c37525721b6d38c5831b1ee5`, after reading all four reports. No files modified, network used, or detector readings adjudicated.
Four corrections remain:
1. **Interval completeness still fails.** The [opening](benchmarks/code/RESULTS-CEILING.md:55) retains bare **1.93 points**, **31.5%**, and **30.0%**. These are estimates, not counts. The [guard](benchmarks/code/tests/test_report_consistency.py:314) exempts them through broad context matching. I found no additional bare estimates in the conclusion.
   Removing the first `30.0%` interval turns red. Moving it far down its sentence also turns red. But this displacement **stays green** in both completeness and interval-value checks:
   ```text
   (30.0% at 16.0% [10.1, 22.3], with the recall interval [20.0, 40.7])
   ```
   The recall interval is 49 characters away; the guard accepts the **false-positive interval**, ten characters away. Bind each rate to its own interval and retain this counterexample as a regression test.
2. **Both manifests still contradict their new provenance record.** `finalised_at_commit` is absent; `working_tree_at_freeze` has corrected wording and is explicitly retained. However, the old `superseded_fields_removed` block still says it was removed—in [ceiling1](benchmarks/code/records/ceiling/manifest_ceiling1.json:2707) and [loop](benchmarks/code/records/ceiling/manifest_loop.json:869). Remove or explicitly supersede that contradictory block.
3. **Seed offsets are complete, but their ranges are inaccurate.** Every `BOOT_SEED` expression is represented, including `+50+total`, `+14`, `+15`, and new `+60`; `+2` is correctly marked unused. But both [inventories](benchmarks/code/records/ceiling/manifest_loop.json:19) say `K = 8 .. 16`. Actual curve K values are **1–8**, giving seeds **20260929–20260936**. Actual mixed-family seeds are **20260939–20260946**; comparator totals are **2, 3, 4, 6, 8**, giving seeds **20260960, 20260961, 20260962, 20260964, 20260966**.
4. **Deviation 18 still mixes coverage methods without labels.** Its [“0.960 beneficial / 0.075 detrimental” sentence](benchmarks/code/RESULTS-CEILING.md:646) pairs Tango’s coverage with exact-grid coverage. Label the methods there, as the corrected table now does.
The requested numerical checks pass:
- **All 29 tests passed**, directly invoked under Python 3.13.5. The report-writing mutation test operated entirely in memory. Application and hidden suites were not rerun.
- The committed pre-fix estimators reproduce the corrected attribution; the report table, Amendment 5, and CORRECTIONS #17 agree:
  | Pre-fix method | Beneficial, q=.1 | Detrimental, q=.5 |
  |---|---:|---:|
  | Tango | 0.960370409515 | 0.953264931806 |
  | Exact grid | 0.996879092228 | 0.075224906343 |
- Deviation 19’s sentence is struck through and explicitly superseded by 21. Deviations are monotonically **1–25**.
- Independent ledger counting confirms **10 run IDs, 24 events: 2 probes, 16 pilot audits, 6 pilot revisions**.
- All **300 previous interval arrays are byte-identical**; all **533 version-1 scalars remain unchanged**.
- All **six new intervals regenerate and independently reproduce exactly**. Their actual composition is **three families × P/C last-step gains**; the added prose intervals reuse existing arrays.
- All 99 generated table rows occur in the report. Raw evidence is unchanged from round 4. `src/` is empty against the merge base and in branch-only history. The overall study diff also includes `.gitignore`.
- The freeze locator resolves to `273a405`; every recorded code hash matches.
With credential-like environment variables unset, sockets disabled, and writes intercepted, regeneration returned zero and reproduced both artifacts byte-for-byte:
```text
numbers.json 846a8070de59b62dfcf34a2a3364ef53ee80c41c747d344fc6492f4a2e8a8132
tables.md    61e44f17fee1bc5c5c1d5092f86396117a4ae8ca7b3e5226a294d5b4ffc6b9d3
```
The reader sentence is present beside the headline, verbatim apart from Markdown wrapping:
> Self-audit changed accuracy by +0.89 percentage points (problem-cluster percentile interval −3.54 to +5.88; 112 instances from 96 problems), establishing no improvement; the interval method was changed after analysis, its coverage in this clustered design is unvalidated, and modest benefits remain compatible with the data.
**May these numbers be quoted in a paper — yes with corrections.** The single most important reason is that **complete uncertainty reporting is still falsely certified: bare estimates remain, and the guard accepts another quantity’s interval as their uncertainty.**
