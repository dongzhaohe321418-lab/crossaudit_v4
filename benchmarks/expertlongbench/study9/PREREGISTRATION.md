# Study 9 — the spaced-unit narrowing and E4, preregistered against the frozen gold

Committed **before any line of `src/` is touched**, under D160 rulings 1–2 and
`docs/design/CONTAINMENT_RULE.md` §3. The corpus is frozen and already published
(`benchmarks/expertlongbench/RESULTS-GOLD.md`), so what is preregistered here is
not the corpus but **the rule, the statistic, the kill, and the numbers I expect
before I have run anything**. Nothing under `study8gold/` is modified.

## 1. The two rules, verbatim

**Narrowing (D160 ruling 1).** Today `unit_token` stops at whitespace, so a bare
`°C` satisfies a source that writes `°C min⁻¹`, `mg` satisfies `mg h⁻¹`, `K`
satisfies `K min⁻¹` — 9 of the gold's 11 false passes (7.33%). Rule: when the
token after a number is followed by whitespace and a **unit-shaped
continuation** — a token that is letters/symbols carrying a superscript,
`⁻¹`/`^-1`/`-1`, a solidus, a middle dot, or a member of the synonym table — the
bare first token does NOT satisfy the annotation; the whole spaced expression is
the unit. This removes the nine false passes and can add no new pass. Mirror
(must stay green): `5 g sample`, `5 g of powder`, `2 h later` — a word is not a
unit fragment.

**E4 (extension).** The same spaced expression becomes a candidate the
annotation CAN match in full: source `5 °C min⁻¹` annotated `5 / °C min⁻¹` →
PASS (today it blocks because the token stops at the space). Whole-token
comparison still applies to the whole spaced expression; a prefix (`°C`) never
satisfies.

Together: the annotation must name the whole unit the source writes, spaced or
not.

### 1a. One deviation from the verbatim rule, named in advance

The verbatim rule's continuation set ends "or a member of the synonym table".
`SYNONYMS` (`numbers.py:302-307`) holds `hours, hour, minutes, minute, wt %,
mol %, µm` and nothing else, so under the sentence read literally the token `m`
in `5 kg m` is not a continuation and `kg` keeps satisfying it — a strict prefix
of the unit expression `kg m`, which the gold's R6 calls not stated, and which
D160's own adversarial list requires to BLOCK. The two halves of the sentence
disagree, and the disagreement is recorded rather than resolved silently.

**What ships:** a continuation is a token that carries a *unit-structural
marker* — a superscript digit or sign (`⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻`), a letters-then-exponent
shape (`s-1`, `min−1`, `m^2`, U+2212 read as `-`), a solidus, a middle dot, or
`%`/`‰` — **or** is a member of a small fixed unit-fragment table that contains
the synonym table's keys. The table is stated with its exclusions in the code:
no English function word (`of`, `in`, `at`, `a`, `and`, `per`, `to`, `with`), no
bare capital and no element symbol (`K`, `A`, `N`, `Ni`, `Ti`), because those
are what ordinary prose and materials prose put after a quantity. **The table's
incompleteness fails toward today's behaviour** — a unit symbol it does not name
leaves the existing bare-token pass exactly as it is now, which is why an
incomplete table here is not the defect the containment note warns about (there
a dictionary would have *shortened* a token; here it can only lengthen one). Its
only harm is a wrong inclusion, and a wrong inclusion is a false blocker, which
is what §3's second quantity measures.

## 2. The corpus

The gold's **300 frozen rows** — 53 Arm 3 blocks, 150 sampled passes, 97
wrong-location panel draws — with `GOLD.csv`'s adjudicated labels under R6a
(Amendment 1). The sheet is derived corpus text and is not committed
(`~/Documents/Crossaudit/study-data/gold-containment/sheet.jsonl`); `key.jsonl`
carries the identities and hashes. No generation, no model calls, $0.

**Amendment 2 governs how the result may be read.** W = 0 on this gold is *no
evidence against*, not *no regression*: the gold is a kill screen for the six
classes of `CONTAINMENT_RULE.md` §1 and the wrong-location panel, and is silent
about every class it lacks. Both halves of this slice touch a mechanism the
corpus exercises thinly (nine rows, all of them `°C min⁻¹`-shaped) and one it
does not exercise at all (a bare word after a unit, a plain unit symbol after a
unit, a spaced unit annotated in full). Those classes therefore ship as
**adversarial cases in the slice's own tests**, listed in §5, and the report
says which classes the gold covers in the same sentence as it quotes W.

## 3. The statistic, and the kill

`CONTAINMENT_RULE.md` §3, unchanged:

* **R** = rows the change turns from BLOCK to PASS that the gold labels `C`
  (the text states the pair) — wrong blocks removed.
* **W** = rows anywhere in the corpus, **panel included**, that the change turns
  from BLOCK to PASS and the gold labels `N` — wrong passes added.
* **The kill: W must be 0.** If W > 0 for either half, stop and report; do not
  tune.

A narrowing turns no block into a pass, so **R = 0 and W = 0 hold for it by
construction** and neither quantity counts the nine false passes. The nine are
counted by two further quantities, named here because §3 does not have them:

* **R′ (wrong passes removed)** = rows the change turns from PASS to BLOCK that
  the gold labels `N`. This is the quantity that counts the nine.
* **W′ (wrong blocks added)** = rows the change turns from PASS to BLOCK that
  the gold labels `C`. **W′ must be 0**: no gold-correct pass may be lost. This
  is the narrowing's kill, the mirror of W, and it is the only way a narrowing
  can do harm.

