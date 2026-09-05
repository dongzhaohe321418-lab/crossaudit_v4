# Fifteen audit architectures, one ROC curve — the shipped architecture is on the front and nothing measured here improves on it

**The preregistered null is the result.** Fifteen architectures were composed and
scored against model-free ground truth over the same 290 frozen instances. Under
the objective fixed before any of them was scored — *highest P-recall on the
confirm half among specs whose false-positive rate on correct code is ≤ 6.7%* —
**no spec beats the shipped architecture. Every spec that satisfies the constraint
has lower recall than the shipped architecture, and every spec with higher recall
violates it.** The shipped `holistic-cross` sits on the Pareto front, and it is the
cheapest thing on the front above 12.7% recall.

| on the confirm half (n = 55 P, 74 C, 15 F) | P-recall | false positives on correct code | $/instance |
|---|---|---|---:|
| **`hc` — the shipped architecture** | **20.0% (11/55), CI [11.6, 32.4]** | **6.8% (5/74), CI [2.9, 14.9]** | **$0.0069** |
| `tri_majority` — best under the objective | 14.5% (8/55), CI [7.6, 26.2] | 5.4% (4/74), CI [2.1, 13.1] | $0.0283 |
| `cheap_hc` — what the explore half selected | 10.9% (6/55), CI [5.1, 21.8] | 5.4% (4/74), CI [2.1, 13.1] | $0.0066 |
| `tri_union` — the highest recall in the grid | 41.8% (23/55), CI [29.7, 55.0] | 33.8% (25/74), CI [24.0, 45.1] | $0.0283 |

The objective's literal answer is `tri_majority`, at **5.5 points *below* the
shipped architecture's recall** and four times its cost. The reason `hc` is not
itself the answer is that its confirm-half false-positive rate is **5 of 74 =
6.76%**, which misses the ≤ 6.7% constraint **by less than one instance**. That is
stated as a count, not a rate, because at n = 74 one instance is 1.35 points and
the interval [2.9%, 14.9%] straddles the constraint entirely. The rule is applied
as written and its answer is reported as found; no second objective was
constructed, and the honest reading of the whole table is the same either way:
**nothing in this grid buys recall above the shipped architecture without paying
for it in false positives at a rate the constraint forbids.**

**This reproduces study 2's diagnosis on eight new architectures.** Of the eight
specs that beat `hc` on recall, all eight are outside the constraint, and the
recall they add tracks the false positives they add almost one for one. Of the six
inside or below, all six trade recall away faster than they remove false alarms.
The curve is the same curve.

**Whole-study spend: $4.42 of a $15 budget, 1,242 model calls.** Ten of the fifteen
specs cost nothing: they are set operations over records studies 1 and 2 already
produced.

**Phase 2 did not run.** Its kill condition fired before this grid finished — 13 of
56, against a bar of 19. See `RESULTS-CHECKS.md`. No exec-check adjudication grid
was built, and none is reported here.

Everything below is measured. Nothing is extrapolated.

---

## What was run

Preregistered in [`explore/PREREGISTRATION.md`](explore/PREREGISTRATION.md) with
the grid in [`explore/GRID.json`](explore/GRID.json), both committed at `54b3d5c`
**before the first model call this study reports** — including the credential
probe. The loop is [`explore.py`](explore.py); the objective is applied by
[`report_explore.py`](report_explore.py) and by nothing else.

