# Arm 2 — the generator writes its own number annotations, and the shipped check verifies them

Study 7. Preregistered at `benchmarks/expertlongbench/study7/PREREGISTRATION.md`,
committed at `0ddcc1e` **before any study model call**. n = 24 T03 instances
(batch 1 = Arm 1's own 16, seed 20261104; batch 2 = 8 more under §8's
budget-only pooling rule). Generator `anthropic:claude-sonnet-4-6`, auditor
`openai:gpt-5.6-terra`, one round each, `checks: science`, the shipped
`skills/provenance-numbers.md` written verbatim by
`scaffold.annotation_skill_tree` (sha256 `7bc51d53…`), nothing prompt-engineered
and nothing under `src/` touched. Total spend **$1.8437** of a $4 budget
($1.7782 the 24 measured instances, $0.0653 one diagnostic replay outside the n,
$0.0002 the credentials probe).

**Arm 1 could not make this measurement**: every block it found was its own
probe's extraction error, so the corpus could not separate the verifier's
false-blocker rate from the instrument's (D157). Here the generator wrote the
annotations, and the check that ran is the shipped one — verified twice, not
assumed: the loop's own `cycles/*/checks.json` finding set equals the re-run
check's on **24 of 24** instances, and the receipt's own `inputs.manifest`
equals the reconstructed increment on **24 of 24**.

---

## 1. The primary, and the §8g disposition

> **Of the annotation rows whose `src` locator genuinely contains the
> transcribed (value, unit) pair — adjudicated by a deterministic re-read of the
> named span, never by a model — the fraction the check BLOCKS:
> 7 of 7 = 100%.**
> 95% Wilson score interval for that binomial proportion of annotation rows:
> **64.57–100.00%**. Draft-clustered 95% percentile bootstrap for the same
> proportion, 10,000 resamples of the 24 drafts: 100.00–100.00% (3,571
> resamples discarded for an empty denominator).

**§8g disposition: KILL.** The rule fixed before this arm was run — *kill if the
interval's lower bound exceeds 2%; pass only if the upper bound is below 5%;
anything between is inconclusive* — fires on the lower bound, 64.57% against a
2% line. It is not close and no reading of the data is close: **not one of the
215 annotation rows the generator wrote passed the check**, on any draft.

Two honesty notes that belong in the same breath as that number.

**The denominator is one draft.** All 7 correct-`src` rows come from
`10.1002/cssc.201700885` — the single instance that got its source line numbers
exactly right (modal offset +0). Per EXPERIMENT_RECORD §9 the honest form is the
count: **7 of 7, from 1 of 24 drafts**. The Wilson interval assumes independent
rows and this denominator has one cluster, which is why the clustered bootstrap
is printed beside it and why it degenerates. The *direction* is unambiguous; the
*magnitude* rests on one draft.

**The primary and the block classification disagree, and both are right.** The
primary counts every block landing on a row whose evidence locator is correct,
whatever caused the block. The classification (§4) says **0 verifier false
blockers**: all 7 blocked because the row's OTHER address — `at`, the line of
the generator's own draft where it says it wrote the number — pointed past the
end of that draft, and §10.1 of the preregistration assigns a CA-NUM-001 raised
before any span is read to the generator. So the check was never wrong about a
span; it refused annotations whose evidence claim was correct because the
writer could not count the lines of the file it was writing. §8g is read off the
primary, as preregistered, and the primary is what it is.

### 1.1 The sensitivity analysis (preregistered §5, not a second objective)

Adjudicator **B** is independent of everything in `src/`: exact substring of the
value and of the unit in the named span, no normalisation, no tokenisation. Over
its denominator the block rate is **15 of 15 = 100%** (95% Wilson score interval
for a binomial proportion of annotation rows: 79.61–100.00%). The §8g
disposition is **not** read off it.

Agreement between the two adjudicators on the 183 rows carrying a resolvable
locator: **175 of 183 = 95.6%** — A+/B+ 7, A+/B− 0, A−/B+ 8, A−/B− 168. Every
one of the 8 disagreements was hand-inspected: in all 8 B matched a digit
sitting inside a longer number while the unit's letter turned up separately
elsewhere on the line — a one-digit value "found" inside a three-digit rpm
figure, an `h` "found" inside an ordinary English word. **B is wrong on all 8
and A on none**, so the
primary's denominator is not an artefact of using the check's own containment
test — the looser independent test would only have made it larger.

