# Independent cross-vendor review of provenance slice 3, round 5 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over 5d3b6be. Verdict: **do not merge** — one P1 and one P2, both
narrow. The percent-sign branch tested stem length where `_word()` was owed,
so `5 wt % dry% powder` blocked `wt %` (a named short word); short parts on an
underscore (`lot_id`) or a middle dot (`oz·yd`) blocked as the hyphen and
solidus shapes do but the disclosure named only hyphens and solidi; and the
abbreviation list had six entries where the contract and skill said four.
Everything else reproduced: every round-4 row repaired, every requested
attack as claimed, all 13 disclosure rows binding contract, skill and
behaviour, ablations to the row, the 18-entry literal, 45 / 216 / 96
mappings, 878 + 127 tests. Round 6 uses `_word()` in the percent branch,
names all four joiners and all six abbreviations in both documents, and
grows the disclosure table to 20 rows compared whitespace-normalised.
Verbatim below; paths shortened to the repository root; trailing whitespace
stripped.

---

## Verdict: do not merge `5d3b6be`
Two issues remain.
1. **P1 — undisclosed base-PASS → head-BLOCK classes remain through both interfaces.**
   The clearest counterexample is `5 wt % dry% powder`, annotated `wt %`: base **PASS → head BLOCK** through fenced and structured citations. `dry` is explicitly named in `_SHORT_WORDS`, but the `%`/`‰` branch ignores `_word()` and accepts only stems of four or more letters ([numbers.py](src/crossaudit/dcl/numbers.py:541)). `wet‰` behaves identically. This three-letter threshold is absent from the contract and skill, which say words with trailing punctuation read as words.
   Other transitions outside the claimed enumerated shapes:
   - `lot_id` / `ab_cd`: short parts joined by underscore.
   - `oz·yd` / `oz⋅yd`: short unknown parts joined by a middle dot.
   All are base **PASS → head BLOCK** through both interfaces. Only the broader “short or marked fragment” sentence could be stretched to cover them; the detailed disclosure names hyphens and solidi, not underscores or middle dots.
2. **P2 — executable dotted-abbreviation policy contradicts both public descriptions.**
   `_ABBREVIATIONS` admits six values, including `n.b` and `c.f` ([numbers.py](src/crossaudit/dcl/numbers.py:581)). The contract and skill say every dotted abbreviation except `e.g.`, `i.e.`, `a.m.`, and `p.m.` blocks ([contract](src/crossaudit/dcl/numbers.py:1353), [skill](src/crossaudit/scaffold/templates/PROVENANCE_NUMBERS_SKILL.md:49)). Nevertheless, `5 kg m n.b. note` and `… c.f. note` accept `kg m` through both interfaces. No `DISCLOSED_LIMITS` row detects this mismatch.
### Requested attacks
Both interfaces agreed throughout:
- No `_SHORT_WORDS` entry collides with a `SYNONYMS` key/value or `_UNIT_FRAGMENTS`.
- `pH` PASS; `ph` BLOCK.
- `a.u`, `a.u.`, and `A.U.` BLOCK.
- `E.G` and `E.G.` PASS.
- Apostrophe followed by a digit/space: unknown `qz` forms BLOCK; named `dry` forms PASS.
- Contractions at the first continuation and after a join PASS.
- `sample%` PASS; `dry%` and `wet‰` BLOCK—the P1 above.
- `Ω⁻¹`: prefix BLOCK, whole expression PASS.
- `α²`: preceding join and unreadable whole expression BLOCK; at the first continuation it ends the preceding unit.
All round-4 examples themselves are repaired.
### Disclosure and verification
- All 13 `DISCLOSED_LIMITS` rows contain non-null contract and skill phrases and reproduce their asserted behavior.
- The table is not exhaustive: it misses the `%`/`‰` short-stem cliff, underscore/middle-dot shapes, and the six-versus-four abbreviation whitelist mismatch. The trailing-punctuation row tests only `sample，`, so it overclaims the broader behavior.
- D160’s corrected trailer accurately says every existing row binds contract, skill, and behavior.
- Ablations reproduced exactly: shipped `6/0/11/0`; E4 `6/0/0/0`; prefix-only `0/0/11/0`; all-spaced `0/0/11/2`. Right blocks `10/10`; panel `2/97`, zero wrong.
- Fragment table: 112 entries; exact pinned 18. Adding `ramp` blocks G0056 and makes the literal guard fail.
- Historical 45-row comparison: zero base/head differences.
- The files governing the 216 helper and 96 declaration mappings are byte-identical to base.
- All 13 named mutation families I applied in memory reddened at least one intended test instance.
- `878 passed`, with exactly 30 filesystem-dependent cases excluded; all benchmark tests: `127 passed`.
- The claimed full `3695/4` run could not be independently repeated because this read-only environment has no writable temporary directory.
- All 300 external sheet ID/text/value/unit hashes match the frozen key.
- `SKILL_B.md`, frozen gold/key, and study-9 preregistration have the required matching Git object IDs.
- Only `src/crossaudit/dcl/numbers.py` changes in the named kernel directories; `number_source` remains in no profile.
- `git diff --check` and final worktree status are clean. No files modified.
**Do not merge — the single most important reason is that a named short word with `%` or `‰` still creates an undisclosed, contract-inconsistent base-PASS → head-BLOCK regression through both interfaces. Arm 4 remains held.**
