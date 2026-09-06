# Independent cross-vendor review of provenance slice 5, round 3 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over 70f39d4. Verdict: **do not merge** on one sentence: RESULTS
called "a dash followed by a word" absent from the gold, while the gold
holds `2.54-cm diameter` twice (G0263, G0300 — the compound-adjective rows,
M4, gold C, blocked by contract before and after E1); the intended shape is a
dash followed by a space and then a word. Everything else verified: `src`
unchanged since 7db0947, both gold configurations to the row, the four
disclosure rows, Amendment 1's wording, the remaining "absent" shapes truly
absent. Round 4 corrects the sentence. Verbatim below; paths shortened to
the repository root.

---

One blocking overclaim remains.
[RESULTS.md:26](<benchmarks/expertlongbench/study11/RESULTS.md:26>) calls “a dash followed by a word” absent from the gold. The gold contains two such rows:
- G0263: `2.54-cm diameter`, `(2.54, cm)`, gold `C`
- G0300: the same shape and pair, gold `C`
Both are R9/M4 rows, base `False`, and shipped code still returns `False`. The gold report explicitly identifies them as the two hyphenated-compound-adjective wrong blocks. If the intended claim is only the preregistered “dash followed by a space then a letter” shape, RESULTS must retain that qualifier.
Everything else requested checks out:
- `git diff 7db0947..HEAD -- src` is empty.
- Metrics reproduce exactly: shipped `14/0/0/0`, base `0/0/0/0`, right blocks `10/10`, panel `2/97`.
- G0004/G0032 are spaced EN-dash ranges; G0214 is a base pass and remains a pass with E1 disabled.
- The other listed absent shapes were absent from the 300-row sheet.
- Exactly four E1 `DISCLOSED_LIMITS` rows exist and their phrase/behavior checks agree.
- Amendment 1 correctly describes one clarification and two deviations; no unsupported sentence remains there.
- No other overclaim was found in RESULTS.
**Do not merge — the single most important reason is that RESULTS still falsely declares the gold’s two `2.54-cm` dash-plus-word rows absent.**
