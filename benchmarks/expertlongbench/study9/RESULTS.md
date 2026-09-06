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

**The shipped rule, E4 alone and the narrowing alone clear both kills: W = 0 and
W′ = 0 in each. The over-strong ablation does not (W′ = 2); §2 records why that
number measures the instrument and not the narrowing.**

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
* a continuation across a **line break**;
* an **unnamed fragment of four or more letters** after a join (`5 kg m mmHg`),
  or a substance or a marked word after one (`5 wt % K`, `5 wt % batch-1`).

*A correction to round 1 of this file:* it said the gold contains no bracketed
continuation prose. **It does** — G0105, `… for 5 h (heating/cooling rate 5 °C
min⁻¹)`, is exactly that, and it is the row that caught the first build's
missing guard. The sentence was wrong and the row is the counterexample it names
three paragraphs later.

Those classes ship as the slice's own adversarial cases,
`tests/test_number_source_check.py::SPACED_UNITS` (44 rows, both interfaces),
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

Round 1 claimed omissions "fail toward today's behaviour"; round 2 claimed that
after a join an omission is a block. **Both were example-driven, and the second
review showed the second holds only for a fragment of one to three lower-case
letters or a marked one** (`s`, `sr`, `K⁻¹`): removing `mbar`, `Torr`, `sccm`
or `µmol` from the table makes `5 kg m <fragment>` offer `kg m`, because an
alphabetic token of four or more letters, or a capitalised one, reads as prose —
and nothing on the surface separates `mmHg` from `sample`. That is the base's
own class at the first continuation (`5 g mmHg` has always offered `g`), reached
after a join by the same rule; not a new one. A generated test now removes every
one of the table's 112 entries in turn: **18 are guarded by the table alone** —
`Bq GHz GPa Gy Hz MHz MPa MeV Sv Torr Wb mbar mmol nmol sccm torr µmol μmol` —
pinned as a literal so an addition to that class is a visible change; the other
94 block when unnamed, and with its fragment unnamed the whole expression never
reads in either class. The contract, the shipped skill and `_is_boundary` state
the limit in the same words.

Four entries in the round-1 table were redundant and are gone: `hour`, `hours`,
`minute` and `minutes`, folded by `normalise_unit` (`_fragment` consults it).
`µm` and `μm` both stay — the folding runs one way, and the generated test shows
`µm` still named when removed for exactly that reason — and `%`/`‰` stay because
they are load-bearing for `wt %` under the structural test. Round 2 of this file
said seven entries; that was wrong.

### What the second review found, and what it changed

1. **The substance test came after the fragment table** (P1). `_continues_unit`
   refuses a bare element or capital, so `K` after `5 wt %` reached
   `_is_boundary` — which asked the table first, found `K` named (for `K⁻¹`),
   and called it a unit it could not read: `5 wt % K`, `5 wt % Pa`, `5 wt % A`
   blocked `wt %` where `5 wt % Ni` passed, **15 of the 118 elements** (`B C F H
   I K N O P Pa S U V W Y`). After `5 g` the first-continuation path never asks,
   which is why the 118-element loop was green while this was red. The order is
   now the first continuation's — substance or label first, then the table — and
   every element and every capital is asserted after both joins.
2. **Marked prose blocked after a join** (P1). `wet/dry`, `batch-1`, `sample¹`,
   `A2`, `Li₂O`, `H2O` — the forms round 2 had just taught the first
   continuation to read as words — fell through `_is_boundary`'s alphabetic test
   and blocked `wt %`. `_is_boundary` now **enumerates the prose shapes** and
   blocks whatever is left; the mirrors (`xyz⁻¹`, `g/xyz`, `qz`, `°X`) still
   block. One consequence is disclosed rather than argued away: `run-2` blocks
   after a join, because a three-letter stem under an exponent is the shape of
   `s-1`.
3. **The cap fired before the boundary test** (P2). A complete six-token
   expression blocked whenever anything followed it on the line — ` sample`,
   ` 10 s`, ` (dry)` — while a comma read. The cap is now consulted only when a
   seventh fragment would join; then, as before, nothing reads. That a valid
   seven-token expression cannot be read at all is a readability limit of the
   cap, stated here; it is not a false pass.
4. **The omission claim, narrowed** — the paragraph above.
5. **Three sentences of this file were false** and are corrected in place:
   "every configuration clears both kills" (the over-strong ablation does not,
   W′ = 2, §2); "seven redundant entries are gone" (four); "36 rows" (44).

