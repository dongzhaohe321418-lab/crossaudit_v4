"""Every rate in RESULTS-ARM6.md, from the committed records, with both registered intervals.

    python benchmarks/expertlongbench/study15/arm6_rates.py [--sheet <archive>/sheet/sheet-arm6.jsonl]

Wilson score intervals and a draft-clustered percentile bootstrap (seed 20261108, 10,000
resamples; a resample with an empty denominator is discarded and counted), as
`PREREGISTRATION-ARM6.md` inherits from Arm 4/5. Reads `rows-arm6.jsonl`,
`manifest-arm6.json` (per-draft numbers present and fence blocks) and `key-arm6.jsonl`; the
value-shape shares need the sheet's values, which are in the archive, not the repo.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED, REPS = 20261108, 10_000


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def draft_bootstrap(by_draft: dict[str, tuple[int, int]]) -> tuple[float, float, int]:
    """Percentile bootstrap resampling DRAFTS; (k, n) per draft; returns lo, hi, discarded."""
    drafts = list(by_draft)              # the records' order, as the report resamples them
    rng = random.Random(SEED)
    stats, discarded = [], 0
    for _ in range(REPS):
        k = n = 0
        for _ in range(len(drafts)):
            kk, nn = by_draft[drafts[rng.randrange(len(drafts))]]
            k += kk
            n += nn
        if n == 0:
            discarded += 1
            continue
        stats.append(k / n)
    stats.sort()
    # the same percentile index as provenance_arm4_report.cluster_bootstrap
    return stats[int(0.025 * (len(stats) - 1))], stats[int(0.975 * (len(stats) - 1))], discarded


ALL_DRAFTS: list[str] = []


def rate(name: str, rows) -> None:
    """rows: iterable of (draft, in_denominator, in_numerator); every one of the 33 drafts is a
    cluster, as in the report — a draft with no row in the denominator contributes nothing."""
    by = defaultdict(lambda: [0, 0])
    for d in ALL_DRAFTS:
        by[d] = [0, 0]
    k = n = 0
    for draft, in_d, in_k in rows:
        by.setdefault(draft, [0, 0])
        if not in_d:
            continue
        by[draft][1] += 1
        n += 1
        if in_k:
            by[draft][0] += 1
            k += 1
    lo, hi = wilson(k, n)
    blo, bhi, disc = draft_bootstrap({d: (v[0], v[1]) for d, v in by.items()})
    print(f"{name:52s} {k:4d}/{n:<4d} = {100 * k / n if n else float('nan'):6.2f}%  "
          f"Wilson {100 * lo:6.2f}–{100 * hi:6.2f}%  bootstrap {100 * blo:6.2f}–{100 * bhi:6.2f}%"
          + (f"  ({disc} discarded)" if disc else ""))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", default="")
    args = ap.parse_args()
    rows = [json.loads(l) for l in (HERE / "rows-arm6.jsonl").read_text().splitlines() if l.strip()]
    manifest = json.loads((HERE / "manifest-arm6.json").read_text())
    drafts = manifest["drafts"]
    ALL_DRAFTS[:] = [d["instance"] for d in drafts]
    print(f"rows {len(rows)}; drafts {len(drafts)}; seed {SEED}, {REPS} resamples\n")

    # the predicates are provenance_arm4_report.py's, so its numbers reproduce here
    addressed = lambda r: r["src_kind"] not in ("uncited", "governed")
    blockable = lambda r: addressed(r) and r["severity"] != "ADVISORY"
    located = lambda r: bool(r["gold_label"])            # the 19 sheet rows
    blocked = lambda r: r["severity"] == "BLOCKER"
    passed = lambda r: r["severity"] == "PASS"

    # primary — on located rows: false blocks (gold C and blocked) over gold C+N rows
    # §8g: false blocks over the located rows whose quotation genuinely contains the pair
    # (gold C) — the two gold-N blocks are right and outside the denominator
    rate("§8g primary: wrong blocks / located gold-C rows",
         [(r["instance"], located(r) and r["gold_label"] == "C", located(r) and blocked(r) and r["gold_label"] == "C") for r in rows])
    rate("pass sample: correct passes / passes labelled",
         [(r["instance"], located(r) and not blocked(r), located(r) and not blocked(r) and r["gold_label"] == "C") for r in rows])
    rate("H6b: cross-line (Q1) / addressed rows",
         [(r["instance"], addressed(r), r["mechanism"] == "Q1") for r in rows])
    rate("quote-absent (Q2) / addressed rows",
         [(r["instance"], addressed(r), r["mechanism"] == "Q2") for r in rows])
    rate("Q1 rows with the pair elsewhere in the named file",
         [(r["instance"], r["mechanism"] == "Q1", r["mechanism"] == "Q1" and bool(r["pair_in_named_file"])) for r in rows])
    rate("Q2 rows with the pair elsewhere in the named file",
         [(r["instance"], r["mechanism"] == "Q2", r["mechanism"] == "Q2" and bool(r["pair_in_named_file"])) for r in rows])
    rate("Q1+Q2 rows with the pair elsewhere in the named file",
         [(r["instance"], r["mechanism"] in ("Q1", "Q2"), r["mechanism"] in ("Q1", "Q2") and bool(r["pair_in_named_file"])) for r in rows])
    rate("resolved (PASS) / addressed rows",
         [(r["instance"], addressed(r), passed(r)) for r in rows])
    rate("resolved (PASS) / blockable rows",
         [(r["instance"], blockable(r), passed(r)) for r in rows])
    rate("located (a quotation found on one line) / addressed rows",
         [(r["instance"], addressed(r), bool(r["resolved_location"])) for r in rows])
    rate("ambiguous (advisory) / addressed rows",
         [(r["instance"], addressed(r), r["reason"] == "ambiguous") for r in rows])
    rate("uncited / all rows", [(r["instance"], True, r["src_kind"] == "uncited") for r in rows])
    rate("unit-bearing / all rows", [(r["instance"], True, r["u_len"] > 0) for r in rows])
    rate("unit shortened / located rows",
         [(r["instance"], bool(r["resolved_location"]), bool(r["unit_shortened"])) for r in rows])
    print()
    # per-draft: annotation rate and fence share, over all 33 drafts
    rate("annotation rate: rows / numbers present (33 drafts)",
         [(d["instance"], True, True) for d in drafts for _ in range(len([r for r in rows if r["instance"] == d["instance"]]))]
         + [(d["instance"], True, False) for d in drafts
            for _ in range(d["numbers_present"] - len([r for r in rows if r["instance"] == d["instance"]]))])
    rate("drafts with a fence / drafts",
         [(d["instance"], True, d["fence_blocks"] > 0) for d in drafts])
    fenced = [d for d in drafts if d["fence_blocks"] > 0]
    per = Counter(r["instance"] for r in rows)
    counts = sorted(per.get(d["instance"], 0) for d in fenced)
    print(f"fenced drafts {len(fenced)}: parsed rows per fenced draft min {counts[0]} max {counts[-1]} "
          f"median {counts[len(counts) // 2]}; drafts with ≥1 row {sum(1 for c in counts if c)}")
    import hashlib
    names = {hashlib.sha256(u.encode()).hexdigest(): u for u in ("$", "%", "days", "USD", "day", "years")}
    print("unit kinds among unit-bearing rows (by hash of the unit): "
          + ", ".join(f"{k!r}: {v}" for k, v in Counter(
              names.get(r["u_sha256"], r["u_sha256"][:8]) for r in rows if r["u_len"] > 0).most_common()))
    print()
    if args.sheet:
        sheet = {x["id"]: x for x in (json.loads(l) for l in Path(args.sheet).read_text().splitlines() if l.strip())}
        key = {x["id"]: x for x in (json.loads(l) for l in (HERE / "key-arm6.jsonl").read_text().splitlines() if l.strip())}
        def shape(x: dict) -> str:
            """The value's shape from its unit and its immediate context in the quotation.

            The sheet's value is normalised (no thousands separators), so the quotation is
            searched for the value as written with separators too. One row's value is
            written in words in its quotation (the M1b row): its context is read from the
            words around it, which name a span of days.
            """
            v, u, t = x["v"], x["u"], x["text"]
            if u == "%":
                return "percentage"
            if re.fullmatch(r"(19|20)\d\d", v):
                return "year"
            forms = [v]
            if re.fullmatch(r"\d+(\.\d+)?", v):
                whole, _, frac = v.partition(".")
                forms.append(f"{int(whole):,}" + (f".{frac}" if frac else ""))
            i = next((t.find(f) for f in forms if f in t), -1)
            before = t[max(0, i - 2):i] if i >= 0 else ""
            after = t[i + len(next(f for f in forms if f in t)):][:16].lower() if i >= 0 else t.lower()
            if u == "$" or "$" in before or re.fullmatch(r"\d+\.\d\d", v):
                return "dollar amount"
            if u == "days" or re.search(r"\bdays?\b", after):
                return "duration in days"
            return "count"
        shapes = defaultdict(list)
        for sid, x in sheet.items():
            shapes[shape(x)].append(key[sid]["instance"])
        print("value shapes on the 19-item sheet (rule in `shape()`):")
        for name in ("year", "duration in days", "dollar amount", "count", "percentage"):
            rate(f"  {name} / sheet items",
                 [(key[sid]["instance"], True, shape(x) == name) for sid, x in sheet.items()])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
