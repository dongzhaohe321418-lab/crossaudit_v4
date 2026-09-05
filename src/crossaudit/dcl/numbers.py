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

The same two questions are asked of a `results.json` quantity whose `source`
carries a `#L14` fragment (§2.1's additive widening). That belongs here and not
in `check_provenance`, which decides membership and never opens a file: putting
it there would change an existing check's contract and leave two span
implementations that have to agree. A source with no fragment is untouched.

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
from .quantities import (declared_inputs, is_number_shape, normalise_number,
                         results_files)

#: A fenced ```crossaudit-numbers block; its body is a JSON array of rows.
_FENCE = re.compile(r"```crossaudit-numbers[^\n]*\n(.*?)\n```", re.S)
#: Every opening, closed or not. A block whose closing fence was never written
#: is not "no annotation" — it is an annotation that went missing, and silence
#: over it is the §5.4 failure in miniature.
_FENCE_OPEN = re.compile(r"```crossaudit-numbers[^\n]*(?:\n|\Z)")
_TEXT_SUFFIXES = (".md", ".txt", ".rst", ".tex")

#: Line numbers are bounded at nine digits. Not a style rule: `int()` refuses a
#: string of more than 4300 digits outright, so an unbounded `\d+` turns a
#: malformed annotation into an uncaught ValueError escaping `run_checks`. A
#: bounded pattern makes the same input fail the locator match and become an
#: ordinary CA-NUM-001 finding, which is what a malformed annotation is.
_LINE = r"\d{1,9}"
#: ``<path>[@<sha256>]#L<start>[-L<end>]`` — a span, never a file and never a
#: value. The sha is optional and may be a prefix of at least 8 hex characters,
#: because a committed annotation abbreviates one the way git does.
_SPAN = re.compile(r"(?P<path>[^@#]+?)(?:@(?P<sha>[0-9a-fA-F]{8,64}))?"
                   rf"#L(?P<start>{_LINE})(?:-L(?P<end>{_LINE}))?")
#: ``#L<n>`` — where in the enclosing artefact the number was written.
_AT = re.compile(rf"#L(?P<line>{_LINE})(?:-L{_LINE})?")
#: The same span fragment where it hangs off a `path@revision` results source.
_SOURCE_FRAGMENT = re.compile(rf"#L(?P<start>{_LINE})(?:-L(?P<end>{_LINE}))?$")

#: A bare number, sign and thousands separators included.
#:
#: The sign is not cosmetic: without it `-5 °C` transcribed as `-5` is a
#: non-overridable blocker on a correct citation, and transcribed as `5` it
#: PASSES against a span that says minus five — a wrong number accepted and a
#: right one refused, from one missing character class.
#:
#: A grouped token like ``1,000`` has two honest readings — one thousand, and a
#: "1" that happens to be followed by a comma — and `contains_pair` tries both
#: rather than picking one, because which reading a transcription meant is not
#: something this layer can know and guessing wrong would block correct work.
_NUMBER = re.compile(r"(?<![\w.])([+\-−]?[0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?"
                     r"(?:[eE][+\-−]?[0-9]{1,4})?)")
#: Any run of whitespace between a number and its unit, or none at all. Plain
#: `\s`, because Python's `\s` on a str pattern is the Unicode definition and
#: already covers U+00A0, U+2003 and U+202F — the three a copied table cell, a
#: typeset paper and a spreadsheet respectively produce. A hand-written list of
#: the ones somebody thought of is how the first two got in and the third did
#: not.
_GAP = r"\s*"

#: What follows a number and counts as its unit. THE TOKEN IS MAXIMAL, and that
#: is the whole point: taking a shorter reading as well let `5 mg/mL` satisfy an
#: annotation of `mg` and `5 cm-1` satisfy `cm` — the check accepting a
#: transcription of a different quantity, which is the direction that must never
#: be permitted. One maximal token, plus exactly two alternates that are longer
#: rather than shorter than it:
#:
#: * the word split from a percent sign (`wt %`), which the space would
#:   otherwise cut short;
#: * a purely numeric token, because `1` is a legitimate dimensionless marker
#:   and `{"value": 0.42, "unit": "1"}` against a line reading `0.42 1` is a
#:   correct citation that had no reading at all.
_UNIT_BODY = r"A-Za-zµμ°ÅΩ%‰"
_UNIT_TAIL = r"A-Za-zµμ°ÅΩ%‰0-9()⁻⁰¹²³⁴⁵⁶⁷⁸⁹+\-"
#: Maximal: letters/symbols, then any number of connector-joined parts, then an
#: optional exponent written as superscripts or as `-1` / `2`.
#:
#: The `-1` / `2` exponent tail is taken only where nothing unit-shaped follows
#: it. Without that guard a range — `(20°C-25°C)`, which is how a source states
#: an ambient window — read as the single unit `°C-25`, and a draft citing
#: `20 °C` off that line was blocked for transcribing it correctly. A hyphen
#: between two units is a range; a hyphen before the end of the token is an
#: exponent; the lookahead is the only thing that can tell them apart.
_EXPONENT_TAIL = rf"(?:[⁻]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+|-?[0-9]{{1,3}}(?![0-9]*[{_UNIT_BODY}]))?"
_UNIT_MAXIMAL = re.compile(
    rf"[{_UNIT_BODY}]+(?:[/·⋅∙*^][{_UNIT_TAIL}]+)*{_EXPONENT_TAIL}")
_UNIT_SPLIT_PERCENT = re.compile(rf"[A-Za-z]+{_GAP}[%‰]")
#: A dimensionless numeric marker, and nothing that continues into a word.
_UNIT_NUMERIC = re.compile(rf"[0-9]+(?:\.[0-9]+)?(?![{_UNIT_BODY}0-9.])")

#: The unit-synonym table §3.1 calls load-bearing, carried over verbatim from
#: the probe that measured it. Measured again against THIS code over the 16
#: archived drafts (`benchmarks/expertlongbench/provenance_arm1.py`): deleting it
#: takes the primary false-blocker rate from 6 of 365 (1.64%) to 12 of 365
#: (3.29%, 95% Wilson 1.89–5.66%) — past §6's 2% kill line — and the six it adds
#: are every draft that wrote `hours`, `minutes` or `wt%` where its source wrote
#: `h`, `min` or `wt %`. The six that remain either way are an artefact of the
#: harness's own unit vocabulary, measured and reported there rather than
#: corrected.
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


def _unit_candidates(rest: str) -> list[str]:
    """Every reading of what follows a number, after any run of whitespace.

    The first is maximal, so a shorter prefix of a compound unit is never a
    candidate. The other two are longer than it, not shorter.
    """
    tail = rest[re.match(_GAP, rest).end():]
    out: list[str] = []
    for pattern in (_UNIT_MAXIMAL, _UNIT_SPLIT_PERCENT, _UNIT_NUMERIC):
        m = pattern.match(tail)
        if m and m.group(0):
            out.append(m.group(0))
    return out


def contains_pair(span: str, value: str, unit: str) -> bool:
    """Whether the transcribed (value, unit) pair occurs in this text.

    Exact, and deliberately so: the number must appear as a number, and where a
    unit was transcribed it must be the whole of the unit token following that
    occurrence, under the synonym table. A value stated in words, converted, or
    read off a plot is not matched and must not be — that is what `uncited` is
    for.

    A value that does not normalise as a number returns False, and the caller
    turns that into CA-NUM-001. There is no substring fallback: the one that
    used to be here ignored the unit entirely, so source `1e3 K` satisfied an
    annotation of `1e3` with unit `g`.
    """
    wanted_unit = normalise_unit(unit)
    wanted_value = normalise_number(value)
    if wanted_value is None:
        return False
    for m in _NUMBER.finditer(span):
        token = m.group(1)
        if normalise_number(token) == wanted_value:
            if not wanted_unit:
                return True
            rest = span[m.end():]
            if any(normalise_unit(c) == wanted_unit for c in _unit_candidates(rest)):
                return True
        if "," in token and not wanted_unit:
            # The other reading of a grouped token: the digits before the
            # separator, which are followed by a comma and so carry no unit.
            if normalise_number(token.split(",")[0]) == wanted_value:
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


#: A transcribed value or unit may arrive as a string or as a JSON number: a
#: generator writing `"v": 950` has still transcribed, not judged, and refusing
#: it would be a non-overridable blocker on a well-formed annotation.
_SCALAR = (str, int, float)


def _row_findings(path: str, files: Mapping[str, bytes], row: dict) -> list[Finding]:
    # All four fields, present. `u` was previously allowed to be absent and read
    # as unitless, which let a row opt out of the half of the check that
    # compares units by simply not writing the key — the contract says four
    # fields, so a row with three is not a row this check can verify.
    missing = [k for k in ("v", "u", "at", "src") if k not in row]
    bad = [k for k in ("v", "u") if k in row and not isinstance(row[k], _SCALAR)]
    bad += [k for k in ("at", "src") if k in row and not isinstance(row[k], str)]
    if missing or bad:
        detail = ("is missing " + ", ".join(missing) if missing
                  else "has a non-text " + ", ".join(bad))
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"a source annotation {detail}; each row names v, u, at "
                        f"and src, and a row that names fewer cannot be checked")]
    v, u = str(row["v"]), str(row["u"])
    src = str(row["src"]).strip()
    at = _at_line(row["at"])
    if not at or not v.strip() or not src:
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        "a source annotation has an empty number or location; each "
                        "row names v, u, at and src")]
    shown = f'"{v} {u}"' if u else f'"{v}"'
    where = f"line {at}"
    if normalise_number(v) is None:
        # A transcription that is not a number cannot be looked for. It used to
        # fall through to a substring test that ignored the unit entirely, so
        # source `1e3 K` satisfied an annotation of `1e3` with unit `g`.
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} transcribes {v!r}, which is not a number; write the "
                        f"number alone, or name no source with \"uncited\"")]

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
    return _verify_locator(path, files, locator, v, u, shown, where, src)


