# Independent cross-vendor review of provenance slice 3, round 3 — 2026-09-06

Reviewer: `gpt-5.6-sol` (the astra endpoint was at capacity; the standing
fallback), read-only, over efa6b80. Verdict: **do not merge** — two P1s and a
P2. A solidus joining nothing but short unknown parts (`oz/yd`) read as prose
and passed `kg m`, against this branch's own sentence that a short or marked
unknown fragment blocks, and `m2` / `m₂` did the same through the digit rule;
ordinary prose blocked after a join, one row (`5 wt % high-purity powder`) a
regression against the base; and the disclosure was present in six places but
bound to behaviour in none. Everything else reproduced: 88/88 rows, the
2,561-assertion cap sweep, the exact 18-entry table-only-guarded literal, the
two-way door (adding `ramp` blocks gold-correct G0056 and the literal reddens),
all four ablations to the row, 45 / 216 / 96 historical mappings with zero
differences. Round 4 blocks the `oz/yd` shape (and discloses `wet/dry` with
it, a false block after a join in the safe direction), widens the prose
grammar to hyphenated words, abbreviations, other scripts and trailing
punctuation, and binds every disclosed limit to its row. Verbatim below;
paths shortened to the repository root; trailing whitespace stripped.

---

**Do not merge `efa6b80`.** No files modified.
### Findings
1. **P1 — undisclosed partial-unit false pass.**
   `5 kg m oz/yd`, annotated `kg m`, changes **base BLOCK → head PASS** through `contains_pair`, fenced citations, and structured citations; the whole `kg m oz/yd` blocks. Both `oz` and `yd` are short lowercase unknown fragments and the token is solidus-marked, directly contradicting the stated rule that short or marked unknown fragments block. The cause is [numbers.py:513](src/crossaudit/dcl/numbers.py:513): an all-alphabetic solidus expression with no named atom is classified as prose. `m2` and `m₂` produce the same base-BLOCK/head-PASS result.
2. **P1 — ordinary prose still falsely blocks after a join, including a backward-compatibility regression.**
   `5 wt % high-purity powder`, annotated `wt %`, changes **base PASS → head BLOCK** through all three interfaces. Other false-block forms include `e.g.`, `sample，`, and short non-Latin prose such as `样品`. These fall through the supposedly enumerated prose grammar at [numbers.py:462](src/crossaudit/dcl/numbers.py:462). This contradicts the shipped statements that a word is not part of the unit and that punctuation ends a token ([skill:37](src/crossaudit/scaffold/templates/PROVENANCE_NUMBERS_SKILL.md:37), [contract:1270](src/crossaudit/dcl/numbers.py:1270)).
3. **P2 — the synchronized disclosure is still incomplete.**
   The contract, skill, `_is_boundary` docstring, fragment-table comment, RESULTS §3, and D160 trailer consistently describe only the unknown-four-letter/capitalized limit. They omit both classes above. `test_the_shipped_words_say_what_the_scanner_does` passes, but it only checks selected phrases and therefore does not bind those claims to behavior.
### Confirmed
- All 44 `SPACED_UNITS` rows pass through both interfaces: **88/88**.
- Round-2 rows, 118 elements, 26 capitals, marked-prose mirrors, stopped scans, and 7–20-token sweeps otherwise reproduce.
- Cap sweep: **2,561 assertions**, covering six- and seven-token expressions, every enumerated punctuation boundary, prose/numeral/bracket/substance classes, both citation interfaces, and all prefixes: **0 failures**.
- Exact generated omission test passes: **112 entries**, exact 18 literal
  `Bq GHz GPa Gy Hz MHz MPa MeV Sv Torr Wb mbar mmol nmol sccm torr µmol μmol`; all unnamed whole expressions block.
- The table is a two-way door: adding `ramp` blocks gold-correct G0056 (`3 K min⁻¹ ramp`). The pinned-literal test does redden for that addition.
- Measurements reproduce exactly:
  - shipped `6/0/11/0`
  - E4 `6/0/0/0`
  - prefix-only `0/0/11/0`
  - all-spaced `0/0/11/2`
  - right blocks `10/10`; panel `2/97`, zero wrong.
- All eleven in-memory mutations redden their named tests.
- Reconstructed historical comparisons: **45 rows, 216 helper mappings, 96 declaration mappings; zero differences**.
- `SKILL_B.md`, frozen gold/key, and preregistration are byte-identical to their required commits. `number_source` remains in no profile. Only `dcl/numbers.py` changes among the named kernel directories.
- Semantic additivity does **not** hold because of the `wt % high-purity` base-pass/head-block regression.
- Full pytest could not be independently run: the read-only sandbox provides no writable temporary directory. The exact focused test functions were invoked directly and passed.
- `git diff --check` is not clean: the committed round-2 report has trailing whitespace on lines 22, 32, and 41.
**Do not merge — the single most important reason is that `oz/yd` defeats the narrowed guarantee and newly lets a partial unit pass through every interface. Arm 4 must remain held.**
