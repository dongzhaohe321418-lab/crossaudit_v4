#!/usr/bin/env python3
"""E3's own probe — study 13 §3a. Model-free, $0, seconds.

Reads the gitignored T03 corpus (`CROSSAUDIT_T03_CORPUS`, or the checkout's copy)
and the two archived draft sets; writes counts and formula-token shapes only.

  P1  every whitespace-delimited token in every source procedure that the shipped
      `_SUBSCRIPT` hook reads, with the value it yields — for classification by hand
  P2  the line-scoped coincidental-containment rate with the owner line named by
      the generator's own quotation (Arm 4's 26 annotated drafts; seed 20261104,
      five wrong-line draws per traced pair, and five draws from other sources),
      under base (E3 off) and shipped; all pairs and empty-unit pairs alone
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


FENCE = re.compile(r"```crossaudit-numbers\s*\n(.*?)\n```", re.S)


def annotated_rows(draft_text: str):
    for block in FENCE.findall(draft_text):
        try:
            rows = json.loads(block)
        except ValueError:
            continue
        for row in rows:
            src = row.get("src") or {}
            if isinstance(src, dict) and src.get("quote") and isinstance(row.get("v"), str):
                yield row["v"], row.get("u") or "", src["quote"]


def p2_rates(seed: int = P.SEED, draws: int = P.DRAWS):
    """The line-scoped coincidental-containment rate, with the OWNER line named by
    the generator's own quotation and not by the matcher. The third review found
    the first version excluding every line the matcher accepted and then testing
    the rest with the same matcher — zero by construction. Here a traced pair is
    one whose quoted line contains it; the wrong lines are the other non-empty
    lines of the same source (five draws), and, file-scoped, five lines of other
    instances' sources; a draw that contains the pair is a coincidence a wrong
    citation would have enjoyed. Only the 26 Arm 4 drafts carry annotations."""
    rng = random.Random(seed)
    root = os.path.expanduser(DRAFTS[1][1])
    sources = {}
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name, "project/work/synthesis/RECIPE.md")
        if os.path.exists(path):
            sources[name] = [ln for ln in open(path, encoding="utf-8").read().split("\n") if ln.strip()]
    out = {k: [0, 0] for k in ("line", "line-empty", "file", "file-empty")}
    n_rows = n_traced = n_unlocated = 0
    for name, lines in sources.items():
        draft = os.path.join(root, name, "project/work/synthesis/explanation.md")
        if not os.path.exists(draft):
            continue
        for v, u, quote in annotated_rows(open(draft, encoding="utf-8").read()):
            n_rows += 1
            owners = [i for i, ln in enumerate(lines) if quote in ln]
            if not owners:
                n_unlocated += 1
                continue
            if not any(N.contains_pair(lines[i], v, u) for i in owners):
                continue
            n_traced += 1
            others = [i for i in range(len(lines)) if i not in owners]
            for i in rng.sample(others, min(draws, len(others))):
                hit = N.contains_pair(lines[i], v, u)
                out["line"][1] += 1; out["line"][0] += hit
                if u == "":
                    out["line-empty"][1] += 1; out["line-empty"][0] += hit
            for other in rng.sample([k for k in sources if k != name], draws):
                ln = rng.choice(sources[other])
                hit = N.contains_pair(ln, v, u)
                out["file"][1] += 1; out["file"][0] += hit
                if u == "":
                    out["file-empty"][1] += 1; out["file-empty"][0] += hit
    return n_rows, n_traced, n_unlocated, out


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

    n_rows, n_traced, n_unlocated, rates = p2_rates()
    def pct(k):
        c, n = rates[k]
        return f"{c}/{n}={100 * c / max(1, n):.2f}%"
    print(f"P2  Arm 4 annotated rows {n_rows}; quote unlocated {n_unlocated}; traced by the "
          f"generator's own quote {n_traced}; coincidental containment, wrong line of the "
          f"right source: all {pct('line')}  empty-unit {pct('line-empty')}; a line of a "
          f"wrong source: all {pct('file')}  empty-unit {pct('file-empty')}")

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
