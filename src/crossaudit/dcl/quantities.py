"""What a quantity is, and what makes two numbers the same number.

Shared by `builtin.check_provenance` and `numbers.check_number_source` because
they must agree, and the way they stopped agreeing is instructive. The span
widening let `check_provenance` accept `path@revision#L14` on the promise that
`number_source` would open the file and look — but `number_source` recognised
only the exact basename `results.json` where builtin recognised any path ending
in it, and it skipped rows whose `value` was a shape it could not read, on the
belief that `check_units` validated `value`. `check_units` tests the truthiness
of `unit` and `source` and has never looked at `value` at all. Between the two
gaps, a quantity with a null value citing line 999 of a two-line file passed the
complete science profile with no finding, where the code before the widening
blocked it.

So the three things both checks need — which files hold quantities, what the
declared inputs are, and whether a value is a number — live here, once.

**Numbers are compared as canonical decimal strings, never as floats.** Two
integers 2**53 apart round to the same double, so a float comparison would
report a span containing 9007199254740992 as containing 9007199254740993: a
check saying it verified a number literally while accepting a different one.
`Decimal` construction from a string is exact and unbounded, and `format(d, "f")`
is exact, so `1e3` and `1000` canonicalise to the same string without either
one passing through binary floating point.
"""
from __future__ import annotations

import math
import re
from decimal import Decimal, InvalidOperation
from typing import Mapping

import yaml

RESULTS_SUFFIX = "results.json"

#: A decimal or exponent literal. ASCII digits only — `\d` also matches Arabic-
#: Indic and Devanagari digits, which `Decimal` and `int` do accept and which no
#: transcription of a source's bytes would ever produce deliberately.
#:
#: The lengths are bounded because this text arrives from a generator: an
#: unbounded coefficient is a 4300-digit `int()` refusal waiting to happen, and
#: an unbounded exponent turns `format(Decimal("1e999999999"), "f")` into a
#: gigabyte of zeros inside the deterministic layer.
_DECIMAL = re.compile(r"[+-]?(?:[0-9]{1,512}(?:\.[0-9]{1,512})?|\.[0-9]{1,512})"
                      r"(?:[eE][+-]?[0-9]{1,4})?")
#: U+2212 MINUS SIGN is what a typesetter, a spreadsheet export and half the
#: scientific literature write for a negative number. It is a minus.
_MINUS = "−"


def results_files(files: Mapping[str, bytes]) -> list[str]:
    """Every path holding structured quantities. One definition, so a file the
    builtin checks read is never a file `number_source` silently ignores."""
    return [p for p in files if p.endswith(RESULTS_SUFFIX)]


def declared_inputs(files: Mapping[str, bytes]) -> list[tuple[str, str]]:
    """Every `(metadata path, inputs entry)` pair, in file order."""
    out: list[tuple[str, str]] = []
    for m in sorted(p for p in files if p.endswith("metadata.yml")):
        try:
            doc = yaml.safe_load(files[m].decode("utf-8")) or {}
        except Exception:                              # reported by check_schema
            continue
        if not isinstance(doc, dict):
            continue
        raw = doc.get("inputs")
        for item in (raw if isinstance(raw, list) else []):
            if isinstance(item, str) and item.strip():
                out.append((m, item.strip()))
    return out


def normalise_number(token) -> str | None:
    """One canonical decimal string for a transcribed number, or None.

    Canonical means: a U+2212 minus folded onto `-`, thousands separators
    dropped, exponent notation expanded (`1e3` and `1000` are one number), a
    leading `+` dropped, leading zeros before the point dropped, trailing zeros
    after the point dropped, and a negative zero folded onto zero.

    None means "this is not a number", and every caller must treat that as a
    finding rather than falling back to something looser. A substring fallback
    is what let source `1e3 K` satisfy an annotation of `1e3` with unit `g`.
    """
    text = str(token).strip().replace(",", "").replace(_MINUS, "-")
    if not _DECIMAL.fullmatch(text):
        return None
    try:
        value = Decimal(text)
    except InvalidOperation:                           # pragma: no cover
        return None
    plain = format(value, "f")
    negative = plain.startswith("-")
    digits = plain.lstrip("+-")
    whole, _, frac = digits.partition(".")
    frac = frac.rstrip("0")
    whole = whole.lstrip("0") or "0"
    out = whole + ("." + frac if frac else "")
    return out if out == "0" else (("-" if negative else "") + out)


def is_number_shape(value) -> bool:
    """Whether a `results.json` `value` is a number at all.

    `check_units` never asked this — it tests that `unit` and `source` are
    truthy — so nothing in the layer established it before a span locator was
    allowed to hang off the row. A bool is not a number here: JSON `true` is not
    a measurement, and Python would otherwise call it 1.
    """
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, str):
        return normalise_number(value) is not None
    return False
