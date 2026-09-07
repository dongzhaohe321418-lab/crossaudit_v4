# Arm 5 — the shipped check, after the containment extensions, on every T03 instance

*Fifth version, after four cross-vendor reviews (the fourth: `…-arm5-astra-round4.md` — "unit-less" and "only T03" were still categorical; Amendment 3). Fourth version, after three cross-vendor reviews (the third: `…-arm5-astra-round3.md` — Arm 4's uncited interval misquoted; the preregistration's census amendment still categorical, now Amendment 2). Third version, after two cross-vendor reviews (the second: `…-arm5-astra-round2.md` — the unit-shortening sentence, the missing intervals, the diff script's count, the preregistration's census rationale). Second version, after the first cross-vendor review (`benchmarks/reviews/2026-09-07-provenance-arm5-astra-round1.md`): the first version's mechanism table quoted short source phrases — the same defect that rejected Arm 4's first review — and is replaced by shapes; the bootstrap now uses the registered seed; the matcher diff reads the quotation; the new class is M12; the start state is stated as recorded.*

Study 8. Preregistered at `benchmarks/expertlongbench/study8/PREREGISTRATION-ARM5.md`,
committed at `38d3d22` **before any study model call** (20 s before the plan was written,
24 s before the first archived model event). n = **50 T03 instances × 1 arm = 50 drafts** —
every corpus row, in corpus order, no seed: the **26 instances of Arm 4** as a replicate of
that arm under the changed matcher and skill, and the **24 instances of Arms 2–3**, on which
the shipped skill had never been run. **Neither stratum is fresh** (D161 ruling 3's second
option). The other six public ExpertLongBench tasks were censused first
(`study8/arm5_census.txt`), and the choice was made on **number density per instance and
unit-bearing numbers**, not on absence: T04's median input carries no number and its
references 19 numbers in all (12 traceable, 26% with a unit); T07 and T08 describe a
molecule or a protein from a structure string, with 39% and 0% of the description's
numbers occurring in the input and 0.1% and 0% carrying a unit; T11's references carry a
median of one number (the label; 47% traceable, 1% with a unit); T06's transcripts write
most numbers in words (median input numbers 0; 16% traceable); T01's reference numbers
are 93% traceable and its inputs are denser in numbers than any task (median 5,067 per
input), but 0.6% of its reference numbers carry a unit the extractor recognises (43 of
6,938, 22 of them percentages) and its instances are 250,000 characters of legal record —
**deferred for shape, cost and unit density.** T03 is the task whose inputs are number-dense
(median 16.5 per input) *and* whose quantities carry units throughout; no other public task
combines the two at that level. Generator `anthropic:claude-sonnet-4-6`, auditor `openai:gpt-5.6-terra`, one
round, `checks: ["number_source"]`, the **shipped** skill, contract and per-row verifier,
matcher blob `620fb3bcc1f57b1888e1cd4b74acd30aa93a10bf` (`numbers.py` at `edda6da`, the merge
of slice 8; Arm 4 ran `8dfd07d9…`, the merge of slice 3). 49 of 50 drafts completed in the
run; one loop produced no deliverable (exit 11, no model spend recorded) and was **retried
once** with the harness's retry flag and completed; the errored record is kept and counted.
The receipt's `inputs.manifest` equals the reconstructed increment on 50 of 50. Spend
**$4.4417** of a $5.00 budget, $0.0888 per draft.

D161 ruling 2 shipped five containment extensions (E5, E6, E1, E2, E3) and ruled M10 out;
ruling 3 asked this arm one question: does the check that now ships block so few correct
annotations that it may enter a default profile?

---

## 1. The §8g disposition, and the decision

> **Among BLOCKABLE annotation rows whose named location genuinely contains the
> transcribed `(v, u)` pair — adjudicated by the frozen gold rule, applied by two labellers
> blinded to each other and to the verdict — the fraction the shipped check BLOCKS.**

| false-blocker rate | 95% Wilson score interval for that binomial proportion of annotation rows | draft-clustered 95% percentile bootstrap, 10,000 resamples of the 50 drafts, seed 20261107 | **§8g** |
|---|---|---|---|
| **4 of 398 = 1.01%** | **0.39–2.56%** | 0.24–1.97% | **PASS** |

The rule fixed before the run — *kill if the interval's lower bound exceeds 2%; pass only
if the upper bound is below 5%; anything between is inconclusive* — reads **PASS**: the
upper bound is 2.56%. Under §9 of the preregistration, **`number_source` may enter the
`science` profile** (D159 ruling 2), in a separate change with its own review; this arm
does not make that change. Arm 4, on the same generator and the matcher of slice 3, read
KILL at 9 of 189 (2.53–8.80%).

