# Independent cross-vendor review of provenance slice 3, round 9 (final) — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over d02c06c. Verdict: **merge** — "the sole round-8 disclosure
gap is closed without changing executable scanner bytes, and all 42
disclosures now agree with both production interfaces." `numbers.py`
byte-identical to f1ad9bc; ablations to the row; the 18-entry literal and its
two-way door; 42 rows each verified four ways; 13 mutation families red;
frozen objects intact; Arm 4 may run per D160 ruling 3. Reader sentence: "A
spaced unit exceeding six symbols, or ending with `/` or `·` without another
readable symbol, blocks instead of allowing a shorter prefix; use `uncited`."
Verbatim below; paths shortened to the repository root; trailing whitespace
stripped.

---

No P1/P2 findings.
- `numbers.py` is byte-identical to `f1ad9bc`: matching Git blob and SHA-256.
- Ablations reproduced: shipped `6/0/11/0`; E4 `6/0/0/0`; prefix-only `0/0/11/0`; all-spaced `0/0/11/2`. Right blocks remain 10/10; panel 2/97 with zero gold-wrong passes.
- `TABLE_ONLY_GUARDED` is exactly 18 entries. Adding `ramp` blocks G0056 and expands the computed set to 19.
- `DISCLOSED_LIMITS` contains 42 rows. All passed contract phrase, skill phrase, fenced interface, and structured interface verification. No limit sentence lacked a behavioral row.
- The round-8 attack set passed through both interfaces, including 472 element-marker checks. `batch-1/g` and `m₂/s` also block both prefix and whole annotations.
- All 13 named mutation families reddened.
- Only `dcl/numbers.py` changed among kernel directories relative to base; `number_source` is absent from all four profiles.
- The 300 frozen IDs and 900 hashes match. Frozen skill, gold, key, preregistration, and packaging objects match their required Git objects.
- `git diff --check` and the worktree are clean. No files were modified.
I independently confirmed collection of 975 focused tests. The read-only sandbox prevented pytest execution because it cannot create a temporary directory, so the supplied `3762 passed, 4 skipped` full-suite result remains independently unexecuted here.
Reader sentence: A spaced unit exceeding six symbols, or ending with `/` or `·` without another readable symbol, blocks instead of allowing a shorter prefix; use `uncited`.
Arm 4 may run per D160 ruling 3.
**MERGE — the single most important reason is that the sole round-8 disclosure gap is closed without changing executable scanner bytes, and all 42 disclosures now agree with both production interfaces.**