| | |
|---|---|
| audit set | study 2's, unchanged: **290 instances — P 110, C 150, F 30** |
| stratum P | passes every visible test, **fails a hidden one** — the defects an audit exists to catch |
| stratum C | passes every test — the false-positive population |
| stratum F | fails a visible test — the sanity check |
| ground truth | a Python interpreter raising `AssertionError` or not. **No model judges anything.** |
| solutions | study 2's, byte-identical; study 1's batch-1 solutions verified identical, **540 of 540 sha256** |
| generator | `anthropic:claude-haiku-4-5-20251001`, frozen — nothing was regenerated |
| cross route | `openai:gpt-5.6-terra` — the shipped cross-vendor auditor |
| self route | `anthropic:claude-haiku-4-5-20251001` — the generator's own model |
| cheap route | `openai:gpt-5.6-luna` — the cheap tier of the cross vendor |
| flag | ≥ 1 BLOCKER finding from the model rung, exactly as studies 1 and 2 |
| split seed | `20260906`, stratified on `(stratum, batch)` |
| dates (UTC) | 2026-09-05 06:44 → 07:36 |
| environment | Python 3.13.5, macOS-26.6.2-arm64 |

### The split

| half | P | C | F |
|---|---:|---:|---:|
| explore | 55 | 76 | 15 |
| confirm | 55 | 74 | 15 |

Each half draws ~28 P from each of the two generation batches. **Selection was
performed on the explore half; every number in the headline and in the tables
below is from the confirm half.** The explore half appears once, in its own
section, and carries no claim.

### The loop, and why it cost $4.42

`explore.py` reads the grid and, for each spec and instance, composes the
aggregate from its detectors' records — from study 1's arms, study 2's arms, or
its own cache at `records/explore/cache/`. **A detector with a record is never
re-run.** Only five of the nine detectors in the grid needed any model call:

| detector | records already existing | run here | source |
|---|---:|---:|---|
| `holistic / cross / draw 1` | 290 | 0 | study 2 `holistic-cross` |
| `holistic / self / draw 1` | 290 | 0 | study 2 `holistic-self` |
| `decomposed / cross / draw 1` | 290 | 0 | study 2 `decomposed-cross` |
| `decomposed / cross / draw 2` | 290 | 0 | study 2 `decomposed-replicate` |
| `holistic / cross / draw 2` | 106 | **184** | study 1 `cross` + this loop |
| `holistic / cross / draw 3` | 106 | **184** | study 1 `cross-replicate` + this loop |
| `holistic / cheap-cross / draws 1–3` | 0 | **870** | this loop |

Study 1's `cross` and `cross-replicate` arms are admitted as draws 2 and 3 of one
detector on the ground `RESULTS-2.md` already used: both carry no deterministic
layer (`dcl_blockers == 0` on every row, re-verified here), and study 2 already
treats study 1's `cross` and its own `holistic-cross` as replicate draws over
byte-identical batch-1 solutions.

---

## The full grid on the confirm half

Sorted by recall. "front" marks membership of the Pareto front over
(recall ↑, false positives ↓, cost ↓). "≤ 6.7%" marks eligibility under the
preregistered constraint.

