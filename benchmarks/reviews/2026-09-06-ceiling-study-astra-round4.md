# Independent cross-vendor review of the ceiling study, round 4 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over `study/ceiling` at 1750bfd against
merge base 19bd161. Verdict: **may be quoted — yes, with corrections**, the
corrections now purely written: one coverage label attributes Tango's 0.960
to the old exact-grid method (which reproduces at 0.997); deviation 19 still
carries the withdrawn "2–5 points optimistic"; opening and conclusion repeat
rates without intervals; one manifest field recorded as removed is present,
the 24 unmatched events are listed as ten groups, and three seed offsets are
missing. Everything numerical reproduces: 25 tests, four consistency
mutations red, 233 arrays byte-identical, 67 new arrays regenerate, 533
scalars unchanged, coverage table to twelve digits, regeneration
byte-identical. Verbatim below, paths shortened.

---

**The numbers reproduce, but several claimed corrections remain incomplete.** Reviewed `1750bfd` against merge base `19bd1615c3d35381c37525721b6d38c5831b1ee5`, after reading all three prior reports. No files modified, network used, or detector readings adjudicated.
The remaining corrections are:
1. **One coverage label is newly wrong.** The [report](benchmarks/code/RESULTS-CEILING.md:424), [Amendment 5](benchmarks/code/ceiling/PREREGISTRATION.md:546), and [CORRECTIONS #17](benchmarks/CORRECTIONS.md:395) assign beneficial coverage **0.960 to the old exact-grid method**. Reexecuting the old code gives **0.996879092228**; **0.960370409515 belongs to Tango**. Old detrimental exact-grid coverage reproduces as **0.075224906343**.
2. **The blanket assertion was not completely withdrawn.** [Deviation 19](benchmarks/code/RESULTS-CEILING.md:630) still explicitly says every interval should be read as “approximately 2 to 5 points optimistic.” Remove it or mark that sentence itself as superseded. The requested searches find “nominal,” “never under,” “did not raise,” and “exactly one” in historical or qualified contexts; this blanket sentence remains an unqualified assertion.
3. **Interval reporting is still incomplete.** Tables 3, 4 and 9 are corrected, but opening repetitions still omit intervals—for example, [30.0%/16.0%](benchmarks/code/RESULTS-CEILING.md:76) and [52.4%/51.8%](benchmarks/code/RESULTS-CEILING.md:115). The conclusion repeats [＋0.89 pp](benchmarks/code/RESULTS-CEILING.md:704), [＋26.8 points and ＋5.36 pp](benchmarks/code/RESULTS-CEILING.md:719) without numerical intervals. Table 1’s last-step gains also lack intervals. Thus the universal completeness claim fails.
4. **Provenance cleanup is overstated.** `finalised_at_commit` is gone, but both manifests still contain `working_tree_at_freeze` while their removal records say it was removed. Its replacement wording is corrected; the removal claim is false. The [unmatched-event block](benchmarks/code/records/ceiling/manifest_loop.json:14) contains **ten run-ID groups totalling 24 events**, not 24 individual event records. Independent ledger inspection confirms **2 probes, 16 pilot audits and 6 pilot revisions**. Finally, the manifest seed inventory omits the new offsets **`+50+total`, `+14`, and `+15`**, despite claiming manifest-only sufficiency.
The requested numerical and implementation checks otherwise pass:
- **All 25 test functions passed**, invoked directly with bytecode disabled; `pytest` was unavailable. The application and hidden suites were not rerun.
- **All four requested in-memory mutations turn red**, including the hundredth change, Unicode-minus headline change, positive-number change, and `[−99.99, +99.99]` headline. An additional `+5.88 → +5.89` mutation also fails. The committed mutation test passes; headline and primary spans are bound to specific record paths.
- The referent−cross P-flag exact interval is now stored at `ceiling2.contrasts.referent-loop__vs__cross-loop.flag_discordance.P.exact_unconditional_ci95`. Recalculation gives **[6.250002980232, 43.749996913331] pp**, correctly displayed in the opening as **[+6.3, +43.7]**.
- **All 233 pre-existing interval arrays are literally byte-identical to round 3.** All **67 added arrays regenerate**: 50 comparator intervals, nine exact flag intervals, four registered-population cluster intervals and four Wilson intervals. Independent comparator bootstrap calculations agree within **2.78×10⁻¹⁷**.
- All **533 version-1 numeric scalars** remain present and unchanged. No raw evidence changed since round 3. There are no `src/` changes against the merge base or in branch-only history; the overall study diff also includes `.gitignore`.
- **46/57**, independently bootstrapped with **seed 20260919**, gives **[66.101695, 93.106371]%**, correctly displayed as **[66.1, 93.1]**. Small residual categories are now counts.
- Power recomputes as **0.321205, 0.600805, 0.811490**. The independent-pair model and its distinction from clustered-procedure power are explicitly stated.
- Deviations are monotonically numbered **1–23**; deviation 22 correctly references deviation 20. `splice_tables.py` exists, and all **99 generated table rows** occur in the report.
All six current coverage entries reproduce:
| Method | Beneficial, q=.1 | Detrimental, q=.5 |
|---|---:|---:|
| Ideal percentile bootstrap | 0.923731894539 | 0.953264931806 |
| Tango | 0.960370409515 | 0.953264931806 |
| Returned exact-grid intervals | 0.996879092228 | 0.983740418538 |
The detrimental bootstrap test exists and passes. At `(0,44,112)`, the returned lower endpoint is **−0.499999993614**, while direct grid acceptance gives **p=0.050731428873**. Including that boundary case raises coverage to **0.989508639384**, exactly as disclosed.
The freeze locator resolves to `1750bfd`; every recorded code hash matches. Current `report_ceiling.py` SHA-256:
```text
bf06b09e4956891c877b778ea740d06d135616a00b1714226f3e461319820e4a
```
With credential-like environment variables unset, sockets disabled, and output writes intercepted in memory, regeneration returned zero and reproduced both artifacts byte-for-byte:
```text
numbers.json  01dc7450053f694c7066325f120596513d4fdadc18181cd001f8ff5c68ace5f5
tables.md    a377534745797b6becfa8900584f089af78a6cd2c7c9d0c3d4d4dfeb08d0fa03
```
The reader sentence is present beside the headline, verbatim apart from Markdown wrapping:
> Self-audit changed accuracy by +0.89 percentage points (problem-cluster percentile interval −3.54 to +5.88; 112 instances from 96 problems), establishing no improvement; the interval method was changed after analysis, its coverage in this clustered design is unvalidated, and modest benefits remain compatible with the data.
**May these numbers be quoted in a paper — yes with corrections.** The single most important reason for retaining that condition is that **the uncertainty calculations reproduce, but their written characterization remains contradictory**.
