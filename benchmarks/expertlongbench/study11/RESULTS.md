# Study 11 — slice 5: E1, the endpoints of a range, measured on the frozen gold

Preregistered at `study11/PREREGISTRATION.md` (fcf2c20) before `src/` was touched;
baseline `study11/base-verdicts.jsonl` (the merge base a4fdfa5's verdict on all 300
items — 152 passes, 148 blocks; three rows moved from study 10's base, the three E5 and
E6 read). Measured with `study11/measure.py`, which imports the shipped `contains_pair`
and switches E1 off by monkeypatching `_RANGE_TAIL`.

## 1. The table, with the kills applied

| configuration | R (wrong blocks removed) | W (wrong passes added, kill) | R′ | W′ (wrong blocks added, kill) | right blocks | panel (≤ 4 of 97 preregistered) |
|---|---:|---:|---:|---:|---:|---:|
| **base** (E1 off) | 0 | 0 | 0 | 0 | 10/10 | 2/97 — equals the frozen base on 300 of 300 |
| **shipped** (E1) | **14** | **0** | 0 | **0** | 10/10 | **2/97** |

Every preregistered expectation is met to the row: R = 14 — G0004, G0007, G0032,
G0041, G0062, G0100, G0114, G0140, G0176, G0205, G0215, G0216, G0217, G0257, the
fourteen M2 rows, all gold `C` — W = 0, R′ = 0, W′ = 0, the ten gold-right blocks still
block, and the §6 re-measurement holds: the panel's coincidental-containment count is
unchanged at 2 of 97, neither panel draw whose line holds a range is newly contained,
and the one range line the gold labels `N` stays blocked.

## 2. What the gold could not decide

* A range whose low endpoint carries its own unit (`5 g–10 mL`), a signed high
  endpoint, an em dash, spaced dashes, a thousands group, a spaced or `wt %` tail after
  the high endpoint, a high endpoint continued by refused notation, and a dash followed
  by a word — none is in the gold; each ships as a test (§5 of the preregistration). A
  chain of three numbers was NOT in §5: its semantics were decided after the run and are
  stated in Amendment 1, with rows.
* **A spaced ASCII hyphen is refused** (round 2, Amendment 1 item 3): the first review
  showed `10 - 5 °C` accepted as a range where the base blocked it, and a subtraction
  has that surface. An en or em dash reads spaced or not; an ASCII hyphen only glued.
  `5 - 10 °C` therefore blocks — a false block on a shape absent from the gold,
  disclosed in the contract, the skill and a row. The gold table is unchanged by the
  narrowing (re-measured: R = 14, W = 0, R′ = 0, W′ = 0).
* The interior refusal is by construction: a value between the endpoints is not in the
  text and matches nothing; it is asserted at three interior values and as a mutation
  target.
* W = 0 on this gold is *no evidence against* for shapes the corpus lacks
  (`RESULTS-GOLD.md` Amendment 2).

## 3. What changed, exactly

* `_unit_candidates` gained one branch, taken first — the preregistration's §1a said
  "after the whole-token and range-split readings"; Amendment 1 item 2 records the
  difference and why it changes nothing measured: where the text after the number
  begins with a dash and a second number (`_RANGE_TAIL`), the candidates are those of
  the text after the second number, read by the same function with the range branch
  off, with each end offset so the quotation interval reaches through the high
  endpoint's unit. A high endpoint continued by `_UNPARSED` notation offers nothing.
* Three earlier test rows that asserted the low endpoint of `99-102 kPa` / `20-25 °C`
  does NOT carry the unit are superseded, with the reason on the row.
* The contract string and the shipped skill each gain one sentence; three
  `DISCLOSED_LIMITS` rows bind them.
* Tests: 24 rows, two mutation tests (E1 off; the interior and the borrowed unit), the
  quotation-interval test; round 2 adds the spaced-hyphen rows.
  `tests/test_number_source_check.py` 1050 passed. Full suite
  on the host, runner line (round 2): "3837 passed, 4 skipped, 1 warning in 350.25s (0:05:50)".

## 4. Cost

$0.
