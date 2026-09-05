# The containment gold — a ruler that is not the matcher

Study 8, gold standard. Preregistered at
`benchmarks/expertlongbench/study8gold/PREREGISTRATION-GOLD.md`, committed at
`9a8fc76` **before any labeller saw an item**, under `docs/design/
CONTAINMENT_RULE.md` §3 and D159 ruling 3.

**n = 300 frozen (located text, `v`, `u`) triples** from Arm 3's archive: all
**53** Arm 3 blocks, a seeded random **150** of the 348 passes, and a
wrong-location negative panel of **97** draws. No generation, no new corpus,
**$0** except the second labeller (`gpt-6-astra`, 44,186 tokens across 5 calls).
Nothing under `src/` is modified.

---

## 1. The headline

> **Cohen's κ = 0.986** (SE 0.010, 95% 0.966–1.000), raw agreement **99.33%**
> (298 of 300), between two labellers blinded to each other and to the matcher.
> **2 disagreements**, both the same text and the same pair, both citing the same
> rule, both adjudicated in the third pass.
>
> **Every extension E1–E6 has `W` = 0.** All six are licensed by this gold.

| stratum | n | κ | raw |
|---|---|---|---|
| all | 300 | **0.986** (95% 0.966–1.000) | 99.33% |
| `block` — the 53 Arm 3 blocks | 53 | 1.000 | 100.00% |
| `pass` — 150 of the 348 passes | 150 | 0.903 (95% 0.769–1.000) | 98.67% |
| `panel` — wrong-location draws | 97 | 1.000 | 100.00% |

Both disagreements are in the `pass` stratum and are the whole of its κ deficit.

**The gold**: 186 `C` (the text states the pair), 114 `N`, **0 undecided**. No
extension's verdict below rests on a missing label.

### The R/W table, with the kill applied

`R` = `block` items the extension turns into passes **and the gold calls stated**.
`W` = items **anywhere in the corpus, panel included**, the extension turns into
passes **and the gold calls not stated**. The note's kill condition, fixed in
advance: **`W` must be 0.**

| extension | mechanism | newly passes | **R** | **W** | R − W | verdict |
|---|---|---|---|---|---|---|
| **E4** — a unit transcribed with a space | M5 | 6 | **6** | **0** | +6 | **licensed** |
| **E5** — a period before `%` continues the token | M6 | 1 | **1** | **0** | +1 | **licensed** |
| **E6** — superscript/sign fold, both sides | M9c | 2 | **2** | **0** | +2 | **licensed** |
| **E1** — the endpoints of a range | M2 | 14 | **14** | **0** | +14 | **licensed** |
| **E2** — a list with one trailing unit | M3 | 2 | **2** | **0** | +2 | **licensed** |
| **E2 + E5**, as the note sequences them | M3 + M6 | 6 | **6** | **0** | +6 | **licensed** |
| **E3** — decimal stoichiometric subscripts | M1a | 11 | **11** | **0** | +11 | **licensed** |
| **U0** — the `_UNPARSED` whitespace narrowing | — | 0 | 0 | 0 | 0 | licensed, no effect on this corpus |
| **wave 1** = E4+E5+E6 | | 9 | **9** | **0** | +9 | **licensed** |
| **wave 1+2** = + E1+E2 | | 28 | **28** | **0** | +28 | **licensed** |
| **all** = + E3 | | 39 | **39** | **0** | +39 | **licensed** |

**Every item any extension newly passes is a `block` item the gold calls stated.**
Not one pass-stratum row and **not one of the 97 wrong-location panel draws** is
newly passed by any extension, alone or in any wave. The panel's
coincidental-containment rate is **2 of 97 = 2.06% [0.57, 7.21]** under the
shipped matcher and **identical under every extension and every wave** — inside
`PROVENANCE_CHECKS.md` §6's preregistered ≤ 5% line, which E1 was required to be
re-measured against before shipping. Both of those two are correct containments
of a bare value at a wrong location (the gold's question is containment, not
whether the citation points at the right line), so the *wrong*-pass rate over the
panel is **0 of 97 = 0.00% [0.00, 3.81]**.

### What the gold says about the 53 blocks