| spec | detectors | P-recall | false positives on C | F | $/inst | $/defect caught | front | ≤ 6.7% |
|---|---|---|---|---|---:|---:|:---:|:---:|
| `tri_union` | 3 | 41.8% (23/55) [29.7, 55.0] | 33.8% (25/74) [24.0, 45.1] | 100.0% (15/15) | $0.0283 | $0.177 | yes | — |
| `hc_u_dc` | 2 | 38.2% (21/55) [26.5, 51.4] | 17.6% (13/74) [10.6, 27.8] | 93.3% (14/15) | $0.0255 | $0.175 | yes | — |
| `hs_u_dc` | 2 | 34.5% (19/55) [23.4, 47.7] | 31.1% (23/74) [21.7, 42.3] | 100.0% (15/15) | $0.0214 | $0.163 | yes | — |
| `dc_x2` | 2 | 30.9% (17/55) [20.3, 44.0] | 17.6% (13/74) [10.6, 27.8] | 86.7% (13/15) | $0.0337 | $0.285 | — | — |
| `dc` | 1 | 27.3% (15/55) [17.3, 40.2] | 14.9% (11/74) [8.5, 24.7] | 80.0% (12/15) | $0.0186 | $0.179 | yes | — |
| `hc_u_hs` | 2 | 25.5% (14/55) [15.8, 38.3] | 24.3% (18/74) [16.0, 35.2] | 100.0% (15/15) | $0.0097 | $0.100 | yes | — |
| `hc_x3` | 3 | 23.6% (13/55) [14.4, 36.3] | 10.8% (8/74) [5.6, 19.9] | 93.3% (14/15) | $0.0186 † | $0.206 | yes | — |
| `hc_x2` | 2 | 21.8% (12/55) [12.9, 34.4] | 8.1% (6/74) [3.8, 16.6] | 93.3% (14/15) | $0.0140 † | $0.168 | yes | — |
| **`hc` (shipped)** | **1** | **20.0% (11/55) [11.6, 32.4]** | **6.8% (5/74) [2.9, 14.9]** | **86.7% (13/15)** | **$0.0069** | **$0.090** | **yes** | **—** |
| `cheap_hc_x3` | 3 | 16.4% (9/55) [8.9, 28.3] | 9.5% (7/74) [4.7, 18.3] | 93.3% (14/15) | $0.0129 | $0.207 | — | — |
| `tri_majority` | 3 | 14.5% (8/55) [7.6, 26.2] | 5.4% (4/74) [2.1, 13.1] | 93.3% (14/15) | $0.0283 | $0.510 | yes | **yes** |
| `hs` | 1 | 12.7% (7/55) [6.3, 24.0] | 18.9% (14/74) [11.6, 29.3] | 73.3% (11/15) | $0.0028 | $0.058 | yes | — |
| `hc_x3_maj` | 3 | 12.7% (7/55) [6.3, 24.0] | 5.4% (4/74) [2.1, 13.1] | 93.3% (14/15) | $0.0186 † | $0.383 | yes | **yes** |
| `cheap_hc` | 1 | 10.9% (6/55) [5.1, 21.8] | 5.4% (4/74) [2.1, 13.1] | 73.3% (11/15) | $0.0066 | $0.159 | yes | **yes** |
| `tri_unanimous` | 3 | 3.6% (2/55) [1.0, 12.3] | 1.4% (1/74) [0.2, 7.3] | 46.7% (7/15) | $0.0283 | $2.041 | yes | **yes** |

All intervals are 95% Wilson. `$/defect caught` is cost per instance × 144 confirm
instances ÷ P-flags; where the flag count is one or two the figure is arithmetic,
not an estimate, and `tri_unanimous`'s $2.04 rests on **2 flags**.

**†** — the cost for these three is **part-reconstructed**. Study 1's committed
rows carry no per-row cost, so their 106 instances are priced from study 1's arm
total ÷ its call count; the other 184 carry the figure the usage ledger recorded.
Every other cost in this table is from the ledger, per instance, unreconstructed.

### The Pareto front, stated as a front

Thirteen of the fifteen specs are non-dominated, which is itself the finding: on
three axes almost nothing is strictly worse than something else, because every
architecture trades along the same curve. Only `dc_x2` and `cheap_hc_x3` are
dominated — `dc_x2` by `hc_u_dc` (more recall, same false positives, less money)
and `cheap_hc_x3` by `hc` (more recall, fewer false positives, less money).

Reading the front from the cheap end: `hs` ($0.0028, 12.7% recall, but 18.9% false
positives) → **`hc` ($0.0069, 20.0%, 6.8%)** → `hc_x2` → `hc_x3` → `hc_u_hs` →
`dc` → `hs_u_dc` → `hc_u_dc` → `tri_union` ($0.0283, 41.8%, 33.8%). Every step
right buys recall and pays in false positives. **The shipped architecture is the
last point on that walk that is anywhere near the constraint.**

---

## Which specs beat the shipped architecture, and where

Paired on identical instances; exact McNemar on the discordant pairs. The
preregistered noise floor is **1.8 points on P**; §"The noise floor is wider than
the record says" below shows the honest floor is larger, which only strengthens
the negative reading.

