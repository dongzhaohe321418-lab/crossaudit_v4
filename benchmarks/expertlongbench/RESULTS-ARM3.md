# Arm 3 — the two addressing contracts, run against each other

Study 8. Preregistered at `benchmarks/expertlongbench/study8/PREREGISTRATION-ARM3.md`,
committed at `785bd9e` **before any study model call**. n = **24 T03 instances × 2
contracts = 48 drafts**, the same 24 as Arm 2 (batch 1 = 16, seed 20261104; batch
2 = 8). Generator `anthropic:claude-sonnet-4-6`, auditor `openai:gpt-5.6-terra`,
one round each, `checks: ["number_source"]`, one skill variant per arm written
verbatim from `study8/SKILL_A.md` / `SKILL_B.md`, nothing under `src/` modified.
All 48 drafts completed; the receipt's `inputs.manifest` equals the reconstructed
increment on **48 of 48**. Total spend **$3.0162** of a $4 budget ($3.0160 the 48
measured drafts, $0.0002 the credentials probe).

D158 sent the addressing half of the contract back to design because the
generator could not address lines it is never shown. Both replacements work.

---

## 1. The §8g disposition, per arm, and the decision

> **Of the BLOCKABLE annotation rows whose named location genuinely contains the
> transcribed `(v, u)` pair — adjudicated by a deterministic re-read of that
> location, never by a model — the fraction the arm's verifier BLOCKS.**

| arm | false-blocker rate | 95% Wilson score interval for that binomial proportion of annotation rows | draft-clustered 95% percentile bootstrap, 10,000 resamples of the 24 drafts | **§8g** |
|---|---|---|---|---|
| **A — numbered rendering** | **0 of 183 = 0.00%** | **0.00–2.06%** | 0.00–0.00% | **PASS** |
| **B — content addressing** | **2 of 167 = 1.20%** | **0.33–4.26%** | 0.00–2.98% | **PASS** |

The rule fixed before either arm ran — *kill if the interval's lower bound
exceeds 2%; pass only if the upper bound is below 5%; anything between is
inconclusive* — reads **PASS** on both: A's upper bound is 2.06%, B's is 4.26%.
Arm 2's rate on the same estimand was 7 of 7 = 100% (Wilson 64.57–100.00%).

**Both of B's two false blockers are the 80-character cap, and nothing else.**
They are quotes of **97 and 104 characters** that the named file does contain,
exactly, once, and that do contain the transcribed pair. Neither is a defect of
content addressing; both are the contract's own length rule refusing a correct
annotation. Quoted as the count, per EXPERIMENT_RECORD §9: **2 of 167, from 2 of
24 drafts**. Arm A produced **no false blocker of any kind**, and neither arm
produced one that was a verifier error about a span.

### 1.1 The decision under the preregistered rule

The rule, written in §8 of the preregistration before the run: prefer the arm
that passes; **if both pass, prefer the higher resolved fraction unless the
difference lies inside the paired interval**, in which case the study does not
separate them and the recommendation falls to the design's standing argument.

Both passed. A resolves 87.56% of blockable rows and B 85.94%; paired by
instance the mean difference is **+2.5 points in A's favour, 95% paired
percentile bootstrap −1.3 to +6.9 points** (§4). **The difference lies inside the
interval.** The preregistered rule therefore hands the decision to
`PROVENANCE_ADDRESSING.md` §7 — and §7's single stated condition for reversing
itself did not occur (§5).

**Build B, with one change the data require: the 80-character cap must not
raise a BLOCKER.** See §8.

## 2. Rows resolved, beside the simulated ceilings

The design's §3 predictions were made from Arm 2's archive with no new
generation. These are their measured counterparts.

| | denominator | predicted | measured | 95% Wilson | difference |
|---|---|---|---|---|---|
| **A** — resolved / blockable | 209 | 82.0% | **183 of 209 = 87.56%** | 82.40–91.37% | **+5.6 pts** |
| **B** — resolved / blockable | 192 | 85.5% | **165 of 192 = 85.94%** | 80.31–90.15% | **+0.4 pts** |
| **B** — resolved / addressed | 192 | 77.6% | **165 of 192 = 85.94%** | 80.31–90.15% | **+8.3 pts** |