## 2. Every block, by (instance, at, src, class)

189 blocks over 24 drafts. Classes are the preregistration's §10 rule, fixed
before any block was seen, with the single hand correction named under the table
(the committed rows carry both: `class` as the rule computed it and `class_hand`
as the table shows it) (`L-unresolved` = wrong locator, refused before any
span was read; `L-wrong-line` = the pair is in the named file, on another line;
`transcription` = the pair is nowhere in the named file; `notation` = notation
the check documents that it cannot represent; `hyphen` = D157's open dial;
`VERIFIER` = a verifier false blocker):

| class | count | what it means |
|---|---|---|
| `L-wrong-line` | 123 | the generator named a line of the right file; the pair is on a different line of it |
| `L-unresolved` | 50 | CA-NUM-001 before any span was read — **every one of the 50 is the same cause: `at` points past the end of the generator's own draft** |
| `transcription` | 13 | the pair occurs nowhere in the named file |
| `notation` | 3 | the transcribed unit contains a space, which the check documents it reads as the first token only |
| `hyphen` | 0 | — |
| `VERIFIER` | 0 | — |

| instance | at | src | class |
|---|---|---|---|
| 10.1002/adfm.201000591 | #L38 | RECIPE.md#L10 | L-unresolved |
| 10.1002/adfm.201000591 | #L38 | RECIPE.md#L10 | L-unresolved |
| 10.1002/adfm.201000591 | #L43 | RECIPE.md#L10 | L-unresolved |
| 10.1002/adfm.201000591 | #L47 | RECIPE.md#L11 | L-unresolved |
| 10.1002/adfm.201000591 | #L52 | RECIPE.md#L12 | L-unresolved |
| 10.1002/adfm.202002249 | #L11 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/adfm.202002249 | #L11 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/adfm.202002249 | #L17 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/adfm.202002249 | #L29 | RECIPE.md#L12 | L-wrong-line |
| 10.1002/adfm.202002249 | #L29 | RECIPE.md#L12 | L-wrong-line |
| 10.1002/adfm.202002249 | #L29 | RECIPE.md#L12 | notation |
| 10.1002/adfm.202002249 | #L33 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/adfm.202002249 | #L33 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/adfm.202002249 | #L37 | RECIPE.md#L14 | L-unresolved |
| 10.1002/adfm.202402444 | #L19 | RECIPE.md#L8 | L-wrong-line |
| 10.1002/adfm.202402444 | #L23 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/adfm.202402444 | #L23 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/adfm.202402444 | #L27 | RECIPE.md#L12 | L-wrong-line |
| 10.1002/adfm.202402444 | #L27 | RECIPE.md#L12 | L-wrong-line |
| 10.1002/adfm.202402444 | #L27 | RECIPE.md#L12 | transcription |
| 10.1002/adfm.202402444 | #L31 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/adfm.202402444 | #L31 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/adfm.202402444 | #L35 | RECIPE.md#L14 | L-wrong-line |
| 10.1002/adfm.202402444 | #L35 | RECIPE.md#L14 | L-wrong-line |
| 10.1002/adfm.202402444 | #L35 | RECIPE.md#L14 | L-wrong-line |
| 10.1002/aic.18378 | #L20 | RECIPE.md#L8 | L-wrong-line |
| 10.1002/aic.18378 | #L20 | RECIPE.md#L8 | L-wrong-line |
| 10.1002/aic.18378 | #L24 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/aic.18378 | #L28 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/aic.18378 | #L28 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/aic.18378 | #L32 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/aic.18378 | #L40 | RECIPE.md#L12 | L-wrong-line |
| 10.1002/aic.18378 | #L40 | RECIPE.md#L12 | L-wrong-line |
| 10.1002/aic.18378 | #L60 | RECIPE.md#L16 | L-wrong-line |
| 10.1002/aic.18378 | #L60 | RECIPE.md#L16 | L-wrong-line |
| 10.1002/aic.18378 | #L60 | RECIPE.md#L16 | L-wrong-line |
| 10.1002/aic.18378 | #L64 | RECIPE.md#L16 | L-wrong-line |
| 10.1002/aic.18378 | #L68 | RECIPE.md#L16 | L-wrong-line |
| 10.1002/aic.18378 | #L80 | RECIPE.md#L18 | L-wrong-line |
| 10.1002/aic.18378 | #L76 | RECIPE.md#L18 | L-wrong-line |
| 10.1002/ange.202112688 | #L28 | RECIPE.md#L9 | L-unresolved |
| 10.1002/ange.202112688 | #L28 | RECIPE.md#L10 | L-unresolved |
| 10.1002/ange.202112688 | #L33 | RECIPE.md#L9 | L-unresolved |
| 10.1002/ange.202112688 | #L33 | uncited | L-unresolved |
| 10.1002/ange.202112688 | #L39 | RECIPE.md#L10 | L-unresolved |
| 10.1002/ange.202112688 | #L39 | uncited | L-unresolved |
| 10.1002/asia.202100022 | #L17 | RECIPE.md#L7 | L-wrong-line |
| 10.1002/asia.202100022 | #L17 | RECIPE.md#L7 | L-wrong-line |
| 10.1002/asia.202100022 | #L23 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/asia.202100022 | #L23 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/asia.202100022 | #L31 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/batt.202200056 | #L19 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/batt.202200056 | #L19 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/batt.202200056 | #L19 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/batt.202200056 | #L26 | RECIPE.md#L14 | L-wrong-line |
| 10.1002/batt.202200056 | #L31 | RECIPE.md#L15 | L-wrong-line |
| 10.1002/batt.202200056 | #L38 | RECIPE.md#L16 | L-wrong-line |
| 10.1002/batt.202200056 | #L38 | RECIPE.md#L16 | L-wrong-line |
| 10.1002/batt.202200056 | #L38 | RECIPE.md#L16 | L-wrong-line |
| 10.1002/batt.202200056 | #L38 | RECIPE.md#L16 | L-wrong-line |
| 10.1002/batt.202200056 | #L44 | RECIPE.md#L17 | L-wrong-line |
| 10.1002/batt.202200056 | #L44 | RECIPE.md#L17 | L-wrong-line |
| 10.1002/batt.202200056 | #L50 | RECIPE.md#L18 | L-unresolved |
| 10.1002/batt.202200056 | #L50 | RECIPE.md#L18 | L-unresolved |
| 10.1002/batt.202200056 | #L50 | RECIPE.md#L18 | L-unresolved |
| 10.1002/batt.202200056 | #L50 | RECIPE.md#L18 | L-unresolved |
| 10.1002/batt.202200056 | #L50 | RECIPE.md#L18 | L-unresolved |
| 10.1002/celc.202200772 | #L7 | RECIPE.md#L8 | transcription |
| 10.1002/celc.202200772 | #L11 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/celc.202200772 | #L15 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/celc.202200772 | #L15 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/celc.202200772 | #L19 | RECIPE.md#L12 | notation |
| 10.1002/celc.202200772 | #L19 | RECIPE.md#L12 | L-wrong-line |
| 10.1002/celc.202200772 | #L23 | RECIPE.md#L12 | L-wrong-line |
| 10.1002/cjce.24030 | #L9 | RECIPE.md#L8 | L-wrong-line |
| 10.1002/cjce.24030 | #L9 | RECIPE.md#L8 | L-wrong-line |
| 10.1002/cjce.24030 | #L17 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/cjce.24030 | #L17 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/cjce.24030 | #L17 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/cjce.24030 | #L17 | RECIPE.md#L9 | transcription |
| 10.1002/cjce.24030 | #L17 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/cjce.24030 | #L23 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/cjce.24030 | #L23 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/cjce.24030 | #L23 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/cjce.24030 | #L29 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/cjce.24030 | #L45 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/cjce.24030 | #L45 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/cjce.24030 | #L45 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/cjce.24030 | #L51 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/cnma.202200403 | #L62 | uncited | L-unresolved |
| 10.1002/cnma.202200403 | #L62 | uncited | L-unresolved |
| 10.1002/cnma.202200403 | #L66 | uncited | L-unresolved |
| 10.1002/cnma.202200403 | #L66 | uncited | L-unresolved |
| 10.1002/cssc.202300809 | #L47 | RECIPE.md#L11 | L-unresolved |
| 10.1002/cssc.202300809 | #L47 | RECIPE.md#L11 | L-unresolved |
| 10.1002/cssc.202300809 | #L53 | RECIPE.md#L13 | L-unresolved |
| 10.1002/cssc.202300809 | #L53 | RECIPE.md#L13 | L-unresolved |
| 10.1002/cssc.202300809 | #L38 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/cssc.202300809 | #L41 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/cssc.202300809 | #L33 | RECIPE.md#L8 | L-wrong-line |
| 10.1002/jbm.a.36681 | #L9 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/jbm.a.36681 | #L9 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/jbm.a.36681 | #L9 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/jbm.a.36681 | #L13 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/jbm.a.36681 | #L17 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/jbm.a.36681 | #L21 | RECIPE.md#L12 | transcription |
| 10.1002/jbm.a.36681 | #L21 | RECIPE.md#L12 | L-wrong-line |
| 10.1002/jbm.a.36681 | #L25 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/jbm.a.36681 | #L25 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/jbm.a.36681 | #L25 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/smll.201800441 | #L37 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/smll.201800441 | #L43 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/smll.201800441 | #L47 | RECIPE.md#L11 | notation |
| 10.1002/smll.201800441 | #L51 | RECIPE.md#L11 | L-unresolved |
| 10.1002/smll.201800441 | #L63 | RECIPE.md#L13 | L-unresolved |
| 10.1002/smll.201800441 | #L63 | RECIPE.md#L13 | L-unresolved |
| 10.1002/smll.201800441 | #L63 | RECIPE.md#L13 | L-unresolved |
| 10.1002/smll.201800441 | #L67 | RECIPE.md#L13 | L-unresolved |
| 10.1002/smll.202408072 | #L27 | RECIPE.md#L8 | L-wrong-line |
| 10.1002/smll.202408072 | #L35 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/smll.202408072 | #L35 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/smll.202408072 | #L47 | RECIPE.md#L10 | L-unresolved |
| 10.1002/smll.202408072 | #L53 | RECIPE.md#L10 | L-unresolved |
| 10.1002/zaac.202200095 | #L6 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/zaac.202200095 | #L6 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/zaac.202200095 | #L6 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/zaac.202200095 | #L44 | RECIPE.md#L14 | L-wrong-line |
| 10.1002/zaac.202200095 | #L44 | RECIPE.md#L14 | transcription |
| 10.1002/zaac.202200095 | #L44 | RECIPE.md#L14 | L-wrong-line |
| 10.1002/zaac.202200095 | #L38 | RECIPE.md#L12 | L-wrong-line |
| 10.1002/zaac.202200095 | #L33 | RECIPE.md#L14 | transcription |
| 10.1002/zaac.202200095 | #L40 | RECIPE.md#L14 | L-wrong-line |
| 10.1002/zaac.202200095 | #L44 | RECIPE.md#L14 | transcription |
| 10.1126/sciadv.adj5431 | #L46 | RECIPE.md#L13 | L-wrong-line |
| 10.1126/sciadv.adj5431 | #L46 | RECIPE.md#L14 | L-wrong-line |
| 10.1126/sciadv.adj5431 | #L51 | RECIPE.md#L13 | L-wrong-line |
| 10.1126/sciadv.adj5431 | #L51 | RECIPE.md#L13 | L-wrong-line |
| 10.1126/sciadv.adj5431 | #L35 | RECIPE.md#L10 | L-wrong-line |
| 10.1126/sciadv.adj5431 | #L40 | RECIPE.md#L11 | L-wrong-line |
| 10.1126/sciadv.adj5431 | #L40 | RECIPE.md#L11 | L-wrong-line |
| 10.1126/sciadv.adj5431 | #L40 | RECIPE.md#L11 | L-wrong-line |
| 10.1126/sciadv.adj5431 | #L46 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/adfm.202209924 | #L43 | RECIPE.md#L13 | L-wrong-line |
| 10.1002/adfm.202209924 | #L49 | RECIPE.md#L15 | L-unresolved |
| 10.1002/adfm.202209924 | #L55 | RECIPE.md#L16 | L-unresolved |
| 10.1002/adfm.202209924 | #L33 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/advs.202406453 | #L37 | RECIPE.md#L11 | transcription |
| 10.1002/advs.202406453 | #L37 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/advs.202406453 | #L41 | RECIPE.md#L12 | L-unresolved |
| 10.1002/advs.202406453 | #L55 | RECIPE.md#L14 | L-unresolved |
| 10.1002/advs.202406453 | #L55 | RECIPE.md#L14 | L-unresolved |
| 10.1002/anie.201812472 | #L36 | RECIPE.md#L11 | L-unresolved |
| 10.1002/anie.201913331 | #L7 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/anie.201913331 | #L7 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/anie.201913331 | #L7 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/anie.201913331 | #L7 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/anie.201913331 | #L35 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/anie.201913331 | #L23 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/anie.201913331 | #L29 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/batt.202100174 | #L11 | RECIPE.md#L4 | transcription |
| 10.1002/batt.202100174 | #L11 | RECIPE.md#L4 | transcription |
| 10.1002/batt.202100174 | #L43 | RECIPE.md#L12 | L-unresolved |
| 10.1002/batt.202100174 | #L43 | RECIPE.md#L12 | L-unresolved |
| 10.1002/chem.201905217 | #L35 | RECIPE.md#L11 | L-unresolved |
| 10.1002/chem.201905217 | #L29 | RECIPE.md#L9 | L-unresolved |
| 10.1002/chem.201905217 | #L29 | RECIPE.md#L9 | L-unresolved |
| 10.1002/cjce.23950 | #L9 | RECIPE.md#L8 | transcription |
| 10.1002/cjce.23950 | #L9 | RECIPE.md#L8 | L-wrong-line |
| 10.1002/cjce.23950 | #L9 | RECIPE.md#L8 | L-wrong-line |
| 10.1002/cjce.23950 | #L17 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/cjce.23950 | #L17 | RECIPE.md#L9 | transcription |
| 10.1002/cjce.23950 | #L17 | RECIPE.md#L9 | L-wrong-line |
| 10.1002/cjce.23950 | #L23 | RECIPE.md#L10 | L-wrong-line |
| 10.1002/cjce.23950 | #L29 | RECIPE.md#L10 | transcription |
| 10.1002/cjce.23950 | #L35 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/cjce.23950 | #L41 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/cjce.23950 | #L41 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/cjce.23950 | #L47 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/cjce.23950 | #L47 | RECIPE.md#L11 | L-wrong-line |
| 10.1002/cjce.23950 | #L47 | RECIPE.md#L12 | L-wrong-line |
| 10.1002/cjce.23950 | #L53 | RECIPE.md#L12 | L-wrong-line |
| 10.1002/cjce.23950 | #L53 | RECIPE.md#L12 | L-wrong-line |
| 10.1002/cssc.201700885 | #L37 | RECIPE.md#L13 | L-unresolved |
| 10.1002/cssc.201700885 | #L37 | RECIPE.md#L9 | L-unresolved |
| 10.1002/cssc.201700885 | #L41 | RECIPE.md#L15 | L-unresolved |
| 10.1002/cssc.201700885 | #L41 | RECIPE.md#L15 | L-unresolved |
| 10.1002/cssc.201700885 | #L53 | RECIPE.md#L17 | L-unresolved |
| 10.1002/cssc.201700885 | #L53 | RECIPE.md#L17 | L-unresolved |
| 10.1002/cssc.201700885 | #L61 | RECIPE.md#L19 | L-unresolved |

