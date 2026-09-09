# Probe — the eight escalated Arm 6 instances, re-run under `fix/envelope-re-ask`

2026-09-07, `wt-arm6-runs/probe-envelope-fix/` (archive), the eight instances of
`ATTEMPT-1.md` re-run with the runner's retry flag from the fix's tree (066a7a1 + the Arm 6
commits). Counts only; nothing quotes the corpus or a draft.

| | attempt 1 (d8d5210) | under the fix (066a7a1) |
|---|---|---|
| instances completing round 1 with a deliverable | **0 of 8** | **8 of 8** |
| generator calls per instance | 2, 2, 2, 2, 2, 2, 2, 2 | 3, 3, 3, 3, 4, 4, 3, 3 |
| spend | $0.365 | $3.351 ($0.42 per draft) |
| loop status | ESCALATED ×8 (3 `generator_format`, 5 `answered` — one root cause, two labels) | 8 receipts |

The three-call shape is the mechanism the fix addresses: a narrated tool request (format
failure), the re-ask that now restates the TOOL envelope, the clean tool request, then the
continuation that writes the summary — read from the ledgers' generator-role call counts.
Two instances took four calls: in both, the third call — the continuation that writes
the summary — returned exactly 4,096 output tokens, the generator's output ceiling, and a
fourth call followed under a re-ask. The archive keeps token counts and not reply text, so
the parser message of that third reply is not recoverable; a reply cut at the ceiling that
no longer parses is the inference, and an output ceiling of 4,096 tokens on a task whose
deliverable is a long summary plus an annotation fence is a second shape to watch in Arm 6.

**What the eight drafts then show, as a preview of Arm 6 and not as its result** (the arm's
own preregistration governs; these eight are not a sample): 3 of 8 drafts carry the
annotation fence at all; those three hold 9 annotation rows against 503 numbers present in
the eight drafts (1.8%; Arm 5 on T03: 38.1%); of the 9 rows, 0 pass — 3 quotations cross a
line break (H6b's class), 3 are absent from the file as quoted, 1 is ambiguous (the quoted
run occurs on more than one line), 1 names a location without the pair, 1 is `uncited`.
Whether the skill is rendered on the continuation turn after a tool result is the next
product question and is checked before Arm 6 runs.
