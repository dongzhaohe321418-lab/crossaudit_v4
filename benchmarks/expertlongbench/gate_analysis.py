"""Oracle-gate replay over the archived revision runs. Zero model calls.

What this answers
-----------------
1. **The gate.** Every round of every arm is already CLEAR-scored. Simulate an
   exogenous gate that rejects a revision whose post-revision CLEAR F1 is below
   the text it replaces, and recompute each arm's final F1. Reported as an
   intention-to-treat contrast over **every assigned instance**, never over the
   subset that happened to revise.
2. **Preservation.** Per *transition*, how many checklist items the revision
   fixed, how many it broke, and how many it left alone -- the RARR-style
   attribution/preservation split that a net F1 delta hides.
3. **Implementability.** Whether anything a running product can see (round
   index, finding count, which rule fired, growth in length) separates the
   harmful transitions from the rest.

Analysis rules this script is built to obey (see ``benchmarks/CORRECTIONS.md``)
------------------------------------------------------------------------------
* The primary unit is the **instance**, and the primary population is every
  instance assigned to the arm. Nothing is conditioned on "a revision occurred",
  which is a post-treatment variable. The conditional view is computed too and
  is labelled exploratory wherever it is printed.
* Where the unit is the **transition** it is named as such. A transition is one
  round-k to round-k+1 step, not one instance.
* Arms are never pooled into a headline. Each arm is reported on its own. A
  pooled line is printed only with a bootstrap clustered on source sample id,
  and is labelled secondary.
* Any bootstrap interval whose sample has no sign change is flagged: a
  percentile bootstrap over same-signed values cannot resample across zero, so
  its bound excludes zero mechanically rather than empirically.

Usage::

    python benchmarks/expertlongbench/gate_analysis.py \
        --out benchmarks/expertlongbench/records/gate  <run-dir> [<run-dir> ...]

Input is a run directory containing ``results.json`` (the archived study-data
tree). Only scores, counts, ids and text *lengths* are read; no corpus text and
no model output text leaves this script.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

BOOT_SEED = 20260905
BOOT_N = 20000


# ----------------------------------------------------------------------------------
# statistics
# ----------------------------------------------------------------------------------

def boot_mean_ci(xs, alpha=0.05, seed=BOOT_SEED, n_boot=BOOT_N):
    """Percentile bootstrap CI of the mean, plus the degeneracy flag.

    ``degenerate`` is True when every non-zero observation shares a sign. In that
    case no resample can cross zero and the excluded-zero conclusion is an
    artefact of the estimator, not evidence. Quote the counts instead.
    """
    xs = list(xs)
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan"), True
    nz = [x for x in xs if x != 0]
    degenerate = (not nz) or all(x > 0 for x in nz) or all(x < 0 for x in nz)
    if n < 2:
        return float("nan"), float("nan"), True
    rng = random.Random(seed)
    boots = sorted(st.mean([xs[rng.randrange(n)] for _ in range(n)]) for _ in range(n_boot))
    lo = boots[int(alpha / 2 * n_boot)]
    hi = boots[min(n_boot - 1, int((1 - alpha / 2) * n_boot))]
    return lo, hi, degenerate


def cluster_boot_mean_ci(pairs, alpha=0.05, seed=BOOT_SEED, n_boot=BOOT_N):
    """Percentile bootstrap resampling whole clusters (source sample ids)."""
    groups = defaultdict(list)
    for cluster, value in pairs:
        groups[cluster].append(value)
    keys = sorted(groups)
    if len(keys) < 2:
        return float("nan"), float("nan"), True
    values = [v for _, v in pairs]
    nz = [v for v in values if v != 0]
    degenerate = (not nz) or all(v > 0 for v in nz) or all(v < 0 for v in nz)
    rng = random.Random(seed)
    boots = []
    for _ in range(n_boot):
        drawn = []
        for _ in range(len(keys)):
            drawn.extend(groups[keys[rng.randrange(len(keys))]])
        boots.append(st.mean(drawn))
    boots.sort()
    lo = boots[int(alpha / 2 * n_boot)]
    hi = boots[min(n_boot - 1, int((1 - alpha / 2) * n_boot))]
    return lo, hi, degenerate


def sign_test(xs):
    """Two-sided exact binomial sign test on non-zero values. Returns (p, pos, neg)."""
    pos = sum(1 for x in xs if x > 0)
    neg = sum(1 for x in xs if x < 0)
    n = pos + neg
    if n == 0:
        return 1.0, pos, neg
    k = min(pos, neg)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail), pos, neg


def auc(pos, neg):
    """Mann-Whitney AUC: P(signal higher in `pos` than in `neg`), ties at 0.5."""
    if not pos or not neg:
        return float("nan")
    wins = 0.0
    for a in pos:
        for b in neg:
            wins += 1.0 if a > b else (0.5 if a == b else 0.0)
    return wins / (len(pos) * len(neg))


def cluster_boot_auc(rows, key, label_key="harmful", seed=BOOT_SEED, n_boot=4000):
    """Observed AUC and a bootstrap CI resampling whole instances (clusters).

    Resampling the instance, not the transition, is what keeps the interval
    honest: the two transitions of one instance are not independent draws. A CI
    covering 0.5 means the signal does not separate the classes at this n.
    """
    obs = auc([r[key] for r in rows if r[label_key]], [r[key] for r in rows if not r[label_key]])
    clusters = defaultdict(list)
    for r in rows:
        clusters[r["sample_id"]].append(r)
    keys = sorted(clusters)
    if len(keys) < 3 or math.isnan(obs):
        return obs, float("nan"), float("nan")
    rng = random.Random(seed)
    boots = []
    for _ in range(n_boot):
        drawn = []
        for _ in range(len(keys)):
            drawn.extend(clusters[keys[rng.randrange(len(keys))]])
        a = auc([r[key] for r in drawn if r[label_key]], [r[key] for r in drawn if not r[label_key]])
        if not math.isnan(a):
            boots.append(a)
    if len(boots) < 100:
        return obs, float("nan"), float("nan")
    boots.sort()
    return obs, boots[int(0.025 * len(boots))], boots[min(len(boots) - 1, int(0.975 * len(boots)))]


# ----------------------------------------------------------------------------------
# loading
# ----------------------------------------------------------------------------------

def _slug(sample_id: str) -> str:
    return sample_id.replace("/", "__")


def _text_len(run_dir: Path, sample_id: str, rnd: int) -> int | None:
    """Character count of one round's output. Length only -- text is never emitted."""
    p = run_dir / "instances" / _slug(sample_id) / f"armB.round{rnd}.md"
    if not p.exists():
        return None
    return len(p.read_text(encoding="utf-8", errors="replace"))