def _verify_locator(path: str, files: Mapping[str, bytes], locator: str,
                    v: str, u: str, shown: str, where: str,
                    src: str) -> list[Finding]:
    """Resolve one span and look in it. The half of the check that opens a file.

    Shared by the fenced annotation and by a `results.json` quantity whose
    `source` carries a `#L…` fragment, so there is exactly one implementation of
    "does the named span hold this pair" and exactly one mutation that reddens
    both.
    """
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


def _results_findings(path: str, files: Mapping[str, bytes], data: bytes,
                      opaque: frozenset) -> list[Finding]:
    """The structured half: a `results.json` quantity whose `source` names a span.

    §2.1 widens a quantity's `source` from `path@revision` to
    `path@revision#L…`. `check_provenance` decides membership and never opens a
    file — that is its whole contract — so without this nobody would look at the
    line, and the widening would have accepted a claim no code checks. A source
    with no `#L…` fragment is the world before the widening and is left exactly
    as it was.

    Two rules learned from the review, both of which had made the compensation
    partial rather than real:

    * **A row this cannot read is a finding, never a skip.** It used to skip a
      value of the wrong shape "reported by units", and `check_units` has never
      looked at `value` at all — so a null value citing line 999 of a two-line
      file passed the complete science profile in silence.
    * **Whole-string precedence.** If the entire source string is itself an
      exact declared input, someone declared a revision that happens to contain
      `#L…`; it is opaque, and `check_provenance` already accepted it as a
      member. Reading a fragment out of it here would block on a shape the
      other check just approved.
    """
    out: list[Finding] = []
    text = _text(data)
    if text is None:
        return out
    try:
        # As in the fence: no literal is rounded through a float before the
        # canonical-decimal comparison sees it.
        doc = json.loads(text, parse_float=str, parse_int=str)
    except ValueError:
        return out                              # reported by parseable / schema
    if not isinstance(doc, dict) or not isinstance(doc.get("quantities"), list):
        return out
    for i, q in enumerate(doc["quantities"]):
        if not isinstance(q, dict):
            continue
        raw_src = q.get("source")
        if not isinstance(raw_src, str):
            continue                            # not a locator; provenance blocks it
        src = raw_src.strip()
        if src in opaque:
            continue                            # declared verbatim, so opaque
        fragment = _SOURCE_FRAGMENT.search(src)
        if not fragment:
            continue
        where = f"quantities[{i}]"
        v, u = q.get("value"), q.get("unit")
        if not is_number_shape(v) or not isinstance(u, str):
            out.append(Finding(
                BLOCKER, "CA-NUM-001", path,
                f"{where} names a line for a value this check cannot read; a "
                f"quantity citing a line needs a numeric value and a text unit"))
            continue
        v, u = str(v), str(u)
        named = src[:fragment.start()].rpartition("@")[0] or src[:fragment.start()]
        shown = f'"{v} {u}"' if u else f'"{v}"'
        out.extend(_verify_locator(
            path, files, named + fragment.group(0), v, u, shown, where, src))
    return out


