"""Replace every table in RESULTS-CEILING.md with the current generated one.

The report is prose plus generated tables. Editing prose without re-splicing leaves the two
a version apart — which happened twice, and the third cross-vendor review caught the second
time. This makes the splice a command instead of a habit, so "regenerate then splice" is one
step that cannot be half-done.

    python benchmarks/code/ceiling/splice_tables.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent.parent
REPORT = CODE / "RESULTS-CEILING.md"
TABLES = CODE / "records" / "ceiling" / "tables.md"


def splice(text: str, tables: str) -> tuple[str, list[str], list[str]]:
    """The report with every generated table swapped in: (new text, keys swapped, keys
    generated but absent from the report). Pure, so a test can assert that splicing the
    committed tables into the committed report changes nothing — the twelfth review found
    the generator still emitting a sentence the report had rejected, which this catches."""
    generated = {}
    for part in re.split(r"(?m)^(?=### Table )", tables):
        match = re.match(r"### Table (\w+)", part)
        if match:
            generated[match.group(1)] = part.rstrip() + "\n"
    out, pos, swapped = [], 0, []
    for match in re.finditer(r"(?m)^### Table (\w+) —", text):
        key = match.group(1)
        if key not in generated:
            continue
        rest = text[match.end():]
        ends = [x for x in (rest.find("\n### Table "), rest.find("\n---\n"),
                            rest.find("\n## ")) if x != -1]
        end = match.end() + (min(ends) if ends else len(rest))
        out.append(text[pos:match.start()])
        out.append(generated[key])
        swapped.append(key)
        pos = end + 1 if text[end:end + 1] == "\n" else end
    out.append(text[pos:])
    return "".join(out), swapped, sorted(set(generated) - set(swapped))


def main() -> int:
    new_text, swapped, missing = splice(REPORT.read_text(encoding="utf-8"),
                                        TABLES.read_text(encoding="utf-8"))
    REPORT.write_text(new_text, encoding="utf-8")
    print(f"spliced {len(swapped)} tables: {', '.join(swapped)}")
    if missing:
        print(f"WARNING: generated but not present in the report: {', '.join(missing)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
