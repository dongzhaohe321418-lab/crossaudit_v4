# Independent cross-vendor review of the ceiling study, round 8 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over `study/ceiling` at b887bb8. Numbers
byte-identical to round 7; seed status derived and overriding a hand edit;
zero duplicates; 37 tests. Verdict: **yes with corrections** — the family
binding is still example-driven (loop nets omitted from subject requirements;
asymptote rules accept generic words), the AST duplicate check is not a
committed test, and the attribution summary miscounts an expanded table.
Round 9 requires generated re-attribution mutations over every binding.
Verbatim below.

---

**The numbers reproduce unchanged, but two corrections remain.** Reviewed `b887bb8` against merge base `19bd1615c3d35381c37525721b6d38c5831b1ee5`, with all seven prior reports read. No files modified, network used, or detector readings adjudicated.
1. **The family-binding guarantee remains false.** The [subject requirements](benchmarks/code/tests/test_report_consistency.py:465) omit loop nets; the asymptote requirements accept generic words without naming a family.
   | In-memory mutation | Result |
   |---|---|
   | Round-7 re-attribution | **Red**, including the exact message `missing ['astra\|frontier']` |
   | `Self-audit changed accuracy by +0.89` → `Cross-loop changed accuracy by +0.89` | **All 16 report tests green** |
   | `Its fitted asymptote is` → `Its fitted curve provides a comparison. The self model's fitted asymptote is` | **All 16 report tests green**, falsely attributing `31.5% [21.7, 45.6]` to self |
   | Add “The shipped auditor's one-reading recall starts from 10.7% [5.1, 17.4].” | Value, interval, and family checks pass; **uniqueness alone fails**, as documented |
   Re-attributing the conclusion’s self-loop net to cross-loop also leaves all 16 green. Preserve these counterexamples and require actual family/arm identification for the affected bindings.
2. **Attribution is corrected, but its new summary miscounts the expanded table.** [CORRECTIONS.md](benchmarks/CORRECTIONS.md:521) now correctly credits the beta-tail defect to the author and narrows the former “every defect” claim. However, the table now contains **ten findings: eight reviewer discoveries and two author discoveries**, while the following sentence says nine and “the single exception.” Say **eight of nine numbered items, plus the author-discovered beta-tail**, or eight of ten listed findings. The report’s “eight of the nine” correctly describes the original numbered set.
The remaining checks pass:
- **Hashes equal round 7**, with empty artifact diffs against `6073d0d`:
  ```text
  numbers.json 412534c7222569ed736cdcb84019a0ff1efdb01273ec2e555312b515463d8ee0
  tables.md    c5e939aac38fc238767dfb918f8cc10b026c9231f59329f7911e5a300c6f7e2e
  ```
- **Seed status is derived.** Both manifests match the instrument: **34 distinct seeds, 205 constructions**. `+1` and `+7` are consumed; the absent set is exactly **{+2, +14, +15}**, with reasons. Hand-marking `+7` unconsumed—even adding a false prose reason—is overwritten by derivation.
- **Zero duplicate definitions** across all four checked files, and every other Python file changed on the branch. Duplicating a function turns the review-time AST check **red**. **No AST regression check is committed**; duplicating `_pairs` leaves the committed report suite green.
- **All 37 distinct tests passed: 21 statistics + 16 report**, directly invoked under Python 3.13.5 because pytest is unavailable. Application and hidden suites were not rerun.
- Regeneration returned zero with credential-like variables unset, sockets disabled, bytecode disabled, and writes intercepted in memory; both artifacts reproduced byte-for-byte.
- Deviations are exactly **1–33**; all **99 generated table lines** occur in the report; `src/` diff and branch-only history are empty.
**May these numbers be quoted in a paper — yes with corrections, because the claimed family-aware verification still accepts false attribution of a rate and its interval.**
