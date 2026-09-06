# Independent cross-vendor review of the ceiling study, round 15 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over `study/ceiling` at 645b237. All six round-14 corrections
verified; artefacts byte-identical; regeneration and splice leave the report
unchanged; 29 + 22 tests pass by the reviewer's own run. Verdict: **no** on
six further overclaims from a fresh sweep: the coverage test read six known
rows and ignored an appended one ("cell by cell" was false); two statistics
docstrings spoke of the report without reading it; the generator called its
saturation fit "exact, with no optimiser" and itself runnable "on partial
data"; `measure_coverage.py` said "every coverage figure". Round 16 parses
each coverage table whole and asserts its row set, and narrows the five
sentences. Verbatim below; paths shortened to the repository root.

---

## Verdict: no
All six round-14 corrections are present and accurate, but the broader promise-vs-enforcement sweep found additional overclaims.
### Verified
- Clean `study/ceiling` at `645b237d4a1468d8591445275973983b030ee25a`.
- Diff against `d07cdb0` touches only the report and docstrings in two Python files; the `src/` diff and entire records/artifacts diff are empty.
- Artifacts match `d07cdb0` byte-for-byte:
  - `numbers.json`: `412534c7222569ed736cdcb84019a0ff1efdb01273ec2e555312b515463d8ee0`
  - `tables.md`: `d1bf2a7d501e1ab0d7cdfb3dc34f8ee3e92cc7678a199299d46ba345948649d4`
  - `coverage.json`: `92d115a1803c21980c74d7153cfa9632d854687742b090add08f180d710984d5`
- Intercepted regeneration attempted exactly two writes; both matched the committed files. All 11 generated tables spliced, none missing, and the report remained byte-identical at `eb641dfc…`.
- Deviations are exactly 1–39.
- Fourteen review reports exist, and R3 correctly says “Fifteenth version” and “Fourteen independent cross-vendor reviews.”
- The scanner’s actual boundary matches the revised descriptions: bare `0.ddd` reddens; two decimals, `1.000`, words, a sign, brackets, and a sentence without `cover` remain green.
- The generator’s four targeted corrections are accurate: the Table 9 `--run` exception, Wilson/Tango/grid coverage status, amendment-4 provenance, and finite-grid qualification.
- Tests:
  - All 29 report assertions passed in 2.24s.
  - All 22 statistics assertions passed in 1227.15s.
  - `pytest` itself was unavailable in this workspace, so these were executed through direct equivalent function harnesses rather than reproducing the claimed runner commands literally.
- Final worktree remained clean.
### Remaining overclaims
1. [test_report_consistency.py:1356](benchmarks/code/tests/test_report_consistency.py:1356) and the corresponding claims at [RESULTS-CEILING.md:163](benchmarks/code/RESULTS-CEILING.md:163) and [RESULTS-CEILING.md:984](benchmarks/code/RESULTS-CEILING.md:984) say both coverage tables equal the artifact “cell by cell.” The check reads the first occurrence of six expected row prefixes but rejects neither extra nor duplicate rows. I appended an invented row containing false `0.123 / 0.456` coverage; all 29 report tests remained green.
2. [test_ceiling_stats.py:356](benchmarks/code/tests/test_ceiling_stats.py:356) says the report “must not reuse one number for the other” scenario, but that test never reads the report. Re-attributing the live `0.924` prose from beneficial to detrimental left all report tests green, consistent with the disclosed membership-only scanner.
3. [test_ceiling_stats.py:382](benchmarks/code/tests/test_ceiling_stats.py:382) claims endpoint rounding “is declared” and that the report states the `0.9895` alternative, but its body only checks one returned endpoint. Changing the report’s `0.9895` to `0.9999` left all 29 tests green. The genuine value is `0.989508639…`, so the prose is numerically right but not enforced.
4. [report_ceiling.py:26](benchmarks/code/report_ceiling.py:26) calls the saturation fit “exact, with no optimiser to tune.” The implementation uses a bounded log grid, tuning choices, and a 120-iteration golden-section numerical optimization. Its test checks three cases with tolerances; it is deterministic, not exact.
5. [report_ceiling.py:6](benchmarks/code/report_ceiling.py:6) promises operation on “partial data at any point” while reporting missing inputs. Required `study2/instances.jsonl` and `audit_set.json` are read unconditionally; a missing one raises `FileNotFoundError`.
6. [measure_coverage.py:1](benchmarks/code/ceiling/measure_coverage.py:1) and [measure_coverage.py:7](benchmarks/code/ceiling/measure_coverage.py:7) say the script measures “every coverage figure” and that prose is thereby bound. It emits eleven method/scenario cells; historical/simulation figures such as `0.933`, `0.897`, and the four-decimal `0.9895` are outside that artifact and not generally bound.
The six `[PENDING: ceiling r4]` placeholders must remain pending.
**No — most importantly, the coverage test still claims table equality while an additional false coverage row survives the entire report suite.**