**Inside the constraint, beating `hc` by more than the noise floor: none.**
Not one. The four specs that satisfy ≤ 6.7% on the confirm half — `tri_majority`,
`hc_x3_maj`, `cheap_hc`, `tri_unanimous` — score **−5.5, −7.3, −9.1 and −16.4**
points of recall against it.

**Outside the constraint, beating `hc` by more than the noise floor: eight.**

| spec | ΔP | ΔC | discordant (spec-only / hc-only) | McNemar exact p |
|---|---:|---:|---|---:|
| `tri_union` | **+21.8** | +27.0 | 12 / 0 | **0.0005** |
| `hc_u_dc` | **+18.2** | +10.8 | 10 / 0 | **0.0020** |
| `hs_u_dc` | **+14.6** | +24.3 | 12 / 4 | 0.0768 |
| `dc_x2` | +10.9 | +10.8 | 11 / 5 | 0.2101 |
| `dc` | +7.3 | +8.1 | 10 / 6 | 0.4545 |
| `hc_u_hs` | +5.5 | +17.6 | 3 / 0 | 0.2500 |
| `hc_x3` | +3.6 | +4.0 | 2 / 0 | 0.5000 |
| `hc_x2` | +1.8 | +1.4 | 1 / 0 | 1.0000 |

Only the first two are individually significant, and both of those raise false
positives by more than the entire budget the constraint allows. `hc_u_dc` is the
best exchange rate in the grid — **+18.2 points of recall for +10.8 points of
false positives, 10 discordant pairs with none pointing back** — and it still
flags 1 correct solution in 6.

**Not beating it at all: six.** `cheap_hc_x3` (−3.6), `tri_majority` (−5.5), `hs`
(−7.3), `hc_x3_maj` (−7.3), `cheap_hc` (−9.1), `tri_unanimous` (−16.4).

### The three results inside that table worth naming

**1. Voting is destructive, not selective — again.** Majority-of-3 over three
*different* architectures removes 1.4 points of false positives and 5.5 points of
recall. Unanimity removes 5.4 points of false positives and **16.4** points of
recall, at 4× the cost of the shipped single reader, and drops to **7 of 15** on
code that does not even run. This is study 2's two-stage filter result reproduced
by a different mechanism: **the second reader cannot tell the first reader's good
findings from its bad ones, so requiring agreement taxes true findings and false
ones at about the same rate.** Combined with study 2's finding, agreement filters
have now failed in this harness three separate ways.

**2. The cheap tier does not pay, which contradicts the cost argument in the
design doc.** `AUDIT_ARCHITECTURE.md` §4 argues detection is the cheaper half of
the problem, so "the detectors need not be the expensive model". Measured:
**`cheap_hc_x3` costs 1.9× the shipped architecture and finds less** — 16.4%
against 20.0%, with 9.5% false positives against 6.8%. It is one of only two
dominated specs in the grid. Three cheap reads are not a substitute for one good
one here. The cheap reader is not merely a weaker version of the expensive one
either: of the 6 defects `cheap_hc` catches on the confirm half, 2 are ones the
shipped auditor misses — so it is partially complementary, and complementary in
the direction that costs false positives.

**3. Complementarity is real and is not free.** On the confirm half's 55 P
instances: **4 defects seen only by `hc`, 2 only by `hs`, 9 only by `dc`, 2 by all
three, 23 by their union, 32 by nothing.** Study 2's 18/8/8 pattern reproduces in
shape. But the union that captures it flags **a third of all correct code**, and
that is the whole content of this study's answer: the complementarity study 2
identified as "the finding worth pursuing" was pursued, in every combination the
existing records allow, and **it does not convert into a usable architecture under
a false-positive constraint the product can live with.**

---

## The noise floor is wider than the record has been saying

This study ran the shipped architecture three times over all 290 instances — the
same configuration, the same bytes, the same constitution — which is the replicate
arm `EXPERIMENT_RECORD.md` §4 requires, on exactly this study's estimand and n.

