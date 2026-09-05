# Study 6 — the audit-stage noise floor. The aggregate is reproducible to the decimal; almost nothing underneath it is

**The kill condition did not fire.** Four replicates of the shipped cross-vendor audit
over twenty byte-identical drafts gave pooled round-one recalls of **23.5, 19.4, 25.5,
25.5** — a **range of 6.12 points** against the 8.0 preregistered in
`PREREGISTRATION-6.md` §6, SD 2.89, **2 SD = 5.77**. So an *aggregate* recall claim at
n = 20 is interpretable, and study 3's 2.0% → 23.5% is not an artefact of re-running the
same configuration.

**Everything below the aggregate is a different story, and it is the finding.** The same
four runs disagree about individual instances by a mean absolute paired difference of
**14.46 points (95% CI 10.51 – 18.36)**. Only **4 of 20** instances returned the same
recall in all four runs; **11 of 20** moved by more than 20 points and one moved by 60.
Only **2 of 20** produced the same *number of findings* four times. And **6 of 20
instances did not return the same BLOCKED/PASS verdict in all four runs** — on this task,
re-running the identical audit over the identical commit changes whether work is stopped
about **thirty percent of the time**.

> **The sentence this licenses is: the audit's aggregate rate is a measurement, and its
> per-instance output is close to a coin flip on a third of the sample.** Both were being
> reported as if they were the same kind of thing.

**Study 5's 2.59 pp replicates.** Its audit-only floor — three passes over 11 fixed
drafts, SD 2.59 pp, range 5.09 — comes out here as **SD 2.89 pp** over 20 fixed drafts
with four passes, on the same code path. That number was correct and is now better
estimated. `CORRECTIONS.md` item 1 was right that it is the spread of a pooled rate, and
right that it bounds nothing where generation changes; what it did not say is how much
larger the *paired* quantity is, which is the number below.

**No published prose finding is killed by this floor. One is closer to it than its report
suggests**, and the reason no finding dies is worth stating plainly: the surviving
results in this line are large, and they are large because the effects that were not
large were already withdrawn.

**Spend: US$1.945** of a US$2 budget. **Zero generation, zero re-scoring** — the drafts
and their CLEAR verdicts are study 3's, read back from disk.

---

## What this bounds, and what it does not

This is the estimand `CORRECTIONS.md` item 1 says was crossed, measured properly:

- **It bounds** run-to-run variation of the **audit** when the draft and the ground truth
  are held fixed. Every study-5 comparison is of this kind — all its arms judge the same
  bytes — so every study-5 number can be read against it.
- **It does not bound any study in which generation varies.** Study 3's `+2.04 F1`,
  study 2's `2.0% → 3.8%`, study 3's `−6.11 F1` and `−11.01 F1` all regenerate the
  document. Study 5B's generation-inclusive floor (SD 1.84 F1, n = 8) governs those, and
  it has already withdrawn the first two. **Nothing in this report may be used against
  them**, and using it that way would repeat the exact error being corrected.
- **It is a lower bound, not a bound, for study 3's `S → X` recall contrast**, which
  changes the constitution *and* regenerates the drafts. The audit-stage variation
  measured here is one component of that contrast's variance, not all of it.

## What was run

| | |
|---|---|
| task | `T03MaterialSEG` — justify the key decisions in a solid-state synthesis recipe |
| corpus | `T03MaterialSEG.jsonl`, sha256 `0b525eae93aab406…`, 50 rows, CC BY-NC-SA 4.0, not redistributed here |
| material | **study 3's arm-X round-one drafts**, 20 of them, byte-fixed. Nothing generated. |
| ground truth | **study 3's own CLEAR verdicts**, read back. Nothing re-scored. 98 wrong rubric items of 120. |
| auditor | `openai:gpt-5.6-terra`, one arm, **K = 4 replicates** |
| adjudicator | `openai:gpt-5.6-terra` via `adjudicate.py`, unchanged |
| rules | rubric-grade, constitution sha256 `9f1ee353ec4cb05e…` — byte-equal to studies 3 and 5 |
| settings | `max_rounds: 1`, `checks: general`, `lone_model_blocker: block`, N/A policy literal |
| harness | `premise.py --rejudge`, **unchanged** — the code path study 5's audit-only floor was measured with |
| preregistration | `PREREGISTRATION-6.md`, committed `c4fa6c8` **before any model call** |
| environment | CPython 3.13.5, macOS 26.6.2 arm64 |
| records | `study6/*.rows.jsonl` (one row per instance per pass), manifests, `MANIFEST-SHA256.json` |

