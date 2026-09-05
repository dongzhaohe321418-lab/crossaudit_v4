# Independent cross-vendor review of the ceiling study, round 3 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over `study/ceiling` at d9bf61e against
merge base 19bd161. Verdict: **may be quoted — yes, with the listed
corrections.** Nuisance bound confirmed fixed; every interval array matches
round 2; 90 added cluster intervals, the power curve, the two survivors, the
freeze hash and byte-identical regeneration all reproduce. Remaining items are
reporting: one coverage figure labelled with the wrong scenario (0.924 is
q = 0.1; detrimental at q = 0.5 is 0.953); the blanket "2–5 points optimistic"
unsupported; opening and Table 9 labels; missing intervals in Tables 3, 4, 9;
legacy `finalised_at_commit` still present; and the consistency test does not
redden on a 0.01 mutation. Reader sentence supplied. Verbatim below.

---

**The numerical results reproduce, but the report still needs corrections before quotation.** The nuisance-bound defect is fixed. The remaining problems concern coverage claims, incomplete interval reporting, the consistency test, and contradictory provenance fields.
Reviewed `d9bf61efd8786779ae0d22ae470641bae43c8800`, using merge base `19bd1615c3d35381c37525721b6d38c5831b1ee5`. Both the diff and branch-only history for `src/` are empty. The statement “commits touch `benchmarks/` only” is slightly inaccurate: `.gitignore` also changed.
No files modified or network used. Detector readings were not adjudicated. **All 21 test functions passed**—17 statistics tests and four consistency tests—by direct invocation under Python 3.13.5; `pytest` was unavailable. The full application and hidden suites were not rerun.
**1 — Paired intervals and coverage: fixed-but-new-problem.**
Both nuisance bounds are corrected. Executing the committed functions gives:
| Call | Recomputed interval |
|---|---|
| `tango_score_interval(20,70,112)` | `[−0.576935424475, −0.290871853774]` |
| `exact_unconditional_interval(0,40,40)` | `[−1, −0.800000071526]` |
Sign symmetry passes for all five requested triples: `(20,70,112)`, `(3,2,112)`, `(11,2,112)`, `(0,4,56)`, `(16,1,56)`. With the default 40-grid exact method, the largest sign-symmetry discrepancy was **5.56×10⁻¹⁷ for Tango and zero for exact**.
My coverage recomputations are:
| Method | Beneficial: `D~Bin(112,.1)` | Detrimental: `C~Bin(112,.5)` |
|---|---:|---:|
| Ideal percentile bootstrap | **0.923731894539** | **0.953264931806** |
| Tango | **0.960370409515** | **0.953264931806** |
| Committed exact-grid interval, literal endpoint containment | **0.996879092228** | **0.983740418538** |
Exact recomputation: sum the binomial masses over accepted counts. These are bootstrap **7–18**, Tango **5–17**, exact **4–24** in the beneficial scenario; bootstrap/Tango **46–66**, exact **45–71** in the detrimental scenario. I independently checked Tango using the nuisance parameter `s=p_b+p_c`, and the grid test using convolution of the −1/0/+1 distribution.
**The report’s detrimental bootstrap value `0.924` is wrong for its stated scenario.** It would apply to the sign-reversed **q=.1** scenario, not **q=.5**. The committed bootstrap coverage test exercises only the beneficial scenario.
There is also a numerical boundary issue. At `(b,c,n)=(0,44,112)`, the grid test accepts `δ=−.5`, with **p=0.050731428873**, but bisection returns lower endpoint **−0.499999993614**, excluding −.5. Direct test acceptance includes **44–71**, giving **0.989508639384** coverage. The difference is exactly the mass at C=44, **0.005768220846**. Thus the stated `0.984` reproduces for the returned intervals, but depends materially on inward endpoint rounding.
The finite bootstrap simulations also reproduce: **280/300=.933333** independent and **269/300=.896667** clustered.
The replacement blanket assertion—“every interval … 2–5 points optimistic”—is unsupported. These scenarios do not establish coverage for every estimand or the actual clustered design; several check coverages exceed .95. Correct the scenario labels and report measured coverage without generalizing it. See [coverage discussion](benchmarks/code/RESULTS-CEILING.md:359).
**2 — Problem clustering: still-present in reporting; calculations fixed.**
All **143 pre-existing interval arrays** match round 2 exactly, not merely to displayed precision. Regeneration confirms the current implementation produces them.
The headline remains:
- Cluster: **[−3.539823, +5.882353] pp**
- Tango: **[−3.975142, +6.062178] pp**
- Exact grid: **[−6.696423, +8.482138] pp**
The sole `b<c` outcome contrast, self−cross `(3,5)`, remains:
- Cluster: **[−7.826087, +4.385965] pp**
- Tango: **[−7.785014, +3.806057] pp**
- Exact grid: **[−10.267855, +6.696427] pp**
I independently reproduced **90 added cluster intervals**: 40 in Table 2, 40 in Table 4, six in Table 5b, and four in Table 9. I reconstructed per-instance quantities, resampled sorted whole-problem clusters 10,000 times, divided by each resample’s instance count, and linearly interpolated positions `9999×.025` and `9999×.975`.
For **46/57**:
| Seed | Recomputed interval |
|---|---|
| Manifest’s category seed `20260919` | **[66.101695, 93.106371]%** |
| Earlier review’s seed `20260908` | **[66.666667, 93.103448]%** |
**The difference is the seed, not interpolation.**
Table 9 reproduces as cross **[20.388350,42.156863]%**, self **[7.843137,27.884615]%**, astra **[20.388350,45.631068]%**, residual **[40.384615,64.423077]%**.
Remaining reporting defects:
- The [opening still gives 46/57 the old Wilson interval `[68.7,88.9]`](benchmarks/code/RESULTS-CEILING.md:88).
- [Table 9](benchmarks/code/RESULTS-CEILING.md:443) labels its **cluster** intervals “95% Wilson”; Wilson is not printed beside them.
- Table 4’s single-family comparator rates still lack intervals.
Table 7b’s Tango column is present; its one-signed C contrast reproduces **[5.28,23.63] pp**. Table 6’s explicit 0/56 degeneracy warning is present.
**3 — Limits, mechanism, and headline: reproduced-as-fixed, with a power-wording qualification.**
The title and opening now say **no improvement was established**. The mechanism paragraph explicitly disclaims measuring what a model could infer.
Independent subset enumeration still gives:
`R(7)=0.280681818182`, `R(8)=0.300000000000`; gain **1.931818 pp**.
Independent power calculation—conditioning on total discordance and then enumerating its direction—gives:
| True improvement | Power |
|---|---:|
| +5 pp | **0.321205378390** |
| +7.5 pp | **0.600805436163** |
| +10 pp | **0.811489664209** |
The model uses **112 independent multinomial pairs**, fixing worsening probability at **2/112**, with improvement probability `2/112+δ`. Total discordance therefore varies as `4/112+δ`; it is not held at the observed 5/112. The report explicitly states the fixed worsening rate, but this is an instance-independent McNemar calculation, not power for a clustered procedure.
Replace “could not have detected a small one either way” with **“had limited power to detect small effects.”** Power .32 is not zero.
**4 — Multiplicity: reproduced-as-fixed substantively.**
I reconstructed all **16** paired contrasts from records. Exactly two survive **.05/16=.003125**:
| Contrast | McNemar p | Exact cluster sign-flip p |
|---|---:|---:|
| Referent−cross P flags | **0.000274658203125** | **0.0008544921875** |
| Referent−cross pooled flags | **0.00000298023223877** | **0.0000100135803223** |
Both are named and exploratory. Referent net does not survive.
The threshold appears **once in the live statistical-analysis prose, twice in the entire report**—the other occurrence is in the historical correction table. Thus literal “once anywhere” is not satisfied.
The previously noted sampled pooled self−cross cluster p remains **0.123739381303**; independent exact dynamic programming gives **0.122053205967**. Its sampled status is disclosed and its threshold decision is unchanged.
**5 — Timeouts: reproduced-as-fixed.**
Archived scoring records reproduce **seven timeouts**, **103 remaining instances**, unions **32/18/34**, and residual **54**. Three timeouts remain in the registered residual. The population definition and sensitivity distinction are explicit.
**6 — Provenance: still-present, narrowly; the substantive freeze check now works.**
The `analysis_freeze` locator resolves to **`05985f30c2f5b27e1942d760a9b87557d724d8d9`**. Its `report_ceiling.py` hash equals the current file:
```text
ed4460a84741017c046dd9f8d7db480177041e9a347f5e2f76a7d13b3e08029b
```
Every recorded code-file hash matches. Independent ledger grouping reproduces **12 detection windows/3,096 events** and **nine loop windows/679 events**. Completion fields are correctly renamed.
Unmatched invocation stamps reproduce as **22 `ceiling-loop-self-loop` events plus two `ceiling-loop` events**, **24 total**. They are counted by prefix, not individually enumerated. Seeds are present, astra’s endpoint is `AUTHOR_INPUT_NEEDED`, and package versions are explicitly retrospective.
However, **both manifests still retain `finalised_at_commit: f7f515e…`**. It was not renamed away as the report claims. The old freeze wording also remains beside the corrective block. Remove or explicitly deprecate these contradictory legacy fields.
**7 — Non-solution counts and bias directions: reproduced-as-fixed.**
Recounted non-solution returns: **4/4/2/0**. Recounted discarded-run failed audits: **21/93/109/107**. Outcome-informed adaptation and undetermined bias directions remain correctly disclosed.
**8 — Residual descriptions, interval completeness, and consistency guard: still-present.**
All **178 archived evidence files** match their hashes. Each self draw flags **17** P instances, union **19**. Actual final solution strings match **112/112** between self and replicate; flags and outcomes match, while `report_sha256` differs for `b1:HumanEval/35`.
The requested grep finds the prohibited phrases absent as live assertions or historically/explicitly qualified. “Bias: none” remains qualified to excluding stratum F from primary outcomes.
But the interval requirement remains incomplete: Table 3’s component asymptotes, Table 4’s comparator rates, Table 9’s registered rates, several opening repetitions, and conclusion rates lack intervals. Small residual categories still appear as percentages, including **3/57=5.3%**.
All **99 generated table rows** occur in the report. That does not validate surrounding prose.
The [consistency test](benchmarks/code/tests/test_report_consistency.py:76) passes, but the required mutation test **does not turn red**:
| In-memory mutation | Result |
|---|---|
| `[-32.1,-2.3]` → `[-32.11,-2.3]` | Pass |
| `[−3.54,+5.88]` → `[−3.55,+5.88]` | Pass |
| `[5.2,17.2]` → `[5.21,17.2]` | Pass |
| `[5.2,17.2]` → `[55.2,77.2]` | Fail |
It rounds candidates to one decimal and allows **0.051** tolerance. Its regex also ignores Unicode minus signs and leading positive signs: replacing the headline with **`[−99.99,+99.99]` still passes**.
The collector **does walk all 40 nested per-K intervals**. Its failure is extraction and comparison precision, plus allowing any matching interval without checking the corresponding estimand.
**9 — Fitter bounds: reproduced-as-fixed.**
`fit_saturation(union_curve([1]*110,8))` returns **A=1.0**, **τ=4.740000864244**. The constraint remains inside the objective. Existing fitted estimates and intervals are unchanged.
**Regeneration:** with credential-like environment variables removed, sockets disabled, and output writes intercepted in memory, `main([])` returned zero and reproduced both files byte-for-byte:
```text
numbers.json
1a282d1693362789136eeeb2cece9d6bbccfece6298a1354446ed093a31d51fa
tables.md
5b52776421fd2f5d72e20073035c797430758cb0da64360442f2ad36331cbeb4
```
**Amendment 5 and CORRECTIONS 17–19:** candid about post-hoc correction, but **not complete closure**. Amendment 5/#17 inherit the unsupported blanket undercoverage claim; Amendment 5 also contains the wrong detrimental bootstrap value. The old .960/.075 comparison should identify its different methods and scenarios explicitly. #18’s two survivors and #19’s power numbers reproduce. The report’s assertion that its consistency guard catches every absent prose interval is demonstrably false.
**May these numbers be quoted in a paper — yes with the listed corrections.** The single most important reason for conditioning approval is that **the empirical estimates reproduce, but their uncertainty is still mischaracterized**.
The sentence a reader must see beside the headline:
> Self-audit changed accuracy by +0.89 percentage points (problem-cluster percentile interval −3.54 to +5.88; 112 instances from 96 problems), establishing no improvement; the interval method was changed after analysis, its coverage in this clustered design is unvalidated, and modest benefits remain compatible with the data.