| population | draw 1 | draw 2 | draw 3 | widest pair |
|---|---:|---:|---:|---:|
| confirm P (n = 55) | 11 | 7 | 6 | **9.1 pts** |
| explore P (n = 55) | 5 | 5 | 3 | 3.6 pts |
| all P (n = 110) | 16 | 12 | 9 | **6.4 pts** |
| confirm C (n = 74) | 5 | 5 | 4 | 1.4 pts |
| all C (n = 150) | 5 | 7 | 5 | 1.3 pts |
| batch 1 P (n = 56) | 7 | 6 | 5 | 3.6 pts |
| batch 2 P (n = 54) | 9 | 6 | 4 | **9.3 pts** |

**The preregistered 1.8-point floor is the narrowest of the available pairwise
comparisons, not the floor.** It comes from study 2 comparing two of these three
draws on batch 1 (7 vs 6). The third draw on the same 56 instances gives 5, so the
widest pair on batch 1 is 3.6 points; on batch 2, which this study measured for
the first time, the widest pair is 9.3 points. On the confirm half at n = 55 the
same architecture scores anywhere from 6 to 11 of 55.

Two consequences, and both cut against finding anything:

- **Every difference in the table above except `tri_union`'s and `hc_u_dc`'s is
  inside the run-to-run spread of the shipped detector itself.** The negative
  result is therefore robust to the floor and the positive ones mostly are not.
- **The 1.8-point figure should not be quoted again without its estimand.** It is
  one pairwise difference on one batch. This study's own three draws are the wider
  and better-supported measurement, and they are consistent with D154: pooled
  rates reproduce far better than the per-instance verdicts underneath them.

The C column is the reassuring half: 5, 5, 4 of 74 on the confirm half and 5, 7, 5
of 150 overall. **The false-positive rate is the stable measurement in this
harness, and it is also the one the constraint is written on.**

---

## The explore half, reported once and carrying no claim

| spec | explore P-recall | explore C-FP |
|---|---|---|
| `tri_union` | 32.7% (18/55) | 28.9% (22/76) |
| `hs_u_dc` | 30.9% (17/55) | 28.9% (22/76) |
| `hc_u_hs` | 23.6% (13/55) | 25.0% (19/76) |
| `hc_u_dc` | 23.6% (13/55) | 7.9% (6/76) |
| `dc_x2` | 23.6% (13/55) | 11.8% (9/76) |
| `cheap_hc_x3` | 21.8% (12/55) | 7.9% (6/76) |
| `dc` | 20.0% (11/55) | 7.9% (6/76) |
| `hs` | 18.2% (10/55) | 25.0% (19/76) |
| **`cheap_hc`** | **14.5% (8/55)** | **2.6% (2/76)** |
| `tri_majority` | 12.7% (7/55) | 3.9% (3/76) |
| `hc_x2` | 12.7% (7/55) | 2.6% (2/76) |
| `hc_x3` | 12.7% (7/55) | 3.9% (3/76) |
| `hc` | 9.1% (5/55) | 0.0% (0/76) |
| `hc_x3_maj` | 5.5% (3/55) | 0.0% (0/76) |
| `tri_unanimous` | 1.8% (1/55) | 0.0% (0/76) |

**The explore half's selection was `cheap_hc`** — highest recall among the seven
specs meeting the constraint there. On the confirm half `cheap_hc` scores 10.9%
(6/55), against the shipped architecture's 20.0%. **The selection did not
replicate, and neither did the ranking**: from the identical records, the shipped
architecture ranks **thirteenth of fifteen** by recall on the explore half and
**ninth of fifteen** on the confirm half, and it is the highest-recall spec
anywhere near the constraint on the confirm half while being the *lowest*-recall
single detector on the explore half.

That disagreement is the most useful methodological observation in this study. At
n = 55 per half, with a base rate near 20%, an eleven-point swing between halves
for the *same* detector is ordinary sampling. **Split-half selection at this n
selects noise.** It was preregistered and it was honoured; it is reported because
it did not work, and a reader planning a similar design should size for it.