Nothing the harness controls varied between replicates. The provider layer exposes no
seed and temperature comes from the model's capability card, so what varies is provider
nondeterminism — which is the thing being measured. **The code that places and scores an
audit** — `src/`, `premise.py`, `run.py`, `clear.py`, `adjudicate.py`, `tasks.py`,
`provider.py` — is **byte-identical across all four replicates**, verified by diff between
the first replicate's frozen sha and the last's.

What was held fixed was checked, not asserted:

| held fixed | the check |
|---|---|
| the 20 drafts | sha256 per draft; `run_rejudge` refuses a draft whose digest does not match |
| CLEAR ground truth | not recomputed; the rebuild reproduces study 3's denominator exactly (98 of 120) |
| the constitution | `noise_source.py` aborts if the rubric constitution's digest has moved |
| the corpus | verified against `manifest.json` at every run start |
| the audit prompt | every tree rebuilt twice — see §*The `CONSTITUTION @` stamp* |

## The primary outcome

Round-one recall = *(wrong rubric items some finding named) ÷ (wrong rubric items)*.
Primary mapping is the **adjudicator model**, as preregistered, because that is the
mapping every published prose recall number uses. The deterministic **rule** mapping is
reported beside it.

| replicate | findings | BLOCKER | gated | recall (model) | recall (rule) | item precision |
|---|---:|---:|---:|---:|---:|---:|
| rep 1 | 38 | 38 | 18/20 | 23.5% | 22.4% | 62.9% |
| rep 2 | 36 | 36 | 16/20 | 19.4% | 21.4% | 63.6% |
| rep 3 | 42 | 42 | 18/20 | 25.5% | 25.5% | 65.8% |
| rep 4 | 44 | 44 | 18/20 | 25.5% | 27.6% | 67.5% |

### The four spread statistics, all named before the run

n = 20 instances, K = 4 replicates, 6 pairs. Intervals are 20 000-resample percentile
bootstraps over instances, seed `20260930`.

| statistic | model mapping | rule mapping |
|---|---|---|
| **range** of the aggregate — *the kill statistic* | **6.12 pp** [2.91, 17.71] | **6.12 pp** [3.85, 16.04] |
| SD of the aggregate | 2.89 pp [1.26, 7.75] | 2.81 pp [1.71, 7.09] |
| 2 SD | 5.77 pp | 5.62 pp |
| mean \|paired difference\| of the aggregate | 3.40 pp [1.50, 9.38] | 3.57 pp [2.04, 8.61] |
| **mean \|paired difference\| per instance** | **14.46 pp [10.51, 18.36]** | **14.01 pp [9.56, 18.82]** |

**Derived — the floor for a *signed* paired contrast.** A paired experiment does not
report a mean absolute difference; it reports a signed mean and asks whether it differs
from zero. Each replicate pair is two runs of one configuration, so each pair's signed
mean is exactly such an experiment with a true effect of zero:

| | values (pp) | SD | 2 SD | largest \|signed mean\| |
|---|---|---:|---:|---:|
| model mapping | +4.58, −2.42, −2.75, −7.00, −7.33, −0.33 | **4.44** | **8.88** | 7.33 |
| rule mapping | −1.25, −3.58, −7.08, −2.33, −5.83, −3.50 | **2.17** | **4.35** | 7.08 |

**A null paired contrast at n = 20 returned as much as 7.3 points in this study.** That is
the number to hold against any paired recall difference of similar size.

### The kill condition

> **Preregistered:** KILL fires iff the range of the pooled micro round-one recall across
> replicates, adjudicator mapping, exceeds **8.0 pp**.

**Observed 6.12 pp. It did not fire** — under either mapping.

Two honest qualifications, neither of which changes the verdict:

1. **The interval does not exclude a floor above the threshold.** The bootstrap CI on the
   range is [2.91, 17.71]. The point estimate is what the rule names, and the point
   estimate is 6.12; but a reader should not take 6.12 as precise.
