#!/usr/bin/env python3
"""Simulate CONTAINMENT_RULE.md §2's extensions E1-E6 over the frozen items.

**Nothing under `src/` is touched.** This re-implements `contains_pair` with each
extension as a flag, reusing the shipped primitives (`_NUMBER`, `_BOUNDARY`,
`_DASHES`, `SYNONYMS`, `normalise_number`) so that with no flags set it is the
shipped matcher, and every difference is the extension and nothing else. A test
below asserts the no-flag equality on every item of the corpus.

    python3 simulate.py --sheet <archive>/sheet.jsonl [--gold gold.csv]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent.parent / "src"))

from crossaudit.dcl import numbers as N                     # noqa: E402

SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻"
ASCII_SUP = "0123456789+-"
_SUP_MAP = {ord(a): b for a, b in zip(SUP, ASCII_SUP)} | {0x2212: "-"}

#: E1/E2: a dash or a list separator, then a number.
_DASH_NUM = re.compile(r"\s*[-–—]\s*([0-9]+(?:[.,][0-9]+)*)")
_LIST_SEP = re.compile(r"\s*(?:,|and|or)\s+")
_BARE_NUM = re.compile(r"([+\-−]?(?:[0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?|\.[0-9]+))\Z")
#: E3: a whitespace-delimited formula token — letters, digits, brackets, `·`, `.`
_FORMULA = re.compile(r"[A-Za-z0-9()\[\]{}·.−+-]+")


def fold(text: str, e6: bool) -> str:
    return text.translate(_SUP_MAP) if e6 else text


def scan(text: str, skip_space: bool, e5: bool) -> tuple[str, str]:
    """`numbers._scan`, with E5's period rule as a flag."""
    i = (len(text) - len(text.lstrip())) if skip_space else 0
    depth, start = 0, i
    while i < len(text):
        ch = text[i]
        if ch.isspace() or ch in N._BOUNDARY or ch in N._DASHES:
            break
        if ch in N._OPENERS:
            depth += 1
        elif ch in N._CLOSERS:
            if depth == 0:
                break
            depth -= 1
        elif ch == ".":
            nxt = text[i + 1:i + 2]
            ok = nxt.isalnum() or (e5 and nxt in ("%", "‰"))
            if not ok:
                break
        i += 1
    return text[start:i], text[i:]


def unit_candidates(rest: str, ext: set[str]) -> list[str]:
    """The shipped `_unit_candidates`, plus E1, E2 and E4. Every addition is a
    reading of the unit that is at least as long as the whole token; none is
    shorter, which is the invariant the note requires of every extension."""
    e5 = "E5" in ext
    token, after = scan(rest, True, e5)
    out: list[str] = []
    if token:
        out.append(token)
        span = N._RANGE.fullmatch(token)
        if span and N.normalise_unit(span.group("u1")) == N.normalise_unit(span.group("u2")):
            out.append(span.group("u1"))
        if "%" not in token and "‰" not in token and token.isalpha():
            gap = len(after) - len(after.lstrip())
            sign = after[gap:gap + 1]
            if sign in ("%", "‰"):
                tail, _ = scan(after[gap + 1:], False, e5)
                out.append(f"{token} {sign}{tail}")

    # E1 — the endpoints of a range. The number is followed by <dash><number>,
    # and the unit token after that second number is offered to the first.
    # Only the two literal endpoints; the interior is never offered.
    if "E1" in ext and not token:
        m = _DASH_NUM.match(rest)
        if m:
            tail, _ = scan(rest[m.end():], True, e5)
            if tail:
                out.append(tail)
    if "E1" in ext and token:
        # `775–850°C`: the whole token after `775` is `–850°C`? No — a dash is a
        # boundary, so the token is empty and the branch above fires. The case
        # that reaches here is `99-102 kPa`, where `_scan` stops at `-`.
        pass

    # E2 — a list with one trailing unit. Walk forward over `,`/`and`/`or`
    # separated BARE numbers; the first member that carries a unit token ends the
    # walk and that token is offered. Any member carrying its own unit stops it.
    if "E2" in ext and not token:
        cursor = rest
        for _ in range(8):
            m = _LIST_SEP.match(cursor)
            if not m:
                break
            cursor = cursor[m.end():]
            nm = N._NUMBER.match(cursor)
            if not nm:
                break
            cursor = cursor[nm.end():]
            tok, _after = scan(cursor, True, e5)
            if tok:
                out.append(tok)
                break
    return out