For arm A, blockable and addressed rows are the same set: A has no
advisory-by-routing disposition other than `uncited`.

Three readings, in order of how much they matter.

**B's prediction was almost exact on the denominator the design said to use.**
85.5% predicted, 85.94% measured — the simulation of contract B was a
measurement of the corpus and the shipped matcher, and it transferred.

**B's two predicted risks both came in at zero.** The design predicted 9.3% of
rows would be ambiguous (the pair on more than one line) and 13.1% would name a
file the pair is not in. Measured: **ambiguity 0 of 192 (95% Wilson 0.00–1.96%)**
and **quote-not-found 0 of 192 (0.00–1.96%)**. A copied quote is longer than a
line and disambiguates itself, which the line-based simulation could not see.
That is why B's measured rate over *addressed* rows beat its own 77.6% ceiling:
the ceiling assumed 17 rows would be routed away as ambiguous, and none were.

**A beat its own ceiling by 5.6 points.** The design's 82.0% was "what A gets *if*
a writer shown a gutter copies it", and said plainly that nothing in the archive
could prove the writer would. It does: **0 of 209 addressed rows named a line the
named file does not have, 0 named a path outside the increment, and 0 named a
line where the pair sits elsewhere in the same file.** Arm 2's central failure —
a per-draft constant line offset on 15 of 23 measurable drafts, 123 wrong-line
blocks — is **completely absent**. Showing the writer the numbers removed the
whole of it.

Both arms clear `PROVENANCE_CHECKS.md` §6's secondary kill line ("fewer than 80%
of emitted rows resolve and contain"), which Arm 2 failed at 0%.

## 3. Every block, and what caused it

53 blocks over 48 drafts: **26 in arm A** (11 of 24 drafts) and **27 in arm B**
(14 of 24 drafts). The `class` column is the preregistered §10 rule, evaluated in
order, fixed before any block was seen. The last column is a **deterministic
substratum computed after the blocks were seen and therefore exploratory**
(§9.5): it reads what the source actually writes at the named place, because the
preregistered class names could not distinguish six quite different things.

| class (preregistered) | A | B | what it means |
|---|---|---|---|
| `verifier wrong` | 0 | **2** | the location resolves, adjudicator A says it holds the pair, the arm blocked anyway — **both are the 80-character cap** |
| `malformed row` | 0 | 0 | — |
| `outline-replaced file` | 0 | 0 | no file in this corpus was large enough to be outlined |
| `unparsed notation` | 2 | 4 | the unit as transcribed contains a space after the synonym fold, or `_UNPARSED` rejects the notation after the value |
| `ambiguous` | 0 | 0 | advisory by routing; never reached |
| `paraphrase` | 0 | 0 | **B's whole risk, and it did not occur once** |
| `generator wrong file` | 24 | 21 | the pair occurs nowhere in the named file — **every one of the 45 is the second limb of the rule, never the first: no path failed to resolve in either arm** |
| `generator wrong line/quote` | 0 | 0 | **the addressing failure Arm 2 was made of: gone in both arms** |

| substratum (exploratory) | A | B | the source writes … |
|---|---|---|---|
| range or list | 11 | 6 | the source writes `<lo>–<hi> °C`, or `<a>, <b>, <c> wt.%` before one shared unit, and the annotation names a single member |
| stoichiometric subscript | 6 | 5 | the source writes a formula of the shape `LiM<x>N<y>O2` and the annotation names a subscript as a number |
| unit rendered differently | 3 | 7 | `°C min⁻¹` / `dm3/s` against `°C/min` / `dm³/s` |
| unit is a word, not a symbol | 4 | 4 | the unit is an English word (`degrees`) or the quantity is words (`<n> times molar`) |
| hyphenated compound adjective | 1 | 1 | `<n>-cm diameter` — D157's dial, seen from the other side |
| value genuinely absent | 1 | 2 | a transcription the named place does not support |
| over-80-character quote | — | 2 | the cap, on a correct annotation |

