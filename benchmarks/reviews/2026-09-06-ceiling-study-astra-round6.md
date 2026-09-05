# Independent cross-vendor review of the ceiling study, round 6 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over `study/ceiling` at ba1f232. Verdict:
**yes with corrections**, three items: the reader sentence's interval is not
bound (its declaration names a mechanism that checks the headline); reused
labels bind without family/reading context (a fabricated "eight-reading cost
9.7%" bound to astra's one-reading array); seed 20260915 declared unused but
consumed by the sampled sign-flip path; CORRECTIONS #25 misattributes #22/#23
to tests when round 4 reported them. Numerically: the four changed arrays are
exactly the declared duplicates, 302 byte-identical, 533 scalars unchanged,
33 tests, all mutations red, regeneration byte-identical. Verbatim below.

---

**The numerical checks pass, but three corrections remain.** Reviewed `ba1f232` against merge base `19bd1615c3d35381c37525721b6d38c5831b1ee5`, with `273a405` as round 5 and all five prior reports read. No files modified, network used, or detector readings adjudicated.
1. **The binding guard still accepts false uncertainty reporting.** The [reader-sentence declaration](benchmarks/code/tests/test_report_consistency.py:748) says `BOUND_SPANS` checks its interval. It does not: that mechanism checks the separate headline. Both mutations below leave **all 12 report tests green**:
   - `percentile interval −3.54 to +5.88` → `percentile interval +1.00 to +2.00`
   - `percentile interval −3.54 to +5.88;` → `percentile interval omitted;`
   A second counterexample also leaves all 12 green when inserted into the conclusion:
   > The shipped auditor's eight-reading false-positive cost (9.7% [5.3, 14.5]) was lower still.
   Rule 33 binds this to **Astra’s one-reading** array because it matches `cost (9.7% …)` without checking the family or reading count. The shipped eight-reading value is **16.0% [10.1, 22.3]**. Bind the reader sentence explicitly and strengthen the semantic context of reused labels.
2. **The seed reconciliation incorrectly declares `20260915` unused.** Both manifests inherit the [claim](benchmarks/code/ceiling/finalise_manifests.py:266) that no contrast exceeds 22 nonzero clusters and every sign-flip result is exact. Actual execution consumes this seed. The [self−cross pooled flag contrast](benchmarks/code/records/ceiling/numbers.json:2382) has **25 nonzero clusters**, **200,000 sampled draws**, and **p = 0.12373938130309349**. Its absence from the bootstrap inventory means it uses another random-number path, not that it is unused.
3. **CORRECTIONS #25 misattributes discoveries.** [Round 4, findings 1 and 2](benchmarks/reviews/2026-09-06-ceiling-study-astra-round4.md:19) explicitly reported the defects now numbered **#22 and #23**. [#25](benchmarks/CORRECTIONS.md:513) instead attributes #22–24 to tests written after reviews. Record #22/#23 as reviewer findings subsequently pinned by tests; distinguish #24’s author-reported discovery during the binding rewrite.
**Numerical changes verified.** Exactly these four arrays changed; their full-precision values now equal their canonical counterparts:
| Changed array under `timeout_sensitivity` | Round 5, % | Current, % | Canonical counterpart |
|---|---|---|---|
| `families.cross.union_registered.cluster_ci95` | [20.0, 40.5] | [20.0, 40.7] | `ceiling1.families.cross.P.union_at_kmax_block.cluster_ci95` |
| `families.self.union_registered.cluster_ci95` | [8.2, 27.3] | [8.3, 27.3] | `ceiling1.families.self.P.union_at_kmax_block.cluster_ci95` |
| `families.astra.union_registered.cluster_ci95` | [20.9, 45.5] | [20.7, 45.0] | `ceiling1.families.astra.P.union_at_kmax_block.cluster_ci95` |
| `residual_registered.cluster_ci95` | [40.4, 63.6] | [40.0, 63.3] | `ceiling1.residual.all_families.share_block.cluster_ci95` |
The other **302 numeric interval-array substrings are literally byte-identical** to round 5. All **533 version-1 numeric scalars remain present and unchanged**. No non-array value in `numbers.json` changed since round 5. Table 9’s registered column now agrees with Tables 1 and 5.
**Binding inventory.** There are **36 direct binding rules plus seven declarations**. The current scanner finds **34 rate tokens in the opening and 11 in the conclusion**, each matched exactly once: 38 direct bindings and seven declarations. Thus no scanned token is unmatched, but the reader-sentence exception prevents confirmation that every empirical rate is actually bound as claimed.
Below, rule numbers follow source order; grouped numbers enumerate separate rules sharing an array. Abbreviations:
- `F` = `ceiling1.families`
- `Q` = `ceiling1.primary_ceiling1.P`
- `D` = `ceiling2.contrasts.referent-loop__vs__cross-loop`
| Rule(s) | Rate or difference | Bound interval array |
|---|---|---|
| 1 | Cross one-reading recall, 10.7% | `F.cross.P.draw1_block.cluster_ci95` |
| 2, 8, 17, 32 | Cross union recall, 30.0% | `F.cross.P.union_at_kmax_block.cluster_ci95` |
| 3 | Cross one-reading FP, 4.5% | `F.cross.C.draw1_block.cluster_ci95` |
| 4, 18, 30 | Cross union FP, 16.0% | `F.cross.C.union_at_kmax_block.cluster_ci95` |
| 5, 7 | Cross fitted asymptote, 31.5% | `F.cross.P.fit_A_ci95` |
| 6 | Cross last-step gain, 1.93 points | `F.cross.P.last_step_gain_block.cluster_ci95` |
| 9 | Self one-reading recall, 15.5% | `F.self.P.draw1_block.cluster_ci95` |
| 10 | Self union recall, 17.3% | `F.self.P.union_at_kmax_block.cluster_ci95` |
| 11 | Self fitted asymptote, 16.6% | `F.self.P.fit_A_ci95` |
| 12, 29 | Self union FP, 24.0% | `F.self.C.union_at_kmax_block.cluster_ci95` |
| 13 | Fitted self−cross, −14.9 points | `Q.ci95` |
| 14 | Raw self−cross, −12.7 points | `Q.raw_diff_ci95` |
| 15, 31 | Astra one-reading recall, 30.2% | `F.astra.P.draw1_block.cluster_ci95` |
| 16, 33 | Astra one-reading FP, 9.7% | `F.astra.C.draw1_block.cluster_ci95` |
| 19, 20, 35 | Referent−cross P flags, +26.8 points | `D.flag_discordance.P.ci95` |
| 21 | Referent−cross pooled flags, +19.6 points | `D.flag_discordance.all.ci95` |
| 22 | Referent net, +8.04 pp | `ceiling2.arms.referent-loop.net_primary.ci95` |
| 23, 36 | Referent−cross outcome, +5.36 pp | `D.ci95` |
| 24, 34 | Residual share, 51.8% | `ceiling1.residual.all_families.share_block.cluster_ci95` |
| 25 | Unexercised-edge share, 80.7% | `ceiling1.residual_classified.all_families.cluster_ci95.unexercised-edge` |
| 26 | Assertion-only residual, 52.4% | `timeout_sensitivity.residual_assertion_only.cluster_ci95` |
| 27 | Registered residual, 51.8% | `timeout_sensitivity.residual_registered.cluster_ci95` |
| 28 | Self-loop net, +0.89 pp | `ceiling2.arms.self-loop.net_primary.ci95` |
The seven declarations cover three nominal confidence levels, two power-curve quantities, the separately checked headline, and the incorrectly described reader-sentence check. Rules 14 and 30 each match twice. The file also contains identical duplicate definitions; the counts above describe the effective rules and distinct tests.
All five requested mutations turn red:
| Mutation | Result |
|---|---|
| Round-5 neighboring-interval counterexample | Red: two unbound rates |
| Strip the first 30.0% interval | Red |
| Change 30.0% to 31.0% beside its correct interval | Red |
| Swap the 10.7% and 30.0% intervals | Red: two interval mismatches |
| Delete the self-model bound sentence | Red through liveness: four rules stop matching |
Changing `+8.04 pp` to `+8.04%` also turns red. The new accepted counterexamples are those reported above.
**Seed inventory.** Both the cheap logged pass and full regeneration reproduce **32 distinct seeds over 196 `cluster_bootstrap_ci` calls**, matching both manifests. The three corrected ranges are accurate:
| Purpose | Actual values |
|---|---|
| Union curves, K = 1–8 | `20260929–20260936` |
| Mixed families, 1–8 draws per family | `20260939–20260946` |
| Comparator totals 2, 3, 4, 6, 8 | `20260960, 20260961, 20260962, 20260964, 20260966` |
Seeds **20260922 and 20260923** are explicitly documented as retired and are no longer consumed. Broader instrumentation of the cheap pass records **34 distinct seeds across 205 `Random` constructions**, including the inline primary bootstrap and the sampled sign-flip path. The bootstrap inventory is correct; its reconciliation of `+7` is not.
**Manifests, deviations, and scope.** `superseded_fields_removed` and `finalised_at_commit` are absent from both manifests. `working_tree_at_freeze` remains with corrected wording. The freeze locator resolves to **ba1f232**, its recorded parent is **273a405**, and every recorded code-file hash matches. These provenance fields are consistent, subject to the seed error above.
Deviation 18 labels both methods and scenarios correctly. Deviations are monotonically **1–27**. CORRECTIONS **#22–24** accurately describe the numerical/reporting corrections; **#25 requires the attribution correction**.
Since round 5, only the nine declared files changed. Raw evidence is unchanged. Both the `src/` diff against the merge base and branch-only `src/` history are empty. The complete study diff includes the previously noted `.gitignore` change.
**Execution results.** All **33 distinct tests passed** by direct invocation under Python 3.13.5: **21 statistics + 12 consistency**. The application suite and hidden suites were not rerun. All **99 generated table rows** occur in the report.
With credential-like environment variables unset, sockets disabled, bytecode disabled, and output writes intercepted in memory, regeneration returned zero and reproduced both artifacts byte-for-byte:
```text
numbers.json 412534c7222569ed736cdcb84019a0ff1efdb01273ec2e555312b515463d8ee0
tables.md    c5e939aac38fc238767dfb918f8cc10b026c9231f59329f7911e5a300c6f7e2e
```
The reader sentence is present verbatim apart from Markdown wrapping:
> Self-audit changed accuracy by +0.89 percentage points (problem-cluster percentile interval −3.54 to +5.88; 112 instances from 96 problems), establishing no improvement; the interval method was changed after analysis, its coverage in this clustered design is unvalidated, and modest benefits remain compatible with the data.
**May these numbers be quoted in a paper — yes with corrections.** The single most important reason is that **the uncertainty calculations reproduce, but the claimed verification still accepts fabricated uncertainty in the mandatory reader sentence.**
