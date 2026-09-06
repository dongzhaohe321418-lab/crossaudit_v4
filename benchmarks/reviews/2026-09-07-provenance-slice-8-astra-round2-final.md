<!-- verbatim: codex exec -m gpt-6-astra, read-only, on feat/provenance-slice-8 at d8a0d99; archived unedited -->

All three round-one findings are resolved:

- `git diff 98d0269..HEAD -- src tests` is empty.
- RESULTS and Amendment 1 correctly attribute non-shipment to the shipped-contract regression and §7, acknowledge §5’s error, and disclose the exact punctuation limitation.
- Both HEAD configurations refuse execution. Loading `1a817b6`’s matcher and measurement script from Git into memory reproduced gold `R=W=R′=W′=0`, right blocks `10/10`, panel `2/97`, base `300/300`, and Arm 4 `2/2` versus `0/2`. Historical M10 panel: `25/25` passed.

One nonblocking wording overreach remains: [RESULTS.md:11](benchmarks/expertlongbench/study14/RESULTS.md#L11) says “refuses any other tree.” The guard checks only the `numbers.py` blob, as Amendment 1 accurately states. I found no other substantive overclaim.

Focused verification: **1,187 passed, 30 deselected** with conftest disabled and writable-path tests excluded. Full-suite collection was blocked by the read-only environment; `4004 passed` remains author-supplied. No files modified.

Reader sentence: “En-dash exponent support was measured and reverted because it broke an existing range contract; this slice documents the remaining limitation.”

**MERGE — the decisive reason is that the corrected record now accurately explains why the measured rule cannot ship.**