2. **A range is monotone non-decreasing in K**, so it is not comparable across studies
   with different replicate counts. At K = 3 (replicates 1–3) this range was also 6.12 pp
   under the model mapping and 4.08 pp under the rule mapping. Study 5's range of 5.09 pp
   was at K = 3, n = 11. **For cross-study comparison use the SD**, which is what §*Study
   5's 2.59 replicates* does.

## The result the aggregate hides

| | |
|---|---:|
| instances with identical recall in all four runs | **4 / 20** |
| instances that moved more than 20 pp | **11 / 20** |
| instances that moved 40 pp or more | 6 / 20 |
| instances with an identical **finding count** in all four runs | **2 / 20** |
| mean within-instance spread of the finding count | 1.45 findings (max 3) |
| instances whose **gated verdict** was not the same in all four runs | **6 / 20** |

Per instance, recall under the model mapping:

| instance | wrong | rep1 | rep2 | rep3 | rep4 | range |
|---|---:|---:|---:|---:|---:|---:|
| adfm.202002249 | 5 | 40.0 | 0.0 | 60.0 | 20.0 | **60.0** |
| adfm.202209924 | 6 | 33.3 | 0.0 | 33.3 | 33.3 | 33.3 |
| adfm.202309656 | 5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| ange.202112688 | 2 | 50.0 | 0.0 | 50.0 | 50.0 | 50.0 |
| anie.201812472 | 3 | 0.0 | 0.0 | 33.3 | 0.0 | 33.3 |
| anie.202410016 | 5 | 20.0 | 60.0 | 20.0 | 60.0 | 40.0 |
| celc.202200984 | 5 | 40.0 | 0.0 | 40.0 | 40.0 | 40.0 |
| chem.201905217 | 4 | 0.0 | 25.0 | 0.0 | 25.0 | 25.0 |
| chem.202302565 | 5 | 20.0 | 40.0 | 20.0 | 40.0 | 20.0 |
| cjce.24030 | 5 | 0.0 | 0.0 | 20.0 | 20.0 | 20.0 |
| cnma.202200403 | 6 | 16.7 | 33.3 | 33.3 | 16.7 | 16.7 |
| cssc.201000245 | 5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| cssc.202300809 | 6 | 33.3 | 0.0 | 16.7 | 0.0 | 33.3 |
| ijch.201400157 | 5 | 40.0 | 60.0 | 80.0 | 60.0 | 40.0 |
| pssb.201900312 | 5 | 20.0 | 40.0 | 0.0 | 20.0 | 40.0 |
| smll.201800441 | 6 | 33.3 | 16.7 | 33.3 | 16.7 | 16.7 |
| smll.202408072 | 5 | 40.0 | 20.0 | 20.0 | 40.0 | 20.0 |
| zaac.201800357 | 6 | 16.7 | 16.7 | 16.7 | 16.7 | 0.0 |
| zaac.202200095 | 5 | 20.0 | 20.0 | 20.0 | 20.0 | 0.0 |
| sciadv.adp3309 | 4 | 50.0 | 50.0 | 25.0 | 50.0 | 25.0 |

**What this closes.** `RESULTS-GATE.md` already reported that no runtime-visible signal is
established as a predictor of a harmful revision, its best candidate being the **number of
findings** at AUC 0.737 with a clustered interval reaching 0.510 — a lower bound at chance.
This study supplies the mechanism rather than a contradiction: **the predictor variable
itself is not reproducible.** Its within-instance re-run spread is 1.45 findings against a
between-instance range of 0–5, and only 2 of 20 instances give the same count twice, let
alone four times. A per-instance predictor cannot be built on it, and the gate study's
negative conclusion should be read as settled rather than merely unproven.

## Study 5's 2.59 pp replicates

| | study 5, first execution | **study 6** |
|---|---|---|
| material | 11 fixed drafts | **20 fixed drafts** |
| passes | 3 | **4** |
| code path | `premise.py --rejudge` | the same, unchanged |
| pooled recalls | 20.3, 15.3, 18.6 | 23.5, 19.4, 25.5, 25.5 |
| **SD** | **2.59 pp** | **2.89 pp** [1.26, 7.75] |

