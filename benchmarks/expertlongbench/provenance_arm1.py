"""Arm 1 of `docs/design/PROVENANCE_CHECKS.md` §6, run against the SHIPPED check.

`provenance_probe.py` measured the *contract* — whether a locator must name a
span — with a matcher written for the measurement. This runs the code that
actually ships (`crossaudit.dcl.numbers.check_number_source`) over the same 16
archived T03 drafts, with the annotations the probe derives, and reports the
preregistered primary outcome:

    the BLOCK RATE ON PAIR-MATCHED CITATIONS — of numbers whose extracted
    (value, unit) pair does occur on the line the harness names, the fraction
    the verifier blocks. Kill condition: > 2%. Read it as an UPPER BOUND on the
    verifier's false-blocker rate: the stratum contains annotations the probe
    itself got wrong, and those are counted against the checker rather than
    excused.

No model is called, no key is read, nothing is written. ~2 seconds, $0.

**How an annotation is derived, and what the strata mean.** The design's
contract asks the generator to transcribe a number it wrote and name the line it
read it on. Here the probe plays the generator: for every number in the draft,
the harness looks for the same number in the instance's source procedure and
names the first line that holds it, with the value and unit as the DRAFT wrote
them, unnormalised. Three outcomes, reported separately because they are not the
same claim:

* **pair-matched** — the pair the PROBE extracted from the draft occurs on the
  named line. **This is the primary denominator and the one the >2% kill
  condition is read against.** It is not "correct by construction", and calling
  it that was the last thing wrong with this script: the probe's `NUM` has a
  closed unit alternation, so on a ramp rate written `°C/min` it captures `°C`
  and the annotation it derives is not what the draft wrote. Every block in this
  stratum on the current corpus is one of those, and the count of them is
  printed beside the rate. They stay in the numerator — the instrument's error
  is not the checker's credit — but they are reported as what they are:
  harness-annotation errors, not demonstrated verifier false blockers.
* **value-only** — the value occurs on that line and no rendering of its unit
  does. The harness picked the line by value alone, so these are DERIVED
  annotations, not established literal-pair citations: finding the same number
  somewhere does not establish that the unit merely reads differently. A blocker
  here may well be correct, so they are reported as their own stratum with the
  source line printed beside each one, never folded into the primary rate.
* **uncited** — the value occurs nowhere in the source (57 of 430; melting
  points and ionic radii, parametric recall). Excluded, exactly as §3.4 routes
  them at run time.

An earlier version of this script reported pair-matched and value-only together
as "373 traceable" and called every block over them a false blocker. That
overclaimed: it counted a `1 %` sodium excess cited against a source line stating
a `1.01:1` molar ratio — a DERIVED percentage, which §3.1 says the check must not
attempt and §3.4 routes to `uncited` — as evidence against the checker.

Usage:  python3 benchmarks/expertlongbench/provenance_arm1.py
"""
from __future__ import annotations

import json
import math
import os
import re
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


#: A character that continues a unit token past where the probe's fixed
#: alternation stops. `NUM` knows `°C` and not `°C/min`, so on a ramp rate it
#: captures `("5", "°C")` and the annotation it derives is NOT what the draft
#: wrote. That is an instrument limit, and it is measured rather than corrected:
#: rebuilding the annotation with the product's own unit grammar would be
#: feeding the checker its own reading and calling the agreement a result.
_CONTINUES = re.compile(r"[/·⋅∙^A-Za-zµμ°ÅΩ]")


