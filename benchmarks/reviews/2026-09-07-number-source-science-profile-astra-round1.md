<!-- verbatim: codex exec -m gpt-6-astra, read-only, on feat/number-source-science-profile at de65f30; archived unedited -->

DO NOT MERGE.

The single most important reason: the mutation evidence is falsely documented, violating AGENTS.md §3.5. The rewritten guard says removing `number_source` from either list makes that node fail, but a scaffold-only mutation left it green; the same docstring still describes the obsolete “put it back” mutation ([test_number_source_check.py](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-profile/tests/test_number_source_check.py:318>)).

Additional evidence defects:

- `science_with_numbers()` now returns the science profile directly, but its docstring still says the profile lacks the check and that the helper composes it by name ([test_number_source_check.py](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-profile/tests/test_number_source_check.py:92>)).
- The claimed sixth guard does not name D164 or its reverse mutation; it only says “Science users keep their path” ([test_constitution_moment.py](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-profile/tests/test_constitution_moment.py:306>)). The browser guard names D164 in a comment but likewise records no mutation.

Verified successfully:

- Both science lists are equal, with `number_source` last.
- The fresh-project equality assertion reddens under either one-sided list mutation.
- `general` remains unchanged and receives no numbers skill/fence; explicitly naming the check supplies both.
- `research` remains unchanged and receives only its sources skill.
- `number_source` remains registered and explicitly selectable.
- Science skill rendering includes the numbers fence and `uncited`.
- Source reasons agree with D164/RESULTS-ARM5: 4/398 and Wilson 0.39–2.56%; scaffold records 4/398 and points to the complete profile rationale.
- The shipped matcher blob is byte-identical to the base. Auditor, broker, ledger, policy, receipt, and controller trees are unchanged.
- Frozen-gold measurement reproduced `R=11, W=0, R′=0, W′=0`, 10/10 right blocks, and panel 2/97 with zero gold-wrong passes. The T03 probe also reproduced its recorded counts.
- No current product-facing template, wizard, console, or README text says science lacks the numbers check.
- 21 runnable focused tests passed with repository conftest disabled.

The full suite and disk-backed CLI/console creation walkthrough could not be independently run because this read-only sandbox has no writable temporary directory; pytest’s global fixture fails before test execution. No files were modified.