**51 of the 53 blocks are neither an addressing failure nor a verifier error.**
They are the containment rule — literal value, whole unit token — meeting a
source that writes ranges, chemical formulae and units in a different notation.
They occur in **the same kinds and nearly the same numbers in both arms**, which
is the strongest evidence in this study that addressing is no longer the binding
constraint: change the addressing contract completely and the residue does not
move.

**This is also the study's sharpest limitation.** Adjudicator A *is* the
containment rule, so a row whose annotation a person would call a fair reading of a
range is adjudicated "the location does not contain the pair" and leaves
the primary's denominator. The primary therefore cannot see these 51, by
construction, and it was preregistered knowing that (§14 of the preregistration).
They are reported here in full rather than left inside a rate.

| arm | instance | address | rule | class | what the source writes there |
|---|---|---|---|---|---|
| A | 10.1002/adfm.202002249 | `work/synthesis/RECIPE.md#L18` | CA-NUM-002 | generator wrong file | formula-subscript |
| A | 10.1002/adfm.202002249 | `work/synthesis/RECIPE.md#L18` | CA-NUM-002 | generator wrong file | formula-subscript |
| A | 10.1002/adfm.202209924 | `work/synthesis/RECIPE.md#L17` | CA-NUM-002 | generator wrong file | value-absent-from-location |
| A | 10.1002/advs.202406453 | `work/synthesis/RECIPE.md#L20` | CA-NUM-002 | generator wrong file | range-or-list |
| A | 10.1002/aic.18378 | `work/synthesis/RECIPE.md#L20` | CA-NUM-002 | generator wrong file | range-or-list |
| A | 10.1002/aic.18378 | `work/synthesis/RECIPE.md#L20` | CA-NUM-002 | generator wrong file | range-or-list |
| A | 10.1002/aic.18378 | `work/synthesis/RECIPE.md#L20` | CA-NUM-002 | generator wrong file | range-or-list |
| A | 10.1002/aic.18378 | `work/synthesis/RECIPE.md#L20` | CA-NUM-002 | generator wrong file | unit-word-not-symbol |
| A | 10.1002/aic.18378 | `work/synthesis/RECIPE.md#L24` | CA-NUM-002 | generator wrong file | range-or-list |
| A | 10.1002/aic.18378 | `work/synthesis/RECIPE.md#L5` | CA-NUM-002 | generator wrong file | formula-subscript |
| A | 10.1002/aic.18378 | `work/synthesis/RECIPE.md#L5` | CA-NUM-002 | generator wrong file | formula-subscript |
| A | 10.1002/batt.202100174 | `work/synthesis/RECIPE.md#L15` | CA-NUM-002 | generator wrong file | range-or-list |
| A | 10.1002/batt.202100174 | `work/synthesis/RECIPE.md#L5` | CA-NUM-002 | generator wrong file | formula-subscript |
| A | 10.1002/batt.202100174 | `work/synthesis/RECIPE.md#L5` | CA-NUM-002 | generator wrong file | formula-subscript |
| A | 10.1002/batt.202200056 | `work/synthesis/RECIPE.md#L17` | CA-NUM-002 | generator wrong file | range-or-list |
| A | 10.1002/batt.202200056 | `work/synthesis/RECIPE.md#L19` | CA-NUM-002 | unparsed notation | unit-rendered-differently |
| A | 10.1002/batt.202200056 | `work/synthesis/RECIPE.md#L19` | CA-NUM-002 | unparsed notation | unit-rendered-differently |
| A | 10.1002/batt.202200056 | `work/synthesis/RECIPE.md#L19` | CA-NUM-002 | generator wrong file | range-or-list |
| A | 10.1002/celc.202200772 | `work/synthesis/RECIPE.md#L9` | CA-NUM-002 | generator wrong file | unit-word-not-symbol |
| A | 10.1002/chem.201905217 | `work/synthesis/RECIPE.md#L13` | CA-NUM-002 | generator wrong file | range-or-list |
| A | 10.1002/cjce.23950 | `work/synthesis/RECIPE.md#L11` | CA-NUM-002 | generator wrong file | range-or-list |
| A | 10.1002/cjce.23950 | `work/synthesis/RECIPE.md#L12` | CA-NUM-002 | generator wrong file | hyphen-compound |
| A | 10.1002/cjce.23950 | `work/synthesis/RECIPE.md#L13` | CA-NUM-002 | generator wrong file | unit-word-not-symbol |
| A | 10.1002/cjce.23950 | `work/synthesis/RECIPE.md#L14` | CA-NUM-002 | generator wrong file | unit-rendered-differently |
| A | 10.1002/cjce.24030 | `work/synthesis/RECIPE.md#L13` | CA-NUM-002 | generator wrong file | range-or-list |
| A | 10.1002/jbm.a.36681 | `work/synthesis/RECIPE.md#L15` | CA-NUM-002 | generator wrong file | unit-word-not-symbol |
| B | 10.1002/adfm.202002249 | `RECIPE.md + 27-char quote` | CA-NUM-002 | generator wrong file | unit-rendered-differently |
| B | 10.1002/adfm.202002249 | `RECIPE.md + 52-char quote` | CA-NUM-002 | generator wrong file | unit-rendered-differently |
| B | 10.1002/adfm.202209924 | `RECIPE.md + 22-char quote` | CA-NUM-002 | generator wrong file | value-absent-from-location |
| B | 10.1002/adfm.202402444 | `RECIPE.md + 14-char quote` | CA-NUM-002 | unparsed notation | unit-word-not-symbol |
| B | 10.1002/adfm.202402444 | `RECIPE.md + 23-char quote` | CA-NUM-002 | generator wrong file | formula-subscript |
| B | 10.1002/adfm.202402444 | `RECIPE.md + 23-char quote` | CA-NUM-002 | generator wrong file | formula-subscript |
| B | 10.1002/adfm.202402444 | `RECIPE.md + 23-char quote` | CA-NUM-002 | generator wrong file | formula-subscript |
| B | 10.1002/advs.202406453 | `RECIPE.md + 21-char quote` | CA-NUM-002 | generator wrong file | unit-word-not-symbol |
| B | 10.1002/aic.18378 | `RECIPE.md + 97-char quote` | CA-NUM-001 | verifier wrong | over-80-char quote |
| B | 10.1002/batt.202100174 | `RECIPE.md + 31-char quote` | CA-NUM-002 | generator wrong file | formula-subscript |
| B | 10.1002/batt.202100174 | `RECIPE.md + 31-char quote` | CA-NUM-002 | generator wrong file | formula-subscript |
| B | 10.1002/batt.202100174 | `RECIPE.md + 9-char quote` | CA-NUM-002 | generator wrong file | range-or-list |
| B | 10.1002/batt.202200056 | `RECIPE.md + 38-char quote` | CA-NUM-002 | generator wrong file | range-or-list |
| B | 10.1002/batt.202200056 | `RECIPE.md + 25-char quote` | CA-NUM-002 | unparsed notation | unit-rendered-differently |
| B | 10.1002/batt.202200056 | `RECIPE.md + 30-char quote` | CA-NUM-002 | unparsed notation | unit-rendered-differently |
| B | 10.1002/batt.202200056 | `RECIPE.md + 42-char quote` | CA-NUM-002 | generator wrong file | range-or-list |
| B | 10.1002/celc.202200772 | `RECIPE.md + 46-char quote` | CA-NUM-002 | generator wrong file | unit-word-not-symbol |
| B | 10.1002/celc.202200772 | `RECIPE.md + 28-char quote` | CA-NUM-002 | unparsed notation | unit-rendered-differently |
| B | 10.1002/chem.201905217 | `RECIPE.md + 24-char quote` | CA-NUM-002 | generator wrong file | range-or-list |
| B | 10.1002/cjce.23950 | `RECIPE.md + 37-char quote` | CA-NUM-002 | generator wrong file | range-or-list |
| B | 10.1002/cjce.23950 | `RECIPE.md + 36-char quote` | CA-NUM-002 | generator wrong file | hyphen-compound |
| B | 10.1002/cjce.24030 | `RECIPE.md + 21-char quote` | CA-NUM-002 | generator wrong file | range-or-list |
| B | 10.1002/jbm.a.36681 | `RECIPE.md + 38-char quote` | CA-NUM-002 | generator wrong file | unit-word-not-symbol |
| B | 10.1002/smll.201800441 | `RECIPE.md + 20-char quote` | CA-NUM-002 | generator wrong file | value-absent-from-location |
| B | 10.1002/smll.201800441 | `RECIPE.md + 104-char quote` | CA-NUM-001 | verifier wrong | over-80-char quote |
| B | 10.1002/smll.201800441 | `RECIPE.md + 15-char quote` | CA-NUM-002 | generator wrong file | unit-rendered-differently |
| B | 10.1002/zaac.202200095 | `RECIPE.md + 28-char quote` | CA-NUM-002 | generator wrong file | unit-rendered-differently |