---

## What it cost

From the projects' own usage ledgers, per call, not reconstructed.

| work | calls | spend |
|---|---:|---:|
| credential probes (3 routes, one call each) | 3 | $0.0002 |
| `holistic / cheap-cross / draw 1` (290 + 1 retry) | 291 | $1.0668 |
| `holistic / cheap-cross / draw 2` | 290 | $0.7702 |
| `holistic / cheap-cross / draw 3` | 290 | $0.7585 |
| `holistic / cross / draw 2` (the 184 uncovered) | 184 | $1.2638 |
| `holistic / cross / draw 3` (the 184 uncovered) | 184 | $0.5645 |
| **total** | **1,242** | **$4.4241** |

Of $15.00 budgeted, **$4.42 spent** — because ten of the fifteen specs were set
operations over records that already existed. The stopping rule was "grid
exhausted or $15", and the grid was exhausted.

### Repeat draws are much cheaper than K×, and the reason is the prompt cache

`holistic / cross / draw 3` cost **$0.5645 for the same 184 instances draw 2 cost
$1.2638 for** — 45% — with comparable output (172 vs 185 output tokens per call)
and comparable behaviour (0.15 vs 0.16 findings per instance). The ledger says
why: draw 2 billed 301,123 fresh input tokens and 5,055 cached; draw 3 billed
5,527 fresh and **300,651 cached**. The prompts are byte-identical, so the
provider served them from its prompt cache.

**This is a real and reportable property of union-of-K detection: K identical
reads do not cost K×.** It is also why the `hc_x2` and `hc_x3` costs above are
lower than three times `hc`'s, and it is the one place the design doc's cost
argument survives — though it survives attached to an architecture (`hc_x3`) that
buys 3.6 points of recall, inside the noise floor, for 2.7× the money and 4.0
points of false positives.

---

## Deviations from the plan, numbered, with the direction of each bias

1. **The split is 55/55 on P, not "~28 P per half".** The brief's two
   specifications of the split were inconsistent — "the 110 instances" and "~28 P
   per half" cannot both hold. The larger reading was taken: all 110 P instances
   split 55/55, all 150 C split 76/74, all 30 F split 15/15. The stratification is
   on `(stratum, batch)`, so each half does receive ~28 P from each batch, which
   is the reading under which both statements are true. Effect: larger n per half
   than the alternative, so the conservative direction.
2. **Study 1's `cross` and `cross-replicate` arms supply draws 2 and 3 on batch 1
   only; batch 2's draws 2 and 3 were run here.** Draw 2 is therefore not one
   homogeneous arm: 106 instances were audited on 2026-09-04 at study 1's commit,
   184 on 2026-09-05 at this study's. Both are `run_audit` with the same route,
   the same constitution and no deterministic layer, and batch 1's solutions are
   byte-identical (540/540 sha256). It could bias the `hc_x2`/`hc_x3` specs in
   either direction; the batch-split noise-floor table above is the evidence
   available on it, and it shows batch 2 spreading wider than batch 1.
3. **A transient SSL EOF on the first invocation tripped the provider circuit
   breaker**, which cooled down for 60 s and failed 274 queued instances of
   `cheap-cross / draw 1` in seconds. No record was cached for a failed instance,
   so nothing was scored from them; the loop was given bounded retry passes and
   every instance was subsequently completed. The failures are recorded in
   `records/explore/cache/*.failed.jsonl` (275 + 16 + 14 rows, all
   `circuit_open` or one SSL EOF). **No instance is missing from any spec: every
   detector covers all 290.** No bias, but it is why the first invocation's
   partial output was discarded.
4. **Concurrency was reduced from 5 to 3 workers** after deviation 3. Wall time
   only; no call sees another's prompt or reply.
