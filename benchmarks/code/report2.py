"""Study 2's numbers: does the audit's *structure* move recall, and at what cost?

Every estimator here is study 1's, imported rather than reimplemented, so the two studies'
numbers are produced by the same arithmetic: Wilson intervals on proportions, two-sided
exact McNemar on the discordant pairs, and a seeded paired bootstrap that resamples
*instances* on the difference.

No model runs here. This file reads the arms' JSONL and prints.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from report import (BOOTSTRAP_N, mcnemar_exact, paired_bootstrap_ci,  # noqa: E402
                    pct, wilson)

ARM_FILES = {
    "checks": "arm-checks.jsonl",
    "holistic-cross": "arm-holistic-cross.jsonl",
    "holistic-self": "arm-holistic-self.jsonl",
    "decomposed-cross": "arm-decomposed-cross.jsonl",
    "two-stage-filtered": "arm-two-stage-filter.jsonl",
    "decomposed-replicate": "arm-decomposed-replicate.jsonl",
    "decomposed+two-stage": "arm-decomposed-two-stage.jsonl",
}

#: Reported as an arm but derived, not run: the union of the two holistic arms' blockers.
DERIVED = ("two-stage-union",)


def load(run_dir: Path) -> tuple[dict[str, dict[str, dict]], dict, dict]:
    arms: dict[str, dict[str, dict]] = {}
    for arm, name in ARM_FILES.items():
        path = run_dir / name
        if not path.exists():
            continue
        arms[arm] = {json.loads(l)["instance_id"]: json.loads(l)
                     for l in path.read_text(encoding="utf-8").splitlines() if l.strip()}
    aset = json.loads((run_dir / "audit_set.json").read_text(encoding="utf-8"))
    instances = {json.loads(l)["instance_id"]: json.loads(l)
                 for l in (run_dir / "instances.jsonl").read_text(
                     encoding="utf-8").splitlines() if l.strip()}

    # two-stage-union: flagged if either holistic arm raised a BLOCKER. Derived from arms
    # already run, so it costs nothing and is preregistered as one of the two-stage numbers.
    if "holistic-self" in arms and "holistic-cross" in arms:
        arms["two-stage-union"] = {
            iid: {"instance_id": iid, "ok": True,
                  "stratum": arms["holistic-cross"][iid]["stratum"],
                  "flagged": bool(arms["holistic-cross"][iid].get("flagged")
                                  or arms["holistic-self"][iid].get("flagged")),
                  "cost_usd": (arms["holistic-cross"][iid].get("cost_usd", 0.0)
                               + arms["holistic-self"][iid].get("cost_usd", 0.0)),
                  "wall_s": (arms["holistic-cross"][iid].get("wall_s", 0.0)
                             + arms["holistic-self"][iid].get("wall_s", 0.0))}
            for iid in arms["holistic-cross"] if iid in arms["holistic-self"]}
    return arms, aset, instances


def ids_of(instances: dict, aset: dict, stratum: str) -> list[str]:
    return sorted(i for i in aset["instance_ids"] if instances[i]["stratum"] == stratum)


def usable(arms: dict, names: list[str], ids: list[str]) -> list[str]:
    """Instances every named arm completed without error — every comparison is paired."""
    return [i for i in ids
            if all(i in arms.get(n, {}) and arms[n][i].get("ok") for n in names)]


def rate(arms: dict, arm: str, ids: list[str]) -> tuple[int, int, tuple[float, float]]:
    good = usable(arms, [arm], ids)
    k = sum(1 for i in good if arms[arm][i].get("flagged"))
    return k, len(good), wilson(k, len(good))


def compare(arms: dict, a: str, b: str, ids: list[str]) -> dict:
    """b minus a, paired on the instances both arms completed."""
    good = usable(arms, [a, b], ids)
    pairs = [(int(bool(arms[a][i].get("flagged"))), int(bool(arms[b][i].get("flagged"))))
             for i in good]
    only_b = sum(1 for x, y in pairs if y and not x)
    only_a = sum(1 for x, y in pairs if x and not y)
    ka = sum(x for x, _ in pairs)
    kb = sum(y for _, y in pairs)
    n = len(pairs)
    return {"a": a, "b": b, "n": n, "k_a": ka, "k_b": kb,
            "rate_a": ka / n if n else 0.0, "rate_b": kb / n if n else 0.0,
            "diff": (kb - ka) / n if n else 0.0,
            "only_b": only_b, "only_a": only_a,
            "p": mcnemar_exact(only_b, only_a),
            "ci": paired_bootstrap_ci(pairs)}


def line(label: str, k: int, n: int, ci: tuple[float, float]) -> str:
    r = k / n if n else 0.0
    return (f"  {label:24s} {pct(r):>7s}  {k:3d}/{n:<4d}  "
            f"[{pct(ci[0])}, {pct(ci[1])}]")


def show(cmp: dict, title: str) -> None:
    print(f"\n  {title}")
    print(f"    {cmp['b']} {pct(cmp['rate_b'])} vs {cmp['a']} {pct(cmp['rate_a'])}"
          f"   difference {cmp['diff']*100:+.1f} points")
    print(f"    n = {cmp['n']}   discordant {cmp['only_b']} ({cmp['b']}-only) "
          f"vs {cmp['only_a']} ({cmp['a']}-only)")
    print(f"    McNemar exact p = {cmp['p']:.6g}   "
          f"95% CI [{cmp['ci'][0]*100:+.1f}, {cmp['ci'][1]*100:+.1f}] points")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--json-out", default="")
    args = parser.parse_args(argv)

    run_dir = Path(args.run)
    arms, aset, instances = load(run_dir)
    P = ids_of(instances, aset, "P")
    C = ids_of(instances, aset, "C")
    F = ids_of(instances, aset, "F")
    order = [a for a in ("checks", "holistic-cross", "holistic-self", "decomposed-cross",
                         "two-stage-union", "two-stage-filtered", "decomposed-replicate",
                         "decomposed+two-stage") if a in arms]

    out: dict = {"n": {"P": len(P), "C": len(C), "F": len(F)}, "arms": {}, "comparisons": {}}

    print("=" * 78)
    print("RECALL on P — 'looks right, is wrong' (passes visible tests, fails hidden)")
    print("=" * 78)
    for arm in order:
        k, n, ci = rate(arms, arm, P)
        print(line(arm, k, n, ci))
        out["arms"].setdefault(arm, {})["recall_P"] = {"k": k, "n": n, "ci": ci}

    print("\n" + "=" * 78)
    print("FALSE POSITIVES on C — correct solutions flagged")
    print("=" * 78)
    for arm in order:
        k, n, ci = rate(arms, arm, C)
        print(line(arm, k, n, ci))
        out["arms"].setdefault(arm, {})["fp_C"] = {"k": k, "n": n, "ci": ci}

    print("\n" + "=" * 78)
    print("STRATUM F — the sanity check (code that does not even pass the visible suite)")
    print("=" * 78)
    for arm in order:
        k, n, ci = rate(arms, arm, F)
        print(line(arm, k, n, ci))
        out["arms"].setdefault(arm, {})["flag_F"] = {"k": k, "n": n, "ci": ci}

    # ---- precision and corpus-level flag rate, reweighted ----
    print("\n" + "=" * 78)
    print("PRECISION and FLAG RATE, reweighted to the 1,080-instance population")
    print("=" * 78)
    w = aset["weights"]
    print(f"  weights: P {w['P']:.2f}  C {w['C']:.2f}  F {w['F']:.2f}")
    print(f"  {'arm':24s} {'flag rate':>10s} {'precision':>10s}")
    for arm in order:
        num = den = tp = fp = 0.0
        for stratum, ids in (("P", P), ("C", C), ("F", F)):
            good = usable(arms, [arm], ids)
            k = sum(1 for i in good if arms[arm][i].get("flagged"))
            weight = w[stratum]
            num += k * weight
            den += len(good) * weight
            # a flag is correct if the solution fails any test: strata P and F
            if stratum in ("P", "F"):
                tp += k * weight
            else:
                fp += k * weight
        flag_rate = num / den if den else 0.0
        precision = tp / (tp + fp) if (tp + fp) else float("nan")
        print(f"  {arm:24s} {pct(flag_rate):>10s} "
              f"{(pct(precision) if precision == precision else '—'):>10s}")
        out["arms"][arm]["flag_rate_weighted"] = flag_rate
        out["arms"][arm]["precision_weighted"] = precision

    # ---- the preregistered comparisons ----
    print("\n" + "=" * 78)
    print("THE PREREGISTERED COMPARISONS")
    print("=" * 78)
    print("\n--- PRIMARY OUTCOME ---")
    primary = compare(arms, "holistic-cross", "decomposed-cross", P)
    show(primary, "1. decomposed-cross - holistic-cross, RECALL on P  [PRIMARY]")
    out["comparisons"]["primary_recall_P"] = primary
    fp_cmp = compare(arms, "holistic-cross", "decomposed-cross", C)
    show(fp_cmp, "2. decomposed-cross - holistic-cross, FALSE POSITIVES on C")
    out["comparisons"]["decomposed_fp_C"] = fp_cmp

    print("\n--- SECONDARY ---")
    for key, a, b, ids, title in (
        ("union_recall_P", "holistic-cross", "two-stage-union", P,
         "3. two-stage-union - holistic-cross, RECALL on P"),
        ("union_fp_C", "holistic-cross", "two-stage-union", C,
         "4. two-stage-union - holistic-cross, FALSE POSITIVES on C"),
        ("filtered_recall_P", "holistic-cross", "two-stage-filtered", P,
         "5. two-stage-filtered - holistic-cross, RECALL on P"),
        ("filtered_fp_C", "holistic-cross", "two-stage-filtered", C,
         "6. two-stage-filtered - holistic-cross, FALSE POSITIVES on C"),
    ):
        if b in arms:
            cmp = compare(arms, a, b, ids)
            show(cmp, title)
            out["comparisons"][key] = cmp

    # ---- noise floors ----
    print("\n" + "=" * 78)
    print("NOISE FLOOR — the same configuration, run twice")
    print("=" * 78)
    if "decomposed-replicate" in arms:
        for stratum, ids in (("P", P), ("C", C)):
            good = usable(arms, ["decomposed-cross", "decomposed-replicate"], ids)
            disagree = sum(1 for i in good
                           if bool(arms["decomposed-cross"][i].get("flagged"))
                           != bool(arms["decomposed-replicate"][i].get("flagged")))
            k1 = sum(1 for i in good if arms["decomposed-cross"][i].get("flagged"))
            k2 = sum(1 for i in good if arms["decomposed-replicate"][i].get("flagged"))
            print(f"  decomposed on {stratum}: {k1}/{len(good)} vs {k2}/{len(good)} — "
                  f"{disagree} disagreements, {abs(k1-k2)/len(good)*100:.1f} points apart")
            out.setdefault("noise", {})[f"decomposed_{stratum}"] = {
                "disagreements": disagree, "n": len(good),
                "points": abs(k1 - k2) / len(good) * 100}

    # ---- exploratory: the combined arm ----
    if "decomposed+two-stage" in arms:
        print("\n" + "=" * 78)
        print("EXPLORATORY — decomposed+two-stage (composition fixed after scores were seen)")
        print("=" * 78)
        for stratum, ids in (("P", P), ("C", C)):
            cmp = compare(arms, "decomposed-replicate", "decomposed+two-stage", ids)
            show(cmp, f"filtering the decomposed arm's findings, on {stratum}")
            out["comparisons"][f"exploratory_combined_{stratum}"] = cmp

    # ---- cost and time ----
    print("\n" + "=" * 78)
    print("COST AND TIME")
    print("=" * 78)
    print(f"  {'arm':24s} {'spend':>9s} {'$/instance':>11s} {'$/true finding':>15s} "
          f"{'s/instance':>11s}")
    everything = sorted(set(P) | set(C) | set(F))
    for arm in order:
        good = usable(arms, [arm], everything)
        spend = sum(float(arms[arm][i].get("cost_usd") or 0.0) for i in good)
        wall = sum(float(arms[arm][i].get("wall_s") or 0.0) for i in good)
        tp = sum(1 for i in good if arms[arm][i].get("flagged")
                 and instances[i]["stratum"] in ("P", "F"))
        per_true = (spend / tp) if tp else float("nan")
        print(f"  {arm:24s} ${spend:8.4f} ${spend/max(len(good),1):10.5f} "
              f"{('$%.4f' % per_true) if per_true == per_true else '—':>15s} "
              f"{wall/max(len(good),1):10.2f}s")
        out["arms"][arm].update({"spend_usd": spend, "true_findings": tp,
                                 "cost_per_true_finding": per_true,
                                 "wall_s_per_instance": wall / max(len(good), 1)})

    # ---- decomposition descriptives ----
    if "decomposed-cross" in arms:
        rows = [r for r in arms["decomposed-cross"].values() if r.get("ok")]
        props = [r.get("n_properties", 0) for r in rows]
        print(f"\n  decomposition: {sum(props)} property checks over {len(rows)} instances, "
              f"mean {sum(props)/len(rows):.2f} per instance; "
              f"{sum(1 for p in props if p == 0)} instances decomposed to nothing; "
              f"{sum(r.get('n_unparsed', 0) for r in rows)} unparseable check replies")
        out["decomposition"] = {"total_checks": sum(props), "mean_properties": sum(props)/len(rows),
                                "zero_property_instances": sum(1 for p in props if p == 0),
                                "unparsed": sum(r.get('n_unparsed', 0) for r in rows)}

    print(f"\n  bootstrap draws {BOOTSTRAP_N}")
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(out, indent=2, default=str) + "\n",
                                       encoding="utf-8")
        print(f"  numbers -> {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