## 4. A versus B, paired by instance

23 of the 24 pairs enter the comparison. `10.1002/cnma.202200403` wrote **no
annotation block at all** in either arm, so its resolved fraction is undefined on
both sides and the pair is dropped rather than imputed (§9.7).

| | over blockable rows | over addressed rows |
|---|---|---|
| A mean per instance | 88.4% | 88.4% |
| B mean per instance | 85.9% | 85.9% |
| instances A > B / B > A / tied | 6 / 2 / 15 | 6 / 2 / 15 |
| exact McNemar on the discordant pair directions (identical here to the exact paired sign test) | **p = 0.2891** | p = 0.2891 |
| draft-clustered sign-flip randomisation on the paired difference (A−B), 10,000 draws | **+2.5 points, p = 0.2591** | +2.5 points, p = 0.2591 |
| paired percentile bootstrap 95% interval for the mean paired difference (A−B), 10,000 resamples of the 23 instances | **−1.3 to +6.9 points** | −1.3 to +6.9 points |

The pairing is at the **instance**, not the row: the two arms produce different
drafts with different row counts, so no row-level pairing exists. The interval
contains zero and the sign test does not reach significance on 8 discordant
pairs. **This study does not separate the two contracts on the fraction of rows
they resolve.**

On the §8g quantity the arms are not tied — A blocked no correct annotation and B
blocked two — but at these denominators the intervals overlap heavily (A
0.00–2.06%, B 0.33–4.26%) and the whole of B's excess is one fixable rule (§8).

