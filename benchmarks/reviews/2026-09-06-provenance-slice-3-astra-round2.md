# Independent cross-vendor review of provenance slice 3, round 2 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over edffde8. Verdict: **do not merge** —
two P1s and a P2. The boundary rule read any unknown alphabetic token of four
or more letters as prose, so `5 kg m mmHg` offered `kg m` and the round-2
omission claim was false again; the substance test came after the fragment
table, so fifteen elements blocked `wt %` where `Ni` passed, and six marked
prose forms blocked after a join; and the token cap fired before the boundary
test, so a complete six-token expression blocked whenever anything followed
it. All three reproduced on our host before anything was changed. Round 3
closes the second and third by giving the join the first continuation's order
and narrows the first to what holds — a fragment of one to three lower-case
letters or a marked one blocks when unnamed; the 18 table entries nothing else
guards are pinned as a literal (`study9/RESULTS.md` §3). The report's "every
configuration clears both kills", "seven redundant entries" and "36 rows" were
also wrong, as found, and are corrected. Verbatim below; paths shortened to
the repository root.

---

**Do not merge `edffde8`.** The original counterexamples are repaired, but the boundary heuristic still creates new partial-unit false passes. I also reproduced new false blocks through both fenced and structured citations. No files modified.
1. **P1 — Unknown longer unit fragments still produce a successful prefix.**
   [`_is_boundary`, line 468](src/crossaudit/dcl/numbers.py:468) treats unknown alphabetic tokens of four or more characters as prose.
   | Source | Annotation | Base → head |
   |---|---|---|
   | `5 kg m mmHg` | `kg m` | BLOCK → **false PASS** |
   | `5 kg m mrad` | `kg m` | BLOCK → **false PASS** |
   | `5 kg m kcal` | `kg m` | BLOCK → **false PASS** |
   | `5 kg m dbar` | `kg m` | BLOCK → **false PASS** |
   Whole transcriptions block. Both interfaces reproduce every row.
   The corrected omission-safety claim is therefore **still false**. Removing only `mbar`, `Torr`, `sccm`, or `µmol` from the fragment table in memory makes `5 kg m <fragment>` newly accept `kg m`. Removing `s` blocks as claimed; the claimed behavior does not generalize.
2. **P1 — Element and prose boundaries break after a join, including previously valid percentage readings.**
   [`_is_boundary`, lines 464–468](src/crossaudit/dcl/numbers.py:464) rejects named fragments before checking element identity. Its prose fallback also rejects labels and marked words.
   | Source, annotated `wt %` | Base → head |
   |---|---|
   | `5 wt % Ni` | PASS → PASS |
   | `5 wt % K`, `5 wt % Pa`, `5 wt % A` | PASS → **false BLOCK** |
   | `5 wt % wet/dry`, `batch-1`, or `sample¹` | PASS → **false BLOCK** |
   | `5 wt % A2`, `Li₂O`, or `H2O` | PASS → **false BLOCK** |
   All **118 elements pass after `5 g`**, as requested. After `5 wt %`, **15 wrongly block**: `B C F H I K N O P Pa S U V W Y`. The full element table does not fix the ordering error.
3. **P2 — The cap fires before checking an actual boundary.**
   [`_spaced_unit`, line 570](src/crossaudit/dcl/numbers.py:570) rejects any nonempty next token after six tokens, including prose, a numeral, or an opening bracket.
   Annotating the complete six-token unit `kg m s⁻² A⁻¹ K⁻¹ mol⁻¹` passes at end-of-line or before a comma, but **blocks** when followed by ` sample`, ` 10 s`, or ` (dry)`. These are false blocks within the stated limit.