def load_arm(run_dir: Path) -> dict:
    payload = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    plan = payload["plan"]
    label = plan.get("label") or run_dir.name
    assigned = list(plan.get("sample_ids") or [])
    instances = []
    seen = set()
    for row in payload["instances"]:
        entry = row.get("arms", {}).get("B")
        if entry is None:
            continue
        sample_id = row["sample_id"]
        seen.add(sample_id)
        rs = {int(k): v for k, v in (entry.get("round_scores") or {}).items()}
        if not rs:
            continue
        rounds = sorted(rs)
        findings = defaultdict(list)
        for f in entry.get("findings") or []:
            findings[int(f["round"])].append(f)
        instances.append({
            "sample_id": sample_id,
            "rounds": rounds,
            "f1": {r: rs[r]["f1"] for r in rounds},
            "accuracy": {r: rs[r]["accuracy"] for r in rounds},
            "precision": {r: rs[r]["precision"] for r in rounds},
            "recall": {r: rs[r]["recall"] for r in rounds},
            "n_items": rs[rounds[0]]["n_items"],
            "per_item": {r: rs[r]["per_item"] for r in rounds},
            "findings": findings,
            "chars": {r: _text_len(run_dir, sample_id, r) for r in rounds},
        })
    return {
        "label": label,
        "run_dir": f"{run_dir.parent.name}/{run_dir.name}",
        "run_id": plan.get("run_id"),
        "started_utc": plan.get("started_utc"),
        "task": plan.get("task"),
        "corpus_sha256": plan.get("corpus_sha256"),
        "constitution_sha256": plan.get("constitution_sha256"),
        "seed": plan.get("seed"),
        "settings": plan.get("settings"),
        "models": plan.get("models"),
        "n_assigned": len(assigned) or plan.get("n"),
        "n_scored": len(instances),
        "missing": sorted(s for s in assigned if s not in seen),
        "instances": instances,
    }


