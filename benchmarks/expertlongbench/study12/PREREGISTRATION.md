# Study 12 — slice 6: E2, a list with one trailing unit

Preregistered **before any line of `src/` was touched**, on `feat/provenance-slice-6`
(branched from `fusion/evidence-authority` at e890dfe, the merge of slice 5). Binding:
`docs/design/CONTAINMENT_RULE.md` §2 (E2) and §3, `RESULTS-GOLD.md` (E2 licensed: R = 2
alone, R = 6 composed with E5; W = 0), `PROVENANCE_CHECKS.md` §6, D160 ruling 2 (E2
after E1 and E5, never bundled), D161 ruling 2.

## 1. The rule, verbatim from the design

E1 with `,`, `and`, `or` as separators, **and one guard**: every member between the
annotated number and the unit-bearing member must be a bare number carrying no unit
token of its own, so `0, 20, 40, 80 wt.%` distributes and `0.2 kg, 0.5 kg, or 1 kg` does
not. It composes with E5 (`wt.%` is one token) and with the spaced-unit reading (the
unit after the last member is read whole). An intervening bare number is skipped, never
taken for a unit. The trailing unit belongs to every member the guard admits; nothing
between members is stated (R8).

### 1a. Where it lives

One branch in `_unit_candidates` beside E1's: where the text after the number begins
with a separator (`,` or the word `and`/`or`, whitespace either side) and a number, walk
members while each is a bare number followed by a separator, and when a member is
followed by a unit expression instead, offer that expression's candidates for the
annotated number with the end offset through the unit. Any member that carries its
own unit token, any separator that is not `,`/`and`/`or`, or a member continued by
refused notation stops the walk and offers nothing. Chains stop at the first
unit-bearing member.

## 2. The corpus and the baseline

The frozen gold; baseline `study12/base-verdicts.jsonl`, the merge base's verdict after
slice 5 on every item, — 166 passes; it differs from study 11's base on exactly the fourteen rows E1 moved — frozen before this file was committed.

## 3. The statistic, and the kills

R, W, R′, W′ as before; **W = 0 and W′ = 0**; the 10 gold-right blocks still block; the
panel's coincidental-containment count stays ≤ 4 of 97 and no gold-N panel draw is
newly contained. The design calls E2's false-pass surface larger than E1's, because
prose separates unrelated quantities with commas far more often than it writes ranges;
the panel and the adversarial cases are where that is measured.

## 4. What I expect, before running

* R = **5**: G0124, G0244, G0248 (`wt.%` list members, gold C, blocked until E2 could
  reach the trailing `wt.%` that E5 made one token) and G0134, G0204 (`106 and 25 μm`),
  all gold C. (RESULTS-GOLD's R = 6 for "E2 + E5" counts G0098 too, which E5 alone
  moved in study 10.)
* W = **0**, R′ = **0**, W′ = **0**; the one panel line holding a list is not newly
  contained; panel stays 2 of 97.

## 5. Adversarial cases the gold cannot supply, each a committed test

`0.2 kg, 0.5 kg, or 1 kg` (each member keeps its own; `(0.2, μm)` against it red);
`1 : 1 : 0.125–0.5 mass ratio` (a colon is not a separator; nothing distributes); `5, 10
and 20 °C` (three members, two separator words); `5 and 10` with no unit; `5, 10 × 10⁵
Pa` (refused notation stops it); a comma between unrelated quantities (`5 g, 10 mL`:
the first carries its own unit, nothing distributes); `5, 10 °C min⁻¹` (a spaced
expression after the last member); `5,000 and 10,000 rpm` (a thousands comma is not a
separator); `5, 10–20 °C` (a range as the last member: E1 inside E2); an Oxford-comma
list; `and/or`.

## 6. The D64 mutations, each with its mirror

| mutation | what must redden |
|---|---|
| drop the list branch (E2 off) | the five gold shapes, as tests |
| drop the bare-member guard | `0.2 kg, 0.5 kg, or 1 kg` with `(0.2, kg)` must stay green and `(0.2, μm)` red — the guard's own row goes green |
| accept `:` or `;` as a separator | the ratio mirror |
| distribute past a member with refused notation | the `× 10⁵` mirror |

## 7. What else must hold

`dcl/` only; kernel dirs untouched; `number_source` in no profile; the contract string
and the skill say in one sentence what a list with one trailing unit states and what it
does not, bound by disclosure rows; suite green; gold re-measured with
`study12/measure.py` (hook `_LIST_TAIL` ablated by monkeypatch).

## Amendment 1 — 2026-09-06, after the gold run, before the first review

One narrowing this document did not specify: a number that a LABEL word precedes
(`Step 5, 10 mL`, `Fig. 5, 10 °C`, `Sample 5`) is not a list member, so E2 offers it
nothing. Under gold R8 read literally those rows would be `C`; the guard blocks them,
which is the safe direction, and the word list is small, capitalised-or-not, and named
(`_LABEL_WORDS`). Added after probing E2's false-pass surface with the labelled forms
this corpus writes constantly and the gold happens not to hold on a list line; the gold
was re-measured after adding it and is reported in RESULTS §1 as measured.