**Hand inspection.** Every one of the 189 blocks was read against its named
source line and its true location, and every A/B disagreement was read
separately (§1.1). One block's class was corrected by hand and the correction is
recorded as data, not applied silently (`study7/emit_records.py`, `HAND`):
`10.1002/batt.202200056 #L26 → RECIPE.md#L14` was `notation` under §10's rule 4,
whose "the transcribed unit contains a space" clause fires before rule 5 can ask
where the pair is — but `wt %` is in the shipped synonym table and **does**
match, so this block's cause is the wrong line and nothing else. Rule-as-written
counts are 122 / 50 / 13 / 4; the hand-corrected counts in the table above are
123 / 50 / 13 / 3. The correction cannot move the primary, which is computed
from the adjudication and the severity and never from the class.

The other three `notation` blocks are annotations whose unit was written
`°C min⁻¹`. The skill tells the writer in as many words to join such a unit or
write `uncited`; the generator wrote it with the space anyway, and the check
cannot match it at any line. Those three are the contract's documented limit
meeting a writer that did not follow the instruction, not a verifier error.

## 3. Why the blocks happened: the generator can count neither file

Two mechanical failures produce 173 of the 189 blocks, and neither is about
evidence.

**The `src` line index is off by a constant, per draft.** Of the 183 rows
carrying a span locator, the transcribed pair occurs **somewhere in the named
file** on 159 (86.9%) — the generator picks the right file and the right number
and misses the line. The offset (nearest true line − named line) is not noise:
its median is **+4**, and on **15 of 23** drafts with a measurable offset every
single row is off by the *same* constant. The generator is counting the recipe's
content lines and not the file's physical lines. It is never shown line numbers:
`generator.build_prompt` renders the workspace as `--- <path> ---` followed by
the raw bytes (`generator.py:449-450`).

