# Independent cross-vendor review of provenance slice 3, round 8 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over f1ad9bc. Verdict: **do not merge** on one P2 and no
behavioural finding: every round-7 case and every new attack behaved as
claimed through both interfaces, the 80-token corpus showed no transition
outside a disclosed class in either direction, ablations, literal, mappings,
mutations and frozen objects all reproduced — but the commit said 40
disclosure rows where 38 existed, and two limits the contract states (more
tokens than the scanner reads; an operator with nothing after it) had no row
and no skill sentence of their own. Round 9 names both in the skill, adds
their rows, and reads the row count from the test file. Verbatim below;
paths shortened to the repository root; trailing whitespace stripped.

---

## Eighth independent review — `f1ad9bc`
**Verdict: DO NOT MERGE.** No remaining P1 behavioral bypass was found, but the disclosure evidence still violates the repository’s no-overclaim invariant.
### Finding — P2 disclosure mismatch
`DISCLOSED_LIMITS` contains **38 rows, not 40** ([test table](<tests/test_number_source_check.py:1958>)).
All 38 rows passed four-way verification:
- Contract phrase present.
- Shipped-skill phrase present.
- Fenced interface matches expected behavior.
- Structured `results.json` interface matches expected behavior.
The two apparent missing rows correspond to concrete limitations named in the [contract](<src/crossaudit/dcl/numbers.py:1363>):
- More tokens than the scanner reads.
- An operator with nothing after it.
The [skill](<src/crossaudit/scaffold/templates/PROVENANCE_NUMBERS_SKILL.md:41>) only states the generic “cannot read to its end” rule. Neither condition has a `DISCLOSED_LIMITS` row, although both have behavioral coverage in `STOPPED_SCANS`. Thus the claimed 40-row contract/skill/behavior mapping is not present.
Other disclosure claims check out:
- `g/xyz`, `2/g`, and `2/kg` have rows.
- The full-width-joiner class appears in the contract, skill, and `_is_boundary`.
- All named full-width/mixed cases are either disclosure rows or `JOINED_UNREADABLE` entries. `kg／m-batch` and `10／20` are in the latter, not `DISCLOSED_LIMITS`.
- RESULTS §3 correctly retracts its earlier sentence.
### Behavioral attacks
Every round-7 case now agrees through both interfaces:
- Prefix and whole expression block: `2/g`, `2/kg`, `2／g`, `batch-1/g`, `m₂/s`, `kg／m/dry`, `kg／m-batch`, `kg－m/batch`, `lot＿id/batch`, `oz／yd-batch`, `dry／wet-batch`.
- `2/dry` and `o'clock-1` remain valid prefix boundaries; their whole expressions block.
New attacks also held:
- Digit-led fragments block: `2/m²`, `2/s⁻¹`, `2/dry/g`.
- Joiner cases block: `kg・m`, `kg～m`, `kg／m`, `10／20`.
- Opening brackets do not hide full-width joiners: `(kg／m)`, `[kg－m]`, `{lot＿id}` all block.
- Plain `10` and `2/dry` remain numeral/label boundaries.
The round-6 suffix repairs, 472 element `%`/`‰` checks, and prose boundaries also held. Across the reconstructed 80-token corpus, I found:
- No base-PASS → head-BLOCK transition outside the disclosed blocker classes.
- No base-BLOCK → head-PASS transition outside the disclosed unknown-fragment class.
- No fenced/structured disagreement.
### Remaining verification
- Ablations reproduced exactly: shipped `6/0/11/0`; E4 `6/0/0/0`; prefix-only `0/0/11/0`; all-spaced `0/0/11/2` with the expected kill.
- The table-only literal is exactly 18 entries. Adding `ramp` blocks G0056 and changes the offered-set literal: the two-way door works.
- Historical 45 mappings show zero differences; code governing the 216 helper and 96 declaration mappings is byte-identical to base.
- All 13/13 named slice-3 mutation families reddened their tests.
- All 300 frozen-sheet IDs and 900 value/unit/text hashes match.
- Frozen skill, gold, key, preregistration, and packaging objects remain unchanged as required.
- Only `src/crossaudit/dcl/numbers.py` changed among the named kernel directories.
- `number_source` remains absent from all profiles.
- `git diff --check` is clean, and the worktree remains clean. No files were modified.
I confirmed that 971 focused tests collect. Execution cannot complete in this read-only sandbox because the autouse fixture cannot create its temporary directory, so the claimed `971 passed` and full-suite `3758 passed, 4 skipped` remain independently unconfirmed here.
**DO NOT MERGE — the single most important reason is that the commit asserts a 40-row three-way disclosure contract, but only 38 rows exist and two explicitly contracted scanner limits lack skill-specific disclosure rows. Arm 4 remains held under D160 ruling 3.**
