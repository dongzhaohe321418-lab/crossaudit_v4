# Study 15 — Arm 6 wrap-join slice: the frozen Arm 6 rows re-verified on joined text

Preregistered **before any code of this slice was written**, on `study/arm6-wrapjoin`
(branched from `fusion/evidence-authority` at 1f6120e). It is the slice D166 ruling 1
sends to preregistration: a **re-analysis of frozen records** — the 91 annotation rows of
`rows-arm6.jsonl`, the 33 archived projects, the 19-item frozen gold — under one change,
made in the harness and not in the product: the source files are joined at their hard
wraps before the shipped matcher runs. **No generator call, no auditor call, no spend.
Nothing under `src/` is modified**; the shipped `number_source` matcher is run unmodified
on a `files` mapping whose source files are replaced by their joined text, and every
located interval is mapped back to the original line span. Binding:
`benchmarks/EXPERIMENT_RECORD.md` §1–§10, `PREREGISTRATION-ARM6.md` §7 (never corpus text,
never a quotation, never a fragment in prose) and D166.

## 0. What was looked at before this file was written, said plainly

The author ran a **shape-only survey** of the archive before fixing the join rule: counts of
lines, blank lines, heading-shaped, list-shaped and digit-led lines and a histogram of
line lengths over the 33 source files; the 91 rows re-verified once with the shipped
matcher on the *unjoined* files to confirm that every row reproduces its recorded
severity and reason (it does: 91 of 91 match, no row pins a sha, none names `computed:`);
and, for the 40 Q1 rows, the shape of the breaks their quotations cross (the count of
lines the minimal whole-file window spans; whether a break sits after a blank line, after
terminal punctuation, before a digit-led or list-marker-shaped line). No source text was
read or printed. **This means outcome (a)'s direction was foreseeable before the rule was
fixed** — the survey found every Q1 window to be 2 or 3 consecutive non-blank lines — so
the kill's first clause is a weak test, and it is said so here rather than discovered
later. The survey did **not** run the matcher on joined text, did not compute the verdict
of any row after the join, and did not touch the 19 located rows; outcomes (b), (c) and
(d) were not previewed.

## 1. The join rule, verbatim

The file is split on `\n`. A line is **structural** if, after its leading whitespace is
removed, it is empty; or begins with `#` followed by a space, a tab or another `#` (an ATX
heading); or begins with `|` (a table row); or begins with `>` (a blockquote); or begins
with three or more backticks or three or more tildes (a code fence line); or consists of
three or more of one character from `=`, `-`, `_`, `*` and nothing else (a setext underline
or thematic break). A line is **block-opening** if it is not structural and, after its
leading whitespace is removed, begins with `-`, `*` or `+` followed by a space or tab (a
bullet), or with one to nine ASCII digits followed by `.` or `)` and then a space or tab
(an ordered-list marker). A code-fence line toggles **fence state**; the file starts
outside a fence.

The break between consecutive lines A and B is **JOINED** if and only if: the break is
outside a fence; neither A nor B is structural; and B is not block-opening. Every other
break is **KEPT**. A joined break replaces A's trailing whitespace, the newline and B's
leading whitespace with one space. The rule reads no punctuation and no letter case: a
hard wrap can fall after a sentence's full stop and before a capital, and a rule that
kept such breaks would keep hard wraps; the rule is structural only. No line is added,
removed or reordered, so the whole file folds identically under the matcher's own
whitespace fold before and after the join (`_fold(joined) == _fold(original)`); that
identity and the mapping are tested.

`join_wraps(text) -> (joined_text, mapping)`: `mapping[k] = (start, end)` is the 0-based
inclusive span of original lines that joined line `k` was made from; the spans partition
the original lines in order. A located joined line maps back to original lines
`start + 1 … end + 1` (1-based), and `joined_span_lines = end - start + 1`.

Every file of each instance's audited increment except the annotating draft
(`work/synthesis/explanation.md`) is joined; in this run that is one file per instance,
`work/synthesis/RECIPE.md`. The draft, the rows and the matcher are untouched.

## 2. The four outcomes, with their denominators

"Located" means the shipped `_quote_span` (reached through `provenance_arm4.located_line`,
unmodified) returns a location on the joined file: exactly one joined line holds the
whitespace-folded quotation. "Verdict after join" is `provenance_arm4.verify_shipped` on
the joined files: PASS, BLOCKER (with its reason key) or ADVISORY.

* **(a) Q1 rows located after the join / the 40 Q1 rows.** Beside it, of the 40: rows
  whose quotation the joined file holds on more than one joined line (ADVISORY, ambiguous
  — found, not located), rows still crossing a kept break, rows absent (should be 0 by
  construction, reported if not).
* **(b) The newly located rows** — every row not located in Arm 6 (the 61 no-location
  blocks: 40 Q1, 21 Q2) that is located after the join — by verdict after join: PASS /
  BLOCKER (the pair is not in the quoted interval) / other; denominator the newly located
  rows. **They have no gold label and are reported as unlabelled candidates, never as C
  or N.** The wrong-block share among them is bounded: it lies in
  `[0, blocked share]`, because every wrong block is a block; that bound is what the kill
  reads. As a description, not a label, each newly located row also carries the two
  automatic readings Arm 6 recorded for located rows — `adj_a` (`contains_pair` on the
  located joined line) and `adj_b` (exact substring, the instrument Arm 4 disqualified) —
  with the same standing they had there: neither is a gold label.
