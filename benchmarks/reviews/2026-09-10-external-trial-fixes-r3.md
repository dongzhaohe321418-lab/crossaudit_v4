No blocking code findings at `fcf8006`.

Verified independently:

- **184 DeepSeek negative probes**, including comma, parentheses, and semicolon bodies with contiguous **0–60-space sweeps**: no retry or temperature change. Positive temperature mandates still repair correctly.
- Interactive `select()` with rerendering, real `input()`, and banner subtitles pass strict GBK in English/Chinese, with ANSI on/off.
- All three Moonshot models send `1.0` to both endpoints.
- China attestation, custom-origin rejection, actual CLI region forwarding, Chinese denial translation, and byte-identical default/global config all pass.
- Fifteen focused test cases pass directly in memory; relevant mutation checks detect removed fixes. Audit-core directories are untouched; worktree is clean.

One evidence correction: **`│` is GBK-encodable**, so GBK cannot detect removal of its guard. Strict ASCII does: current banner passes; restoring the unguarded rule fails.

The full suite remains independently unverified: the read-only sandbox prevents temporary-file creation. The author’s log records **4025 passed, 4 skipped**. Native Windows, frozen-app, and light/dark walkthroughs were not performed.

**MERGE — the temperature-ownership blocker is resolved in every repeated DeepSeek transport probe.**
