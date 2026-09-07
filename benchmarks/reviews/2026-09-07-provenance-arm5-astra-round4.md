<!-- verbatim: codex exec -m gpt-6-astra, read-only, on study/provenance-arm5 at b7e9564; archived unedited -->

Not quotable yet. One publication-blocking overclaim remains.

The revised rationale still calls T01 “unit-less” and says only T03 combines number density with unit-bearing quantities ([RESULTS-ARM5.md:18](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm5/benchmarks/expertlongbench/RESULTS-ARM5.md:18), [PREREGISTRATION-ARM5.md:167](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm5/benchmarks/expertlongbench/study8/PREREGISTRATION-ARM5.md:167)). The census contradicts that categorical wording: T01 has median 5,067.5 input numbers and 43/6,938 reference numbers with recognized units—0.6%, including 22 percentages. Shape, cost, and low unit density support deferring T01; “unit-less” and “only T03” do not.

Everything else checked out:

- Arm 4’s interval independently reproduces as **4.84–12.24%**.
- The stated T04, T06, T07, T08, and T11 census figures reproduce.
- Arm 5 remains **4/398 = 1.01%, Wilson 0.39–2.56%, bootstrap 0.24–1.97%, PASS**.
- Strata, matcher movement, annotation intervals, records, blinded-sheet digests, and the 57/57 agreement reproduce.
- All **3,499** archive checksums verify.
- No source-specific corpus fragments were found in post-base additions.
- `src/`, `tests/`, and kernel directories are unchanged; `number_source` remains in no profile.
- Conflict retained: **L2 was `gpt-6-astra`; I did not re-label.**
- Pytest collected 3,931 tests but stopped on two collection-time temporary-directory errors imposed by the read-only environment. The direct verifier fixture script passed.
- No files were modified.

**not quotable** — the census itself contradicts the amended categorical claim that T01 is unit-less and that only T03 is both number-dense and unit-bearing.
