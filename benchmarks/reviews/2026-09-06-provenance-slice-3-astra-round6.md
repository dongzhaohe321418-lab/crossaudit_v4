# Independent cross-vendor review of provenance slice 3, round 6 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over 880865b. Verdict: **do not merge** — two P1s and two P2s. A
digit added to a disclosed blocker made it pass (`5 kg m lot_id/2` offered
`kg m`, because "any digit is prose" ran before the joiners were read); the
percent branch bypassed the element refusal (`Ni‰`, all 118 elements); the
disclosure omitted `oz⋅yd`, per-mille, the capitalised half of the
unknown-fragment limit, fragments joined to words and full-width joiners.
Everything else reproduced: every round-5 row, all four ablations to the row,
the 18-entry literal, 45 / 216 / 96 mappings, 13 mutation families. Round 7
reads the joiners before the digit, keeps the element refusal in the percent
branch, and names every remaining shape in the contract, the skill and a
row (30 rows). Verbatim below; paths shortened to the repository root;
trailing whitespace stripped.

---

## Findings
- **P1 — disclosed blockers remain bypassable.** `5 kg m lot_id` correctly blocks, but `5 kg m lot_id/2`, annotated as `kg m`, changes base **BLOCK → head PASS** through both fenced and `results.json` interfaces. The complete annotation `kg m lot_id/2` blocks. The unconditional digit branch at [numbers.py:553](src/crossaudit/dcl/numbers.py:553) reclassifies the mixed token as a prose boundary. `ab_cd/2`, `kg-m/2`, `oz/yd/2`, and `qz/2` reproduce the same fail-open.
- **P1 — the percent/per-mille repair bypasses the element guard.** `5 kg m Ni‰`, annotated as `kg m`, changes base **BLOCK → head PASS** through both interfaces, while `kg m Ni‰` blocks. I reproduced this for all 118 element symbols with both `%` and `‰`. The `%/‰` branch calls `_word()` without preserving the preceding element-symbol refusal ([numbers.py:537](src/crossaudit/dcl/numbers.py:537), [numbers.py:543](src/crossaudit/dcl/numbers.py:543)).
- **P2 — disclosure remains incomplete.** All 20 `DISCLOSED_LIMITS` rows pass their whitespace-normalised contract phrase, skill phrase, and behavior checks. They are not exhaustive:
  - `oz⋅yd` is in `JOINED_UNREADABLE`, but the contract, skill, `_is_boundary` prose, and disclosure rows name only `oz·yd`.
  - `wet‰` is tested, but the contract, skill, and disclosure rows describe only percent signs.
  - The capitalized-unknown half of the stated “four or more letters, or capitalised” limit has no disclosure behavior row.
  - `kg-m/s`, `dry·g`, `lot_id/2`, and full-width joiners are in neither contract nor skill nor disclosure rows.
- **P2 — undisclosed base-PASS → head-BLOCK transitions remain.** Through both interfaces: `kg-m/s`, `dry·g`, `kg／m`, `kg－m`, `lot＿id`, `oz／yd`, and `dry／wet`. The rest of the prior prose/label transition corpus falls under a named disclosed shape.
The other requested attacks behaved as follows: `Sample%` passes, `as-received-dry` passes, `kg-m/s` blocks, `lot_id/2` passes as a strict-prefix boundary, and `dry·g` blocks. Full-width `dry％` passes.
## Verified
- Every round-5 row now has the claimed behavior through both interfaces: `dry%`/`wet‰` pass; `abc%`, `lot_id`, `ab_cd`, `oz·yd`, and `oz⋅yd` block; all six named abbreviations are implemented and `n.b.`/`c.f.` pass.
- Ablations reproduced exactly: shipped `6/0/11/0`; E4 `6/0/0/0`; prefix-only `0/0/11/0`; all-spaced `0/0/11/2`.
- The guarded literal is exactly 18 entries. Adding `ramp` blocks G0056 and invalidates the literal: the two-way door works.
- Historical/helper/declaration mappings are byte-identical across all `45/216/96` cases.
- Only `src/crossaudit/dcl/numbers.py` changes among the named kernel directories. `number_source` remains in no profile; frozen gold/key, `SKILL_B.md`, preregistration, and packaging files retain their required bytes.
- `git diff --check a763dd3..880865b` is clean; worktree remains clean.
- All 13 slice-3 mutation families named in the relevant docstrings reddened their intended tests under in-memory mutation.
- I collected exactly 924 tests from `tests/test_number_source_check.py`. I could not independently execute pytest or the full suite because this review environment has no writable temporary directory; pytest errors while creating `tmp_path_factory`. The claimed `924 passed` and `3711 passed, 4 skipped` therefore remain unconfirmed here.
**Do not merge `880865b`.** The single most important reason is that adding `/2` converts an explicitly disclosed unreadable token such as `lot_id` into a passing strict prefix through both production interfaces. Arm 4 should not run under D160 ruling 3 until this narrowing is fail-closed.
