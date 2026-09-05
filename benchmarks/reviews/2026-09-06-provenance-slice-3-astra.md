# Independent cross-vendor review of provenance slice 3 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over 770b372 against a763dd3. Verdict:
**do not merge.** The gold table reproduces (all three configurations, 10/10
right blocks, panel 2/97), all mutation counts confirmed, the 30-row table
60/60, slices 1–2 unchanged. Two P1s: a stopped scan (six-token cap, length
bound, or unrecognised continuation) offers the joined PREFIX as a complete
unit — the prefix defect a fourth time; and short prose carrying a marker
(`wet/dry`, `batch-1`, `sample¹`) is read as a unit, plus element-symbol
collisions in the fragment table (`Pa`, `K`). P2: the narrowing-only
ablation deletes the base's valid `wt %` reading, so "narrowing alone fails"
is the instrument's artefact. Verbatim below, paths shortened.

---

**Do not merge `770b372`.** The reported gold and mutation counts reproduce, but E4 introduces new partial-unit false passes through both interfaces. No files modified.
1. **P1 — A stopped scan is incorrectly accepted as a complete unit.**  
   [_spaced_unit, line 504](src/crossaudit/dcl/numbers.py:504) stops at six tokens or an unrecognized continuation; `_unit_candidates` then offers that prefix as complete.
   | Source | Annotation unit | Base → head |
   |---|---|---|
   | `5 g / 100 mL` | `g /` | BLOCK → **false PASS** |
   | `5 kg m s⁻² A⁻¹ K⁻¹ mol⁻¹ cd⁻¹` | `kg m s⁻² A⁻¹ K⁻¹ mol⁻¹` | BLOCK → **false PASS** |
   | `5 kg m mol⁻¹·K⁻¹·s⁻¹` | `kg m` | BLOCK → **false PASS** |
   | `5 kg m sr` | `kg m` | BLOCK → **false PASS** |
   The third continuation is 13 characters; the fourth uses an omitted fragment. Full transcriptions of these expressions block.
   Contiguous sweeps reproduce the mechanism: expressions of **7–20 tokens all accept their first six**; marked continuation lengths **13–24 all permit the preceding joined prefix**. Thus the bounds and omissions do **not** merely restore an old false pass once E4 has already joined preceding tokens. Overflow must not yield a successful partial reading.
2. **P1 — Short prose carrying a marker becomes a unit.**  
   [_continues_unit, line 404](src/crossaudit/dcl/numbers.py:404) exempts bracketed or long prose, but accepts short prose indiscriminately:
   | Source | Correct annotation | Base → head |
   |---|---|---|
   | `5 g wet/dry sample` | `g` | PASS → **false BLOCK** |
   | `5 g batch-1` | `g` | PASS → **false BLOCK** |
   | `5 g sample¹` | `g` | PASS → **false BLOCK** |
   Conversely, annotations including `wet/dry`, `batch-1`, or the footnoted word newly pass. The bracket/length repair does not establish the promised ordinary-prose boundary.
   The fragment table also contains `Pa`: in a materials reading of `5 g Pa` as five grams of protactinium, `g` newly blocks. The stated exclusion of element symbols is therefore not absolute.
3. **P2 — The narrowing-only interpretation overstates what the instrument proves.**  
   [measure.py, line 47](benchmarks/expertlongbench/study9/measure.py:47) deletes **every** candidate for a spaced expression, including the pre-existing valid `wt %` reading. Its W′=2 is reproducible, but does not prove that removing the bare `wt` necessarily loses `wt %`.
   I independently subtracted prefix readings from the **base’s existing candidate set**, preserving its already-valid whole percent reading and adding no E4 candidates. That gives **R=0, W=0, R′=11, W′=0**. The report should describe its particular ablation without claiming that narrowing alone necessarily fails.
