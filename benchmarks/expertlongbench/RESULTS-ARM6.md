# Arm 6 — the shipped check on a second domain (T01LegalMDS): both preregistered hypotheses fail

Study 15. Preregistered at `benchmarks/expertlongbench/study15/PREREGISTRATION-ARM6.md`
at commit 081f4f0 (2026-09-07 14:12:02 +08:00; attempt 1's first call began 14:12:03 UTC+8
— one second later, so "before any model call" rests on the log's sub-second stamp and the
commit's one-second clock). That commit fell off the branch when its history was rewritten
to remove corpus fragments; it is kept reachable by the tag `study15-prereg-arm6`, and the
same blob is on the branch at 4113b9a (18:44:36 +08:00, which precedes attempt 2 only).
Amendments 1–4 at d688383, db16e85, 4297d6e, f4a8d6b. Every rate measured in this arm
carries its Wilson interval and the draft-clustered bootstrap (seed 20261108, 10,000
resamples of the 33 drafts; resamples with no denominator discarded and counted), computed
by `study15/arm6_rates.py`, which reproduces `report-arm6.json`'s figures and adds the ones
the report does not print; the two Arm 5 figures quoted for comparison carry Arm 5's
intervals. Population: every T01LegalMDS instance
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
(`PROBE-envelope-fix.md`) enter no rate. Attempt 2, under the merged fix, started at
10:44:36 UTC on 2026-09-07 (code 5b8da46) and was stopped by the author when the generator
key's credit ran out: 6 drafts completed, instances 3 and 8–14 failed as outages, instance
15 had begun (Amendments 3–4). It resumed in the same directory at 10:57:33 UTC the same
day (code f4a8d6b, the two amendments committed between). **11 records are provider
outages** over 10 instances (one SSL transport error and seven "credit balance is too low"
before the stop, three transport errors after the resume), all set aside in
`records-outage.jsonl` with their directories under `instances-outage/` and re-run per
Amendment 3; every one of the 33 instances then completed. **The resume rewrote
`plan.json`** (the runner kept an existing plan only for `--only` retries — review round 1
found it): the plan printed at the true start is recovered from `arm6.log` as
`plan-start.json`, and `manifest-arm6.json` carries both (`plan_at_start`, `plan`) with the
fields that differ — `run_id`, `started_utc`, `code_sha`, `git_status` — population, models,
settings, skill, contract, corpus and matcher hashes identical. **The clean-tree proof at
the true start is missing**: the runner prints the plan without `git_status`, so the log
cannot say whether the tree was clean at 10:44 UTC; the manifest records that as "NOT
RECORDED", not as clean. What the record can say is that the resume's tree at 10:57 was
clean at f4a8d6b, and that the commits between the two starts touch study material only
(the emitter and Amendments 3–4) — `src/` is identical at both code hashes. The runner now
never rewrites a plan (`write_plan` in `provenance_arm6.py`, with a test). Spend **$13.41** on the 33 counted drafts ($0.41 per
draft): generator $9.23, auditor $4.18; the outages cost $0.34 in all.

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
T03, where Arm 5 read PASS at 4 of 398 = 1.01% (Wilson 0.39–2.56%; bootstrap 0.24–1.97%);
the science profile's standing (D164) is unaffected.

**H6b, the one-line rule on hard-wrapped documents.** Over addressed rows (a quotation was
given): **40 of 87 = 45.98% cross a line break** (Wilson 35.90–56.40%; bootstrap
26.15–60.98%). The other quotation failure, absent from the file as quoted: 21 of 87 =
24.14% (Wilson 16.36–34.10%; bootstrap 2.22–47.30%). The preregistered bar was a lower bound of 20%; it is exceeded by 16 points.
**H6b comes out false, as §1 said it was likely to**: on documents wrapped at 58 characters
the contract's requirement that a quotation lie within one line is the largest single
reason the check blocks. **What the run does not separate is whose failure that is.** The
skill asks for the shortest run from ONE line that contains the pair; the generator
returned a run crossing a line break on 40 of 87 rows, and only 12 of those 40 end at
sentence punctuation (30.0%; Wilson 18.1–45.4%; bootstrap 0–60%, 5 discarded —
`arm6_rates.py --run`, which reads the quotations from the archive), so "it quoted
sentences" is not the account. Whether a one-line rule is the wrong shape for wrapped text or the generator
simply did not comply is the author's inference to make, and it is made in D166 as an
inference the redesign slice will test, not as a finding of this run. Per §8
of the preregistration, **the check does not enter any profile for prose-wrapped documents
until the line rule is redesigned** — a decision record (D166, in `docs/DECISIONS.md` on
this branch), not a fix here.

**Adjudication.** 19 items on the blinded sheet — the 5 blocks with a located quotation and
all 14 passes — labelled by L1 (the author's session) and L2 (`gpt-6-astra` through `codex
exec`, read-only, the sheet and the rule only). **κ = 1.000, 19 of 19 agree**
(`study15/L1-arm6.csv`, `L2-arm6.csv`, `GOLD-arm6.csv`); rule codes differ on 12 empty-unit
rows (L1 R1, L2 R3 — both correct, R3 the more specific; L1's carried). The 14 passes are 14
of 14 C (Wilson 78.47–100%; bootstrap 100–100%, 49 resamples discarded). The 61 blocks without a located quotation are N by definition
for the primary (§3) and are the subject of §2.

## 2. What the 66 blocks are (shapes only; no source text)

| class | n | what it is | by contract |
|---|---|---|---|
| **Q1** — the quotation crosses a line break | **40** | the quoted run crosses a hard wrap of the source (58 characters per line); 12 of the 40 end at sentence punctuation, 28 do not | right by contract (the one-line rule); H6b measures how often the rule is unmet on this shape of document, not why |
| **Q2** — the quotation is not in the file as quoted | **21** | 6 differ only in typographic apostrophes or quotation marks the generator normalised to ASCII (28.6%; Wilson 13.8–50.0%; bootstrap 0–100%, 128 discarded — 21 rows over few drafts); 6 share their first 40 characters with the source and diverge after (an elision; 28.6%; 13.8–50.0%; 0–66.7%); 9 are not found by prefix (a paraphrase, or a different file; 42.9%; 24.5–63.5%; 0–55.6%) — the rule is `archive_rates` in `arm6_rates.py` | right by contract; the 6 rendering cases are a fold the product could make (a candidate slice) |

The pair is somewhere in the named file for 26 of 40 Q1 rows (65.00%; Wilson 49.51–77.87%;
bootstrap 32.26–100%, 5 discarded) and 12 of 21 Q2 rows (57.14%; Wilson 36.55–75.53%;
bootstrap 0–100%, 128 discarded — 21 rows over few drafts), 38 of 61 together (62.30%;
Wilson 49.75–73.39%; bootstrap 39.66–95.24%): the number is usually real and elsewhere,
which is what a wrapped or normalised quotation looks like from the check's side.
| **M13, new** — a currency sign before the value, transcribed as the unit | **3** | the source writes the sign first; the scanner reads a unit after the number and finds none | **wrong block** (gold C): the three rows behind the KILL |
| M1b — the value written in words | 1 | | right (gold N) |
| M1b — the value outside the quoted run | 1 | the quotation is a run of the source that does not contain the value, and neither does the line it sits on; the value is on a line seven lines away in the same file | right under both readings (gold N): the quotation adjudicator and the line-level reading agree here, so this run holds no row where D164 ruling 3's two readings part |

Under the Arm 4 matcher blob (`study8/arm5_matcher_diff.py`, quotation reading) the 19
located rows are 5 block / 14 pass under both matchers: **the containment extensions moved
no row on this domain**, because nothing here is a range, list or subscript.

## 3. The generator on this domain (secondaries 8, 15, 16)

* **Annotation rate**: 91 rows over 2,630 numbers present = **3.5%** (Wilson 2.8–4.2%;
  bootstrap 1.5–5.8%); Arm 5 on T03 read 446 of 1,170 = 38.1% (Wilson 35.38–40.94%;
  bootstrap 34.47–41.94%). **Only 11 of 33 summaries carry the fence at
  all** (33.3%, Wilson 19.8–50.4%; bootstrap 18.2–48.5%); those 11 parsed to 0 to 22 rows
  (median 9; one fenced draft yielded no row, so 10 drafts carry the 91). The skill was rendered on every generator call, the tool result returned the
  whole source (512 KiB bound), and the generator still wrote no fence two times in three.
  Reported first, as the preregistration asks when it is below Arm 5's by more than the
  intervals allow.
* **Unit-bearing rows**: 42 of 91 = 46.2% (Wilson 36.3–56.3%; bootstrap 15.7–70.7%) — 27
  carry a currency sign, 8 a count of days, 7 a percent sign; the rest are empty-unit
  dates, counts and identifiers. The
  empty-unit contract carried half the load, as the census predicted.
* **Shapes of the transcribed values** (secondary 16; the rule is `shape()` in
  `arm6_rates.py`, run on the archived sheet — unit, then the characters around the value):
  of the 19 located rows, 3 are years (15.8%; Wilson 5.5–37.6%; bootstrap 0–50%), 2
  durations in days (10.5%; 2.9–31.4%; 0–25%), 7 dollar amounts (36.8%; 19.2–59.0%;
  12–100%), 5 counts (26.3%; 11.8–48.8%; 0–60%), 2 percentages (10.5%; 2.9–31.4%; 0–25%);
  7 resamples discarded in each; none is a docket number.
* `uncited` 4 of 91 = 4.40% (1.72–10.76%; 0.00–9.09%). Resolved (a pass) 14 of 80
  blockable = 17.50% (10.72–27.26%; 4.40–36.67%) and 14 of 87 addressed = 16.09%
  (9.83–25.22%; 4.00–33.33%). Located on one line (passes and located blocks) 19 of 87 =
  21.84% (14.45–31.61%; 8.93–39.66%). Ambiguous 7 of 87 = 8.05% (3.95–15.69%;
  2.53–16.67%). Unit shortening 0 of 19 (Wilson 0.00–16.82%; bootstrap 0–0%, 7 discarded).
* **The generator path**: every one of the 33 drafts took the narrated-tool → corrected
  re-ask → tool → continuation shape (3 calls; 2 drafts took 4), so the report's
  "malformed-envelope re-ask on 33 of 33" is the mechanism D165 fixed, working. 3 of 101
  generator calls returned exactly 4,096 output tokens, the ceiling.
* `adjudicator_b` (exact substring) on the 19 labelled rows: C rows 10 true / 7 false, N rows
  0 true / 2 false — the disqualified instrument misses 7 of 17 correct rows here, because
  thousands commas and a currency sign sit between the value and its digits.

## 4. What this run licenses

* The check's science-profile standing stands on Arm 5; **on hard-wrapped prose the
  contract's one-line rule went unmet on 40 of 87 rows, and the run cannot say whether the
  rule or the generator is at fault**. The decision (D166) is to test the author's
  inference that the rule is the wrong shape for such text by redesigning it (a quotation
  may span a soft wrap: the file's line breaks inside a sentence are joined before the
  match, with the interval mapped back) as a slice to be preregistered with its own gold
  rows — the 40 Q1 rows of this run are that gold's first candidates, labelled here as N
  only by definition; if the joined-text rule still fails on them, the fault was the
  generator's.
* M13 (a currency sign before the value) is a real matcher class on this domain: three
  rows, all C, and the KILL rests on them. It goes to the containment design's §6 beside
  M12, with the same rule: a note first, a measured slice if ever.
* The 6 rendering cases of Q2 (typographic apostrophes and quotation marks) are a fold the
  quotation matcher could make without a semantic claim; also a note, not a fix here.
* Nothing here changes what Arm 5 licensed; nothing here is quotable for T03.

## 5. Records

`study15/rows-arm6.jsonl` (91 rows), `manifest-arm6.json` (both plans), `key-arm6.jsonl` (19
sheet items + 61 no-location blocks), `L1-arm6.csv`, `L2-arm6.csv`, `GOLD-arm6.csv`,
`report-arm6.json`, `arm6_rates.py`, `arm6_population.txt`; **no corpus text, no draft, no quotation** — this file was scanned
for 2–5-word runs against the corpus before commit. Drafts, projects, the sheet, the logs
and the outage records are at `~/Documents/Crossaudit/study-data/wt-arm6-runs/` with
`MANIFEST.sha256` and an entry in the archive's `MANIFEST.json`.

## 6. Limitations

The preregistration's; a size-capped population; one generator; L2 a model; the primary's
n is 17 rows, so its interval is wide and its KILL is decided by three rows of one class —
the disposition is the rule's, and the sentence to carry is H6b's, which rests on 87 rows.
