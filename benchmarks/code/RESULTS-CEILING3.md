# Ceiling 3 — two more auditor families: the BLOCKER ceiling is not one number, and half the defects are blocked by nothing

Study 18. Preregistered at `benchmarks/code/ceiling3/PREREGISTRATION.md` (0e8c7e0, 10:56:52
UTC on 2026-09-09; the first call at 10:58:28). Amendment 1 (64af5f3, 11:14:31 UTC) was
committed after 30 draw-2 readings had landed, not before draw 2 as it said; Amendment 2
corrects that and withdraws an outcome-dependent fit guard the first version of this file
used. Substrate, instances, solutions, constitution, audit path and the union-of-K protocol
are ceiling 1's, frozen (`RESULTS-CEILING.md`, D162). Records: `records/ceiling3/cache/`
(one row per reading, no text), `records/ceiling3/numbers.json` (from
`report_ceiling3.py --run`), the archive `~/Documents/Crossaudit/study-data/wt-ceiling3-runs/`
(ledgers, run log, the re-run probe, `MANIFEST.sha256`). Every rate below carries the Wilson
interval and the problem-cluster bootstrap (seed 20260910, 10,000 resamples), the cluster
interval being the primary one as in ceiling 1, with ceiling 1's caveat inherited: the
percentile bootstrap's coverage under this clustered design has not been validated by
simulation. Both new families ran at the product's default reasoning setting for the
auditor role (`reasoning_effort` unset), as the existing families did; 3,074 of their 3,120
readings carry the same prompt digest as study 2's committed holistic-cross reading of the
same instance, and the other 46 are the product's bounded repair prompts after a malformed
first reply (`invalid_reason` empty because the repair succeeded).

## 1. The preregistered outcomes