**The `at` line index runs past the end of the draft.** 50 of 215 rows name an
`at` line the generator's own artefact does not have, on **14 of the 24 drafts**
(every row on 4 of them). Those 50 are the CA-NUM-001 blocks. **6 of the 50 are
`uncited` rows** — which matters, because `PROVENANCE_CHECKS.md` §2.1 and §3.4
say `uncited` "never blocks". It does: `_row_findings` validates `at` before it
reaches the `uncited` branch (`numbers.py:406-421`), so a row that declines to
name evidence still blocks if it miscounts its own address. That is defensible
as a malformed row and it contradicts the design text as written; it is a
finding, not a fix.

Three counterfactuals over the 183 span rows, each holding everything else
fixed, to show where the loss sits:

| a check identical except that… | rows that would pass |
|---|---|
| — (as shipped) | **0 of 183** |
| `at` is advisory rather than blocking | 7 of 183 (3.8%) |
| the span is read as the whole named FILE | 123 of 183 (67.2%) |
| both | 159 of 183 (86.9%) |

The middle row is the design's own §5 trade priced on generator-written data:
file-scoping recovers two thirds of these annotations and costs the 27.7%
coincidental-pass rate `PROVENANCE_CHECKS.md` measured — which is why the design
chose the span, and why this arm is a finding about the *writer's addressing*
rather than an argument for widening the check.

