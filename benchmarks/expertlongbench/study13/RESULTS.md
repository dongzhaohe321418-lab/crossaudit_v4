# Study 13 — results: E3, a decimal stoichiometric subscript

*Third version, after the first and second reviews' findings (PREREGISTRATION Amendments 1 and 2). The numbers in §1 and §2 did not move in either rebuild; §3–§5 describe the round-3 build.*

Measured after the implementation, against the expectation in `PREREGISTRATION.md`
(committed at e28256b, before `src/` was touched). Sheet: the frozen gold, 300 items;
baseline `base-verdicts.jsonl` (171 passes, code 7a26ac1).

## 1. The gold

```
config shipped   items 300   R 11   W 0   R' 0   W' 0
kill conditions clear (W = 0 and W' = 0)
gold-right blocks still blocking: 10/10
panel: 2/97 contained, of which gold-wrong 0
config base      items 300   R 0    W 0   R' 0   W' 0     head == frozen base on 300 of 300
```

R = 11, exactly the eleven rows §4 named: G0001, G0063, G0082, G0110, G0113, G0120, G0159,
G0196, G0203, G0213, G0267 — every one gold C, every one an empty-unit row, every one a
decimal inside a formula token. G0110 and G0120 are the `−δ` rows of §1a. W = 0, R′ = 0,
W′ = 0; the ten gold-right blocks still block; the panel is unchanged at 2 of 97 with no
gold-N draw newly contained. G0192 and G0206 (integer subscripts, gold C) stay blocked, as
preregistered: two wrong blocks E3 leaves by design.

## 2. E3's own probe (`probe.py`, output in `probe-output.txt`)