Same estimand, same machinery, a nearly identical answer at nearly twice the n. The 2.59
figure was a real measurement of a real quantity. What was wrong was only what it was used
*for*, which `CORRECTIONS.md` item 1 has already recorded.

## Two things about the adjudicator, and a correction to my own interim reading

**The model mapper agreed with the deterministic one on 130 of 130 findings it managed to
map. Zero disagreements, across four replicates.** On this constitution, `CA-RUBRIC-00N`
*is* rubric item N by construction, and the adjudicator model never found anything the
rule already encoded. It adds no information here — only cost, latency, and failure modes.

It does add failure modes. Its calls were rate-limited hard, and a failed call leaves its
finding citing no item, which depresses the model mapping and cannot touch the rule
mapping: **16 of 160 findings** went unmapped (2, 7, 2, 5 by replicate).

**Correction to an interim reading of my own.** At K = 3 I recorded that imputing the
deterministic mapping for exactly those failed calls cut the range from 6.12 pp to
3.06 pp, and wrote that half the spread in the primary was adjudicator unavailability
rather than the auditor. **The fourth replicate falsified that.** Imputed, the four
replicates read 24.49 / 23.47 / 26.53 / **29.59** — a range of **6.12 pp, identical to the
raw figure**. The K = 3 impression was an accident of which three replicates were in hand.
It is recorded here rather than quietly dropped, because it is exactly the shape of error
this report exists to measure: a three-point pattern that did not survive a fourth point.

## Severity: 160 findings, 160 BLOCKER, zero ADVISORY

Study 5 reported that `cross` had never, in 48 findings over 30 instances, filed an
advisory. Over **160 findings in four replicates** here, it still has not. That is an
independent reproduction of study 5's severity result at more than three times the
findings, and it is the single most stable thing this study measured.

It also means blocking recall and total recall are the same number in this configuration,
so the floor below applies to both.

## Which published claims this floor licenses, and which it does not reach

Floors are scaled between sample sizes by √(20/n); the relevant floor is the one matching
the claim's estimand.

| claim | delta | the right floor here | verdict |
|---|---|---|---|
| Study 3: auditor recall 2.0% → 23.5% (n = 20) | +21.5 pp | 2 SD 5.77 pp — *lower bound only*, generation also differs | **survives** |
| Study 5: `cross` − `self` recall, adjudicator (n = 30) | −11.8 pp | signed paired contrast, 2 SD **7.25 pp** | **survives** |
| Study 5: `cross` − `self` recall, rule (n = 30) | −13.6 pp | 2 SD **3.55 pp** | **survives comfortably** |
| Study 5: `cross` − `sibling`, adjudicator (n = 30) | +9.3 pp | 2 SD **7.25 pp** | survives — **by 28%; the fragile one** |
| Study 5: `cross` − `sibling`, rule (n = 30) | +8.7 pp | 2 SD 3.55 pp | survives |
| Study 5: `sibling` − `self`, rule (n = 30) | −22.2 pp | 2 SD 3.55 pp | **survives outright** |
| Study 5: gate rate `cross` − `self` (n = 30) | +76.7 pp | paired binary, 2 SD **12.29 pp** | **survives outright** |
| Study 5: blocking recall `cross` − `self` (n = 30) | +18.5 pp | 2 SD 7.25 pp (all findings are BLOCKER) | **survives** |
| Study 3: item precision 100% → 73% | −27 pp | 2 SD 4.21 pp | survives (its 100% still rests on 2 observations) |
| Study 5: item precision `cross` 72.5% vs `self` 82.0% | −9.5 pp | 2 SD 3.44 pp, *unpaired pooled rates* | survives, **approximately** |
| Study 3: round-one draft +2.04 F1 | — | **not bounded here** — generation varies | already withdrawn against study 5B's 1.84 F1 |
| Study 2: recall 2.0% → 3.8% | — | **not bounded here** | already withdrawn |
| Study 3: final output −6.11 F1; revision −11.01 F1 | — | **not bounded here** — generation and revision vary | untouched by this study |

