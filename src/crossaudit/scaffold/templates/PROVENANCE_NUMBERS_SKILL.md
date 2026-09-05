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
