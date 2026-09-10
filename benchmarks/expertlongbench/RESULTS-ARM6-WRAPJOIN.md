# Arm 6 wrap-join slice — the join locates 24 of the 40 crossing quotations; 10 of the 24 are then blocked, and without a gold the inference is undetermined

Study 15, the slice D166 ruling 1 sends to preregistration. Preregistered at
`benchmarks/expertlongbench/study15/PREREGISTRATION-WRAPJOIN.md` (918b14b, before any code
of the slice was written; §0 of that file says what shape-only survey preceded it and why
outcome (a)'s direction was foreseeable). **A re-analysis of frozen records, not a run**: no
generator or auditor call, no spend. The 91 rows of `study15/rows-arm6.jsonl`, the 33
archived projects and the 19-item frozen gold are read; nothing under `src/` is modified;
**the shipped matcher is the same blob as Arm 6's** (`620fb3bc…`, asserted by the driver),
run unmodified through `provenance_arm4.verify_shipped` and `located_line` on a `files`
mapping whose one source file per instance is replaced by its joined text, the draft
untouched. Before any joined verdict is taken, every row's unjoined verdict is re-derived
and asserted equal to the recorded one (91 of 91). Every rate carries the 95% Wilson score
interval and the draft-clustered 95% percentile bootstrap (seed 20261109, 10,000 resamples
of the 33 drafts, discarded resamples counted), computed by `study15/wrapjoin.py`, which
writes `rows-arm6-wrapjoin.jsonl` and `report-wrapjoin.json`. **No row is relabelled.**

**Said first.** The kill's first clause is met and its second is not decidable: 24 of the
40 Q1 rows are located after the join, but 10 of those 24 are then blocked by the shipped
check, and none of the 24 has a gold label. Under the preregistered reading of the second
clause (§3 of the preregistration: the wrong-block share among the newly located rows lies
in `[0, blocked share]`, and no existing rule labels a row), the bound 10 of 24 = 41.67%
is above 3 of 17 = 17.65%, so the verdict is **undetermined — the inference "the one-line
rule is the wrong shape for wrapped text" does not stand on this re-analysis** and needs a
labelled slice. What the re-analysis does establish is narrower: on this domain the join
turns the crossing class into three others — 14 passes, 10 blocks of a shape the check
already has a name for, and 15 ambiguities — and the crossing rate itself falls from 40 of
87 to 1 of 87.

---

## 1. The four preregistered outcomes

| outcome | rate | 95% Wilson | draft-clustered bootstrap (seed 20261109) |
|---|---|---|---|
| **(a)** Q1 rows located after the join / 40 Q1 rows | **24 of 40 = 60.00%** | 44.60–73.65% | 17.65–90.91% (5 of 10,000 discarded) |
| — Q1 rows on more than one joined line (ADVISORY, ambiguous) / 40 | 15 of 40 = 37.50% | 24.22–52.97% | 5.56–77.78% (5 discarded) |
| — Q1 rows still crossing a kept break / 40 | 1 of 40 = 2.50% | 0.44–12.88% | 0.00–12.00% (5 discarded) |
| — Q1 rows absent after the join / 40 | 0 of 40 | 0.00–8.76% | 0.00–0.00% (5 discarded) |
| **(b)** newly located rows PASSED / 24 newly located | 14 of 24 = 58.33% | 38.83–75.53% | 28.57–100.00% (36 discarded) |
| **(b)** newly located rows BLOCKED (the pair is not in the quoted interval) / 24 | **10 of 24 = 41.67%** | 24.47–61.17% | 0.00–71.43% (36 discarded) |
| **(c)** §8g after the join: gold-C rows blocked / gold-C rows still located | **3 of 15 = 20.00%** | 7.05–45.19% | 0.00–75.00% (15 discarded) |
| **(d)** quote-crosses-line after the join / 87 addressed rows | **1 of 87 = 1.15%** | 0.20–6.23% | 0.00–4.00% |

Arm 6's figures for comparison, with Arm 6's intervals (seed 20261108): Q1 40 of 87 =
45.98% (Wilson 35.90–56.40%; bootstrap 26.15–60.98%); §8g 3 of 17 = 17.65% (Wilson
6.19–41.03%; bootstrap 0–60%, 7 discarded).

**(a).** Every one of the 40 quotations is in the joined file (0 absent, as the join
preserves the whitespace fold of the file — asserted per file). 24 are on exactly one
joined line and are located; 15 are on more than one joined line — 19 of the 24 ambiguous
rows after the join sit on 2 joined lines, 4 on 3, 1 on 4 — and go to the auditor as
ADVISORY under the shipped rule, neither blocked nor located; 1 still crosses a break the
rule kept (§3, the fence clause). The quotation's own interval, mapped back, covers 2
original lines in 19 of the 24 newly located rows and 3 in the other 5: short runs
crossing one or two hard wraps. The joined line that holds them is a paragraph: 2 to 55
original lines (2 lines in 2 rows, 3–4 in 4, 10–27 in 17, 55 in 1).

**(b).** The 24 newly located rows are all Q1 (0 of 21 Q2 rows become located: Wilson
0.00–15.46%; bootstrap 0–0%, 139 discarded — as expected, D166 ruling 3's rendering rows
need the typography fold as well). They lie in 5 drafts (11, 7, 3, 2, 1 rows), and the 10
blocks in 3 drafts (7, 2, 1). **They have no gold label and are unlabelled candidates.**
As description, not labels: a predicate on the quotation (`block_shape` in `wrapjoin.py`
— the value's immediate left context and the unit, the mirror of `arm6_rates.py`'s
empty-unit census) puts 9 of the 10 blocks in the shape of M13 (a currency sign directly
before the value, the unit a currency sign: 90.00%; Wilson 59.58–98.21%; bootstrap 0–100%,
395 discarded — 10 rows in 3 drafts) and 1 in the shape of M1b (the value not in the
quotation as written: 10.00%; Wilson 1.79–40.42%; bootstrap 0–100%, 395 discarded); the
same predicate, run on the 5 labelled blocks the join leaves located, returns Arm 6's
classes exactly (3 M13, 2 M1b). Arm 6's three M13 rows were the three wrong blocks behind
its KILL, all gold C. **That is a shape, not a label**: whether these 9 rows would be C
under the frozen gold rule is what a labelled slice decides, and this file does not decide
it. The two automatic readings Arm 6 recorded for located rows, on the located joined
line — a paragraph now, so both are looser than on Arm 6's lines — read: `adj_a`
(`contains_pair`) true on 1 of the 10 blocks (Wilson 1.79–40.42%; bootstrap 0–100%, 395
discarded); `adj_b` (exact substring, the instrument Arm 4 disqualified) true on 4 of 10
(Wilson 16.82–68.73%; bootstrap 14.29–100%, 395 discarded) and on 7 of the 14 passes
(Wilson 26.80–73.20%; bootstrap 0–100%, 135 discarded).

**(c).** 15 of the 17 gold-C rows stay located after the join (88.24%; Wilson 65.66–96.71%;
bootstrap 53.85–100%, 3 discarded); the two that do not, A60011 and A60012, both labelled
passes, become ambiguous — the join built a second joined line that holds their quotation
— so the verdict changed on 2 of 19 labelled rows (10.53%; Wilson 2.94–31.39%; bootstrap
0–44.44%, 3 discarded), and 12 of 14 labelled passes still pass (85.71%; Wilson
60.06–95.99%; bootstrap 33.33–100%, 36 discarded). The 3 wrong blocks and the 2 right
blocks keep their verdicts. The §8g rate on what remains located and labelled is 3 of 15;
it is the same three rows, and the join moved no labelled row into or out of a block.

**(d).** 1 of 87 addressed rows crosses a line break after the join, against 40 of 87
before. The rest of the 87: located 41 (47.13%; Wilson 36.98–57.51%; bootstrap
26.92–63.93%; 19 before), ambiguous 24 (27.59%; Wilson 19.29–37.77%; bootstrap
10.11–48.98%; 7 before), PASS 26 of 80 blockable (32.50%; Wilson 23.24–43.36%; bootstrap
14.00–56.14%; 14 before). 41 of 91 rows change verdict (45.05%; Wilson 35.24–55.27%;
bootstrap 23.08–61.45%), every one of them one of four transitions: crossing → PASS 14,
crossing → BLOCKER (pair not in the quoted interval) 10, crossing → ADVISORY (ambiguous)
15, PASS → ADVISORY (ambiguous) 2.

## 2. The kill

Verbatim from the preregistration: *the inference "the one-line rule is the wrong shape for
wrapped text" stands only if at least half of the 40 Q1 rows become located AND the newly
located rows' wrong-block share among any that CAN be labelled by an existing rule is not
above the located rows' 3/17.*

* Clause 1: **met**, 24 of 40 (the preregistration's §0 says this was foreseeable).
* Clause 2: the set of newly located rows an existing rule can label is **empty** (fixed
  in §3 of the preregistration: `adjudicator_b` is disqualified, `adj_a` is the matcher's
  own reading); the wrong-block share lies in `[0, 10/24]`, and 10 of 24 = 41.67% is
  above 3 of 17 = 17.65%, so the clause is **undetermined**.
* **Verdict: undetermined.** The inference does not stand on this re-analysis. It is not
  refuted either: the 10 blocks could all be right, all wrong, or anything between, and
  the one predicate that speaks to it (9 of 10 in M13's shape) is a description of the
  quotation, not a judgment of the row.

## 3. What this does and does not show

* **Does show.** A structural join of hard wraps (§1 of the preregistration) leaves the
  shipped matcher able to locate 24 of the 40 quotations Arm 6 could not, without any
  change to the matcher; the crossing rate on this domain goes from 40 of 87 to 1 of 87;
  the located quotations themselves are 2- and 3-line runs; and what the check then says
  about them is 14 passes, 10 blocks and — for the other 15 — that the joined file says
  the same words on two to four joined lines.
* **Does not show that any newly located block is wrong or right.** There is no gold for
  the 24; the frozen gold covers the 19 rows Arm 6 located, and those move only by
  becoming ambiguous (2 rows). The M13-shaped share (9 of 10) is a predicate; a labelled
  slice under the frozen gold rule, blinded as Arm 6's was, is what would turn it into a
  wrong-block rate — and if that slice called the 9 rows as Arm 6's gold called its 3 M13
  rows, the wrong-block share among the 24 would be at least 9 of 24, which this file
  neither asserts nor rules out.
* **Ambiguity is the join's cost on this document shape.** 15 of the 40 Q1 quotations,
  and 2 of the 14 labelled passes, are held by more than one joined line: multi-document
  legal records repeat passages, and a line that was unique at 58 characters is not unique
  once it is a paragraph. Under the shipped rule these are ADVISORY and go to the auditor;
  the line-scoped coincidence rate D166 wants preserved was **not re-measured here** on
  joined text, and a joined line is a paragraph of up to 55 original lines, so the
  boundary context the matcher reads is wider than a line — the located interval is still
  the quotation's own (`_pair_in_quote`), but whether that keeps the coincidence rate at
  the line-scoped 0.54% rather than the file-scoped 27.7% (CORRECTIONS #32) is a
  measurement this slice did not make.
* **A join rule chosen by the author, after a shape survey.** The rule is structural only
  (blank lines, headings, tables, blockquotes, fences, rules, bullets and ordered-list
  markers); its fence clause read a line of three or more backticks or tildes as a code
  fence, and **3 of the 33 source files hold such a line with no close** (1, 1 and 7
  fence-shaped lines), leaving 31.8%, 40.9% and 56.9% of their lines unjoined; the one Q1
  row still crossing after the join lies in such a region. The rule was preregistered and
  is not changed here; a variant without the fence clause would be a post-hoc analysis
  and was not run. Joined lines per original line: min 0.054, median 0.194, max 0.654.
* **One domain, one generator, frozen rows.** Every cluster count is small — the 24
  newly located rows lie in 5 drafts, the 10 blocks in 3 — and the bootstrap intervals
  say so (0–100% on the 10-row rates, with hundreds of resamples discarded). Nothing here
  is quotable for T03, and nothing here changes D164 or D166's ruling that the check stays
  out of every profile for hard-wrapped documents.

## 4. Records and the scan

`study15/PREREGISTRATION-WRAPJOIN.md`, `wrapjoin.py` (the rule, the driver, the
intervals), `wrapjoin_scan.py`, `rows-arm6-wrapjoin.jsonl` (the 91 rows of
`rows-arm6.jsonl` with every field unchanged plus `located_after_join`,
`crosses_after_join`, `joined_span_lines` and the description fields §5 of the
preregistration lists, with `quote_span_lines`/`quote_span_start`/`quote_span_end` — the
quotation's own interval mapped back — and `block_shape_after_join` added beside them; the
addition is said here), `report-wrapjoin.json`, and `tests/test_wrapjoin.py` (join and keep
cases, the mapping partition and fold round trip on seeded random documents, and the
shipped matcher unmodified locating a two-line quotation after the join). **No corpus text,
no draft, no quotation**: `benchmarks/withdrawn.py`, which the brief named, does not exist
in this tree; the scan run instead is `wrapjoin_scan.py`, which shingles every text file
under the archive (the repo's own contract, skill and plan files excepted) into runs of
five words, subtracts the runs that the repo's own committed text at HEAD already says
(`src/`, `benchmarks/expertlongbench/`, `docs/` — the product, the harness and the earlier
records hold no corpus text by the repo's rule), and reports any remaining run shared with
a committed file. **Result on the seven files of this commit: clean, 0 shared runs**
(667,892 archive runs, 661,026 after the subtraction). Without the subtraction the scan
flags 5,422 shared runs, every one of them the product's own vocabulary and not the
corpus's: the field names of `rows-arm6-wrapjoin.jsonl` against the archive's own
`records.jsonl` and the fence keys in the drafts, the rendered skill under each project's
`skills/`, and the harness path names in the reproduction commands and the test — the
diagnostic that traced each hit to its archive files is what justified the baseline. The
archive at `~/Documents/Crossaudit/study-data/wt-arm6-runs/arm6/` was read and not
written.

## 5. Reproduction

```sh
export PYTHONPATH=<worktree>/src
python3 benchmarks/expertlongbench/study15/wrapjoin.py --run ~/Documents/Crossaudit/study-data/wt-arm6-runs/arm6
python3 -m pytest benchmarks/expertlongbench/tests/test_wrapjoin.py -q
git archive HEAD src benchmarks/expertlongbench docs | tar -x -C <baseline-dir>
python3 benchmarks/expertlongbench/study15/wrapjoin_scan.py --run ~/Documents/Crossaudit/study-data/wt-arm6-runs/arm6 --baseline <baseline-dir> benchmarks/expertlongbench/RESULTS-ARM6-WRAPJOIN.md benchmarks/expertlongbench/study15/PREREGISTRATION-WRAPJOIN.md benchmarks/expertlongbench/study15/wrapjoin.py benchmarks/expertlongbench/study15/rows-arm6-wrapjoin.jsonl benchmarks/expertlongbench/study15/report-wrapjoin.json benchmarks/expertlongbench/tests/test_wrapjoin.py
```