The requested reproductions:
| Check | Independently observed |
|---|---|
| Eight boundaries after `5 kg m` | All correct: `kg m` PASS, `kg` BLOCK for comma, period, closing parenthesis, semicolon, second numeral, `(dry)`, em dash, and newline. |
| Original `5 g / 100 mL` | `g`, `g /`, and whole transcription BLOCK. |
| Original seven-token expression | All prefixes and whole transcription BLOCK. |
| Original long marked continuation | `kg m` BLOCK; `kg m mol⁻¹·K⁻¹·s⁻¹` PASS. |
| Original `5 kg m sr` | `kg m` BLOCK; `kg m sr` PASS. |
| Unknown `xyz⁻¹` after a join | `kg`, `kg m`, and whole transcription BLOCK. |
| Token sweep, 7–20, with terminal comma | **175/175 strict prefixes BLOCK; 0/14 whole readings PASS**, through both interfaces. |
| Marked-continuation lengths 13–24 | **0/12 prefix passes; 12/12 whole readings PASS.** |
A valid seven-token expression is a **false block of the whole transcription solely because of the cap**. Rejecting every candidate is safe overflow behavior and is now disclosed, but it remains a readability limitation; calling the cap a loop guard does not eliminate that false block. This is separate from the premature six-token rejection above.
The eight requested prose forms—`wet/dry`, `batch-1`, `sample¹`, `A2`, `Li₂O`, `run-2`, `x/y`, `H2O`—all preserve `g` after `5 g`. All eight reject a correct `kg m` after a join. The required mirrors `g min⁻¹`, `m s⁻¹`, and `mg h⁻¹` correctly reject their prefixes and accept their whole expressions.
Element/unit case distinctions also reproduce correctly **at the first continuation**:
- Bare `Pa` and the listed single-capital overlaps preserve `g`; their `⁻¹` and `·s` forms reject `g` and accept the whole expression.
- `mol`, `cd`, and `sr` continue; `Mo`, `Cd`, and `Sr` remain substances. Marking those three element spellings does not make them named unit fragments.
- `5 J K⁻¹`: `J` BLOCK, `J K⁻¹` PASS.
- `5 mPa·s`: `mPa` BLOCK, `mPa·s` PASS.
All four ablations reproduce:
| Configuration | R | W | R′ | W′ |
|---|---:|---:|---:|---:|
| Shipped | 6 | 0 | 11 | 0 |
| E4 | 6 | 0 | 0 | 0 |
| Narrowing-prefix-only | 0 | 0 | 11 | 0 |
| Narrowing-all-spaced | 0 | 0 | 11 | 2 |
Every configuration retains **10/10 right blocks**, panel **2/97**, zero gold-wrong panel passes. All 300 IDs and text/value/unit hashes match the frozen key; git-loaded base verdicts match **300/300**.
The old narrowing claim is explicitly withdrawn in RESULTS §2 and the D160 trailer; its wording remains only as retracted history. However, RESULTS §1’s **“Every configuration clears both kills”** remains incorrect for `narrowing-all-spaced`.
The seven in-memory mutations reproduce **61 / 29 / 33 / 72 / 4 / 11 / 7** failing tests. The three new mutations redden their intended stopped-scan, marked-prose, and element-collision rows. They do not cover the failures above.
Other verification:
- Contract and shipped skill explicitly name the Ni distinction and unreadable-unit blocking. Their omission guarantee exceeds actual behavior.
- RESULTS §3 correctly acknowledges G0105.
- Only **four** redundant entries were removed: `hour`, `hours`, `minute`, `minutes`. `µm` remains; `%` and `‰` intentionally remain. The “seven … gone” statement is inaccurate.
- `SPACED_UNITS` contains **44 rows**, not RESULTS’ stated 36; both interfaces pass all 88 assertions.
- `SKILL_B.md`, frozen gold/key, and preregistration are unchanged.
- Historical **45-row table**: zero base/head differences. Reconstructed **216 helper / 96 declaration mappings**: zero differences, including ordering.
- **824 numeric tests passed**, including exponent, boundary, quote-window, one-line, and cropping sweeps; 30 filesystem-dependent cases excluded. **127 benchmark tests passed.**
- **3641/4 is not independently verified:** full-suite collection fails in two modules because this read-only sandbox cannot create temporary directories.
- Among the named kernel directories, only `dcl/numbers.py` changes. No profile addition; diff checks pass; checkout remains clean.
**Do not merge — the single most important reason is that an unknown longer unit fragment still makes E4 accept a partial expression that the base correctly blocked. Arm 4 should remain held under D160 ruling 3.**
