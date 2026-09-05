# Independent cross-vendor review of the ceiling study — 2026-09-05

Reviewer: `gpt-6-astra` via Codex CLI, read-only, over `study/ceiling` at
f7f515e. Conflict noted in the brief: one detector family is astra; the
reviewer was told to review analysis code and statistics only, and states it
did not adjudicate any model's readings.

Verdict as received: **every number reproduces; not quotable as presented.**
The headline "95% exact" interval estimates the wrong quantity (conditional
direction probability × observed discordance fraction): simulated coverage
0.416. Instances are clustered by problem (112 from 96; 110 P from 56) and
McNemar/Wilson ignore it. Comparison count is 16 performed vs 12 planned.
Seven timeouts sit inside an "assertion-confirmed" population. Several
sentences claim limits and mechanisms the data do not reach. Verbatim below,
paths shortened.

---

**I would withhold quotation approval for the report as written.** The headline arithmetic reproduces, but its “95% exact” confidence interval is not a valid interval for the stated population pass-rate change. Clustering, multiplicity, and several substantive claims also need correction.
Reviewed commit `f7f515ef848c4443e7a40588cb592094b6c2ea01`. No files changed; no keys or network used. I did not adjudicate whether any model’s flags—including astra’s—were correct. Residual spot-checks assess the classification rule, not detector judgments.
**Findings, ranked by severity**
**1. Critical — the paired-difference interval estimates the wrong quantity.**  
[report_ceiling.py:132](benchmarks/code/report_ceiling.py:132), [RESULTS-CEILING.md:459](benchmarks/code/RESULTS-CEILING.md:459).
The code correctly computes a Clopper–Pearson interval for the direction probability **conditional on discordance**, then multiplies by the *observed* discordance fraction. For the population risk difference,
\[
\delta=q(2\pi-1),
\]
the discordance probability \(q\) is unknown. Replacing it by \(D/n\) discards its uncertainty. Conditioning legitimately supports McNemar’s null test; it does not make this transformed interval an exact interval for the unconditional risk difference.
**Exact recomputation:** I enumerated \(D\sim\mathrm{Binomial}(112,0.1)\), with every discordance beneficial, so the true difference is 0.1. The implemented interval becomes
\[
[D(2\,0.025^{1/D}-1)/112,\ D/112].
\]
Summing binomial probabilities over intervals containing 0.1 gives **coverage 0.4162688657**, not 0.95. Excluding \(D=0\) gives 0.4162719884.
Thus the headline interval and the referent intervals reproduce **as calculations**, but cannot be quoted as the advertised confidence intervals. This defect remains after the beta-tail fix.
**2. High — binary inference ignores the problem clusters that the bootstrap correctly preserves.**  
[report_ceiling.py:633](benchmarks/code/report_ceiling.py:633), [report_ceiling.py:680](benchmarks/code/report_ceiling.py:680), [report_ceiling.py:533](benchmarks/code/report_ceiling.py:533).
The loop contains **112 instances from 96 problems**. The detection P population contains **110 instances from only 56 problems**. McNemar and Wilson calculations nevertheless treat instances as independent trials.
**Exact recomputation:** grouping loop changes by `problem_id` gives self-loop’s nonzero cluster totals `[-1,-1,1,2]`: two of its three repairs are `Mbpp/297` in different batches. As a sensitivity check, enumerating every joint sign flip of the nonzero problem totals gives:
| Contrast | Reported instance-level p | Problem-level sign-flip sensitivity p |
|---|---:|---:|
| Self-loop net | 1.000000 | 1.000000 |
| Cross-loop net | 0.250000 | 0.500000 |
| Referent-loop net | 0.022461 | 0.046875 |
| Referent-minus-cross P flags | 0.000275 | 0.000854 |
These sensitivity tests require their own exchangeability assumption; they demonstrate that the reported p-values are not cluster-aware.
For the residual, 10,000 problem-cluster resamples with seed `20260908` give **[40.2%, 63.6%]**, versus the reported Wilson **[42.6%, 60.9%]**. For the uncovered-class share, the corresponding sensitivity interval is **[66.7%, 93.1%]**, versus **[68.7%, 88.9%]**.
**Nothing found:** no test treats the 20 detector readings as 20 independent instances. The saturation bootstraps correctly resample whole problems and refit inside each draw.
**3. High — finite observations are promoted into unlimited-reading and causal mechanism claims.**  
[RESULTS-CEILING.md:14](benchmarks/code/RESULTS-CEILING.md:14), [RESULTS-CEILING.md:331](benchmarks/code/RESULTS-CEILING.md:331), [RESULTS-CEILING.md:651](benchmarks/code/RESULTS-CEILING.md:651).
The report claims an ordering “in the limit of unlimited readings” and says omitted input classes cannot be seen because evidence of their existence is absent. Neither follows from these data.
**Recomputation:** cross recall rises from **0.2806818182 at K=7 to 0.3000000000 at K=8**, a **1.931818-point** gain. It has not flattened under the preregistered criterion. The detailed caveat at lines 161–165 is honest; the opening, table, and concluding claims do not consistently carry it, contrary to preregistration.
An underestimated asymptote is a lower estimate of eventual recall, not evidence of a low upper ceiling. Hand-classifying missed cases cannot establish zero future detection probability.
The title’s “the referent does” also overstates the loop result. The actual referent-minus-cross loop contrast is **+5.36 pp**, reported interval **[−1.54, 9.54]**, **p=0.145996**. The **+8.04 pp** compares referent-loop with its own baseline. Changing instructions supports an effect of that intervention on flags, not the claimed explanation of what models cannot reason about.
Likewise, failure to demonstrate improvement supports “no improvement established,” not proof that improvement is absent.
**4. High — twelve is the planned comparison count, not a reconciled inventory of analyses performed.**  
[PREREGISTRATION.md:310](benchmarks/code/ceiling/PREREGISTRATION.md:310), [PREREGISTRATION.md:475](benchmarks/code/ceiling/PREREGISTRATION.md:475), [RESULTS-CEILING.md:469](benchmarks/code/RESULTS-CEILING.md:469).
**Exact recomputation:** recursively enumerating `p_exact` entries in regenerated `numbers.json` finds **16**: four arm nets, three final-outcome contrasts, and nine flag contrasts across P/C/pooled populations. These are not necessarily 16 distinct hypothesis families, but they already differ from the twelve-item plan. There are also fitted P/C contrasts and numerous mixed-family comparisons.
Conversely, the five planned mixed/astra asymptote contrasts are not delivered as the specified fitted contrasts with uncertainty. Table 4 substitutes raw mixed-union summaries.
The highlighted referent P-flag contrast is absent from the explicit twelve-item enumeration. The pooled referent flag comparison also clears the stated threshold: **p=0.000002980232**, contradicting “exactly one” across the analyses actually computed.
Provide a complete planned/performed/exploratory comparison inventory and define the correction family. The flag effect would still pass a simple Bonferroni-over-16 threshold; this is an accounting and inference-policy defect, not evidence that the flag difference disappears.
**5. High — timeouts remain inside a population repeatedly described as assertion-confirmed defects.**  
[RESULTS-CEILING.md:64](benchmarks/code/RESULTS-CEILING.md:64), [RESULTS-CEILING.md:301](benchmarks/code/RESULTS-CEILING.md:301).
This repeats the ground-truth issue identified in the corrections record.
**Recomputation:** archived baseline scoring records contain **seven P timeouts**; three occur in the loop sample. All three remain unchanged and nonpassing in every loop arm. Three also remain in the all-family residual, despite prose saying they are not counted as missed defects.
A sensitivity exclusion of all seven yields **103 assertion-failure instances**, raw unions **32 cross, 18 self, 34 astra**, and residual **54**, rather than 110/33/19/36/57.
Keep the preregistered population for its registered analysis, but label it accurately as hidden-suite nonpasses, explicitly including timeouts, and distinguish assertion-failure sensitivity results.
**6. Medium — provenance is incomplete, and the beta-bug history is overstated.**  
[manifest_loop.json:32](benchmarks/code/records/ceiling/manifest_loop.json:32), [manifest_ceiling1.json:217](benchmarks/code/records/ceiling/manifest_ceiling1.json:217), [RESULTS-CEILING.md:485](benchmarks/code/RESULTS-CEILING.md:485).
**Recomputations:** parsed both manifests, checked recorded file hashes, and inspected `git log`/`git show`.
- Python 3.13.5, model IDs, dataset revisions/digests, and harness SHAs are present.
- All **5,200 analysed detection readings** have prompt SHA-256 values.
- Package versions, per-arm start/end times, and provider base URLs are absent from these manifests.
- Sampling metadata incorrectly says temperature is universally omitted; the self provider code sends zero.
- Both recorded working trees are dirty; loop’s includes modified `loop.py`.
- Ceiling 1’s recorded `report_ceiling.py` hash does not match the final analysis file.
- The sample file first appears in the completed-loop commit, although its contents reproduce from the registered seed and sorted-cell algorithm.
The tail correction is correct: sweeping every \(k=0,\ldots,n\), \(n=1,\ldots,60\), gives maximum defining-tail error **5.87×10⁻¹⁵**.
But `git show 1a66571:benchmarks/code/records/ceiling/tables.md` contains the erroneous headline interval **[+3.16, −1.93]**, committed at **18:46:39 +08:00**, before fix `7dc2620` at **18:48:18**. “No number had left the harness” needs qualification: erroneous numbers had entered committed results artifacts.
**Nothing found:** the final report was committed at **20:55:51**, after the fix, and its generated intervals contain no stale swapped-tail values.
**7. Medium — deviation statements contain factual errors and unsupported directions of bias.**  
[RESULTS-CEILING.md:530](benchmarks/code/RESULTS-CEILING.md:530).
**Exact recomputation:** counting nonempty `returned_non_solution` fields gives:
| Arm | Returned non-solution files |
|---|---:|
| self-loop | 4 |
| self-loop-rep | 4 |
| cross-loop | 2 |
| referent-loop | 0 |
All ten affected records say tests were touched. The assertion that every arm’s count is zero is false.
I counted **14 numbered deviations**. The pilot-induced prompt change is appropriately acknowledged as favoring the loop relative to the original configuration; however, it is outcome-informed protocol adaptation on reused instances.
For the discarded four-arm run, the archived failed-audit counts reproduce as **21, 93, 109, 107**. A full rerun avoids retaining only successful instances, but does not itself prove “bias: none.” Neutrality requires failures/discarding to be unrelated to potential outcomes; otherwise direction is undetermined. The statement that failed revisions necessarily bias net change downward is also too strong: a successfully obtained revision can break a solution.
**8. Medium — residual descriptions and summary numbers need correction.**  
[residual_classification.json:129](benchmarks/code/records/ceiling/residual_classification.json:129), [RESULTS-CEILING.md:27](benchmarks/code/RESULTS-CEILING.md:27).
`b1:Mbpp/305` is described as failing on empty lists or lists without p-words. Its archived witnesses also show failures with p-words present, involving lowercase handling and words split across list elements. The category may remain `unexercised-edge`, but the recorded description does not support the claimed “fails only” characterization.
**Recomputation:** all eight self draws flag **17 P instances individually**; their union contains **19**. They add **two**, not the opening’s “one more defect.”
Solution bytes reproduce identically for all 112 loop-replicate instances, but audit `report_sha256` differs for `b1:HumanEval/35`. Specify “identical final solutions, flags, and outcomes,” rather than unqualified byte-identical output.
Tables 1, 2, and 4, the opening, and the concluding comparison contain rates without intervals. Small disagreements are unnecessarily rendered as percentages at lines 197–199.
**Nothing found:** no misuse of “significant” as “large.” The noise-floor section correctly names the matching loop replicate and limits its measured zero spread; it does not import the earlier detection floor into loop inference.
**9. Medium — the fitter does not enforce its preregistered parameter bounds.**  
[report_ceiling.py:245](benchmarks/code/report_ceiling.py:245).
**Exact recomputation:**
```python
fit_saturation(union_curve([1] * 110, 8))
```
returns **A=250.3972002**, despite the registered \(A\in[0,1]\). Individual bootstrap estimates are clipped afterward; paired bootstrap differences are not.
I found no resulting discrepancy in the currently quoted rounded estimates. Nevertheless, clipping after optimization is not constrained least squares, and the two bootstrap paths implement different treatments of this boundary.
**Results that reproduced**
The headline’s six requested quantities reproduce from all instance records, without conditioning on revision:
- **112 instances: 56 P and 56 C**, with 28 in each batch/stratum cell.
- **3 repaired, 2 broken**.
- \(100(3-2)/112=\mathbf{+0.892857}\) pp.
- Implemented interval **[−3.155064, +3.993349]** pp.
- Exact instance-level McNemar **p=1.000000**.
Pairing is before/after and across arms **on the same instance**. These are not 56 P–C matched pairs. The registered kill condition fires because the registered statistic’s interval contains zero, not because a conditional statistic was substituted. The secondary problem bootstrap, **[−3.57, +5.88] pp**, also contains zero.
I independently enumerated every draw subset to check the union curves. All requested endpoints and fitted values reproduce:
| Family | Recall K=1 → Kmax | FP K=1 → Kmax | Fitted A, reported 95% CI |
|---|---|---|---|
| cross | 10.7% → 30.0%, 33/110 | 4.5% → 16.0% | 31.5% [21.7, 45.6] |
| self | 15.5% → 17.3%, 19/110 | 21.9% → 24.0% | 16.6% [8.1, 26.3] |
| astra | 30.2% → 32.7%, 36/110 | 9.7% → 10.7% | 32.5% [20.5, 44.8] |
The endpoint columns reproduce the report’s point estimates; their missing intervals are a finding above. Independently recomputed problem-bootstrap intervals for Kmax recall are **[20.0, 40.7]**, **[8.3, 27.3]**, **[20.7, 45.0]**%; corresponding FP intervals are **[10.1, 22.3]**, **[17.2, 31.2]**, **[5.9, 16.1]**%.
The fitted form is \(A(1-e^{-K/\tau})\), unweighted least squares over subset-averaged K points. The primary fitted difference reproduces as **−14.884279 pp [−32.061353, −2.287266]**; raw K=8 difference as **−12.727273 pp [−25.000000, −0.900901]**.
Referent P flags reproduce as **25 versus 10**, discordances **16/1**, **+26.785714 pp**, implemented interval **[12.938858, 30.266789]**, **p=0.0002746582**. Referent-loop net reproduces as **11 repaired/2 broken**, **+8.035714 pp**, implemented interval **[1.056922, 11.161274]**, **p=0.0224609375**. Interval/test qualifications above apply. Its secondary status and instruction to run a larger confirmatory study rather than change the default are explicit at [lines 666–669](benchmarks/code/RESULTS-CEILING.md:666).
Self draw-pair disagreements reproduce exactly:
`1,1,1,2,1,2,0,1,0,2,3,2,1,0,1`, each over 260 instances.
**Residual spot-check and timing**
The committed records reproduce **57/110**, reported Wilson **51.8% [42.6, 60.9]**, and classifications **46 uncovered-class, 8 spec-misreading, 3 timeout**.
Git establishes that the rule was committed at `d96cdaf`, **17:57:14**, before classification at `f7f515e`, **20:55:51**. It cannot establish when a person first privately inspected evidence.
Committed classification labels alone cannot independently validate their own classification. I therefore additionally read the local archived evidence, verified against the report’s committed manifest digest: **178 files, zero missing files, zero hash mismatches**.
For the first ten lexicographically sorted residual instances:
| Instance | Rule check |
|---|---|
| b1:HumanEval/151 | Boolean-input witness supports uncovered class |
| b1:Mbpp/102 | Repeated/boundary underscores support uncovered class |
| b1:Mbpp/103 | Zero-input witnesses support uncovered class |
| b1:Mbpp/109 | Partial rotations absent from visible cases; category supported |
| b1:Mbpp/113 | Empty/whitespace strings support uncovered class |
| b1:Mbpp/137 | All-zero array supports category; witness is 0 versus infinity |
| b1:Mbpp/267 | Recorded timeout correctly takes precedence |
| b1:Mbpp/278 | Missing nested tuple supports uncovered class |
| b1:Mbpp/294 | Boolean/float mixture supports uncovered class |
| b1:Mbpp/305 | Description incomplete, as detailed above |
These are evidence spot-checks, not fresh executions of the hidden suites or endorsement of the oracle.
**Reproducibility check**
I ran `report_ceiling.main([])` under Python 3.13.5 with credential-like environment variables removed, sockets disabled, bytecode disabled, and its two output writes captured in memory. Both outputs reproduced byte-for-byte:
- `numbers.json`: `66a476c9059159b680fe6c480a2e6642f95f5001ddd0000f48e2e97488bf7059`
- `tables.md`: `09b157ebc70d604f51efc4e915c2003163b81aca558c8ad02d607aa4ffc59adc`
Every generated table row appears in the report. All eight statistics tests passed. This verifies deterministic regeneration of the tables, **not every prose assertion**—several are contradicted above. The full application suite and hidden-suite re-execution were not run.
**May these numbers be quoted in a paper — no, as currently presented. The single most important reason is that the headline “95% exact” interval does not provide 95% coverage for the pass-rate change the paper claims to estimate.**