| mechanism | n | gold: wrong block | gold: right block | note §2 disposition |
|---|---|---|---|---|
| M2 | 14 | **14** | 0 | (b) E1 |
| M1a | 11 | **11** | 0 | (b) E3 decimals / (c) integers |
| M5 | 6 | **6** | 0 | (b) E4 |
| M3 | 5 | **5** | 0 | (b) E2 |
| M9c | 2 | **2** | 0 | (b) E6 |
| M6 | 1 | **1** | 0 | (b) E5 |
| M4 | 2 | **2** | 0 | (a) + a skill sentence |
| M11 | 2 | **2** | 0 | D159 ruling 1 (the 80-char cap) |
| M1b | 3 | 0 | **3** | (c) words, (a) a wrong quote |
| M7 | 3 | 0 | **3** | (a) `°C/min` for `°C min⁻¹` |
| M8 | 2 | 0 | **2** | (a) a prefix unit |
| M9a | 1 | 0 | **1** | (a) `3 × 10⁻² mbar` |
| M9b | 1 | 0 | **1** | (c) `degrees` |
| **total** | **53** | **43** | **10** | |

**The gold ratifies `CONTAINMENT_RULE.md` §3.1's dispositions item for item.**
Every class the note called a wrong block is one, on every row; every class it
called a right block is one, on every row. The note's reading of its own corpus
was correct, and it is now correct against something other than itself.

Two wrong blocks no extension reaches: both **M4**, the hyphenated compound
adjective (`2.54-cm diameter`). The gold says the text states the pair; the note
argues at length that no *safe* matcher rule recovers it, and this gold does not
contradict that — it only records that the block is wrong, which is what the
`(a)` skill sentence is for.

---

## 2. The rule, as committed

Verbatim from `PREREGISTRATION-GOLD.md` §2, committed before any item was looked
at. Labels are `C` (the text states the pair), `N` (it does not), `?` (the rule
does not decide). A labeller cites the **lowest-numbered rule that decides** the
item.

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

### The two disagreements, and the third pass

Both are the same line and the same pair, drawn into the corpus twice by
different annotation rows: a percentage whose text continues with a basis
qualifier after the percent sign. **L1 labelled `?` (R6); L2 labelled `N` (R6).**

In the third pass L1 re-read only these two, with the rule and no other input,
and adjudicated **`N`, R6, both**: the qualifier is a statement of the
percentage's basis, not ordinary prose, so R6's own boundary test puts it inside
the unit expression and the transcribed unit is a strict part of it. **L1's `?`
was a failure to apply R6's test, not an ambiguity in it, and L2's reading is
adopted.** Neither original label was changed; `study8gold/ADJUDICATION.md`
carries the record and `GOLD.csv` the adjudicated labels.

---

## 3. What the gold found that no extension was asked about

The gold judges the shipped matcher as well as the proposed changes.

| | gold: stated | gold: not stated |
|---|---|---|
| **matcher passes** | 143 right passes | **11 WRONG passes** |
| **matcher blocks** | **43 wrong blocks** | 103 right blocks |

**The shipped `contains_pair` has a false-pass class, and it is D157 lesson 2's
own defect surviving in a place nobody looked.** In the pass stratum: **11 of
150 = 7.33% [4.14, 12.65]** (Wilson, over annotation rows). Nine of the eleven
are one mechanism: `unit_token` stops at whitespace (`numbers.py:249-264`), so a
transcription of **`°C` satisfies a source that writes `°C min⁻¹`**, `mg`
satisfies `mg h⁻¹`, and `K` satisfies `K min⁻¹`. The whole-token rule that stops
`kg` satisfying `kg-m` does not stop a **prefix of a space-separated compound
unit**, which is exactly the shortening D157 rounds 3–5 record being fixed three
times. The other two are the percent-with-a-basis item of §2.

**This is M5 seen from the other side, and E4 does not close it.** E4 adds the
joined multi-token reading as a *further* candidate, which is why its `W` is 0;
the bare-prefix candidate survives beside it, so `(2, °C)` against `2 °C min⁻¹`
still passes after E4 ships. The repair is a **narrowing** — drop the bare first
token as a candidate where a further unit token follows the number with only
whitespace between — and, being a narrowing, it cannot add a false pass and is
not subject to the kill rule, but it can add a false blocker and so belongs in
front of this same gold. It is not proposed here and not simulated here: this
report records the defect and routes it.