**Adjudication.** 57 items on the blinded sheet — every one of the 7 blocks, and 50 of the
394 passes drawn at seed 20261107 — labelled by L1 (the author's session) and L2
(`gpt-6-astra` through `codex exec`, read-only, the sheet and the rule only). **κ = 1.000
on the labels, 57 of 57 agree**; no label adjudication was needed (`study8/L1-arm5.csv`,
`L2-arm5.csv`, `GOLD-arm5.csv`). Rule codes differ on 8 items and L1's are carried; each
difference is named in the gold file's header. The 50 sampled passes are **50 of 50 C**
(Wilson 92.86–100%): the false-pass sensitivity finds nothing, and scaling the passes by
that fraction leaves the denominator at 398.

## 2. The seven blocks, each with its mechanism (shapes only; no source text)

| gold | n | mechanism (`CONTAINMENT_RULE.md` §1) | what happened |
|---|---|---|---|
| C | 2 | **M4** — a hyphen joins the unit to a neighbouring word: in one row between the value and its unit, in the other after the unit (with a tilde before the value) | right by contract ("never split a hyphen"), wrong by the gold; disclosed since Arm 4 and D163 |
| C | 1 | **M9b** — the quoted sentence writes the unit as an English word | the located line also carries the same value in a dash range with the symbol unit, which the quotation excludes; the gold labels the line (its record cites R7) and the check reads the quotation — right by contract, wrong by the rule |
| C | 1 | **M12, new** — a percent sign followed by a two-letter capitalised abbreviation naming the quantity's basis; the boundary rule reads a bare capital as prose and ends the unit at the percent sign | a wrong block: the source writes the unit the generator transcribed (M11 is the gold study's 80-character-cap class, so this is M12) |
| N | 2 | **M1b** — the value is written in words | right |
| N | 1 | **M9a** — the value is continued by a power of ten, which the generator dropped | right |

