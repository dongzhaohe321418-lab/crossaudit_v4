"""Arm 1 of `docs/design/PROVENANCE_CHECKS.md` §6 — model-free, $0, ~2 seconds.

Measures, over the 16 already-generated T03 drafts in the archived run data:

  * how many draft numbers trace to the instance's source procedure, and how
    many fail only on unit rendering (the case the synonym table must absorb);
  * the **coincidental-pass rate** of a wrong locator — the number that decides
    whether a provenance annotation may name a file or must name a span.

Nothing here calls a model and nothing here is part of the product. Reads the
gitignored corpus and the read-only archive; writes nothing.

Expected output (seed 20261104):

    n=430 traced=365 unit-clash=8 absent=57
    file-scoped 596/2150=27.7%  line-scoped 0/1825=0.0% (zero by construction)

**The line-scoped number is zero by construction** (CORRECTIONS #32): the owner
lines are every line this reader finds the pair in, they are excluded, and the
rest are tested with the same reader. Arm 1's drafts carry no annotations, so
this file has no independent owner to use; the real line-scoped instrument is
`study13/probe.py`'s P2, whose owner is the generator's own quotation (0.54%).
The file-scoped number is a measurement and stands.
"""
from __future__ import annotations

import json
import os
import random
import re

#: The corpus is gitignored (CC BY-NC-SA, not redistributed): resolve it beside
#: this file first, then fall back to the working directory, so the probe runs
#: from whichever checkout actually fetched it.
CORPUS_REL = "benchmarks/expertlongbench/data/T03MaterialSEG.jsonl"
CORPUS_LOCAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "data", "T03MaterialSEG.jsonl")
RUNS = "~/Documents/Crossaudit/study-data/wt-revision-runs/armT-scoped/instances"
SEED = 20261104
DRAWS = 5

#: A number and, when it has one, the unit token immediately after it.
NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*"
                 r"(°C|h\b|hours?|min(?:utes)?\b|wt ?%|mol ?%|%|K\b|MPa|mL|g\b"
                 r"|mg\b|nm|µm|μm|Å|sccm|rpm)?")
#: The unit-synonym table §3.1 calls load-bearing. Without it, 8 of 430 draft
#: numbers fail while naming the right line — spurious non-overridable blockers.
SYNONYM = {"hours": "h", "hour": "h", "minutes": "min", "minute": "min",
           "wt %": "wt%", "mol %": "mol%", "µm": "μm"}


def pairs(text: str) -> list[tuple[str, str]]:
    out = []
    for m in NUM.finditer(text):
        unit = (m.group(2) or "").strip()
        out.append((m.group(1), SYNONYM.get(unit, unit)))
    return out


def main() -> int:
    path = next((p for p in (os.environ.get("CROSSAUDIT_T03_CORPUS", ""),
                             CORPUS_LOCAL, CORPUS_REL) if p and os.path.exists(p)), "")
    if not path:
        print(f"corpus not found: fetch it into {CORPUS_REL}, or set "
              "CROSSAUDIT_T03_CORPUS to a checkout that has it")
        return 2
    corpus = {r["id"]: r for r in map(json.loads, open(path))}
    runs = os.path.expanduser(RUNS)
    rng = random.Random(SEED)
    ids = sorted(corpus)
    total = traced = clash = absent = 0
    coin_file = draws_file = coin_line = draws_line = 0

    for name in sorted(os.listdir(runs)):
        key = "T03MaterialSEG-" + name.replace("T03MaterialSEG-", "").replace("__", "/")
        row = corpus.get(key)
        draft = os.path.join(runs, name, "armB.round1.md")
        if row is None or not os.path.exists(draft):
            continue
        lines = [ln for ln in row["input"].split("\n") if ln.strip()]
        per_line = [set(pairs(ln)) for ln in lines]
        whole = set().union(*per_line)
        values = {v for v, _ in whole}

        for value, unit in pairs(open(draft).read()):
            total += 1
            if (value, unit) in whole:
                traced += 1
            elif value in values:
                clash += 1          # right line, unit rendered differently
            else:
                absent += 1         # no source at all: parametric domain recall
            # A wrong FILE: does it happen to contain the same pair?
            for other in rng.sample([i for i in ids if i != key], DRAWS):
                draws_file += 1
                coin_file += (value, unit) in set(pairs(corpus[other]["input"]))
            # A wrong LINE of the right file: same question, span-scoped.
            if (value, unit) in whole:
                owners = [i for i, s in enumerate(per_line) if (value, unit) in s]
                others = [i for i in range(len(lines)) if i not in owners]
                for i in rng.sample(others, min(DRAWS, len(others))):
                    draws_line += 1
                    coin_line += (value, unit) in per_line[i]

    print(f"n={total} traced={traced} unit-clash={clash} absent={absent}")
    print(f"file-scoped {coin_file}/{draws_file}={100 * coin_file / draws_file:.1f}%  "
          f"line-scoped {coin_line}/{draws_line}={100 * coin_line / draws_line:.1f}% "
          "(zero by construction, CORRECTIONS #32)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