5. **Cost for `hc_x2`, `hc_x3` and `hc_x3_maj` is part-reconstructed.** Study 1's
   committed rows carry no per-row cost, so its 106 instances are priced at study
   1's arm total ÷ 235 calls. Marked at every occurrence with †.
6. **`hc_x2`/`hc_x3` costs are prompt-cache-warm** (see above), so they understate
   what K independent draws would cost in a deployment that did not run them
   back-to-back. This makes the repeat-draw specs look *cheaper* than they would
   be, which is the anti-conservative direction — and they still lose.
7. **The same-vendor bypass is inherited but unused.** `explore.py` leaves
   `generator:` unset when the auditor's vendor equals the generator's, exactly as
   studies 1 and 2 did for their `self` arms. No detector in this grid needed it:
   the only `self` detector used is study 2's existing record. `src/` is untouched.
8. **`checks` (the deterministic layer alone) is not a spec.** It flags 0/110 on P
   by construction. Reported as context; excluded from the grid and from every
   count.
9. **The leaderboard was re-scored once with `--force`** after the cost
   attribution was corrected to blend per-row ledger costs with reconstructed ones
   rather than reconstructing a whole detector. Scoring is free and reads only
   cached records; no flag changed.
10. **Two additional free draws exist and were not used.** Study 1's `self` arm is
    a second draw of `holistic-self` on batch 1. It is wired into the loop's
    source table but no preregistered spec names it, and none was added after the
    fact.
11. **`manifest.json` cannot record its own commit.** It is written by the loop and
    then committed, so its `code.commit` names the commit that existed when it was
    written and its `status_porcelain` is non-empty (it lists the study's own
    staged records). The meaningful freeze is the separate `frozen_at` field:
    **`54b3d5c`, the commit that carried the preregistration and the grid, made
    before the first model call including the probe.** That commit's tree is clean
    and is the one a reader should check the plan against.
12. **Phase 2 was skipped.** Its kill condition fired (13/56 against a bar of 19);
    `RESULTS-CHECKS.md` existed at the time this grid finished and confirms it.
    No second grid was built, exploratory or otherwise.

## Limitations, stated here rather than left to the reader

- **Split-half selection at n = 55 does not work, and this study demonstrates it
  on itself.** The explore half and the confirm half select different specs and
  rank the shipped architecture nine places apart. Treat every per-half point
  estimate as having an interval about twelve points wide, because they do.