Every one of Arm 4's **five E1 ranges and one E2 list** is gone: the **four** instances Arm 4
blocked for those shapes carry **no block** in Arm 5 (§5.12). Arm 4's two M10 rows (the
en-dash exponents) also carry no block — the generator wrote those rows differently this
time — so the disclosed M10 limit was not exercised. Of the four wrong blocks, three are
right by the shipped contract and disclosed (M4 ×2, M9b's quotation), and one is a **new
matcher class, M12**, which goes back to the containment design as Arm 4's did.

## 3. What the extensions did on this text (secondary 13)

Every located row re-adjudicated by the Arm 4 matcher blob loaded from git, beside the
shipped one (`study8/arm5_matcher_diff.py`), **under the contract's own reading — the pair
inside the quotation, read in its line** (`_pair_in_quote`): of 401 located rows, **361 pass
under both, 7 block under both, and 33 pass now that blocked under the slice-3 matcher**.
Read on the whole located line instead, the counts are 361 / 6 / 34: the one row that
differs is the M9b block, whose line states the pair outside the quotation. The
extensions moved **33 rows** — 33 of 401 = 8.2% of located rows (Wilson 5.92–11.33%;
draft-clustered bootstrap, seed 20261107, 4.36–12.58%) — on a real generator's output, and
none the other way.

## 4. The two strata (secondary 11), reported and deciding nothing

| stratum | drafts | rows | wrong blocks / (wrong blocks + passes) | Wilson | bootstrap (seed 20261107) | `uncited` | Wilson | bootstrap |
|---|---|---|---|---|---|---|---|---|
| replicate of Arm 4's 26 instances | 26 | 224 | **1 of 199 = 0.50%** | 0.09–2.79% | 0.00–1.60% | 23 of 224 = 10.3% | 6.94–14.94% | 4.76–16.90% |
| the 24 instances new to the shipped skill | 24 | 222 | **3 of 199 = 1.51%** | 0.51–4.34% | 0.00–3.15% | 17 of 222 = 7.7% | 4.84–11.92% | 3.47–13.17% |

Both strata are inside the whole's interval; the replicate reads lower than the whole, the
new stratum higher, and neither alone would read differently from PASS at its own n.

## 5. Secondaries, in the preregistration's order

1. **`uncited`**: 40 of 446 = **8.97%** (Wilson 6.66–11.98%; bootstrap 5.46–13.16%). Arm 3
   read A 25 of 234 = 10.68% (Wilson 7.34–15.30%) and B 14 of 206 = 6.80% (4.09–11.08%);
   Arm 4 read 16 of 206 = 7.77% (Wilson 4.84–12.24%, as RESULTS-ARM4 states it; the
   second and third versions here misquoted it). No materiality
   threshold was registered, so none is claimed; the number is reported first because the
   design asks for it.
2. **Resolved**: 394 of 401 blockable = 98.25% (Wilson 96.44–99.15%; bootstrap 97.06–99.34%);
   394 of 406 addressed = 97.04% (94.91–98.30%; 94.90–98.75%).
3. **Ambiguous** (a quotation the file says on more than one line): 5 of 406 = 1.23%
   (0.53–2.85%; 0.00–3.23%).
4. **Quote-absent** 0 of 406 (Wilson 0.00–0.94%; bootstrap 0.00–0.00%); **cross-line** 0 of
   406 (Wilson 0.00–0.94%; bootstrap 0.00–0.00%).
5. **Mechanisms**: §2; carried in `study8/rows-arm5.jsonl`.
6. **Matcher version**: `620fb3bc…` in every row.
7. **Unit shortening**: the instrument flags 2 of 401 (Wilson 0.14–1.80%; bootstrap
   0.00–1.27%). One is an M4 block: the instrument's sole triggering occurrence there is
   the transcribed value itself, preceded by a tilde and followed by whitespace, and the
   unit token at that occurrence begins with the transcribed unit followed by a hyphen —
   the hyphen-glued unit-and-word token that M4 names, so the flag is the M4 block seen
   again, not a shortened unit (the second version called this an artefact of the digit
   inside another number; the second review executed the instrument and it is not); one
   is a pass on a hyphen-glued range with
   the unit written on both endpoints: the shipped scanner offers the low endpoint's own
   unit there (`_unit_candidates` yields both the whole hyphenated token and the low
   endpoint's unit), which the gold rule counts as stated (R7) and which is the correct
   reading. **No unit was shortened.** The instrument's definition — the transcribed unit is
   a prefix of the token after the value — is not the design's "a reading shorter than the
   whole token", because here the token is not one unit; noted for the next arm's
   instrument.
8. **Annotation rate**: 446 rows / 1,170 numbers present = 38.1% (Wilson 35.38–40.94%;
   draft-clustered bootstrap 34.47–41.94% — a ratio of rows to numbers, quoted with the
   registered intervals for form's sake).
9. **Cost**: $4.4417, $0.0888 per draft; **malformed-envelope re-ask on 31 of 50 drafts**,
   counted and not fixed.
10. **`adjudicator_b`** (exact substring) against the gold on the 57 labelled rows: C rows
    54 true / 0 false; N rows 2 true / 1 false — the disqualified instrument reads two of
    the three right blocks as containing (a step number at the start of one line supplies
    the value that its sentence writes in words; on the power-of-ten line the numeral and
    the unit are both present, apart), as the gold study said it would.
11–13. §4, §2 and §3 above.

## 6. Deviations, as recorded

* **`plan.json` was rewritten by the first retry invocation** (the harness wrote the plan on
  every call). The log had printed the plan at the start **without its `git_status`
  field**; every other field was restored from the log, and `git_status` was taken from
  the dry run at the same tree — which ran **before** the preregistration commit, so the
  field shows the report script modified and the Arm 5 study files untracked. The run
  itself started at `code_sha` 38d3d22 (in the log's plan); its own status at start is not
  recorded. The restored plan carries a `git_status_note` saying exactly this, and
  `manifest-arm5.json` copies it. The harness now keeps the plan on a retry (`a0e7723`).
* The failed first attempt's directory is kept beside the retry as
  `…__S.attempt1-failed`.
* The report script carried Arm 4's bootstrap seed for every arm; the first review found
  it, and the seed now follows `--arm` (the first version's intervals were off in the
  second decimal).
* The report script's title said "Arm 4" for any arm; fixed to read the `--arm` flag.

## 7. What is recorded

`study8/rows-arm5.jsonl` (446 rows), `manifest-arm5.json`, `key-arm5.jsonl`,
`L1-arm5.csv`, `L2-arm5.csv`, `GOLD-arm5.csv`, `arm5_census.txt`, `report-arm5.json`;
**no corpus text, no draft, no quotation** — this version was checked against the corpus
before commit for 2–5-word runs (ordinary words that any text shares are not what the
rule forbids). Drafts, projects, the sheet and the log are at
`~/Documents/Crossaudit/study-data/wt-arm5-runs/` (CC BY-NC-SA 4.0, not redistributed),
with `MANIFEST.sha256` and an entry in the archive's `MANIFEST.json`.

## 8. Limitations

Those the preregistration named: the instances are not fresh; one task family; L2 is a
model; the gold rule is about characters. And one this run found: the quotation-versus-line
mismatch of §2 (M9b) — the primary is adjudicated on the located line while the contract
reads the quotation, so a quotation that excludes the pair the line states elsewhere is a
wrong block by the rule and a right one by the contract. It is one row here; a larger n
should decide whether the adjudicator should be the quotation.