Re-measured after the fix, the table in §1 is unchanged to the row: shipped
R = 6, W = 0, R′ = 11, W′ = 0; E4 6/0/0/0; narrowing-prefix-only 0/0/11/0;
narrowing-all-spaced 0/0/11/2; 10 of 10 gold-right blocks; panel 2 of 97. The
gold holds no instance of any of the three shapes, which is why it could not
have found them (the list above).

### What the third review found, and what it changed

1. **A solidus joining nothing but short unknown parts read as prose** (P1).
   `5 kg m oz/yd` offered `kg m` through every interface, against this file's
   own sentence that a short or marked unknown fragment blocks; `m2` and `m₂`
   did the same through the digit rule. Both shapes now block after a join.
   **The cost is a false block, disclosed**: `wet/dry` and `x/y` are the same
   shape as `oz/yd` — two short lower-case parts on a solidus — and nothing
   on the surface separates two three-letter words from two unnamed symbols,
   so after a join they block too, in the safe direction. At the first
   continuation they end the unit exactly as before (`5 g wet/dry sample`
   still passes `g`), asserted beside the block.
2. **Ordinary prose blocked after a join, one row a regression against the
   base** (P1). `5 wt % high-purity powder` passed `wt %` on the base and
   blocked on round 3; `e.g.`, `sample，` (a trailing full-width comma the
   scanner keeps) and `样品` blocked with it. The enumerated grammar was too
   short: it now names hyphenated and apostrophised words with a word among
   their parts, single-letter abbreviations, words in a script that writes no
   unit symbol, and trailing punctuation as prose — and `kg-m`, short stems on
   a hyphen, as a unit shape that blocks.
3. **The disclosure was present but not bound** (P2). The words-say-what-the-
   scanner-does test asserts phrases, which binds presence, not truth.
   `DISCLOSED_LIMITS` now lists every limit sentence beside the row that
   makes it true, in the contract and in the skill, and each row asserts both.

Re-measured after this round, again unchanged to the row: shipped R = 6, W = 0,
R′ = 11, W′ = 0; E4 6/0/0/0; narrowing-prefix-only 0/0/11/0; narrowing-all-spaced
0/0/11/2. `tests/test_number_source_check.py` 894 passed.

### What the fourth review found, and what it changed

1. **`a.u.` read as prose** (P1). The single-letter-abbreviation rule that made
   `e.g.` a word made arbitrary units one too, and `5 kg m a.u. signal` offered
   `kg m`. A dotted abbreviation is now a word only if this module names it
   (`e.g.`, `i.e.`, `a.m.`, `p.m.`, `n.b.`, `c.f.`); any other run of dotted
   letters — `a.u.`, `p.u.`, `r.u.` — is a unit symbol and blocks after a join.
2. **Contractions blocked, a regression against the base** (P1). `_scan` splits
   at an apostrophe, so `_is_boundary` saw `we` and not `we're`, and the
   apostrophe rule the contract promised could never run. `_spaced_unit` now
   reads a letter directly after an apostrophe as a contraction and ends the
   unit there. The other undisclosed base-pass regressions the review found —
   `α`, `pH`, `sample%`, `sample_name`, and three-letter words such as `dry` —
   are prose by rule now (a bare Greek letter other than `µ`/`Ω`; a percent
   sign on a long stem; underscores as hyphens), and by a short named list of
   common words (`dry wet raw hot old new mix air gas oil ice ash sol gel wax
   dye pH etc cf vs`) for the three-letter class, whose remainder (`qz`) blocks
   and is disclosed and bound as a row. The same list makes `wet/dry` read as
   a word pair after a join, so round 3's disclosed false block on it is gone;
   `oz/yd` and `x/y` still block.
3. **Five of ten disclosure rows skipped the skill** (P2). The skill now names
   every shape, and every row of `DISCLOSED_LIMITS` asserts a contract phrase,
   a skill phrase and the behaviour.

Re-measured after this round, unchanged to the row: shipped R = 6, W = 0, R′ = 11,
W′ = 0; E4 6/0/0/0; narrowing-prefix-only 0/0/11/0; narrowing-all-spaced 0/0/11/2.
`tests/test_number_source_check.py` 908 passed.

### What the fifth review found, and what it changed

