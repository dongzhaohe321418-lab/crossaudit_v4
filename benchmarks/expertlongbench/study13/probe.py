#!/usr/bin/env python3
"""E3's own probe — study 13 §3a. Model-free, $0, seconds.

Reads the gitignored T03 corpus (`CROSSAUDIT_T03_CORPUS`, or the checkout's copy)
and the two archived draft sets; writes counts and formula-token shapes only.

  P1  every whitespace-delimited token in every source procedure that the shipped
      `_SUBSCRIPT` hook reads, with the value it yields — for classification by hand
  P2  `provenance_probe.py`'s line-scoped coincidental-containment instrument
      (seed 20261104, five wrong-line draws per traced pair), with `contains_pair`
      as the containment test, under base (E3 off) and shipped; all pairs and
      empty-unit pairs alone
  P3  subscript decoys: values E3 reads from more than one distinct formula token

    PYTHONPATH=src .venv/bin/python benchmarks/expertlongbench/study13/probe.py [--config base|shipped]
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent.parent / "src"))
sys.path.insert(0, str(HERE.parent))

from crossaudit.dcl import numbers as N                     # noqa: E402
import provenance_probe as P                                # noqa: E402

DRAFTS = [
    ("armT-scoped", "~/Documents/Crossaudit/study-data/wt-revision-runs/armT-scoped/instances",
     "armB.round1.md", ""),
    ("wt-arm4-runs", "~/Documents/Crossaudit/study-data/wt-arm4-runs/arm4/instances",
     "project/work/synthesis/RECIPE.md", "__S"),
]


def corpus_path() -> str:
    for p in (os.environ.get("CROSSAUDIT_T03_CORPUS", ""), P.CORPUS_LOCAL, P.CORPUS_REL,
              str(HERE.parent / "data" / "T03MaterialSEG.jsonl")):
        if p and os.path.exists(p):
            return p
    raise SystemExit("corpus not found")


def instance_key(name: str, suffix: str) -> str:
    stem = name[: -len(suffix)] if suffix and name.endswith(suffix) else name
    return "T03MaterialSEG-" + stem.replace("T03MaterialSEG-", "").replace("__", "/")


def p1_tokens(corpus: dict) -> dict[str, set[str]]:
    """token -> values E3 reads from it that the ordinary scan does not, over
    every whitespace-delimited token of every source procedure; a token is a
    formula as the check reads it, sentence punctuation stripped."""
    read: dict[str, set[str]] = defaultdict(set)
    on, off = N._SUBSCRIPT, re.compile(r"(?!x)x")
    for row in corpus.values():
        for tok in row["input"].split():
            for m in on.finditer(tok):
                v = m.group(1)
                N._SUBSCRIPT = off
                base = N.contains_pair(tok, v, "")
                N._SUBSCRIPT = on
                if not base and N.contains_pair(tok, v, ""):
                    # the check strips sentence punctuation; so does the count
                    read[tok.rstrip(N._TRAILING_PUNCTUATION)].add(v)
    return read


def p2_rates(corpus: dict, seed: int = P.SEED, draws: int = P.DRAWS):
    rng = random.Random(seed)
    out = {"all": [0, 0], "empty": [0, 0]}
    n_pairs = 0
    for label, root, draft_rel, suffix in DRAFTS:
        root = os.path.expanduser(root)
        for name in sorted(os.listdir(root)):
            row = corpus.get(instance_key(name, suffix))
            draft = os.path.join(root, name, draft_rel)
            if row is None or not os.path.exists(draft):
                continue
            lines = [ln for ln in row["input"].split("\n") if ln.strip()]
            for value, unit in P.pairs(open(draft).read()):
                n_pairs += 1
                owners = [i for i, ln in enumerate(lines) if N.contains_pair(ln, value, unit)]
                if not owners:
                    continue
                others = [i for i in range(len(lines)) if i not in owners]
                for i in rng.sample(others, min(draws, len(others))):
                    hit = N.contains_pair(lines[i], value, unit)
                    for k in ("all",) + (("empty",) if unit == "" else ()):
                        out[k][1] += 1
                        out[k][0] += hit
    return n_pairs, out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", choices=["shipped", "base"], default="shipped")
    args = ap.parse_args(argv)
    if args.config == "base":
        N._SUBSCRIPT = re.compile(r"(?!x)x")
    corpus = {r["id"]: r for r in map(json.loads, open(corpus_path()))}
    print(f"config {args.config}   corpus instances {len(corpus)}")

    read = p1_tokens(corpus)
    print(f"P1  tokens E3 reads: {len(read)} distinct, "
          f"{sum(len(v) for v in read.values())} (token, value) readings")
    for tok in sorted(read):
        print(f"    {tok}  <- {sorted(read[tok], key=float)}")

    n_pairs, rates = p2_rates(corpus)
    print(f"P2  draft pairs {n_pairs}; line-scoped coincidental containment: "
          f"all {rates['all'][0]}/{rates['all'][1]}"
          f"={100 * rates['all'][0] / max(1, rates['all'][1]):.2f}%   "
          f"empty-unit {rates['empty'][0]}/{rates['empty'][1]}"
          f"={100 * rates['empty'][0] / max(1, rates['empty'][1]):.2f}%")

    by_value: dict[str, set[str]] = defaultdict(set)
    for tok, vals in read.items():
        for v in vals:
            by_value[N.normalise_number(v)].add(tok)
    decoys = {v: toks for v, toks in by_value.items() if len(toks) > 1}
    print(f"P3  values read from more than one distinct formula token: {len(decoys)} "
          f"of {len(by_value)}")
    for v in sorted(decoys, key=float):
        print(f"    {v}: {len(decoys[v])} tokens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
