<!-- verbatim: codex exec -m gpt-6-astra, read-only, on study/provenance-arm5 at 4801eae (a commit since replaced: its results prose quoted corpus fragments and was rewritten out of the branch history); archived unedited — the report itself quotes no corpus text -->

Not quotable yet. The preregistered Wilson result does independently remain **4/398 = 1.01%, 95% Wilson 0.39–2.56%, PASS**, but several publication-blocking defects remain.

### Findings

1. **Blocking — licensed corpus fragments were committed.** Direct comparison found eight exact T03 fragments in [RESULTS-ARM5.md](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm5/benchmarks/expertlongbench/RESULTS-ARM5.md:55), at lines 55, 57–59 and 99–101. This contradicts §7’s “no corpus text” claim. The structured rows, manifest, key, CSVs, and report JSON contain no raw text/value/unit/quotation fields; the leakage is in the prose.

2. **Major — the registered bootstrap seed was not used.** [provenance_arm4_report.py](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm5/benchmarks/expertlongbench/provenance_arm4_report.py:28) retains Arm 4’s seed `20261106`; Arm 5 registered `20261107`. With the registered seed:

   - Primary bootstrap: **0.24–1.97%**, not 0.24–1.99%.
   - `uncited`: **5.46–13.16%**, not 5.43–13.12%.

   The Wilson interval and PASS decision do not change.

3. **Major — the matcher diff does not exercise the shipped quotation contract.** [arm5_matcher_diff.py](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm5/benchmarks/expertlongbench/study8/arm5_matcher_diff.py:66) calls `contains_pair` on the whole located line and ignores the quotation interval. Recomputing with `_pair_in_quote` gives:

   - 7 block under both,
   - 33 pass now / block before,
   - 361 pass under both.

   Thus the contract-correct movement is **33/401**, not 34/401. The extra apparent move is the M9b row: E1 finds the pair elsewhere on the line, outside the quotation.

4. **Major — “M11, new” collides with the frozen taxonomy.** M11 already denotes the two 80-character-cap blocks in [RESULTS-GOLD.md](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm5/benchmarks/expertlongbench/RESULTS-GOLD.md:80) and [containment_classes.py](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm5/benchmarks/expertlongbench/study8/containment_classes.py:84). The capitalized-abbreviation failure is real and C-labelled, but requires a new unused identifier.

5. **Major — the preserved start state is misreported.** The archived and committed manifest records seven dirty entries, including the report script and five Arm 5 study files, not only the corpus mount; see [manifest-arm5.json](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm5/benchmarks/expertlongbench/study8/manifest-arm5.json:140). Moreover, only the plan *without* `git_status` appears in `arm5.log`; §6’s claim that the plan was printed “in full” and restored solely from that log is unsupported.

6. **Additional report errors/omissions.**

   - M9b’s “right by contract, wrong by the gold rule” characterization is exact: the gold evaluates the located line while the contract requires the satisfying occurrence inside the quotation. But [RESULTS line 56](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm5/benchmarks/expertlongbench/RESULTS-ARM5.md:56) cites R13; its gold record is **R7**.
   - The six Arm 4 E1/E2 blocks are gone, but they occupied **four instances**, not the reported five.
   - One M4 case has the hyphen between value and unit; the other has it after the unit. The table describes both as the latter.
   - Blob `620fb3bc…` is correct, but `7691827` is not its slice-8 merge commit; that commit contains blob `203f61e3…`. The slice-8 merge is `edda6da`.
   - The strata omit preregistered bootstrap intervals and `uncited` intervals. Several other reported rates likewise omit the Wilson/bootstrap evidence required by §6 and EXPERIMENT_RECORD §9–§10.
   - “Not materially higher” has no registered materiality threshold.
   - The census rationale says the other tasks have no traceable numbers, while its own table identifies T01 as highly value-traceable; the valid rationale is deferral because of task shape/input cost, not absence.
   - [arm5_sheet.py](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm5/benchmarks/expertlongbench/study8/arm5_sheet.py:12) documents the old seed although its executable constant is correct.

### Confirmed

- Preregistration commit preceded the plan by 20.37 seconds and the first archived model event by 24.33 seconds.
- 51 attempt records: 50 analysed drafts and one zero-spend errored attempt; the error is excluded and the successful retry included.
- Primary denominator is exactly `394 PASS + 4 C-labelled BLOCK = 398`; three N blocks and all 45 ADVISORY rows are excluded.
- Seeded 50-pass draw reconstructs exactly. Both blinded sheets have verdict-free schemas. L1/L2 labels agree 57/57, κ = 1.000; eight rule-code differences are accurately recorded.
- The seven underlying block shapes and labels were verified without re-labelling. The unit-shortening and `adjudicator_b` explanations match the archived records.
- Cost, re-ask count, row counts, strata counts, and 50/50 manifest agreement reproduce.
- Archive `MANIFEST.sha256` verifies.
- Kernel directories and all `src/`/`tests/` files are unchanged; `number_source` remains outside every named profile.
- Pytest collected 3,931 tests but could not complete collection in the enforced read-only environment because no writable temporary directory exists. No files were modified.

**not quotable.** The single most important reason is that the supposedly corpus-free results file directly commits exact licensed corpus fragments—the same blocking defect that rejected Arm 4’s first review.