1. **A named short word with a percent sign blocked** (P1): `5 wt % dry% powder`
   blocked `wt %` because the percent-sign branch tested length instead of
   `_word()`. It uses `_word()` now, and `dry%`, `wet‰` read; `abc%` blocks
   and is disclosed. Short parts on an underscore (`lot_id`) and on a middle
   dot (`oz·yd`) blocked as the hyphen and solidus shapes do, but the
   disclosure named only hyphens and solidi; it names all four joiners now.
2. **The abbreviation list had six entries and the words said four** (P2):
   `n.b.` and `c.f.` read as words while the contract and skill said only
   `e.g.`, `i.e.`, `a.m.`, `p.m.` did. Both now list all six, and a row binds
   `n.b.`.
3. `DISCLOSED_LIMITS` grows to 20 rows, each a contract phrase, a skill phrase
   (compared whitespace-normalised, so line wrapping is not a claim) and the
   behaviour; the trailing-punctuation row gains `样品。`.

Re-measured after this round, unchanged to the row: shipped R = 6, W = 0, R′ = 11,
W′ = 0; E4 6/0/0/0; narrowing-prefix-only 0/0/11/0; narrowing-all-spaced 0/0/11/2.
`tests/test_number_source_check.py` 924 passed.

### What the sixth review found, and what it changed

1. **A digit added to a disclosed blocker made it pass** (P1): `5 kg m lot_id/2`
   offered `kg m`, because "any digit is prose" ran before the joiners were
   read. The joiners are read first now: a joined token blocks when any part
   is a unit fragment (`dry·g`, `kg-m/s`) or when no part is a word (`lot_id/2`,
   `oz/yd/2`, `qz/2`); `batch-1/2` reads because `batch` is a word; `H2O` and
   `Li₂O`, with no joiner, still read by the digit.
2. **The percent branch bypassed the element refusal** (P1): `5 kg m Ni‰`
   offered `kg m` for all 118 elements. The branch keeps the refusal; every
   element with `%` and `‰` is asserted after a join.
3. **Disclosure gaps** (P2): `oz⋅yd`, per-mille, the capitalised half of the
   unknown-fragment limit (`GBq`), `kg-m/s`, `dry·g`, `lot_id/2` and full-width
   joiners (`kg／m`, `kg－m`, `lot＿id`, `oz／yd`, `dry／wet`, which are not joiners
   this module reads and block) are now named in the contract, the skill,
   `_is_boundary` and the tests; `DISCLOSED_LIMITS` has 30 rows.

Re-measured after this round, unchanged to the row: shipped R = 6, W = 0, R′ = 11,
W′ = 0; E4 6/0/0/0; narrowing-prefix-only 0/0/11/0; narrowing-all-spaced 0/0/11/2.
`tests/test_number_source_check.py` 951 passed.

### What the seventh review found, and what it changed

1. **The numeral exit ran before the joiners** (P1): `5 kg m 2/g` offered
   `kg m`, because a digit-leading token is a numeral before anything else is
   asked. A digit-leading token is now split on the joiners first, and blocks
   when a part is a unit fragment (`2/g`, `2/kg`); `10` and `2/dry` stay
   numerals and labels.
2. **A full-width joiner beside ASCII ones was hidden by the ASCII split**
   (P1): `kg／m/dry` split into `kg／m` and `dry`, and the word made the token
   prose. A full-width joiner anywhere in the token now blocks before anything
   else is asked (`kg／m/dry`, `kg－m/batch`, `lot＿id/batch`, `oz／yd-batch`,
   `dry／wet-batch`, `2／g`).
3. **Disclosure** (P2): `g/xyz` and `2/g` have rows; the full-width class is
   named in the contract, the skill and `_is_boundary` with `kg／m` and
   `kg／m/dry` as its exemplars, and all five of the sixth review's full-width
   examples plus the six mixed ones are rows or listed unreadable tokens. This
   file's earlier sentence that all five were named in the contract was wrong
   — one was.

The eighth review found no behavioural bypass and one disclosure gap: the
commit said 40 rows where 38 existed, and two limits the contract states —
more tokens than the scanner reads, and an operator with nothing after it —
had no row and no skill sentence of their own. The skill names both, each has
rows, and the row count — 42, read from the test file rather than claimed — is
the table's own.

Re-measured after this round, unchanged to the row: shipped R = 6, W = 0, R′ = 11,
W′ = 0; E4 6/0/0/0; narrowing-prefix-only 0/0/11/0; narrowing-all-spaced 0/0/11/2.
`tests/test_number_source_check.py` 971 passed.

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