* **(c) The §8g rate on the located-and-labelled rows after the join.** Denominator: the
  gold-C rows (17 in `GOLD-arm6.csv`) that are still located after the join; numerator:
  those the shipped check BLOCKS after the join. Beside it: every one of the 19 labelled
  rows whose verdict after the join differs from Arm 6's, by count and by reason (a join
  can create a second joined line that holds the quotation, turning a located row
  ambiguous), and the 14 labelled passes still passing / 14.
* **(d) The quote-crossing rate after the join / the 87 addressed rows** (rows whose
  `src_kind` is neither `uncited` nor `governed`; 40 of 87 before the join).

Secondaries, each with both intervals: located after join / 87 addressed (19 of 87
before); ambiguous after join / 87 (7 before); Q2 rows located after join / 21 (a join
alone, without the typography fold of D166 ruling 3, is not expected to recover the 5
"rendering" rows that need both); the joined-span line count of the newly located rows
(2, 3, more) as counts; per file, joined lines / original lines as a shape of how much the
rule joined.

## 3. The kill, verbatim

**The inference "the one-line rule is the wrong shape for wrapped text" stands only if at
least half of the 40 Q1 rows become located AND the newly located rows' wrong-block share
among any that CAN be labelled by an existing rule is not above the located rows' 3/17.**

How the second clause is read here, fixed now: no existing rule labels a row C or N without
a labeller — `adjudicator_b` was disqualified in Arm 4 and misses 7 of 17 correct rows on
this domain; `adj_a` is the matcher's own reading — so the set of newly located rows that
CAN be labelled by an existing rule is **empty**, and the clause is decided on the bound of
§2(b): it is **met** if the blocked share among the newly located rows (the upper bound of
the wrong-block share) is at or below 3/17 = 17.65%, as a point comparison with both
intervals reported beside it; it is **undetermined** if the blocked share is above 3/17,
because the rows between 0 and that bound cannot be told apart without a gold. Verdicts:
**stands** (both clauses met), **does not stand** (fewer than 20 of 40 located), or
**undetermined** (20 or more located, second clause undetermined) — and an undetermined
verdict means the inference does not stand on this re-analysis and needs a labelled slice.
Outcome (c) is reported as a check that the join moved no labelled row, and is not part of
the kill.

## 4. Intervals

Every rate carries the 95% Wilson score interval, named as such, and the draft-clustered
95% percentile bootstrap: 10,000 resamples of the 33 drafts with replacement, every draft a
cluster whether or not it holds a row in the denominator, **seed 20261109**, resamples with
an empty denominator discarded and their count reported, the same percentile index as
`arm6_rates.py` (`stats[int(0.025 * (len - 1))]`, `stats[int(0.975 * (len - 1))]`).
`wrapjoin.py` copies `arm6_rates.py`'s `wilson` and `draft_bootstrap` with the seed changed
and nothing else.

## 5. What is and is not done

* **No row is relabelled.** `GOLD-arm6.csv`, `L1-arm6.csv`, `L2-arm6.csv`, `key-arm6.jsonl`
  and `rows-arm6.jsonl` are read and not written. The new record
  `rows-arm6-wrapjoin.jsonl` carries every field of `rows-arm6.jsonl` unchanged and adds
  `located_after_join`, `crosses_after_join`, `joined_span_lines` (and, as description,
  the verdict after join, its reason key, `occurrences_after_join`, `adj_a_after_join`,
  `adj_b_after_join`, `joined_span_start`, `joined_span_end`, `newly_located`).
* The archive is read-only; the rows are matched to the archive by instance and row
  index, the annotation rows read from the draft by `provenance_arm3.fence_rows` exactly
  as Arm 6 read them, and every row's unjoined verdict is asserted equal to the recorded
  one before the joined verdict is taken.
* Never corpus text: `RESULTS-ARM6-WRAPJOIN.md` describes shapes; before the commit a
  fragment scan (`wrapjoin_scan.py`) checks that no run of five or more words from any
  file under the archive (the projects, drafts, ledgers and logs; the repo's own contract
  and skill files excepted) appears in any file this slice commits, and its result is
  stated in the results file.
* One generator, one domain, a join rule chosen by the author after a shape survey (§0),
  no gold for the newly located rows: what this slice can show is whether the join
  changes what the shipped matcher can locate and how it disposes of what it locates; it
  cannot show that any newly located block is wrong or right.

## 6. Reproduction

```sh
export PYTHONPATH=<worktree>/src
python3 benchmarks/expertlongbench/study15/wrapjoin.py --run ~/Documents/Crossaudit/study-data/wt-arm6-runs/arm6
python3 -m pytest benchmarks/expertlongbench/tests/test_wrapjoin.py -q
python3 benchmarks/expertlongbench/study15/wrapjoin_scan.py --run ~/Documents/Crossaudit/study-data/wt-arm6-runs/arm6 <files…>
```
