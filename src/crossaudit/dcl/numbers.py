"""number → source: a declared span must resolve and contain the number.

`docs/design/PROVENANCE_CHECKS.md` §2.1/§3.1/§3.4, under D155's surviving rule:
**a model may name evidence; code verifies it exists and says what was claimed;
a model is never asked what the evidence says.**

A text artefact carries one fenced block listing the numbers it wrote and where
each came from:

    ```crossaudit-numbers
    [{"v": "950", "u": "°C", "at": "#L14", "src": "work/synthesis/RECIPE.md#L11"},
     {"v": "180", "u": "°C", "at": "#L9",  "src": "uncited"}]
    ```

No field carries a truth value. `v`/`u` transcribe bytes the generator itself
wrote into its own prose; `at` and `src` are addresses. The check asks two
mechanical questions and no others:

1. does `src` resolve — is its path in the audited scope, do its declared bytes
   still hash to what it declared, is its line range inside the file;
2. does the **named span** contain the transcribed `(value, unit)` pair.

**Span-scoped, never file-scoped.** Measured on 16 archived drafts
(`benchmarks/expertlongbench/provenance_probe.py`): a *wrong source file*
contains the claimed pair 27.7% of the time (596/2150); a *wrong line of the
right file* contains it 0.0% of the time (0/1825). Checking the file would let a
plausible-but-wrong citation through a quarter of the time — the
inverted-executable-check failure D155 killed, in a new costume. `_span` is
therefore the load-bearing line of this module, and it has a test that asserts
the check goes green when it is widened.

Honest boundary, stated the way A4's is (`provenance.py:16-20`):

* This enforces **declared** provenance, never coverage. A number the generator
  did not annotate produces nothing at all, and a document with no fence passes
  vacuously. Whether every number *should* have been annotated is a judgment
  about the text, which is the auditor's tier, not this one.
* `uncited` is not a truth value. It is the generator declining to name a
  location — a fact about the annotation, not a claim about the world — and it
  is ADVISORY: 13.3% of real draft numbers (57/430) are melting points and ionic
  radii that occur in no source, and blocking those would make the product
  refuse to state a well-known constant.
* Containment is exact. Where a source states a value in another form — "a
  third" for 0.33, an hour for 60 min, a value read off a plot — the check must
  not attempt it; such a number is annotated `uncited` and reaches the auditor.
* A `governed:` locator names bytes this project does not retain (§1.2), so the
  check cannot re-read them and says so as an ADVISORY rather than passing in
  silence.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Mapping

from .framework import ADVISORY, BLOCKER, Finding, register

#: A fenced ```crossaudit-numbers block; its body is a JSON array of rows.
_FENCE = re.compile(r"```crossaudit-numbers[^\n]*\n(.*?)\n```", re.S)
_TEXT_SUFFIXES = (".md", ".txt", ".rst", ".tex")

#: ``<path>[@<sha256>]#L<start>[-L<end>]`` — a span, never a file and never a
#: value. The sha is optional and may be a prefix of at least 8 hex characters,
#: because a committed annotation abbreviates one the way git does.
_SPAN = re.compile(r"(?P<path>[^@#]+?)(?:@(?P<sha>[0-9a-fA-F]{8,64}))?"
                   r"#L(?P<start>\d+)(?:-L(?P<end>\d+))?")
#: ``#L<n>`` — where in the enclosing artefact the number was written.
_AT = re.compile(r"#L(?P<line>\d+)(?:-L\d+)?")

#: A bare number, thousands separators included. A grouped token like ``1,000``
#: has TWO honest readings — one thousand, and a "1" that happens to be followed
#: by a comma — and `contains_pair` tries both rather than picking one, because
#: which reading a transcription meant is not something this layer can know and
#: guessing wrong would block correct work.
_NUMBER = re.compile(r"(?<![\w.])(\d+(?:,\d{3})*(?:\.\d+)?)")
#: What may follow a number and count as its unit, in two shapes: a plain run
#: (``°C``, ``h``, ``hours``, ``μm``) and a word split from a percent sign
#: (``wt %``), which the synonym table folds together.
_UNIT_RUN = re.compile(r"[ \t]?([A-Za-zµμ°Å%]+)")
_UNIT_SPLIT_PERCENT = re.compile(r"[ \t]?([A-Za-z]+)[ \t]?(%)")

#: The unit-synonym table §3.1 calls load-bearing, carried over verbatim from
#: the probe that measured it. Without it, 8 of 430 draft numbers (1.9%) fail
#: while naming the RIGHT line, purely on unit rendering — eight spurious
#: non-overridable blockers per 16 drafts, and §6's kill condition (>2%) fires.
#:
#: It is fixed, and it is small on purpose. Growing it against a failing corpus
#: would be tuning a measurement to pass its own test; entries belong here only
#: when two renderings of a unit are the same unit by definition.
SYNONYMS: dict[str, str] = {
    "hours": "h", "hour": "h",
    "minutes": "min", "minute": "min",
    "wt %": "wt%", "mol %": "mol%",
    "µm": "μm",
}


def _text(data: bytes) -> str | None:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def normalise_unit(unit: str) -> str:
    """Fold one rendering of a unit onto another. Whitespace only, plus the
    fixed synonym table; nothing here is a conversion."""
    folded = " ".join(str(unit or "").split())
    return SYNONYMS.get(folded, folded)


def _value(token: str) -> float | None:
    try:
        return float(str(token).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _unit_candidates(rest: str) -> list[str]:
    out: list[str] = []
    run = _UNIT_RUN.match(rest)
    if run:
        out.append(run.group(1))
    split = _UNIT_SPLIT_PERCENT.match(rest)
    if split:
        out.append(f"{split.group(1)} {split.group(2)}")
    return out


def contains_pair(span: str, value: str, unit: str) -> bool:
    """Whether the transcribed (value, unit) pair occurs in this text.

    Exact, and deliberately so: the number must appear as a number, and where a
    unit was transcribed it must follow that occurrence of the number under the
    synonym table. A value stated in words, converted, or read off a plot is not
    matched and must not be — that is what `uncited` is for.
    """
    wanted_unit = normalise_unit(unit)
    wanted_value = _value(value)
    if wanted_value is None:
        # Not a number at all; fall back to plain containment so a malformed
        # transcription fails on the bytes rather than on the parser.
        return str(value or "") in span
    for m in _NUMBER.finditer(span):
        token = m.group(1)
        if _value(token) == wanted_value:
            if not wanted_unit:
                return True
            rest = span[m.end():]
            if any(normalise_unit(c) == wanted_unit for c in _unit_candidates(rest)):
                return True
        if "," in token and not wanted_unit:
            # The other reading: the digits before the separator, which are
            # followed by a comma and so can carry no unit.
            if _value(token.split(",")[0]) == wanted_value:
                return True
    return False


def _resolve(files: Mapping[str, bytes], annotated: str, path: str) -> str | None:
    """A key of the `files` mapping, or None. Exact first, then relative to the
    annotating artefact's own directory — both deterministic, neither a search."""
    if path in files:
        return path
    base = annotated.rsplit("/", 1)[0] if "/" in annotated else ""
    if base:
        joined = f"{base}/{path}"
        if joined in files:
            return joined
    return None