def contains_pair(span: str, value: str, unit: str, ext: frozenset[str] = frozenset()) -> bool:
    e6 = "E6" in ext
    wanted_unit = N.normalise_unit(fold(unit, e6))
    wanted_value = N.normalise_number(value)
    if wanted_value is None:
        return False
    for m in N._NUMBER.finditer(span):
        if N.normalise_number(m.group(1)) != wanted_value:
            continue
        rest = span[m.end():]
        if N._UNPARSED.match(rest):
            continue
        if "U0" in ext and N._UNPARSED.match(rest.lstrip()) and rest[:1].isspace():
            continue                       # the out-of-band narrowing (§4)
        if not wanted_unit:
            return True
        cands = unit_candidates(rest, ext)
        # E4 — a unit transcribed with a space inside it: join as many
        # whitespace-separated tokens after the number as the transcription has
        # words, never fewer, never a token cut short.
        if "E4" in ext and " " in N.normalise_unit(unit):
            want_n = len(N.normalise_unit(unit).split())
            cursor, parts = rest, []
            for _ in range(want_n):
                tok, cursor = scan(cursor, True, "E5" in ext)
                if not tok:
                    break
                parts.append(tok)
            if len(parts) == want_n:
                cands = cands + [" ".join(parts)]
        if any(N.normalise_unit(fold(c, e6)) == wanted_unit for c in cands):
            return True
    # E3 — a decimal glued to a letter inside a formula token is a number with
    # the empty unit. Decimals only; integer subscripts stay unreadable.
    if "E3" in ext and not N.normalise_unit(unit) and "." in str(value):
        for tok in _FORMULA.findall(span):
            if not any(c.isalpha() for c in tok):
                continue
            for m in re.finditer(r"[0-9]*\.[0-9]+", tok):
                head = tok[:m.start()]
                if head and head[-1].isalpha() and N.normalise_number(m.group(0)) == wanted_value:
                    return True
    return False


#: The waves the note sequences, plus each extension alone.
SETS = {
    "E1": frozenset({"E1"}), "E2": frozenset({"E2"}), "E3": frozenset({"E3"}),
    "E4": frozenset({"E4"}), "E5": frozenset({"E5"}), "E6": frozenset({"E6"}),
    "U0 (out-of-band narrowing)": frozenset({"U0"}),
    "wave 1 = E4+E5+E6": frozenset({"E4", "E5", "E6"}),
    "wave 1+2 = +E1+E2": frozenset({"E4", "E5", "E6", "E1", "E2"}),
    "all = +E3": frozenset({"E4", "E5", "E6", "E1", "E2", "E3"}),
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True, type=Path)
    ap.add_argument("--gold", type=Path)
    args = ap.parse_args(argv)

    items = [json.loads(l) for l in args.sheet.read_text(encoding="utf-8").splitlines() if l.strip()]
    key = {r["id"]: r for r in (json.loads(l) for l in
           (HERE / "key.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}

    # Invariant: with no flags this IS the shipped matcher, on every item.
    bad = [it["id"] for it in items
           if contains_pair(it["line"], it["v"], it["u"])
           != N.contains_pair(it["line"], it["v"], it["u"])]
    print(f"no-flag equality with shipped matcher: {len(items) - len(bad)}/{len(items)}"
          + (f"  MISMATCH {bad[:5]}" if bad else "  OK"))
    if bad:
        return 1

    gold = {}
    if args.gold and args.gold.exists():
        for line in args.gold.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                i, lab = line.split(",")[:2]
                gold[i.strip()] = lab.strip()

    print(f"\n{'extension':<28} {'newly passes':>12} {'R':>4} {'W':>4} {'R-W':>5}   verdict")
    for name, ext in SETS.items():
        newly = [it for it in items
                 if contains_pair(it["line"], it["v"], it["u"], ext)
                 and not N.contains_pair(it["line"], it["v"], it["u"])]
        lost = [it for it in items
                if not contains_pair(it["line"], it["v"], it["u"], ext)
                and N.contains_pair(it["line"], it["v"], it["u"])]
        if gold:
            R = sum(1 for it in newly if key[it["id"]]["kind"] == "block"
                    and gold.get(it["id"]) == "C")
            W = sum(1 for it in newly if gold.get(it["id"]) == "N")
            unk = sum(1 for it in newly if gold.get(it["id"]) == "?")
            verdict = ("KILLED" if W else "undecided" if unk else "licensed")
            print(f"{name:<28} {len(newly):>12} {R:>4} {W:>4} {R - W:>5}   {verdict}"
                  + (f"  (+{len(lost)} newly blocked)" if lost else ""))
        else:
            print(f"{name:<28} {len(newly):>12}    -    -     -   (no gold yet)"
                  + (f"  (+{len(lost)} newly blocked)" if lost else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
