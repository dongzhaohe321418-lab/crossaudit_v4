# Study 10 — slice 4: E5 and E6, the two folds that cannot shorten a token

Preregistered **before any line of `src/` was touched**, on `feat/provenance-slice-4`
(branched from `fusion/evidence-authority` at 815ee02, after Arm 4). Binding:
`docs/design/CONTAINMENT_RULE.md` §2 (E5, E6) and §3, `RESULTS-GOLD.md` (E5 and E6
licensed, W = 0), D160 ruling 2 (the order: E5 + E6, then E1, then E2), D161 ruling 2.

Arm 4 killed the shipped check on §8g; six of its nine wrong blocks are E1 and E2 and
none is E5 or E6. This slice ships E5 and E6 first because D160 fixed that order and
because E5 is a prerequisite for E2: a list distributing `wt.%` needs the token read
whole. The rows Arm 4 found are not this slice's test; the frozen gold is.

**M10 is deferred**, stated here so it is not silently dropped. An EN DASH exponent
(`h–1`) has the same surface as a closed-up range written with an en dash between a
unit and the next value (`5 g–10 g`, `20°C–25°C`): a letter, an en dash, digits. The
gold holds **zero** lines of the `<letter>–<digit>` shape, so W for that class cannot
be measured on it, and D161 ruling 2 requires its own gold rows and its own W = 0. It
gets its own study with a designed negative panel of en-dash ranges.

---

## 1. The two rules, verbatim from the design

**E5** (`CONTAINMENT_RULE.md` §2): in `_scan`, a period continues the token when the
next character is alphanumeric **or** `%` / `‰`. Today `80 wt.%` scans as `wt` and the
annotation `wt.%` blocks; `wt` — a prefix — passes.

**E6**: before comparison only, and on **both** sides, fold superscript digits and
signs (`⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻`) to ASCII and U+2212 to `-`. `SYNONYMS` stays fixed. The fold is
applied to the comparison and **not** to `_UNPARSED`, which needs raw superscripts to
see `10⁵` as notation it cannot parse. Today `0.22 s−1` annotated `s⁻¹` blocks, and
`0.5 dm3/s` annotated `dm³/s` blocks.

Both are folds that make a token longer or make two renderings one; neither can make a
reading shorter than the whole token, and neither touches the unit table.

### 1a. Where each lives

* E5: one branch in `_scan` — the set of characters a period may precede inside a
  token grows from "alphanumeric" to "alphanumeric or `%`/`‰`", as a named constant so
  the study's ablation can empty it.
* E6: one function, `_unit_key`, applied to both the candidate and the transcribed
  unit at the single comparison in `pair_occurrences`. `normalise_unit` — used by the
  fragment table, the boundary rule and the range split — is **not** changed, so the
  fold reaches nothing but the comparison.

## 2. The corpus

The frozen gold (`study8gold/`): 300 items, 53 blocks, 150 passes, 97 wrong-location
panel draws; labels `GOLD.csv`; the sheet in the archive. The baseline is **the merge
base's own verdict on every item**, frozen at `study10/base-verdicts.jsonl` (ids and
verdicts only) from `contains_pair` at 815ee02 (matcher blob `8dfd07d9…`) before this
file was committed — 149 passes, 151 blocks; it differs from `study8gold/key.jsonl`'s
pre-slice-3 column on exactly the 17 rows slice 3 moved.

## 3. The statistic, and the kill

`CONTAINMENT_RULE.md` §3 and study 9 §3, unchanged: R, W, R′, W′ over the base
verdicts, panel included. **W must be 0 and W′ must be 0**, for each fold alone and
for the two composed. The 10 gold-right blocks must still block. The panel's
coincidental-containment count must stay 2 of 97.

## 4. What I expect, before running

* **E5 alone**: R = **1** (the `80 wt.%` row, gold C; the other three `wt.%` rows on
  the same line are list members and need E2), W = 0. **R′ = 0 or 1**: the design says
  `wt` against `80 wt.%` "is a pass today that must become a block"; whether the gold
  holds such a row is not known to me at this writing and is read off the run, not
  arranged. W′ = 0.
* **E6 alone**: R = **2** (`s⁻¹` against a source writing `s-1`/`s−1`; `dm³/s` against
  `dm3/s`), W = 0, R′ = 0, W′ = 0.
* **Composed**: R = 3, W = 0, R′ = the E5 figure, W′ = 0; all 10 right blocks block;
  panel 2 of 97.
* If any expectation misses, the miss is reported as a miss; nothing is tuned.

## 5. The adversarial cases the gold cannot supply, each a committed test

E5: `80 wt.%` reads `wt.%` (green after), `wt` against it is red after (a prefix), a
period before a space or a letter-less end still ends the token (`5 g.` → `g`), a
period before a letter still continues (`kg.m`), `5 %.` reads `%`. E6: `s⁻¹` / `s−1`
/ `s-1` are one unit on both sides; `s⁻²` against `s⁻¹` red; `10⁵` stays unparsed
notation (the `_UNPARSED` mirror); a superscript footnote `sample¹` stays prose; the
fold does not reach `_is_boundary` or the fragment table (`m²` continues as before, by
its own rule).

## 6. The D64 mutations, each shipped with its mirror

| mutation | what must redden |
|---|---|
| empty the period-continuer set (E5 off) | `80 wt.%` annotated `wt.%` |
| make `_unit_key` the identity (E6 off) | `0.22 s−1` annotated `s⁻¹`; `0.5 dm3/s` annotated `dm³/s` |
| apply the fold to `_UNPARSED`'s input | the `10⁵` notation mirror |
| fold `−` inside `normalise_unit` instead of `_unit_key` | the boundary/fragment mirrors that must not move |

## 7. What else must hold

`dcl/` only; no change under `auditor/`, `broker/`, `ledger/`, `policy/`;
`number_source` in no profile (D161 ruling 1); the contract string and the skill say
what E5 and E6 do in one sentence each, bound by the phrase-and-behaviour test
(`DISCLOSED_LIMITS` gains rows for both); the full suite green on the host (baseline
after Arm 4: 3762 passed / 4 skipped); `benchmarks/` green; the gold re-measured with
`study10/measure.py`, which imports the shipped `contains_pair` and ablates each fold by
monkeypatching its named hook, never by re-implementing the matcher.

## 8. Reproduction

```
PYTHONPATH=src .venv/bin/python benchmarks/expertlongbench/study10/measure.py \
    --sheet ~/Documents/Crossaudit/study-data/gold-containment/sheet.jsonl \
    --config {shipped|e5|e6}
```