### The block rate, and `PROVENANCE_CHECKS.md` §6's 2% line

`contains_pair`-scoped, so the two 80-character-cap blocks are out of scope
(the matcher passes their located text; D159 ruling 1 removes the cap):

| configuration | blocks / 401 resolvable rows | 95% Wilson | of which the gold says **wrong** |
|---|---|---|---|
| shipped matcher | 51 = **12.72%** | [9.81, 16.34] | 41 |
| wave 1 = E4+E5+E6 | 42 = **10.47%** | [7.84, 13.86] | 32 |
| wave 1+2 = + E1+E2 | 23 = **5.74%** | [3.85, 8.46] | 13 |
| all = + E3 | 12 = **2.99%** | [1.72, 5.16] | **2** |

Those first three columns reproduce `CONTAINMENT_RULE.md` §5 exactly. The last
column is new, and it changes §5's conclusion. §6's line is *of numbers that **do
trace** to the source, no more than 2% blocked* — and 401 is not that
denominator: it includes rows that do not trace. On §6's own estimand, with the
gold supplying the denominator:

| configuration | wrong blocks / rows that do trace | draft-clustered 95% percentile bootstrap |
|---|---|---|
| shipped matcher | **11.28%** | [8.62, 13.14] |
| wave 1 | **9.03%** | [6.58, 11.13] |
| wave 1+2 | **3.88%** | [1.66, 6.07] |
| all = + E3 | **0.62%** | **[0.00, 1.55]** |

**`CONTAINMENT_RULE.md` §5's answer to D159 was too pessimistic.** It concluded
that even with every extension the rule "does not arrive" at 2%, and that
reaching the line depends on the `(a)`/`(c)` skill sentences changing the
generator's behaviour. That conclusion was computed over all 401 resolvable rows.
Against §6's stated estimand the extensions alone land at **0.62%, upper bound
1.55% — under the 2% line, without any skill change** — because the ten right
blocks leave the denominator rather than sitting in the numerator. The skill
sentences remain worth writing; they are no longer what stands between the check
and its design target. **§5's "flat no" is withdrawn to that extent** and the
correction is recorded in `CORRECTIONS.md`.

*This interval is **uncalibrated** (EXPERIMENT_RECORD §10): it combines a census
of the blocks with a sample of the passes, and its coverage has not been
simulated. The point estimate stands; the interval may not be quoted until a
coverage simulation is committed beside it.*

---

## 4. Does anything ship

**Yes — all of wave 1, then E1, then E2, then E3, in the note's own order.**

* **E4, E5, E6 (wave 1).** `R` = 9, `W` = 0, no panel item touched. Licensed. E4
  ships with §3's narrowing filed as a follow-up, not as a condition: the false
  pass it leaves standing exists today and E4 does not worsen it.
* **E1.** `R` = 14, `W` = 0. The note required E1 to be re-measured against §6's
  ≤ 5% coincidental-containment bound before shipping, because it is the first
  rule matching a number to a unit it does not adjoin. **Measured: 2 of 97 =
  2.06% [0.57, 7.21] on the line-scoped negative panel, unchanged from the
  shipped matcher's own rate**, and neither of the two is a wrong containment.
  The bound is met on this panel. Licensed.
* **E2.** `R` = 2 alone, `R` = 6 composed with E5 as the note sequences it,
  `W` = 0 either way. Licensed. The note rated it medium confidence for a reason
  the gold cannot dismiss: prose separates unrelated quantities with commas far
  more often than this corpus does, and 97 draws from 5 drafts is not evidence
  about prose in general.
* **E3, decimals only.** `R` = 11, `W` = 0, and no integer subscript is made
  citable, so the `O2`/`Cr2O3` hazard the note names is not exercised at all on
  this corpus. Licensed — with the note's own reservation intact: E3 is the only
  extension that adds matches **no unit constrains**, so its danger is not
  visible in a corpus where every E3 row is a real composition. Ship it last and
  with its own probe, exactly as §4 sequences.
