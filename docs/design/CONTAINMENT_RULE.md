# The containment rule: what "the source contains the pair" should mean

D159 ruling 3 (`docs/DECISIONS.md:7146`). A design note: no code, no model calls. Arm 3
settled addressing — 0 of 401 rows named a location that does not resolve
(`benchmarks/expertlongbench/RESULTS-ARM3.md` §3) — so what is left is the containment
rule, `contains_pair` (`src/crossaudit/dcl/numbers.py:296-325`), meeting legitimate
source text: **51 of 53 blocks are that meeting**, the other two the 80-character cap
D159 ruling 1 disposed of. Denominator throughout: **401 rows with a resolvable
location** (209 A, 192 B; `benchmarks/expertlongbench/study8/rows.jsonl`,
`resolved_location: true`); 348 pass, 53 block. Every count is reproducible corpus-free
from that file plus `study8/containment_classes.py`, committed beside it.

## 1. The six classes, and what actually blocked

The committed `substratum` column (`study8/emit_records.py:48-86`; exploratory, written
after the blocks were seen) groups by *what the source writes*, and its six classes
stand at **range or list A 11 / B 6, stoichiometric subscript 6 / 5, unit rendered
differently 3 / 7, unit is a word not a symbol 4 / 4, hyphenated compound 1 / 1, value
genuinely absent 1 / 2**, plus the over-80-character quote 0 / 2. It is a good first cut
and a poor second one: three of those six each hold two unrelated matcher mechanisms,
and the table below re-groups the 51 by the mechanism that actually fired, with its
disposition from §2.

| # | n | mechanism, and the shape at the named place | disposition |
|---|---|---|---|
| M2 | 14 | the number abuts a dash range, so the unit token is empty or is the range tail — source `775–850°C` / `99-102 kPa` / `1.5 – 6 sccm`, generator wrote `(775, °C)` / `(99, kPa)` / `(1.5, sccm)` | **(b)** E1 |
| M1a | 11 | the value is glued to a letter, so `_NUMBER`'s `(?<![\w.])` (`numbers.py:125`) refuses it — source writes a formula token, generator wrote `(0.8, "")` against `LiNi0.8Co0.2O2` and `(0.95, "")` against `Ni0.95Co0.04Mn0.01(OH)2`; every one of the 11 is a decimal | **(b)** E3, decimals only; **(c)** integers |
| M5 | 6 | **the transcription is byte-exact** and `unit_token` stops at the space — source `heat 5 °C min⁻¹` / `3 K min⁻¹ ramp`, generator wrote exactly those pairs | **(b)** E4 |
| M3 | 5 | the number is a list member and one unit trails the list — source `(0, 20, 40, 80 wt.% …)` / `(106 and 25 μm)`, generator wrote `(0, wt.%)` / `(106, μm)` | **(b)** E2 |
| M1b | 3 | the value is not in the located text at all — 2 stated in words, 1 a quote holding a different quantity | **(c)** ×2, **(a)** ×1 |
| M7 | 3 | the source writes a negative exponent, the generator a solidus — source `°C min⁻¹`, written `°C/min` | **(a)** |
| M4 | 2 | the token begins `-`: a compound adjective — `2.54-cm diameter` | **(a)** + a skill sentence |
| M8 | 2 | the generator transcribed a **prefix** of the source's unit — source `5 wt %`, written `%` | **(a)** |
| M9c | 2 | one unit, two Unicode renderings — `dm3/s` vs `dm³/s`, `s−1` vs `s⁻¹` | **(b)** E6 |
| M6 | 1 | **transcription byte-exact**, but `_scan`'s period rule (`numbers.py:237-244`) cuts `wt.%` to `wt` — `80 wt.%` | **(b)** E5 |
| M9a | 1 | the token is a multiplication sign — `3 × 10⁻² mbar`, written `3 mbar` | **(a)** |
| M9b | 1 | the source writes the unit as an English word — `900 degrees`, written `°C` | **(c)** |