Flag = at least one BLOCKER finding (ceiling 1's rule). Union of K readings.

| family | K | P union recall | Wilson | cluster | C union FP | Wilson | cluster | single-draw P / C |
|---|---|---|---|---|---|---|---|---|
| `cross` (gpt-5.6-terra) | 8 | 33/110 = 30.0% | 22.2–39.2 | 19.8–40.7 | 24/150 = 16.0% | 11.0–22.6 | 10.1–22.3 | 10.7% / 4.5% |
| `self` (Haiku 4.5) | 8 | 19/110 = 17.3% | 11.4–25.3 | 8.2–27.3 | 36/150 = 24.0% | 17.9–31.4 | 17.2–31.2 | 15.5% / 21.9% |
| `astra` (gpt-6-astra) | 4 | 36/110 = 32.7% | 24.7–41.9 | 20.7–45.0 | 16/150 = 10.7% | 6.7–16.6 | 5.3–14.5 | 30.2% / 9.7% |
| **`self-strong` (Sonnet 4.6)** | **8** | **4/110 = 3.6%** | 1.4–9.0 | 0.9–7.4 | 5/150 = 3.3% | 1.4–7.6 | 0.7–6.7 | 0.6% / 1.7% |
| **`self-frontier` (Opus 4.8)** | **4** | **1/110 = 0.9%** | 0.2–5.0 | 0.0–2.8 | 4/150 = 2.7% | 1.0–6.7 | 0.7–5.4 | 0.5% / 0.8% |

Curves at K = 1…K_max (P; then C):
`self-strong` 0.6, 1.1, 1.6, 2.1, 2.5, 2.9, 3.3, 3.6%; C 1.7, 2.0, 2.3, 2.5, 2.8, 3.0, 3.2, 3.3%.
`self-frontier` 0.5, 0.8, 0.9, 0.9%; C 0.8, 1.6, 2.2, 2.7%.
Fitted asymptotes (§1.2's form, always reported; a post-hoc diagnostic beside each, added
after the results were seen and labelled so): `self-strong` A = 8.5% [1.1, 100], τ = 14.3 —
τ > K_max, so the asymptote extrapolates past the readings taken (the curve is near-linear
over K = 1…8; ceiling 1's flattening bar is not met); `self-frontier` A = 1.0% [0.0, 3.1],
τ = 1.5. Exchange rates (Δ recall / Δ FP, K = 1 → K_max): `self-strong` 1.84, `self-frontier`
0.25, against `cross` 1.68, `self` 0.87, `astra` 2.50.

* **Primary (H18b, equivalence with `cross` at K = 8): false.** `self-strong` − `cross` on
  P = **−26.4 points, cluster 95% [−37.3, −15.6]**; 3 instances flagged by `self-strong`
  only, 32 by `cross` only; exact McNemar p = 4.2 × 10⁻⁷; cluster sign-flip p = 2.0 × 10⁻⁵
  (sampled, 200,000 draws). On C: −12.7 points [−19.3, −6.1] (3 vs 22; McNemar p = 1.6 ×
  10⁻⁴; sign-flip p = 2.4 × 10⁻⁴).
* **H18a (size, not vendor): false, in the opposite direction.** `self-strong` − `self` on
  P at K = 8 = **−13.6 points [−24.1, −4.5]** (2 vs 17; McNemar p = 7.3 × 10⁻⁴; sign-flip
  p = 0.015). The larger same-vendor model blocks less than the small one.
* **H18c (frontier point).** K = 1 as preregistered — each family's mean single-draw rate
  over its four draws, paired per instance — `self-frontier` − `astra` on P = **−29.8
  points [−41.4, −18.6]**, sign-flip p < 10⁻⁵ (the draw-1-only contrast the first version
  of this file reported, −27.3 [−39.1, −16.4], is kept in `numbers.json` as exploratory).
  K = 4 unions: −31.8 [−44.1, −20.0] (0 vs 35; sign-flip p = 3.8 × 10⁻⁶); on C −8.0
  [−13.9, −2.6] (McNemar p = 0.008; sign-flip p = 0.011).
* **Blocked by no family, ever**: 56 of 110 defects = 50.9% (Wilson 41.7–60.1; cluster
  39.1–62.7) across the five families' 32 draws.
* `mixed` (K/2 `cross` + K/2 `self-strong`): 11.2, 16.0, 19.8, 23.1% at K = 2, 4, 6, 8,
  against `cross` alone 16.5, 24.0, 27.7, 30.0% at the same totals: spreading readings to
  this family loses recall at every K.
* **Residual (§1.5)**: the strongest family under the BLOCKER rule is unchanged (`astra`,
  then `cross`), so ceiling 1's residual classification stands and was not re-run.

## 2. What the near-zero rate is, and what the record can and cannot say about it

**It is not a format failure.** 0 of 2,080 Sonnet readings and 5 of 1,040 Opus readings
were rejected as malformed; the ledgers hold 3,166 auditor calls for 3,120 readings, so at
most 46 readings needed the product's repair re-ask (2–5 per draw). 66–77 of Sonnet's 260
replies per draw and 51–59 of Opus's are over 300 output tokens.

**It is a grading outcome.** Per draw Sonnet returned at least one finding of some severity
on 54–73 of the 260 instances and graded 2–5 of those BLOCKER; Opus on 23–30, with 1–3
BLOCKER. Under an **EXPLORATORY, not preregistered** rule — flag = at least one finding of
any severity — the rates are:

| family | K | P union (any finding) | Wilson | cluster | single P | C union (any finding) | cluster |
|---|---|---|---|---|---|---|---|
| `cross` | 8 | 34.5% | 26.3–43.8 | 23.6–45.5 | 11.5% | 19.3% | 12.8–26.3 |
| `self` (Haiku) | 8 | 20.9% | 14.4–29.4 | 10.9–31.8 | 18.8% | 27.3% | 20.1–34.9 |
| `astra` | 4 | 32.7% | 24.7–41.9 | 20.7–45.0 | 30.5% | 10.7% | 5.9–16.1 |
| **`self-strong` (Sonnet)** | 8 | **59.1%** | 49.7–67.8 | 47.3–70.6 | 33.9% | 34.0% | 26.5–41.7 |
| `self-frontier` (Opus) | 4 | 20.9% | 14.4–29.4 | 11.6–31.2 | 10.9% | 18.0% | 11.7–24.8 |

**Mentioned by no family at any severity: 25 of 110 = 22.7%** (Wilson 15.9–31.4; cluster
13.5–32.7), against 50.9% blocked by none.

**What this does and does not show.** The any-finding rate is a flag rate: an instance on
which the model returned *some* finding. The advisory texts were not archived or
adjudicated against the hidden failure, so a finding on a P instance is not shown to name
that instance's defect, and "Sonnet sees 59% of the defects" is **not** a claim this record
supports. What the record supports is narrower: the Anthropic families return findings on
far more instances than they block, and the gap between "mentioned by none" (22.7%) and
"blocked by none" (50.9%) is 28 points of the defect population. **That the gap is a
severity policy rather than a limit of seeing is the author's inference**, and the study
designed to test it — the same families under a constitution that states the blocking
criterion (ceiling 3b) — is preregistered separately. Whether the advisory findings name
the defects is a question that study answers only if it archives and adjudicates the texts.

## 3. What this study licenses

* On this substrate the **BLOCKER ceiling is not a property of "AI audit"**: at the same
  instructions it is ~30% for one vendor's models and ~1–4% for the other's, and within the
  second vendor it falls with model size. What is stable across families is the residual:
  56 of 110 defects are blocked by no reading of anything measured.
* The instruction axis is the next thing to vary on these families, as it was for the
  shipped auditor in ceiling 2 (the referent rule). Nothing here changes ceiling 1's numbers
  or D162; the generator axis (stage B) and the task axis (stage C) remain.

## 4. Cost, deviations, limits

* **Cost**: $36.05 from the twelve project ledgers (Sonnet $2.17–2.28 per 260-reading draw,
  Opus $4.49–4.57), 3,166 calls; budget $120. The per-row `cost_usd` stamped into the cache
  is unreliable where a draw needed several passes: `explore.run_detector` numbers `run_id`
  by position within the pass, so rows of different passes can share an id and one row can
  carry another's cost (a harness limitation inherited from ceiling 1, which also quoted
  ledger totals). `numbers.json`'s `cost_by_draw` is not the cost table; the ledger totals
  are (`reply_format_secondary.*.ledger_usd`).
* **Run history**: stopped by the author during `self-strong` draw 2 after 30 of its
  readings had landed (Amendment 1 misdated this; Amendment 2 corrects it) and resumed with
  no design change; transport failures (SSL EOF) tripped the provider breaker repeatedly;
  `self-frontier` draws 2 and 3 were completed by a second invocation of the same resumable
  loop (41 and 105 readings). Each reading is one accepted reply; 46 of the 3,120 needed one
  repair call first.
* **Post-hoc elements, all labelled**: the any-finding rule; the τ > K_max diagnostic; the
  draw-1-only H18c contrast; the probe re-run (the original replies were not archived).
* **Limits**: one substrate, one constitution, the product's default reasoning setting; the
  Opus family has four draws; the same-vendor bypass is the harness's and says nothing about
  the product path, exactly as for `self`; `tests/test_ceiling3_report.py` binds the figures
  of §1's table, the contrasts and §2's counts to `numbers.json` — the prose is the
  reviewer's to check.