## 4. What the generator did when asked to annotate

| quantity | value |
|---|---|
| annotation rows written | 215 over 24 drafts (mean 9.0, median 8, min 1, max 17) |
| numbers present in the prose (Arm 1's `NUM` extractor) | 592 (24.7 per draft; Arm 1 measured 26.9) |
| **annotation rate** | **215 / 592 = 36.3% pooled**; per draft mean 39.1%, median 38.2%, range 6.2–100% |
| **`uncited`** | **32 of 215 = 14.88%** (95% Wilson score interval for a binomial proportion of annotation rows: 10.74–20.26%) |
| rows that PASSED the check | **0 of 215** |
| rows BLOCKED | 189 of 215 = 87.9% |
| rows ADVISORY (`uncited` with a valid `at`) | 26 |
| drafts with at least one blocker | 24 of 24 |
| **unit written shorter than the source's** | **0 of 183 rows with a resolvable locator** |

Two of these deserve their own sentence.

**The `uncited` rate is right where the design predicted.** 14.9%
[10.74, 20.26] against §6's "expect ≈13%" — the generator is not opting out
wholesale, which was the silent failure the secondary existed to catch. It
declines where the design says it should: the 32 `uncited` rows are melting
points, ionic radii and other parametric recall.

**Arm 1's failure did not reappear on the generator's side.** Arm 1's seven
blocks were all its probe writing a unit shorter than the source's (`°C` for
`°C/min`, `10` for `10⁻²`). The generator, given the skill's "in full: `°C/min`,
not `°C`" instruction, did this **zero times in 183 rows** — it wrote `°C/min`,
`K/min`, `dm³/s` and `°C min⁻¹` at full length. The half of the contract the
skill teaches by example, the generator obeys. The half that requires counting
lines, it cannot do.

