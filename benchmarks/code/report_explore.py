"""Apply study 7's preregistered objective to the leaderboard, and nothing else.

The objective, from ``explore/PREREGISTRATION.md`` §5, fixed before any spec was scored:

    Best = the highest P-recall on the **confirm** half among specs whose
    C-false-positive rate on the confirm half is <= 6.7%.

6.7% is the shipped architecture's own upper 95% Wilson bound from study 1 (4/150).
Selection is on the explore half; every reported claim is on the confirm half. This module
computes both, applies the rule, and prints the Pareto front. It takes no view: if nothing
clears the shipped architecture by more than the noise floor inside the constraint, it says
so, and there is no second objective.

    python benchmarks/code/report_explore.py --json-out records/explore/numbers.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from explore import EXPLORE, mcnemar_exact  # noqa: E402

#: The preregistered constraint: study 1's `cross` arm flagged 4 of 150 correct solutions,
#: 95% Wilson CI [1.0%, 6.7%]. In code, false positives are the number that ends a tool's
#: life, so the constraint is the shipped architecture's own upper bound.
FP_CONSTRAINT = 0.067
#: Study 1's `cross-replicate`: the same configuration, the same bytes, run twice.
NOISE_FLOOR_P = 1.8
NOISE_FLOOR_C = 0.7
SHIPPED = "hc"


def pct(block: dict) -> str:
    lo, hi = block["ci95"]
    return f"{100 * block['rate']:.1f}% ({block['k']}/{block['n']}) [{100 * lo:.1f}, {100 * hi:.1f}]"


def pareto(entries: list[dict], half: str) -> list[str]:
    """Specs not dominated on (recall up, false positives down, cost down)."""
    front = []
    for a in entries:
        ra, fa, ca = a[half]["P"]["rate"], a[half]["C"]["rate"], a["cost_usd_per_instance"]
        dominated = False
        for b in entries:
            if b["spec_id"] == a["spec_id"]:
                continue
            rb, fb, cb = b[half]["P"]["rate"], b[half]["C"]["rate"], b["cost_usd_per_instance"]
            if rb >= ra and fb <= fa and cb <= ca and (rb > ra or fb < fa or cb < ca):
                dominated = True
                break
        if not dominated:
            front.append(a["spec_id"])
    return front


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", default=str(EXPLORE / "numbers.json"))
    args = parser.parse_args(argv)

    entries = [json.loads(l) for l in (EXPLORE / "leaderboard.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    by_id = {e["spec_id"]: e for e in entries}
    rows = [json.loads(l) for l in (EXPLORE / "rows.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    flags: dict[str, dict[str, bool]] = {}
    half_of: dict[str, str] = {}
    stratum_of: dict[str, str] = {}
    for row in rows:
        flags.setdefault(row["spec_id"], {})[row["instance_id"]] = row["flagged"]
        half_of[row["instance_id"]] = row["half"]
        stratum_of[row["instance_id"]] = row["stratum"]

    shipped = by_id[SHIPPED]

    # --- selection, on the explore half only -------------------------------------
    explore_eligible = [e for e in entries if e["explore"]["C"]["rate"] <= FP_CONSTRAINT]
    explore_best = max(explore_eligible, key=lambda e: e["explore"]["P"]["rate"], default=None)

    # --- the reported objective, on the confirm half ------------------------------
    eligible = [e for e in entries if e["confirm"]["C"]["rate"] <= FP_CONSTRAINT]
    best = max(eligible, key=lambda e: e["confirm"]["P"]["rate"], default=None)

    def paired(spec_id: str, half: str, stratum: str) -> dict:
        a, b = flags.get(SHIPPED, {}), flags.get(spec_id, {})
        ids = [i for i in a if i in b and half_of[i] == half and stratum_of[i] == stratum]
        only_new = sum(1 for i in ids if b[i] and not a[i])
        only_ship = sum(1 for i in ids if a[i] and not b[i])
        return {"n": len(ids), "only_spec": only_new, "only_shipped": only_ship,
                "mcnemar_exact_p": round(mcnemar_exact(only_new, only_ship), 6)}

    verdicts = []
    for e in entries:
        if e["spec_id"] == SHIPPED:
            continue
        d_p = 100 * (e["confirm"]["P"]["rate"] - shipped["confirm"]["P"]["rate"])
        inside = e["confirm"]["C"]["rate"] <= FP_CONSTRAINT
        beats = d_p > NOISE_FLOOR_P
        verdicts.append({
            "spec_id": e["spec_id"], "label": e["label"],
            "delta_P_points": round(d_p, 2),
            "delta_C_points": round(100 * (e["confirm"]["C"]["rate"] - shipped["confirm"]["C"]["rate"]), 2),
            "inside_constraint": inside, "beats_noise_floor": beats,
            "verdict": ("beats the shipped architecture inside the constraint" if beats and inside
                        else "beats it, but only outside the constraint" if beats
                        else "does not beat it by more than the noise floor"),
            "mcnemar_P_confirm": paired(e["spec_id"], "confirm", "P"),
        })

    numbers = {
        "objective": {
            "rule": "highest confirm-half P-recall among specs with confirm-half "
                    "C-false-positive rate <= 6.7%",
            "fp_constraint": FP_CONSTRAINT,
            "noise_floor_points": {"P": NOISE_FLOOR_P, "C": NOISE_FLOOR_C},
            "selected_on_explore": explore_best["spec_id"] if explore_best else None,
            "best_on_confirm": best["spec_id"] if best else None,
            "eligible_on_confirm": [e["spec_id"] for e in eligible],
        },
        "shipped": shipped,
        "leaderboard": entries,
        "pareto_confirm": pareto(entries, "confirm"),
        "pareto_explore": pareto(entries, "explore"),
        "against_shipped": verdicts,
    }
    Path(args.json_out).write_text(json.dumps(numbers, indent=2, sort_keys=True) + "\n",
                                   encoding="utf-8")

    print(f"\nSELECTION (explore half only): {explore_best['spec_id'] if explore_best else 'none'}")
    print(f"BEST under the objective (confirm half): {best['spec_id'] if best else 'none'}\n")
    header = f"{'spec':15s} {'confirm P-recall':30s} {'confirm C-FP':28s} {'$/inst':>8s}  front"
    print(header)
    print("-" * len(header))
    front = set(numbers["pareto_confirm"])
    for e in sorted(entries, key=lambda x: -x["confirm"]["P"]["rate"]):
        mark = "*" if e["spec_id"] in front else " "
        flagm = "<=6.7%" if e["confirm"]["C"]["rate"] <= FP_CONSTRAINT else "      "
        print(f"{e['spec_id']:15s} {pct(e['confirm']['P']):30s} "
              f"{pct(e['confirm']['C']):28s} {e['cost_usd_per_instance']:8.4f}  {mark} {flagm}")
    print("\nagainst the shipped architecture, on the confirm half:")
    for v in sorted(verdicts, key=lambda x: -x["delta_P_points"]):
        print(f"  {v['spec_id']:15s} {v['delta_P_points']:+6.1f} P  "
              f"{v['delta_C_points']:+6.1f} C   {v['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
