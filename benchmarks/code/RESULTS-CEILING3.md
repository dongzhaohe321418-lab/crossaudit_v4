# Ceiling 3 — two more auditor families: the BLOCKER ceiling is a severity policy, not a limit of seeing

Study 18. Preregistered at `benchmarks/code/ceiling3/PREREGISTRATION.md` (0e8c7e0, before any
model call; Amendment 1 at 64af5f3 after `self-strong` draw 1, before draw 2). Substrate,
instances, solutions, constitution, audit path and the union-of-K protocol are ceiling 1's,
frozen (`RESULTS-CEILING.md`, D162). Records: `records/ceiling3/cache/` (one row per reading,
no prompt or reply text), `records/ceiling3/numbers.json` (from `report_ceiling3.py --run`),
the archive `~/Documents/Crossaudit/study-data/wt-ceiling3-runs/` (ledgers, run log, the
probe, `MANIFEST.sha256`). Every rate carries the Wilson interval and the problem-cluster
bootstrap (seed 20260910, 10,000 resamples; the cluster interval is the primary one, as in
ceiling 1). Both new families ran at the product's default reasoning setting for the auditor
role, as the existing families did.

## 1. The preregistered outcomes

Union-of-K on the same 110 P and 150 C instances; the flag is ceiling 1's, **at least one
BLOCKER finding**.

| family | K | P union recall | Wilson | cluster | C union FP | Wilson | cluster | single draw P |
|---|---|---|---|---|---|---|---|---|
| `cross` (gpt-5.6-terra) | 8 | 33/110 = 30.0% | 22.2–39.2 | 19.8–40.7 | 24/150 = 16.0% | 11.0–22.6 | 10.1–22.3 | 10.7% |
| `self` (Haiku 4.5) | 8 | 19/110 = 17.3% | 11.4–25.3 | 8.2–27.3 | 36/150 = 24.0% | 17.9–31.4 | 17.2–31.2 | 15.5% |
| `astra` (gpt-6-astra) | 4 | 36/110 = 32.7% | 24.7–41.9 | 20.7–45.0 | 16/150 = 10.7% | 6.7–16.6 | 5.3–14.5 | 30.2% |
| **`self-strong` (Sonnet 4.6)** | **8** | **4/110 = 3.6%** | 1.4–9.0 | 0.9–7.4 | 5/150 = 3.3% | 1.4–7.6 | 0.7–6.7 | 0.6% |
| **`self-frontier` (Opus 4.8)** | **4** | **1/110 = 0.9%** | 0.2–5.0 | 0.0–2.8 | 4/150 = 2.7% | 1.0–6.7 | 0.7–5.4 | 0.5% |

The `self-strong` curve on P is 0.6, 1.1, 1.6, 2.1, 2.5, 2.9, 3.3, 3.6% at K = 1…8; it has
not flattened in the preregistered sense (the K = 7 → 8 gain is 0.34 points) but it is a
line through the origin, and the saturation fit is **not estimable** on it (the constrained
A runs to its bound; the report says n/e wherever the K_max union is under 5%, a guard added
after the first draw and before any result was read as a fit).

* **Primary (H18b, equivalence with `cross` at K = 8): false.** `self-strong` − `cross` on
  P = **−26.4 points, cluster 95% [−37.3, −15.6]**; 3 instances flagged by `self-strong` only,
  32 by `cross` only; exact McNemar p < 0.001; cluster sign-flip p < 0.001. The interval
  excludes zero by a wide margin: the ~30% figure is not reproduced by a stronger model of
  the other vendor under this rule.
* **H18a (size, not vendor): false, in the opposite direction.** `self-strong` − `self` on
  P at K = 8 = **−13.6 points [−24.1, −4.5]** (2 vs 17 instances only; p = 0.001). The larger
  same-vendor model blocks *less* than the small one, so the low same-vendor ceiling of
  ceiling 1 is not a size effect.
* **H18c (frontier point).** `self-frontier` − `astra` on P: K = 1, −27.3 points
  [−39.1, −16.4]; K = 4, −31.8 [−44.1, −20.0]; on C at K = 4, −8.0 [−13.9, −2.6]. The
  Anthropic frontier model blocks almost nothing where the OpenAI frontier model blocks a
  third of the defects at a tenth of the correct code.