**P1 — every token E3 reads in the corpus.** 17 distinct tokens (sentence punctuation
stripped), 39 (token, value) readings, over the 50 T03 source procedures. Classified by
hand, all 17 are chemical formulae with decimal stoichiometric coefficients:
`(Li6.4La3Zr1.4Ta0.6O12)`, `Fe1.2V` (an alloy), `K0.5Na0.5(Nb0.85Ta0.15)O3`, `La2.74Te4`,
`Li0.75H1.25RuO3`, `Li1.3Al0.3Ti1.7(PO4)3`, `Li1.3Mn0.4Nb0.3O2−xFx` (the `−x` marker, `x` a
letter), `Li1.5Al0.5Ti1.5(PO4)3`, `LiNi0.8Co0.2O2`, `LiNi0.92Co0.04Mn0.04O2`,
`LiNi0.95Co0.04Mn0.01O2`, `Na3V1.20V0.80(PO4)2F2.20O0.80`, `NaNi0.8Mn0.1Co0.1O2`,
`Ni0.8Mn0.1Co0.1(OH)2`, `Ni0.92Co0.04Mn0.04(OH)2`, `Ni0.95Co0.04Mn0.01(OH)2`,
`SrCo0.6Fe0.4O3−δ`. **Other: 0.** The kill ("an *other* token whose decimal is not a
stated value") is clear — on this corpus. A materials-synthesis corpus does not write
version strings or glued figure labels; those shapes are held red by the committed rows
(`Fig.3.2`, `v1.2.3`, `run_v1.5`, `x=Ni0.5`), not by this count.

**P2 — the line-scoped coincidental rate.** 874 draft pairs from the 42 archived drafts
(16 `armT-scoped`, 26 `wt-arm4-runs`), five wrong-line draws per traced pair:

| config | all pairs | empty-unit pairs |
|---|---|---|
| base (E3 off) | 0 / 3900 = 0.00% | 0 / 2195 = 0.00% |
| shipped | 0 / 3910 = 0.00% | 0 / 2205 = 0.00% |

E3 traces two more draft pairs (ten more draws) and produces no coincidental containment.
The §6 limit (5%) is not approached. Note what this instrument can and cannot say: the
draws are lines of the *right* file; the panel of §1 is where wrong files are drawn, and it
did not move either.

**P3 — subscript decoys.** Of the 23 distinct values E3 reads, 12 are read from more than
one distinct formula (`0.04` and `0.8` from four each; ten others from two). This is the
number the skill's warning carries: a unit-free match is the weakest the check makes, and
the same digits in a different formula satisfy it, so the annotation should quote the
formula. It is not a kill and was not preregistered as one.

## 3. The D64 mutations

Before the implementation, with the tests committed first: **25 failed, 86 passed** in the
E3 and disclosure selections (`red-run.txt`, first build). After the round-3 build:
`tests/test_number_source_check.py` **1200 passed** (1124 + 76: 58 E3 rows, four E3 tests,
fourteen disclosure rows). Each mutation and the row it reddens:

| mutation | row |
|---|---|
| empty `_SUBSCRIPT` (E3 off) | `LiNi0.8Co0.2O2` (0.8), `SrCo0.6Fe0.4O3−δ` (0.6) redden; the ordinary scan, E1, E2 hold |
| read integer subscripts | `H2O` with `(2, "")` goes green |
| drop the charset guard (`_FORMULA_TOKEN`) | `x=Ni0.5` goes green (`run_v1.5` is held by the element parse as well) |
| drop the element-symbol parse (`_element_symbols`) | `Figure3.2` goes green |
| drop the any-script digit guard after the decimal (`_continued_by_digit`) | `Ni0.5２O`, `Ni0.5₂O` go green |
| drop the letter guard before it (`_glued_to_letter`) | `Ni２0.5O`, `x²0.5` go green |
| yield for a transcribed unit | `(0.8, M)` against `LiNi0.8Co0.2O2` — held red by its row and by the interval test |
| interval on the digits instead of the formula | the fenced-interface test: a quotation of `0.8` alone must raise CA-NUM-002 |
| yield after a middle dot | the interval test: `CuSO4·0.5H2O` yields the digits only, the ordinary scan's |

## 4. What the run and the reviews taught that the preregistration did not say

* **A charset is not a formula test** (round 1): the letters must parse as element symbols.
  `pH7.4` is therefore red, not green as §5 predicted. The parse is syntactic — `BaNaNa1.2`
  reads — and the words say so. The corpus census (P1) did not change.
* **The letter guard is a guard, and it has rows.** The first build's mirror (`Fig.3.2`) was
  wrong (the charset refuses the period); the second build removed the guard as having no
  row, and the second review found the row: `Ni２0.5O`, a digit of another script before the
  decimal, which the ASCII lookbehind does not see. The guard is back with that row and
  `x²0.5`. A decimal after a bracket or a middle dot (`Zr(HPO4)0.5·H2O`, `CuSO4·0.5H2O`) is
  the ordinary scan's bare-number reading, digits as the interval; E3 yields nothing there.
* **`(OH)2` with `(2, "")` passes, and always did** (round 1): the ordinary scan reads a
  bare number after a bracket or a middle dot. The words say "glued to a letter" for what
  this rule does not read, and name the bracket case.
* **Digits are not ASCII, on either side** (rounds 1 and 2): after the decimal the guard is
  `str.isnumeric`; before it the letter guard is `str.isalpha`; and letter runs are
  `str.isalpha` runs, so a subscript digit elsewhere in a formula (`LiNi0.5O₂`) is a digit.
* **The interval is the formula** (round 1), so the quotation must contain it.
* **Observed, not this slice's, and disclosed:** the ordinary scan reads a bare number
  after any character that is not a word character — including an invisible one. A
  zero-width joiner before the digits (`Ni‍0.5O`) makes `0.5` a bare-number pass in
  the frozen base; E3 refuses the token (the joiner is outside the charset) and yields
  nothing, which a row and the interval test assert. Whether the base scanner should
  treat format characters as word characters is a question for its own slice; the
  preregistration does not license touching it here.

## 5. What is pinned in words

Contract clauses, each bound to a row: "decimal stoichiometric subscript", "with the
empty unit" (the `(0.8, M)` row), "an integer subscript glued to a letter", "'3' in
'Cr2O3'", "after a bracket or a middle dot" (two rows), "the '−δ' / '±δ' marker", "parse
as element symbols", "'pH7.4'", "'x=Ni0.5'", "'run_v1.5'", "the parse is syntactic",
"weakest match this check makes", "the quotation must contain the whole formula" (its
interval half bound by the fenced-interface test). Skill phrases: "decimal stoichiometric
subscript", "with the empty unit", "integer subscript glued to a letter", "`3` in `Cr2O3`",
"after a bracket or a middle dot", "`−δ` marker", "element symbols", "`pH7.4`",
"`x=Ni0.5`", "`run_v1.5`", "spell symbols", "weakest match the checker makes", "quote the
whole formula". Any other wording in either text is not pinned by a row.

## 6. What else held

`git diff 7a26ac1..HEAD -- src` touches `dcl/numbers.py` and the skill template only;
kernel dirs untouched; `number_source` in no profile. Full suite on the branch: see §7.

## 7. Full suite

First build (fe42d31): `3952 passed, 4 skipped, 6 warnings in 388.57s (0:06:28)`. Second build (1141248): `3971 passed, 4 skipped, 1 warning in 381.56s (0:06:21)`. Third build: `3981 passed, 4 skipped, 6 warnings in 381.86s (0:06:21)` (run on the round-3 source; the six exotic-character rows were added to the test file afterwards and the focused file rerun: 1200 passed).
