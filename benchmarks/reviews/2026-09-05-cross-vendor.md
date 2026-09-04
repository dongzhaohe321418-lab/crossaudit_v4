# Independent cross-vendor review of the measurement code — 2026-09-05

An external reviewer running on a different vendor's model, read-only, over this
repository and the study worktrees. Commissioned because every review of this
project's measurement code until now had been the same vendor reviewing its own
work, which is the failure mode the product itself exists to address.

It found five high-severity publication-blocking issues, gave explicit negative
findings on the two questions that most threatened the results, and corrected an
error in `CORRECTIONS.md` itself. Findings acted on are recorded there; this file
is the report as received, unedited except that temporary scratchpad paths are
shortened to `SCRATCH` and the run directories referenced now live durably at
`~/Documents/Crossaudit/study-data/`.

Verbatim below.

---

I completed the audit and found multiple publication-blocking issues. I could not create the requested `findings.md`: the session’s read-only filesystem policy rejected the write.

1. **HIGH — Study 4 conditions on a post-treatment event.**  
   [analyse.py:130](<SCRATCH/wt-revision/benchmarks/expertlongbench/study4/analyse.py:130>), [RESULTS-4.md:3](<SCRATCH/wt-revision/benchmarks/expertlongbench/RESULTS-4.md:3>). The treatment decides whether a proposed revision is committed, but the primary analysis retains only instances with a committed revision. It therefore compares different selected subsets: C has 9 revised instances, T has 11, and the “paired” result uses only the 7 revised in both arms. The headline’s “On 16 paired instances” is false for that statistic.  
   Recomputing all 16 assigned pairs gives C final-minus-round-one −1.20 F1, T −5.21, and paired T−C change **−4.01**, BCa 95% CI **[−16.82,+8.10]**, Wilcoxon **p=0.6816**—not the selected-pair −19.60, CI [−39.37,−1.19]. Use all assigned instances as the primary analysis; label revised-only analyses exploratory.

2. **HIGH — The published `p=0.0014` pools dependent, heterogeneous observations.**  
   [report2.py:118](/Users/ericdong/Documents/Crossaudit/crossaudit_integ/benchmarks/expertlongbench/report2.py:118), [RESULTS-3.md:172](/Users/ericdong/Documents/Crossaudit/crossaudit_integ/benchmarks/expertlongbench/RESULTS-3.md:172). Arms S, R, and X change the constitution, auditor context, and revision prompt, yet their selected revision rows are pooled. Arm means are −13.56, +5.83, and −14.42. The 25 observations contain only 18 unique sample IDs; the 17 nonzero Wilcoxon observations contain only 12 unique IDs. The sign enumeration therefore assumes independence that the data do not have.  
   I reproduce the arithmetic exactly: **−11.0074**, SE **2.4654**, script `p=0.001434326`. The point estimate is a configuration-weighted mixture, and the p-value is not valid evidence that revision generally harms. Report arms separately or use source-instance-clustered inference.

3. **HIGH — The code study’s bootstrap CI falsely establishes a sign.**  
   [report.py:54](<SCRATCH/wt-code/benchmarks/code/report.py:54>), [RESULTS.md:183](<SCRATCH/wt-code/benchmarks/code/RESULTS.md:183>). The five `cross+checks − checks` discordances all point one way. Resampling the empirical observations cannot generate a negative effect, so the percentile bootstrap mechanically produces a positive lower bound even though exact McNemar gives `p=0.0625`. The report nevertheless calls the effect “real in sign.”  
   The descriptive **5/56 = +8.9 points** reproduces, but `[1.8%,17.9%]` is anti-conservative at this sparse boundary and cannot establish exclusion of zero. Use a paired-binary interval appropriate to sparse discordances and aligned with the exact test.

4. **HIGH measurement risk — CLEAR silently scores malformed model responses.**  
   [clear.py:275](/Users/ericdong/Documents/Crossaudit/crossaudit_integ/benchmarks/expertlongbench/clear.py:275), [test_clear.py:186](/Users/ericdong/Documents/Crossaudit/crossaudit_integ/benchmarks/expertlongbench/tests/test_clear.py:186). Missing mapper keys, `null`, and empty values are silently converted to semantic `"N/A"`, although the procedure requires the mapper to emit every key and explicitly select N/A. `parse_yes_no()` similarly takes the first yes/no token from a possibly contradictory answer. The tests explicitly bless these normalizations.  
   Either behavior can change item hits and every CLEAR-derived F1. Realized impact cannot be measured because raw mapper/judge replies were not retained in the committed evidence. Require a complete schema and an unambiguous verdict; reject or separately rescore malformed replies.