**The single most important sentence for a reader of this project:** *no previously
published prose finding becomes indistinguishable from run-to-run variation under this
floor.* Study 5's primary outcome, which its own report called its weakest result and
cleared only after a scaling assumption, clears this better-measured floor by a comfortable
margin under the deterministic mapping (−13.6 against 3.55) and by 63% under the
adjudicator mapping (−11.8 against 7.25). **The one number that should now carry a caution
is study 5's `cross` − `sibling` = +9.3 pp**, which exceeds its floor by 28% — inside a
factor the wide interval on that floor ([1.26, 7.75] on the SD) cannot rule out. It was
not in study 5's licence list, and it should not enter one.

**What the floor does kill is a class of claim rather than a specific number:** anything
resting on *which* instances the auditor catches, on how many findings it raises on a given
document, or on whether a given commit is blocked. Those are not reproducible here.

## An exploratory observation that K = 4 cannot settle

Rule-mapping recall across replicates, in run order, is **22.4 → 21.4 → 25.5 → 27.6**, and
findings totals are **38 → 36 → 42 → 44**. Replicates 3 and 4 ran later than 1 and 2. This
is consistent with a run-level drift — provider load, a silently updated build — and also
perfectly consistent with noise at K = 4. **No pairwise Wilcoxon approaches significance**
(smallest p = 0.078, `rep2` vs `rep4`, 8 usable pairs). Study 5's Deviation 10 said three
replicates could not separate run-level shift from per-instance noise; **four cannot
either**, and the monotone ordering is a reason to prefer the upper end of the intervals
above rather than the point estimates. This is labelled exploratory and was not
preregistered.

## The `CONSTITUTION @ <commit>` stamp — a finding that will fire in every future replay

`prompt.build` stamps the commit that versioned the rules into the audit prompt, so an
audit can cite the standard it applied. **A git commit id is a function of the tree *and*
the commit timestamp.** Rebuilding the same tree a second later yields the same rules, the
same recipe, the same draft, the same deterministic check results — and a different prompt
digest.

So `run_rejudge`'s `prompt_digest_matches_source` reported a mismatch on **every instance
of every replicate**, and it means nothing. Rather than assert that, it was measured: each
of the 20 trees was rebuilt twice and the prompts diffed.

- **At most one line of 94–150 differed**, and it is `CONSTITUTION @ <sha>`.
- Under normalisation of that one line the prompts are **byte-identical on all 20**.

`study6/source-digests.json` carries `audit_prompt_sha256_normalised` and
`audit_prompt_lines_differing_on_rebuild` per instance. **Any future replay harness should
compare the normalised digest**; the raw one cannot succeed across processes.

## Is the replay faithful?

Study 3's arm-X round-one audit ran inside the live build loop; this study replays it
through `premise.py --rejudge`. If the two disagreed, a spread measured with the second
would be a property of the harness.

| | study 3, arm X, round 1 | study 6, replicate 1 |
|---|---|---|
| pooled round-one recall | **23/98 = 23.5%** | **23/98 = 23.5%** |
| findings | 37 | 38 |
| rules cited | `CA-CONTENT-001`, `CA-RUBRIC-001/003/004/005/006` | the same six |

`max_rounds` differs (3 there, 1 here) and does not enter the audit prompt; `TASK.md` is
absent in both, so the auditor's task text is empty in both. Full comparison at
`study6/fidelity-check.json`.

**And the same table carries this study's headline in miniature:** only 8 of 20 instances
produced the same number of findings. The published aggregate reproduced exactly; the
behaviour beneath it did not.

Study 3's arm-X round-one audit is therefore usable as an **observational fifth
observation** of the aggregate — 23.5%, sitting inside the four replicates' 19.4–25.5
range. It is *not* folded into K, because it ran through a different harness.

## Analysis, stated so it can be checked

- **Unit of independence** is the instance; every bootstrap resamples instances, 20 000
  percentile resamples, seed `20260930`, so each interval is a deterministic function of
  the committed rows.
- **Tests:** exact two-sided Wilcoxon signed-rank on paired per-instance differences,
  ties dropped, exact by enumeration at ≤ 20 usable pairs. All six pairwise tests are
  reported in `study6/analysis.txt`; none is significant, which is what a set of
  replicates of one configuration *should* look like.
- **n per cell:** 20 seeded, **20 analysed in every replicate**. No cell shrank; the
  preregistered exclusion rule for an incomplete replicate never had to be applied.
