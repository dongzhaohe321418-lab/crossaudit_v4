# Study 10 — slice 4: E5 and E6, measured on the frozen gold

Preregistered at `study10/PREREGISTRATION.md` (2d77378) before `src/` was touched;
baseline `study10/base-verdicts.jsonl` (the merge base 815ee02's verdict on all 300
items, matcher blob `8dfd07d9…`). Measured with `study10/measure.py`, which imports the
shipped `contains_pair` and switches a fold off by monkeypatching its named hook.

## 1. The table, with the kill applied

| configuration | R (wrong blocks removed) | W (wrong passes added, kill) | R′ | W′ (wrong blocks added, kill) | right blocks | panel |
|---|---:|---:|---:|---:|---:|---:|
| **base** (both folds off) | 0 | 0 | 0 | 0 | 10/10 | 2/97 — equals the frozen base on **300 of 300** |
| **E5 alone** | **1** (G0098, `wt.%`) | **0** | 0 | **0** | 10/10 | 2/97 |
| **E6 alone** | **2** (G0057 `s⁻¹`, G0086 `dm³/s`) | **0** | 0 | **0** | 10/10 | 2/97 |
| **shipped** (E5 + E6) | **3** | **0** | 0 | **0** | 10/10 | 2/97 |

Every preregistered expectation is met to the row: E5 R = 1, E6 R = 2, composed R = 3,
W = 0 and W′ = 0 throughout, the ten gold-right blocks still block, the panel's
coincidental-containment count is unchanged at 2 of 97, and the three rows that moved
are the three the design named (M6 ×1, M9c ×2). **R′ = 0**: the gold holds no `wt`
prefix pass against a `wt.%` source, so the narrowing E5 also performs (a prefix of
`wt.%` becomes a block) had nothing to remove here; it is asserted in the tests.

## 2. What the gold could not decide

* The other three `wt.%` rows on G0098's line (G0124, G0244, G0248) are list members
  and need E2; they stay blocked, as expected.
* Arm 4's two en-dash rows (M10) are not E6 and are not touched: `_scan` still ends a
  token at an en dash. Deferred to its own study (PREREGISTRATION §0).
* A period followed by a SPACE and then a percent sign (`5 wt. % Ni`) is not read as
  one unit by E5 or by the base: the period before a space still ends the token, and
  the `wt %` tail rule looks for the sign directly after the space. Under gold R4 the
  annotation `wt. %` would be `C`; the check blocks it. Pre-existing, unchanged here,
  and stated because a reviewer will try it.
* W = 0 on this gold is *no evidence against* for shapes the corpus lacks
  (`RESULTS-GOLD.md` Amendment 2): the folds' adversarial cases — a period before a
  space or the end, `s⁻²` against `s⁻¹`, `10⁵` staying unparsed notation, a
  superscript footnote staying prose — ship as tests, not as gold rows.

## 3. What changed, exactly

* `_scan`: a period continues the token before `%`/`‰` as well as before a letter or
  digit (`_PERIOD_CONTINUERS`).
* `_unit_key`: `normalise_unit` followed by the exponent fold (superscript digits and
  signs → ASCII, U+2212 → `-`), applied to both sides at the one comparison in
  `pair_occurrences`. `normalise_unit` itself, the fragment table, the boundary rule,
  the range split and `_UNPARSED` are unchanged.
* The contract string and the shipped skill each gain one sentence per fold; three
  `DISCLOSED_LIMITS` rows bind the sentences to behaviour.
* Tests: 17 rows for the two folds, three mutation tests (E5 off, E6 off, the fold
  reaching the notation rule or the scanner), the mirrors listed in the preregistration.
  `tests/test_number_source_check.py` 998 passed. Full suite on the host, runner line: "3785 passed, 4 skipped, 1 warning in 382.93s (0:06:22)".

### What the first review found, and what it changed

E5 lengthened `wt` to `wt.%`, and `_continues_unit` did not know the lengthened token,
so `5 kg wt.%` ended its join at `kg` and offered the prefix — base BLOCK, head PASS,
through both interfaces, on 180 of the reviewer's 224 fragment × suffix combinations;
and after a join, a word carrying `.%` (`approx.%`, `e.g.%`) newly blocked. Three
repairs: a fragment with `.%`/`.‰` attached is a unit atom (`_unit_atom`), so the join
continues and `kg` is the prefix it always was; at the boundary a word with `.%` is
read as the word (`approx.%` prose, `e.g.%` a named abbreviation); and `.%` at a token's
start is not a unit (`5.%` reads nothing, as before E5). A generated test sweeps every
alphabetic fragment in the table with `%` and `‰`. Two consequences of E5 are stated
rather than argued away: an element with `.%` (`K.%`, `Ni.%`) is refused as the bare
element is, so it ends the unit as before; and a fragment glued to `.%`-junk (`wt.%%`)
is not unit-shaped and ends the unit, where the base's scanner cut it to `wt` and
continued — that continuation was the period rule's artefact, not a reading. The gold table above is unchanged
by the repair (re-measured: base 0/0/0/0, E5 1/0/0/0, E6 2/0/0/0, shipped 3/0/0/0).
`tests/test_number_source_check.py` 1008 passed. Full suite on the host, runner line: "3801 passed, 4 skipped, 1 warning in 344.10s (0:05:44)" (an earlier run with a second suite executing concurrently on the same host failed one timing test in the streaming provider, unrelated to this slice; alone it passes 9 of 9).

## 4. Cost

$0. No generation, no model calls, no new corpus.
