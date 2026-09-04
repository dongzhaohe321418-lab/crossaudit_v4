# Study 5 — the premise. Cross-vendor auditing did not name more defects than the model that wrote them

**The different-vendor auditor named *fewer* of the draft's real defects than the
generator judging its own work: 22.3% against 32.7%, a paired difference of −10.3
percentage points (95% CI −25.3 to +5.0, exact Wilcoxon p = 0.28, n = 10 paired
instances).** It was worse on 5 instances, better on 1, tied on 4. Under the
deterministic finding-to-item mapping the gap widens to −14.0 pp (CI −28.0 to −1.0,
p = 0.16). The heterogeneity invariant is the thing this product refuses to run without,
and on this task, at this n, **it did not buy the recall the README says it buys.**

This is the preregistered primary outcome and it came out against the product. Per the
study's own rule it stands as measured and is not re-run until it flips.

**What the vendor difference did buy is a different thing entirely: the willingness to
block.** The cross-vendor auditor filed **all 18** of its findings as BLOCKER and gated
8 of 11 increments. The same-vendor auditor raised *more* findings — 24 — and filed
**18 of them as ADVISORY**, gating only 2 of 11. The same-vendor sibling did the same:
2 of 11. The generator's own vendor sees the problems and calls them suggestions;
the stranger sees fewer and calls them defects. On this evidence the invariant is not a
recall mechanism. It is a **severity** mechanism, and it has been sold as the former.

**The noise floor, measured for the first time in this project: 2.6 pp.** Three runs of
the identical cross-vendor configuration over the identical 11 drafts gave recalls of
20.3%, 15.3% and 18.6% — SD 2.59 pp, range 5.1 pp. Read against it, study 2's headline
that *"a stronger auditor model moved recall from 2.0% to 3.8%"* is **inside the noise
and is not a finding**. Study 3's 2.0% → 23.5% survives it comfortably. Which of this
project's other numbers survive is set out below, and several cannot be judged at all
because the floor measured here covers the auditor and not the generator.

**The study is incomplete.** Both vendors' API credit ran out during the run: 5 of 16
instances have no draft, the preregistered three-replicate noise floor could not be run
as designed, and what is reported instead is a narrower substitute obtained after the
primary scores were read. Every one of those is a numbered deviation below. Spend:
**US$2.40** recorded, about **US$4.00** including discarded trial runs, of a US$20
two-study budget. The budget was not the binding constraint; the credit balance was.

---

## What was run

Preregistration: **`PREREGISTRATION-5.md`**, committed at `9656cbf` before any model was
called under that sha. Provenance, per-instance raw records and directory digests:
**`study5/`**. The full run directories stay gitignored and their absolute paths and
sha256 are in `study5/MANIFEST-SHA256.json`.

| | |
|---|---|
| task | `T03MaterialSEG` — justify the key decisions in a solid-state synthesis recipe |
| corpus | `T03MaterialSEG.jsonl`, sha256 `0b525eae93aab406…`, 50 rows, CC BY-NC-SA 4.0, not redistributed here |
| sample | 16 of 50, seed `20261104`, sorted by id → sampled → re-sorted |
| generator | `anthropic:claude-sonnet-4-6` (every arm, one draft per instance) |
| CLEAR mapper / judge / adjudicator | `openai:gpt-5.6-terra` |
| rules | **rubric-grade**, constitution sha256 `9f1ee353ec4cb05e…` — the same file study 3 used |
| settings | `max_rounds: 1`, `checks: general`, `authority.lone_model_blocker: block`, N/A policy literal |
| code | frozen at **`9656cbf`**, `git status --porcelain` empty at freeze |
| environment | CPython 3.13.5, Darwin 25.6.0 arm64 |

One generator writes **one** draft per instance through the product's real
`crossaudit.cli.build.run_loop`, in a fresh git project with a real `crossaudit.yml` and
the recipe committed inside the audited scope. That one committed draft is then judged
four ways.

The drafts are poor, which is what makes the auditors' job measurable at all: mean CLEAR
F1 **14.2**, accuracy 10.6, and **59 of 66 rubric items scored wrong** across the 11
analysed instances. An arm that named everything wrong would score 100% recall on a
denominator of 59; the best arm named 19.

