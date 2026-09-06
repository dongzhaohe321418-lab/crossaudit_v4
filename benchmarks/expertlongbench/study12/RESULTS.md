# Study 12 — slice 6: E2, a list with one trailing unit, measured on the frozen gold

Preregistered at `study12/PREREGISTRATION.md` (be0de4e) before `src/` was touched;
baseline `study12/base-verdicts.jsonl` (the merge base e890dfe's verdict on all 300
items — 166 passes; fourteen rows moved from study 11's base, the fourteen E1 read).
Measured with `study12/measure.py`, which imports the shipped `contains_pair` and
switches E2 off by monkeypatching `_LIST_TAIL`.

## 1. The table, with the kills applied

| configuration | R (wrong blocks removed) | W (wrong passes added, kill) | R′ | W′ (wrong blocks added, kill) | right blocks | panel (≤ 4 of 97 preregistered) |
|---|---:|---:|---:|---:|---:|---:|
| **base** (E2 off) | 0 | 0 | 0 | 0 | 10/10 | 2/97 — equals the frozen base on 300 of 300 |
| **shipped** (E2) | **5** | **0** | 0 | **0** | 10/10 | **2/97** |

Every preregistered gold-metric expectation is met to the row: R = 5 — G0124, G0244,
G0248 (the `wt.%` list members E5 made reachable) and G0134, G0204 (the `and`-separated
pair), all gold `C` — W = 0, R′ = 0, W′ = 0, the ten gold-right blocks still block, the
panel's coincidental-containment count is unchanged at 2 of 97, and the one panel line
holding a list is not newly contained.

## 2. What the gold could not decide

Absent from the gold, shipped as tests (§5 of the preregistration): a member with its
own unit inside a list, a colon or semicolon "list", three members with two separator
kinds, an Oxford comma, `and/or`, a list with no trailing unit, a comma between unrelated
quantities, a spaced expression after the last member, a thousands comma, a range as the
last member (E1 inside E2), refused notation on a member, a word after the last member.
One of those is stated as a limit rather than a rule: a word after the last member is
read exactly as the base reads a word after a single number — the annotation must copy
the source's token, and the check verifies transcription, not whether the token is a
unit — so `heated 5, 10 and 20 were` with `(5, were)` passes as `(20, were)` always
has. A second limit is a narrowing, added by Amendment 1 after probing the false-pass
surface: a number that a label word precedes (`Step 5, 10 mL`, `Fig. 5`, `Sample 5`)
is not a list member — a small named list, `_LABEL_WORDS`, and the safe direction
(under gold R8 read literally those rows would be `C`; the check blocks them). The
gold was re-measured after the guard and the table in §1 is as measured. W = 0 on this gold is *no evidence against* for shapes the corpus lacks
(`RESULTS-GOLD.md` Amendment 2), and the design calls E2's false-pass surface larger
than E1's; the 2 of 97 panel count is the measured part of that.

### What the first review found, and what it changed

Three P1s, all on E2's false-pass surface or its evidence: the label list missed plurals
and a colon (`Figs. 5, 10 °C`, `Pages 5, 10 and 20`, `Step: 5, 10 mL` distributed); a
comma with no whitespace after it read a decimal comma as a list (`12,5 °C` gave
`(12, °C)` where the base blocked it); and the refused-notation mutation test asserted a
row the mutant leaves unchanged. Amendment 2: the label list is built from stems with
their plurals (`_LABEL_STEMS`, now with `tab`, `eqn`, `experiment`, `compound` and the
like), admits a period, colon or hyphen after the word, and reaches E1 as well (`Step
5–10 °C` names steps); a capitalised word outside the list (`Heat 5, 10 mL`) distributes,
stated as the list's limit; a comma separates only with whitespace after it (`5, 10` a
list; `12,5` is neither a list nor a number this check reads — a false block on an English
list written `5,10 °C` is the cost, disclosed); the mutation test asserts `(5, ×)`. The gold was re-measured after each
change and is unchanged (R = 5, W = 0, R′ = 0, W′ = 0).

## 3. What changed, exactly

* `_unit_candidates` gained a second branch after E1's: where the text after the number
  begins with a separator and a number (`_LIST_TAIL`), the members are walked while each
  is a bare number followed by another separator and number; the first member followed by
  anything else is the unit-bearing one, and its unit expression — read by the same
  function with E1 allowed and no further list — is offered with the end offset through
  that unit. A member continued by refused notation stops the list with no reading. A
  member with its own unit never reaches the branch (it is read first), which is the
  preregistered guard.
* The contract string gains one sentence and the shipped skill two. The disclosure table
  pins these, and only these, each to a behaviour — a phrase not listed here is not pinned:
  contract clauses "a comma, 'and' or 'or' and the next number follow it directly", "only
  the last member carries a unit expression", "every member states that unit", "provided
  every member between it and the unit-bearing one is a bare number", "a member with its
  own unit keeps it", "a colon or a semicolon is not a separator", "a comma needs a space
  after it to separate", "neither a list nor a number this check reads", "refused notation
  on a member stops the list", "a number that a label word precedes", "('Step 5, 10 mL',
  'Figs. 5', 'Step: 5')"; skill phrases "every member may be annotated", "a member that
  carries its own unit keeps it", "keeps it", "a colon or a semicolon does not make a
  list", "a comma needs a space after it to separate", "is not a list", "nor a number this
  checker reads", "write `uncited` for a decimal-comma value", "a labelled number",
  "`Step 5`", "`Figs. 5`", "`Step: 5`", "fixed named list", "with their plurals",
  "compounds and the like", "a word outside it does not protect a number". A row may carry
  its own value (the decimal-comma rows test `12,5`); a skill-template patch that silently
  fails (round 2's) reddens on the first of these.
* Tests: 51 rows, two mutation tests (E2 off; the guard, the separators and the notation
  stop), the quotation-interval test. `tests/test_number_source_check.py` 1122 passed.
  Full suite on the host, runner line (round 5): "3909 passed, 4 skipped, 1 warning in 361.41s (0:06:01)".

## 4. Cost

$0.
