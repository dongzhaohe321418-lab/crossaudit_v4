---
requires_check: number_source
---

# Saying where a number came from

**The one rule: you name a location, you never say what is at it.** Code opens
the file and looks for itself. Nothing here asks whether a number is right or
what a line says — those are the auditor's questions, and an annotation that
answers them is answering a question nobody asked. If you are not certain a
value is at the line you would name, write `uncited`. That is a fact about your
annotation, it never counts against the work, and it is always better than a
guess.

At the end of any artefact that states numbers, add one block:

```crossaudit-numbers
[{"v": "950", "u": "°C", "src": "work/synthesis/RECIPE.md#L11"},
 {"v": "1",   "u": "h",  "src": "work/synthesis/RECIPE.md#L11"},
 {"v": "180", "u": "°C", "src": "uncited"}]
```

All three fields, every row. A row with two cannot be checked and is refused.

- `v` — the number **exactly as you wrote it in your own prose**, and nothing
  else: no `~`, no range, no words. If what you wrote is not a single number,
  write `uncited`.
- `u` — its unit, as you wrote it, **in full**: `°C/min`, not `°C`; `mg/mL`, not
  `mg`. The whole unit is compared, so half of one does not match. Use `""` when
  the number has no unit.
  - A unit written with a **space inside it** is read as its FIRST token only,
    because a space is where a unit ends. Against a source saying `5 m-2 s-1`
    the checker sees `m-2` and cannot see the rest: `m-2` is accepted, and
    `m-2 s-1`, `m-2s-1` and `m-2·s-1` are all rejected, because none of them is
    what is written at that spot. This is the one place a partial unit passes,
    and it is structural. Write the unit joined in your own prose (`m-2s-1`,
    `m-2·s-1`) so it is one token, or write `uncited`.
- `src` — where you read it, as a **line**, never as a whole file:
  - `path/to/file.md#L11`, or `path/to/file.md#L11-L13` for a short range;
  - `uncited` when you did not read it anywhere — a constant you know, a value
    you computed, a number taken off a figure, or one you rounded or converted.

**Every file you may cite is shown to you with its line numbers in a gutter:**
`   11| Calcination: 950 °C for 1 h`. The number in the gutter *is* the line.
Copy it, never count it.

**A file shown without a gutter, or shown as an outline instead of its
contents, cannot be cited — write `uncited`.** An outline's tenth line is not
the file's tenth line, and a line you cannot see the number of is a line you
cannot name.

Do not write a line of your own artefact anywhere in the block. Code knows
where you wrote the number; it needs only to know where you read it.

Name a line and not a file, because a file is not evidence: a *wrong* source
file happens to contain the right number about a quarter of the time, and a
wrong line almost never does. A file-wide citation tells the checker nothing it
can use.

Annotate what you can locate. There is no requirement to annotate every number,
and no number is worse for being `uncited`.

A `results.json` quantity says the same thing in its own `source` field, by
adding the line to the input it already names: `runs.csv@v3#L14`.
