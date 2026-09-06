# Study 13 — slice 7: E3, a decimal stoichiometric subscript

Preregistered **before any line of `src/` was touched**, on `feat/provenance-slice-7`
(branched from `fusion/evidence-authority` at 7a26ac1, after the merge of slice 6).
Binding: `docs/design/CONTAINMENT_RULE.md` §2 (E3, "and why it is last"), §3 (the label
rule: "a subscript counts"), §4 item 5 ("last, and with its own probe, because it is the
only extension that adds unit-free matches"); D160 ruling 2; D161 ruling 4 (E3 last, own
probe). `number_source` stays out of every profile (D161).

## 1. The rule, verbatim from the design

*A value containing a `.`, glued directly to a letter, inside a whitespace-delimited
token of letters, digits, brackets and `·`, is a number with the empty unit.* Integer
subscripts stay unreadable — `O2`, `H2O`, `Cr2O3`, `Co(NO3)2·6H2O` must not make `2` and
`3` citable from every formula on the page; they are **(c)**, `uncited`.

### 1a. One stated deviation, decided here and not after the run

Two of the gold's eleven M1a rows (G0110, G0120) are `SrCo0.6Fe0.4O3−δ`: the token carries
U+2212 MINUS before `δ`, which the design's enumerated charset does not admit, although
the same design counts all eleven M1a rows as E3's. The resolution: the token charset
admits `−` (U+2212) and `±` (U+00B1) **only when a letter follows** — the
non-stoichiometry marker `O3−δ` / `O2±δ` — never before a digit. If a reviewer holds the
enumerated charset to be binding, the two rows stay (c) and the expectation below drops
to R = 9; the rule is otherwise unchanged.

### 1b. Where it lives

`pair_occurrences`, in the **empty-unit branch only**. After the ordinary `_NUMBER`
scan, a second scan by one named hook, `_SUBSCRIPT`: an unsigned `[0-9]+\.[0-9]+`
immediately preceded by a letter and not followed by a digit or a period; the
whitespace-delimited token holding it, with trailing sentence punctuation (`.,;:!?`)
removed, must consist entirely of letters, digits, brackets, `·`, the marker of §1a, and
periods that sit between two digits. `_UNPARSED` on the value's continuation refuses the
occurrence as it does everywhere else. E3 yields nothing when a unit was transcribed:
`(0.8, M)` against `LiNi0.8Co0.2O2` stays blocked.

## 2. The corpus and the baseline

The frozen gold; baseline `study13/base-verdicts.jsonl`, the merge base's verdict on
every item — **171 passes**; it differs from study 12's base on exactly the five rows E2
moved — frozen before this file was committed.

## 3. The statistic, and the kills

R, W, R′, W′ as before; **W = 0 and W′ = 0**; the 10 gold-right blocks still block; the
panel's coincidental-containment count stays ≤ 4 of 97 and no gold-N panel draw is newly
contained.

### 3a. E3's own probe, `study13/probe.py`

E3 is the only extension that adds matches no unit constrains, so the gold's panel is
not enough: the probe reads the whole T03 corpus (gitignored; `CROSSAUDIT_T03_CORPUS`)
and both archived run sets (`armT-scoped`, 16 instances; `wt-arm4-runs`, 26 instances).

* **P1 — every token E3 reads.** Enumerate every whitespace-delimited token in every
  source procedure that `_SUBSCRIPT` reads, with the value it yields. Each token is
  classified by hand as *formula* (a chemical formula whose decimal is a stoichiometric
  coefficient) or *other* (a version string, an identifier, a figure label, a pH
  glued to its value, anything else). The list of token shapes and the two counts are
  committed (formula tokens are facts, not corpus prose). **KILL if any *other* token's
  decimal is not a value the text states** — the design's danger is exactly a number
  that is citable without being stated.