| arm | who judges | vendor vs. generator |
|---|---|---|
| `cross` | `openai:gpt-5.6-terra` — the shipped configuration | **different** |
| `self` | `anthropic:claude-sonnet-4-6` — the generator itself | same vendor, same weights |
| `sibling` | `anthropic:claude-opus-4-8` | same vendor, different model |
| `none` | nothing | — |

### The arms really are judging the same thing

Held fixed: the draft bytes, the committed tree, the constitution and its commit, the
deterministic-check output, the audit prompt, the system message, the reply parser and
rule validator, the CLEAR ground truth, the adjudicator. Varying: which model receives
the prompt.

This is checked, not asserted. For **every one of the 11 judged instances the harness's
audit prompt digest equalled the digest the product's own audit recorded for the same
commit** — e.g. `8cb14fe22745da86`, `f3347ade1832cc9a`, `76f92d9fffba015d`. The three
arms then received those identical bytes. Had any digest differed the study would be
void; none did.

### The heterogeneity bypass, and where it lives

`self` and `sibling` cannot exist while `config.heterogeneity` runs, and the guard sits
inside `crossaudit.auditor.run.run_audit`. **`src/` was not modified.** `premise.py` does
not call `run_audit`; it calls the same product functions `run_audit` calls —
`_materialise_tree_scope`, `_committed_constitution`, `_committed_task`, `run_checks`,
`prompt.build`, `resilience.complete`, `parse_reply`, `validate_reply` — in the same
order, and skips the one guard. The product still refuses a same-vendor pair everywhere
a user can reach it. The prompt-digest equality above is what makes that substitution
checkable rather than a claim.

### Rubric-grade rules, said out loud

The constitution is generated from the task's own rubric, **not** the shipped general
one. Under the general rules the auditor is near-silent — 2.0% recall in studies 2 and 3
— and all four arms would have looked identical **because none of them would have said
anything**, which would be a null result about the constitution wearing the costume of a
null result about vendors. This is a deliberate departure from the shipped default. Every
number here is therefore about a configuration a user would have to opt into.

---

## The primary outcome

Recall for an arm on an instance is *(rubric items CLEAR scored wrong that some finding
of that arm named) ÷ (rubric items CLEAR scored wrong in that draft)*. The effect is the
mean paired difference in percentage points; the interval is a 20 000-resample percentile
bootstrap over instances; the p is an exact two-sided Wilcoxon signed-rank with ties
dropped as the test requires.

| comparison | mapping | n | A | B | **effect** | 95% CI | b/w/t | exact p | pairs used |
|---|---|---:|---:|---:|---:|---|---|---:|---:|
| **`cross` − `self`** | adjudicator | **10** | 22.3% | 32.7% | **−10.3 pp** | −25.3, +5.0 | 1/5/4 | **0.2812** | 6 |
| `cross` − `self` | rule | 10 | 22.3% | 36.3% | −14.0 pp | −28.0, −1.0 | 1/5/4 | 0.1562 | 6 |
| `cross` − `sibling` | adjudicator | 10 | 22.3% | 13.7% | +8.7 pp | +0.0, +17.0 | 5/1/4 | 0.1562 | 6 |
| `cross` − `sibling` | rule | 10 | 22.3% | 13.7% | +8.7 pp | +0.0, +17.0 | 5/1/4 | 0.1562 | 6 |
| `sibling` − `self` | adjudicator | 10 | 13.7% | 32.7% | −19.0 pp | −32.0, −5.7 | 1/7/2 | 0.0625 | 8 |
| `sibling` − `self` | rule | 10 | 13.7% | 36.3% | **−22.7 pp** | −33.7, −13.3 | 0/8/2 | **0.0078** | 8 |

The row in bold at the top is the one named in advance. **It is negative.** Its interval
crosses zero under the adjudicator mapping and does not under the deterministic one, and
neither p clears any conventional threshold at n = 10 — this study is not powered to call
a 10-point difference significant, and it is not claimed to be. What can be said is that
the difference is **larger than the run-to-run noise floor measured below (2.6 pp)** and
points the wrong way for the product.

The comparison that *is* significant is not about vendors at all: **`sibling` − `self`,
−22.7 pp, p = 0.0078.** Two models from the *same* vendor differ from each other by more
than either differs from the other vendor. Whatever governs recall here, it is not the
vendor boundary.

