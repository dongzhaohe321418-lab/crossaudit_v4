# Independent cross-vendor review of provenance slice 3, round 7 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over 97c9f51. Verdict: **do not merge** — two P1s and a P2. The
numeral exit still ran before the joiners, so `5 kg m 2/g` offered `kg m`;
a full-width joiner beside ASCII ones was hidden by the ASCII split
(`kg／m/dry` read as prose through the word `dry`); `g/xyz` had no row and
only one of the five full-width examples was named outside the tests.
Everything else reproduced: every round-6 row, 472 element checks, the
80-token prose corpus with every false block in a disclosed class,
ablations to the row, the 18-entry literal, 45 / 216 / 96 mappings, 13
mutation families. Round 8 decides a full-width joiner anywhere in the
token first, splits a digit-led token on the joiners before calling it a
numeral, and adds the missing rows. Verbatim below; paths shortened to the
repository root; trailing whitespace stripped.

---

## Verdict: do not merge
### Findings
1. **P1 — the joiners still do not run before every digit branch.**
   [`_is_boundary`](<src/crossaudit/dcl/numbers.py:527>) returns `True` for a digit-leading token at line 529 before `_JOINERS` is consulted at line 557.
   Through both fenced and structured interfaces:
   | Source | Annotation | Base → head | Whole annotation |
   |---|---|---|---|
   | `5 kg m 2/g` | `kg m` | BLOCK → **PASS** | BLOCK |
   | `5 kg m 2/kg` | `kg m` | BLOCK → **PASS** | BLOCK |
   | `5 kg m 2／g` | `kg m` | BLOCK → **PASS** | BLOCK |
   These are not the disclosed unknown ≥4-letter/capitalised class. `g` and `kg` are named fragments, so they contradict the claimed “any fragment part blocks” rule.
2. **P1 — mixed full-width/ASCII joiners bypass the disclosed full-width blocker.**
   The ASCII split can leave the full-width expression hidden inside one part; a later named word then makes the entire token a boundary.
   Both interfaces produce base BLOCK → head **PASS** for `kg m`, while the whole annotation blocks:
   - `kg／m/dry`
   - `kg／m-batch`
   - `kg－m/batch`
   - `lot＿id/batch`
   - `oz／yd-batch`
   - `dry／wet-batch`
   This conflicts with the contract and skill’s statement that anything joined by a full-width character blocks.
3. **P2 — disclosure remains incomplete at exemplar/behavior-row level.**
   - All 30 `DISCLOSED_LIMITS` rows do contain their whitespace-normalised contract and skill phrases, and all 60 interface behaviors pass.
   - `g/xyz` is explicitly stated in both public descriptions but has no corresponding behavior row in `DISCLOSED_LIMITS`; its rows exercise only `dry·g` and `kg-m/s`.
   - The claim that all five full-width examples are “named in the contract, skill and `_is_boundary`” is false. Only `kg／m` is literal there. `kg－m`, `lot＿id`, `oz／yd`, and `dry／wet` appear only in tests; only `dry／wet` additionally has a generic disclosure row.
### Requested attacks and prior rows
- Round-6 digit-suffix repairs hold: `lot_id/2`, `ab_cd/2`, `kg-m/2`, `oz/yd/2`, and `qz/2` block the prefix and whole expression through both interfaces.
- All **118 elements × `%`/`‰` × two interfaces = 472 checks** block the preceding `kg m`.
- `Sample%`, `dry%`, `wet‰`, `as-received-dry`, and `dry％` end the joined expression.
- Requested new cases:
  - `batch-1/g`: prefix BLOCK, whole BLOCK.
  - `m₂/s`: prefix BLOCK, whole BLOCK.
  - `2/dry`: prefix PASS, whole BLOCK; consistent with `dry` being a word.
  - `o'clock-1`: prefix PASS, whole BLOCK; contraction boundary works.
  - Mixed full-width/ASCII: unsafe PASS cases listed above.
- In my 80-token prose/label corpus, the **35 base-PASS → head-BLOCK** transitions all fit a disclosed blocker class; no new undisclosed false-block shape appeared.
- Among unit-like base-BLOCK → head-PASS transitions, the disclosed `mmHg`/`kcal`/`mrad`/`dbar`/`GBq` class remains, but `2/g`, `2/kg`, `2／g`, and the mixed-full-width cases above are outside it.
### Other verification
- Ablations reproduced exactly: shipped `6/0/11/0`; E4 `6/0/0/0`; prefix-only `0/0/11/0`; all-spaced `0/0/11/2`. Right blocks remain `10/10`; panel `2/97`, zero wrong.
- The table-only literal is exactly 18 entries. Adding `ramp` blocks G0056 and breaks the literal guard: the two-way door works.
- Reconstructed 45-row historical matcher comparison: zero differences. The code governing the 216 helper and 96 declaration mappings is byte-identical to base.
- All **13/13** slice-3 in-memory mutation families reddened their named tests.
- Focused test execution: **921 passed, 30 temporary-directory fixture errors**. Thus the claimed 951 passes and full `3738 passed, 4 skipped` cannot be independently confirmed in this read-only sandbox. All benchmark tests passed: **127/127**.
- All 300 sheet IDs and 900 text/value/unit hashes match the frozen key.
- `SKILL_B.md`, gold/key, preregistration, and packaging retain their required Git objects.
- Only `src/crossaudit/dcl/numbers.py` changes in the named kernel directories. `number_source` is in none of the four profiles.
- `git diff --check` and final worktree status are clean. No files modified.
**DO NOT MERGE — the single most important reason is that the leading-digit exit still precedes joiner analysis, allowing `2/g` to turn an unreadable continuation into a new strict-prefix PASS through both production interfaces. Arm 4 remains held under D160 ruling 3.**