## 5. The hyphen stratum (D157's open dial)

**0 blocks** of the shape D157 left open — a hyphenated English word after the
unit (`5 g-sample` → `g`). The dial is not exercised by this corpus, and this
arm therefore says nothing about it either way.

One adjacent case is worth recording because it is the same boundary rule seen
from the other side: where a source writes a hyphenated compound adjective —
`<number>-<unit> <noun>` — `unit_token` reads the token as `-<unit>`, so an
annotation transcribing that number with that unit cannot match it. The hyphen
precedes the unit rather than following it. It appears once
(`10.1002/cjce.23950 #L17`), on a row already blocked for naming the wrong line,
and it would still have blocked had the line been right. It is the mirror of
D157's case and belongs in the same product decision.

## 6. Cost

From the product's own usage ledger, per instance, not reconstructed.

| | mean | median | total (24) |
|---|---|---|---|
| all calls | $0.0741 | $0.0732 | **$1.7782** |
| generator | $0.0568 | — | $1.363 |
| auditor | $0.0173 | — | $0.415 |
| generator output tokens | 2,048 | 1,956 | — |
| wall clock | 56 s | — | 22 min |

The annotation block itself is **738 bytes** mean (median 705, max 1,413),
**12.4%** of the rest of the draft — about half the 31% `PROVENANCE_CHECKS.md`
§7 projected, because the generator annotated 36% of the numbers rather than all
of them. **There is no no-skill control arm in this study, so the cost the skill
*adds* is not measured**; what is measured is the total, and the fence's share
of the output.