R, W, R′ and W′ are reported for each half separately and for the two composed,
measured **on the shipped code** (not on a simulator re-implementation), against
`GOLD.csv`.

## 4. What I expect, before running

**Narrowing.**

* R′ = **9** — the nine spaced-unit false passes D160 names (`°C` against
  `°C min⁻¹`, `mg` against `mg h⁻¹`, `K` against `K min⁻¹`), each gold `N` under
  R6.
* R′ = **11**, stated as a secondary prediction and made before running: the
  other two of the gold's eleven false passes are `%` transcribed against
  `20% vol/vol ethanol`, and `vol/vol` carries a solidus, so the same rule
  reaches them. R6a (Amendment 1) says a basis qualifier is part of the unit
  expression, so removing them is correct under the gold and they are counted in
  R′, not treated as collateral. If the measured R′ is 9 rather than 11 the rule
  did not reach them and that is reported as a miss, not repaired.
* W′ = **0** — no gold-`C` pass lost. This is the kill for this half.
* R = 0, W = 0 by construction; both are reported anyway, because a narrowing
  that unblocked anything would mean the change is not a narrowing.

**E4.**

* R = **6** — the six M5 rows (`RESULTS-GOLD.md` §1, E4 licensed at R = 6).
* W = **0**. This is the kill for this half.
* R′ = 0, W′ = 0 for E4 taken alone; measured composed with the narrowing, the
  composed change is expected at R = 6, W = 0, R′ = 11, W′ = 0.

**The 10 right blocks.** The gold labels 10 of the 53 blocks right blocks (M1b
×3, M7 ×3, M8 ×2, M9a ×1, M9b ×1). **All 10 must still block** after both
halves. A right block that becomes a pass is a W by definition and fires the
kill; it is called out separately because it is the specific thing "additive in
`dcl/`" is claimed to guarantee.

**The panel.** 0 of the 97 wrong-location draws may be newly passed. The panel's
coincidental-containment rate stays 2 of 97 = 2.06%, inside
`PROVENANCE_CHECKS.md` §6's ≤ 5%.

## 5. The adversarial cases the gold cannot supply

Each is asserted through **both interfaces** — the fenced
` ```crossaudit-numbers ` block and a `results.json` quantity whose `source`
carries a `#L` fragment — and each ships in `tests/`.

| source | annotated unit | required |
|---|---|---|
| `5 °C min⁻¹` | `°C` | BLOCK |
| `5 mg h⁻¹` | `mg` | BLOCK |
| `5 K min⁻¹` | `K` | BLOCK |
| `5 °C min⁻¹` | `°C min⁻¹` | PASS |
| `5 m s⁻¹` | `m s⁻¹` | PASS |
| `5 m s⁻¹` | `m` | BLOCK |
| `5 g sample` | `g` | PASS |
| `5 g of powder` | `g` | PASS |
| `2 h later` | `h` | PASS |
| `5 kg m` | `kg` | BLOCK |
| `5 kg m` | `kg m` | PASS |
| `5 wt % Ni` | `wt %` | **PASS** — decided below |
| `5 mol L⁻¹` | `mol` | BLOCK |
| `5 mol L⁻¹` | `mol L⁻¹` | PASS |

**`5 wt % Ni`, decided and stated.** `Ni` is **not** a continuation. It carries
no marker and it is not in the unit-fragment table, and it is deliberately not
in it: an element symbol after a quantity is the commonest thing materials prose
writes there (`5 wt % Ni`, `20 g Ti`), and reading it as part of the unit would
block a correct annotation on every one of them. R6a puts the *basis qualifier*
inside the unit expression (`wt`, `vol/vol`, `w/w`) and says nothing about the
substance the percentage is of, so the unit expression at `5 wt % Ni` is `wt %`
and the annotation `wt %` names it whole. Consequently `wt` alone against
`5 wt % Ni` must BLOCK — `%` carries the marker, so the bare first token is
narrowed away — and that case ships with the table above.

## 6. The D64 mutations, each shipped with its mirror

| mutation | what must redden |
|---|---|
| stop at whitespace again (drop the continuation scan) | the narrowing BLOCK cases |
| accept the bare first token when a continuation exists | the narrowing BLOCK cases |
| drop the joined spaced expression from the candidates | the E4 PASS cases |
| treat any word as a continuation | the mirrors (`5 g sample`, `5 g of powder`, `2 h later`) |

## 7. What else must hold

* `dcl/` only, additive in the sense the slice claims: the narrowing is
  strictly stricter and E4 only ever offers a reading **at least as long as** the
  whole token, so no previously-blocked wrong annotation can pass. The 10 right
  blocks are the evidence, not the argument.
* No change to `auditor/`, `broker/`, `ledger/`, `policy/`.
* `number_source` stays in no profile (D159 ruling 2, D158 ruling 3).
* The contract string's "structural" sentence and the skill's
  write-it-joined-or-`uncited` paragraph are **deleted**, both replaced with
  *write the unit exactly as the source writes it, spaces included*.
* Gate: the full suite in the foreground, then `benchmarks/`, then the gold
  simulator. Baseline on the merged base is 3541 passed / 4 skipped.

## 8. Reproduction

```
PYTHONPATH=src .venv/bin/python benchmarks/expertlongbench/study9/measure.py \
    --sheet ~/Documents/Crossaudit/study-data/gold-containment/sheet.jsonl
```

`measure.py` imports the **shipped** `crossaudit.dcl.numbers.contains_pair` and
compares it row for row against a baseline verdict frozen from the merge base
(`key.jsonl`'s `matcher` column), so what it reports is the shipped code and
nothing else. Measured R/W/R′/W′ are committed beside the expectations above in
`RESULTS.md`.