## 5. B's premise, tested directly

`PROVENANCE_ADDRESSING.md` §7 named exactly one thing that would overturn its
recommendation: *evidence that this generator paraphrases rather than copies.* If
byte-exact quote failures ran well above the predicted 13.1% with the excess
attributable to retyped rather than absent text, B's premise would be false.

> **Quotes not found in the named file by exact, whitespace-folded bytes:
> 0 of 192 addressed rows** (95% Wilson score interval for a binomial proportion
> of annotation rows: 0.00–1.96%; draft-clustered bootstrap 0.00–0.00%).
> **Paraphrase rate: 0 of 192.** Every quote the generator wrote was in the file
> it named, character for character under the one whitespace fold, and every one
> of them was there exactly once.

Quote lengths: mean 36 characters, median 36, max 104; **2 of 192 over the
80-character cap**. The generator copies, and it copies short. The condition §7
set for reversing itself did not occur.

Two further behaviours, both preregistered:

* **`uncited` rate.** A **25 of 234 = 10.68%** (95% Wilson 7.34–15.30%); B **14
  of 206 = 6.80%** (4.09–11.08%). Arm 2 measured 14.88% under the shipped skill.
  Neither arm shows the generator opting out wholesale, which is the silent
  failure this secondary exists to catch. B declines less often than A, which is
  consistent with a quote being easier to produce than a line number and is not
  separately tested here.
* **Unit shortening.** The prefix heuristic fires on **1 row in each arm — the
  same annotation in both** (`cjce.24030`, a value inside `(20°C-25°C)`), and
  hand inspection says it is the documented **range-split** unit reading
  (`_unit_candidates`), not a shortened unit. Both rows **passed**. Read
  correctly, **unit shortening is 0 of 209 and 0 of 192**, as Arm 2 found. The
  flag is left in the record uncorrected, with this note.
* **Annotation rate.** A 234 / 577 = 40.6% pooled; B 206 / 553 = 37.3% pooled
  ("numbers present" is Arm 1's `NUM` extractor over the fence-stripped draft, so
  the denominator's blind spots are Arm 1's). Arm 2 measured 36.3%.

