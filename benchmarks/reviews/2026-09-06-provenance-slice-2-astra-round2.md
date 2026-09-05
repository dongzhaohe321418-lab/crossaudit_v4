# Independent cross-vendor review of provenance slice 2, round 2 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over cd242f6. Verdict: **do not merge**
on one narrow item — the fifth `_UNPARSED` alternative permits whitespace
between the right operand and its superscript, so a footnote after a grid
dimension (`5 x 3 ¹`) is read as an exponent (100/100 false blockers on a
sweep). P1 (the cropped-quote bypass) is closed and survived every added
attack including 625 whitespace combinations; all four mutation counts
confirmed; gold W=0 reproduced for both the shipped and the rejected draft
with Amendment 2's caveat in place; the two pre-existing false passes
(`10 ^ 3`, `5 x 10e3`) do not block this slice. Verbatim below, paths
shortened.

---

**Do not merge.** Reviewed `cd242f6` against `1880d75`, including the first report. P1 is fixed; P2 still introduces a false blocker. No files modified.
1. **P2 remains merge-blocking: a footnote on the right-hand operand is mistaken for an exponent.** The fifth alternative’s trailing `[^\S\r\n]*` permits whitespace between the operand and its superscript marker. See [numbers.py:267](src/crossaudit/dcl/numbers.py:267).
   Source:
   ```text
   Grid dimensions: 5 x 3 ¹
   ¹ Dimensions are in cells.
   ```
   Annotation: `5 / ""`, quoting the complete first line.
   | Interface | Base `1880d75` | Head `cd242f6` |
   |---|---|---|
   | `contains_pair` | PASS | BLOCK |
   | Fenced quotation | Base matcher accepts the line | BLOCKER CA-NUM-002 |
   | Structured `#L1-L2` citation | PASS | BLOCKER CA-NUM-002 |
   A contiguous sweep of `Grid dimensions: N x 101 ¹`, **N=1–100**, produces **0 base blockers and 100 head false blockers**. NBSP before the footnote also reproduces it. This violates the stated rule that a separated superscript is a footnote. The operand’s exponent condition must preserve that distinction, with regression coverage through both interfaces.
   The specifically requested P2 cases otherwise behave correctly: `Participants: 5 ¹` passes; `3 × 10⁻² mbar` annotated `3 / ""` blocks; a newline before `×` does not continue the preceding number; `5 x 3 grid` passes.
2. **P1 passes the original and additional attacks.**
   | Probe | Observed |
   |---|---|
   | All six original rows | BLOCKER CA-NUM-002 |
   | Sign-cropping sweep, 1–100 | **100/100 BLOCK** |
   | Quote spans two occurrences; only second matches | PASS |
   | `50 °C` quoted as `0 °C` | BLOCK |
   | `5 mg/mL` quoted as `5 mg/m` | BLOCK |
   | Only matching occurrence lies outside quotation | BLOCK |
   | Valid occurrence inside, another outside | PASS |
   | Same quote on two lines, with differing pair validity | ADVISORY CA-NUM-004 |
   | Honest compound-unit, percent, temperature and either `Add…hold…` crop | PASS |
   | Quote `then hold at 25 °C.` for `5 / g` | BLOCK |
   There is **no folded-to-raw offset map**: lookup and pair scanning both use the same folded line. That avoids a coordinate mismatch. **625 independent whitespace combinations**, including NBSP, narrow NBSP, tabs and repeated spaces, preserve containment and reject the outside pair.
3. **Gold measurement reproduced, with its limitation.** Across **300 rows—53 blocks, 150 passes, 97 panel draws—base, shipped narrowing and rejected first draft produce identical matcher results**. Thus both narrowing versions reproduce **W=0/R=0**, with zero newly introduced false blockers *in this corpus*.
   The caveat is present in [RESULTS-GOLD.md, Amendment 2](benchmarks/expertlongbench/RESULTS-GOLD.md:440): the corpus lacks separated-superscript footnotes and cannot distinguish the rejected draft. It is recorded in the gold report, rather than added to `CONTAINMENT_RULE.md` itself. The new grid-footnote counterexample demonstrates that limitation again.
4. **All four in-memory mutation counts confirmed.**
   | Mutation | Failing tests |
   |---|---:|
   | Match isolated quotation | **106** |
   | Drop quoted-interval bound | **1** |
   | Restore first-draft `_UNPARSED` | **4** |
   | Replace fifth-alternative inline whitespace with `\s` | **1** |
5. **Skill and documentation corrections confirmed.** The fence guidance contains zero `#L` references and zero `at` fields; the restored structured section contains exactly one `#L`. The requested corrections agree with execution: absent/across-line quotes use -002, ambiguity counts lines, `_derive_at` blanks fences while preserving newlines, `computed:` prefixes `file`, and legacy `at` compatibility requires the new `src`. The “stays bought” assertion is explicitly marked false under isolated matching and corrected to whole-line scanning plus interval containment. The `_span` test now actually applies its mutation.
6. **Round-one confirmations hold.** Both actual archived **97/104-character quotations pass**, with quotation/value/unit hashes verified; committed fixtures accurately identify themselves as synthetic length reproductions. Cross-line and multiline whole-file quotes block; two-line ambiguity remains advisory. Scope refusals—including an existing symlink—hold. Historical **45-row matcher results match base**; boundary tables and exponent sweeps pass. Reconstructed **216 helper / 96 declaration differentials show zero differences**, including ordering.
   Only `dcl/numbers.py` changes within the kernel directories; auditor, broker, ledger, policy, receipt and controller are unchanged. `number_source` remains in **no profile**.
7. **Pre-existing false passes remain:** `10 ^ 3` annotated `10 / ""` and `5 x 10e3` annotated `5 / ""` still pass at base and head. They do **not independently block this slice’s merge**; retain them for the narrowing+E4 work. Arm 4 still waits for narrowing+E4 under D160.
Independent execution: **612 focused tests passed; 30 filesystem-dependent cases deselected**. Arm 3 verifier fixtures pass. Full-suite collection fails in two modules because no temporary directory is writable; the author’s **3429/4** remains unverified here.
**Do not merge—the single most important reason is that the fifth alternative still turns correctly annotated, footnoted grid dimensions into non-overridable blockers.**