def check_number_source(files: Mapping[str, bytes]) -> list[Finding]:
    """CA-NUM-001/002: a number's declared source span must resolve and contain it."""
    out: list[Finding] = []
    # The same discovery the builtin checks use, so a file they read is never a
    # file this one silently ignores: `myresults.json` was recognised by
    # `_results_files` and not by the exact-basename test that used to be here.
    structured = set(results_files(files))
    # A source string declared verbatim as an input is opaque (see below).
    opaque = frozenset(item for _meta, item in declared_inputs(files))
    for path, data in sorted(files.items()):
        if path in structured:
            out.extend(_results_findings(path, files, data, opaque))
            continue
        if not path.endswith(_TEXT_SUFFIXES):
            continue
        text = _text(data)
        if text is None:
            continue
        bodies = _FENCE.findall(text)
        if len(_FENCE_OPEN.findall(text)) > len(bodies):
            # An opening with no closing fence. Reading it as "no annotation"
            # would let a truncated or hand-mangled block pass vacuously, which
            # is indistinguishable from a document that never annotated at all.
            out.append(Finding(
                BLOCKER, "CA-NUM-001", path,
                "a crossaudit-numbers block was opened and never closed; its "
                "annotation cannot be read"))
        for body in bodies:
            try:
                # Every literal arrives as text. `json.loads` would otherwise
                # round `9007199254740993.0` through a double before the string
                # comparison ever saw it, so the precision the canonical-decimal
                # comparison exists to preserve would already be gone.
                rows = json.loads(body, parse_float=str, parse_int=str)
            except ValueError as exc:
                # ValueError, not JSONDecodeError: a literal with more than
                # 4300 digits raises the plain base class, and letting it escape
                # `run_checks` turned a malformed annotation into a crash.
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
         "block, and every results.json quantity whose source carries a '#L14' span "
         "fragment, must name a span — a path and a line range inside the audited "
         "scope — that resolves and literally contains the transcribed value and unit "
         "(under a fixed unit-synonym table). A named span that does not resolve or "
         "does not contain the pair is a blocker; 'uncited' is advisory and never "
         "blocks; a number nobody annotated is not this check's business. It enforces "
         "DECLARED provenance, never coverage, and never judges whether a number is "
         "correct.")
