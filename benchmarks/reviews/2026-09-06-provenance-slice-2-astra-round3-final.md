# Independent cross-vendor review of provenance slice 2, round 3 (final) — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over 8076927. Verdict: **merge.** The
footnoted-grid false blocker is closed; the fifth-alternative attacks
(spaced/tabbed/signed variants) produce no new false pass or block; all five
mutation counts confirmed; gold W=0 reproduced with the stated limitation;
P1 rows, sweeps, whitespace combinations, differentials and scope refusals
unchanged; only `dcl/numbers.py` among kernel dirs; `number_source` in no
profile. Suite 3541/4 re-run on a second host before merge. Verbatim below.

---

**Merge recommended.** Reviewed `8076927` against `1880d75`, including both prior reports. No remaining blocking finding in the requested scope. No files modified.
All results below agree through fenced quotations and structured `#L1` / `#L1-L2` citations.
| Eleven-row regression table | Annotation | Result |
|---|---|---|
| `Grid dimensions: 5 x 3 ¹` | `5 / ""` | PASS |
| Same, NBSP before `¹` | `5 / ""` | PASS |
| `Grid dimensions: 5 x 3 ¹` | `3 / ""` | PASS |
| `5 x 10 ³ g` | `5 / ""` | PASS |
| `a 5 x 3 grid` | `5 / ""` | PASS |
| `Participants: 5 ¹` | `5 / ""` | PASS |
| `5 x 10³ g` | `5 / ""` | BLOCK |
| `5 x 10^3 g` | `5 / ""` | BLOCK |
| `5 × -10³ g` | `5 / ""` | BLOCK |
| `base pressure ≈ 3 × 10⁻² mbar` | `3 / ""` | BLOCK |
| `3×10⁻² mbar` | `3 / ""` | BLOCK |
The contiguous **1–100 footnoted-grid sweep produces 0 blockers through each interface/span**. `10⁵` annotated as `10` still blocks.
| Additional fifth-alternative attack, annotated `5 / ""` | Result |
|---|---|
| `5 x 10 ³` | PASS |
| `5 x 10³ g` | BLOCK |
| `5 ×10³` | BLOCK |
| `5x 10³` | BLOCK |
| `5 x  10³` | BLOCK |
| `5 x\t10³` — actual tab | BLOCK |
| `5 x 10⁻ ³` | BLOCK |
| `5 x 10^ 3` | BLOCK |
The adjacent superscript sign or caret suffices to trigger rejection; whitespace after that marker does not escape it. **No new false PASS/BLOCK found in these attacks.** The pre-existing `10 ^ 3` and `5 x 10e3` false passes remain unchanged.
All five mutations, applied only in memory, reproduce:
| Mutation | Failing tests |
|---|---:|
| Restore trailing whitespace allowance | **104** |
| Match isolated quotation | **106** |
| Drop quoted-interval bound | **1** |
| Restore first-draft `_UNPARSED` | **110** |
| Replace inline whitespace with `\s` | **1** |
Gold reproduction: **300 hash-verified rows**, comprising 53 blocks, 150 passes and 97 panel draws. Base, both rejected drafts and final head give identical matcher results: **W=0/R=0**, no newly passing or blocked rows, panel containment **2/97**. The fixture-side sentence is present and accurate: **zero rows contain digit–whitespace–superscript**, so this gold cannot distinguish the footnote regression from its repair.
Earlier confirmations hold:
- Six P1 rows and the 100-row sign-cropping sweep block; interval and ambiguity attacks remain correct. **625 whitespace combinations** preserve inside/outside containment.
- Historical **45-row matcher table** matches base; boundary tables and exponent sweeps pass.
- Reconstructed **216 helper / 96 declaration mappings** have zero differences, including ordering.
- Actual archived **97/104-character quotations** pass; scope refusals, including an existing symlink, hold.
- Skill halves and documentation corrections remain unchanged. Only `_UNPARSED` changes executable AST since round two.
- Among kernel directories, only `dcl/numbers.py` changes from base; auditor, broker, ledger, policy, receipt and controller are unchanged. `number_source` remains registered and **in no profile**.
Independent execution: **724 focused tests passed, 30 filesystem-dependent cases deselected**; Arm 3 verifier fixtures pass. Full-suite collection still fails in two modules because temporary directories are unwritable; **3541 passed / 4 skipped remains the author’s host result**, subject to the manager’s normal-host merge gate.
For readers: this verifies declared quotation containment, not coverage or scientific correctness; empty units impose no constraint, spaced-unit limitations remain, and precision is normalized.
**Arm 4 waits for the narrowing+E4 slice under D160**, before profile activation.
**Merge — the single most important reason is that the last footnoted-grid false blocker is closed while the scientific-notation and cropped-quote protections remain effective.**
