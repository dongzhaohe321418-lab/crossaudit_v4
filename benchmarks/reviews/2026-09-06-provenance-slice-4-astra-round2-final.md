# Independent cross-vendor review of provenance slice 4, round 2 (final) — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over 2dc4f78. Verdict: **merge** — "the
original strict-prefix defect is closed through both interfaces, with no
undisclosed prefix regression found in the requested sweeps" (8,960
comparisons; the only new prefix pass is the disclosed `wt.%%`). Scope: only
`_unit_atom`, `_continues_unit`, `_is_boundary`, `_scan`; eight mutations
red; all four gold configurations to the row; base 300/300. Three precision
corrections to RESULTS, applied before the merge: the generated test covers
the 85 eligible alphabetic fragments, `wt.%%` ends the unit only before a
join, 1014 tests, and the boundary rule did change in round 2. Reader
sentence: "Period-percent fragments now preserve complete unit joins, while
recognized prose boundaries retain their earlier behavior." Verbatim below;
paths shortened to the repository root.

---

The original P1 is repaired at `2dc4f78`. I found no additional undisclosed prefix regression in the requested probes.
- **Sweep:** Reproduced the original 180/224 base-BLOCK → first-head-PASS transitions per interface. Current HEAD has **zero**, including four whitespace forms × all five trailing variants (`x`, `sample`, `Ni`, comma, end of line): **8,960 comparisons through both interfaces**.
- **Requested attacks:** The only new prefix PASS was the disclosed `5 kg wt.%%` → `kg`, consistently across all five tails and both interfaces.
The atom and boundary behavior reproduces as follows:
| Token following the unit | First continuation | After an existing join |
|---|---|---|
| `wt.%`, `Bq.%` | Continues; prefix blocks | Continues; prefix blocks |
| `wt.%.` | Reads `wt.%` | Reads `wt.%` |
| `wt..%` | Reads `wt` | Reads `wt` |
| `wt.%%` | Offers preceding single unit | Blocks the joined prefix |
| `K.%`, `Ni.%` | Ends unit | Ends unit |
| `.%` alone | Scanner reads nothing; preceding unit survives | Same |
| `Sample.%`, `dry.%`, `approx.%`, `e.g.%` | Ends unit | Ends unit |
| `qz.%`, `a.u.%` | Ends single unit | Blocks joined prefix |
`Bq.%` correctly continues under this grammar: `Bq` is a named non-element fragment, and continuation is checked before the capitalized-word boundary. Complete joins read before `sample`, `Ni`, comma, or end of line; trailing `x` remains an unknown short token and blocks the complete join.
**Scope and mutation checks:** AST comparison finds only `_unit_atom`, `_continues_unit`, `_is_boundary`, and `_scan` changed since `8c79cc5`, implementing the three repairs. Tests and two benchmark/review documents also changed. Eight in-memory mutations produced assertion failures: reverting each changed function, disabling E5/E6 separately, and moving either exponent fold into `normalise_unit`. All 34 restored guards passed.
**Measurements:** Reproduced base **0/0/0/0**, E5 **1/0/0/0**, E6 **2/0/0/0**, shipped **3/0/0/0**, with **10/10** right blocks and panel **2/97** throughout. Live `815ee02` matches all **300** frozen baseline verdicts.
RESULTS.md needs minor precision corrections: its generated test covers **85 eligible alphabetic fragments**, excluding bare elements/capitals; `wt.%%` ends the unit only before a join; and **1,008** is stale against **1,014 collected**. The earlier “boundary rule unchanged” statement is also superseded by this repair.
I independently ran **984 focused tests successfully**, excluding 30 filesystem-dependent tests and filesystem-dependent conftest setup. The claimed normal-host full suite remains unverified here. No files were modified; worktree status and diff whitespace checks are clean.
Reader sentence: “Period-percent fragments now preserve complete unit joins, while recognized prose boundaries retain their earlier behavior.”
**MERGE — the original strict-prefix defect is closed through both interfaces, with no undisclosed prefix regression found in the requested sweeps.**
