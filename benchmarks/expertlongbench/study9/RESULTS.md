# Study 9 — measured: the spaced-unit narrowing and E4

Preregistered in `PREREGISTRATION.md` (committed `085379b`, before any line of
`src/` was touched). Measured on the **shipped** matcher with
`study9/measure.py`, which imports `crossaudit.dcl.numbers.contains_pair` and
compares it row for row against the merge base's verdict frozen in
`study8gold/key.jsonl` (`matcher`), verified equal to the merge base's live
`contains_pair` on 300 of 300 before the first edit.

```
PYTHONPATH=src .venv/bin/python benchmarks/expertlongbench/study9/measure.py \
    --config {shipped|e4|narrowing-prefix-only|narrowing-all-spaced} \
    --sheet ~/Documents/Crossaudit/study-data/gold-containment/sheet.jsonl
```

Each half is measured alone by replacing the one shipped function that carries
both — the D64 device, used as an instrument. §2 says exactly what each ablation
subtracts, because round 1 of this report did not and got a claim wrong for it.

## 1. Preregistered against measured

*Round 2. The numbers below are measured on the code after independent review
refused the first build (two P1s and a P2, `codex-review-s3/report.md`). The
gold numbers were unchanged by the repair; §2 and §3 record what the review
changed.*

| | | R | W | R′ | W′ |
|---|---|---|---|---|---|
| **narrowing** (half 1 alone, prefix-only ablation) | preregistered | 0 | 0 | **9**, secondary 11 | **0** |
| | **measured** | 0 | 0 | **11** | **0** |
| *the same, over-strong ablation (see §2)* | | 0 | 0 | 11 | *2* |
| **E4** (half 2 alone) | preregistered | **6** | **0** | 0 | 0 |
| | **measured** | **6** | **0** | 0 | 0 |
| **both, as shipped** | preregistered | **6** | **0** | 11 | **0** |
| | **measured** | **6** | **0** | **11** | **0** |