### Pooled over items

Micro-averaged over all 11 instances, deterministic rule mapping, with Wilson intervals:

| arm | recall | item precision | fired | **gated** |
|---|---|---|---|---|
| `cross` | 20.3% (12/59) [12, 32] | 75.0% (12/16) [51, 90] | 8/11 [43, 90] | **8/11 (72.7%)** |
| `self` | **35.2%** (19/54) [24, 49] | 79.2% (19/24) [60, 91] | 10/11 [62, 98] | **2/11 (18.2%)** |
| `sibling` | 11.1% (6/54) [5, 22] | 75.0% (6/8) [41, 93] | 6/11 [28, 79] | 2/11 (18.2%) |
| `none` | 0.0% (0/59) [0, 6] | n/a | 0/11 [0, 26] | 0/11 |

Denominators differ by arm because one instance's `self` and `sibling` calls died on a
provider outage (Deviation 5); `cross` keeps 59 wrong items, the two Anthropic arms 54.
No reply was rejected by the rule validator in any arm — 0 invalid of 11, in all three —
so the arms' recalls are comparable in the way the preregistration required.

**Precision did not collapse.** 75%, 79%, 75%: the three arms are indistinguishable, and
all three sit near study 3's 73%. Whatever differs between vendors, it is not the rate at
which an objection is about something that was actually wrong.

---

## The mechanism: severity, not sight

| arm | findings | BLOCKER | ADVISORY | verdicts | rules cited |
|---|---:|---:|---:|---|---|
| `cross` | 18 | **18** | **0** | BLOCKED 8, PASS 3 | `CA-RUBRIC-*` ×16, `CA-CONTENT-*` ×2 |
| `self` | 24 | 6 | **18** | PASS 8, BLOCKED 2 | `CA-RUBRIC-*` ×24 |
| `sibling` | 9 | 4 | 5 | PASS 8, BLOCKED 2 | `CA-RUBRIC-*` ×8, `CA-CONTENT-*` ×1 |

This is the study's clearest result and it was **not** preregistered, so it is
**exploratory** and is stated as a hypothesis for a future study rather than a finding:

> The cross-vendor auditor did not notice more. It objected harder. Every single one of
> its 18 findings was a BLOCKER. The generator's own model noticed *more* — 24 findings,
> 19 of which hit items CLEAR had scored wrong — and filed three quarters of them as
> advice that gates nothing and returns nothing to the writer.

Both same-vendor arms gate at exactly 18.2% and the cross-vendor arm at 72.7%, a 54.5 pp
difference against a gating noise floor of 10.5 pp (below). The two Anthropic models agree
with each other on severity while disagreeing sharply on recall — which is what a
*vendor-level* disposition looks like, as opposed to a model-level one.

Restricting recall to BLOCKER findings only — the findings that actually stop an
increment — reverses the headline (also exploratory, also not preregistered):

| comparison | mapping | n | A | B | effect | 95% CI | exact p |
|---|---|---:|---:|---:|---:|---|---:|
| `cross` − `self` | BLOCKER, rule | 10 | 22.3% | 9.0% | +13.3 pp | −2.0, +26.3 | 0.2344 |
| `cross` − `sibling` | BLOCKER, rule | 10 | 22.3% | 3.7% | +18.7 pp | +8.3, +30.0 | 0.0312 |

So the honest two-sentence summary of this study is: **a same-vendor auditor names more
of what is wrong; a cross-vendor auditor is far more likely to stop the work over it.**
Which of those a person wants depends on whether the loop's revision step helps — and
study 3 measured that it does not, at −11.0 F1 per revision, p = 0.0014. Read together,
the two studies say the shipped configuration blocks four times as often as a same-vendor
one, feeding a revision path already measured as harmful. That is a claim about two
studies joined at their edges, not a measurement, and it is flagged as such.

---

## The noise floor

**This is not the preregistered study B, which could not be run** (Deviation 3). It is
what was still obtainable after the generator's vendor ran out of credit, it was built
**after** the primary scores were read, and it is therefore **exploratory**.

