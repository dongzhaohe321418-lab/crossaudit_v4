# Independent cross-vendor review of provenance slice 5, round 1 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over 856fa86. Verdict: **do not merge** — E1 read a spaced ASCII
hyphen as a range dash, so `10 - 5 °C` accepted `(10, °C)` through the fenced
interface where the base blocked it, and the gold holds no such shape;
three smaller points: the chain `1-2-3 °C` had semantics decided after the
preregistration while RESULTS said §5 listed it, the branch was implemented
first where the preregistration said "after", and `study11/measure.py`'s
docstring still named study 10. Everything else reproduced: both gold
configurations to the row, the frozen base 300/300 with 152 passes, the
quotation-interval behaviour, the attack list, scope, 63 targeted tests.
Round 2 refuses a spaced ASCII hyphen (an en or em dash reads spaced or
not; an ASCII hyphen only glued), discloses the false block that buys, and
adds Amendment 1 to the preregistration for the chain and the branch order.
Verbatim below; paths shortened to the repository root.

---

Do not merge.
The single most important reason: E1 introduces a new false PASS for subtraction. Through the real fenced interface, source and quote `10 - 5 °C` accepts `(10, °C)` with no finding; the base correctly blocks it. `_RANGE_TAIL` cannot distinguish the accepted spaced-hyphen “range” from subtraction ([numbers.py](<src/crossaudit/dcl/numbers.py:294>)). This shape is absent from the gold, so reported `W = 0` does not cover it.
Additional findings:
- `1-2-3 °C` has inconsistent, post-preregistered semantics: `(1, °C)` blocks while `(2, °C)` passes ([test](<tests/test_number_source_check.py:2085>)). A three-number chain was not listed in preregistration §5, but RESULTS later says it was and cites §5 ([RESULTS.md](<benchmarks/expertlongbench/study11/RESULTS.md:25>)).
- Preregistration specified the branch “after” existing readings, while implementation and RESULTS say it is taken first. The deviation is not disclosed.
- `measure.py`’s docstring and example command incorrectly refer to `study10`, although the executable code correctly uses study 11’s baseline ([measure.py](<benchmarks/expertlongbench/study11/measure.py:5>)).
Verified successfully:
- Base: `R/W/R′/W′ = 0/0/0/0`, 10/10 right blocks, panel 2/97, frozen baseline 300/300.
- Shipped: `14/0/0/0`, exactly the fourteen named M2 rows, 10/10, panel 2/97.
- Independently loaded `numbers.py` from `a4fdfa5`: frozen baseline matches 300/300 and has 152 passes.
- Quote boundaries behave correctly: quoting only `775–850` blocks `(775, °C)`; quoting only `850 °C` accepts `(850, °C)` and blocks `(775, °C)`.
- Other probes behaved as claimed: `%`, brackets, glued ASCII range and exponent endpoint pass; unit prefix, different-unit borrowing, dates/pages with invented units, ratio, U+2212 negative-number form, and the first item of the dash chain block.
- Targeted E1/E5/E6 and mutation-guard tests: 63 passed.
- Only the two expected `src/` files changed; kernel directories and frozen study files are untouched; `number_source` is in no profile; `git diff --check` is clean.
- Preregistration commit `fcf2c20` contains only the preregistration and baseline, predating the implementation commit.
I could not independently rerun the full suite: this read-only environment provides no writable temporary directory, so pytest’s autouse `tmp_path` fixture produced 1044 setup errors. The branch remained unmodified.
