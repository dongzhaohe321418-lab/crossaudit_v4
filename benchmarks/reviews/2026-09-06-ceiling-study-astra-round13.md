# Independent cross-vendor review of the ceiling study, round 13 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over `study/ceiling` at 483e4a1. Regeneration and splice leave the
report byte-identical; 29 report tests and 22 statistics tests pass by the
reviewer's own run; every round-12 attack is red or disclosed. Verdict:
**no** on two overclaims: the coverage test's docstring says "every coverage
figure the report prints" while the prose scan reads only three-decimal
figures in sentences containing the letters `cover`, so a coverage described
in other words ("contains the true parameter in 0.123 of repetitions") is not
read; and the generator's own module docstring is stale ("every number",
"every interval resamples problem clusters", the exact-conditional interval
presented as current). Round 14 states the literal trigger in the test and
the report and rewrites the generator's docstring. Verbatim below; paths
shortened to the repository root.

---

## Verdict: no
Two overclaims remain.
1. The coverage scanner still promises more than it enforces. [test_report_consistency.py:1357](benchmarks/code/tests/test_report_consistency.py:1357) says “Every coverage figure the report prints equals…”, while the implementation only examines unsigned three-decimal tokens in sentences containing the literal substring `cover` ([line 1420](benchmarks/code/tests/test_report_consistency.py:1420)). Adding:
> The exact grid contains the true parameter in 0.123 of repetitions.
leaves all 29 report tests green. The corresponding report descriptions still say “a figure in a sentence” and “a sentence about coverage” at [R163](benchmarks/code/RESULTS-CEILING.md:163) and [R991](benchmarks/code/RESULTS-CEILING.md:991), without disclosing the literal-`cover` trigger. This is the round-12 coverage-synonym attack, still surviving.
2. The generator’s module contract remains stale. [report_ceiling.py:1](benchmarks/code/report_ceiling.py:1) still claims to regenerate “every number” in the report; lines 11–13 say every interval resamples problem clusters, despite generated Tango, exact-unconditional, and Wilson intervals; lines 25–27 still present an exact-conditional interval as current. These evade the seven-word guarantee list.
Everything else requested checks out:
- Clean `483e4a1`; `src/` diffs against both bases are empty; deviations are exactly 1–39.
- Intercepted regeneration attempted exactly two writes. Both were byte-identical:
  - `numbers.json`: `412534c7222569ed736cdcb84019a0ff1efdb01273ec2e555312b515463d8ee0`
  - `tables.md`: `d1bf2a7d501e1ab0d7cdfb3dc34f8ee3e92cc7678a199299d46ba345948649d4`
  - `coverage.json`: `92d115a1803c21980c74d7153cfa9632d854687742b090add08f180d710984d5`
- All 11 tables spliced; none missing; report remained byte-identical at `d211dbdd…`.
- Post-splice report suite: 29/29 passed.
- Statistics: 22/22 passed in 1182.08s by direct runner; `pytest` is unavailable on this host. All 11 coverage values were remeasured against the artifact.
- Hand-edited table and absent-table attacks are red.
- Tuple-target duplication is red; 28 modules are walked; reverting to an eight-file inventory makes the inventory test red.
- `Bin(112,0.1)` is red. `Bin(112, 0.10)` is green, correctly: it is numerically the same `(n,q)` pair.
- Underscore and footnote attacks are red. HTML entities, zero-width characters, and HTML tags remain green as disclosed; that limitation is acceptable for an explicitly source-lexical lint.
- All 11 `ALLOWED_SENTENCES` are live, contextually accurate, and are denials, qualified descriptions, or audit history—not bare assertions.
- The six declarations, R926/R933 corrections, round-11 false-pass row, R3, and R5 are accurate.
The six `[PENDING: ceiling r4]` placeholders must remain pending.
**no — the coverage contract still says it covers every coverage sentence, while the unchanged round-12 synonym attack passes the entire report suite.**