* **P2 — the line-scoped coincidental rate, empty-unit pairs.** `provenance_probe.py`'s
  instrument (seed 20261104, five wrong-location draws per pair) over the drafts' pairs,
  under base and under E3, reported for all pairs and for empty-unit pairs alone.
  **KILL if E3 raises the line-scoped rate above §6's 5%** (`PROVENANCE_CHECKS.md`, shipped
  rule 0/1825); the empty-unit-only rate is reported beside it and any rise is disclosed.
* **P3 — subscript decoys.** For every formula token P1 finds, every *other* formula
  token in the corpus that E3 reads the same value from is a decoy; the count of
  (value, distinct-formula) collisions is reported. A collision is not a kill — the
  empty-unit annotation already "can never establish that a number is unitless" — but
  it is the number the skill's warning has to carry.

## 4. What I expect, before running

* R = **11**: G0001, G0082, G0196, G0203 (`LiNi0.8Co0.2O2`: 0.2 / 0.8), G0063, G0113,
  G0267 (`Ni0.95Co0.04Mn0.01(OH)2`), G0159, G0213 (`Li0.75H1.25RuO3`), G0110, G0120
  (`SrCo0.6Fe0.4O3−δ`, §1a). All gold C. (R = 9 without §1a.)
* W = **0**, R′ = **0**, W′ = **0**. The panel's gold-N empty-unit draws (G0099, G0158,
  G0186, G0201, G0227, G0231, G0233, G0236, G0254, G0255, G0260, G0297) do not contain
  their value string at all, or only as an integer, so E3 cannot newly contain them;
  panel stays 2 of 97. G0192 (`(ZrOCl2·8H2O)`, 2) and G0206 (`(AgNO3`, 3) are integer
  subscripts, gold C, and stay blocked by design — two wrong blocks E3 leaves, disclosed.
* P1: only formula tokens in T03 (a materials-synthesis corpus); P2: line-scoped rate
  unchanged at 0; P3: some collisions, because the corpus repeats its target materials.

## 5. Adversarial cases the gold cannot supply, each a committed test

`LiNi0.8Co0.2O2` with `(0.8, "")` and `(0.2, "")` green, `(8, "")`, `(2, "")` and `(0.8,
M)` red; `H2O`, `Cr2O3`, `Co(NO3)2·6H2O` with the integer red; `Fig.3.2` and `v1.2.3`
with `(3.2, "")`/`(1.2, "")` red (a period follows, or precedes); `run_v1.5`,
`x=Ni0.5`, `"Ni0.5"` red (a character outside the charset); `Ni0.5×10³` red
(`_UNPARSED`); `pH7.4` with `(7.4, "")` green (a stated value glued to letters — E3
reads it and the skill says so); `SrCo0.6Fe0.4O3−δ` green for 0.6 and 0.4, `O3−0.5`
red (the marker before a digit); a sentence-final `LiNi0.8Co0.2O2.` green; `0.8` alone,
unglued, unchanged (the ordinary scan).

## 6. The D64 mutations, each with its mirror

| mutation | what must redden |
|---|---|
| drop `_SUBSCRIPT` (E3 off) | the eleven gold shapes, as tests |
| read integer subscripts | `H2O` with `(2, "")` goes green — its row |
| drop the letter-before requirement | `Fig.3.2` with `(3.2, "")` goes green |
| drop the charset requirement | `run_v1.5` with `(1.5, "")` goes green |
| yield for a transcribed unit | `(0.8, M)` against `LiNi0.8Co0.2O2` goes green |

## 7. What else must hold

`dcl/` only; kernel dirs untouched; `number_source` in no profile; the contract string
and the skill say in one sentence what a decimal subscript states, that an integer
subscript states nothing this check reads, and that a unit-free match is the weakest
match the check makes — bound by disclosure rows; suite green; gold re-measured with
`study13/measure.py` (hook `_SUBSCRIPT` ablated by monkeypatch); the probe's three
outputs committed as counts and token shapes, never corpus prose.