## 6. The adjudicators

| arm | rows with a resolvable location | A+B+ | A+B− | A−B+ | A−B− |
|---|---|---|---|---|---|
| A | 209 | 183 | 0 | 23 | 3 |
| B | 192 | 167 | 0 | 19 | 6 |

Agreement is 186 of 209 (89.0%) in arm A and 173 of 192 (90.1%) in arm B. **Every
disagreement is A−B+, every one falls on a blocked row, and all 42 were
hand-inspected**: in each, the naive substring adjudicator found the value's
digits and the unit's characters *separately* inside the located text: the
value's digits inside a range with the unit symbol present at the far end of it,
or a stoichiometric subscript inside a chemical formula, where an empty
transcribed unit imposes no constraint at all. **B is wrong on all 42 and A on none**, exactly as
in Arm 2, so neither arm's denominator is an artefact of using the check's own
containment test: the looser independent test would only have enlarged it. The
sensitivity rate over B's denominator is 23 of 206 = 11.17% (95% Wilson
7.56–16.20%) for arm A and 21 of 186 = 11.29% (7.50–16.64%) for arm B; **§8g's
disposition is not read off it.**

## 7. Cost, and the two things it says

From the product's own usage ledger, per draft, not reconstructed.

| | arm A | arm B |
|---|---|---|
| money per draft, mean / median | **$0.0606 / $0.0583** | **$0.0651 / $0.0650** |
| total (24 drafts) | $1.4541 | $1.5620 |
| generator / auditor | $1.0676 / $0.3865 | $1.1652 / $0.3968 |
| **first generator prompt, input tokens** (mean) | **4,394** | **4,368** |
| generator output tokens (mean) | 2,050 | 2,138 |
| draft size (chars, mean) | 6,370 | 7,108 |
| wall clock, total | 19.6 min | 20.1 min |

**The gutter costs +26 input tokens per prompt, +0.59%.** The design predicted
+32 tokens and +0.7% against one generator prompt from the archive; measured on
live prompts it is +26 and +0.59%. The prediction transferred, and so does the
scaling law behind it: 7 characters per rendered line, 17% of source bytes on
this corpus's 41-character lines, less on longer ones. On this corpus that is
$0.0001 a round; on a project whose scope is a code tree it is the 9–17% the
design priced, paid on every file every round.

**B costs 7.4% more per draft**, +88 generator output tokens on average (the
design projected ≈180) and a longer draft, plus five more corrective re-asks
(below). Neither difference is large and neither was preregistered as a decision
input; both are reported because §5.5 named them.

**The malformed-envelope re-ask did not reproduce.** Arm 2 saw a second
generation call on **23 of 24** rounds, ≈¼ of generator spend. Here: **1 of 24
drafts in arm A and 6 of 24 in arm B — 7 of 48 rounds**. It was not fixed and
nothing in either arm targets it; the plausible cause is that this study's
`checks: ["number_source"]` renders a much shorter deterministic contract than
Arm 2's `science` profile did, but **that is a hypothesis this study did not
test** and the difference between the arms (1 vs 6) is 7 events and should not be
read as a rate. Counted, as §5.9 required, and left alone.

## 8. What should be built

**Contract B — content addressing — with the length cap changed from a blocker to
something that cannot refuse a correct annotation.**

The preregistered rule got the arms to a tie on resolved rows and handed the
decision to `PROVENANCE_ADDRESSING.md` §7, whose argument is unchanged by this
data and is now supported by it:

* B asks the writer only to copy bytes it can see, and this generator copied
  **192 of 192** without a single character's drift. The one thing §7 said would
  overturn its recommendation did not happen.
* B's two predicted weaknesses — ambiguity and absent quotes — measured **0 and
  0**. The 9.3% ambiguity the line-based simulation predicted is an artefact of
  simulating a quote by a line; a real quote is longer and unique.
* A works too, and works better than its own ceiling, but it buys that by
  changing the prompt for the life of the project: 7 characters on every line of
  every file every round, a rule forbidding citation into any outlined file
  (untested here — **no file in this corpus was ever outlined**, so A's known new
  hazard was never exercised and remains unmeasured), and a silent mismatch with
  `file_read`, which returns no gutter. This study measured none of those costs
  because this corpus cannot produce them.