5. **HIGH — The specified branch is not a publishable evidence bundle.**  
   [EXPERIMENT_RECORD.md:42](/Users/ericdong/Documents/Crossaudit/crossaudit_integ/benchmarks/EXPERIMENT_RECORD.md:42), [.gitignore:1](/Users/ericdong/Documents/Crossaudit/crossaudit_integ/benchmarks/expertlongbench/.gitignore:1). At `fusion/evidence-authority`/`51ba8e5`, `RESULTS-4.md`, `RESULTS-5.md`, and `benchmarks/code/` are absent. Studies 1–3 have no committed per-instance records or study manifests; their evidence remains in ignored run directories in other worktrees. Study 4 claims conformance, while its manifest records `worktree_clean: false`.  
   This does not alter a point estimate, but a clean checkout cannot audit or reproduce most publication results. Consolidate the reports and corpus-safe records on the publication branch and reproduce from a fresh clone.

6. **MEDIUM-HIGH — “n revisions” actually means revised instances, with multi-round changes collapsed.**  
   [run.py:959](/Users/ericdong/Documents/Crossaudit/crossaudit_integ/benchmarks/expertlongbench/run.py:959), [report2.py:94](/Users/ericdong/Documents/Crossaudit/crossaudit_integ/benchmarks/expertlongbench/report2.py:94). `_revision_pair()` stores the number of transitions but `report2.py` ignores it and records one first-to-final delta per revised instance. Intermediate fixes and breakages disappear.  
   Study 2 has **17 revised instances but 23 transitions**; adjacent-transition summaries are −2.52 F1 and 4/8 fixed/broken, versus published −3.40 and 3/7. Study 3 has **25 revised instances but 36 transitions**; adjacent-transition summaries are −7.64 and 5/19, versus −11.01 and 3/17. Choose either net change per revised instance or per-transition change and label/analyze that unit honestly.

7. **MEDIUM-HIGH — Study 5’s 2.6-point noise floor is the wrong estimand.**  
   [premise_report.py:355](<SCRATCH/wt-premise/benchmarks/expertlongbench/premise_report.py:355>), [RESULTS-5.md:22](<SCRATCH/wt-premise/benchmarks/expertlongbench/RESULTS-5.md:22>). The primary outcome is a paired per-instance macro `cross−self` difference. The substitute noise study reruns only `cross` on fixed drafts, computes pooled micro recall, and takes the SD of three means. That is not the variability of the primary contrast or of generation-changing studies.  
   The committed rows reproduce 20.34%, 15.25%, 18.64%, SD 2.59 pp, but using that number to accept or withdraw other findings is invalid. Repeat the full paired contrast and calculate the identical statistic on every replicate.

8. **MEDIUM-HIGH — “No model ever saw the hidden tests” is unsupported.**  
   [manifest_corpus.json:15](<SCRATCH/wt-code/benchmarks/code/manifest_corpus.json:15>), [RESULTS.md:29](<SCRATCH/wt-code/benchmarks/code/RESULTS.md:29>). HumanEval+ and MBPP+ are public datasets predating the evaluated models. Runtime prompt isolation cannot establish absence from pretraining or evaluation tuning; recognizable task specifications may identify the cases.  
   Contamination could affect generation, population selection, or audit recall. Replace the claim with “not present in runtime prompts/tool inputs,” or use private/new hidden tests.

9. **MEDIUM — Four P cases are timeout classifications, not observed assertion failures.**  
   [execute.py:117](<SCRATCH/wt-code/benchmarks/code/execute.py:117>), [evaluate.py:32](<SCRATCH/wt-code/benchmarks/code/evaluate.py:32>). `HumanEval/163`, `Mbpp/267`, `Mbpp/300`, and `Mbpp/765` have `timed_out=true`, binary mode, and no recovered assertion vector. This contradicts the report’s “AssertionError or not” ground-truth description.  
   `cross+checks` missed all four. Separating them pending official-runner adjudication changes recall from **5/56=8.9%** to **5/52=9.6%**. Use the official EvalPlus execution policy or report timeout-only cases separately.

