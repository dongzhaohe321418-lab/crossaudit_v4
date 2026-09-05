---
requires_check: source_provenance
---

# Saying where a fetched source came from

**The one rule: you name a location, you never say what is at it.** Code checks
that the source was really retrieved. Nothing here asks whether a source
supports a claim — that is the auditor's question.

When a report cites something you retrieved with a research tool this round,
list those source ids:

```crossaudit-sources
["<64-hex source id>", "<64-hex source id>"]
```

Only ids from this round's own fetches. Do not invent one and do not carry one
over from memory.