# ----------------------------------------------------------------------------------
# per-transition and per-instance records
# ----------------------------------------------------------------------------------

def item_split(pre_items: dict, post_items: dict) -> dict:
    """Fixed / broken / untouched, on three axes.

    ``accuracy`` is CLEAR's per-item both-hit state (precision_hit and
    recall_hit) -- the item is right. ``recall`` alone is the attribution axis
    (did the output cover the reference item at all); ``precision`` alone is
    whether what it said about the item was right.
    """
    out = {}
    for axis in ("accuracy", "recall", "precision"):
        fixed = broken = kept = never = 0
        for key, post in post_items.items():
            pre = pre_items.get(key)
            if pre is None:
                continue
            def state(d):
                if axis == "accuracy":
                    return bool(d["precision_hit"]) and bool(d["recall_hit"])
                return bool(d[f"{axis}_hit"])
            a, b = state(pre), state(post)
            if not a and b:
                fixed += 1
            elif a and not b:
                broken += 1
            elif a and b:
                kept += 1
            else:
                never += 1
        out[axis] = {
            "fixed": fixed, "broken": broken,
            "kept_right": kept, "kept_wrong": never,
            "untouched": kept + never,
        }
    return out


def transitions_of(arm: dict) -> list[dict]:
    rows = []
    for inst in arm["instances"]:
        rounds = inst["rounds"]
        for a, b in zip(rounds, rounds[1:]):
            pre_f1, post_f1 = inst["f1"][a], inst["f1"][b]
            fs = inst["findings"].get(a, [])
            pre_chars, post_chars = inst["chars"].get(a), inst["chars"].get(b)
            growth = (post_chars / pre_chars) if (pre_chars and post_chars) else None
            rows.append({
                "arm": arm["label"],
                "sample_id": inst["sample_id"],
                "from_round": a,
                "to_round": b,
                "n_items": inst["n_items"],
                "pre_f1": pre_f1,
                "post_f1": post_f1,
                "delta_f1": post_f1 - pre_f1,
                "harmful": post_f1 < pre_f1,
                "improving": post_f1 > pre_f1,
                "tied": post_f1 == pre_f1,
                "pre_accuracy": inst["accuracy"][a],
                "post_accuracy": inst["accuracy"][b],
                "items": item_split(inst["per_item"][a], inst["per_item"][b]),
                # runtime-visible signals, measured on the audit that caused this revision
                "n_findings": len(fs),
                "rules": sorted({f["rule"] for f in fs}),
                "n_rules": len({f["rule"] for f in fs}),
                "severities": sorted({f["severity"] for f in fs}),
                "pre_chars": pre_chars,
                "post_chars": post_chars,
                "growth_ratio": growth,
                "growth_pct": None if growth is None else 100 * (growth - 1),
            })
    return rows