10. **MEDIUM — Study 2’s causal headline compares unequal populations and different drafts.**  
    [RESULTS-2.md:15](/Users/ericdong/Documents/Crossaudit/crossaudit_integ/benchmarks/expertlongbench/RESULTS-2.md:15). The headline compares shipped B’s 4/201 over 40 instances with 10-instance B′/B″ arms, then concludes “It is the constitution” and “A stronger model changed nothing.” On the matched ten, shipped B is 0/52, B″ 2/52, and B′ 9/58. All ten B″ drafts and all ten B′ drafts differ byte-for-byte from shipped B; B′ also changes the generator prompt, as later disclosed. No CI or paired test is supplied for these recall contrasts.  
    The micro rates reproduce, but the causal attribution does not. Re-audit identical frozen drafts under each rules/model condition.

11. **MEDIUM — Promoted effect sizes omit CIs, and Wilcoxon p-values are described as tests of means.**  
    [EXPERIMENT_RECORD.md:61](/Users/ericdong/Documents/Crossaudit/crossaudit_integ/benchmarks/EXPERIMENT_RECORD.md:61), [RESULTS-3.md:136](/Users/ericdong/Documents/Crossaudit/crossaudit_integ/benchmarks/expertlongbench/RESULTS-3.md:136). Study 3’s +2.04 and **+24.07 at n=4** have no CI; −11.01 has SE only. Study 4’s −5.44 row has neither CI nor p. `report2.py` also says Wilcoxon determines whether the arithmetic mean differs from zero, although signed-rank tests a symmetric location/distribution null.  
    I reproduce +24.0741 from four differences: +16.67, 0, +22.22, +57.41. The omission hides extreme uncertainty. Add CIs and align the test with the stated estimand.

12. **LOW current impact — Floating-point equality splits mathematical ties.**  
    [stats.py:31](/Users/ericdong/Documents/Crossaudit/crossaudit_integ/benchmarks/expertlongbench/stats.py:31). Five mathematically identical 1/6-scale differences are stored as four `16.666666666666664` values and one `16.666666666666668`, so exact `==` assigns different ranks. Correctly grouping them changes `p=0.001434326` to `p=0.001388550`; both print as `0.0014`. Use integer/rational score components or canonicalized ties.

13. **LOW-MEDIUM — Item-level Wilson intervals ignore clustering.**  
    [report2.py:176](/Users/ericdong/Documents/Crossaudit/crossaudit_integ/benchmarks/expertlongbench/report2.py:176). Rubric items occur six per draft, recur over rounds, and sometimes repeat the same source instance across arms. Treating these as independent Bernoulli trials gives uncalibrated precision/recall intervals. Point rates are unchanged, but uncertainty can be understated. Bootstrap or otherwise cluster by source instance.

14. **LOW — Study 5 promotes an exploratory mechanism in its opening.**  
    [RESULTS-5.md:14](<SCRATCH/wt-premise/benchmarks/expertlongbench/RESULTS-5.md:14>). The opening declares severity “what the vendor difference did buy” and calls it a mechanism; only at line 169 is it identified as unregistered and exploratory. Counts are unchanged, but claim status is overstated. Label it exploratory in the opening.

Explicit negative checks:

- CLEAR’s full-checklist denominator, precision/recall direction, per-sample harmonic F1, and sample-level aggregation match the described procedure and the [paper](https://arxiv.org/abs/2506.01241). I found no chain-of-thought exposure to the extractor or comparator.
- I found no direct code-study hidden-test leak through prompts, imports, fixtures, caches, or generated solution filesystem behavior.
- The code population reproduces exactly: C=455, P=56, F=29; audit set P=56, C=150, F=29. All reported arm counts and McNemar p-values regenerate from the committed records.
- I did not find a p-value copied from an unrelated comparison.

Verification limitation: the repository has no `.venv`, and system Python lacks `pytest`, so the benchmark unit tests could not run. I did rerun both `report2.py` analyses, the code report, and independent calculations from the Study 4 and Study 5 JSONL records.
