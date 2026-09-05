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

## Numbers

At the end of any artefact that states numbers, add one block:

```crossaudit-numbers
[{"v": "950", "u": "°C", "at": "#L14", "src": "work/synthesis/RECIPE.md#L11"},
 {"v": "1",   "u": "h",  "at": "#L14", "src": "work/synthesis/RECIPE.md#L11"},
 {"v": "180", "u": "°C", "at": "#L9",  "src": "uncited"}]
```

All four fields, every row. A row with three cannot be checked and is refused.

- `v` — the number **exactly as you wrote it in your own prose**, and nothing
  else: no `~`, no range, no words. Transcribe the characters; do not convert or
  re-render them. If what you wrote is not a single number, write `uncited`.
- `u` — its unit, as you wrote it, in full: `mg/mL`, not `mg`. Use `""` when the
  number has no unit.
- `at` — the line of *this* artefact where you wrote it: `"#L14"`.
- `src` — where you read it, as a **line**, never as a whole file:
  - `path/to/file.md#L11`, or `path/to/file.md#L11-L13` for a short range;
  - `uncited` when you did not read it anywhere — a constant you know, a value
    you computed, a number taken off a figure, or one you rounded or converted.

Name a line and not a file, because a file is not evidence: a *wrong* source
file happens to contain the right number about a quarter of the time, and a
wrong line almost never does. A file-wide citation tells the checker nothing it
can use.

Annotate what you can locate. There is no requirement to annotate every number,
and no number is worse for being `uncited`.

A `results.json` quantity says the same thing in its own `source` field, by
adding the line to the input it already names: `runs.csv@v3#L14`.

## Fetched sources

When a report cites something you retrieved with a research tool this round,
list those source ids:

```crossaudit-sources
["<64-hex source id>", "<64-hex source id>"]
```

Only ids from this round's own fetches. Do not invent one and do not carry one
over from memory.
