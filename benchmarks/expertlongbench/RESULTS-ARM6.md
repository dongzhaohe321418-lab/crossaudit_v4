# Arm 6 — the shipped check on a second domain (T01LegalMDS): both preregistered hypotheses fail

Study 15. Preregistered at `benchmarks/expertlongbench/study15/PREREGISTRATION-ARM6.md`
(081f4f0, before any model call; Amendments 1–4). Population: every T01LegalMDS instance
whose input is at most 200,000 characters — **33 of 100** (`study15/arm6_population.txt`;
median 159,917 characters, 2,825 lines, 58 characters per line). One arm, the shipped
configuration after D165: generator `anthropic:claude-sonnet-4-6`, auditor
`openai:gpt-5.6-terra`, one round, `checks: ["number_source"]`, the shipped skill, contract
and per-row verifier, matcher blob `620fb3bc…`. **The primary is adjudicated on the
quotation** (D164 ruling 3): the labellers saw the run of characters the generator quoted,
not the whole line.

**Three attempts, as the amendments record.** Attempt 1 (8 of 8 escalated in round 1: the
generator narrated its `file_read` call beside the envelope and the re-ask restated the
wrong envelope — D165, `study15/ATTEMPT-1.md`) and the eight-instance probe of the fix
(`PROBE-envelope-fix.md`) enter no rate. Attempt 2, under the merged fix, paused at instance
12 when the generator key's credit ran out and resumed the next day; **11 records are
provider outages** (one SSL transport error, seven "credit balance is too low", three more
transport errors after the resume), all set aside in `records-outage.jsonl` and re-run per
Amendment 3; every one of the 33 instances then completed. Spend **$13.41** on the 33
counted drafts ($0.41 per draft); the outages cost $0.34 in all.

---

## 1. The two dispositions

**§8g (H6a).** Among blockable rows whose quotation genuinely contains the transcribed pair:

| false-blocker rate | 95% Wilson score interval | draft-clustered 95% percentile bootstrap (seed 20261108) | **§8g** |
|---|---|---|---|
| **3 of 17 = 17.65%** | **6.19–41.03%** | 0.00–60.00% (7 of 10,000 resamples discarded, no denominator) | **KILL** |

The lower bound exceeds 2%. The denominator is 17 rows — 14 passes and 3 correct blocks —
because only 19 rows in the whole run have a quotation the check can locate on one line;
the number is quoted as a count (EXPERIMENT_RECORD §9), and it decides what §8g says it
decides: **on this domain the check does not enter any profile.** It says nothing about
T03, where Arm 5 read PASS at 4 of 398; the science profile's standing (D164) is unaffected.

**H6b, the one-line rule on hard-wrapped documents.** Over addressed rows (a quotation was
given): **40 of 87 = 45.98% cross a line break** (Wilson 35.90–56.40%; bootstrap
26.15–60.98%). The preregistered bar was a lower bound of 20%; it is exceeded by 16 points.
**H6b comes out false, as §1 said it was likely to**: on documents wrapped at 58 characters
the contract's requirement that a quotation lie within one line is the largest single
reason the check blocks, and it is the contract's shape, not the generator's error. Per §8
of the preregistration, **the check does not enter any profile for prose-wrapped documents
until the line rule is redesigned** — a decision record (D166), not a fix here.

