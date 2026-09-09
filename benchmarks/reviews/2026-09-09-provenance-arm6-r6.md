## Sixth-review verdict

The numerical and provenance repairs reproduce, but the record is still not quotable because several sentences claim more than the archive demonstrates.

### Unsupported claims

1. **The exact generator-repair sequence is not archived.**  
   [RESULTS-ARM6.md:136](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:136>) asserts that all 33 drafts followed the narrated-tool → corrected re-ask → tool → continuation sequence and calls this D165’s mechanism “working.”

   The archive establishes 3 generator calls for 31 drafts, 4 for 2 drafts, and one successful `file_read` per draft. It does not retain provider reply text or retry reasons. Moreover, the report labels **any** draft with more than one generator-role call a “malformed-envelope re-ask”; that predicate cannot distinguish a normal tool/continuation cycle from a malformed-envelope retry. The harness collects event kinds only in memory and does not serialize them ([run.py:511](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/run.py:511>)). The defensible statement is that the call-count shape is consistent with the proposed mechanism, not that it proves the exact sequence or cause.

2. **Q2’s nine “not found” cases are semantically overclassified.**  
   [RESULTS-ARM6.md:96](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:96>) calls them “a paraphrase, or a different file.” The implemented test proves only that the normalized 40-character prefix was not found. It does not distinguish paraphrase, wrong file, an earlier divergence, or another transformation.

3. **D166’s closing causal summary exceeds its own uncertainty boundary.**  
   [DECISIONS.md:7664](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7664>) says the measurement “found the rule’s sensitivity to document shape.” The study did not isolate document shape from generator compliance; D166 correctly acknowledges that immediately above. It found association on this domain, not sensitivity attributable to shape.

   Similarly, [RESULTS-ARM6.md:153](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:153>) says a future joined-text failure would make the generator at fault. That attribution depends on the future preregistration, implementation, and gold adjudication and cannot yet be guaranteed.

4. **“Reported first” does not match Amendment 1 literally.**  
   Amendment 1 required the low annotation rate to be stated “in the first paragraph.” It first appears in §3, after the setup, attempt history, both dispositions, and adjudication. Therefore [RESULTS-ARM6.md:119](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/benchmarks/expertlongbench/RESULTS-ARM6.md:119>) and [DECISIONS.md:7652](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm6/docs/DECISIONS.md:7652>) should not say the requirement was met.

### What did reproduce

- The repaired §4 and D166 title now correctly say the rule went unmet on 40/87 and causation is unresolved.
- D166 now correctly says the redesign slice is **to be preregistered** and has no preregistration yet.
- `arm6_rates.py --run` reproduces:
  - Q1 punctuation: 12/40; bootstrap 0–60%, 5 discarded.
  - Q2: 6 rendering, 6 elision, 9 not found.
  - Rendering: bootstrap 0–100%, 128 discarded.
- Independent draft-clustered recomputation at seed 20261108 reproduced all reported Wilson and bootstrap intervals, including §8g, H6b, annotation, fence, unit-bearing, pair-elsewhere, and value-shape rates.
- The report JSON, matcher comparison, 19-item verdict-free sheet, all 14 passes, five mechanism rows, κ = 1.000, M13 rows, and the value-outside-quotation row reproduce.
- Preregistration/amendment chronology and outage handling reproduce; the original plan was not silently presented as preserved.
- Archive manifests and hashes verify; the reconstructed rows and manifest are exact.
- No corpus-fragment overlap was found in added committed lines. `src/` and `tests/` are untouched relative to `bd491d5`; `number_source` remains unchanged.
- I could not rerun the full pytest suite because the read-only environment provides no writable temporary directory; pytest failed before test execution. The worktree remains unchanged.

**not quotable — the single most important reason is that RESULTS presents the exact malformed-envelope repair sequence as observed fact even though the archive retains only call counts, not the reply text or retry-event evidence needed to establish that mechanism.**
