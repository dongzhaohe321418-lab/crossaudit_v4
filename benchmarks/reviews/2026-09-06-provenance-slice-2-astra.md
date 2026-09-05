# Independent cross-vendor review of provenance slice 2 (contract B) — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over b99ea47 against 1880d75. Verdict:
**do not merge.** P1: the quote is matched in isolation, so cropping a quote
bypasses every boundary rule the matcher enforces on a whole line (`5 mg`
from `5 mg/mL`, `5 g` from `-5 g`, `3` from `30 °C`; a 1–100 sign-cropping
sweep gives 100/100 false passes) — the prefix defect reborn through the
addressing mechanism. P2: `_UNPARSED`'s whitespace allowance turns a
separated superscript footnote into a continuation (false blocker) and can
cross a newline; the narrowing was not measured against the gold as the
containment note requires. Everything else built for addressing holds and
all six mutations discriminate. Verbatim below, paths shortened.

---

**Do not merge.** Reviewed `b99ea47` against `1880d75`, read-only. The principal defect is that quote cropping reintroduces numeric-prefix and unit-prefix false passes that earlier reviews eliminated.
1. **P1 — quoting a substring bypasses the matcher’s source boundaries.** [_quote_span](src/crossaudit/dcl/numbers.py:456) returns the isolated quote; [the containment check](src/crossaudit/dcl/numbers.py:659) therefore cannot see adjoining signs, digits, exponents or unit continuations.
   | Source line | Quote | Annotation | Base line citation | Head quote citation |
   |---|---|---|---|---|
   | `5 mg/mL` | `5 mg` | `5 / mg` | BLOCKER | **PASS** |
   | `5 m-2s-1` | `5 m` | `5 / m` | BLOCKER | **PASS** |
   | `-5 g` | `5 g` | `5 / g` | BLOCKER | **PASS** |
   | `1e+5 g` | `5 g` | `5 / g` | BLOCKER | **PASS** |
   | `30 °C` | `3` | `3 / ""` | BLOCKER | **PASS** |
   A contiguous sign-cropping sweep, `-1 g` through `-100 g`, produced **100/100 incorrect PASS results**. The unchanged matcher rejects all 100 original lines. Quoting only `3` also bypasses the new protection against `3 × 10⁻² mbar`.
   Resolution must retain the quote’s position and original token context while requiring the matched pair to lie inside the quoted interval. Checking elsewhere on the line would introduce another bypass. The design’s assertion that “every property the span rule bought stays bought” is disproved.
2. **P2 — `_UNPARSED` adds a footnote false blocker.** At [numbers.py:235](src/crossaudit/dcl/numbers.py:235), the whitespace allowance treats a separated superscript footnote as numeric continuation. `Participants: 5 ¹`, followed by `¹ Enrollment count; see trial log.`, changes from PASS to CA-NUM-002 for `5 / ""`. Reproduced through a complete-line quote and a structured citation. `\s*` can also cross a newline.
   The containment note explicitly requires this narrowing to go through the same gold because it can introduce false blockers. The commit’s assertion that it is exempt from that gold misreads the note.