* B collapses §2.1's and §2.3's grammars into one matcher with one mutation set.

**The change the data require.** The 80-character cap is the **entire** measured
false-blocker rate of either contract: 2 of 167, both correct annotations, both
refused for length alone. The design chose 80 because the archive simulation said
it never bound; on live drafts it bound twice in 192 rows (1.04%, 95% Wilson
0.29–3.72%). Two repairs are consistent with the evidence, and the design must
pick one before building:

1. **Route an over-length quote to ADVISORY**, as ambiguity is routed. It is a
   malformed annotation, not a wrong one — both over-cap rows resolved uniquely
   and contained the pair — and this keeps a non-overridable blocker from ever
   firing on a correct transcription. Cost: a writer can evade the span contract
   by quoting the whole file and accepting an advisory. `PROVENANCE_CHECKS.md` §5
   measured what file-scoped citation buys a wrong source: 27.7% coincidental
   containment. Advisory routing does not spend that, because an advisory does
   not pass — it is carried to the auditor.
2. **Raise the cap.** Both offending quotes were ≤ 104 characters and both had a
   shorter unique alternative available in the same line, so the generator
   over-quoted rather than needed the length. A cap of 120–160 would have
   admitted both. Cost: a larger window inside which a coincidental pair can sit,
   unmeasured at any value but 80.

The preregistration does not choose between these and neither does the data;
saying so is the honest end of this study. **Repair 1 is the one consistent with
§3.4's own rule** — only a *named locator* that fails to resolve, or resolves
without containing the value, may block — and a quote that is 97 characters long
is neither.

**And the thing to measure next is not addressing.** 51 of 53 blocks in this
study are the containment rule meeting ranges (17), stoichiometric subscripts
(11), unit re-renderings (10), unit words (8), a hyphenated compound adjective
(2) and three genuinely unsupported transcriptions. They are the same in both
arms. If the next question is "how often does this check refuse an annotation a
domain expert would call correct?", the primary defined here cannot answer it,
because its adjudicator is the containment rule itself. That needs a different
adjudicator and a different preregistration.

## 9. Deviations, numbered

1. **A credentials probe preceded the preregistration commit**: two short
   completions, ≈$0.0002, one per vendor, in a scratch project outside the
   worktree. No corpus row, no study datum. Declared in §13 of the
   preregistration before it was committed.
2. **The first instance's pair was run alone before the rest of batch 1**
   (`--only T03MaterialSEG-10.1002/adfm.201000591`), to confirm the plumbing
   before spending the batch. Same frozen code, same config, same run directory;
   its two records are in `records-b1.jsonl` and are part of the n. It is
   reported because it happened, not because it changed anything.
3. **The block substratum column (§3, second table) is exploratory.** It was
   written after the blocks were seen. The preregistered §10 class was computed
   by the harness before any block was inspected and is what §1 and §3's first
   table use; no disposition, denominator or interval depends on the substratum.
4. **The `unit_shortened` flag fires once per arm on the same annotation and is
   wrong both times** (§5): it is the documented range-split unit reading, not a
   shortened unit. The flag is left uncorrected in `rows.jsonl` and the correction
   is recorded here as data, as Arm 2 recorded its one hand correction.
5. **One pair is excluded from every paired figure.** `10.1002/cnma.202200403`
   emitted no annotation block in either arm, so its resolved fraction is
   undefined on both sides; 23 of 24 pairs enter §4. Direction of any bias:
   unknown and untestable at n = 1.
6. **Arm 2's malformed-envelope re-ask did not reproduce** (§7): 7 of 48 rounds
   here against 23 of 24 there. Not fixed, not targeted, and the cause is not
   established by this study.
7. **`checks: ["number_source"]`, not the `science` profile.** Preregistered in
   §2, so this is not a departure from the plan — it is listed because it is the
   most likely explanation for deviation 6 and for the absence of Arm 2's 48
   incidental `CA-META-001` blockers, and a reader comparing the two studies
   needs it in front of them.