def instances_of(arm: dict) -> list[dict]:
    rows = []
    for inst in arm["instances"]:
        rounds = inst["rounds"]
        f1 = inst["f1"]
        actual = f1[rounds[-1]]
        report_only = f1[rounds[0]]
        keep_best = max(f1[r] for r in rounds)
        # stop-on-first-reject: halt the loop the first time a revision would lower F1
        stop = f1[rounds[0]]
        for a, b in zip(rounds, rounds[1:]):
            if f1[b] < f1[a]:
                break
            stop = f1[b]
        rows.append({
            "arm": arm["label"],
            "sample_id": inst["sample_id"],
            "n_rounds": len(rounds),
            "revised": len(rounds) > 1,
            "n_transitions": len(rounds) - 1,
            "f1_by_round": {str(r): f1[r] for r in rounds},
            "f1_round1": report_only,
            "f1_actual_final": actual,
            "f1_gate_keep_best": keep_best,
            "f1_gate_stop_on_reject": stop,
            "d_gate_vs_actual": keep_best - actual,
            "d_stopgate_vs_actual": stop - actual,
            "d_reportonly_vs_actual": report_only - actual,
            "d_gate_vs_reportonly": keep_best - report_only,
        })
    return rows


# ----------------------------------------------------------------------------------
# implementable proxy gates
# ----------------------------------------------------------------------------------

#: Candidate gates a running product could actually apply, each a predicate over the
#: signals visible at the moment the revision is produced. ``True`` means "reject this
#: revision". A rejection halts the loop and ships the text being revised, because what
#: the loop would have done after a rejection was never generated and cannot be replayed.
PROXY_GATES = {
    "never revise (report-only)": lambda t: True,
    "reject if >=2 findings in the audit": lambda t: t["n_findings"] >= 2,
    "reject if >=3 findings in the audit": lambda t: t["n_findings"] >= 3,
    "reject if text grew >25%": lambda t: (t["growth_pct"] is not None and t["growth_pct"] > 25),
    "allow one revision only (max_rounds=2)": lambda t: t["to_round"] > 2,
}


def proxy_final(inst_transitions, f1_by_round, rounds, predicate):
    """Final F1 under a proxy gate with stop-on-reject semantics."""
    final = f1_by_round[rounds[0]]
    index = {(t["from_round"], t["to_round"]): t for t in inst_transitions}
    for a, b in zip(rounds, rounds[1:]):
        t = index.get((a, b))
        if t is None or predicate(t):
            break
        final = f1_by_round[b]
    return final


# ----------------------------------------------------------------------------------
# reporting
# ----------------------------------------------------------------------------------

def pct(x):
    return 100 * x


