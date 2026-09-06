# Independent cross-vendor review of provenance slice 5, round 2 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over 7db0947. Verdict: **do not merge** on documentation: RESULTS
called spaced-dash ranges and own-unit low endpoints absent from the gold,
while G0004/G0032 (`1.5 – 6 sccm`) and G0214 (`(20°C-25°C)`) are exactly
those; "every preregistered expectation is met" overreached the narrowed dash
grammar; "three disclosure rows" were four; Amendment 1's opening called two
specified matters "not settled". Everything else reproduced: both gold
configurations to the row, the 48-combination dash matrix, every requested
attack, the amendment against code and rows (a branch-after implementation
behaviourally identical on all 300 rows), the mutation evidence, scope.
Round 3 corrects the four sentences; no code changes. Verbatim below; paths
shortened to the repository root.

---

## Findings
1. **Blocking documentation error:** [RESULTS.md](<benchmarks/expertlongbench/study11/RESULTS.md:25>) says ranges with a low-endpoint unit and “spaced dashes” are absent from the gold. The corpus directly contradicts both claims:
   - G0004 and G0032 contain `1.5 – 6 sccm`, a spaced-en-dash range; both are among E1’s fourteen moved rows.
   - G0214 is `(20°C-25°C)`, `(20, °C)`, gold `C`, base `True`: the low endpoint already carries its unit.
   The sentence should distinguish genuinely absent shapes, such as different-unit endpoints and spaced ASCII hyphens.
2. [RESULTS.md](<benchmarks/expertlongbench/study11/RESULTS.md:16>) says “Every preregistered expectation is met.” That is too broad: the original preregistration allowed optional whitespace around ASCII `-`, which Amendment 1 later narrowed. “Every preregistered gold-metric expectation” would be accurate.
3. RESULTS says three disclosure rows bind the contract and skill; there are now four E1 disclosure rows after round 2.
4. Amendment 1’s opening says all three matters were previously “not settled.” Only the chain was unsettled; branch order and whitespace were explicitly specified and later changed. The individual amendment items disclose this honestly, but the opening should say “one clarification and two deviations.”
## Verified
- Measurements reproduced independently:
  - Base: `R/W/R′/W′ = 0/0/0/0`, right blocks `10/10`, panel `2/97`, frozen base `300/300`.
  - Shipped: `14/0/0/0`, exactly the fourteen named rows, right blocks `10/10`, panel `2/97`.
  - Baseline contains 300 unique rows: 152 passes and 148 blocks. Its matcher blob matches `a4fdfa5`.
- Dash matrix, all 48 combinations:
  - ASCII `-`: only no-whitespace/no-whitespace passes; any space, tab, or NBSP on either side blocks.
  - En/em dash: every combination of no whitespace, space, tab, and NBSP passes.
- Requested attacks:
  - `5 -−3 °C`: blocks; glued `5-−3 °C` passes.
  - `5-10-15 °C`: first blocks, middle passes.
  - `5–10 - 15 °C`: first and middle block; final endpoint passes.
  - `−5–10 °C`: negative low endpoint passes.
  - Line-start and post-colon ranges pass.
  - Representative cases behave identically through the fenced `check_number_source` interface.
- Amendment semantics match code and rows. An experimental branch-after implementation was byte-for-behavior identical on all 300 gold rows.
- Mutation evidence:
  - Emptying `_RANGE_TAIL` reddens 12 E1-dependent parameter rows.
  - Restoring round 1’s permissive regex reddens all four spaced-ASCII negative rows.
  - Interior, borrowed-unit, and quote-extent mutations have direct behavioral assertions.
  - Targeted E1 tests: 32 passed. Disclosure tests: 49 passed.
- Since `856fa86`, production changes are limited to `_RANGE_TAIL` plus its comment and the contract sentence; the other changes are the skill, tests, measurement docstring, preregistration/results, and archived review. `measure.py` now correctly names study 11. Worktree and `diff --check` are clean.
- A dated post-run amendment is acceptable as a transparent deviation record, but not as preregistered evidence. Amendment 1 mostly observes that distinction.
I could not rerun the claimed 1,050-test file or full suite because the read-only environment provides no writable pytest temporary directory.
**Do not merge. Single most important reason: RESULTS falsely says spaced-dash shapes are absent from the gold, while G0004 and G0032 are exactly such gold rows, violating the repository’s no-overclaim invariant.**