The requested positive checks otherwise hold:
| Probe | Observed |
|---|---|
| **Actual archived** Arm 3 quotes: 97 characters (`aic.18378`), 104 (`smll.201800441`) | Both PASS |
| Quote crossing source lines; multiline whole-file quote | BLOCKER CA-NUM-002; observation says “across a line break” and “a quotation is a run of one line” |
| Quote absent through retyped word, case change or altered abbreviation | BLOCKER CA-NUM-002 |
| Located quote lacking the pair | BLOCKER CA-NUM-002 |
| Quote on two lines | ADVISORY CA-NUM-004, zero hard failures |
| Quote twice on one line | PASS |
| NBSP, narrow NBSP, doubled spaces, newline inside the quote | PASS; independently varied source-side whitespace too |
| Traversal, absolute and `./` aliases | Refused |
| Existing real symlink, absolute and relative names | Refused; reused an existing fixture without writing |
| Legacy `at`; `computed:` file prefix; valid/stale/malformed SHA pins | Expected dispositions |
| `results.json` locator implementation | Executable AST unchanged |
A whole-file quotation **can pass when the file itself has one line**; D159’s only size boundary permits that.
All requested mutation guards discriminated, with mutations applied only in memory:
| Mutation | Evidence |
|---|---|
| Restore 80-character cap | Both 97/104 tests red |
| Fold and search the whole file | One-line guard red; whole-file citation passes |
| Accept first occurrence | Ambiguity test red |
| Compare raw characters | Five whitespace cases red |
| Resolve through filesystem | Existing symlink refusal assertion red; citation passes |
| Validate `at` again | Four invalid/legacy cases red |
The requested `_UNPARSED` cases also matched expectations: both forms of `3×10⁻²` and spaced `5 x 10^3 g` block; `5 x 3 grid`, `5 * 3 items`, `run 5 of 12`, and correctly annotated `5 mbar` pass. Additional `5 x 10 cm` and `2 × 2 matrix` cases pass unchanged. `10^3` annotated as `10` blocks unchanged. Spaced `10 ^ 3` and `5 x 10e3` remain pre-existing false passes, outside the new branch’s coverage.
My assessment of the nine implementation decisions:
| Item | Assessment; documentation consequence |
|---|---|
| **-001 versus -002** | Defensible classification with unchanged severity, but “the quote is the span” does not uniquely require it. Correct the design pseudocode and mutation expectations. |
| **Per-line ambiguity** | Reasonable line-address refinement. Correct the design’s occurrence counting, D159’s “unique in the file” wording, and the skill’s “more than once” instruction. |
| **Absent versus across-line-break failures** | Right: different observations give different remedies. Document both as CA-NUM-002. |
| **Dead cap mutation** | Right replacement: restoring the cap must fail long-quote tests; whole-file folding must fail the line-bound test. Update the current design; retain the historical Arm 3 instrument as historical. |
| **Blank fence bodies in `_derive_at`** | Right; prevents self-location and preserves line numbering. Add this detail to the design. |
| **`computed:` prefixes `file`** | Right; resolution and containment still execute. Specify the object syntax in the design. |
| **Skill loses `results.json` sentence** | Wrong omission: that supported interface remains active. Restore clearly separated structured-source guidance; do not redefine the design to remove it. |
| **`_UNPARSED` change** | The scientific-notation repair works, but the footnote regression and omitted gold assessment prevent approval. Update the containment record with both. |
| **Delete `_AT`** | Right: no remaining fence-address consumer needs it; structured sources retain `_SPAN`. Correct compatibility wording: an old **`at` field** is accepted with new `src`; an unchanged old-format annotation is rejected. |
Test accounting:
- **492 focused pytest tests passed; 30 filesystem-dependent cases deselected**, using `--noconftest`, disabled cache and bytecode writes.
- Historical **45-row input table** matches this base’s dispositions on all 45 rows. One original historical expectation—accepting `1` from `1,000`—had already been corrected before this base.
- Both **1–100 signed-exponent interface sweeps**, the exponent-bound sweep, and the **39-row boundary table** passed.
- Reconstructed **216 helper mappings / 96 `check_declared` mappings**: zero differences, including ordering. These are reconstructed corpora, not claimed identical historical probe inputs.
- Arm 3 verifier fixtures pass. Independent AST duplicate-name scan across tests found none; `git diff --check` passes.
- Full-suite collection fails because no temporary directory is writable. **3309/4 at head, 3279/4 at base, and reference-host 3275/8 remain reported counts, not independently verified here.**
Every removed or renamed test function is accounted for:
| Former name | Disposition/reason |
|---|---|
| `test_a_fenced_locator_is_ascii_and_exact` | Replaced by rejection of string fence locators; structured fragment discipline retained |
| `test_the_at_locator_is_validated_the_way_the_src_locator_is` | Retired: `at` ignored |
| `test_the_at_locator_must_be_inside_the_artefact_that_carries_it` | Retired: `at` ignored |
| `test_a_span_range_and_a_pinned_sha_both_resolve` | Pin tests retained; multiline fence range retired |
| `test_an_uncited_row_is_advisory_whatever_its_own_address_says` | Renamed and expanded for ignored extra fields |
| `test_the_span_and_not_the_file_is_what_is_checked` | Replaced by quote-scoping mutation test |
No duplicate or dead test definitions were found. Two evidence descriptions need correction: the committed 97/104 fixtures are **synthetic length reproductions**, not the archived quotations, and `_span` still references the removed test name.
Only `dcl/numbers.py` changes among the named kernel directories; `auditor/`, `broker/`, `ledger/`, and `policy/` are unchanged. However, **the new false passes prevent a non-weakening sign-off**. `number_source` remains registered, in **no profile**, with `requires_check` and selection machinery unchanged. The diff also changes `docs/design/PROVENANCE_CHECKS.md`, outside the supplied `src/`/`tests/` scope restriction.
No files were modified, and the prohibited transcript was not read. `CONTAINMENT_RULE.md` was read from the neighboring containment worktree because it is absent here. **Arm 4 remains required before any profile activation.**
**Do not merge — the single most important reason is that cropping a quotation turns previously blocked incorrect numbers and shortened units into PASS.**