The `cross` arm judged **the same 11 drafts three times**: once during study A, then
twice more via `--rejudge`, which rebuilds each instance's tree from its saved draft and
reuses the stored CLEAR ground truth. Nothing was regenerated and nothing was re-scored.

Prompt equality across the three passes was checked and is *almost* exact. The audit
prompt embeds `CONSTITUTION @ <40-hex commit>`, and a rebuilt project cannot reproduce
the original commit id, so raw digests differ. With the 40-hex ids blanked, **all 11
rebuilds are byte-identical** (11/11 commit-normalised digests equal across two
independent rebuilds; 9/11 raw digests equal, the two exceptions being rebuilds that
crossed a one-second boundary). The three passes therefore saw prompts differing only in
a commit id the auditor is not asked about.

| quantity (cross arm, n = 11 instances each pass) | study A | pass 2 | pass 3 | mean | **SD** | range |
|---|---:|---:|---:|---:|---:|---:|
| recall, rule mapping (%) | 20.3 | 15.3 | 18.6 | 18.1 | **2.59** | 5.1 |
| recall, adjudicator mapping (%) | 20.3 | 15.3 | 18.6 | 18.1 | **2.59** | 5.1 |
| item precision (%) | 75.0 | 69.2 | 73.3 | 72.5 | **2.97** | 5.8 |
| fired (% of instances) | 72.7 | 54.5 | 54.5 | 60.6 | **10.50** | 18.2 |
| gated (% of instances) | 72.7 | 54.5 | 54.5 | 60.6 | **10.50** | 18.2 |
| findings per instance | 1.64 | 1.55 | 1.55 | 1.58 | 0.09 | 0.18 |

Two further descriptions of the same instability: the mean Jaccard overlap of the item
sets the three passes named is **0.75**, and **8 of 11** instances had all three passes
name exactly the same items. So the auditor is fairly stable about *what* it names and
much less stable about *whether it speaks at all* — the firing rate moved 18 pp across
identical runs.

### Which earlier findings survive this floor

Recall differences are read against SD ≈ 2.6 pp; firing/gating differences against
SD ≈ 10.5 pp. Anything resting on a **draft or final-output F1** cannot be read against
this floor at all, because it measures the auditor with the draft held fixed and says
nothing about generation variance.

| earlier claim | delta | vs. floor | verdict |
|---|---|---|---|
| Study 3: auditor recall 2.0% → 23.5% (split rules) | +21.5 pp | 8× SD | **survives** |
| Study 2: recall 2.0% → **3.8%** with a stronger auditor model | +1.8 pp | **0.7× SD** | **does not survive — inside the noise** |
| Study 3: audit fires on 5/20 → 16/20 instances | +55 pp | 5× SD | **survives** |
| Study 3: precision 100% → 73% | −27 pp | 9× SD | survives, though its 100% rested on 2 observations |
| This study: `cross` − `self` recall | −10.3 pp | 4× SD | larger than noise; still not significant at n = 10 |
| This study: gating 72.7% vs 18.2% | +54.5 pp | 5× SD | **survives** |
| Study 3: round-one draft +2.04 F1 (p = 0.54) | +2.0 F1 | **not measurable here** | **unjudgeable** — needs a generation-side floor |
| Study 3: final output −6.11 F1 (p = 0.15) | −6.1 F1 | **not measurable here** | **unjudgeable** |
| Study 3: revision −11.01 F1 (p = 0.0014) | −11.0 F1 | **not measurable here** | **unjudgeable** |
| Study 3: split alone +24.07 F1 on n = 4 | +24.1 F1 | **not measurable here** | **unjudgeable** |

The single most useful sentence in this report may be that last block. **Four of this
project's published F1 deltas, including two it has leaned on, still have no noise floor
under them**, and the one measured here does not reach them. A generation-side floor —
three full re-runs including generation — is the obvious next study and it was the one
the credit balance took away.

---

## Analysis, stated so it can be checked

- **Test.** Two-sided Wilcoxon signed-rank on paired per-instance recall differences,
  exact by enumeration (n ≤ 20), exact zero differences dropped as the test requires; the
  number of pairs surviving that drop is in the "pairs used" column and is as low as 6.
  Paired because every arm judges the same draft — the strongest form of pairing
  available, and the reason this design is worth its cost at small n. Non-parametric
  because recall on a 6-item rubric takes seven discrete values and piles up on zero.
