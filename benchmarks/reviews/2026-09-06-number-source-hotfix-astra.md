# Independent cross-vendor review of `fix/number-source-not-default` — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over f6e6621 against 274174f. Verdict:
**do not merge yet** on one D64 item — a test docstring claims a mutation
(restore `PROFILES["science"]` only) that does not redden it, because console
creation reads `scaffold.SCIENCE_CHECKS`. Every behaviour verified: profiles
equal their pre-D157 lists exactly; the `uncited` reorder implements section
3.4 correctly with 720 non-uncited cases identical before/after and 3,015
uncited cases advisory; scaffold and prompt logic correct; `src/` diff exactly
three files. Verbatim below, paths shortened.

---

The behavior changes look correct, but I found a test-evidence overclaim that should be corrected before merge. No files were modified.
1. **Profiles and scope verified.** Before: science and research each included `number_source`. After:
   - Science: `schema, units, convergence, provenance`
   - Research: `parseable, declared, internal, complete, source_provenance`
   All profiles exactly equal their `19bd161` lists. `SCIENCE_CHECKS` matches science; `available()` includes `number_source`; `resolve(["schema", "number_source"])` returns both. README line 1039 matches. The source diff contains exactly the three specified files, with no scanner, matcher, skill-template, generator, or addressing change.
2. **Row behavior verified by execution.** Previously, address/empty-value and numeric-value blockers preceded `uncited`. Now `uncited` precedes both; `_at_span` still runs first to supply diagnostic information. The four-field/type gate remains first.
   | Four-line draft probe | Result |
   |---|---|
   | `uncited`, `at: "#L999"` | CA-NUM-003 ADVISORY, names the invalid address |
   | `uncited`, `v: ""` | ADVISORY, “transcribes no number” |
   | `uncited`, `v: "about 950"` | ADVISORY, “not a number” |
   | Real source, `at: "#L999"` | CA-NUM-001 BLOCKER |
   | Missing `src` | CA-NUM-001 BLOCKER |
   I agree the value change implements §3.4 correctly for rows passing the structural gate: declining a source produces an advisory, with malformed content still visible. Additionally, 720 non-`uncited` cases produced identical before/after findings; 3,015 `uncited` cases were advisory.
3. **Scaffold/prompt logic verified, filesystem integration not executed.** Actual skill-tree selection and prompt rendering yielded no numbers skill, `crossaudit-numbers`, or `uncited` for default science. Explicit selection yielded `skills/provenance-numbers.md` and the instruction under HOUSE SKILLS. I traced `create_project` and `annotation_skills_owned`, but could not execute their filesystem writes in this read-only session.
4. **Mutation evidence needs correction.** Moving the original combined address/empty-value guard above `uncited` reddened both named tests. Moving only an address blocker reddened only `test_an_uncited_row_is_advisory_whatever_its_own_address_says`.
   More concretely, [the fresh-scaffold test’s docstring](tests/test_number_source_check.py:771) claims restoring only `PROFILES["science"]` makes its assertions fail. That is false: console creation uses the independent `SCIENCE_CHECKS` list. An in-memory profile-only mutation left that list and its empty skill tree unchanged. The claimed nine failures remain unverified; exact mutation scope and failing node IDs are needed.
5. **Suite claim remains author-reported.** Commit `f6e6621` records **3275 passed / 8 skipped**. This checkout lacks `.venv`, and available Python installations lack pytest. Six relevant test bodies passed directly, but that is not a suite run. The second-host run remains required.
**Do not merge yet — the mutation evidence overclaims what the tests detect, contrary to AGENTS.md §3.5.**