**Adjudication.** 19 items on the blinded sheet — the 5 blocks with a located quotation and
all 14 passes — labelled by L1 (the author's session) and L2 (`gpt-6-astra` through `codex
exec`, read-only, the sheet and the rule only). **κ = 1.000, 19 of 19 agree**
(`study15/L1-arm6.csv`, `L2-arm6.csv`, `GOLD-arm6.csv`); rule codes differ on 12 empty-unit
rows (L1 R1, L2 R3 — both correct, R3 the more specific; L1's carried). The 14 passes are 14
of 14 C (Wilson 78.47–100%). The 61 blocks without a located quotation are N by definition
for the primary (§3) and are the subject of §2.

## 2. What the 66 blocks are (shapes only; no source text)

| class | n | what it is | by contract |
|---|---|---|---|
| **Q1** — the quotation crosses a line break | **40** | the generator quoted a sentence; the source wraps sentences at ~58 characters | right by contract (the one-line rule), and the contract is what H6b indicts |
| **Q2** — the quotation is not in the file as quoted | **21** | 6 differ only in typographic apostrophes or quotation marks the generator normalised to ASCII; 6 share their first 40 characters with the source and diverge after (an elision); 9 are not found by prefix (a paraphrase, or a different file) | right by contract; the 6 rendering cases are a fold the product could make (a candidate slice); of all 61 Q1+Q2 rows, 38 (62.3%, Wilson 49.75–73.39%) have the pair somewhere in the named file |
| **M13, new** — a currency sign before the value, transcribed as the unit | **3** | the source writes the sign first; the scanner reads a unit after the number and finds none | **wrong block** (gold C): the three rows behind the KILL |
| M1b — the value written in words | 1 | | right (gold N) |
| M1b — the value outside the quoted run | 1 | the quotation ends one token before the value | right under the quotation adjudicator (gold N); the line-level reading would have called it stated — the disagreement D164 ruling 3 anticipated, one row here |

Under the Arm 4 matcher blob (`study8/arm5_matcher_diff.py`, quotation reading) the 19
located rows are 5 block / 14 pass under both matchers: **the containment extensions moved
no row on this domain**, because nothing here is a range, list or subscript.

## 3. The generator on this domain (secondaries 8, 15, 16)

* **Annotation rate**: 91 rows over 2,630 numbers present = **3.5%** (Wilson 2.8–4.2%;
  bootstrap 1.5–5.8%); Arm 5 on T03 read 38.1%. **Only 11 of 33 summaries carry the fence at
  all** (33.3%, Wilson 19.8–50.4%; bootstrap 18.2–48.5%); those 11 hold 1 to 22 rows
  (median 9). The skill was rendered on every generator call, the tool result returned the
  whole source (512 KiB bound), and the generator still wrote no fence two times in three.
  Reported first, as the preregistration asks when it is below Arm 5's by more than the
  intervals allow.
* **Unit-bearing rows**: 42 of 91 = 46.2% (Wilson 36.3–56.3%; bootstrap 15.7–70.7%) — the
  units are `$` and `%`; the rest are empty-unit dates, counts and identifiers. The
  empty-unit contract carried half the load, as the census predicted.
* **Shapes of the transcribed values** (secondary 16, read from the archived rows by hand):
  of the 19 located rows, 3 are years, 2 are durations in days, 7 are dollar amounts, 5 are
  counts, 2 are percentages; none is a docket number.
* `uncited` 4 of 91 = 4.40% (1.72–10.76%; 0.00–9.09%). Resolved 14 of 80 blockable = 17.50%
  (10.72–27.26%; 4.40–36.67%). Ambiguous 7 of 87 = 8.05% (3.95–15.69%; 2.53–16.67%).
  Unit shortening 0 of 19 (Wilson 0.00–16.82%).
* **The generator path**: every one of the 33 drafts took the narrated-tool → corrected
  re-ask → tool → continuation shape (3 calls; 2 drafts took 4), so the report's
  "malformed-envelope re-ask on 33 of 33" is the mechanism D165 fixed, working. 3 of 101
  generator calls returned exactly 4,096 output tokens, the ceiling.
* `adjudicator_b` (exact substring) on the 19 labelled rows: C rows 10 true / 7 false, N rows
  0 true / 2 false — the disqualified instrument misses 7 of 17 correct rows here, because
  thousands commas and a currency sign sit between the value and its digits.

## 4. What this run licenses

* The check's science-profile standing stands on Arm 5; **for hard-wrapped prose the
  contract's line rule is the wrong shape**, and the decision is to redesign it (a quotation
  may span a soft wrap: the file's line breaks inside a sentence are joined before the
  match, with the interval mapped back) as a preregistered slice with its own gold rows —
  the 40 Q1 rows of this run are that gold's first candidates, labelled here as N only by
  definition.
* M13 (a currency sign before the value) is a real matcher class on this domain: three
  rows, all C, and the KILL rests on them. It goes to the containment design's §6 beside
  M12, with the same rule: a note first, a measured slice if ever.
* The 6 rendering cases of Q2 (typographic apostrophes and quotation marks) are a fold the
  quotation matcher could make without a semantic claim; also a note, not a fix here.
* Nothing here changes what Arm 5 licensed; nothing here is quotable for T03.

## 5. Records

`study15/rows-arm6.jsonl` (91 rows), `manifest-arm6.json`, `key-arm6.jsonl` (19 sheet items
+ 61 no-location blocks), `L1-arm6.csv`, `L2-arm6.csv`, `GOLD-arm6.csv`, `report-arm6.json`,
`arm6_population.txt`; **no corpus text, no draft, no quotation** — this file was scanned
for 2–5-word runs against the corpus before commit. Drafts, projects, the sheet, the logs
and the outage records are at `~/Documents/Crossaudit/study-data/wt-arm6-runs/` with
`MANIFEST.sha256` and an entry in the archive's `MANIFEST.json`.

## 6. Limitations

The preregistration's; a size-capped population; one generator; L2 a model; the primary's
n is 17 rows, so its interval is wide and its KILL is decided by three rows of one class —
the disposition is the rule's, and the sentence to carry is H6b's, which rests on 87 rows.
