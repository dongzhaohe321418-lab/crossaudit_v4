<!-- verbatim: codex exec -m gpt-6-astra, read-only, on feat/provenance-slice-8 at 98d0269; archived unedited -->

## Findings

1. **High — the claimed §3 preregistered kill did not fire.** Section 3 limits the kill to the gold or the committed §5 panel. The failing `5 g–10 mL` row is not in that panel; §5 instead contains the reversed `5 mL–10 g` case and preregisters its wrong block as acceptable. Gold and every actual panel row passed. The regression still correctly prevents shipping under backward compatibility and §7’s green-suite requirement, but [RESULTS.md:20](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov8/benchmarks/expertlongbench/study14/RESULTS.md:20>) incorrectly calls it the preregistration’s §3 kill, and lines 53–54 incorrectly say the committed panel found it.

2. **Medium — `1a817b6` was not exactly the preregistered rule.** The guard was supposed to strip “trailing punctuation” ([PREREGISTRATION.md:31](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov8/benchmarks/expertlongbench/study14/PREREGISTRATION.md:31>)), but `_TOKEN_END` omitted typographic quotes and `»`. Executing `1a817b6` in memory showed:

   - `5 min–10 min.` → `(5, min)` passes.
   - `5 min–10 min”` and `5 min–10 min»` → `(5, min)` wrongly block.

   Therefore [RESULTS.md:3](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov8/benchmarks/expertlongbench/study14/RESULTS.md:3>) overstates “implemented exactly as written.”

3. **Medium — the retained measurement script is stale at HEAD.** [measure.py:2](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-prov8/benchmarks/expertlongbench/study14/measure.py:2>) still describes a shipped-vs-ablated M10 comparison, but the reverted scanner never calls the monkeypatched hook. At HEAD, both configurations report Arm 4 as `0 of 2`; the historical `2 of 2` reproduces only after loading `1a817b6`’s matcher in memory. The script should explicitly identify or load the historical measurement commit, or refuse this misleading HEAD invocation.

Other checks passed:

- Historical execution reproduced gold `R=W=R′=W′=0`, panel `2/97`, base `300/300`, and Arm 4 `2/2` versus base `0/2`.
- The archived two failures are exactly the `5 g–10 mL` regression and the stale disclosure phrase.
- `5 g–10 mL` fails while `mol L–1 min–1` passes under the measured rule.
- I found no rule permitted by the exact preregistration that holds both. Doing so requires widening the repeated-stem guard or adding a contextual exception, both outside §1.
- `7691827..HEAD` changes `src/` and `tests/` only by the contract wording, skill wording, and three disclosure rows; matcher behavior is reverted.
- The disclosed complete-unit forms block as promised, including byte-exact, ASCII-hyphen, U+2212, and superscript transcriptions.
- No corpus-prose match appeared in added lines; protected kernel directories are unchanged; `number_source` is in no profile; diff and worktree are clean.
- Read-only-compatible focused tests: `1187 passed, 30 deselected`; those 30 require writable temporary paths. The reported `4004 passed` full suite remains author-supplied.

**DO NOT MERGE — the single most important reason is that RESULTS presents a regression outside the preregistered panel as the preregistration’s §3 kill.**
