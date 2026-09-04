"""Turn one or more :mod:`premise` run directories into the study-5 numbers.

With one run directory it reports study A: the four arms' recall and precision against
CLEAR ground truth on the same drafts, plus the paired cross-versus-self test.

With several it reports study B as well: the same configuration repeated on the same
instances, and the run-to-run standard deviation of every arm mean. That standard
deviation is the noise floor against which this project's published deltas have to be
read.

Usage::

    python benchmarks/expertlongbench/premise_report.py RUN_DIR [RUN_DIR ...]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from stats import mean, stdev, wilcoxon_signed_rank, wilson_interval  # noqa: E402

ARM_ORDER = ("cross", "self", "sibling", "none")
MAPPINGS = ("model_mapping", "rule_mapping",
            "blocker_model_mapping", "blocker_rule_mapping")


def load(path: Path) -> dict:
    return json.loads((path / "results.json").read_text(encoding="utf-8"))


def scored_instances(run: dict) -> list[dict]:
    return [i for i in run["instances"] if i.get("arms") and i.get("draft_score")]


def arm_totals(run: dict, arm: str, mapping: str) -> dict:
    """Micro-averaged over instances: the auditor against ground truth."""
    wrong = named = both = named_correct = 0
    fired = gated = judged = errors = invalid = 0
    findings = blockers = 0
    per_instance_recall: list[float] = []
    for instance in scored_instances(run):
        entry = instance["arms"].get(arm)
        if entry is None:
            continue
        judged += 1
        if not entry["ok"]:
            errors += 1
            continue
        if entry.get("invalid_reason"):
            invalid += 1
        rates = entry[mapping]
        wrong += entry["n_items_wrong"]
        named += rates["n_named"]
        both += rates["n_wrong_and_named"]
        named_correct += rates["n_named_but_correct"]
        findings += entry["n_findings"]
        blockers += entry["n_blockers"]
        if entry["n_findings"]:
            fired += 1
        if entry.get("gated"):
            gated += 1
        if entry["n_items_wrong"]:
            per_instance_recall.append(
                rates["n_wrong_and_named"] / entry["n_items_wrong"])
    return {
        "arm": arm, "judged": judged, "errors": errors, "invalid": invalid,
        "fired": fired, "gated": gated, "findings": findings, "blockers": blockers,
        "items_wrong": wrong, "items_named": named, "wrong_and_named": both,
        "named_but_correct": named_correct,
        "recall": (both / wrong) if wrong else None,
        "precision": (both / named) if named else None,
        "macro_recall": mean(per_instance_recall) if per_instance_recall else None,
        "per_instance_recall": per_instance_recall,
    }


def paired_recall(run: dict, arm_a: str, arm_b: str, mapping: str):
    """Per-instance recall for two arms on the same draft, and their differences."""
    pairs = []
    for instance in scored_instances(run):
        a, b = instance["arms"].get(arm_a), instance["arms"].get(arm_b)
        if not a or not b or not a["ok"] or not b["ok"]:
            continue
        if not a["n_items_wrong"]:
            continue
        pairs.append((
            instance["sample_id"],
            a[mapping]["n_wrong_and_named"] / a["n_items_wrong"],
            b[mapping]["n_wrong_and_named"] / b["n_items_wrong"],
        ))
    return pairs


def cost(run: dict, path: Path) -> dict:
    """Every dollar this run spent, priced by the product's own usage ledger.

    Two sources, because a scratch project is deleted the moment its instance is
    recorded: generation and judging spend is read out of that project's ledger *before*
    the delete and carried on the record, and the host project's surviving ledger holds
    the CLEAR scoring and adjudication calls. Reading only the surviving ledgers, as a
    first version of this function did, silently reported about a fifth of the true
    figure.
    """
    sys.path.insert(0, str(HERE.parents[1] / "src"))
    from crossaudit import usage  # noqa: PLC0415

    run_ids = set(run["plan"].get("run_ids") or [run["plan"]["run_id"]])
    by_phase: dict[str, float] = {}
    for instance in run["instances"]:
        generation = instance.get("generation") or {}
        # `generation.cost_usd` is read off the scratch project's ledger before the
        # judging turns are placed against that same project, so the two lines do not
        # overlap.
        judging = float(instance.get("judging_cost_usd") or 0.0)
        gen_total = float(generation.get("cost_usd") or 0.0)
        by_phase["generation+product-audit"] = (
            by_phase.get("generation+product-audit", 0.0) + gen_total)
        by_phase["judging (3 arms)"] = by_phase.get("judging (3 arms)", 0.0) + judging
    for ledger in path.rglob(usage.LEDGER_NAME):
        events, _bad = usage.read_events(ledger)
        for event in events:
            if event.get("run_id") not in run_ids:
                continue
            phase = str(event.get("phase", "?"))
            if phase.startswith("premise-") or phase in {"generation", "audit"}:
                continue          # already counted from the record
            by_phase[phase] = by_phase.get(phase, 0.0) + float(
                event.get("api_value_usd") or 0.0)
    by_phase["TOTAL"] = sum(v for k, v in by_phase.items() if k != "TOTAL")
    return by_phase


def render(paths: list[Path]) -> str:
    runs = [(p, load(p)) for p in paths]
    out: list[str] = []
    add = out.append

    primary_path, primary = runs[0]
    plan = primary["plan"]
    add(f"study 5 -- the premise. task {plan['task']}, seed {plan['seed']}, "
        f"code {plan['code_sha'][:12]}")
    add(f"rules: {plan['settings']['audit_rules']} "
        f"(constitution {plan['constitution_sha256'][:16]})")
    add(f"generator {plan['models']['generator']}   judge {plan['models']['judge']}")
    for arm, spec in plan["arm_models"].items():
        add(f"  arm {arm:8} -> {spec or '(no judgement)'}")
    add("")

    for path, run in runs:
        n = len(scored_instances(run))
        add(f"=== {path.name}  n={n} ===")
        drafts = [i["draft_score"] for i in scored_instances(run)]
        if drafts:
            add(f"draft CLEAR F1 mean {100 * mean([d['f1'] for d in drafts]):.1f}   "
                f"accuracy {100 * mean([d['accuracy'] for d in drafts]):.1f}   "
                f"items wrong {sum(sum(1 for v in d['per_item'].values() if not (v['precision_hit'] and v['recall_hit'])) for d in drafts)}"
                f" of {sum(d['n_items'] for d in drafts)}")
        for mapping in MAPPINGS:
            add(f"\n  -- {mapping} --")
            add(f"  {'arm':8} {'judged':>6} {'fired':>5} {'gated':>5} {'find':>5} "
                f"{'wrong':>6} {'named':>6} {'hit':>4} {'recall':>8} {'precision':>10}")
            for arm in ARM_ORDER:
                t = arm_totals(run, arm, mapping)
                if not t["judged"]:
                    continue
                rec = "  n/a  " if t["recall"] is None else f"{100 * t['recall']:6.1f}%"
                pre = "   n/a   " if t["precision"] is None else f"{100 * t['precision']:8.1f}%"
                add(f"  {arm:8} {t['judged']:>6} {t['fired']:>5} {t['gated']:>5} "
                    f"{t['findings']:>5} {t['items_wrong']:>6} {t['items_named']:>6} "
                    f"{t['wrong_and_named']:>4} {rec:>8} {pre:>10}")
        add("")
        spend = cost(run, path)
        add("  spend: " + "  ".join(f"{k}=${v:.2f}" for k, v in sorted(spend.items())))
        add("")

    # ---------------------------------------------------------------- study A
    add("=== the comparison the study exists for: cross vs self ===")
    for mapping in ("model_mapping", "rule_mapping", "blocker_rule_mapping"):
        pairs = paired_recall(primary, "cross", "self", mapping)
        if not pairs:
            continue
        diffs = [c - s for _id, c, s in pairs]
        w = wilcoxon_signed_rank(diffs)
        better = sum(1 for d in diffs if d > 0)
        worse = sum(1 for d in diffs if d < 0)
        add(f"  [{mapping}] n={len(pairs)}  cross {100 * mean([c for _i, c, _s in pairs]):.1f}%  "
            f"self {100 * mean([s for _i, _c, s in pairs]):.1f}%  "
            f"paired delta {100 * mean(diffs):+.1f} pp  "
            f"cross better/worse/tied {better}/{worse}/{len(diffs) - better - worse}  "
            f"Wilcoxon p={w.p_value:.3f}")
    for mapping in ("model_mapping", "rule_mapping"):
        pairs = paired_recall(primary, "cross", "sibling", mapping)
        if not pairs:
            continue
        diffs = [c - s for _id, c, s in pairs]
        w = wilcoxon_signed_rank(diffs)
        add(f"  [{mapping}] cross vs SIBLING: n={len(pairs)}  "
            f"delta {100 * mean(diffs):+.1f} pp  p={w.p_value:.3f}")
    add("")

    # precision intervals, because a collapse there would matter
    add("=== precision, with intervals (rule mapping, all findings) ===")
    for arm in ARM_ORDER:
        t = arm_totals(primary, arm, "rule_mapping")
        if not t["items_named"]:
            continue
        interval = wilson_interval(t["wrong_and_named"], t["items_named"])
        add(f"  {arm:8} {100 * interval.point:5.1f}%  "
            f"({t['wrong_and_named']}/{t['items_named']})  "
            f"95% CI {100 * interval.low:.0f}-{100 * interval.high:.0f}%")
    add("")

    # ---------------------------------------------------------------- study B
    if len(runs) > 1:
        add("=== study B: the noise floor. same instances, same configuration, "
            f"{len(runs)} runs ===")
        common = set.intersection(*[
            {i["sample_id"] for i in scored_instances(r)} for _p, r in runs])
        add(f"  instances common to every replicate: {len(common)}")
        add(f"  {'quantity':34} " + " ".join(f"{p.name[:12]:>12}" for p, _r in runs)
            + f" {'mean':>8} {'SD':>8}")

        def restrict(run: dict) -> dict:
            return {"plan": run["plan"],
                    "instances": [i for i in run["instances"]
                                  if i["sample_id"] in common]}

        rows: list[tuple[str, list[float]]] = []
        f1s = [[i["draft_score"]["f1"] * 100 for i in scored_instances(restrict(r))]
               for _p, r in runs]
        rows.append(("draft CLEAR F1 (mean, %)", [mean(v) for v in f1s]))
        for arm in ARM_ORDER:
            for mapping, label in (("rule_mapping", "recall"),
                                   ("blocker_rule_mapping", "BLOCKER recall")):
                values = []
                for _p, r in runs:
                    t = arm_totals(restrict(r), arm, mapping)
                    values.append(100 * t["recall"] if t["recall"] is not None else 0.0)
                rows.append((f"{arm} {label} (%)", values))
            fired = [100 * arm_totals(restrict(r), arm, "rule_mapping")["fired"]
                     / max(1, len(common)) for _p, r in runs]
            rows.append((f"{arm} fired (% of instances)", fired))
        for label, values in rows:
            add(f"  {label:34} " + " ".join(f"{v:12.1f}" for v in values)
                + f" {mean(values):8.1f} {stdev(values):8.2f}")
        add("")
        add("  A delta smaller than about 2 SD of its own quantity is not "
            "distinguishable from re-running the same configuration.")

    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    print(render([Path(a).resolve() for a in args]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
