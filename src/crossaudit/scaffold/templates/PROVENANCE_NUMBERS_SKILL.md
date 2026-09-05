---
requires_check: number_source
---

# Saying where a number came from

**The one rule: you name a location, you never say what is at it.** Code opens
the file and looks for itself. Nothing here asks whether a number is right or
what a line says — those are the auditor's questions, and an annotation that
answers them is answering a question nobody asked. If you are not certain a
value is where you would say it is, write `uncited`. That is a fact about your
annotation, it never counts against the work, and it is always better than a
guess.

At the end of any artefact that states numbers, add one block:

```crossaudit-numbers
[{"v": "950", "u": "°C", "src": {"file": "work/synthesis/RECIPE.md", "quote": "Calcination: 950 °C for 1 h"}},
 {"v": "1",   "u": "h",  "src": {"file": "work/synthesis/RECIPE.md", "quote": "Calcination: 950 °C for 1 h"}},
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
- `src` — where you read it, as **the file and a quotation from it**, never as a
  line number and never as a whole file:
  - `{"file": "path/to/file.md", "quote": "…"}`, where the quote is the
    **shortest run of characters from ONE line of that file that you can see
    contains both the number and its unit**. There is no limit on how long it
    may be; the one rule is that it stays inside a single line of the file.
    **Copy it, do not retype it.**
    Code searches the file for those exact characters, so a word changed, a
    symbol re-spelled or an abbreviation expanded is a quote that is not there.
    Only runs of whitespace are forgiven: a line break inside your quote is the
    same as a space.
  - If you cannot copy such a run, or the file says what you copied more than
    once and you cannot make it longer, write `uncited`.
  - `uncited` when you did not read it anywhere — a constant you know, a value
    you computed, a number taken off a figure, or one you rounded or converted.

Do not write a line number anywhere in the block — not for the source, and not
for your own artefact. Code knows where you wrote the number, and it finds the
source by its characters.

Quote a span and not a whole file, because a file is not evidence: a *wrong*
source file happens to contain the right number about a quarter of the time, and
a wrong quotation almost never does. A file-wide citation tells the checker
nothing it can use.

Annotate what you can locate. There is no requirement to annotate every number,
and no number is worse for being `uncited`.
