# Saying where a number or a source came from

This project's deterministic checks read the fenced block below. It is the only
way the machine can tell something you traced from something you remembered, so
write it whenever you produce an artefact that has either.

**The one rule: you name a location, you never say what is at it.** Code opens
the file and looks for itself. Nothing here asks whether a number is right,
whether a source supports a claim, or what a line says — those are the auditor's
questions, and an annotation that answers them is answering a question nobody
asked. If you are not certain a value is at the line you would name, write
`uncited`. That is a fact about your annotation, it never counts against the
work, and it is always better than a guess.

## Fetched sources

When a report cites something you retrieved with a research tool this round,
list those source ids:

```crossaudit-sources
["<64-hex source id>", "<64-hex source id>"]
```

Only ids from this round's own fetches. Do not invent one and do not carry one
over from memory.