- **Effect size and interval.** Mean paired difference, with a 20 000-resample percentile
  bootstrap over instances, seeded (`20261104`) so the interval is a deterministic
  function of the committed rows. Rates carry Wilson intervals, chosen over Wald because
  these denominators are small enough for Wald to run past 0 and 1.
- **n per cell.** 16 seeded → 11 with a draft → **10 paired** for every comparison
  involving an Anthropic arm (one instance lost both Anthropic arms to an outage). The
  noise floor is 3 passes × 11 instances. Cells that shrank are named in the deviations.
- **Comparisons made.** **7 preregistered** (six paired recall tests plus the noise
  floor). **4 exploratory**, added after the scores were read and labelled as such
  everywhere: the two BLOCKER-restricted comparisons, the severity/gating analysis, and
  the substitute noise floor itself. No correction for multiplicity is applied; with the
  primary outcome negative and the exploratory findings offered as hypotheses rather than
  results, a correction would not change any conclusion drawn here.
- **This is the fifth study over the same task and the same 50 rows.** Studies 1–5 have
  drawn overlapping samples from one 50-row corpus and asked related questions of it. The
  multiple-comparison picture is therefore wider than any single study's count, and no
  number in this series should be read as if it came from a fresh corpus.

## Cost

From the product's own usage ledger, not reconstructed.

| | study A | pass 2 | pass 3 | total |
|---|---:|---:|---:|---:|
| generation + the loop's own audit | $0.63 | — | — | $0.63 |
| CLEAR ground truth | $0.48 | — | — | $0.48 |
| judging (all arms) | $0.81 | $0.23 | $0.21 | $1.25 |
| adjudication | $0.00 | $0.02 | $0.02 | $0.04 |
| **total** | **$1.91** | **$0.25** | **$0.23** | **$2.40** |

Per judging arm across study A's 11 instances: `cross` $0.16 (mean 14.7 s), `self` $0.18
(11.1 s), `sibling` $0.47 (12.9 s), `none` $0.00. Generation averaged 56 s per instance.
Discarded trial runs, deleted before the frozen study, cost about **$1.60** more; the
whole effort was about **$4.00** of the US$20 two-study budget. Token counts are on every
JSONL row; the OpenAI adapter reported far fewer input tokens than the prompt contains
(3 684 across 11 audits of ~9 800-byte prompts), which is prompt caching and/or a
different accounting convention at that provider, so **input-token counts are not
comparable across vendors** and no per-token claim is made here.

---

## Deviations, numbered and complete

1. **An unregistered trial ran first and was discarded in full.** Before
   `benchmarks/EXPERIMENT_RECORD.md` existed, this harness ran a 3-instance trial and
   then a 5-instance partial run, and their scores were read. When the record standard
   landed mid-run the run was killed, the run directories were deleted, and the study was
   restarted from zero at `9656cbf` with `PREREGISTRATION-5.md` committed first. **No
   number from those runs appears anywhere above**, and nothing in the preregistration
   was chosen after seeing them — but they were seen, which is why they are item 1.
2. **OpenAI's credit balance was exhausted mid-study and later restored.** The first
   frozen attempt died on `insufficient_quota` (reported by the provider as HTTP 429 with
   `credit_balance_exhausted`, which is why the harness's rate-limit backoff waited on it
   for 17 minutes before the cause was identified). Credit was restored by the operator
   and the run restarted. **Bias:** none on the comparison — no scores from before the
   restoration are used.
3. **Anthropic's credit balance was exhausted during the run and was not restored.**
   This is the study's largest deviation. It caused, in order: 4 of study A's last
   instances to produce no draft (0.9 s failures with zero cost, the generator's circuit
   open); one instance to lose both its Anthropic judging arms mid-instance; and **both
   preregistered study-B replicates to fail every instance in under a second.** The
   preregistered noise floor — three full re-runs including generation — was therefore
   **not obtained**. The substitute in this report varies only the auditor.
   **Bias:** the attrition is generation-side and identical across arms, so it cannot bias
   the between-arm comparison; it narrows what the result generalises to and it removed
   the generation-side noise floor entirely.
