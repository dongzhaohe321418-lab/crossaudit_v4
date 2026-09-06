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

## Amendment 1 — 2026-09-06, after the first review (fe42d31 → round 2)

The first review (`benchmarks/reviews/2026-09-06-provenance-slice-7-astra-round1.md`) said
do not merge on four findings; each changes something this file stated, so each is
recorded here and not edited above.

1. **"Not followed by a digit" was ASCII.** `_SUBSCRIPT`'s lookahead refused `[0-9]`; a
   full-width, Arabic-Indic or subscript digit after the decimal (`Ni0.5２O`, `Ni0.5٢O`,
   `Ni0.5₂O`) let `0.5` — a strict prefix of the digits the source wrote — satisfy the
   pair, through the real fenced interface. §1b's rule now reads *not followed by a digit of
   any script* (`str.isnumeric`), by a named guard `_continued_by_digit` with its own
   mutation row (`Ni0.5２O`; the subscript-digit shape is also held by item 2).
2. **The charset was not a formula test.** `Figure3.2`, `Table1.2`, `SampleA0.8`,
   `DOI10.1234`, `version1.2` passed the charset and became empty-unit passes. The rule
   now requires, in addition, that every run of letters in the token parse as a sequence
   of element symbols (118, with `x`, `y`, `z`, `δ` admitted as variables); named
   `_element_symbols`, mutation row `Figure3.2`. Two consequences the run measured:
   `pH7.4` — §5 said green — is now red (`p` is no symbol), a disclosed limit; and the
   design's "glued to a letter" is carried by this parse, so the separate letter guard
   of the first build, which had no row of its own to redden, is gone (§6's third row is
   now the element parse; `x²0.5` stays red because `x²` is no element run). P1 on the
   corpus is unchanged: 17 tokens, all formulae.
3. **"An integer subscript is never read" overclaimed.** `(OH)2` and `[Fe(CN)6]3−` make
   `2` and `6` citable through the ordinary scan, which reads any number a non-word
   character precedes and always did. The contract and the skill now say exactly that
   ("glued to a letter" is what this rule does not read; after a bracket or a middle dot
   the ordinary scan reads it), with rows for `(OH)2` and `Co(NO3)2·6H2O`.
4. **The interval was the digits, so "quote the formula" was advice.** `pair_occurrences`
   now yields the whole formula token as the interval, so under content addressing a
   quotation of `0.8` alone is a wrong span (CA-NUM-002) and the formula must be quoted —
   the one deterministic tie between a unit-free match and the material it belongs to.
   A fenced-interface test binds it. Gold, probe and panel are unaffected (they use
   `contains_pair`).

The gold and the probe were re-run after these changes: R = 11, W = R′ = W′ = 0, right
blocks 10/10, panel 2/97; P1 17/0, P2 0/3910 and 0/2205, P3 12 of 23 — identical to the
first run.

## Amendment 2 — 2026-09-06, after the second review (1141248 → round 3)

The second review (`…-slice-7-astra-round2.md`) said do not merge on four findings.

1. **The left side of the decimal.** With the letter guard removed in Amendment 1, the
   ASCII lookbehind let `Ni２0.5O`, `Ni٢0.5O`, `Ni२0.5O` read `0.5` as a suffix of a
   mixed-script numeric run. Amendment 1 item 2's claim that the element parse carries
   "glued to a letter" was **false**: the parse never looked at the character before the
   digits. `_glued_to_letter` (`str.isalpha`) is back, now with the row that Amendment 1
   said it lacked — `Ni２0.5O` — and `x²0.5` beside it.
2. **Letter runs were `[^\W\d_]+`**, which takes `₂` and `²` for letters, so `LiNi0.5O₂`
   was refused while `LiNi0.5O2` read. Runs are now maximal `str.isalpha` runs
   (`_letter_runs`); a subscript or superscript digit elsewhere in the token is a digit of
   the charset. Consequence: after the decimal, `Ni0.5₂O` is now held by the digit guard
   alone (it was also held by the parse), which the mutation test states.
3. **What the element parse does and does not carry**, stated exactly: it decides whether
   the token is formula-shaped; it is syntactic (`BaNaNa1.2` reads, `Nice1.2` does not,
   `ce` being no symbol), and the contract and skill now say so with a row. Whether the
   digits are glued to a letter is the letter guard's, and only its. A decimal after a
   middle dot or a bracket (`CuSO4·0.5H2O`, `Zr(HPO4)0.5·H2O`) is the ordinary scan's, read
   as a bare number with the digits as the interval — E3 yields nothing there, which the
   interval test now asserts (the first build yielded the whole token for `·0.5`).
