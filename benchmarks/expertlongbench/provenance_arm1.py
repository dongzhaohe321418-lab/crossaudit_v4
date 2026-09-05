"""Arm 1 of `docs/design/PROVENANCE_CHECKS.md` §6, run against the SHIPPED check.

`provenance_probe.py` measured the *contract* — whether a locator must name a
span — with a matcher written for the measurement. This runs the code that
actually ships (`crossaudit.dcl.numbers.check_number_source`) over the same 16
archived T03 drafts, with the annotations the probe derives, and reports the
preregistered primary outcome:

    the FALSE-BLOCKER RATE — of numbers that DO trace to the source, the
    fraction the verifier fails. Kill condition: > 2%.

No model is called, no key is read, nothing is written. ~2 seconds, $0.

**How an annotation is derived, and why that is the honest input.** The design's
contract asks the generator to transcribe a number it wrote and name the line it
read it on. Here the probe plays the generator, perfectly: for every number in
the draft whose value occurs somewhere in the instance's source procedure, the
annotation names the first line that holds it, with the unit as the DRAFT
rendered it. That is a correctly-annotated number by construction, so every
blocker the verifier raises over this set is a false one — the failure mode a
non-overridable check must not have. Numbers whose value occurs nowhere in the
source (57 of 430; melting points and ionic radii — parametric recall) cannot be
correctly annotated at all, are annotated `uncited`, and are excluded from the
denominator, exactly as §3.4 routes them at run time.

The denominator is therefore the 373 TRACEABLE numbers: the 365 whose (value,
unit) pair matches outright plus the 8 that name the right line and differ only
in unit rendering — the eight the synonym table exists for, and the eight that
made the naive matcher fire the kill condition at 2.1%.

Usage:  python3 benchmarks/expertlongbench/provenance_arm1.py
"""
from __future__ import annotations

import json
import math
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))

from crossaudit.dcl.framework import BLOCKER                    # noqa: E402
from crossaudit.dcl.numbers import check_number_source          # noqa: E402
from provenance_probe import (CORPUS_LOCAL, CORPUS_REL,         # noqa: E402
                              NUM, RUNS, SYNONYM)

#: The two paths the synthesised increment uses. In a live run these are the
#: committed `work/synthesis/RECIPE.md` and the artefact that cites it.
SOURCE_PATH = "work/synthesis/RECIPE.md"
DRAFT_PATH = "work/explanation.md"


def draft_pairs(text: str):
    """Every (value, unit, line) the probe's extractor sees in a draft."""
    out = []
    for m in NUM.finditer(text):
        unit = (m.group(2) or "").strip()
        out.append((m.group(1), SYNONYM.get(unit, unit),
                    text[:m.start()].count("\n") + 1))
    return out


def source_pairs(line: str):
    out = set()
    for m in NUM.finditer(line):
        unit = (m.group(2) or "").strip()
        out.add((m.group(1), SYNONYM.get(unit, unit)))
    return out


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval — the one that stays inside [0, 1] at k = 0,
    which is the case this measurement is most likely to land in."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def main() -> int:
    path = next((p for p in (os.environ.get("CROSSAUDIT_T03_CORPUS", ""),
                             CORPUS_LOCAL, CORPUS_REL) if p and os.path.exists(p)), "")
    if not path:
        print(f"corpus not found: fetch it into {CORPUS_REL}, or set "
              "CROSSAUDIT_T03_CORPUS to a checkout that has it")
        return 2
    corpus = {r["id"]: r for r in map(json.loads, open(path))}
    runs = os.path.expanduser(RUNS)

    instances = traceable = blocked = uncited = 0
    exact = exact_blocked = 0
    by_rule: dict[str, int] = {}
    examples: list[str] = []

    for name in sorted(os.listdir(runs)):
        key = "T03MaterialSEG-" + name.replace("T03MaterialSEG-", "").replace("__", "/")
        draft_file = os.path.join(runs, name, "armB.round1.md")
        row = corpus.get(key)
        if row is None or not os.path.exists(draft_file):
            continue
        instances += 1

        # The source procedure, as a file: blank lines dropped so a line number
        # in the annotation is a line number in the bytes the check reads.
        lines = [ln for ln in row["input"].split("\n") if ln.strip()]
        per_line = [source_pairs(ln) for ln in lines]
        values = {v for s in per_line for v, _ in s}
        source = "\n".join(lines) + "\n"

        draft = open(draft_file).read()
        rows, strict_rows = [], []
        for value, unit, at in draft_pairs(draft):
            owners = [i for i, s in enumerate(per_line) if (value, unit) in s]
            strict = bool(owners)
            if not owners and value in values:
                # Right line, unit rendered differently: still a correct
                # annotation, and the case the synonym table must absorb.
                owners = [i for i, s in enumerate(per_line)
                          if any(v == value for v, _ in s)]
            if not owners:
                uncited += 1
                continue                     # §3.4 routes these to the auditor
            annotation = {"v": value, "u": unit, "at": f"#L{at}",
                          "src": f"{SOURCE_PATH}#L{owners[0] + 1}"}
            rows.append(annotation)
            if strict:
                strict_rows.append(annotation)
        traceable += len(rows)
        exact += len(strict_rows)

        def run(annotations: list[dict]) -> list:
            fence = ("\n\n```crossaudit-numbers\n"
                     + json.dumps(annotations, ensure_ascii=False) + "\n```\n")
            files = {SOURCE_PATH: source.encode(),
                     DRAFT_PATH: (draft + fence).encode()}
            return [f for f in check_number_source(files) if f.severity == BLOCKER]

        exact_blocked += len(run(strict_rows))
        for f in run(rows):
            blocked += 1
            by_rule[f.rule] = by_rule.get(f.rule, 0) + 1
            if len(examples) < 8:
                examples.append(f"    {name}: {f.observation}")

    total = traceable + uncited
    rate = blocked / traceable if traceable else 0.0
    low, high = wilson(blocked, traceable)
    print(f"instances={instances} numbers={total} traceable={traceable} "
          f"uncited={uncited}")
    print(f"FALSE BLOCKERS {blocked}/{traceable} = {100 * rate:.2f}%  "
          f"(95% Wilson {100 * low:.2f}–{100 * high:.2f}%)")
    if by_rule:
        print("  by rule: " + ", ".join(f"{r}×{n}" for r, n in sorted(by_rule.items())))
    e_low, e_high = wilson(exact_blocked, exact)
    print(f"  of the {exact} whose (value, unit) pair matches outright: "
          f"{exact_blocked} blocked = {100 * exact_blocked / exact:.2f}% "
          f"(95% Wilson {100 * e_low:.2f}–{100 * e_high:.2f}%)")
    for line in examples:
        print(line)
    killed = rate > 0.02
    print(f"kill condition (>2%): {'FIRED' if killed else 'not fired'}")
    return 1 if killed else 0


if __name__ == "__main__":
    raise SystemExit(main())