4. **5 of 16 instances produced no round-one deliverable and were dropped before any
   judging.** One early (18 s, cause unrecorded) and four to Deviation 3. Analysed
   n = 11. **Bias:** none between arms — all four arms judge the same drafts, and an
   instance with no draft is absent from every arm equally.
5. **One instance (`10.1002/smll.202408072`) lost its `self` and `sibling` arms** to
   `ProviderDenial: all configured auditor provider routes failed` (Deviation 3). Its
   `cross` arm succeeded and is included in the `cross` micro-totals; the instance is
   excluded from every paired comparison, which is why every paired n is 10 while the
   pooled `cross` denominator is 11 instances / 59 items. **Bias:** on that instance
   `cross` had 5 wrong items and recalled 1 of them (20%), just under its own pooled mean
   of 20.3%, so its exclusion from the paired tests moves them very little — but it is one
   instance in ten and the direction is only knowable for the arm that survived.
6. **Study A was resumed once.** The first invocation recorded 14 instances; a `--resume`
   added the remaining 2 (both of which then failed under Deviation 3). The frozen sha was
   the same before and after and no arm, prompt, model or setting was touched. No score
   was read between the two invocations.
7. **The substitute noise floor was built after the primary scores were read.** `--rejudge`
   was written and committed at `b05aee3`, after study A's numbers were known. It changes
   no measurement in study A; it adds two further passes. Labelled exploratory throughout.
8. **The re-judged prompts differ from study A's by an embedded commit id.** Raw digests
   do not match; commit-normalised digests match 11/11. Quantified in the noise-floor
   section. **Bias:** the auditor is not asked about the commit id, but this is an
   assumption about the model rather than a measurement of it.
9. **The CLEAR judge shares a vendor with the `cross` arm.** `openai:gpt-5.6-terra` both
   judged the drafts and, as `cross`, audited them — there was no third vendor with
   credentials. **Bias: in `cross`'s favour**, and `cross` lost the primary outcome
   anyway, which strengthens rather than weakens the headline. It correspondingly weakens
   any reading of `self`'s advantage as large.
10. **`sibling` is `claude-opus-4-8`, a more expensive and nominally stronger model than
    the generator.** A "same vendor, different model" arm cannot also hold capability
    fixed with only two vendors available. **Bias:** unclear; `sibling` had the *lowest*
    recall of the three, so a capability story does not explain the data.
11. **Temperature and seed are not settable.** The adapters take temperature from the
    model's capability card and `resilience.complete` exposes no seed. The study cannot
    *set* determinism, only measure the resulting spread — which is what the noise floor
    is for.
12. **The provider-echoed model id was not captured.** The harness records it, but
    `Reply.raw` is empty at this seam under sealed retention, so
    `provider_model_echoed` is `""` on every row. The requested id is recorded and the
    provider's silent resolution of an alias, if any, is not visible here.
13. **`max_rounds: 1`**, unlike studies 1–3, which allowed 3. This study judges a draft
    and does not revise it, so there is no round two anywhere in the data, and `none`'s
    "final output" is identical to every other arm's. The final-output comparison the
    brief asked `none` to anchor is therefore **degenerate by construction** and is not
    reported; what `none` establishes is the floor it can establish — that an unjudged
    draft has 0% of its defects named, on 59 wrong items.
