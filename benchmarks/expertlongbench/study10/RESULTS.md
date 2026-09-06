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
  `tests/test_number_source_check.py` 998 passed. Full suite on the host: SUITE.

## 4. Cost

$0. No generation, no model calls, no new corpus.
