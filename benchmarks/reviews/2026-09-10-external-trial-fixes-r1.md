Found two blocking issues in `431db67`:

1. **P1 — Repair can silently change another vendor’s temperature for an unrelated restriction.** In [openai_compat.py:52](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-trial/src/crossaudit/providers/openai_compat.py:52), the matcher associates any occurrence of “temperature” with any “only N is allowed” in the denial. Through the DeepSeek provider path, a mocked HTTP 400 containing `temperature must be between 0 and 2; n: only 1 is allowed` caused a retry changing temperature **0 → 1.0**. Bind the required value specifically to the temperature restriction and add negative regression cases.

2. **P1 — The GBK setup fix is incomplete.** `tui.ok()` now succeeds with a strict GBK stream, but the subsequent text prompt still emits an unguarded ❯ at [tui.py:322](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-trial/src/crossaudit/cli/tui.py:322). Executing `tui.text()` with terminal-like stdin and strict GBK stdout raises `UnicodeEncodeError`. This is a remaining pre-existing failure in the reported setup flow.

Verification:

- All three reported Moonshot model IDs send **1.0**, including to the China endpoint, using mocked transport.
- China passes `source_independent` and the receipt’s configured/runtime source-attestation gate.
- CLI region forwarding and Chinese denial translation work. Simulated China selection produces the expected config.
- Captured default/global config output is byte-identical to the base and contains no `base_url` line.
- Only `src/` and `tests/` changed; listed kernel directories are untouched. Worktree remains clean.
- Seven focused test functions passed when invoked directly in memory. Reverting registry temperature, repair logic, `ok()`, or region resolution made their corresponding tests fail.
- Coverage remains incomplete: the GBK mock is a non-encoding `StringIO`; `test_init_accepts_the_region_flag` calls `wizard.run()` directly, so removing CLI forwarding would escape that test.

The requested full suite failed **before collection** because the read-only sandbox cannot create pytest temporary files. I could not independently confirm the author’s **4017 passed** or perform a native Windows walkthrough.

**DO NOT MERGE — the new repair matcher silently changes another vendor’s temperature without a temperature-specific mandate from the origin.**
