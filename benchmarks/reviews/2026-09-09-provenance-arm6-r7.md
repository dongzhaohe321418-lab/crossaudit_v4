## Seventh-review verdict

The four round-6 corrections are satisfactory, but the record is still not quotable. A full sweep found additional unsupported statements.

### Remaining findings

1. **Blocking — Q2’s six “rendering” rows are not six typography-only cases.**  
   [RESULTS §2](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:99>) says six quotations “differ only” in typographic quotation marks or apostrophes. The classifier normalizes typography **and joins whitespace across the entire file**. Independently separating those operations shows:

   - 6/21 satisfy the implemented “rendering” predicate.
   - Only 1/6 becomes contained within a single source line after typography normalization.
   - The other 5/6 match only after line breaks are also joined.

   Therefore the typography-only description is false. The related claims that all six are fixable by a quotation-character fold in [RESULTS §4](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:166>) and [D166 ruling 3](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7648>) also exceed the evidence.

2. **Major — Q2’s six prefix matches are not established as “elisions.”**  
   [RESULTS §2](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:99>) calls them elisions. The executable predicate proves only that the whitespace-folded first 40 characters occur and the complete quotation does not. None of the six contains an ellipsis marker, and the predicate does not distinguish omission from replacement, paraphrase, or another later divergence. “40-character-prefix match” is the supported label.

3. **Major — the sentence-ending predicate is promoted into a semantic conclusion.**  
   [RESULTS §1](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:76>) and [D166](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7630>) conclude that the generator was not simply quoting sentences. The instrument establishes only that 12/40 strings end in `.`, `?`, or `!` after limited stripping. It does not determine sentence boundaries or whether punctuation was omitted. The safe statement is the measured terminal-punctuation count alone.

4. **Major — the empty-unit census is incomplete.**  
   [RESULTS §3](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:125>) says the 49 remaining rows are empty-unit dates, counts, and identifiers. In the archive, at least 13 empty-unit rows have a currency sign directly before the transcribed value. They are dollar amounts under the report’s own shape logic, so the stated exhaustive classification is false.

5. **Major — the stated cause of `adjudicator_b`’s seven misses is partly false.**  
   [RESULTS §3](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:148>) attributes the misses to thousands commas and a currency sign. All seven failures disappear when commas are removed. Only two have `$`, and that sign is present in the text and does not cause this exact-substring adjudicator to fail. The supported cause is thousands separators.

6. **Reporting defect — the new first-paragraph fence rate lacks its intervals.**  
   [RESULTS opening paragraph](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:14>) now correctly places the annotation rate first, but also quotes 11/33 without its Wilson and clustered-bootstrap intervals. This contradicts the same paragraph’s “every rate” statement and EXPERIMENT_RECORD §9. The missing intervals are 19.75–50.39% and 18.18–48.48%.

### The four requested rewrites

All four round-6 issues themselves are corrected:

- The generator sequence is now explicitly limited to call counts and described as consistent with, not proof of, D165’s path.
- The nine Q2 residual rows are accurately described as failing the 40-character-prefix test, with several possible explanations left unresolved.
- D166’s close now says association, not causal sensitivity; the future slice’s outcome is left open.
- The annotation rate is physically in the first paragraph, satisfying Amendment 1.

### Reproduced

- Preregistration precedes the first recorded start by 1.175 seconds. Amendments 1–2 precede attempt 2; Amendments 3–4 precede resumption.
- Outages reproduce: initial positions 3 and 8–14; 11 records over 10 instances; one initial SSL failure, seven credit failures, three later SSL failures; partial instance 15 retained; all affected instances completed.
- The report regenerates byte-for-byte: 33 drafts, 91 rows, 66 blocks, 14 passes, 11 advisory.
- Independent intervals reproduce for §8g 3/17, H6b 40/87, annotation 91/2,630, fence 11/33, unit-bearing 42/91, pair-elsewhere rates, and every value-shape rate.
- Matcher comparison remains 5 blocks/14 passes under both matchers and both readings.
- The sheet reconstructs exactly: 19 verdict-free items, five located blocks plus every one of the 14 passes; sheet text equals the archived quotation; κ = 1.000.
- All three M13 rows and the seven-line-away M1b row reproduce.
- Costs reproduce: $13.4095 counted, $9.2310 generator, $4.1785 auditor, $0.3440 outages; 101 generator calls, three at 4,096 output tokens.
- All 33 `file_read` hashes match complete, untruncated source results.
- Archive integrity and reconstructed rows/manifests pass. Fresh ten-word and 80-character scans found no corpus overlap in added lines.
- `src/`, `tests/`, kernel areas, profiles, and the `number_source` blob are unchanged from `bd491d5`.
- Full pytest still cannot initialize because the enforced read-only environment has no writable temporary directory; selected Arm 6/verifier tests collect successfully.
- Worktree remained clean; no file was modified.

**not quotable — the single most important reason is that the six Q2 rows presented as typography-only rendering failures are not: five require cross-line joining, so both the mechanism claim and its proposed fold exceed what the archive demonstrates.**