* **Blocked by no family, ever**: 56 of 110 defects (50.9%; Wilson 41.7–60.1%) across the
  five families' 32 draws — the ceiling of *blocking* by reading, over everything measured.
* `mixed` (4 `cross` + 4 `self-strong` readings): 23.1% on P against `cross`'s own 30.0% at
  eight readings and 24.0% at four: spreading readings to this family loses recall.

## 2. What the near-zero rate is, and is not (Amendment 1's secondary, plus one exploratory rule)

**It is not a format failure.** 0 of 2,080 Sonnet readings and 5 of 1,040 Opus readings
were rejected as malformed; the harness's re-ask path was used at most 46 times over the
3,120 readings (the ledgers hold 3,166 auditor calls). About a quarter of Sonnet's replies
and a fifth of Opus's are long (over 300 output tokens): the models read and write.

**It is a severity policy.** Sonnet returned at least one finding on 54–73 of 260 instances
per draw, Opus on 23–30, and graded almost all of them ADVISORY. Under an **EXPLORATORY,
not preregistered** rule — flag = at least one finding of any severity — the picture
inverts:

| family | K | P union (any finding) | cluster | single | C union (any finding) |
|---|---|---|---|---|---|
| `cross` | 8 | 34.5% | 23.6–45.5 | 11.5% | 19.3% |
| `self` (Haiku) | 8 | 20.9% | 10.9–31.8 | 18.8% | 27.3% |
| `astra` | 4 | 32.7% | 20.7–45.0 | 30.5% | 10.7% |
| **`self-strong` (Sonnet)** | 8 | **59.1%** | **47.3–70.6** | **33.9%** | 34.0% |
| `self-frontier` (Opus) | 4 | 20.9% | 11.6–31.2 | 10.9% | 18.0% |

Under that rule Sonnet's single reading sees more defects than the shipped auditor's
eight, and its eight readings reach 59%, at a false-positive rate (34%) the product could
not ship; **mentioned by no family at any severity: 25 of 110 = 22.7%** (Wilson 15.9–31.4%)
across the same 32 draws, against 50.9% blocked by none. The gap between those two
numbers — 28 points of the defect population — is what the constitution's severity rule
does to what the models saw. This is the D153 pattern ("sees, and lets it pass") measured
on the strongest models available, and it is exploratory because the rule was chosen after
the BLOCKER result was seen; it is reported so that the preregistered near-zero is not
read as blindness.

## 3. What this study licenses

* On this substrate the **BLOCKER ceiling is not a property of "AI audit"**: it moves from
  ~30% to ~1% across vendors at the same instructions, and within a vendor it moves the
  wrong way with model size. What is stable across families is not the ceiling but the
  residual: half the defects are blocked by no reading of anything.
* The **severity rule is the lever**, as the referent rule was in ceiling 2: the next
  preregistered study on this axis runs the two Anthropic families under a constitution
  whose blocking criterion is stated for them (the referent rule, or "any finding that names
  an input on which the code is wrong is a BLOCKER"), with the any-finding rule now
  preregistered beside the BLOCKER rule for every family.
* Nothing here changes ceiling 1's numbers or D162; the generator axis (stage B) and the
  task axis (stage C) remain to be measured.

## 4. Cost, deviations, limits

* **Cost**: $36.05 from the twelve project ledgers (Sonnet $2.17–2.28 per 260-reading draw,
  Opus $4.49–4.57), 3,166 calls; budget $120. The per-row `cost_usd` stamped into the cache
  is unreliable where a draw needed several passes: `explore.run_detector` numbers `run_id`
  by position within the pass, so rows of different passes can share an id and one row can
  carry another's cost (a harness limitation inherited from ceiling 1, which quoted ledger
  totals, as this does). `numbers.json`'s `cost_by_draw` is therefore not the cost table;
  the ledger totals above are.
* **Run history**: stopped by the author after `self-strong` draw 1 (Amendment 1) and
  resumed with no design change; transport failures (SSL EOF) tripped the provider breaker
  repeatedly, and `self-frontier` draws 2 and 3 were completed by a second invocation of the
  same resumable loop after the ladder had finished (41 and 105 readings). Every reading
  is one call keyed by `(family, draw, instance)`; none was bought twice.
* **Limits**: one substrate, one constitution, the product's default reasoning setting; the
  any-finding rule is post hoc; the Opus family has four draws, not eight; the same-vendor
  bypass is the harness's and says nothing about the product path, exactly as for `self`.
