# Independent cross-vendor review of provenance slice 6, round 2 — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over 4c04e9c. Verdict: **do not merge** on one P1: the skill
guidance the commit claimed was not in the template (the patch that carried
it had failed silently behind an earlier assertion), so the shipped skill
still said "a labelled number" with no comma rule, no plurals and no
statement that the labels are a finite list; the reviewer's extra words
(`Appendices`, `Formulae`, `Supplement`, `Trial #5`) distributed. A record
defect: "25 rows" where `E2_ROWS` had 47. Everything else verified: base
300/300, R 5 on the five rows, every label and comma probe, E1 fail-closed
under the guard, the mutation now red on `(5, ×)`, scope five files. Round 3
writes the skill sentence, adds the four labels and the `#`, binds the comma
and finite-list phrases as rows, and corrects the count. Verbatim below;
paths shortened to the repository root.

---

## Second-review verdict: do not merge
### P1 — the claimed skill update is absent
The generated `provenance-numbers` skill was unchanged since `4a70b83`. Its list guidance still says only that “a labelled number” is excluded; it does not disclose:
- that commas require following whitespace;
- the plural/stem behavior;
- that label recognition is a finite allowlist.
See [PROVENANCE_NUMBERS_SKILL.md:69](<src/crossaudit/scaffold/templates/PROVENANCE_NUMBERS_SKILL.md:69>). The rendered skill lacks `a comma needs a space after it`, `Figs. 5`, `Step: 5`, and any plural/finite-list caveat. The disclosure test still checks only the generic phrase and one `Step 5` example at [test_number_source_check.py:2332](<tests/test_number_source_check.py:2332>).
That generic wording overpromises actual behavior: `Appendices 5, 10 °C`, `Formulae 5, 10 °C`, `Supplement 5, 10 °C`, and `Trial #5, 10 °C` still distribute. A finite list is acceptable if disclosed; the shipped generator guidance currently hides that limit.
### Other results
- `measure.py --config base`: **0/0/0/0**, 10/10, panel 2/97, **300/300**.
- Independently loaded `e890dfe` matcher: **300/300**, 166 passes; matcher blob matches.
- `--config shipped`: **R=5, W=0, R′=0, W′=0**, exact five claimed rows, 10/10, panel 2/97.
- All 47 current `E2_ROWS` and 53 existing disclosure rows pass when executed directly.
- Requested labels block first-number unit distribution: `Experiment`, `Fig`, `Tab.`, `Eqn.`, `Reaction`, `Compound`, `Sample no.`, uppercase `STEP`, and `Step-`.
- `Heat 5, 10 mL` distributes as disclosed.
- E1 behavior is correct and appropriately fail-closed: `(5, °C)` blocks for `Step 5–10 °C` and passes for `at 5–10 °C`.
- Commas behave as claimed: `5,10` blocks; `5 , 10` and `5,\t10` pass; `5,000, 10,000 rpm` passes. A cross-line comma blocks through both direct matching and the fenced interface.
- The named refused-notation mutant makes `(5, ×)` pass while leaving `(5, Pa)` blocked, so the new assertion genuinely turns red.
- Scope since `4a70b83` is exactly five files: `numbers.py`, its test, two study records, and the archived round-one review. No hidden production surface changed; `git diff --check` is clean.
- Record defect: RESULTS still says “Tests: 25 rows” at [RESULTS.md:68](<benchmarks/expertlongbench/study12/RESULTS.md:68>), while `E2_ROWS` now contains 47.
- I could not independently rerun the reported 1,104-test file or full suite: this worktree has no `.venv`, and system Python has no pytest.
**DO NOT MERGE — the single most important reason is that the shipped skill did not receive the claimed comma/plural/finite-list guidance and therefore promises broader label handling than the matcher implements.**
