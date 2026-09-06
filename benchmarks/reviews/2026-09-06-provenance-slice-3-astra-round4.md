# Independent cross-vendor review of provenance slice 3, round 4 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over 3428936. Verdict: **do not merge** — two P1s and a P2. The
single-letter-abbreviation rule that admits `e.g.` admitted `a.u.`, `p.u.`
and `r.u.` too, so `5 kg m a.u. signal` offered `kg m`; contractions blocked
after a join because the scanner splits at the apostrophe before the boundary
rule can see the word (`we're`, `don't`, `l'état`), with `α`, `pH`, `sample%`
and `sample_name` beside them, all base-pass regressions; and five of the ten
disclosure rows skipped the skill, so the D160 trailer's "in both the
contract and the skill" was false. Confirmed: the round-3 repairs, a 736/736
end-to-end sweep, the 18-entry literal, all four ablations to the row,
45 / 216 / 96 mappings. Round 5 names the dotted abbreviations that are words
and blocks the rest, reads a letter after an apostrophe as a contraction in
`_spaced_unit`, names a short list of common three-letter words (which lets
`wet/dry` read again), and makes every disclosure row assert a contract
phrase, a skill phrase and the behaviour. Verbatim below; paths shortened to
the repository root; trailing whitespace stripped.

---

**Do not merge `3428936`.** No files modified.
### Findings
1. **P1 — a new partial-unit false pass remains through both interfaces.**
   `5 kg m a.u. signal`, annotated as `kg m`, is base **BLOCK → head PASS** through fenced and structured citations, while the complete `kg m a.u.` does not match. `p.u.` and `r.u.` reproduce identically.
   The broad single-letter-abbreviation rule treats these scientific unit abbreviations as prose ([numbers.py:531](src/crossaudit/dcl/numbers.py:531)). This collision is not disclosed as an unknown-unit false-pass class; the shipped skill identifies only unknown ≥4-letter or capitalised symbols ([skill:43](src/crossaudit/scaffold/templates/PROVENANCE_NUMBERS_SKILL.md:43)).
2. **P1 — the promised apostrophised-word grammar is unreachable for ordinary contractions.**
   `5 wt % we're ready`, `don't`, `l'état`, `we’re`, and `l’état`, annotated `wt %`, are base **PASS → head BLOCK** through both interfaces. The contract and docstring say apostrophised words end the unit, but `_scan` treats straight and typographic apostrophes as boundaries ([numbers.py:197](src/crossaudit/dcl/numbers.py:197), [numbers.py:581](src/crossaudit/dcl/numbers.py:581)). `_is_boundary` therefore receives `we`, `don`, or `l`, not the apostrophised word; its apostrophe split at [numbers.py:543](src/crossaudit/dcl/numbers.py:543) cannot run on the complete token.
   Other undisclosed base-PASS→head-BLOCK prose/label forms found include bare `α`, `pH`, `sample%`, and `sample_name`.
3. **P2 — `DISCLOSED_LIMITS` does not assert “both” contract and skill for ten rows.**
   Five of ten rows set `skill_phrase=None`, and the assertion explicitly skips the skill in that case ([test:1904](tests/test_number_source_check.py:1904), [test:1930](tests/test_number_source_check.py:1930)). Consequently:
   - `kg-m` is checked only against the contract.
   - The skill says `run-2`, but not `m2`/`m₂`.
   - Hyphenated words, abbreviations, other scripts, and retained trailing punctuation are contract-only details.
   - The D160 trailer’s claim that every limit is bound “in both the contract and the skill” is false ([DECISIONS.md:7294](docs/DECISIONS.md:7294)).
### Confirmed
- The claimed repairs themselves work: `oz/yd`, `m2`, `m₂`, and `kg-m` block after a join; `wet/dry` and `x/y` block after a join but end a one-token unit; `high-purity`, `as-received`, `e.g.`, `sample，`, and `样品` pass the preceding join.
- Fresh end-to-end sweep: **736/736** assertions across fenced and structured citations, covering joined prose/unreadable rows, all 118 elements, 26 capitals, first-continuation mirrors, stopped scans, and cap boundaries.
- Gold base-PASS→head-BLOCK transitions: **11**, all the disclosed intended spaced-prefix narrowing; base live matcher equals the frozen key **300/300**.
- Own prose/label corpus: **23** base-PASS→head-BLOCK transitions; only six were the disclosed `wet/dry`/`x/y`/`run-2`/`m2`/`m₂`/`kg-m` shapes. Semantic additivity therefore fails outside the gold.
- Ablations reproduce exactly: shipped `6/0/11/0`; E4 `6/0/0/0`; prefix-only `0/0/11/0`; all-spaced `0/0/11/2`; right blocks `10/10`; panel `2/97`, zero wrong.
- Fragment table: **112 entries**, exact **18-entry** table-only literal. Adding `ramp` blocks G0056 and makes the literal guard fail.
- All eleven earlier in-memory mutation families and the behavioral half of the new disclosure mutation went red. The new test does not detect the missing skill coverage described above.
- Historical reconstructed **45-row** matcher comparison: zero base/head differences. The files governing the prior **216 helper / 96 declaration** mappings are byte-identical to base, so those mappings cannot differ.
- `SKILL_B.md`, frozen gold/key, and study-9 preregistration have matching Git object IDs against their required commits; all 300 sheet ID/text/value/unit hashes match the key.
- Only `dcl/numbers.py` changes among the named kernel directories. `number_source` remains in no profile. Checkout and `git diff --check` are clean.
- **864 passed, 30 filesystem-dependent cases deselected**. The full suite could not be independently rerun because the read-only environment has no writable temporary directory; the claimed `3681/4` remains an author-host result.
**Do not merge — the single most important reason is that `a.u.` still lets a newly supported spaced expression satisfy a strict prefix through both interfaces. Arm 4 remains held.**
