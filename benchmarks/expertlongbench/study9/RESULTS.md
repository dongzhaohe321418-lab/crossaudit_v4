# Study 9 — measured: the spaced-unit narrowing and E4

Preregistered in `PREREGISTRATION.md` (committed `085379b`, before any line of
`src/` was touched). Measured on the **shipped** matcher with
`study9/measure.py`, which imports `crossaudit.dcl.numbers.contains_pair` and
compares it row for row against the merge base's verdict frozen in
`study8gold/key.jsonl` (`matcher`), verified equal to the merge base's live
`contains_pair` on 300 of 300 before the first edit.

```
PYTHONPATH=src .venv/bin/python benchmarks/expertlongbench/study9/measure.py \
    --config {narrowing|e4|shipped} \
    --sheet ~/Documents/Crossaudit/study-data/gold-containment/sheet.jsonl
```

`--config narrowing` and `--config e4` measure each half alone by replacing the
one shipped function that carries both — the D64 device, used as an instrument.

## 1. Preregistered against measured

| | | R | W | R′ | W′ |
|---|---|---|---|---|---|
| **narrowing** (half 1 alone) | preregistered | 0 | 0 | **9**, secondary 11 | **0** |
| | **measured** | 0 | 0 | **11** | **2** |
| **E4** (half 2 alone) | preregistered | **6** | **0** | 0 | 0 |
| | **measured** | **6** | **0** | 0 | 0 |
| **both, as shipped** | preregistered | **6** | **0** | 11 | **0** |
| | **measured** | **6** | **0** | **11** | **0** |

`R` = blocks the change turns into passes that the gold labels `C`; `W` = the
same turned passes that the gold labels `N` (**the kill: W must be 0**); `R′` =
passes turned into blocks that the gold labels `N` (wrong passes removed); `W′`
= passes turned into blocks that the gold labels `C` (wrong blocks added, **the
narrowing's kill**).

**As shipped, W = 0 and W′ = 0. Neither kill fires.**

* **The 10 gold-right blocks all still block**, 10 of 10 (M1b ×3, M7 ×3, M8 ×2,
  M9a ×1, M9b ×1). This is the claim "additive in `dcl/`" makes, measured rather
  than argued: no previously-blocked wrong annotation passes.
* **The panel is untouched**: 2 of 97 wrong-location draws contain their pair,
  unchanged from the merge base, and neither is a wrong containment — so the
  line-scoped coincidental-containment rate stays 2.06% [0.57, 7.21], inside
  `PROVENANCE_CHECKS.md` §6's preregistered ≤ 5%.
* R′ = **11**, the secondary prediction, not 9. The two beyond D160's nine are
  `%` transcribed against `20% vol/vol ethanol` (G0177, G0291) — the gold's
  other two false passes, reached because `vol/vol` carries a solidus and R6a
  (Amendment 1) puts a basis qualifier inside the unit expression. **The shipped
  matcher's false-pass class is closed entirely on this corpus: 11 of 11.**

## 2. The finding: half 1 alone fails its own kill, and that is the argument for shipping them together

`--config narrowing` measures **W′ = 2**. The two rows are `10 wt %` (G0092) and
`1.8 wt %` (G0189), annotated `wt %` and gold-labelled `C`. The narrowing takes
the bare `wt` away as a reading, and until E4 offers the join there is nothing
left to satisfy a correct `wt %` — the shipped percent split
(`_unit_candidates`, the `wt %` special case) was the only reading of a spaced
unit the matcher had.

D160 ruling 2 says E4 ships "together with the narrowing since they are two
halves of one rule". **This is that ruling measured.** Half 1 alone is not a
shippable state, it is a stricter matcher that loses two correct passes; half 2
alone (R = 6, W = 0) leaves the false-pass class open exactly as
`RESULTS-GOLD.md` §3 said it would ("the bare-prefix candidate survives beside
it"). Only the composition has both kills clear, and it is the composition that
ships.

## 3. What the gold could not decide, and what carries it instead

`RESULTS-GOLD.md` **Amendment 2**: `W = 0` on this gold is *no evidence
against*, not *no regression*. The gold is a kill screen for the six classes of
`CONTAINMENT_RULE.md` §1 and the wrong-location panel. Of the classes this slice
touches it covers exactly one — a spaced unit of the shape `°C min⁻¹`, `mg h⁻¹`,
`K min⁻¹`, `°C min-1`, `°C min−1` (17 rows in all) — and **it contains no
instance at all** of:

* a bare **word** after a unit (`5 g sample`, `2 h later`, `5 g of powder`);
* a **plain unit symbol** as a continuation (`5 kg m`);
* an **element symbol** after a percentage (`5 wt % Ni`);
* a **preposition that is also a unit symbol** (`10 g at 300 °C`, `5 mL in
  water`);
* a continuation-shaped token that is **prose** (`5 h (heating/cooling rate)`);
* a continuation across a **line break**.

Those ship as the slice's own adversarial cases,
`tests/test_number_source_check.py::SPACED_UNITS` and the four tests beside it,
asserted through **both** interfaces — the fence and a `results.json` quantity
with a `#L` fragment.

One of them was found by the gold rather than by the table: the first build of
`_continues_unit` had no bracket guard, `(heating/cooling` carries a solidus,
and G0105's correct `(5, h)` became a block — **W′ = 1 that the gold caught and
no adversarial case of mine had anticipated.** The guard and its mirror
(`5 h (heating/cooling rate)`, `5 g heating/cooling`) ship together.

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