- **Comparisons:** the primary is a spread, not a test, and carries no p value. Six
  pairwise Wilcoxons are secondary and their count is stated. This is the **seventh study
  on `T03MaterialSEG` and the same 50 rows**; that is the multiple-comparison picture.
- **K = 4 is a poor estimator of a standard deviation.** The interval on an SD from four
  points is wide — [1.26, 7.75] — which is why the range is the kill statistic, why every
  figure carries an interval, and why the drift observation above is not dismissed.

## Deviations, numbered and complete

1. **`--only-unreached-in` was added to `noise_source.py` after replicate 1 had begun.**
   Replicate 1 lost 3 of 20 audits to `[SSL: UNEXPECTED_EOF_WHILE_READING]` through the
   machine's HTTP proxy — the same environmental failure studies 3 and 5 recorded. The
   flag restricts a source to instances whose audit call **never reached a provider**, so
   they can be retried. **Bias: none available.** An instance qualifies only when `ok` is
   false, meaning no model answered and there is no outcome to have selected on; an
   auditor that replied — with findings, with none, or with a reply the validator
   rejected — is never re-asked. Retries used: rep 1 two passes (3 then 1), rep 2 one pass
   (3), rep 3 one pass (2), rep 4 two passes (4, then the same 4 again). **12 audit calls
   in total were retried; all four replicates finished at 20/20.**
2. **`prompt_digest_matches_source` was false on all 80 instance-replicates.** Fully
   explained by the `CONSTITUTION @` stamp above, with the diff evidence committed. No
   instance was excluded for it.
3. **16 of 160 findings were never mapped by the adjudicator** (2, 7, 2, 5 by replicate),
   its calls having been rate-limited to exhaustion. **Bias: downward, on the model
   mapping only.** Quantified by imputation above; the rule mapping is unaffected.
4. **Heavy provider rate-limiting throughout.** `premise.retrying` waited out shared quota
   windows (45/120/300/600 s). It changes how long a number takes to obtain, not what the
   number is: a model that answered is never asked again.
5. **Three run directories recorded `tree_clean: false`.** The uncommitted paths were
   `study6/run-replicate.sh` (the driver, unchanged from creation and committed at
   `9b9c9c3`) and, for replicate 4, collected record files. **No replicate executes
   either.** The manifests record exactly which paths. Replicate 1 ran on a clean tree at
   the preregistration commit `c4fa6c8`.
6. **The measurement code did not move between replicates, and this was verified**:
   `git diff` over `src/`, `premise.py`, `run.py`, `clear.py`, `adjudicate.py`, `tasks.py`
   and `provider.py` between the first replicate's sha and the last's is empty. Only
   `noise_source.py` (source construction, retry restriction, digest evidence) and
   `noise_report.py` (analysis, no model calls) changed.
7. **The source directory was rebuilt once**, after replicate 1, when the prompt-stability
   check was added. **Draft digests are identical before and after**; replicate 1 used the
   pre-rebuild source and judged the same bytes.
8. **The corpus was copied into this worktree's gitignored `data/`** from another
   worktree rather than re-downloaded. Its sha256 is verified against `manifest.json` at
   every run start, and matches study 3's `corpus_sha256`.
9. **An interim K = 3 reading was published to the coordinator and is corrected here.**
   See §*Two things about the adjudicator*. It claimed imputation halved the primary's
   range; the fourth replicate showed it does not.
10. **The drift observation is exploratory** and was not preregistered.
11. **K = 4 was reached, not cut.** The preregistered stopping rule was four replicates or
    US$2.00, whichever came first; spend at the start of replicate 4 was US$1.466 with a
    measured per-replicate cost near US$0.47, so the rule permitted it. Final spend
    US$1.945.

## Limitations

- **The CLEAR scorer is a reimplementation from the paper.** The authors released no
  evaluation code and it has never been diffed against theirs. Every number here inherits
  that, including the 98 wrong items that are this study's denominator.
- **A model-judged ground truth is not ground truth.** "Wrong" means
  `openai:gpt-5.6-terra` judged a draft and the human reference not mutually contained on
  a rubric item — and the same vendor's model supplied the auditor being measured.
- **One task, one corpus, one vendor pair, one auditor model, one constitution.** Seventh
  study on `T03MaterialSEG` and the same 50 rows. The floor is `anthropic → openai` under
  rubric-grade rules. **The shipped general constitution is not measured**, and under it
  the auditor is near-silent (2.0%) — a near-silent auditor has little room to vary, so
  this floor should not be transported to it.
