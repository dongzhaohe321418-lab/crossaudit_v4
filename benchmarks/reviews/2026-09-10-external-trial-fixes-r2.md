Two findings remain at `3feb784`:

1. **P1 — Repair still applies another field’s restriction to temperature.** The [matcher](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-trial/src/crossaudit/providers/openai_compat.py:47) rejects the exact round-one semicolon case, but this mocked DeepSeek HTTP 400 still triggers a successful retry changing **temperature `0 → 1.0`**:

   `temperature must be between 0 and 2, n: only 1 is allowed`

   Parentheses also reproduce it. Sweeping 0–60 spaces after the comma reproduces the incorrect repair at 0–12 spaces. The matcher limits proximity; it does not establish which field the mandate governs.

2. **P2 — “Every glyph” remains incomplete.** The original `tui.text()` probe now passes with real `input()`, terminal-like stdin, and strict GBK stdout. However, interactive `tui.select()` still raises `UnicodeEncodeError` on the [unguarded menu ❯](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-trial/src/crossaudit/cli/tui.py:232). Separately, an ASCII banner with a subtitle raises on its [unguarded │](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-trial/src/crossaudit/cli/tui.py:95). The new GBK test does not exercise the interactive menu.

Verified:

- Ten focused test functions passed directly in memory. Strict GBK tests now enforce encoding; the new CLI test executes `cmd_init` and detects removed forwarding.
- All three Moonshot model IDs send `1.0` to both global and China endpoints using mocked transport.
- China passes configured/runtime source-attestation checks; a custom runtime origin remains rejected.
- Actual argument parsing forwards `--auditor-region china`; Chinese denial translation works.
- Captured default/global config is byte-identical to the original base; flagged and simulated China selection produce identical regional config.
- Round-one mutation checks still detect removed fixes.
- Audit-core directories are untouched. Changes outside `src/` and `tests/` consist solely of the archived round-one review. Worktree remains clean.

The full suite failed before collection because the read-only sandbox cannot create temporary files. **4020 passed, 4 skipped remains author-reported**; native Windows, frozen-app, and light/dark walkthroughs were not performed.

**DO NOT MERGE — the repair matcher still silently changes another vendor’s temperature based on a restriction belonging to another field.**
