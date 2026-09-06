# Independent cross-vendor review of provenance slice 4, round 1 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over 8c79cc5. Verdict: **do not merge**
on one P1: E5 lengthened `wt` to `wt.%`, which `_continues_unit` did not
recognise, so `5 kg wt.%` ended its join at `kg` and offered the prefix —
base BLOCK, head PASS, through both interfaces, 180 transitions in a
224-combination sweep; after a join, `approx.%` and `e.g.%` newly blocked.
Everything else reproduced: all four gold configurations to the row, the
frozen base 300/300 and its 17-row difference from the pre-slice-3 column,
the E5/E6 attack list, the scope (only `_scan`, `pair_occurrences` and the
new `_unit_key`), seventeen mutation variants, the preregistration unchanged
since before `src/` moved. Round 2 makes a fragment with `.%`/`.‰` a unit
atom, reads a word with `.%` as a word at the boundary, refuses `.%` at a
token's start, and sweeps the whole fragment table. Verbatim below; paths
shortened to the repository root.

---

**P1 — E5 introduces a new strict-prefix PASS.**
The [scanner change](src/crossaudit/dcl/numbers.py:659) lengthens the next token, but can **shorten the accepted unit expression**:
| Source | Annotation | Live `815ee02` | `8c79cc5` |
|---|---|---|---|
| `5 kg wt.%` | `(5, kg)` | BLOCK | **PASS** |
| `5 kg wt.‰` | `(5, kg)` | BLOCK | **PASS** |
| `5 kg vol.%` | `(5, kg)` | BLOCK | **PASS** |
Previously, `wt` continued the expression. E5 now scans `wt.%`, which `_continues_unit` rejects. `_spaced_unit` then takes its `len(parts) == 1` exit and offers only `kg`. The complete annotation `kg wt.%` still blocks.
I reproduced this through **both fenced and structured interfaces**, with spaces, doubled spaces, tabs, and nonbreaking spaces. A generated sweep produced 180 such transitions across 224 fragment/suffix combinations. These are synthetic grammar probes, not additional gold-labelled observations.
The repair needs to prevent an E5-extended continuation from becoming permission to accept the preceding prefix, with regression tests through both interfaces.
The remaining verification:
- **Measurements reproduced exactly:**
  | Configuration | R | W | R′ | W′ |
  |---|---:|---:|---:|---:|
  | Base | 0 | 0 | 0 | 0 |
  | E5 | 1 | 0 | 0 | 0 |
  | E6 | 2 | 0 | 0 | 0 |
  | Shipped | 3 | 0 | 0 | 0 |
  Every configuration retains 10/10 right blocks and panel 2/97. Moved IDs are exactly G0098, G0057, G0086.
- **Baseline integrity:** live merge-base matcher matches 300/300 frozen verdicts; all 900 sheet hashes match. Its difference from the old matcher column is exactly slice 3’s 17 rows. Slice 3 and `815ee02` have identical matcher blobs.
- **E5 attacks:** `approx.%`, `e.g.%`, and leading `.%` become whole tokens. `5.%` accepts unit `.%`, while numeral extraction remains `5`. `5.5%` is unchanged. `wt.%.` reads `wt.%`. `wt. %` remains split and its complete annotation blocks. After an existing join, `approx.%` and `e.g.%` can also introduce new blocks.
- **E6 attacks:** `s⁺¹`/`s+1`, spaced bare `⁻`/`-`, and `m²`/`m2` compare equal. `m2` is unit-shaped under the boundary rule, but does not continue like `m²`; E6 does not change that. `10⁵` annotated `10^5` still blocks; value-side minus handling is unchanged. Spaced exponent comparisons work. Identically rendered range endpoints permit folded annotations; mixed-rendering endpoints still block.
- **Scope:** AST comparison finds only `_scan` and `pair_occurrences` changed, plus new `_unit_key`. Protected kernel directories, profiles, packaging, and earlier frozen study files are unchanged. `number_source` remains absent from every profile. `git diff --check` and worktree status are clean.
- **Tests:** 968 focused tests passed with filesystem-dependent fixtures excluded; 30 were deselected. Benchmarks: 127 passed. Thirteen earlier mutation variants—including the requested eleven—and four E5/E6 mutation variants all caused assertion failures in their named guards; restored guards passed. The normal full suite cannot run in this read-only environment, so the claimed 3785-pass result remains independently unverified.
- **Preregistration:** committed before source changes and subsequently unchanged. `R′ = 0 or 1` is an honest pre-stated uncertainty, not an exact prediction. M10’s deferral is supported by zero matching gold shapes. RESULTS’ numerical claims reproduce, but they do not establish safety for the continuation interaction above.
No files were modified.
**DO NOT MERGE — the most important reason is that E5 newly accepts a strict unit prefix through both production interfaces.**