4. **Stale text.** The E3 comment said an integer subscript "is never read" and described
   a letter guard that had been removed; and `_ELEMENTS` had been defined twice, because
   the module already held the 118 symbols for the fragment table and Amendment 1's build
   added a copy. The region is rewritten once; the module's own set is used.

Gold and probe re-run: identical to the first run (R = 11, W = R′ = W′ = 0, 10/10, panel
2/97; P1 17/0, P2 0/3910 and 0/2205, P3 12 of 23).

## Amendment 3 — 2026-09-06, after the third review (efd38ff → round 4)

The third review (`…-slice-7-astra-round3.md`) said do not merge on four findings.

1. **The marker guard used `[^\W\d_]`** for "a letter follows", which admits every
   numeric character that is not `\d` — `Ni0.5O−₂`, `Ni0.5O−²`, `Ni0.5O−Ⅷ`, `Ni0.5±₂`
   read `0.5` (1,151 such characters in the review's sweep). The charset is now a
   function, `_formula_charset`, in which the marker must be followed by `str.isalpha`,
   a period must sit between two ASCII digits, and everything else is `isalpha`,
   `isnumeric`, a bracket or the middle dot. Rows for the four shapes; the charset
   mutation now also turns `Ni0.5O−₂` green.
2. **P2 was zero by construction.** The probe named the owner lines of a pair as every
   line `contains_pair` accepted, excluded them, and tested the rest with `contains_pair`.
   §3a's "P2 — the line-scoped coincidental rate" and its kill condition were therefore
   not measurements. The design's own §6 figure (0/1825) has the same shape, and is
   withdrawn in CORRECTIONS #32 with a dated note in both design files. P2 is rebuilt:
   the owner line is the one the generator's own quotation names (Arm 4's 26 annotated
   drafts, 190 rows, 186 traced by their quote), the wrong lines are the other lines of
   that source (five draws) and lines of other sources (five draws), the containment test
   is the shipped matcher. Arm T's 16 drafts carry no annotations and drop out of P2. The
   kill stays as preregistered (> 5%) and is now decided by a real number.
3. **A decimal ending the token before sentence punctuation** (`Ni0.5.`) was refused by the
   regex's `(?![0-9.])` before punctuation stripping ran; `Ni0.5` and `Ni0.5,` read. The
   lookahead is `(?![0-9])` and the period rule is a named guard, `_continued_by_version`
   (a period AND a digit: `v1.2.3`), with its mutation row `Fe1.2.3`.
4. **RESULTS §4 said the ordinary scan reads a number after "any character that is not a
   word character"**; a period is the exception (`Ni.0.5O` blocks). Corrected, with a row.

Gold re-run: unchanged (R = 11, W = R′ = W′ = 0, 10/10, panel 2/97). Probe: P1 and P3
unchanged; P2 under the rebuilt instrument, base and E3 alike: **5/930 = 0.54%** on a
wrong line of the right source (empty-unit pairs 0/20), 3/930 on a line of a wrong source.

## Amendment 4 — 2026-09-06, after the fourth review (8faa0ce → round 5)

The fourth review (`…-slice-7-astra-round4.md`) said do not merge on one finding and noted
one inexact sentence.

1. **The charset admitted every `str.isnumeric` character** — 1,114 that are no digit
   (Roman numerals, circled and parenthesised numbers, vulgar fractions, ancient counting
   marks), 1,023 of which made `0.5` citable after `Ni0.5O`; and the words said "digits".
   A formula's digits are now the decimal digits of any script (`str.isdecimal`, category
   Nd) and the twenty sub- and superscript digits (`_SCRIPT_DIGITS`); `str.isdigit` was
   not used because it admits the circled numbers too. `Ni0.5O½`, which §5's first build
   had green, is red with `Ni0.5OⅧ`, `Ni0.5O⑧`, `Ni0.5O⑴`; `Ni0.5O２`, `LiNi0.5O₂` and
   `Fe³Ni0.5O` stay green. The contract and skill name the exclusion, with a row. The guard
   after the decimal keeps `str.isnumeric`: a numeric symbol continuing the digits refuses
   the match, which is the safe direction.
2. **CORRECTIONS #32 said "the three design passages carry a dated note."** One dated
   note exists (PROVENANCE_CHECKS §6); the figure's other four appearances now carry an
   inline pointer to the item, and the sentence says exactly that.

Gold and probe re-run: unchanged (R = 11, W = R′ = W′ = 0, 10/10, panel 2/97; P1 17/0,
P2 5/930 and 3/930, P3 12 of 23).