14. **Adjudication cost for study A reads $0.00** in the ledger query, against a non-zero
    figure for the two passes. The adjudicator calls were placed (every finding carries a
    mapping) and are metered somewhere the phase filter missed; the total is small enough
    (≈$0.02 by the passes' rate) not to change any figure, and it is stated rather than
    silently absorbed.

## Limitations

- **The CLEAR scorer is a reimplementation from the paper.** The authors released no
  evaluation code, so it has never been diffed against theirs. The only external check is
  that this implementation places frontier models roughly where the paper places them on
  this task. **Every number in this report inherits that.**
- **A model-judged ground truth is not ground truth.** "Wrong" here means
  `openai:gpt-5.6-terra` judged the draft and the human reference not to be mutually
  contained on that rubric item. Every recall and precision figure above is *against a
  model's opinion*, and the same model supplied one of the four arms.
- **Vendor independence is not statistical independence.** Two models from different
  vendors share training data, architecture and human-feedback conventions. Cross-vendor
  auditing reduces *correlated* error; it does not create an independent oracle, and
  nothing here should be read as if it did. This matters especially for the negative
  result: **the finding is not "independence does not help", it is "this particular
  vendor boundary did not raise recall on this task"** — which is a much smaller claim,
  and the smaller claim is the one the data supports.
- **One task is one task.** T03MaterialSEG is solid-state synthesis justification. This
  is the fifth study on it and none of them has been repeated elsewhere.
- **n = 10 paired.** This study cannot detect a 10-point recall difference. Its most
  defensible outputs are the noise floor and the severity asymmetry, not a verdict on the
  invariant.
- **The arms are two vendors, three models, one generator, one seed.** "Cross-vendor" is
  operationalised here as exactly `anthropic → openai`. A different pair could behave
  differently and this study says nothing about that.
- **The measured configuration is not the shipped default.** Rubric-grade rules, one
  round, no revision.

## What this run does and does not license

**It licenses:**

1. **The cross-vendor auditor did not name more defects than the same-vendor one**, on
   this task at n = 10: −10.3 pp paired, and −14.0 pp under the deterministic mapping.
2. **The run-to-run standard deviation of audit recall is 2.6 pp**, and of the firing
   rate 10.5 pp, over three identical runs.
3. **Study 2's 2.0% → 3.8% auditor-model result is inside that noise** and should not be
   cited again.
4. **Two models from the same vendor differed by more than the two vendors did**
   (−22.7 pp, p = 0.0078), so vendor is not the axis that governs recall here.
5. **Precision is unharmed by same-vendor judging**: 75% / 79% / 75%, indistinguishable.

**It does not license:**

- **"Cross-vendor auditing is useless."** It is not measured as useless; it is measured
  as not-better-at-recall on one task with one vendor pair at n = 10, while being
  dramatically more willing to block. The invariant may well be doing something valuable
  that this study did not measure.
- **"Same-vendor auditing is safe."** `self` named more and blocked almost nothing. An
  auditor that files real defects as advice does not gate, and a gate that never closes is
  not an audit. This study measured what each arm *said*, not what shipping on its verdict
  would produce.
- **Any statement about the final output.** No arm revised anything.
- **The severity finding as a result.** It is exploratory, from 51 findings across 11
  instances, and belongs in a preregistered follow-up.
- **Anything about the generation-side noise floor**, which remains unmeasured and under
  which four of this project's published F1 deltas still sit unjudged.

**Do not re-run this study hoping for a different number.** If the configuration changes,
the study restarts and says so here.

---

## Reproduction

Requires `CROSSAUDIT_ANTHROPIC_KEY` and `CROSSAUDIT_OPENAI_KEY` (or the role-named
fallbacks in `~/.crossaudit-keys.env`), both funded, and network access to both vendors.

```sh
git checkout 9656cbf                      # the frozen sha; tree was clean at freeze
export PYTHONPATH="$(git rev-parse --show-toplevel)/src"
python benchmarks/expertlongbench/fetch.py --tasks T03MaterialSEG   # CC BY-NC-SA 4.0,
                                          # not redistributed by this repository
R="$PWD/benchmarks/expertlongbench/runs"

# study A -- one draft per instance, judged four ways
python benchmarks/expertlongbench/premise.py --n 16 --seed 20261104 \
    --verify-prompt --label premise-A --out "$R/premise-A"

# the substitute noise floor (added at b05aee3): judge the same drafts again
for k in 2 3; do
  python benchmarks/expertlongbench/premise.py --n 16 --seed 20261104 --arms cross \
      --label premise-C-pass$k --rejudge "$R/premise-A" --out "$R/premise-C-pass$k"
done

python benchmarks/expertlongbench/premise_report.py "$R/premise-A"
```

`--out` must be absolute. It will not reproduce byte-identically: the provider layer
exposes no seed and temperature comes from the model's capability card. The
preregistered study B — three full re-runs including generation — is the command that
was never able to run:

```sh
for k in 1 2 3; do
  python benchmarks/expertlongbench/premise.py --n 16 --seed 20261104 --subset 8 \
      --label premise-B-rep$k --out "$R/premise-B-rep$k"
done
python benchmarks/expertlongbench/premise_report.py "$R"/premise-B-rep{1,2,3}
```
