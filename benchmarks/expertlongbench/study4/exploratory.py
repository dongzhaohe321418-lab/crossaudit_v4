"""EXPLORATORY. Study 4's Phase-1 diagnosis of the revision defect.

Everything here is computed on **study 3's** run directories — data gathered to
answer a different question — and was chosen after looking at it. Per
`benchmarks/EXPERIMENT_RECORD.md` #1 that makes it exploratory, and it is
labelled so wherever it appears. It generated the hypothesis study 4 then tested
prospectively; it does not test it.

Correlations carry n and a BCa bootstrap 95% interval. The 25% threshold is
*fitted here*, on these 25 revisions, and is therefore a description of this
data rather than a validated cutoff.
"""
from __future__ import annotations

import difflib
import json
import math
import random
import re
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyse import BOOT_SEED, BOOT_N  # noqa: E402

STUDY3 = {
    "S": "wt-control/benchmarks/expertlongbench/runs/armS-shipped",
    "R": "wt-control/benchmarks/expertlongbench/runs/armR-rubric",
    "X": "wt-split/benchmarks/expertlongbench/runs/armX-split",
}


def pearson(xs, ys):
    mx, my = st.mean(xs), st.mean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    den = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
    return num / den if den else float("nan")


def pearson_ci(xs, ys):
    n = len(xs)
    rng = random.Random(BOOT_SEED)
    boots = []
    for _ in range(BOOT_N):
        idx = [rng.randrange(n) for _ in range(n)]
        try:
            boots.append(pearson([xs[i] for i in idx], [ys[i] for i in idx]))
        except (ZeroDivisionError, ValueError):
            pass
    boots = sorted(b for b in boots if not math.isnan(b))
    return boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots))]


def blocks(t):
    return [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]


def collect(base: Path):
    rows = []
    for arm, rel in STUDY3.items():
        d = base / rel
        if not (d / "instances").exists():
            continue
        for inst in sorted((d / "instances").iterdir()):
            b = json.loads((inst / "record.json").read_text())["arms"].get("B")
            if not b or not b.get("revision"):
                continue
            rv = b["revision"]
            pre_p = inst / f"armB.round{rv['pre_round']}.md"
            post_p = inst / f"armB.round{rv['post_round']}.md"
            pre = pre_p.read_text()
            post = post_p.read_text() if post_p.exists() else (inst / "armB.output.md").read_text()
            pb, qb = blocks(pre), blocks(post)
            sm = difflib.SequenceMatcher(None, pre, post, autojunk=False)
            steps = []
            for r in range(rv["pre_round"], rv["post_round"]):
                a, c = inst / f"armB.round{r}.md", inst / f"armB.round{r+1}.md"
                if not a.exists():
                    continue
                w0 = len(a.read_text().split())
                w1 = len((c.read_text() if c.exists() else (inst / "armB.output.md").read_text()).split())
                if w0:
                    steps.append((w1 - w0) / w0)
            rows.append({
                "arm": arm, "inst": inst.name,
                "delta": rv["delta_f1"],
                "fixed": len(rv["items_fixed"]), "broken": len(rv["items_broken"]),
                "char_preserved": sum(bl.size for bl in sm.get_matching_blocks()) / max(len(pre), 1),
                "max_growth": max(steps) if steps else 0.0,
                "n_findings": len(b["findings"]),
                "blocks_pre": len(pb),
                "blocks_kept": len(set(pb) & set(qb)),
            })
    return rows


def main(base):
    base = Path(base)
    rows = collect(base)
    print(f"EXPLORATORY — study 3 revisions, n = {len(rows)}\n")
    ys = [r["delta"] for r in rows]
    for field, name in (("char_preserved", "characters of the round-one draft preserved"),
                        ("max_growth", "largest per-round net word growth"),
                        ("n_findings", "number of findings")):
        xs = [r[field] for r in rows]
        r = pearson(xs, ys)
        lo, hi = pearson_ci(xs, ys)
        print(f"  r({name}, revision ΔF1) = {r:+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]  n={len(xs)}")
    print()
    tot_pre = sum(r["blocks_pre"] for r in rows)
    tot_kept = sum(r["blocks_kept"] for r in rows)
    print(f"  paragraph blocks: {tot_kept}/{tot_pre} = {100*tot_kept/tot_pre:.1f}% survive byte-identical")
    print(f"  mean characters preserved: {st.mean(r['char_preserved'] for r in rows):.3f}")
    print(f"  revisions that grew the deliverable: "
          f"{sum(1 for r in rows if r['max_growth'] > 0)}/{len(rows)}")
    print()
    print("  threshold sweep on largest per-round net word growth (FITTED ON THIS DATA):")
    for thr in (0.10, 0.15, 0.20, 0.25, 0.30, 0.40):
        lo_g = [r for r in rows if r["max_growth"] <= thr]
        hi_g = [r for r in rows if r["max_growth"] > thr]
        f = lambda g: (len(g), 100 * st.mean(r["delta"] for r in g) if g else 0,
                       sum(r["fixed"] for r in g), sum(r["broken"] for r in g))
        a, c = f(lo_g), f(hi_g)
        print(f"    <= {thr:.0%}: n={a[0]:>2} mean {a[1]:+6.2f} fixed {a[2]} broken {a[3]}"
              f"   |  > {thr:.0%}: n={c[0]:>2} mean {c[1]:+6.2f} fixed {c[2]} broken {c[3]}")
    print()
    print("  counterfactual replay of the 25% screen (EXPLORATORY; says which revisions")
    print("  it would have refused, NOT what the re-ask would then have produced):")
    fired = [r for r in rows if r["max_growth"] > 0.25]
    rest = [r for r in rows if r["max_growth"] <= 0.25]
    print(f"    would refuse {len(fired)}/{len(rows)} revisions, carrying "
          f"{sum(r['fixed'] for r in fired)} fixes and {sum(r['broken'] for r in fired)} breaks")
    print(f"    would leave  {len(rest)}/{len(rows)} revisions, carrying "
          f"{sum(r['fixed'] for r in rest)} fixes and {sum(r['broken'] for r in rest)} breaks, "
          f"mean {100*st.mean(r['delta'] for r in rest):+.2f} F1  <-- the floor the treatment must beat")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1
         else "/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad")