8. **The deterministic-contract sentence differs per arm**, by a committed
   targeted substitution on the shipped `dcl.describe` text (preregistration §2.2;
   `contract-A.txt`, `contract-B.txt`, sha256 in `plan.json`). Preregistered, and
   named here for the same reason as 7: without it each arm's prompt would carry
   a contract contradicting its own skill.

## 10. Limitations

* **One task, one corpus, one vendor pair, one round.** T03MaterialSEG, 24 of 50
  rows, `claude-sonnet-4-6` writing and `gpt-5.6-terra` auditing. A different
  generator may address, or copy, better or worse.
* **The primary's adjudicator is the containment rule itself**, applied to an
  independently resolved location. Without `at`, each arm's disposition and its
  adjudication differ only in *how* the location is resolved, so a near-zero
  false-blocker rate is close to structural and is weak evidence taken alone.
  That is why §2's resolved fractions and §3's block table carry the weight, and
  why §8 says what the next study must adjudicate differently. Stated in §14 of
  the preregistration, before the run.
* **A's known new hazard was never exercised.** Every source file in this corpus
  is 15–25 lines, so `shape_work` outlined nothing (**0 outline-replaced files in
  48 drafts**) and A's rule against citing an outlined file was never tested. A's
  87.56% is a figure for small, fully-rendered sources only.
* **No control arm without an annotation skill**, so the cost the contract *adds*
  is not measured; §7 measures each arm's total and their difference.
* **`max_rounds: 1`.** First-pass annotation behaviour. Whether a second round
  repairs a refused annotation is a different question and is not answered here.
* **Run-to-run variation is unmeasured for this contrast**: no replicate arm
  exists for this estimand, so no difference reported here may be called "inside
  the noise floor".
* **The 51 contract-residue blocks are counted as generator errors** by the
  preregistered classification. Whether a domain expert would agree that
  annotating one endpoint of a range as the value is an error is not a question
  this study asked or can answer.

## 11. Reproduction, records and archive

```sh
export PYTHONPATH=<worktree>/src
set -a && . ~/.crossaudit-keys.env && set +a
cp <corpus>/T03MaterialSEG.jsonl benchmarks/expertlongbench/data/   # gitignored
python3 benchmarks/expertlongbench/study8/test_arm3_verifiers.py
python3 benchmarks/expertlongbench/provenance_arm3.py --batch 1 --out <abs>
python3 benchmarks/expertlongbench/provenance_arm3.py --batch 2 --out <abs>
python3 benchmarks/expertlongbench/provenance_arm3_report.py <abs>
python3 benchmarks/expertlongbench/study8/emit_records.py <abs>
```

* Code frozen at `785bd9e` (`study/provenance-arm3`, branched from
  `fusion/evidence-authority` at `bbceff2`). Python 3.13.5, darwin.
* Corpus `T03MaterialSEG.jsonl` sha256
  `0b525eae93aab406d13e5f90b61afbed575dae7d789e70af6a470a764a2b1af0`, 50 rows,
  CC BY-NC-SA 4.0 — **not redistributed and not committed**.
* Committed records: `study8/rows.jsonl` (440 annotation rows: arm, addresses,
  dispositions, adjudications, occurrence counts, classes, substrata, and
  **sha256 and length of the transcribed value, unit and quote — never the
  text**), `study8/drafts.jsonl` (48 drafts, including each arm-A prompt's gutter
  log), `study8/manifest.json`, `study8/analysis.txt` (the report script's own
  output), `study8/PREREGISTRATION-ARM3.md`, `study8/SKILL_A.md`,
  `study8/SKILL_B.md`, `study8/test_arm3_verifiers.py`. The verifiers' observation
  strings would quote the corpus and are deliberately absent from the records.
* Run directories (model output, which quotes the corpus) archived at
  `~/Documents/Crossaudit/study-data/wt-arm3-runs/arm3/` — 3,227 files,
  4,301,594 bytes, per-file digests in `MANIFEST-SHA256.txt`, directory digest
  `6cfe11f0ab4bc78185e227e8624b19cc70e582f0d61cc00e0cf692734b9ea8f9` in
  `MANIFEST-SHA256.json`.