def draft_pairs(text: str):
    """Every (value, unit-as-written, line) the probe's extractor sees.

    The unit is NOT folded through the synonym table here. The contract asks the
    generator to transcribe the characters it wrote, so an annotation carrying
    `"hours"` where the draft says hours is the input this measurement is about;
    normalising first would test the harness's rendering rather than the
    product's, and would quietly hide any asymmetry between the two tables.
    """
    out = []
    for m in NUM.finditer(text):
        truncated = bool(m.group(2)) and bool(_CONTINUES.match(text[m.end():m.end() + 1]))
        out.append((m.group(1), (m.group(2) or "").strip(),
                    text[:m.start()].count("\n") + 1, truncated))
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

    instances = uncited = 0
    exact = exact_blocked = derived = derived_blocked = exact_truncated = 0
    by_rule: dict[str, int] = {}
    examples: list[str] = []
    derived_examples: list[str] = []

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
        pair_rows, value_rows, truncated_at = [], [], set()
        for value, unit, at, truncated in draft_pairs(draft):
            folded = SYNONYM.get(unit, unit)
            owners = [i for i, s in enumerate(per_line) if (value, folded) in s]
            stratum = "pair"
            if not owners and value in values:
                # The value is on the line and no rendering of the unit is. The
                # harness picks the line by VALUE ALONE here, so these are
                # DERIVED annotations, not established literal-pair citations,
                # and they are reported as their own stratum rather than folded
                # into the primary denominator. Finding the same number does not
                # establish that the unit merely reads differently.
                owners = [i for i, s in enumerate(per_line)
                          if any(v == value for v, _ in s)]
                stratum = "value-only"
            if not owners:
                uncited += 1
                continue                     # §3.4 routes these to the auditor
            annotation = {"v": value, "u": unit, "at": f"#L{at}",
                          "src": f"{SOURCE_PATH}#L{owners[0] + 1}"}
            if truncated and stratum == "pair":
                truncated_at.add((at, value, unit))
            (pair_rows if stratum == "pair" else value_rows).append(annotation)
        exact += len(pair_rows)
        derived += len(value_rows)

        def run(annotations: list[dict]) -> list:
            fence = ("\n\n```crossaudit-numbers\n"
                     + json.dumps(annotations, ensure_ascii=False) + "\n```\n")
            files = {SOURCE_PATH: source.encode(),
                     DRAFT_PATH: (draft + fence).encode()}
            return [f for f in check_number_source(files) if f.severity == BLOCKER]

        for f in run(pair_rows):
            exact_blocked += 1
            at = re.search(r"line (\d+)", f.observation)
            if at and any(str(a) == at.group(1) for a, _v, _u in truncated_at):
                exact_truncated += 1
            by_rule[f.rule] = by_rule.get(f.rule, 0) + 1
            if len(examples) < 8:
                examples.append(f"    [pair-matched] {name}: {f.observation}")
        for f in run(value_rows):
            derived_blocked += 1
            if len(derived_examples) < 8:
                # Print the line the harness named, so the reader can see what
                # the block actually was rather than take "false blocker" on
                # trust. Both shapes in this corpus are §3.1's "where
                # determinism ends" — a source stating the value in another
                # form — and the design routes them to `uncited`.
                named = re.search(r":(\d+)", f.observation.split(" — ")[0])
                cited = lines[int(named.group(1)) - 1][:96] if named else ""
                derived_examples.append(
                    f"    [value-only] {name}: {f.observation}\n"
                    f"                 source line reads: {cited!r}")

    total = exact + derived + uncited
    rate = exact_blocked / exact if exact else 0.0
    low, high = wilson(exact_blocked, exact)
    print(f"instances={instances} numbers={total}")
    print(f"  pair-matched  {exact:4d}   the pair the PROBE extracted occurs on "
          f"the named line")
    print(f"  value-only    {derived:4d}   the value occurs there and no rendering "
          f"of the unit does — DERIVED")
    print(f"  uncited       {uncited:4d}   the value occurs nowhere in the source; "
          f"§3.4 routes these to the auditor")
    print()
    print(f"PRIMARY — blocked, of pair-matched citations: "
          f"{exact_blocked}/{exact} = {100 * rate:.2f}%  "
          f"(95% Wilson {100 * low:.2f}–{100 * high:.2f}%)")
    print("  An UPPER BOUND on the verifier's false-blocker rate, not a "
          "measurement of it.")
    d_rate = derived_blocked / derived if derived else 0.0
    d_low, d_high = wilson(derived_blocked, derived)
    print(f"SECONDARY — blocked, of the DERIVED value-only stratum: "
          f"{derived_blocked}/{derived} = {100 * d_rate:.2f}%  "
          f"(95% Wilson {100 * d_low:.2f}–{100 * d_high:.2f}%)")
    print("  Also not established false blockers. The harness chose their line "
          "by value alone,")
    print("  so a block here can mean the citation was wrong, and each one below "
          "says which.")
    print(f"  of those {exact_blocked}, {exact_truncated} are HARNESS-ANNOTATION "
          f"ERRORS: the draft's own text continues")
    print("  the unit past the probe's fixed alternation (a ramp rate written "
          "°C/min, captured as °C),")
    print("  so the annotation is the harness's transcription and not the "
          "draft's. Left in the numerator;")
    print("  correcting it with the product's own unit grammar would be feeding "
          "the checker its own reading.")
    if by_rule:
        print("  primary by rule: "
              + ", ".join(f"{r}×{n}" for r, n in sorted(by_rule.items())))
    for line in examples + derived_examples:
        print(line)
    killed = rate > 0.02
    print(f"kill condition (>2% on the primary denominator): "
          f"{'FIRED' if killed else 'not fired'}")
    return 1 if killed else 0


if __name__ == "__main__":
    raise SystemExit(main())