**Is each block right under §3.1?** `PROVENANCE_CHECKS.md:158-162` draws the line at
*another form* — a value in words, a conversion, a rounding, a plot reading.

* **M5, M6 and M9c are wrong blocks, unambiguously.** M5/M6: the transcribed `(v, u)` is
  in the source, adjacent, character for character — not "another form"; the matcher
  cannot read a unit holding a space (`numbers.py:249-264`) or a period before `%`. M9c:
  `dm3/s` and `dm³/s` are one unit under any Unicode normalisation, a font and not a
  claim.
* **M2 and M3 are wrong blocks under a fair reading, and the matcher already agrees with
  itself against them**: `_unit_candidates` (`numbers.py:284-286`) *already* distributes
  a range's unit — `(20°C-25°C)` contains `20 °C`, and it passed in both arms
  (RESULTS-ARM3 §5). Only the spaced or open form fails, so what separates a block from
  a pass is whether the typesetter glued the unit to the first endpoint: notation, not
  semantics.
* **M1a is defensible either way**: the lookbehind is a deliberate refusal and a
  coefficient is arguably "another form", while a domain reader would say the source
  states the composition. The one class §3.1 does not settle.
* **M1b, M7, M8, M9a, M9b and M4 are right blocks** under §3.1 as written: words are the
  section's own example, a solidus for an exponent is a re-notation the generator
  performed, a prefix unit is the defect D157 lesson 2 prevents, `3 × 10⁻²` is not `3`,
  `degrees` names no scale, and M4 D157 left open.

## 2. The dispositions

`(a)` the block stands, the skill instructs differently: copy the unit as the source
renders it (M7), never a prefix of it (M8), never a number the source continues with
`×10ⁿ` (M9a), a unit inside a compound adjective is not a unit token (M4). `(c)`
`uncited` by contract, and the skill must say so: a unit as an English word (M9b), a
value in words (M1b), an integer subscript (part of M1a). `(b)` matcher extension — a
deterministic reading with no truth value from the model — is the rest, each stated with
its D64 mutation and the false pass it could admit.

**E4 — a unit transcribed with a space inside it.** *Rule:* if `normalise_unit(u)` holds
a space, take that many whitespace-separated tokens after the number, each read by
`_scan`, join with single spaces, and offer the join as a further candidate; never fewer
tokens than the transcription has words, never a token cut short. *D64 mutation:* source
`heat 5 °C min⁻¹`, annotation `u: "°C min⁻¹"` — red today, green after; red before and
after are `u: "°C"` (a prefix) and `u: "°C min"` (a truncated join). *False-PASS
surface: none identified* — the candidate list only grows rightward, as the percent
split already does (`numbers.py:287-292`), so no reading shorter than the whole token
appears. It retires `study8/SKILL_B.md:31-38`, which asks the generator to rewrite its
prose so a unit is one token: an instruction that distorts the artefact to suit the
checker.

**E5, E6 — two folds that cannot shorten a token.** *E5:* in `_scan`
(`numbers.py:237-244`) a period continues the token when the next character is
alphanumeric **or** `%`/`‰`. *E6:* before comparison only, and on **both** sides, fold
superscript digits and signs (`⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻`) to ASCII and U+2212 to `-`; `SYNONYMS`
(`numbers.py:201-206`) stays fixed. *D64 mutations:* `80 wt.% sub-micron` with `u:
"wt.%"`, `0.22 s−1` with `s⁻¹`, `0.5 dm3/s` with `dm³/s` — red today, green after; `s-2`
against `s⁻¹` stays red, and `u: "wt"` against `80 wt.%` is a *pass* today that must
become a block. That direction is the point: both are narrowings dressed as extensions,
and lengthening a token can only make matching harder. *False-PASS surface: none* —
except that E6 must be applied to the comparison and **not** to `_UNPARSED`
(`numbers.py:174-178`), which needs raw superscripts to see `10⁵` as notation it cannot
parse.