`R` = blocks the change turns into passes that the gold labels `C`; `W` = the
same turned passes that the gold labels `N` (**the kill: W must be 0**); `R′` =
passes turned into blocks that the gold labels `N` (wrong passes removed); `W′`
= passes turned into blocks that the gold labels `C` (wrong blocks added, **the
narrowing's kill**).

**Every configuration clears both kills. W = 0 and W′ = 0 throughout.**

* **The 10 gold-right blocks all still block**, 10 of 10 (M1b ×3, M7 ×3, M8 ×2,
  M9a ×1, M9b ×1). This is the claim "additive in `dcl/`" makes, measured rather
  than argued: no previously-blocked wrong annotation passes.
* **The panel is untouched**: 2 of 97 wrong-location draws contain their pair,
  unchanged from the merge base, and neither is a wrong containment — so the
  line-scoped coincidental-containment rate stays 2.06% [0.57, 7.21], inside
  `PROVENANCE_CHECKS.md` §6's preregistered ≤ 5%.
* R′ = **11**, the secondary prediction, not 9. The two beyond D160's nine are
  `%` transcribed against `20% vol/vol ethanol` (G0177, G0291) — the gold's
  other two false passes, reached because `vol/vol` parses as two named
  fragments joined by a solidus and R6a (Amendment 1) puts a basis qualifier
  inside the unit expression. **The shipped matcher's false-pass class is closed
  entirely on this corpus: 11 of 11.**

## 2. The ablation, described as performed — and a claim withdrawn

Round 1 of this report said *"half 1 alone fails its own kill (W′ = 2)"* and
built an argument on it. **That claim is withdrawn.** It was an artefact of the
ablation, not a property of the narrowing, and the review found it.

`--config narrowing-all-spaced` deletes **every** candidate wherever the source
writes a spaced unit — including the base's own, already-valid whole `wt %`
reading, which the narrowing does not touch. Its W′ = 2 (G0092, G0189, both
`wt %`) reproduces, and it measures the instrument.

`--config narrowing-prefix-only` subtracts from the base's candidate set only
the readings that are a strict **prefix** of the whole spaced expression, adds
nothing, and is what "the narrowing alone" means. It measures **R = 0, W = 0,
R′ = 11, W′ = 0** — independently obtained by the reviewer before this file was
corrected. **The narrowing alone clears its kill.** Both configurations stay in
`measure.py` so the over-strong one is on the record rather than deleted.

What survives of the original point is smaller and is not about a kill: E4 alone
(R = 6, W = 0) leaves the false-pass class open exactly as `RESULTS-GOLD.md` §3
predicted ("the bare-prefix candidate survives beside it"), and the narrowing
alone removes no wrong block. D160 ruling 2's "two halves of one rule" is a
statement about what the check is *for*, and it did not need a false kill to
support it.

## 3. What the gold could not decide, and what carries it instead

`RESULTS-GOLD.md` **Amendment 2**: `W = 0` on this gold is *no evidence
against*, not *no regression*. The gold is a kill screen for the six classes of
`CONTAINMENT_RULE.md` §1 and the wrong-location panel. Of the classes this slice
touches it covers one — a spaced unit of the shape `°C min⁻¹`, `mg h⁻¹`,
`K min⁻¹`, `°C min-1`, `°C min−1` (17 rows in all) — and **it contains no
instance at all** of:

* a bare **word** after a unit (`5 g sample`, `2 h later`, `5 g of powder`);
* a **plain unit symbol** as a continuation (`5 kg m`);
* an **element symbol** after a percentage or a mass (`5 wt % Ni`, `5 g K`);
* a **preposition that is also a unit symbol** (`10 g at 300 °C`, `5 mL in
  water`);
* **short prose carrying a marker** (`5 g wet/dry sample`, `5 g batch-1`,
  `5 g sample¹`);
* a spaced expression the matcher **cannot read to its end** (`5 g / 100 mL`,
  `5 kg m qz`, seven tokens);
* a continuation across a **line break**.

*A correction to round 1 of this file:* it said the gold contains no bracketed
continuation prose. **It does** — G0105, `… for 5 h (heating/cooling rate 5 °C
min⁻¹)`, is exactly that, and it is the row that caught the first build's
missing guard. The sentence was wrong and the row is the counterexample it names
three paragraphs later.

Those classes ship as the slice's own adversarial cases,
`tests/test_number_source_check.py::SPACED_UNITS` (36 rows, both interfaces),
`STOPPED_SCANS`, the 2–20-token sweep, and the three continuation tests beside
them.

### What review found that neither the gold nor round 1's table did

1. **A stopped scan was offered as a complete unit** (P1). The scan stopped at
   the token cap, at an operator with nothing after it, or at a token it could
   not read, and the join built so far was handed back as the whole unit:
   `5 kg m sr` satisfied `kg m`, `5 g / 100 mL` satisfied `g /`, and expressions
   of 7 to 20 tokens **all** accepted their first six. That is "a prefix never
   satisfies" defeated a fourth time, on the join instead of the token. The rule
   now: once a join has begun the expression is a candidate **only if the scan
   ended at a true boundary** — prose, a numeral, an opening bracket, punctuation
   or the end of the line. A cap, an operator, or an unnamed fragment ends it
   with **no candidate**, so the row blocks.
2. **Short prose carrying a marker was read as a unit** (P1). Testing for a
   marker *anywhere in the token* made `wet/dry`, `batch-1` and `sample¹`
   continuations, blocking three correct `(5, g)` annotations. A continuation is
   now **unit-shaped in itself**: a named fragment, a fragment with an exponent
   attached, or such atoms joined by a solidus or middle dot. The bracket and
   length guards round 1 added are gone — they were guessing at a boundary that
   is not length.
3. **A bare element symbol is not a unit.** `K`, `Pa`, `N`, `C`, `S`, `P`, `H`,
   `O`, `F`, `B`, `V`, `W`, `Y`, `I`, `U` and every other element symbol, and any
   bare capital, now need a structural marker to continue: `5 g K` is potassium
   and `5 g A` is a labelled batch, while `5 J K⁻¹` still reads `K⁻¹`. The
   collision set is the full 118-symbol table, so it is exact rather than
   guessed.

### The fragment table's incompleteness, stated correctly

Round 1 claimed omissions "fail toward today's behaviour". **That is true only
before a join has begun.** After one, an omitted fragment means the scan cannot
reach a boundary, and the shipped rule makes that a **block**, not a pass — the
reviewer's `5 kg m sr` is the witness. The contract now says this. Seven entries
in the round-1 table were redundant and are gone: `hour`, `hours`, `minute`,
`minutes` and `µm` are covered by `normalise_unit`'s synonym folding (`_fragment`
consults it), and `%`/`‰` stay because they are load-bearing for `wt %` under
the new structural test.

### Out of scope, noted for a later extension

Two limitations the reviewer confirmed are **pre-existing and untouched here**:
`5 % (w/w)` passes `%` (the bracketed basis is unreadable, and `% (w/w)` blocks),
and `5 mg per kg` passes `mg` while the whole expression blocks (`per` is
deliberately a stopword, so an English-word operator is not a continuation).
Both belong to a later extension, with their own gold measurement.

## 4. The gold's own simulator, after this slice

`study8gold/simulate.py` asserts on every run that with no extension flag set it
reproduces the shipped `contains_pair` on all 300 items. **That invariant is now
false and reports 283/300**, and the 17 mismatches are exactly this slice's 6 R
and 11 R′ rows. It is not a defect in either: the simulator models the matcher
as it stood when the gold was labelled, and the matcher has moved. The gold's
labels are unaffected — they are labels about text, not about code — and
`study9/measure.py` is the instrument for any measurement taken after this
slice. Recorded as `RESULTS-GOLD.md` Amendment 3.

## 5. Cost

$0. No generation, no model calls, no new corpus. The frozen sheet is read-only
and nothing under `study8gold/` is modified except the appended amendment.
