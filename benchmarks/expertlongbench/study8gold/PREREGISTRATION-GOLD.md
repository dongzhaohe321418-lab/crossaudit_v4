# The containment gold — preregistration

`docs/design/CONTAINMENT_RULE.md` §3, under D159 ruling 3. This file is committed
**before any labeller sees an item**. It fixes the question, the corpus, the rule,
the labellers, the statistic and the kill condition. Nothing below may be changed
after labelling begins; every departure is numbered in `RESULTS-GOLD.md` §D.

No model call is made by the study except the second labeller's. Nothing under
`src/` is modified. `$0` of generation: the corpus is Arm 3's frozen archive.

## 0. The question

For a frozen triple **(located text, transcribed value `v`, transcribed unit `u`)**:

> **Does the located text state that value with that unit, as written?**

Not "is the number right". Not "is the claim true". Not "is the citation the
right place to cite". Only whether those bytes state that pair. This is the
question `contains_pair` (`src/crossaudit/dcl/numbers.py:296`) is supposed to
answer, and the gold is built so that a change to `contains_pair` can be scored
against a ruler that is not `contains_pair`.

## 1. The corpus

Reconstructed from the read-only archive
`~/Documents/Crossaudit/study-data/wt-arm3-runs/arm3` (directory digest
`6cfe11f0ab4bc78185e227e8624b19cc70e582f0d61cc00e0cf692734b9ea8f9`) by
`build_sheet.py`, committed beside this file. **Seed `20260906`**, used for the
pass sample and for every panel draw, in that order.

| stratum | n | what it is |
|---|---|---|
| `block` | **53** | every Arm 3 BLOCKER — the 51 containment blocks plus the 2 the 80-character cap raised (D159 ruling 1 removes the cap; they are kept because the task freezes all 53) |
| `pass` | **150** | a seeded random sample without replacement of the 348 Arm 3 passes |
| `panel` | **97** | the wrong-location negative panel: 5 drafts drawn at the seed, every resolvable annotation row of those drafts, each re-pointed at **5 distinct other lines of the same file** that contain at least one digit |
| **total** | **300** | |

**The located text is what the Arm 3 verifier read**, not a re-derivation:
`provenance_arm3.located_text`'s rule — for arm A the named line, for arm B the
whitespace-folded quote (unique in its file). For a `panel` item it is the whole
re-pointed line. Judging the same bytes the matcher judged is what makes the
extension simulation in §5 meaningful.

**The sheet a labeller sees contains only `id`, `line`, `v`, `u`.** No matcher
verdict, no arm, no instance, no mechanism label, no stratum, no disposition.
Items are shuffled at the seed across all three strata, so stratum is not
recoverable from position. The sheet carries corpus text and therefore lives in
the archive (`~/Documents/Crossaudit/study-data/gold-containment/sheet.jsonl`),
never in this repository (EXPERIMENT_RECORD §3). The **key** — id, stratum,
instance, arm, row, file, line, shipped-matcher verdict, and sha256 of the text,
value and unit — carries no corpus text and is committed as `key.jsonl`.

## 2. The rule

Written before any item was looked at. A labeller cites exactly one rule number
per item; where several apply, the **lowest-numbered rule that decides the item**
is cited. Labels are `C` (the text states the pair), `N` (it does not), `?`
(the rule does not decide it).

**R1 — the value, as a numeral.** `v` is stated only where the text writes a
numeral denoting the same number. Leading and trailing zeros are not significant
(`0.80` = `.8` = `0.8`); a thousands comma is not significant (`1,000` = `1000`);
`e`/`E` are the same; a sign character (`-`, `−`, `+`) is significant. A value
written in words (`ten`, `one hundred`) is **not** stated. A value reached by
conversion, arithmetic, rounding or reading a plot is **not** stated.

**R2 — the unit belongs to that occurrence.** The unit must be the one the text
writes for *that* occurrence of the numeral, under R4–R9. Any occurrence in the
located text may satisfy (R13).

**R3 — an empty unit is a claim about the value only.** Where `u` is empty, the
pair is stated iff the value is stated under R1/R10/R11, whatever unit the text
attaches to it. `5 °C` states `(5, "")`.

**R4 — unit identity is by characters, after three folds and nothing else.**
Two unit expressions are the same unit iff they are the same string after:
(a) deleting **all** whitespace, so `wt %` = `wt%` and `°C min⁻¹` = `°Cmin⁻¹`;
(b) folding superscript and subscript digits and signs (`⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻₀₁₂₃₄₅₆₇₈₉`)
to their ASCII forms and U+2212 to `-`, so `dm3/s` = `dm³/s` and `s−1` = `s⁻¹`;
(c) folding U+00B5 `µ` to U+03BC `μ`.
**Nothing else is folded.** No conversion and no algebra: `°C/min` is **not**
`°C min⁻¹`, because a solidus and a negative exponent are one operator only under
an algebra this rule does not have.

**R5 — a unit spelled out.** A unit written as its English name is the same unit
as its symbol iff the name is the standard full name of exactly that unit and of
no other: `hour`/`hours` = `h`, `minute`/`minutes` = `min`, `second`/`seconds` =
`s`, `percent` = `%`. A word naming a quantity family or a dimension rather than a
specific unit — `degrees`, `times`, `mesh`, `fold` — is **not** any unit symbol.

**R6 — the whole unit, never a part of it.** The unit the text writes at an
occurrence is the whole unit expression there. A strict prefix of it is not it
(`%` is not `wt %`), and neither is a strict extension (`°C` is not `°C min⁻¹`).
A unit expression ends where ordinary prose resumes: in `80 wt.% sub-micron` the
unit expression is `wt.%`. Enclosing brackets are not part of it.