One cost observation the study did not set out to make. **The loop placed two
generation calls on 23 of the 24 instances**, the first 62–82 output tokens and
no receipt recording any tool evidence. A single instrumented diagnostic replay
(outside the study's n, $0.0653, deviation 6) identified it exactly: the generator's first
reply is malformed and the loop spends its one free corrective re-ask —
`generation_retried · correcting a malformed reply · the MCP tool request
envelope must be the entire reply`. That is ≈$0.014 per round, a quarter of
generator spend, on 96% of rounds, and it means a genuine second malformation in
the same round would have stopped the run with no repair left. It is not an
outcome of this study and it is not caused by the annotation contract as far as
this evidence shows; it is reported because it was seen.

## 7. Should the check remain a blocker, on this evidence?

**No — not in the form measured here.** The reason is not that the verifier is
wrong. On 189 blocks it was wrong about a span **zero** times; against the naive
independent adjudicator it won all 8 disagreements; its `uncited` routing
behaved as designed; its unit rule held the generator to full units and the
generator complied. The check is sound.

The contract around it is not usable. Handed the shipped skill through the
shipped channel, the shipped generator produced **215 annotations of which none
passed**, and **24 of 24 drafts were BLOCKED by the deterministic tier before
any model verdict was reached** — a non-overridable stop on every draft, caused
in 173 of 189 cases by an off-by-a-constant line index in one file and a
miscount of the lines in another. D155's rule is that a model may name evidence
and code may verify it exists; this arm says the naming half is not something
this generator can do at line granularity when it is never shown line numbers.

What that leaves, stated as evidence and not as a change (no `src/` file was
modified in this study):

* the failure is concentrated in **addressing**, not evidence — 86.9% of span
  rows name a file that does contain the pair;
* the two loci are mechanical and separable: `at` (50 blocks, and it blocks
  `uncited` rows the design says can never block) and the `src` line offset
  (123 blocks, a per-draft constant on 15 of 23 drafts);
* §6's own Arm 2 kill condition — "fewer than 80% of emitted rows resolve and
  contain" — also fires, at 0%; the §8g rule and the §6 rule agree.

**Is more n needed?** No. §8g's third branch (inconclusive) is not reached: the
lower bound is 64.57% against a 2% line. The one thing more n of *this*
configuration cannot fix is the width of the primary's interval, because its
denominator needs drafts whose annotations are correct and this configuration
produced one in twenty-four. A study that wanted a tight false-blocker rate on
correct annotations would first have to make correct annotations reachable — by
showing the writer line numbers, or by scoping the locator to something it can
address — and would then be measuring a different contract, which is a new
preregistration and not a larger n of this one.

## 8. Deviations, numbered

1. **A credentials probe preceded the preregistration commit**: two 4-token
   completions, $0.000228, one per vendor, in a scratch project outside the
   worktree. No corpus row, no study datum. Declared in the preregistration §13
   before it was committed.
2. **The §10 classifier's implementation was corrected after the pilot
   instance's 5 blocks had been seen.** As first written it tested only whether
   the locator resolved; §10.1's own parenthesis says the class *is* "exactly
   CA-NUM-001 before any span is read", which includes an `at` outside the
   artefact. The correction restores the preregistered rule rather than changing
   it, moves blocks from `L-wrong-line` to `L-unresolved`, and **cannot move the
   primary**, which never reads the class. Direction of any residual bias: it
   makes the verifier look better in §2's table and does not touch §1.
3. **One hand correction to a block's class** (§2), recorded as data in
   `study7/emit_records.py` with both counts reported.
4. **`run.py`'s `bootstrap_project` was monkeypatched, not edited**, so arm B's
   committed harness keeps its behaviour byte for byte; the patch adds the
   shipped skill file and nothing else.
5. **All 24 records were recomputed offline** (`--reanalyse`) after the pilot,
   because `manifest_agrees` was added mid-study. No model call, no spend: the
   analysis is a pure function of the kept project trees.
6. **One diagnostic replay outside the study's n** ($0.0653, §6's last
   paragraph), to identify the cause of the second generation call. It
   contributes no row to any outcome.