- **The measured run-to-run spread of the shipped detector (up to 9.1 points on
  the confirm half's P stratum) is larger than every effect in this study except
  two.** The negative conclusion survives that; no positive conclusion here would.
- **Composition is over verdicts, not evidence.** A union here unions flags. A
  product would have to show a reviewer the union of the *findings*, which costs
  more than the model spend priced above — and the false-positive columns are what
  that reviewer would experience.
- **Fifteen specs, one grid, one selection.** The primary outcome was named before
  any spec was scored, but the objective ranges over all fifteen. This project has
  now run seven studies over two tasks; that history is part of the
  multiple-comparison picture, and the two significant contrasts here
  (`tri_union`, `hc_u_dc`) are the two largest of fifteen.
- **Everything `RESULTS-2.md` lists is inherited unchanged**: two Python
  benchmarks of short self-contained functions are not a repository; one generator
  is one generator; vendor independence is not statistical independence; pooled
  instances are not fully independent; round one only.
- **`cheap-cross` is one cheap model.** "The cheap tier does not pay" is a claim
  about `gpt-5.6-luna` on this corpus, not about cheap models.

## What this run does and does not license

**It licenses**: that on this corpus, under a false-positive constraint set by the
shipped architecture's own measured bound, **none of fifteen compositions of the
detectors available to this harness improves on the shipped architecture**, and
that the recall available above it is bought at a false-positive price that scales
with it. It licenses the negative on agreement filtering a third time, and the
negative on cheap-tier detection for the first time.

**It does not license** the claim that no better audit architecture exists. It
searched compositions of three detector kinds over three routes. It did not change
what the auditor is told to look for — and `AUDIT_ARCHITECTURE.md` §1 records that
the one large mover in this programme's history was exactly that, splitting the
rules, which moved the referent rather than the architecture. **This study is
evidence that the architecture is not the lever, which is the same thing study 2
said, said again over eight more architectures.**

**It does not license** shipping `hc_u_dc` on the strength of its exchange rate.
Its 17.6% false-positive rate is 2.6× the shipped architecture's, on the
population that decides whether anyone keeps the tool.

### Where this sits beside the phase-2 result

The check pre-test killed *"the model states what the evidence will say"*. What
survives there is *"the model names evidence and code verifies the evidence
exists"* — A4's `governed_source_ids` with `check_source_provenance`. **Every spec
in this grid is on the surviving side of that line**: the grid varies who looks and
how their findings are combined, and never asks a model to supply a truth value.
Ground truth throughout is a hidden test suite passing or failing.

So the two studies fit together without contradiction, and the joint conclusion is
narrower than either alone: **the model rung's detection is not improved by
recombining it, and its adjudication cannot be made deterministic by asking it for
assertions.** Neither result touches the rung order, the kernel, or the receipt.

---

## Reproduction

```sh
export PYTHONPATH="$(git rev-parse --show-toplevel)/src"
# credentials: CROSSAUDIT_ANTHROPIC_KEY and CROSSAUDIT_OPENAI_KEY
# study 2's run dir supplies the solutions and the property cache; the corpus is
# not redistributed (see manifest_corpus.json) — python benchmarks/code/fetch.py
python benchmarks/code/explore.py --probe --scratch /tmp/explore-arms
python benchmarks/code/explore.py --run benchmarks/code/runs/study2 \
    --scratch /tmp/explore-arms --budget-usd 15 --workers 3
python benchmarks/code/report_explore.py
```

The loop is resumable and idempotent: re-running it re-runs no detector that has a
cached record and re-scores no spec already on the leaderboard. Running it now,
with `records/explore/cache/` present, costs **$0.00** and reproduces every number
in this file. It will not reproduce byte-identically from an empty cache — the
provider layer exposes no seed and the auditor model's capability card carries
`temperature=False` (D154) — and the noise-floor table above quantifies what that
costs.

The committed record is `benchmarks/code/records/explore/`: `split.json`,
`leaderboard.jsonl` (one row per spec), `rows.jsonl` (one row per spec × instance),
`cache/*.jsonl` (one row per detector × instance), `cache/*.failed.jsonl`,
`numbers.json` and `manifest.json`. **No corpus text, no solutions, no finding
prose, and no prompt that embeds any of them** — the loop drops `blocker_texts`
and per-property evidence before writing, and a scan of every committed row found
no free-text field. The scratch projects, which do contain solution bytes, are
archived outside the repository at
`~/Documents/Crossaudit/study-data/wt-explore-runs/` with a per-file sha256
manifest at `MANIFEST.sha256`
(`523e21aeaffb4a2b188b9a834e15e29d067cbb18db97d437334d7e6deb1f9172` over the
manifest itself).

## Deviation, recorded after the fact (2026-09-06)

**The preregistration fixed the noise floor at 1.8 points on P and justified it
against the estimand; the study's own three full draws then measured a widest
pair of 6.4 points at n = 110 (9.1 on the confirm half), and `CORRECTIONS.md`
item 12 restates the floor accordingly.** The selection rule was executed
against 1.8. That cannot be un-run. What it means for this report: the
"beats the shipped architecture by more than the noise floor" test was applied
with too small a floor, so any spec it admitted on a margin between 1.8 and 6.4
points would have been admitted wrongly. None was — every spec inside the
false-positive constraint had *lower* recall than the shipped architecture, and
the two that beat it outside the constraint did so by +18.2 and +21.8 points —
so the conclusion stands under either floor. Recorded here because a floor
superseded in the corrections file and not in the study that used it would
be repeated.
