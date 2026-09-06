# Study 14 — slice 8: M10, a negative exponent written with an en dash

Preregistered **before any line of `src/` was touched**, on `feat/provenance-slice-8`
(branched from `fusion/evidence-authority` at 7691827, after the merge of slice 7). Binding:
D161 ruling 2 ("The en-dash exponent is a **new class, M10**, not E6 … It gets its own
extension, its own gold rows (the frozen gold holds none) and its own W = 0 before it
ships"), `docs/design/CONTAINMENT_RULE.md` §3 (the label rule: a unit differing only in
Unicode form or exponent position is the same unit) and its "what must never ship" (a
reading shorter than the whole token), study 10's E6 (which folds `−`, U+2212, and does
not reach tokenisation). `number_source` stays out of every profile (D161).

## 0. What this study may conclude

Two outcomes are preregistered as legitimate: **ship**, or **measured and not shipped**.
M10's surface is small — the T03 corpus holds two tokens (`L·h–1`, `K·min–1`, one
instance) against fifteen en-dash ranges — and its rule has a danger the design named ("its
surface is the surface of a closed-up range"). If the rule below cannot hold W = 0 and
W′ = 0 with one guard, the extension stops and the class stays a disclosed limit.

## 1. The rule

An en dash (U+2013) **continues a unit token** when the character before it is a letter
(`str.isalpha`), an unsigned run of ASCII digits follows it, and that run ends the token
(whitespace, the end of the text, or a boundary character follows). The token is then
compared under `_unit_key`, whose fold maps the en dash to the ASCII hyphen beside the
U+2212 minus E6 already folds, so `L·h–1`, `L·h−1` and `L·h-1` are one unit. A signed or
decimal run (`min–−1`, `h–1.5`), a run followed by a letter (`h–1a`), or a dash after a
digit or a bracket (`10–5`, `)–1`) does not continue: those are a range, a subtraction or
prose, and the token ends at the dash exactly as it does today.

**The one guard — a range with a unit on both endpoints.** `5 min–10 min` and `800 °C–1050
°C` are ranges, and under the rule above `min–10` would be one token and `(5, min)` a wrong
block. The continuation is refused when the next whitespace-delimited token, stripped of
trailing punctuation, is the same string as the stem before the dash. `mol L–1 min–1`
continues (`min–1` is not `L`); `5 min–10 min` does not. Nothing else is guessed: `5 mL–10
g` reads `mL–10` and blocks `(5, mL)`, which is disclosed, not extended over.

### 1a. Where it lives

Two touch points, both named for the ablation: `_dash_exponent(text, i, start)` in `_scan`,
returning the offset after the digit run or `None`; and the en dash added to
`_EXPONENT_FOLD` (E6's table) and to `_EXPONENT_TAIL` (so `_unit_atom` accepts the token).
No other function changes. The E1 range branch (`_RANGE_TAIL`) is untouched: it reads the
rest after a *number*, where no letter precedes the dash.

## 2. The corpus and the baseline

The frozen gold; baseline `study14/base-verdicts.jsonl`, the merge base's verdict on every
item — **182 passes**; it differs from study 13's base on exactly the eleven rows E3 moved
— frozen before this file was committed. The gold holds **no** letter–dash–digit row, so
on the gold this study is a no-regression measurement: every count must be zero.

**M10's own gold rows** are Arm 4's two M10 rows (`study8/GOLD-arm4.csv`, both labellers
"wrong block", mechanism M10 in `emit_records_arm4.py`), whose located lines are in the
archive (`~/Documents/Crossaudit/study-data/wt-arm4-runs/sheet/sheet-arm4.jsonl`, not
committed). `study14/measure.py` re-measures those two rows from the archive and reports
counts only.

## 3. The statistic, and the kills

On the frozen gold: R = W = R′ = W′ = **0**, the 10 right blocks still block, panel 2 of 97.
On Arm 4's two M10 rows: both PASS under the shipped rule (R_arm4 = 2). On the committed
panel (§5): every row as labelled. **KILL if any gold or panel row moves the wrong way**,
or if the guard of §1 has to be widened to hold the panel — then the outcome is "measured
and not shipped" and the class stays disclosed.

## 4. What I expect, before running

Gold: all zeros, base reproduced 300 of 300. Arm 4: 2 of 2 pass. Panel: as labelled.

## 5. The panel, each row a committed test

Green: `10 mL min–1` with `(10, mL min-1)` and `(10, mL min⁻¹)`; `2 L·h–1` with `(2,
L·h-1)`; `5 K·min–1` with `(5, K·min-1)`; `0.5 mol L–1 min–1` with the whole expression;
`10 s–1` with `(10, s-1)`; `5 min–10 min` with `(5, min)` (the guard); `800 °C–1050 °C` with
`(800, °C)`; `5–10 °C` with `(5, °C)` (E1, unchanged); `(2 L·h–1)` in brackets; `2 L·h–1.`
sentence-final. Red: `5 min–10 min` with `(5, min-10)`; `10 s–1` with `(10, s)` (no
shorter reading); `5 mL–10 g` with `(5, mL)` (disclosed); `h–1.5`, `min–−1`, `h–1a` with
the exponent readings; `10–5 °C` with `(10, °C)` unchanged (a spaced-or-not en dash after a
number is E1's, and `10–5 °C` states 10 °C — green, in fact; listed to pin that E1 is
untouched); `5 g)–1` with `(5, g-1)`.

## 6. The D64 mutations, each with its mirror

| mutation | what must redden |
|---|---|
| `_dash_exponent` returns `None` (M10 off) | `10 mL min–1`, `2 L·h–1` with their units |
| drop the repeated-unit guard | `5 min–10 min` with `(5, min)` goes red (a wrong block appears) |
| accept a signed or decimal run | `h–1.5` with `(5, h-1.5)` goes green |
| accept a dash after a digit | `10–5 °C` with `(10, °C)` goes red — E1's range reading lost |
| drop the fold | `2 L·h–1` with `(2, L·h-1)` goes red |

## 7. What else must hold

`dcl/` only; kernel dirs untouched; `number_source` in no profile; the contract and the
skill say in one sentence what an en-dash exponent states and what the guard refuses, bound
by disclosure rows; suite green; gold re-measured with `study14/measure.py` (hook
`_dash_exponent` ablated by monkeypatch); Arm 4's two rows re-measured from the archive;
no corpus prose committed (unit tokens are facts).
