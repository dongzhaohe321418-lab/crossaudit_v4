# Arm 6, attempt 1 — stopped after 8 of 33 instances: the generator path escalates on large inputs

2026-09-07, run `arm6-20260907T061203Z` (archive `wt-arm6-runs/arm6-attempt1-escalated/`).
Every instance failed the same way before writing a deliverable: two generator calls,
≈7,100 input tokens and 71–83 output tokens each, spend $0.045 per instance ($0.365 in all),
loop status `ESCALATED` on all eight — cause `generator_format` on 3 (reason "the generator
could not produce auditable work in round 1: the MCP tool request envelope must be the
entire reply") and cause `answered` on 5, where the loop surfaced the generator's own
sentence beside the envelope ("I need to read the … first") as a conversational answer
after the re-ask failed the same way. One root cause, two loop labels.

**What happened, read from the product's own code.** A scope file over 48,000 bytes
(`context/outline.py: MAX_FILE_BYTES`) is not inlined in the generator prompt; its body is
replaced by an outline and the generator is offered `file_read` for the committed text.
Every T01 input is over 100,000 characters, so the generator's first move is a tool
request — and it writes prose around the envelope, which `parse_tool_request` refuses
("the envelope must be the entire reply"). The single re-ask (`generator.REPAIR_ADDENDUM`)
then restates the **file** envelope — "every file in its own block … nothing outside the
SUMMARY line, the file blocks and the NOTES line" — to a model that has not yet read the
source and cannot write the file; the second reply fails the same way, and the round
escalates. On T03's 600-character recipes the file is inlined and no tool call is needed,
which is why Arms 2–5 saw this only as the "malformed-envelope re-ask" incidental
(D159: 23 of 24 rounds in Arm 2, 7 of 48 in Arm 3, "not yet understood and must not be
fixed until it is"). It is understood now: it is the re-ask naming the wrong envelope,
exposed whenever the generator needs a tool before it can write.

**Disposition.** The arm measures the product path as it ships, so the harness is not
changed to work around this. The defect goes to a product slice with its own review (the
re-ask names the envelope the reply attempted — tool, compute or file; the parser stays
strict, so prose beside an envelope is still a format failure and the ONE re-ask is what
changes), measured first by re-running these eight instances. Arm 6
proper runs on the product after that slice merges; its preregistration stands, with an
amendment naming this attempt and the product change between the two.

Nothing in this file quotes the corpus; the eight records in the archive hold no rows.
