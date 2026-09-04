# Study 5B — preregistration for the confirmatory rerun

Amends `PREREGISTRATION-5.md`. Written and committed **before any model is called under
the frozen sha for this run**. Results go to `RESULTS-5.md`, which is rewritten around
this run.

## Why there is a rerun, stated plainly

Study 5's first execution answered its primary question at **n = 10 paired instances**,
which is too few to settle anything, and lost its preregistered noise floor entirely when
both vendors' API credit ran out mid-run. Both providers are verified funded and
answering as of this run. The rerun exists to settle the primary outcome at n ≈ 30 and to
produce the noise floor the original design asked for.

**This is a confirmatory rerun and its sample is disjoint in size, not in kind: it draws
from the same 50-row corpus with the same seed, so the first run's 16 instances are a
subset of this run's 40.** The two runs are **not pooled**. Every number in the rewritten
results comes from this run alone. The first run's numbers are reported beside them as a
prior, independent-attempt estimate, and are labelled as such.

**I already know the sign of the primary outcome and the shape of the severity result
from the first run.** That is precisely why both are fixed in writing here, before this
run, and why the primary outcome's definition is carried over **unchanged**. Nothing
below was chosen to flatter what was seen.

---

## The primary outcome — unchanged, and deliberately so

> **The paired difference in round-one audit recall against CLEAR ground truth,
> `cross` minus `self`, over the same drafts**, with a finding mapped to rubric items by
> the **adjudicator model**.

Same definition, same mapping, same test as `PREREGISTRATION-5.md`: mean paired
difference in percentage points, 95% percentile-bootstrap CI over instances, exact
two-sided Wilcoxon signed-rank with ties dropped. **It is not redefined now that its sign
is known.** The first run put it at −10.3 pp (CI −25.3 to +5.0, p = 0.28, n = 10).

**H1** (the product's claim): `cross` − `self` > 0.
**What the first run suggests**: `cross` − `self` < 0.
Either can come out; the rerun is powered to tell them apart in a way n = 10 was not.

---

## Newly registered secondary outcome — severity (was exploratory)

The first run found that `cross` filed **all 18** of its findings as BLOCKER and gated
8 of 11 increments, while `self` raised **more** findings (24), filed 18 of them
ADVISORY, and gated 2 of 11. That was exploratory. It is registered here as a named
secondary outcome with its own statistics, so this run can **confirm or kill it**.

**S1 — gate rate.** For each arm, the proportion of judged instances on which it raised
at least one BLOCKER finding. This is the quantity that decides whether work is stopped:
an ADVISORY gates nothing, returns nothing to the writer, and lets the draft ship.

- statistic: paired difference in gate rate, `cross` − `self`, in percentage points;
- test: **exact McNemar** (two-sided binomial on the discordant pairs), which is the
  paired test for a binary outcome measured twice on the same instance;
- interval: 95% percentile bootstrap over instances on the paired difference.

**S2 — blocking recall.** Recall computed over **BLOCKER findings only**, otherwise
identical to the primary outcome, under both the adjudicator and the deterministic rule
mapping. Same Wilcoxon and bootstrap machinery as the primary.

**Registered predictions, in advance:**

- **S1: `cross` gate rate exceeds `self` gate rate by at least 30 pp.**
- **S2: `cross` blocking recall exceeds `self` blocking recall.**
- **S3 (the interpretation this is meant to test): `self` total recall ≥ `cross` total
  recall while `cross` gate rate > `self` gate rate.** If both hold, the product's claim
  changes from *"a stranger sees more"* to *"a stranger is less tolerant"* — a different
  and more defensible sentence, and the one the results will lead with.

**Kill criteria, also in advance.** The severity finding is **not** confirmed if either:

- the gate-rate difference is smaller than **two standard deviations of the gate rate's
  own run-to-run spread**, measured by this run's three replicates; or
- the sign of the gate-rate difference is not the predicted one.

A finding that dies by its own registered criterion is reported as dead.

---

## The noise floor — a deliverable, not a nice-to-have

The preregistered design from `PREREGISTRATION-5.md` is run as written this time: **the
identical configuration, three times, over the same 8 instances**, varying nothing the
harness can control. This includes **generation**, which the substitute floor in the
first run did not, and which is the reason four of this project's published F1 deltas
(+2.04, −6.11, −11.01, +24.07) currently have nothing underneath them.

Reported: the run-to-run standard deviation of every arm mean, for draft CLEAR F1, recall,
blocking recall, gate rate and firing rate. Then, explicitly, **a list of this project's
published numbers that survive that floor and a list of those that do not.** Study 2's
2.0% → 3.8% auditor-model result is already dead by the auditor-only floor
(1.8 pp against SD 2.6 pp) and will be stated as **withdrawn**.

---

## n, and the headroom

**Target: 30 complete instances** — drafted, CLEAR-scored, and judged by every arm — not
30 attempted. **40 instances are seeded** (seed `20261104`, same rule as before: sorted by
id, sampled, re-sorted) and the run stops as soon as 30 are complete. The first run
completed 11 of 16 (69%) under a failing credit balance; 40 seeded is 33% headroom over
the target at that rate and considerably more at a healthy one. Instances that fail cost
attempts, not analysed n.

The noise floor runs on the first 8 of that same seeded sample, three times.

## Preflight

Every model this run needs — generator, all three judging arms, CLEAR mapper, judge and
adjudicator — must answer a one-word prompt through the product's own provider layer
**before the first instance is generated**. A failure aborts the run loudly and
immediately rather than losing an arm mid-run after paying for generations. This is a new
harness requirement created by the first run's quota failure, and it is not a
measurement.

## Stopping rule

Run until 30 complete instances, then the three replicates. Stop and report what
completed if the **US$16 remaining** of the US$20 two-study budget is spent, read from the
product's own usage ledger. No arm is dropped to buy more instances and no instance is
dropped after its scores are seen.

## Comparisons this run makes

**Preregistered: 11.** Six paired recall tests (three arm pairs × two mappings, as
before), plus S1 (gate rate, one paired test), plus S2 (blocking recall, two mappings ×
two arm pairs = four). The primary outcome is the first of these and was named before
either run.

This is the sixth study over the same task and the same 50 rows, and the second execution
of this one. That history is the multiple-comparison picture and is restated in the
results rather than left to the reader.

## What would void the run

- Any instance where the harness's audit prompt digest differs from the digest the
  product's own audit recorded for the same commit. The arms would not be judging the
  same bytes.
- An arm whose replies are rejected by the rule validator materially more often than
  another's; its recall would not be comparable, and that is reported rather than
  absorbed.