- **Round one only.** Nothing here covers revision rounds, and study 3's revision numbers
  remain unbounded by any measured floor.
- **A floor is not a model of the noise.** Four points cannot distinguish per-instance
  noise from a run-level shift, and the monotone ordering above is a live alternative.

## Cost

From the product's own usage ledger, via each row's recorded event and each run's `_host`
adjudication ledger.

| | |
|---|---:|
| audit calls (80 auditor turns) | $1.7640 |
| adjudication | $0.1810 |
| **total** | **$1.9450** |
| per replicate | ≈ $0.47 |

Generation: **$0.00**. CLEAR scoring: **$0.00**. Both were read back from study 3, which is
what made four replicates affordable at all.

## Reproduction

Requires `CROSSAUDIT_OPENAI_KEY` and `CROSSAUDIT_ANTHROPIC_KEY` (or the role-named
fallbacks in `~/.crossaudit-keys.env`), and study 3's arm-X run directory.

```sh
git checkout <the sha carrying this file>
export PYTHONPATH="$(git rev-parse --show-toplevel)/src"
export https_proxy=http://127.0.0.1:7897     # if your network needs it
python benchmarks/expertlongbench/fetch.py --tasks T03MaterialSEG   # CC BY-NC-SA 4.0,
                                             # not redistributed by this repository
R="$PWD/benchmarks/expertlongbench/runs"

# present study 3's archived arm-X drafts to premise.py --rejudge
python benchmarks/expertlongbench/noise_source.py \
    --archive ~/Documents/Crossaudit/study-data/wt-split-runs/armX-split \
    --out "$R/study6-source" \
    --digest-table benchmarks/expertlongbench/study6/source-digests.json

# four replicates of the identical configuration, each with bounded retries of any
# audit call that never reached a provider
for k in 1 2 3 4; do
  sh benchmarks/expertlongbench/study6/run-replicate.sh noise-rep$k 3
done

python benchmarks/expertlongbench/study6/collect.py --runs "$R" \
    --replicate noise-rep1 --replicate noise-rep2 \
    --replicate noise-rep3 --replicate noise-rep4
python benchmarks/expertlongbench/noise_report.py \
    --replicate rep1="$R/noise-rep1,$R/noise-rep1-fill1,$R/noise-rep1-fill2" \
    --replicate rep2="$R/noise-rep2,$R/noise-rep2-fill1" \
    --replicate rep3="$R/noise-rep3,$R/noise-rep3-fill1" \
    --replicate rep4="$R/noise-rep4,$R/noise-rep4-fill1,$R/noise-rep4-fill2" \
    --ledger-cost 1.94499
```

### Reproducing the analysis without keys, the corpus, or the run directories

Every number in this report is arithmetic over the committed rows, and
`noise_report.py` accepts those files directly:

```sh
S=benchmarks/expertlongbench/study6
python benchmarks/expertlongbench/noise_report.py \
    --replicate rep1=$S/noise-rep1.rows.jsonl,$S/noise-rep1-fill1.rows.jsonl,$S/noise-rep1-fill2.rows.jsonl \
    --replicate rep2=$S/noise-rep2.rows.jsonl,$S/noise-rep2-fill1.rows.jsonl \
    --replicate rep3=$S/noise-rep3.rows.jsonl,$S/noise-rep3-fill1.rows.jsonl \
    --replicate rep4=$S/noise-rep4.rows.jsonl,$S/noise-rep4-fill1.rows.jsonl,$S/noise-rep4-fill2.rows.jsonl \
    --ledger-cost 1.94499
```

This was checked, not assumed: the command above reproduces
`study6/analysis.txt` exactly.

`--out` must be absolute. **It will not reproduce byte-identically, and that is the
measurement**: the provider layer exposes no seed and temperature comes from the model's
capability card. The analysis, however, is deterministic given the committed rows —
`noise_report.py` makes no model call, so anyone with `study6/*.rows.jsonl` can reproduce
every number in this report without keys, without the corpus, and without the run
directories.

**Do not re-run this study hoping for a smaller floor.** If the configuration changes, the
study restarts and says so here.