* **Integer subscripts** stay `(c)`. The gold says an integer subscript *is*
  stated (R11), which is precisely why extending E3 to integers would be safe on
  containment and unsafe on citation: it would make `2` citable from every
  formula on the page, and containment is not the property that protects against
  that. The gold cannot decide it, because it does not ask that question.

**Killed by this gold: nothing.** `W` = 0 on all eleven configurations.

**Cannot be decided by this gold**, and stated as such rather than passed:

1. **Whether E2 is safe on ordinary prose.** Its false-PASS surface is a property
   of prose that separates quantities with commas; this corpus is 48 drafts over
   one task and 5 drafts' worth of negative panel. `W` = 0 here bounds the
   false-pass rate at [0.00, 3.81%] on the panel — not at zero.
2. **Whether E3 is safe where a formula and a measurement share a page.** Every
   M1a row here is a genuine composition, so the extension was never given the
   chance to be wrong.
3. **The M4 hyphen block.** The gold says both are wrong blocks; the note says no
   safe rule reaches them. Both can be true, and the disposition stays `(a)`.
4. **Any question about whether a citation points at the right place.** The gold
   answers containment only. Four panel items — a wrong location whose line
   nonetheless states the bare value — are gold `C`, and the matcher passes two
   of them. That is correct behaviour under this rule and a wrong citation under
   any reader's, and it is `CA-NUM-002`'s limit, not a defect the gold found.

---

## 5. Is the gold trustworthy enough to be the ruler

**On this corpus, yes.** κ = 0.986 with 2 disagreements in 300, both on one text,
both citing the same rule, and both resolved by applying that rule's own test.
κ = 1.000 on the `block` stratum — the 53 rows every extension is judged by — and
κ = 1.000 on the 97 panel draws, which is where a `W` would have appeared.
**Zero items were left undecided.** The rule is decidable enough to be a ruler
for the question the note asks, and the two load-bearing choices §6.3 of the
preregistration named in advance — R7/R8 (ranges and lists) and R11 (subscripts),
which between them decide 30 of the 53 blocks — carry perfect agreement.

**Four things a reader should discount it for.**

1. **L1 is not independent of the design note** and said so in advance
   (preregistration §6.1): L1 wrote the rule from the note's own dispositions and
   had seen the note's quoted examples. That the gold then ratifies the note on
   every one of the 53 blocks is therefore weaker evidence than it looks. **L2 is
   the control**, and L2 is a different vendor, a different session, blinded, and
   given nothing but the rule and the items — and L2 agrees on 53 of 53 blocks
   and 97 of 97 panel draws. A high κ against an independent labeller who never
   saw the note is the part of this that carries weight.
2. **κ measures agreement about a rule, not truth.** Two labellers applying one
   written rule consistently is exactly what κ = 0.986 says, and a different
   defensible rule would move `R`. R5 and R6 are where a reader is most likely to
   disagree: R5 admits `hours` = `h` but refuses `degrees` = `°C`, and R6 refuses
   `%` for `wt %`. Both were fixed in advance and both are argued; neither is the
   only possible rule.
3. **One task, one corpus.** 48 drafts of materials-synthesis prose from one
   ExpertLongBench task. Every statement about ranges, subscripts and compound
   units is a statement about *this* kind of writing.
4. **The panel is 5 drafts.** `W` = 0 over 97 draws is [0.00, 3.81%], not zero.
   The honest reading of the kill condition is "no extension produced a wrong
   pass in 97 opportunities", not "no extension can".

**What would sharpen it.** Nothing in the rule needs sharpening for the block
stratum. The one place the rule bent was R6's boundary between a unit's qualifier
and prose — the single disagreement, twice. R6 should gain one sentence before
the next study reuses it: *a qualifier that states the basis of a ratio or a
percentage (`vol/vol`, `w/w`, `at.`) is part of the unit expression, not prose.*
That sentence is not applied retrospectively here; the two items keep their
adjudicated labels and the adjudication's reasoning is what the sentence records.

---

## 6. Reproduction, deviations, cost