def _span(text: str, start: int, end: int) -> str | None:
    """The named lines, 1-based and inclusive, or None if the range is not
    inside the file.

    **The whole check turns on this function.** Returning the whole `text`
    regardless of `start`/`end` is the §4 mutation, and it makes a
    wrong-line annotation pass — see
    `tests/test_number_source_check.py::test_the_span_and_not_the_file_is_what_is_checked`.
    """
    lines = text.split("\n")
    if start < 1 or end < start or end > len(lines):
        return None
    return "\n".join(lines[start - 1:end])


def _at_line(at: str) -> str:
    m = _AT.fullmatch(str(at or "").strip())
    return m.group("line") if m else ""


def _row_findings(path: str, files: Mapping[str, bytes], row: dict) -> list[Finding]:
    v, u = str(row.get("v", "")), str(row.get("u", ""))
    src = str(row.get("src", "")).strip()
    at = _at_line(row.get("at", ""))
    if not at or not v or not isinstance(row.get("src"), str) or not src:
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        "a source annotation is missing its number or its location; "
                        "each row names v, u, at and src")]
    shown = f'"{v} {u}"' if u else f'"{v}"'
    where = f"line {at}"

    if src == "uncited":
        return [Finding(ADVISORY, "CA-NUM-003", path,
                        f"{where} names no source for {shown}; passed to the auditor")]
    if src.startswith("governed:"):
        # §1.2: the fetched text is not retained anywhere, so code cannot
        # re-read it. Saying so is honest; passing in silence would not be.
        return [Finding(ADVISORY, "CA-NUM-003", path,
                        f"{where} names a fetched source for {shown}, whose text this "
                        f"project does not keep; passed to the auditor")]

    # `computed:` names a path in this increment exactly as the plain form does.
    # Whether a script CAUSED that value is figure_code's question (§3.2); that
    # the named span holds it is still this one's, and answering it here closes
    # the alternative of evading every locator check with a four-word prefix.
    locator = src[len("computed:"):] if src.startswith("computed:") else src
    m = _SPAN.fullmatch(locator)
    if not m:
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} names {src!r} for {shown}, which is not a line in a "
                        f"file (expected path#L14 or path#L14-L16)")]

    named, start = m.group("path").strip(), int(m.group("start"))
    end = int(m.group("end") or start)
    lines = f"{named}:{start}" if end == start else f"{named}:{start}-{end}"
    key = _resolve(files, path, named)
    if key is None:
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} names {lines} for {shown}, which is not in the "
                        f"audited scope")]
    declared_sha = (m.group("sha") or "").lower()
    if declared_sha:
        actual = hashlib.sha256(files[key]).hexdigest()
        if not actual.startswith(declared_sha):
            return [Finding(BLOCKER, "CA-NUM-001", path,
                            f"{where} names {lines} for {shown}, but that file's bytes "
                            f"are not the ones the annotation pinned")]
    body = _text(files[key])
    if body is None:
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} names {lines} for {shown}, which is not readable text")]
    span = _span(body, start, end)
    if span is None:
        last = len(body.split("\n"))
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} names {lines} for {shown}, but that file ends at "
                        f"line {last}")]
    if not contains_pair(span, v, u):
        tail = "is not on that line" if end == start else "is not in those lines"
        return [Finding(BLOCKER, "CA-NUM-002", path,
                        f"{where} names {lines} — {shown} {tail}")]
    return []


