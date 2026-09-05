# Independent cross-vendor review of the ceiling study, round 2 — 2026-09-05

Reviewer: `gpt-6-astra`, read-only, over `study/ceiling` at 4657e7f.
Verdict: **calculations reproduce; not quotable as presented.** Fixed and
confirmed: withdrawn interval retained and labelled; all cluster rows; fitter
bounded inside the objective; timeouts named with sensitivity table;
non-solution counts; deviations relabelled; regeneration byte-identical.
Remaining: both replacement check intervals bound the nuisance with
(1−|δ|)/2 where (1−δ)/2 is valid for negative δ (exact method coverage 0.075
in the detrimental direction); the bootstrap covers 0.92–0.93 at n=112, not
0.95, and the "0.998" is from n=40; the title and opening say "did not raise"
where the evidence supports "no improvement established"; two contrasts
survive the family threshold, not one; Tables 2, 4, 5b, 9 still Wilson or
without intervals; provenance fields name the wrong commit and omit windows.
Verbatim below, paths shortened.

---

**The calculations reproduce, but the revised report is still not ready for quotation.** The replacement methods introduce a real implementation defect, and several corrections claimed as complete remain incomplete.
Reviewed `4657e7fe7aa5ea62dc02f84070828ba9f8cb7d7e`, against the nine findings in the first review. No files modified, no network used, and no model readings adjudicated.
The committed statistics suite passed: **15 passed**, using the existing `crossaudit_integ` Python environment, with bytecode, pytest caching, and filesystem-based output capture disabled. The suite’s passing status does **not** substantiate all its coverage claims.
**1 — Paired-difference interval: fixed-but-new-problem.**
The withdrawn construction is preserved in `numbers.json` under `withdrawn_conditional_ci95`, explicitly labelled withdrawn. That correction is honest.
I independently enumerated \(D\sim\mathrm{Binomial}(112,0.1)\), all discordances beneficial, so the true difference is 0.1:
| Method | My coverage |
|---|---:|
| Withdrawn conditional × observed discordance | **0.4162688657** |
| Ideal percentile bootstrap, independent singleton clusters | **0.9237318945** |
| Independently implemented Tango score inversion | **0.9603704095** |
| Berger–Boos grid inversion | **0.9968790922** |
Exact recomputation:
- Withdrawn: sum binomial probabilities for \(D=12,\ldots,17\).
- Bootstrap: enumerate \(D^*\sim\mathrm{Binomial}(112,D/112)\), take its 2.5% and 97.5% quantiles, and sum outer probabilities where they contain 0.1. Accepted \(D=7,\ldots,18\). This removes finite-bootstrap Monte Carlo noise.
- Tango: independently maximize the constrained multinomial likelihood using \(s=p_b+p_c\), then invert \((b-c-n\delta)^2/[n(\hat s-\delta^2)]\le1.959964^2\). Accepted \(D=5,\ldots,17\).
- Berger–Boos: independently invert binomial tails for the nuisance confidence set and obtain the distribution of \(b-c\) by repeated convolution of probabilities for −1/0/+1. Use the committed 40-grid, \(\gamma=10^{-4}\) settings. Accepted \(D=4,\ldots,24\). Running the committed interval function over the same enumeration gives the same coverage.
The report’s **0.998** comes from a **different scenario**, \(n=40,q=0.15\): I obtained **0.9984710249**. Calling these results “the same scenario” is incorrect.
The committed bootstrap simulation itself produces:
| Simulation | Covered |
|---|---:|
| 112 independent instances | **280/300 = 0.933333** |
| 56 perfectly correlated two-instance clusters | **269/300 = 0.896667** |
Its assertion accepts coverage down to **0.88**. Thus “0.95 nominal by simulation” overstates the evidence. See [coverage tests](benchmarks/code/tests/test_ceiling_stats.py:230) and [coverage claims](benchmarks/code/RESULTS-CEILING.md:502).
More seriously, **both replacement check implementations use the wrong nuisance upper bound for negative differences**. With \(q=p_c\), the valid bound is \((1-\delta)/2\), not \((1-|\delta|)/2). See [Tango](benchmarks/code/report_ceiling.py:154) and [exact-unconditional](benchmarks/code/report_ceiling.py:240).
My counterexamples:
- `tango_score_interval(20,70,112)` returns **[−0.538750, −0.357660]**; independent constrained inversion gives **[−0.576935, −0.290872]**. Swapping the counts exposes the broken sign symmetry.
- `exact_unconditional_interval(0,40,40)` returns **[−1,−1]**; the independently implemented construction gives **[−1,−0.800000]**.
- Enumerating detrimental discordances \(C\sim\mathrm{Binomial}(112,0.5)\) gives the committed “exact” method coverage **0.0752249063**, accepting only \(C=56\).
Additionally, maximizing over 41 grid points without bounding the missed supremum does not establish guaranteed exact coverage. “Never under-covers” is untenable.
**2 — Problem clustering: still-present, although the main rows are corrected.**
I independently rebuilt signed changes from the JSONL records, grouped by `problem_id`, resampled whole problems **10,000 times with seed 20260908**, divided by each resample’s instance count, and linearly interpolated percentile positions \(9999\times0.025\) and \(9999\times0.975\). Cluster p-values were independently computed by dynamic programming over signed problem totals.
The requested rows reproduce:
| Quantity | Point | Cluster interval | McNemar p | Cluster p |
|---|---:|---|---:|---:|
| Self-loop net | +0.892857 pp | **[−3.539823, +5.882353]** | 1 | 1 |
| Self-loop replicate net | +0.892857 pp | **[−3.539823, +5.882353]** | 1 | 1 |
| Cross-loop net | +2.678571 pp | **[0, +7.142857]** | 0.25 | 0.5 |
| Referent-loop net | +8.035714 pp | **[+1.769912, +15.255764]** | 0.022460938 | 0.046875 |
| Referent−cross final outcome | +5.357143 pp | **[−0.892857, +12.068966]** | 0.145996094 | 0.182617188 |
| Referent−cross P flags | +26.785714 pp | **[+13.559322, +40.350877]** | 0.000274658 | 0.000854492 |
| All-family residual | 51.818182% | **[40.000000, 63.302752]%** | — | — |
The residual uses **seed 20260912**, matching the code’s `BOOT_SEED + 4`.
For the headline, independent check intervals reproduce:
- Withdrawn: **[−3.155064, +3.993349] pp**
- Tango: **[−3.975142, +6.062178] pp**
- Berger–Boos grid: **[−6.696423, +8.482138] pp**
**The kill condition fires under all four methods:** every headline interval contains zero. The implementation defect above does not change these particular check endpoints.
The remaining requested checks also reproduce:
| Contrast | Tango, pp | Berger–Boos grid, pp |
|---|---|---|
| Cross-loop | [−0.726388, +7.580545] | **[−4.464282, +9.644212]** |
| Referent-loop | [+2.025264, +15.266802] | [−1.785711, +17.410710] |
| Referent−cross outcome | [−0.816025, +12.356812] | [−4.464281, +14.732143] |
| Referent−cross P flags | [+14.449565, +40.169320] | [+6.250003, +43.749997] |
**Cross-loop’s one-signed marking is honest**, and its unconditional interval is printed beside it.
But clustering remains unresolved elsewhere: Table 5b and the opening still use Wilson for residual categories. My independent problem bootstrap for **46/57 uncovered-class instances** gives **[66.6667%, 93.1034%]**, while the report retains **[68.7%, 88.9%]**. Table 9 also supplies only Wilson intervals. The claim that every interval now preserves clusters is false.
The one-signed caveat is inconsistently applied: Table 7b marks referent−cross C flags with † but supplies neither unconditional interval there, and the prose repeats its bootstrap interval without that qualification. Table 6’s **0/56 broken [0,0]** also needs an explicit degeneracy warning.
**3 — Limits and mechanism claims: still-present.**
My explicit enumeration of all cross-draw subsets gives:
\[
R(7)=0.2806818182,\quad R(8)=0.3000000000,
\]
a **1.931818-point** last-step gain.
The extrapolation warning is now prominent, and the prohibited “in the limit”/“cannot be seen” language survives only in the historical correction table.
However, the title still says **“self-audit did not raise accuracy”**, and the opening answers whether it can raise accuracy with **“no.”** Those statements exceed an inconclusive interval. The evidence supports **no improvement established**.
The report also retains “a model … has no evidence … that the omitted input classes exist” at lines 75–76 and 370–371. The intervention and observed flags do not establish that mechanism. These are reporting inferences, not judgments about any detector’s readings. See [opening](benchmarks/code/RESULTS-CEILING.md:11).
**4 — Multiplicity: still-present.**
Recursive enumeration of regenerated `numbers.json` gives **16 `p_exact` entries and 16 accompanying cluster-p entries**:
| Contrast | McNemar p | Cluster p |
|---|---:|---:|
| Self net | 1 | 1 |
| Self replicate net | 1 | 1 |
| Cross net | 0.25 | 0.5 |
| Referent net | 0.022460938 | 0.046875 |
| Self−cross outcome | 0.7265625 | 0.78125 |
| Referent−cross outcome | 0.145996094 | 0.182617188 |
| Self−replicate outcome | 1 | 1 |
| Self−cross P flags | 1 | 1 |
| Self−cross C flags | 0.012939453 | 0.012939453 |
| Self−cross pooled flags | 0.087158553 | 0.123739381* |
| Referent−cross P flags | **0.000274658** | **0.000854492** |
| Referent−cross C flags | 0.015625 | 0.015625 |
| Referent−cross pooled flags | **0.000002980232** | **0.000010013580** |
| Self−replicate P flags | 1 | 1 |
| Self−replicate C flags | 1 | 1 |
| Self−replicate pooled flags | 1 | 1 |
\*The reported sampled p reproduces; independent exact dynamic programming gives **0.122053206**. This does not change its threshold decision.
The declared family size is **16**, threshold **0.05/16 = 0.003125**, displayed as **0.00313**. There is one declared policy, although the displayed threshold occurs **13 times**, not once.
**Two contrasts survive**, on both p-value versions: referent−cross **P flags and pooled flags**. “Exactly one” remains false at [line 535](benchmarks/code/RESULTS-CEILING.md:535), also repeated in the opening.
The report **correctly says referent-loop net does not survive correction**.
The five undelivered contrasts are identifiable by name through `planned_twelve` and the referenced item numbers:
- A(mixed)−A(cross), K=8
- A(mixed)−A(self), K=8
- A(astra)−A(cross)
- A(astra)−A(self)
- A(mixed-with-astra)−A(mixed-without)
Deviation 15 honestly records their non-delivery.
**5 — Timeouts in the population: reproduced-as-fixed.**
I parsed both archived `scored-<batch>.jsonl` files, selected P records with `hidden.timed_out`, and recomputed unions from the detector records.
Result: **seven timeouts; 103 remaining instances; unions 32/18/34; residual 54**. Three timeouts occur in the loop and remain nonpassing in every arm. Three occur in the all-family residual.
The revised population-definition paragraph and sensitivity table acknowledge this correctly. The remaining Wilson issue belongs to finding 2.
**6 — Provenance and beta history: fixed-but-new-problem.**
Both manifests now contain package versions, route metadata, corrected sampling metadata, and the original dirty-tree record. Provider code confirms **self sends temperature 0**; the astra invocation supplies no temperature argument.
All recorded code-file hashes match the current files. The corrected `report_ceiling.py` SHA-256 is:
```text
f2d50516cf7ad4dbbb2919d1dacea3b17c57e300bc2111a7a6991722441e90f6
```
But:
- Both `finalised_at_commit` fields name **f7f515e**, whose analysis-file hash is **ba270360…**, while claiming that commit is the clean analysis freeze.
- The 12 detection windows reproduce from ledger completion timestamps, but omit astra and inherited draws.
- The nine loop windows reproduce, but omit **22 unstamped self-loop ledger events** from the pilot work.
- These “start” timestamps are first recorded completions, not invocation starts.
- Package versions were collected retrospectively from the installed environment.
- Broker base URLs are present; astra’s actual endpoint is unrecorded.
- Neither manifest records the bootstrap seed; **20260908** is recorded in the analysis, numbers file, and amendment.
The beta-history correction is accurate. I checked the git artifacts and timestamps: erroneous table at **18:46:39**, fix at **18:48:18**, first report at **20:55:51**.
**7 — Non-solution counts and bias directions: reproduced-as-fixed.**
Counting nonempty `returned_non_solution` fields reproduces **4/4/2/0**. Counting `audit_ok == false` in the archived discarded run reproduces **21/93/109/107**.
The revised deviations acknowledge outcome-informed pilot adaptation and use **direction undetermined** for the discarded-run and failed-revision issues. The remaining “Bias: none” at line 599 is specifically qualified to excluding stratum F from the primary outcomes.
**8 — Residual description and summary reporting: still-present, with several subfixes verified.**
I checked the archived `Mbpp/305` witnesses: lowercase p-words and words split across elements are now included in its corrected description. All **178 archived evidence files** match their manifest hashes.
Independent counts confirm **17 flags in each self draw, union 19: two additional instances**. Comparing actual solution strings confirms **112/112 identical final solutions**; flags and outcomes also match, while `report_sha256` differs for `b1:HumanEval/35`.
The interval requirement remains incomplete:
- Table 1’s main rates now carry intervals.
- **Tables 2 and 4 still lack them.**
- Several opening repetitions and conclusion rates lack intervals.
- Small residual categories remain percentages with Wilson intervals.
- Prose at lines 65 and 422, and CORRECTIONS #15, quotes **[−0.88,+12.08]**, while regeneration gives **[−0.89,+12.07]**.
The requested grep finds “the referent does” absent; historical/qualified occurrences of “in the limit,” “cannot be seen,” “no number had left,” and “byte-identical” are acceptable. **“Exactly one” is still asserted as current fact.**
**9 — Fitter bounds: reproduced-as-fixed.**
Executing
```python
fit_saturation(union_curve([1] * 110, 8))
```
returns **A=1.0**, \(\tau=4.7400008642\). The projection occurs inside the SSE objective. Both bootstrap paths now consume the same constrained fitter without different post-fit clipping.
All six P/C fitted point estimates equal the previous committed values exactly. Quoted P asymptotes remain **31.5%, 16.6%, 32.5%**, with unchanged rounded intervals.
Independent K_max bootstraps also match round one:
- Cross: **[20.0,40.7]%**
- Self: **[8.3,27.3]%**
- Astra: **[20.7,45.0]%**
**Amendment 4 and CORRECTIONS #15–16:** the post-hoc timing, withdrawal, reader’s right to discount the amendment, and committed-artifact history are explicit and honest. They are **not complete closure**: the coverage assurances inherit finding 1, CORRECTIONS #15’s multiplicity correction contradicts the live report, and its referent−cross interval is stale.
**Regeneration:** I ran `report_ceiling.main([])` with credential-like environment variables removed, sockets disabled, and only its directory/output operations intercepted in memory. Both outputs were **byte-identical**:
```text
numbers.json
35ee804691bd1eeb92fa802c7b8646b391f927a33bea630f92b030808015b358
tables.md
5ba1b34b0677c4e67de762bcff30d63eb10eaab71e7f7d55a9776f6ab2ca2ecc
```
The full application suite and hidden suites were not rerun.
**May these numbers be quoted in a paper — no, as presented. The single most important reason is that the revised coverage assurances remain false: the primary bootstrap undercovers in the stated scenario, and the supposedly guaranteed exact check has a demonstrable nuisance-bound defect.**
