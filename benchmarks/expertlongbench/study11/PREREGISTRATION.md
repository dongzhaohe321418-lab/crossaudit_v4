# Study 11 — slice 5: E1, the endpoints of a range

Preregistered **before any line of `src/` was touched**, on `feat/provenance-slice-5`
(branched from `fusion/evidence-authority` at a4fdfa5, the merge of slice 4). Binding:
`docs/design/CONTAINMENT_RULE.md` §2 (E1) and §3, `RESULTS-GOLD.md` (E1 licensed,
R = 14, W = 0, with the §6 re-measurement required), `PROVENANCE_CHECKS.md` §6 (the
≤ 5% coincidental-containment line), D160 ruling 2, D161 ruling 2.

## 1. The rule, verbatim from the design

Where the text after a matched number is `<dash><number>` (`-`, `–`, `—`, optional
whitespace either side) and a unit token follows that second number, offer that unit
token as a further candidate for the first number. **Only the two literal endpoints;
never the interior.** The rule composes with the spaced-unit reading (D160 ruling 1):
the unit following the second number is read by `_unit_candidates`, so a spaced
expression or a `wt %` tail after the high endpoint is offered whole, never as a prefix.

Refused, and asserted: an interior value (`800` against `775–850 °C`); a unit borrowed
across a different quantity (`775` with `kPa` against `775–850 °C … 99 kPa`); a range
whose two ends carry different units (`5 g–10 mL` distributes nothing); a range whose
second number continues with notation the check refuses (`10⁵`); a range whose second
number is itself annotated — that one is adjacent and needs no rule.

### 1a. Where it lives

One branch in `_unit_candidates`, after the whole-token and range-split readings:
recognise `<dash><number>` at the head of `rest` (the whitespace-free `_RANGE` split
already covers a closed-up `20°C-25°C`; this covers `775–850 °C`, `775 – 850 °C`,
`99-102 kPa` and `1.5 – 6 sccm`), then take the candidates of the text after the second
number and offer each with an `end` that reaches to the end of that candidate — so the
quote-containment interval covers the whole range, as it covers a spaced unit.

## 2. The corpus and the baseline

The frozen gold (300 items); baseline `study11/base-verdicts.jsonl`, the merge base's
verdict after slice 4 on every item — 152 passes, 148 blocks; it differs from study 10's
base on exactly the three rows E5 and E6 moved — frozen before this file was committed.

## 3. The statistic, and the kills

R, W, R′, W′ as in studies 9 and 10; **W = 0 and W′ = 0**; the 10 gold-right blocks
still block. **The §6 re-measurement:** the panel's coincidental-containment count
(currently 2 of 97) must stay at or below 5% of 97 — that is, **≤ 4 of 97** — and no
panel draw that the gold labels N may be newly contained (that is a W).

## 4. What I expect, before running

* R = **14**: the fourteen M2 rows (G0004, G0007, G0032, G0041, G0062, G0100, G0114,
  G0140, G0176, G0205, G0215, G0216, G0217, G0257 — sccm ×2, °C ×7, rpm ×2, kPa ×2,
  μm ×2), all gold `C`, all the low endpoint annotated with the unit that follows the
  high one.
* W = **0**, R′ = **0**, W′ = **0**. The one range line the gold labels N and the
  base blocks stays blocked (it is either an interior value or a borrowed unit).
* Panel: the two panel draws whose line holds a range are not newly contained; the
  count stays 2 of 97. If E1 raises it, the figure is reported against the 5% line and
  a rise past 4 of 97 stops the slice.

## 5. Adversarial cases the gold cannot supply, each a committed test

Dashes: `-`, `–`, `—`, spaced and not; a dash followed by a space then a letter is not a
range (`5 g – heat`); a negative second number (`5 – −3 °C`) is a range of two signed
numbers; `775–850°C` closed up reads through both this rule and `_RANGE` with one
answer; `1.5 – 6 sccm`; a decimal second endpoint; a second endpoint with a thousands
group; `20–25 wt %` (the tail reading after the high endpoint); `20–25 °C min⁻¹` (a
spaced expression after it); the interior refusal at every position; `5–10` with no unit
after (the empty-unit row states (5, "") by R3 and nothing more).

## 6. The D64 mutations, each with its mirror

| mutation | what must redden |
|---|---|
| drop the range branch (E1 off) | the fourteen shapes above, as tests |
| offer the interior (accept any number between the endpoints) | the interior mirror |
| take the unit after the high endpoint for ANY earlier number on the line | the borrowed-unit mirror |
| read the range through `_RANGE` only (closed-up) | the spaced-dash cases |

## 7. What else must hold

`dcl/` only; kernel dirs untouched; `number_source` in no profile; the contract string
and the skill say in one sentence that a low endpoint carries the unit written after
the high one and that no interior value is stated, bound by disclosure rows; suite
green on the host; gold re-measured with `study11/measure.py` (the hook `_RANGE_ENDPOINTS`
or its function ablated by monkeypatch).

## Amendment 1 — 2026-09-06, after the run and the first review

Three things this document did not settle, decided afterwards and stated here rather
than in the results alone:

1. **A chain** (`1–2–3 °C`) was not in §5. The rule reads only one dash-number after
   the low endpoint and then the high endpoint's unit; where the high endpoint is itself
   followed by a dash and a number, the first number's reading finds no unit and offers
   nothing, while the middle number is the low endpoint of the last range and reads the
   unit. So `(1, °C)` blocks and `(2, °C)` passes. Decided after the run; asserted as
   rows; not a gold shape.
2. **The branch is taken first**, not "after the whole-token and range-split readings"
   as §1a said. Where the text after the number begins with a dash and a number, the
   whole-token reading is empty (a dash is a boundary) or a hyphen-led token that no
   unit equals, so the order changes nothing the gold measures; it is stated because
   §1a said otherwise.
3. **A spaced ASCII hyphen is refused** (round 2): `10 - 5 °C` read as a range and the
   base blocked it; a subtraction and a spaced-hyphen range have the same surface, and
   the gold holds neither. An en or em dash reads spaced or not; an ASCII hyphen reads
   only with no whitespace either side (`99-102 kPa`). The cost — `5 - 10 °C` blocks —
   is a false block on a shape absent from the gold, disclosed in the contract, the
   skill and a row. §1's "optional whitespace either side" is narrowed accordingly.
