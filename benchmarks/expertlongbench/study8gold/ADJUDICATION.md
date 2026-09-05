# The third pass — every disagreement, adjudicated

Per PREREGISTRATION-GOLD §4. L1 re-read **only** the disagreeing items, with §2
and no other input. **Neither original label is changed**; `GOLD.csv` carries the
adjudicated label.

| id | L1 | L2 | adjudicated | why |
|---|---|---|---|---|
| G0177 | `?` R6 | `N` R6 | **N**, R6 | The transcribed unit is a strict part of the unit expression the text writes at that occurrence. The qualifier following the percent sign is a statement of the percentage's basis, not ordinary prose, so R6's boundary test — "a unit expression ends where ordinary prose resumes" — puts it inside the expression. R6 does decide the item; L1's `?` was a failure to apply R6's own test, not an ambiguity in it. L2's reading is adopted. |
| G0291 | `?` R6 | `N` R6 | **N**, R6 | The same text and the same pair as G0177, drawn into the corpus by a different row. Adjudicated identically, for the reason above. |

Both items are in the `pass` stratum: the **shipped matcher passes both and the
gold says they are wrong passes**. They are not attributable to any extension —
no extension in `simulate.py` changes their verdict — and they therefore enter no
`W`. They are reported in RESULTS-GOLD §3 as a standing defect of the shipped
containment rule, found by the gold rather than by an extension.

**Zero items are gold `?`.** Every denominator in §5 of the preregistration is
therefore full, and no extension's verdict is undecided for want of a label.