def line_effect(name, xs, indent="    "):
    if not xs:
        print(f"{indent}{name}: n=0")
        return
    xs = [pct(x) for x in xs]
    m = st.mean(xs)
    lo, hi, degen = boot_mean_ci(xs)
    p, pos, neg = sign_test(xs)
    flag = "  [CI DEGENERATE: no sign change in the sample -- read the counts, not the bound]" if degen and (pos or neg) else ""
    print(f"{indent}{name}: n={len(xs)}  mean {m:+.2f} F1  95% CI [{lo:+.2f}, {hi:+.2f}]"
          f"  better/worse/tied {pos}/{neg}/{len(xs)-pos-neg}  sign p={p:.4f}{flag}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--primary", default="S-shipped,R-rubric-shipped,X-split",
                    help="comma-separated arm labels forming the primary (study 3) set")
    args = ap.parse_args()

    arms = [load_arm(p) for p in args.runs]
    primary = [a.strip() for a in args.primary.split(",") if a.strip()]

    all_tr, all_inst = [], []
    for arm in arms:
        all_tr.extend(transitions_of(arm))
        all_inst.extend(instances_of(arm))

    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "transitions.jsonl").open("w", encoding="utf-8") as fh:
        for r in all_tr:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    with (args.out / "instances.jsonl").open("w", encoding="utf-8") as fh:
        for r in all_inst:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    with (args.out / "arms.json").open("w", encoding="utf-8") as fh:
        json.dump([{k: v for k, v in a.items() if k != "instances"} for a in arms], fh, indent=1, sort_keys=True)

    by_arm_tr = defaultdict(list)
    for r in all_tr:
        by_arm_tr[r["arm"]].append(r)
    by_arm_inst = defaultdict(list)
    for r in all_inst:
        by_arm_inst[r["arm"]].append(r)

    order = [a["label"] for a in arms if a["label"] in primary] + \
            [a["label"] for a in arms if a["label"] not in primary]

    print("=" * 100)
    print("1. THE ORACLE GATE -- intention-to-treat over every scored instance in the arm")
    print("=" * 100)
    print("Unit: the instance. Population: every instance the arm scored (never-revised")
    print("instances contribute a delta of exactly 0, they are not dropped).")
    print("keep-best  = reject every transition with post < pre, keep the best text seen.")
    print("stop-first = halt the loop at the first transition that would lower F1.")
    print("report-only= never revise; ship the round-1 draft.\n")
    for label in order:
        arm = next(a for a in arms if a["label"] == label)
        rows = by_arm_inst[label]
        tag = "PRIMARY" if label in primary else "secondary"
        print(f"--- arm {label} ({tag}) ---")
        print(f"    assigned {arm['n_assigned']}, scored {arm['n_scored']}"
              + (f", NOT RUN {len(arm['missing'])}" if arm["missing"] else ""))
        revised = sum(1 for r in rows if r["revised"])
        print(f"    revised {revised} of {len(rows)} instances; {sum(r['n_transitions'] for r in rows)} transitions")
        for key, name in (("f1_round1", "arm F1, report-only (round 1)"),
                          ("f1_actual_final", "arm F1, as shipped"),
                          ("f1_gate_stop_on_reject", "arm F1, stop-first gate"),
                          ("f1_gate_keep_best", "arm F1, keep-best gate")):
            vals = [pct(r[key]) for r in rows]
            print(f"      {name:34s} {st.mean(vals):6.2f}  (n={len(vals)})")
        line_effect("ITT keep-best gate  vs as-shipped ", [r["d_gate_vs_actual"] for r in rows])
        line_effect("ITT stop-first gate vs as-shipped ", [r["d_stopgate_vs_actual"] for r in rows])
        line_effect("ITT report-only     vs as-shipped ", [r["d_reportonly_vs_actual"] for r in rows])
        line_effect("ITT keep-best gate  vs report-only", [r["d_gate_vs_reportonly"] for r in rows])
        cond = [r for r in rows if r["revised"]]
        if cond:
            print("      [EXPLORATORY -- conditioned on revision-occurred, a post-treatment variable]")
            line_effect("cond. keep-best gate vs as-shipped", [r["d_gate_vs_actual"] for r in cond], indent="      ")
        print()

    print("Secondary, pooled with a bootstrap clustered on source sample id:")
    for key, name in (("d_gate_vs_actual", "keep-best gate vs as-shipped"),
                      ("d_reportonly_vs_actual", "report-only vs as-shipped"),
                      ("d_gate_vs_reportonly", "keep-best gate vs report-only")):
        rows = [r for r in all_inst if r["arm"] in primary]
        pairs = [(r["sample_id"], pct(r[key])) for r in rows]
        lo, hi, degen = cluster_boot_mean_ci(pairs)
        vals = [v for _, v in pairs]
        flag = "  [CI DEGENERATE]" if degen else ""
        print(f"    {name:32s} n={len(vals)} over {len({s for s,_ in pairs})} unique sample ids"
              f"  mean {st.mean(vals):+.2f}  95% CI [{lo:+.2f}, {hi:+.2f}]{flag}")

    print()
    print("=" * 100)
    print("2. PRESERVATION -- unit: the TRANSITION (one round-k -> round-k+1 step)")
    print("=" * 100)
    print("An item is 'right' when CLEAR scores both precision_hit and recall_hit for it")
    print("(CLEAR's per-item accuracy). recall alone = attribution; precision alone =")
    print("whether what the draft said about that item was correct.\n")
    for label in order:
        rows = by_arm_tr[label]
        if not rows:
            print(f"--- arm {label}: 0 transitions\n")
            continue
        tag = "PRIMARY" if label in primary else "secondary"
        print(f"--- arm {label} ({tag}): {len(rows)} transitions over "
              f"{len({r['sample_id'] for r in rows})} instances ---")
        for axis in ("accuracy", "recall", "precision"):
            f = sum(r["items"][axis]["fixed"] for r in rows)
            b = sum(r["items"][axis]["broken"] for r in rows)
            kr = sum(r["items"][axis]["kept_right"] for r in rows)
            kw = sum(r["items"][axis]["kept_wrong"] for r in rows)
            tot = f + b + kr + kw
            print(f"      {axis:9s} fixed {f:3d}  broken {b:3d}  untouched {kr+kw:3d} "
                  f"(kept-right {kr}, kept-wrong {kw})  of {tot} item-transitions")
        d = [pct(r["delta_f1"]) for r in rows]
        lo, hi, degen = boot_mean_ci(d)
        p, pos, neg = sign_test(d)
        print(f"      per-transition delta F1: mean {st.mean(d):+.2f}  95% CI [{lo:+.2f}, {hi:+.2f}]"
              f"  up/down/tied {pos}/{neg}/{len(d)-pos-neg}  sign p={p:.4f}"
              + ("  [CI DEGENERATE]" if degen else ""))
        churn = sum(1 for r in rows if r["items"]["accuracy"]["fixed"] and r["items"]["accuracy"]["broken"])
        nul = sum(1 for r in rows if not r["items"]["accuracy"]["fixed"] and not r["items"]["accuracy"]["broken"])
        print(f"      transitions that fixed AND broke at least one item: {churn} of {len(rows)}")
        print(f"      transitions that changed no item's correctness:     {nul} of {len(rows)}")
        print()

    print("=" * 100)
    print("3. IS THE GATE IMPLEMENTABLE? -- what a runtime signal would have to predict")
    print("=" * 100)
    print("Label: harmful = post_f1 < pre_f1, one label per TRANSITION.")
    print("AUC 0.5 = the signal orders harmful and non-harmful transitions no better than")
    print("a coin. The interval comes from a bootstrap that resamples whole instances.\n")
    signals = [("to_round", "round index of the new draft"),
               ("n_findings", "findings in the triggering audit"),
               ("n_rules", "distinct rules in that audit"),
               ("growth_pct", "growth in characters, %"),
               ("pre_chars", "length of the text being revised"),
               ("n_items", "checklist size"),
               ("pre_f1", "pre-revision CLEAR F1 [NOT RUNTIME VISIBLE -- reference only]")]
    for label in order + ["ALL PRIMARY ARMS POOLED (clustered)"]:
        if label.startswith("ALL"):
            rows = [r for r in all_tr if r["arm"] in primary]
        else:
            rows = by_arm_tr[label]
        rows = [r for r in rows]
        if len(rows) < 4:
            print(f"--- {label}: {len(rows)} transitions, too few to correlate ---\n")
            continue
        nh = sum(1 for r in rows if r["harmful"])
        print(f"--- {label}: {len(rows)} transitions, {nh} harmful / {len(rows)-nh} not ---")
        for key, desc in signals:
            usable = [r for r in rows if r.get(key) is not None]
            if len({r[key] for r in usable}) < 2 or not usable:
                print(f"      {desc:52s} constant or missing -- no signal")
                continue
            a, alo, ahi = cluster_boot_auc(usable, key)
            hv = [r[key] for r in usable if r["harmful"]]
            nv = [r[key] for r in usable if not r["harmful"]]
            hm = st.mean(hv) if hv else float("nan")
            nm = st.mean(nv) if nv else float("nan")
            print(f"      {desc:52s} AUC {a:.3f} 95% CI [{alo:.3f}, {ahi:.3f}]   "
                  f"mean harmful {hm:8.2f} vs {nm:8.2f}")
        # per-rule harmful rate
        rule_tot, rule_bad = Counter(), Counter()
        for r in rows:
            for rule in r["rules"]:
                rule_tot[rule] += 1
                if r["harmful"]:
                    rule_bad[rule] += 1
        if rule_tot:
            parts = [f"{rule} {rule_bad[rule]} of {rule_tot[rule]}" for rule in sorted(rule_tot)]
            print("      harmful transitions by rule present in the triggering audit:")
            for part in parts:
                print(f"        {part}")
        print()

    print("=" * 100)
    print("3b. THE SAME QUESTION, RESTRICTED TO TRANSITIONS WHERE HARM WAS POSSIBLE")
    print("=" * 100)
    print("A draft already at F1 = 0 cannot be made worse, so it is a guaranteed non-harmful")
    print("transition for arithmetic reasons. Any signal that merely tracks 'the draft was")
    print("bad' will look predictive because of that floor. This repeats section 3 over the")
    print("transitions with pre-revision F1 > 0, where the label carries information.\n")
    for label in order + ["ALL PRIMARY ARMS POOLED (clustered)"]:
        rows = [r for r in all_tr if r["arm"] in primary] if label.startswith("ALL") else by_arm_tr[label]
        rows = [r for r in rows if r["pre_f1"] > 0]
        nh = sum(1 for r in rows if r["harmful"])
        if len(rows) < 4:
            print(f"--- {label}: {len(rows)} harm-possible transitions, too few to correlate ---\n")
            continue
        print(f"--- {label}: {len(rows)} harm-possible transitions, {nh} harmful / {len(rows)-nh} not ---")
        for key, desc in signals:
            if key == "pre_f1":
                continue
            usable = [r for r in rows if r.get(key) is not None]
            if not usable or len({r[key] for r in usable}) < 2:
                print(f"      {desc:52s} constant or missing -- no signal")
                continue
            a, alo, ahi = cluster_boot_auc(usable, key)
            print(f"      {desc:52s} AUC {a:.3f} 95% CI [{alo:.3f}, {ahi:.3f}]")
        print()

    print("=" * 100)
    print("3c. WHAT AN IMPLEMENTABLE PROXY GATE WOULD ACTUALLY BUY -- ITT, per arm")
    print("=" * 100)
    print("Every gate below uses only what the product can see at runtime, and halts the")
    print("loop on rejection. Compare against the oracle's ceiling in section 1.\n")
    tr_by_inst = defaultdict(list)
    for t in all_tr:
        tr_by_inst[(t["arm"], t["sample_id"])].append(t)
    for label in order:
        arm = next(a for a in arms if a["label"] == label)
        tag = "PRIMARY" if label in primary else "secondary"
        rows = by_arm_inst[label]
        print(f"--- arm {label} ({tag}), n={len(rows)} instances ---")
        actual = [pct(r["f1_actual_final"]) for r in rows]
        print(f"      {'as shipped':40s} {st.mean(actual):6.2f} F1")
        print(f"      {'ORACLE keep-best gate (ceiling)':40s} "
              f"{st.mean([pct(r['f1_gate_keep_best']) for r in rows]):6.2f} F1")
        for name, predicate in PROXY_GATES.items():
            vals, deltas = [], []
            for inst in arm["instances"]:
                f1 = inst["f1"]
                got = proxy_final(tr_by_inst[(label, inst["sample_id"])], f1, inst["rounds"], predicate)
                vals.append(pct(got))
                deltas.append(pct(got) - pct(f1[inst["rounds"][-1]]))
            lo, hi, degen = boot_mean_ci(deltas)
            p, pos, neg = sign_test(deltas)
            print(f"      {name:40s} {st.mean(vals):6.2f} F1   ITT {st.mean(deltas):+6.2f}"
                  f"  95% CI [{lo:+.2f}, {hi:+.2f}]  better/worse/tied {pos}/{neg}/{len(deltas)-pos-neg}"
                  + ("  [CI DEGENERATE]" if degen and (pos or neg) else ""))
        print()

    print(f"records written to {args.out}/transitions.jsonl, instances.jsonl, arms.json")


if __name__ == "__main__":
    main()