The requested verification results follow.
**Gold reproduction.** All 300 identities and text/value/unit hashes match the frozen key. Running git-loaded `a763dd3` code gives **300/300 equality** with its recorded matcher column. `085379b` changes only the preregistration, which remains byte-identical at head.
| `measure.py` configuration | R | W | R′ | W′ |
|---|---:|---:|---:|---:|
| Narrowing | 0 | 0 | 11 | 2 |
| E4 | 6 | 0 | 0 | 0 |
| Shipped | 6 | 0 | 11 | 0 |
All three retain **10/10 gold-right blocks** and **2/97 panel passes, zero gold-wrong containment**. These findings cover the frozen corpus; they do not dismiss the new counterexamples above.
**Requested adversarial cases.** The committed 30-row table passes **60/60 assertions across fence and structured citations**. I also ran every following disposition through both interfaces; they agree. All annotations below use value `5`.
| Source | Observed disposition and assessment |
|---|---|
| `5 g / mL` | `g` BLOCK; `g / mL` PASS; `g /` BLOCK — all right. |
| `5 °C · min⁻¹` | `°C` BLOCK; whole expression PASS — right. |
| `5 % (w/w)` | `%` PASS — **pre-existing false PASS under R6a**. `% (w/w)` and `% w/w` BLOCK — the basis remains unreadable. |
| `5 g (dry)` | `g` PASS; `g (dry)` BLOCK — right when `(dry)` is descriptive prose. |
| `5 g/` | `g` BLOCK; `g/` PASS — right under literal whole-token containment; this does not validate the malformed unit physically. |
| `5 g / 100 mL` | `g` BLOCK — right; `g /` **new false PASS**; whole expression remains a **false BLOCK**. |
| `5 mg per kg` | `mg` PASS; whole expression BLOCK — **pre-existing semantic false PASS/BLOCK**. Excluding `per` deliberately preserves this limitation. |
| `5 kg·m` | `kg` BLOCK; `kg·m` PASS — right. |
| `5 m s⁻¹ wind` | `m` BLOCK; `m s⁻¹` PASS — right. |
| `5 h 30 min` | `h` PASS; `h 30 min` and `min` BLOCK — right; these are separate quantities. |
| `5 h (heating/cooling rate 10 °C min⁻¹)` | `h` PASS — right; the bracket guard works here. |
| `5 g 10 mL` | `g` PASS; `g 10 mL` BLOCK — right; the second numeral stops continuation. |
**Fragment table.** The 78 entries are:
```text
m cm mm nm pm km µm μm
g kg mg µg μg ng
s ms µs μs ns ps min h
mL µL μL nL
mol mmol µmol μmol nmol
Pa kPa MPa GPa hPa mbar atm Torr torr psi
Hz kHz MHz GHz rpm
eV keV MeV meV kJ mJ kW mW
mA µA μA mV kV
mM µM μM nM
wt vol
sccm ppm ppb
°C °F ° % ‰ Å
hours hour minutes minute
```
For **each entry `t`**, I executed the concrete source formed as `5 g t`, annotated `g`, then removed only that entry in memory:
- **71 entries:** omission changes BLOCK to PASS on that source.
- **Seven redundant entries:** `%`, `‰`, `hour`, `hours`, `minute`, `minutes`, `µm`. No individual-omission witness exists: marker recognition or normalization still recognizes them.
At the first continuation, omission restores the old bare-token behavior. **The general safety claim is false after a preceding join:** removing `s` makes `5 kg m s` accept `kg m`, which the base blocked. Actual omitted `sr` produces the same defect without mutation. Omissions therefore can create **new false passes**, rather than merely preserving old ones.
**Mutations reproduce exactly**, applied only in memory:
| Mutation | Failing tests |
|---|---:|
| Drop continuation loop | 50 |
| Accept bare token beside join | 23 |
| Drop joined candidate | 27 |
| Treat any word as continuation | 54 |
The fourth reddens **all 16 ordinary-prose mirrors**.
**`wt % Ni` is correctly decided:** `wt %` PASS, `wt` BLOCK, `wt % Ni` BLOCK. R6a includes the basis, not the substance. The decision is explicit in preregistration §5 and code commentary/tests. The shipped contract and skill express the general rule but do not explicitly name the Ni distinction. Their old “structural” wording is absent, with passing assertions.
**Slices 1–2 and validation:**
- Historical **45-row numeric table:** zero differences from base.
- Existing exponent sweeps, boundary tests, six P1 quote cases, sign-cropping sweep, quote-window and one-line rules pass within **788 focused tests**; **30 filesystem-dependent cases deselected**.
- Reconstructed **216 helper mappings / 96 declaration mappings:** zero differences, including ordering. These are reconstructed corpora, not claimed identical historical probe inputs.
- **127 benchmark tests pass.**
- Among kernel directories, only `dcl/numbers.py` changes. Auditor, broker, ledger, policy, receipt and controller are unchanged.
- `number_source` remains registered and **in no profile**.
- `git diff --check` passes; checkout remains clean.
- **3605 passed / 4 skipped is not independently verified here.** Full-suite collection fails in two modules because this read-only sandbox cannot create temporary directories.
**Amendment 3 is numerically accurate:** simulator equality is **283/300**, and its 17 mismatches exactly equal the shipped six removals of wrong blocks plus eleven removals of wrong passes. Frozen labels remain unchanged. Using `measure.py` for the shipped comparison is appropriate, subject to the ablation interpretation above.
Keeping study-8 `SKILL_B.md` frozen is acceptable as an archived experimental input; it is byte-identical to base, and the containment note identifies its instruction as retired. I found no newly added archival note beside that file. Arm 4 must use the current shipped skill, not this historical artifact. Also correct RESULTS §3’s claim that the gold contains no bracketed continuation prose: its own G0105 account demonstrates otherwise.
**Do not merge — the single most important reason is that E4 newly accepts partial unit expressions that the merge base correctly blocked. Arm 4 should wait for that defect to be repaired and independently reviewed.**
