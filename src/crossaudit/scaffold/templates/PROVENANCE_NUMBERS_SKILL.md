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
  - **Write the unit exactly as the source writes it, spaces included.** A
    space is not where a unit ends. Against a source saying `5 m-2 s-1` the unit
    is `m-2 s-1`: write that and it matches, write `m-2` and it does not,
    because half of a unit is still half of a unit. The same for `°C min⁻¹`,
    `mg h⁻¹` and `wt %` — copy the whole thing, spacing and all, and do not
    rewrite your own prose to make it one token.
  - A word after a unit is not part of it, and neither is a substance or a
    label. In `5 g sample` and `2 h later` the units are `g` and `h`; in
    `5 wt % Ni` the unit is `wt %`, because the `Ni` is what the percentage is
    OF, not part of how it is measured.
  - If the unit at that spot is something the checker cannot read to its end
    — more than six symbols in a row, or a `/` or `·` with nothing readable
    after it — the row blocks rather than matching half of it. `uncited` is
    the honest answer there, and it never counts against the work. One limit: a unit
    symbol of four or more letters, or a capitalised one, that the checker
    does not know (`mmHg`, `GBq`) is read as a word after the unit, so the
    part before it may match — copy the whole unit regardless. And after a
    spaced unit, anything with the shape of a unit symbol blocks rather than
    reads as a word: a short symbol pair such as `oz/yd`, `oz·yd` or `oz⋅yd`,
    a short label such as `run-2` or `m2`, short symbols on a hyphen or
    underscore such as `kg-m` or `lot_id` (with or without a digit, as in
    `lot_id/2`), a symbol joined to anything such as `g/xyz`, `dry·g`,
    `kg-m/s` or `2/g`, anything with a full-width joiner in it such as `kg／m`
    or `kg／m/dry`, a
    dotted abbreviation such as `a.u.` (other than e.g., i.e., a.m., p.m.,
    n.b., c.f.), or a short lower-case word the checker does not know.
    Hyphenated words, contractions, abbreviations such as `e.g.`, words in
    another script, words with a percent or per-mille sign such as `sample%`,
    `dry%` or `wet‰` (not an element symbol such as `Ni‰`), and words with
    trailing punctuation are read as words. `uncited` is the honest answer
    where a correct unit blocks.
  - `wt.%` is one unit (the period stays), and `s⁻¹`, `s−1` and `s-1` count as
    the same unit; still copy the source's own rendering.
  - For a range such as `775–850 °C`, either endpoint may be annotated with
    `°C`; never a value inside the range, and never the unit of a different
    quantity on the same line. A range written with a spaced ASCII hyphen
    (`5 - 10 °C`) is not read — it looks like a subtraction — so annotate the
    high endpoint or use `uncited`.
  - In a list such as `0, 20, 40, 80 wt.%`, every member may be annotated with
    `wt.%`; a member that carries its own unit keeps it, a colon or a
    semicolon does not make a list, a comma needs a space after it to separate
    (`12,5` is one number), and a labelled number (`Step 5`, `Figs. 5`,
    `Step: 5`) is not a member. The labels are a fixed named list (steps,
    figures, tables, equations, samples, runs, batches, compounds and the
    like, with their plurals); a word outside it does not protect a number.
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
  - If you cannot copy such a run, or the file says what you copied on more
    than one line and you cannot make it longer, write `uncited`.
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

## The one place a line number is still right

None of the above applies to a `results.json` quantity. That file says the same
thing in its own `source` field, by adding the line to the input it already
names: `runs.csv@v3#L14`. A script wrote that file and knows which line it read,
so the line is a fact there rather than a guess, and the checker reads it as one.

It changes nothing about the block above. **Never write a line number in the
`crossaudit-numbers` fence** — there you quote characters, and only characters.
