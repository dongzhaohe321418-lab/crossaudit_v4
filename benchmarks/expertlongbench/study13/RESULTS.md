# Study 13 — results: E3, a decimal stoichiometric subscript

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
E3 and disclosure selections (`red-run.txt`). After: `tests/test_number_source_check.py`
**1165 passed** (1124 + 41: 30 E3 rows, three E3 tests, eight disclosure rows). Each
mutation and the row it reddens:

| mutation | row |
|---|---|
| empty `_SUBSCRIPT` (E3 off) | `LiNi0.8Co0.2O2` (0.8), `SrCo0.6Fe0.4O3−δ` (0.6) redden; the ordinary scan, E1, E2 hold |
| read integer subscripts | `H2O` with `(2, "")` goes green |
| drop the letter-before guard | `x²0.5` with `(0.5, "")` goes green |
| drop the charset guard | `run_v1.5` with `(1.5, "")` goes green |
| yield for a transcribed unit | `(0.8, M)` against `LiNi0.8Co0.2O2` — held red by its row and by the `pair_occurrences` interval test |

## 4. Two things the run taught that the preregistration did not say

* **The letter-before guard's independent reach is small.** §5 named `Fig.3.2` as its
  mirror; it is not, because the charset guard already refuses the period, and the ordinary
  scan already reads a number after any character that is not a word character or a period
  (`Zr(HPO4)0.5·H2O`, `Co(NO3)2·6H2O`, `O3−0.5` all pass *without* E3 — three rows were
  corrected to say so). What the letter guard alone refuses is a non-letter alphanumeric:
  `x²0.5`. The hook's lookbehind is `(?<![0-9.])` and the letter test is the named function
  `_glued_to_letter`, so the mutation is real and its row is `x²0.5`. Recorded here, not
  edited into the preregistration.
* **`Co(NO3)2·6H2O` with `(6, "")` passes, and always did**: the middle dot is not a word
  character, so the ordinary scan reads the hydrate count. Not E3's, not this slice's; a
  reader of the E3 rows should not take that row for a subscript reading.

## 5. What is pinned in words

Contract clauses, each bound to a row: "decimal stoichiometric subscript", "with the
empty unit" (the `(0.8, M)` row), "an integer subscript", "'3' in 'Cr2O3'", "the '−δ' /
'±δ' marker", "'x=Ni0.5'", "'run_v1.5'", "weakest match this check makes". Skill phrases:
"decimal stoichiometric subscript", "with the empty unit", "integer subscript", "`3` in
`Cr2O3`", "`−δ` marker", "`x=Ni0.5`", "`run_v1.5`", "weakest match the checker makes".
Any other wording in either text is not pinned by a row.

## 6. What else held

`git diff 7a26ac1..HEAD -- src` touches `dcl/numbers.py` and the skill template only;
kernel dirs untouched; `number_source` in no profile. Full suite on the branch: see §7.

## 7. Full suite

`3952 passed, 4 skipped, 6 warnings in 388.57s (0:06:28)` (full suite in the slice-7 worktree, after the implementation).