def check_number_source(files: Mapping[str, bytes]) -> list[Finding]:
    """CA-NUM-001/002: a number's declared source span must resolve and contain it."""
    out: list[Finding] = []
    for path, data in sorted(files.items()):
        if not path.endswith(_TEXT_SUFFIXES):
            continue
        text = _text(data)
        if text is None:
            continue
        for body in _FENCE.findall(text):
            try:
                rows = json.loads(body)
            except json.JSONDecodeError as exc:
                out.append(Finding(
                    BLOCKER, "CA-NUM-001", path,
                    f"a crossaudit-numbers declaration does not parse as JSON: {exc}"))
                continue
            if not isinstance(rows, list) or not all(
                    isinstance(r, dict) for r in rows):
                out.append(Finding(
                    BLOCKER, "CA-NUM-001", path,
                    "a crossaudit-numbers declaration must be a JSON array of "
                    "{v, u, at, src} rows"))
                continue
            for row in rows:
                out.extend(_row_findings(path, files, row))
    return out


register("number_source", check_number_source,
         "Opt-in: every number a text artefact declares in a ```crossaudit-numbers "
         "block must name a span — a path and a line range inside the audited scope — "
         "that resolves and literally contains the transcribed value and unit (under a "
         "fixed unit-synonym table). A named span that does not resolve or does not "
         "contain the pair is a blocker; 'uncited' is advisory and never blocks; a "
         "number nobody annotated is not this check's business. It enforces DECLARED "
         "provenance, never coverage, and never judges whether a number is correct.")
