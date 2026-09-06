# Study 14 — results: M10, measured and not shipped

*Second version, after the first review (PREREGISTRATION Amendment 1): the outcome is a
regression against a shipped contract row, not the §3 kill; the measured build's
punctuation set is stated; the measurement script refuses a tree without the rule.*

The preregistered outcome §0 named second. The rule of `PREREGISTRATION.md` §1 was
implemented as written, with one narrowing stated in Amendment 1 (trailing punctuation
was the ASCII set `.,;:!?)]}`, so `5 min–10 min”` blocks where `5 min–10 min.` passes),
at commit 1a817b6 on this branch — kept in the history as the evidence; `measure.py`
reproduces it only there and refuses any other tree — measured, and reverted in the next
commit. Nothing of M10 ships; the class
stays a disclosed limit, now stated in the contract and the skill.

## 1. What the rule did

| measurement | result |
|---|---|
| frozen gold (300; base 182 passes) | R = W = R′ = W′ = 0; right blocks 10/10; panel 2/97; base reproduced 300/300 |
| Arm 4's two M10 rows (archive, counts only) | 2 of 2 pass (0 of 2 under base) |
| tests before the rule (`red-run.txt`) | 21 failed, 96 passed in the M10 and disclosure selections |
| tests after the rule (`green-run-with-rule.txt`) | 1245 passed, **2 failed** |

The gold could not have moved — it holds no letter–dash–digit row — and did not. The
two rows M10 exists for pass. The two failures are the finding.

## 2. Why it does not ship: a regression, not the §3 kill

**`5 g–10 mL` with `(5, g)` went red.** That row is not in the gold and not in §5's panel —
both held, so §3's kill, scoped to those two, did not fire (the first review's finding;
Amendment 1). It is E1's row (study 11), and its sentence is in the shipped contract: a unit after the high endpoint "never reaches a number that
carries its own unit ('5 g-10 mL' distributes nothing)" — the number keeps its own `g`.
Under M10 the scanner reads `g–10` as `g⁻¹⁰`: a letter, an en dash, an unsigned run of
digits that ends the token, and a next token (`mL`) that is not the stem. A range across
two units has exactly the shape of an exponent, and the one guard the preregistration
allowed — the repeated stem — cannot tell them apart. Holding the row would need a second
guard ("the next token is unit-shaped"), which breaks `mol L–1 min–1`; or a third — a rule
§1 does not permit, and the reviewer asked to find a permitted one that holds both found
none. What stops the rule is §7: the suite must be green, and a shipped contract row is
red. The preregistration had even listed `5 mL–10 g` as a limit to disclose — a mistake,
because the same shape with `g` first is a contract example, and a contract example is not
a limit one may disclose around.

The second failure is a disclosure row whose contract phrase the rule's own sentence had
changed (`'s−1' or 's-1'` → `'s−1', 's–1' or 's-1'`); it is a consequence of the first
build's wording and disappears with the revert.

## 3. What ships instead

Words, not a rule: the contract says that a unit whose negative exponent is written with
an en dash (`L·h–1`) is not read, because the en dash is the character a range is
written with, and the skill tells the generator to transcribe such a unit as the source
writes it and expect the block, or to write `uncited` — bound by a disclosure row
(`2 L·h–1` with `(2, L·h-1)` BLOCK, and byte for byte BLOCK). The class is M10 in every Arm's
mechanism table from now on, and it is the one of Arm 4's nine wrong blocks that the
containment extensions leave.

## 4. Why this is the right outcome and not a failure of nerve

Two rows in fifty procedures, against a rule that changes what the scanner takes for a
token boundary in every unit expression. The gold measured the rule at zero cost only
because the gold has no such shape, and the panel this file designed missed the cost; the
suite found it, in a shape the contract already names. The design's sentence — "its surface is the surface of a closed-up
range" — was the prediction, and the prediction held.

## 5. Full suite

`4004 passed, 4 skipped, 1 warning in 347.57s (0:05:47)` (HEAD: the rule reverted, the limit stated).