**E1 — the endpoints of a range.** *Rule:* where the text after a matched number is
`<dash><number>` (`-–—`, optional whitespace) and a unit token follows that second
number, offer that token as a further candidate for the first. **Only the two literal
endpoints; never the interior.** *D64 mutation:* `775–850°C`, `800–1050 °C`, `99-102
kPa` with the low endpoint annotated — red today, green after; red throughout are `(800,
°C)` against `775–850°C` (an interior value) and `(775, kPa)` against it (a unit
borrowed across a different quantity). *False-PASS it could introduce:* the first rule
matching a number to a unit it does not adjoin, so a wrong line holding any range offers
two matches instead of one. `PROVENANCE_CHECKS.md:296-299` measured the shipped rule at
**0.0% (0/1825)** line-scoped (zero by construction, CORRECTIONS #32) against **27.7%** file-scoped; E1 is re-measured against
§6's **≤ 5%** bound before it ships. Refuse the interior reading outright — "the source
says 775–850 °C, so 800 °C is in it" is a truth claim about an interval, D155's line
exactly.

**E2 — a list with one trailing unit.** *Rule:* E1 with `,`, `and`, `or` as separators
**and one guard** — every member between the annotated number and the unit-bearing
member must be a bare number carrying no unit token of its own, so `0, 20, 40, 80 wt.%`
distributes and `0.2 kg, 0.5 kg, or 1 kg` does not. It composes with E5, and an
intervening bare number is skipped rather than taken for a unit. *D64 mutation:* `(0,
20, 40, 80 wt.% …)` and `(106 and 25 μm)` — red today, green after; `(0.2, μm)` against
`0.2 kg, 0.5 kg, or 1 kg` stays red while `(0.2, kg)` stays green by adjacency.
*False-PASS it could introduce:* larger than E1's, because prose separates unrelated
quantities with commas far more often than it writes ranges — `1 : 1 : 0.125–0.5 mass
ratio` already shows the shape where the trailing token is not a unit. Medium
confidence; after E1, measured separately, never bundled.

**E3 — stoichiometric subscripts, and why it is last.** All 11 M1a values carry a
decimal point (`0.01`–`1.25`), and that is the whole discriminator: *a value containing
a `.`, glued directly to a letter, inside a whitespace-delimited token of letters,
digits, brackets and `·`*, is a number with the empty unit. Integer subscripts stay
unreadable, and integers are the danger — otherwise `O2`, `H2O`, `Cr2O3`,
`Co(NO3)2·6H2O` make `2` and `3` citable from every formula on the page. It is still the
riskiest extension here, for a reason independent of its rule: a subscript annotation
has **no unit**, and `contains_pair` returns `True` on the first value match when the
unit is empty (`numbers.py:321-322`), D157's own reader warning. Every other extension
adds a match a unit must satisfy; E3 adds matches nothing constrains. Last, with its own
probe; integers are **(c)**.

**What must never ship.** *The interior of a range* — a truth claim about an interval,
not containment. *A hyphen split for M4*: offering `cm` from the token `-cm` is the only
proposal here returning something **shorter** than the whole token, the defect D157
rounds 3–5 record being fixed three times (`docs/DECISIONS.md:7023`); it would make `2
h-long` satisfy `h` and `10 kg-m` satisfy `kg`, and no boundary rule separates `-cm`
from `-long` without a unit dictionary, which is never complete. *A unit algebra for
M7*: `X/min ≡ X min⁻¹` needs a solidus and a negative exponent to be one operator, and
§3.1 says of the table *nothing here is a conversion* (`numbers.py:218`). *Growing
`SYNONYMS` against this corpus* (`numbers.py:198-200`) — the same reason a matcher
change cannot be judged by its own matcher.

## 3. The measurement problem, and its solution

Arms 2 and 3 are adjudicated by `contains_pair` itself (RESULTS-ARM3 §10). Change the
matcher and the ruler moves with the thing it measures: the 51 residue blocks are
outside the primary's denominator *by construction*, so no extension can improve the
primary, and one that appeared to would be measuring itself. **Corpus:** freeze Arm 3's
440 rows (`study8/rows.jsonl`) and the archived run directory (digest
`6cfe11f0ab4bc78185e227e8624b19cc70e582f0d61cc00e0cf692734b9ea8f9`); no new generation,
no model calls, $0.

**The naive adjudicator cannot serve as gold.** `adjudicator_b`
(`benchmarks/expertlongbench/provenance_arm3.py:506-511`) is "`v` anywhere in the text
and `u` anywhere in the text". Three disqualifications from the committed rows. (1)
**Unsound in the direction that matters**: it calls `3 mbar` contained in `3 × 10⁻²
mbar` — the one row where the check caught a substantive misreading — so a gold built on
it would ratify that block as wrong and ship a false pass by definition. (2) **Not even
an upper bound** on what a sound extension could unblock: it is `False` on 4 of the 10
unit-rendering and 2 of the 8 unit-word blocks, the transcribed unit's bytes being
absent even where the unit is the same unit, so it is not a screen either. (3) Arm 3
ruled on it already: all 42 disagreements are `A−B+`, hand-inspected, **B wrong on 42
and A on 0** (RESULTS-ARM3 §6), so promoting it would invert the study's own finding. It
stays a sensitivity instrument, never a disposition.

**A hand-labelled gold, under a rule written first**, preregistered in this order.

1. **The label rule.** A row is a *wrong block* iff a reader seeing only the transcribed
   `(v, u)` and the located text would say the text states that value with that unit,
   judged on bytes: a range or list endpoint counts as stated and an interior value does
   not; a subscript counts; a value in words, converted or rounded does not; a unit
   differing only in Unicode form or exponent position is the same unit, one differing
   by any other character is not.
2. **The population.** All 53 blocks, a random sample of 150 of the 348 passes at a
   committed seed, and a **negative panel** — five wrong-location draws per sampled row
   (another line of the same file, and another file), which is `provenance_probe.py`'s
   existing instrument. The panel is where a false pass is actually generated: an
   extension's danger is not that it unblocks this corpus, it is that it lets a *wrong*
   citation contain the pair.
3. **The blinding.** Rows shuffled, arm and disposition removed; a second labeller
   (different session, different vendor) over the same set; agreement reported as a
   rate, disagreements reported, never silently resolved.

**The statistic, and the kill.** For extension X: `R` = blocks X removes that gold
labels wrong blocks; `W` = rows in the frozen corpus **and its negative panel** that X
turns into passes and gold labels wrong passes. Report `R − W`, and report `W` beside it
— a net is not a licence. **Kill condition, fixed in advance: an extension that adds
even one wrong pass per hundred correct removals does not ship.** At this corpus's size
`R ≤ 51`, so `W/R < 1/100` means **`W` must be 0**: an extension ships only with **zero
wrong passes**. Independently of `R − W`, it is killed if it raises the line-scoped
coincidental containment rate above §6's preregistered **5%**
(`PROVENANCE_CHECKS.md:332-341`; the shipped rule measures 0.0%, 0/1825 — a figure CORRECTIONS #32 withdraws as zero by construction; the real rate is study 13's 0.54%). And §8g's rate
cannot be recomputed under an extended matcher and compared with Arm 3's: the
denominator is defined by the adjudicator, so comparisons are made on the frozen gold or
not at all.

## 4. Sequencing

By count × confidence, one change per branch, each with its D64 mutation shown red first.

1. **E4** — 6 rows, highest confidence (byte-exact, cannot shorten a token).
2. **E5, E6** — 1 and 2 rows; folds that strictly narrow, E5 a prerequisite for E2.
3. **E1** — 14 rows, the largest single win, but the first rule matching a non-adjacent
   unit; needs the negative panel and the §6 re-measurement.
4. **E2** — 5 rows, medium confidence; only after E1 and E5, never bundled.
5. **E3, decimals only** — 11 rows; last, and with its own probe, because it is the only
   extension that adds unit-free matches.

**Out of band, and not an extension.** `_UNPARSED` (`numbers.py:174-178`) is matched
with no leading-whitespace allowance, so `3×10⁻²` is refused and `3 × 10⁻²` is not; with
an empty transcribed unit that is a **live false pass in the shipped matcher** —
`contains_pair("… ≈ 3 × 10⁻² mbar", "3", "")` returns `True` (`numbers.py:319-322`),
verified against the shipped code while writing this note. Being a narrowing it cannot
add a false pass and is not subject to the kill rule, but it can add a false blocker, so
it goes through the same gold. Fix it first: three of the six classes argue from what
`_UNPARSED` does, and should not argue from a hole in it.

**What Arm 4 carries**, so its blocks are comparable row-for-row with Arm 3's: the
substratum vocabulary (`study8/emit_records.py:40-46`) **plus** a mechanism column using
§1's M-labels, since the substratum alone conflates three pairs of unrelated mechanisms;
the **matcher version id in every row**, so a block under an extended matcher is never
silently compared with one under the shipped matcher; Arm 3's gold labels for any row
shape that recurs; `adjudicator_b` unchanged as a sensitivity instrument with §3's
disqualifications beside it, so no later study promotes it; the `(a)` and `(c)` skill
sentences under test, because half of this note's dispositions are generator-side and
Arm 4 alone measures them; and the **`uncited` rate** as a named secondary against Arm
3's 10.68% (A) and 6.80% (B) — `(c)` pushes rows to `uncited` by design, and a
materially higher rate would mean the block rate was bought by opting out, the failure
`PROVENANCE_CHECKS.md:320-322` names.

## 5. Can the check reach ≤ 2% on real prose?

The design's line is *of numbers that do trace to the source, no more than 2% blocked*
(`PROVENANCE_CHECKS.md:332-341`). Over Arm 3's 401 resolvable rows the shipped matcher
blocks **53 = 13.22% [10.25, 16.88]**, 51 = 12.72% once D159 ruling 1's cap repair
lands; wave 1 (E4+E5+E6) takes it to **42 = 10.47% [7.84, 13.86]**, adding E1 and E2 to
**23 = 5.74% [3.85, 8.46]**, adding E3 to **12 = 2.99% [1.72, 5.16]**. D159's question
therefore gets a flat no on its first half and a qualified no on its second: the rule
cannot come near 2% on real scientific prose without reading ranges and subscripts —
those two classes alone are 30 of the 53 blocks — and even with every extension proposed
here it does not arrive, because the 2.99% residue is twelve rows the matcher is right
to refuse or that only the generator can fix, on an interval that still crosses 5%.
Reaching the line depends on the `(a)` and `(c)` dispositions changing behaviour: if the
skill moves the generator off `°C/min` for `°C min⁻¹` (3 rows) and off `%` for `wt %` (2
rows), the residue is **7 = 1.75% [0.85, 3.56]** — point estimate under the line, upper
bound above it, exactly the position D157 recorded for Arm 1 and refused to call a pass.
D159's "next constraint" is real and it is **not** the last one: the last one is the
generator's transcription discipline, which Arm 4 measures and no matcher change can.

## 6. Classes found after the gold (D161 ruling 4, D164 ruling 2)

Each arm's blocks carry a mechanism label; a class the gold did not hold gets a note here
before anyone touches the matcher for it, with the same terms as §2: its shape, the rule
that produces it, the rows that would license a reading, and the measurement (W = 0 on
the frozen gold plus a designed panel; "measured and not shipped" is a legitimate outcome,
as study 14 showed).

**M10 — a negative exponent written with an en dash** (Arm 4, two rows). Ruled: study 14
implemented the reading as preregistered, measured it (gold all zeros, the two rows
recovered) and did not ship it, because a range across two units has an exponent's shape
and the rule regressed the contract's own `5 g–10 mL` example. The contract and skill say
the shape is not read.

**M12 — a percent sign followed by a capitalised two-letter abbreviation naming the
quantity's basis** (Arm 5, one row, gold C; the source writes the basis after the sign, as
relative humidity is written). *The rule that produces it:* `_is_boundary` reads a bare
capital or a capitalised word after a unit as the SUBSTANCE or the label the quantity is
of — `5 wt % Ni` is nickel, `5 wt % A` a label — and that reading is right for the 118
element symbols and for every capitalised word the gold holds; the basis abbreviation
collides with it exactly, so the join stops at the sign and the transcribed unit (sign +
abbreviation) does not match. *What a reading would need:* a named, finite list of basis
abbreviations that may follow a percent sign (relative humidity's is the one observed;
`v/v`, `w/w`, `w/v` are already carried by R6a as qualifiers, before or after the sign),
read only directly after `%`/`‰`, never after another unit, so that `5 wt % Ni` keeps
its element reading. *Rows:* the frozen gold holds none; Arm 5's one row is the positive;
a designed panel must hold the element collisions (`% Ni`, `% K`, `% Pa` — bare symbols
after a percent sign stay unread) and capitalised words (`% Sample`), each labelled by the
frozen rule. *Measurement:* study N with W = 0 and W′ = 0 on the frozen gold, the panel
as committed tests, the D64 mutation (empty the list) and a preregistered expectation of
R = 0 on the gold (it has no such row) — which means the only positive evidence is the
one Arm 5 row and the panel's own rows, and the note says so: one row is not a licence,
and a list that admits one abbreviation is a rule about that abbreviation. Not scheduled;
recorded so that the next arm's block classification has the name.

**M13 — a currency sign written before the value** (Arm 6, three rows, all gold C; the
legal sources write amounts as a sign followed by the digits, and the draft transcribed
the sign as the unit). *The rule that produces it:* `unit_token` reads ONE whole token
FOLLOWING the number — its docstring enumerates the boundaries, and every reading in
`_unit_candidates` starts after the digits — so a sign that precedes the value is never
read as a unit, and a transcribed unit of that sign matches nothing; the source pair is
`(amount, '')` and the draft's is `(amount, sign)`. *What a reading would need:* a prefix
unit position — a named, finite set of signs read directly before the digits (no space, or
one space), carried into the pair as the unit, with the same boundary discipline as the
suffix reading (`$5 m` is five metres of something priced, not a unit `$m`). *Rows:* the
frozen gold (materials science) holds no currency; Arm 6's three rows are the positives;
a designed panel must hold a sign before a digit that is not a unit of that number (a
footnote marker, a section sign before a number — `§ 5` is a section, not five of
anything, and it is the one prefix sign the legal domain writes most), and the suffix
forms (`5 USD`, `5 dollars`), each labelled by the frozen rule. *Measurement:* as M12's,
with the preregistered expectation R = 0 on the gold; three rows from one domain are the
same non-licence as one row from another. Not scheduled; and D166 rules that this domain's
documents do not meet the contract's line rule in any case, so a prefix reading is second
in line behind the wrap redesign.

**Q2 rendering — a quotation in the named file once typographic apostrophes and
quotation marks are folded to ASCII and line breaks are joined** (Arm 6: 6 of 21 absent
quotations, 28.6%; only 1 of the 6 lies on one line after the typography fold alone, the
other 5 also cross a hard wrap; RESULTS-ARM6 §2, `arm6_rates.py --run`). A fold of `'’`
and `"“”` before the containment test makes no claim about meaning and would, on that
run, recover one row by itself; the other five belong to D166's wrap-join slice. Recorded
as a candidate note, not a slice: one row is not a gold, and the fold's panel (a quotation
whose only difference is a *different* character the fold does not cover) waits for the
wrap-join slice that would give it a population.