**Corpus.** `~/Documents/Crossaudit/study-data/wt-arm3-runs/arm3`, read-only,
directory digest `6cfe11f0ab4bc78185e227e8624b19cc70e582f0d61cc00e0cf692734b9ea8f9`.
The labelling sheet is derived corpus text and lives beside it at
`~/Documents/Crossaudit/study-data/gold-containment/sheet.jsonl`; **it is not
committed** (EXPERIMENT_RECORD §3). Committed: `study8gold/key.jsonl` (ids,
identities, hashes, the shipped matcher's verdict), `L1.csv`, `L2.csv`,
`GOLD.csv`, `ADJUDICATION.md`, `analysis.txt`, and the four scripts.

```
git checkout study/containment-gold
PYTHONPATH=src python3 benchmarks/expertlongbench/study8gold/build_sheet.py \
    --runs ~/Documents/Crossaudit/study-data/wt-arm3-runs/arm3 \
    --out  ~/Documents/Crossaudit/study-data/gold-containment
PYTHONPATH=src python3 benchmarks/expertlongbench/study8gold/simulate.py  --sheet <out>/sheet.jsonl --gold benchmarks/expertlongbench/study8gold/GOLD.csv
python3 benchmarks/expertlongbench/study8gold/agreement.py --disagreements
PYTHONPATH=src python3 benchmarks/expertlongbench/study8gold/analysis.py  --sheet <out>/sheet.jsonl
```

**Models.** L2 only: `gpt-6-astra` through the Codex CLI 0.153.4,
`model_reasoning_effort="high"`, `--sandbox read-only --skip-git-repo-check`, run
from a scratch directory outside any repository, five calls of 60 items,
**44,186 tokens total**. L1 is this session, by hand. No generator, no auditor,
no corpus regeneration: **the study's marginal cost is one model's five calls.**

**Environment.** Python 3.13, darwin 25.6.0. `simulate.py` asserts on every run
that with no extension enabled it reproduces the shipped
`crossaudit.dcl.numbers.contains_pair` on all 300 items (**300/300**), so every
difference it reports is the extension and nothing else.

**Deviations, numbered.**

1. **`simulate.py` was corrected after it was committed and before any label was
   read.** E1 now also fires where the unit token *is* the range tail (`99-102
   kPa` scans `-102`, an ASCII hyphen being no boundary), and E2 where the token
   is the separator word (`106 and 25 μm` scans `and`) — the two shapes
   `CONTAINMENT_RULE.md` §1 names for M2 and M3 and the first draft missed. Before
   the fix E1 removed 12 of 14 M2 blocks and E2 0 of 5 M3; after it, 14 and 5.
   The correction was made against the *mechanism table*, never against a label.
   Direction of bias: it raises `R`, and cannot lower `W`, so it makes the
   extensions look better than the first draft did — and `W` is 0 either way.
2. **The negative panel is 5 draws per row, not one.** The task's phrasing admits
   one re-point per row (≈ 21 items); the note's §3.2 specifies five draws per
   sampled row. The preregistration took the note's number, committed before
   labelling, giving 97 items instead of ≈ 21. Direction of bias: it can only
   make `W` easier to observe, so it is conservative for the kill condition.
3. **The `block` stratum is Arm 3's 53 BLOCKERs, of which 2 are not containment
   blocks** — the 80-character cap, which D159 ruling 1 removes. Every
   `contains_pair`-scoped table therefore shows 51, and the gold labels both cap
   rows `C`, confirming RESULTS-ARM3 §1's reading of them.
4. **§3's second interval is uncalibrated** and is labelled so at the table: it
   combines a census of the blocks with a sample of the passes and its coverage
   has not been simulated (EXPERIMENT_RECORD §10). A coverage simulation is owed
   before the 0.62% figure is quoted anywhere else.
5. **L1 labelled 2 items `?`; both were adjudicated `N`.** This is §4 of the
   preregistration working as written, not a departure, and is listed here so the
   `?` count in `L1.csv` is not read as an error against `GOLD.csv`.

**Limitations** are §5. The standing ones from EXPERIMENT_RECORD §6 that bear on
this study: one task is one task; and *a model-judged ground truth is not ground
truth* — half of this gold is a model's labels, which is why the headline is κ
and not either labeller's numbers.

## Amendment 1 (2026-09-06)

The one rule sharpening this report said was owed is now written into the
labelling rule as R6a (a basis qualifier — `vol/vol`, `w/w`, `wt` — is part of
the unit expression), dated and after the fact; no recorded label changes. Every
extension measured against this gold from here on is measured under R6a.
