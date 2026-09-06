# Independent cross-vendor review of the ceiling study, round 14 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over `study/ceiling` at d07cdb0. Artefacts byte-identical;
regeneration and splice leave the report unchanged; 29 report tests and 22
statistics tests pass by the reviewer's own run. Verdict: **no** on six
sentences: the coverage trigger is described as "a three-decimal figure"
where the scan reads only unbracketed, unsigned tokens of the literal form
`0.ddd` (so `[0.123, …]`, `+0.123` and `1.000` are not read); the generator's
docstring says Wilson coverage is measured (it is not), calls the grid
interval exact, calls every estimator preregistered (Tango and the grid
interval came by amendment 4), and says it reads only `records/` (Table 9
reads the archived run directory); and the version line still said twelfth.
Round 15 states the literal token form in all four places and rewrites the
four docstring sentences. Verbatim below; paths shortened to the repository
root.

---

## Verdict: no
The analysis artifacts are reproducible, but several descriptions still exceed the implementation.
1. The coverage-trigger description remains too broad.
   - [R163](<benchmarks/code/RESULTS-CEILING.md:163>) says “a three-decimal figure” is checked.
   - [The coverage-test opening sentence](<benchmarks/code/tests/test_report_consistency.py:1357>) omits the bracket exclusion.
   - [Deviation 38](<benchmarks/code/RESULTS-CEILING.md:991>) and the detailed test description say “unsigned three-decimal figure,” which still includes `1.000`.
   - [Deviation 24](<benchmarks/code/RESULTS-CEILING.md:816>) has the same broader “three-decimal figure” wording.
   The actual regex at [test_report_consistency.py:1430](<benchmarks/code/tests/test_report_consistency.py:1430>) reads only unbracketed, unsigned tokens of the literal form `0.ddd`. I reproduced:
   - Red: `Coverage is 0.123.`
   - Green: `Coverage is [0.123, 0.456].`
   - Green: `Coverage is +0.123.`
   - Green: `Coverage is 1.000.`
   - Green: `The exact grid contains the true parameter in 0.123 of repetitions.`
2. The generator docstring incorrectly says Wilson coverage is measured by `measure_coverage.py` at [report_ceiling.py:14](<benchmarks/code/report_ceiling.py:14>). Its method inventory has ideal bootstrap, Tango, exact grid, and withdrawn methods—but no Wilson coverage measurement.
3. The same docstring calls the Berger–Boos grid interval “exact” without the required grid-approximation qualification at [report_ceiling.py:31](<benchmarks/code/report_ceiling.py:31>), while the estimator itself says it is not a guaranteed exact interval at [report_ceiling.py:225](<benchmarks/code/report_ceiling.py:225>).
4. “The estimators, all preregistered” at [report_ceiling.py:17](<benchmarks/code/report_ceiling.py:17>) is false for Tango and the grid interval: Amendment 4 explicitly adopted them after the results were known.
5. “Reads only what is committed under `records/`” at [report_ceiling.py:3](<benchmarks/code/report_ceiling.py:3>) is false. Table 9 reads archived scoring records from the external `--run` directory at [report_ceiling.py:984](<benchmarks/code/report_ceiling.py:984>). The report’s reproduction command makes the same broad claim before subsequently disclosing the exception.
6. Separately, the report still says “Twelfth version” and twelve reviews at [RESULTS-CEILING.md:3](<benchmarks/code/RESULTS-CEILING.md:3>), despite incorporating round 13.
Verified successfully:
- HEAD `d07cdb0`; clean worktree.
- `src/` diff against `483e4a1`: empty.
- Deviations exactly 1–39.
- Artifacts byte-identical to `483e4a1`:
  - `numbers.json`: `412534c7222569ed736cdcb84019a0ff1efdb01273ec2e555312b515463d8ee0`
  - `tables.md`: `d1bf2a7d501e1ab0d7cdfb3dc34f8ee3e92cc7678a199299d46ba345948649d4`
  - `coverage.json`: `92d115a1803c21980c74d7153cfa9632d854687742b090add08f180d710984d5`
- Intercepted regeneration attempted exactly two writes; both hashes matched.
- All 11 tables spliced, none missing; report remained byte-identical (`093a2679…`).
- Report tests: 29/29 passed in 2.30s.
- Statistics: 22/22 passed in 1197.62s; all eleven coverage cells remeasured.
- No file modified.
The six `[PENDING: ceiling r4]` placeholders must remain pending.
**No — most importantly, the claimed literal coverage boundary still says “three-decimal figure,” while the implementation recognizes only unbracketed, unsigned `0.ddd` tokens.**