**R7 — a range states its endpoints and not its interior.** A range written
`a<dash>b U`, or `a U<dash>b U` (dash: `-`, `–`, `—`, spaced or not), states
`(a, U)` and `(b, U)`. It states no interior value with `U`: `775–850 °C` does
**not** state `(800, °C)`.

**R8 — a list with one trailing unit distributes it.** Where numerals are
separated by `,`, `and`, or `or` and only the last member carries a unit
expression, each earlier member states that unit — **provided** every member
between it and the unit-bearing member is a bare numeral with no unit expression
of its own. `0, 20, 40, 80 wt.%` states `(0, wt.%)`; `0.2 kg, 0.5 kg, or 1 kg`
does not state `(0.2, μm)` and does state `(0.2, kg)` by adjacency.

**R9 — a hyphenated compound adjective states its unit.** A hyphen between a
numeral and a unit expression is a compound-adjective hyphen, and the value is
stated with that unit: `2.54-cm diameter` states `(2.54, cm)`; `2 h-long` states
`(2, h)`. A hyphen **between two unit expressions** is part of the unit: `10 kg-m`
states `(10, kg-m)` and does not state `(10, kg)` (R6).

**R10 — a mantissa is not the number.** A numeral the text continues with a
power-of-ten factor or an exponent (`3 × 10⁻² mbar`, `3×10⁻²`, `10⁵`, `5^3`)
states the product, not the mantissa. `3 × 10⁻² mbar` states neither `(3, mbar)`
nor `(3, "")`.

**R11 — a subscript counts.** A numeral written as a stoichiometric subscript or
as a glued digit inside a chemical-formula token (`LiNi0.8Co0.2O2`, `Li₂O`,
`Ni0.95Co0.04Mn0.01(OH)2`) states that value with the empty unit. It states no
value with a non-empty unit.

**R12 — mesh, ratios and counts.** A bare numeral that the text gives no unit
(`a 1:1 mass ratio`, `Step 2`) states that value with the empty unit and with no
other. A `n:m` ratio states `n` and `m` separately under R12, not the quotient.

**R13 — any occurrence.** The text states the pair if at least one occurrence of
the value satisfies the unit rule.

**R14 — case is significant in a unit** (`mM` ≠ `mm`) and not in an exponent
marker (`1E3` = `1e3`).

**R15 — undecided.** An item the rules above do not decide is labelled `?` with
the number of the rule that came closest. A `?` is never resolved by guessing.

## 3. The labellers

Two, independent, blinded to each other and to the matcher.

* **L1 — this session**, applying §2 by hand to the sheet, in id order, in
  batches, writing `id,label,rule_number` and nothing else.
* **L2 — `gpt-6-astra` through the Codex CLI**, a different vendor and a
  different session, invoked from a scratch directory outside any repository as
  `codex exec -m gpt-6-astra -c 'model_reasoning_effort="high"' --sandbox
  read-only --skip-git-repo-check -`, its only input being §2 verbatim and a
  batch of sheet items, its only output `id,label,rule_number` lines. It is told
  nothing about arms, strata, the matcher, or the study.

Neither label set is read against the other until **both are complete and
committed**. L1 is committed first; L2's prompt contains no L1 label.

## 4. Agreement and adjudication

* **Raw agreement** and **Cohen's κ** (three categories `C`/`N`/`?`), overall and
  per stratum, with κ's standard error.
* **Every disagreement listed by id**, with both labels and both cited rules.
* **A third pass**: L1 re-reads *only the disagreeing items*, with §2 and no other
  input, and records the adjudicated gold label and a one-line reason. **Neither
  original label is changed.** The adjudicated label is the gold.
* Items gold-labelled `?` are excluded from §5's denominators and reported as a
  count. An extension is **undecidable** on a stratum whose `?` count could
  change its verdict.

## 5. What the gold licenses

For each extension **E1–E6** of `CONTAINMENT_RULE.md` §2, simulated over the
frozen items by `simulate.py` — a deterministic re-implementation of each
extension's stated rule on top of the shipped `numbers.py`, with **no change to
`src/`** and no model call:

* **R** — items in the `block` stratum that the extension turns into passes and
  the gold labels **C** (a wrong block, correctly removed).
* **W** — items **anywhere in the corpus, `panel` included** that the extension
  turns into passes and the gold labels **N** (a wrong pass, newly admitted).

Reported as `R`, `W` and `R − W`. **The kill condition, fixed in advance by the
note: `W` must be 0.** An extension with `W ≥ 1` does not ship. An extension whose
`W` is 0 but whose decision would flip under the corpus's `?` items is reported as
**undecided**, not licensed.

The simulation is written and committed before the labels are read.

## 6. Threats to this gold, stated in advance

1. **L1 is not independent of the design note.** L1 wrote §2 from the note's §3.1
   dispositions and has seen the note's quoted examples (`775–850°C`, `wt %`,
   `3 × 10⁻² mbar`, `°C min⁻¹`) and one archived draft while writing
   `build_sheet.py`. The rule is therefore partly fitted to shapes L1 had seen.
   L2 is the control for this and is why κ, not L1's labels, is the headline.
2. **The gold is a rule, not a truth.** A different defensible rule would move
   `R` and could move `W`. §2 is committed so a reader can disagree with the rule
   rather than with the arithmetic.
3. **R7/R8 and R11 are the load-bearing choices.** They alone decide 30 of the 53
   blocks. If κ is low on those strata the rule is not decidable enough, and the
   honest finding is that no extension can be licensed yet.
4. **The panel is not a random sample of wrong citations.** It is 5 drafts, and a
   `W` of 0 over 97 draws bounds the false-pass rate only loosely; the report
   quotes the Wilson interval for it rather than "zero".