7. **`checks: science` also raised 48 `CA-META-001` (schema) blockers** across
   the 24 audits — two per instance, the science profile's `metadata.yml` /
   `results.json` contract applied to a prose deliverable. It touches no
   `number_source` row, but it means the 24/24 BLOCKED verdicts are not
   attributable to `number_source` alone. `number_source` alone would have
   blocked 24 of 24 regardless.
8. **The draft-clustered bootstrap on the primary discarded 3,571 of 10,000
   resamples** for an empty denominator, because one draft supplies the whole
   denominator. Reported at the interval, per §10.

## 9. Limitations

* **One task, one corpus, one vendor pair, one round.** T03MaterialSEG, 24 of 50
  rows, `claude-sonnet-4-6` writing and `gpt-5.6-terra` auditing. Nothing here
  generalises past that, and a different generator may address lines better or
  worse.
* **The primary's denominator is a single draft** (7 rows). Quoted as the count
  wherever it travels, per EXPERIMENT_RECORD §9.
* **Adjudicator A is the check's own `contains_pair`.** That is why B exists and
  why the agreement table is reported; B, being looser, would only have enlarged
  the denominator, and it was wrong on all 8 rows where they differed.
* **"Numbers present" is the Arm 1 probe's extractor**, chosen so the annotation
  rate is comparable with Arm 1's 26.9 numbers per draft. Its known blind spots
  (superscript powers, compound units) are Arm 1's and are inherited here.
* **No control arm without the skill**, so the cost the annotation contract adds
  is not measured (§6).
* **`max_rounds: 1`.** This measures first-pass annotation behaviour. Whether a
  second round repairs a line index after being told which one was wrong is a
  different question and is not answered here.
* Run-to-run variation is unmeasured for this contrast: no replicate arm exists
  for this estimand.

## 10. Reproduction, records and archive

```sh
export PYTHONPATH=<worktree>/src
set -a && . ~/.crossaudit-keys.env && set +a
cp <corpus>/T03MaterialSEG.jsonl benchmarks/expertlongbench/data/   # gitignored
python3 benchmarks/expertlongbench/provenance_arm2.py --batch 1 --out <abs>
python3 benchmarks/expertlongbench/provenance_arm2.py --batch 2 --out <abs>
python3 benchmarks/expertlongbench/provenance_arm2.py --reanalyse --batch 1 --out <abs>
python3 benchmarks/expertlongbench/provenance_arm2_report.py <abs>
python3 benchmarks/expertlongbench/study7/emit_records.py <abs>
```

* Code frozen at `b1756f5` (`study/provenance-arm2`, branched from
  `fusion/evidence-authority`; provenance slice 1 is `5395cc8` in its history).
  Python 3.13.5, darwin.
* Corpus `T03MaterialSEG.jsonl` sha256
  `0b525eae93aab406d13e5f90b61afbed575dae7d789e70af6a470a764a2b1af0`, 50 rows,
  CC BY-NC-SA 4.0 — **not redistributed and not committed**.
* Committed records: `study7/rows.jsonl` (215 annotation rows: addresses,
  dispositions, adjudications, classes, and **sha256 of the transcribed value
  and unit — never the text**), `study7/drafts.jsonl` (24 drafts),
  `study7/manifest.json`, `study7/analysis.txt` (the report script's own output).
  The check's observation strings quote the values and are deliberately absent
  from the committed records; they are in the archive.
* Run directories (model output, which quotes the corpus) archived at
  `~/Documents/Crossaudit/study-data/wt-arm2-runs/arm2/` — 1,664 files,
  2,249,955 bytes, per-file digests in `MANIFEST-SHA256.txt`, directory digest
  `ff9164205b497639527149288ce4e565a33b1d0b89202651b3c1db6c862163e3` in
  `MANIFEST-SHA256.json`.
