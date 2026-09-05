"""Study 6 -- the arithmetic over the replicate rows. No model calls.

Every number in ``RESULTS-NOISE.md`` comes from here, and this module reads only the
committed JSONL rows, so a reader with the rows can reproduce the report without keys,
without the corpus and without the run directories.

The four spread statistics are the ones ``PREREGISTRATION-6.md`` §2 named before the run:

1. **range** of the pooled micro recall across replicates -- the kill statistic;
2. **SD** across replicates, and 2 SD, for comparability with study 5's 2.59 pp;
3. **mean absolute paired difference of the aggregate**, over every replicate pair;
4. **mean absolute paired per-instance difference**, which is what a *paired* n = 20
   contrast moves by, and the thing 2.59 pp was wrongly used as.

Intervals are 20 000-resample percentile bootstraps **over instances**, seeded 20260930,
so they are a deterministic function of the rows.

Usage::

    python benchmarks/expertlongbench/noise_report.py \\
        --replicate noise-rep1=runs/noise-rep1,runs/noise-rep1-fill1 \\
        --replicate noise-rep2=runs/noise-rep2 ...
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from stats import wilcoxon_signed_rank, wilson_interval  # noqa: E402

BOOTSTRAP_RESAMPLES = 20_000
BOOTSTRAP_SEED = 20260930

#: The preregistered kill threshold, in recall percentage points (PREREGISTRATION-6 s6).
KILL_POINTS = 8.0

MAPPINGS = ("model_mapping", "rule_mapping")


# --------------------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------------------


def load_replicate(paths: list[Path]) -> dict[str, dict]:
    """One replicate's rows, joined across its fill passes, keyed by instance.

    A later pass wins only where the earlier one never reached a provider. An audit that
    answered is kept as it answered, so a fill pass cannot overwrite a result.
    """
    by_instance: dict[str, dict] = {}
    for path in paths:
        rows_path = path / "rows.jsonl"
        if not rows_path.exists():
            raise SystemExit(f"{rows_path} does not exist")
        for line in rows_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("arm") != "cross":
                continue
            existing = by_instance.get(row["instance_id"])
            if existing is None or not (existing.get("audit") or {}).get("ok"):
                by_instance[row["instance_id"]] = row
    return by_instance


def answered(row: dict) -> bool:
    """Did a model actually reply? A call that never reached a provider is not a zero."""
    return bool((row.get("audit") or {}).get("ok"))


# --------------------------------------------------------------------------------------
# per-replicate quantities
# --------------------------------------------------------------------------------------


def pooled_recall(rows: dict[str, dict], instances: list[str], mapping: str) -> float:
    wrong = sum(rows[i]["clear"]["n_items_wrong"] for i in instances)
    hit = sum(rows[i]["scored"][mapping]["n_wrong_and_named"] for i in instances)
    return 100.0 * hit / wrong if wrong else 0.0


def instance_recall(row: dict, mapping: str) -> float:
    wrong = row["clear"]["n_items_wrong"]
    if not wrong:
        return 0.0
    return 100.0 * row["scored"][mapping]["n_wrong_and_named"] / wrong


def replicate_summary(label: str, rows: dict[str, dict], instances: list[str]) -> dict:
    wrong = sum(rows[i]["clear"]["n_items_wrong"] for i in instances)
    out: dict = {
        "label": label,
        "n_instances": len(instances),
        "n_items_wrong": wrong,
        "n_findings": sum(rows[i]["audit"]["n_findings"] for i in instances),
        "n_blockers": sum(rows[i]["audit"]["n_blockers"] for i in instances),
        "fired": sum(1 for i in instances if rows[i]["audit"]["fired"]),
        "gated": sum(1 for i in instances if rows[i]["audit"]["gated"]),
        "verdict_blocked": sum(1 for i in instances
                               if rows[i]["audit"]["verdict"] == "BLOCKED"),
        "invalid": sum(1 for i in instances if rows[i]["audit"]["invalid_reason"]),
        "repairs": sum(rows[i]["audit"].get("repair_attempts", 0) for i in instances),
        # An adjudicator call that failed leaves a finding mapped to no item, which
        # understates the MODEL mapping only. The rule mapping has no model in it, so a
        # divergence between the two here is a signal about the adjudicator, not the
        # auditor -- which is why the count is reported rather than absorbed.
        "findings_unadjudicated": sum(
            1 for i in instances for f in rows[i].get("findings", [])
            if f.get("note")),
        "cost_usd": sum(float(rows[i]["cost"]["usd"] or 0.0) for i in instances),
        "wall_s": sum(float(rows[i].get("wall_s") or 0.0) for i in instances),
    }
    out["n_advisories"] = out["n_findings"] - out["n_blockers"]
    for mapping in MAPPINGS:
        named = sum(rows[i]["scored"][mapping]["n_named"] for i in instances)
        hit = sum(rows[i]["scored"][mapping]["n_wrong_and_named"] for i in instances)
        blocker = f"blocker_{mapping.split('_')[0]}_mapping"
        out[mapping] = {
            "recall": pooled_recall(rows, instances, mapping),
            "n_named": named,
            "n_hit": hit,
            "precision": (100.0 * hit / named) if named else None,
            "precision_interval": wilson_interval(hit, named) if named else None,
            "blocker_recall": (
                100.0 * sum(rows[i]["scored"][blocker]["n_wrong_and_named"]
                            for i in instances) / out["n_items_wrong"]
                if out["n_items_wrong"] else 0.0),
        }
    return out


# --------------------------------------------------------------------------------------
# spread
# --------------------------------------------------------------------------------------


def spread_statistics(labels: list[str], per_replicate: dict[str, dict[str, dict]],
                      instances: list[str], mapping: str) -> dict:
    """The four preregistered spread statistics, with bootstrap intervals."""
    rates = [pooled_recall(per_replicate[label], instances, mapping)
             for label in labels]
    pairs = list(combinations(range(len(labels)), 2))

    def aggregate_stats(sample: list[str]) -> tuple[float, float, float, float]:
        pooled = [pooled_recall(per_replicate[label], sample, mapping)
                  for label in labels]
        rng = max(pooled) - min(pooled)
        sd = statistics.stdev(pooled) if len(pooled) > 1 else 0.0
        mad_aggregate = statistics.fmean(
            [abs(pooled[a] - pooled[b]) for a, b in pairs]) if pairs else 0.0
        per_instance = [
            abs(instance_recall(per_replicate[labels[a]][i], mapping)
                - instance_recall(per_replicate[labels[b]][i], mapping))
            for a, b in pairs for i in sample
        ]
        mad_instance = statistics.fmean(per_instance) if per_instance else 0.0
        return rng, sd, mad_aggregate, mad_instance

    point = aggregate_stats(instances)
    rng = random.Random(BOOTSTRAP_SEED)
    draws: list[tuple[float, float, float, float]] = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [instances[rng.randrange(len(instances))] for _ in instances]
        draws.append(aggregate_stats(sample))

    def interval(index: int) -> tuple[float, float]:
        values = sorted(d[index] for d in draws)
        low = values[int(0.025 * (len(values) - 1))]
        high = values[int(0.975 * (len(values) - 1))]
        return low, high

    names = ("range", "sd", "mad_aggregate", "mad_per_instance")
    result: dict = {
        "mapping": mapping,
        "per_replicate_recall": dict(zip(labels, rates)),
        "n_instances": len(instances),
        "n_replicates": len(labels),
        "n_pairs": len(pairs),
    }
    for index, name in enumerate(names):
        low, high = interval(index)
        result[name] = {"point": point[index], "ci_low": low, "ci_high": high}
    result["two_sd"] = 2.0 * point[1]

    # Per-pair detail, and a test of "the run shifted" against "instances are noisy".
    result["pairs"] = []
    for a, b in pairs:
        differences = [
            instance_recall(per_replicate[labels[a]][i], mapping)
            - instance_recall(per_replicate[labels[b]][i], mapping)
            for i in instances
        ]
        result["pairs"].append({
            "a": labels[a],
            "b": labels[b],
            "aggregate_difference": rates[a] - rates[b],
            "mean_per_instance_difference": statistics.fmean(differences),
            "mean_absolute_per_instance_difference":
                statistics.fmean([abs(d) for d in differences]),
            "max_absolute_per_instance_difference": max(abs(d) for d in differences),
            "n_instances_identical": sum(1 for d in differences if d == 0),
            "wilcoxon": str(wilcoxon_signed_rank(differences)),
        })

    # DERIVED from the preregistered per-instance differences, and reported as derived.
    #
    # A paired experiment at this n does not report a mean ABSOLUTE difference; it
    # reports a signed mean paired difference and asks whether it is distinguishable
    # from zero. Every pair below is two runs of the SAME configuration, so each pair's
    # signed mean IS such an experiment with a true effect of exactly zero. Their spread
    # is therefore the floor for a signed paired contrast at this n -- the quantity
    # study 5's primary outcome is, and the one a mean absolute difference overstates.
    nulls = [pair["mean_per_instance_difference"] for pair in result["pairs"]]
    result["null_contrast"] = {
        "values": nulls,
        "max_abs": max(abs(v) for v in nulls),
        "sd": statistics.stdev(nulls) if len(nulls) > 1 else 0.0,
        "range": max(nulls) - min(nulls),
        "note": "signed mean paired difference between two runs of one configuration; "
                "the true effect is zero by construction",
    }
    return result


def instance_table(labels: list[str], per_replicate: dict[str, dict[str, dict]],
                   instances: list[str], mapping: str) -> list[dict]:
    """Every instance's recall in every replicate, and how far it moved. Not summarised."""
    table = []
    for instance in instances:
        values = [instance_recall(per_replicate[label][instance], mapping)
                  for label in labels]
        table.append({
            "instance_id": instance,
            "n_items_wrong": per_replicate[labels[0]][instance]["clear"]["n_items_wrong"],
            "recall": dict(zip(labels, values)),
            "findings": {label: per_replicate[label][instance]["audit"]["n_findings"]
                         for label in labels},
            "range": max(values) - min(values),
            "identical_across_replicates": max(values) - min(values) == 0,
        })
    return table


# --------------------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------------------


def render(payload: dict) -> str:
    lines: list[str] = []
    add = lines.append
    add("=" * 88)
    add("STUDY 6 -- the audit-stage noise floor. Fixed drafts, fixed ground truth, "
        "one arm, K replicates")
    add("=" * 88)
    add(f"instances analysed: {payload['n_common']} of {payload['n_seeded']} "
        f"(common set: every replicate's audit reached a model)")
    add(f"replicates: {', '.join(payload['labels'])}")
    if payload["excluded"]:
        add(f"excluded from the common set: {', '.join(payload['excluded'])}")
    add("")
    add(f"{'replicate':<18} {'n':>3} {'wrong':>6} {'find':>5} {'blk':>4} {'adv':>4} "
        f"{'fired':>6} {'gated':>6} {'recall(model)':>14} {'recall(rule)':>13} "
        f"{'prec(model)':>12} {'unadj':>6} {'$':>7}")
    for summary in payload["replicates"]:
        precision = summary["model_mapping"]["precision"]
        add(f"{summary['label']:<18} {summary['n_instances']:>3} "
            f"{summary['n_items_wrong']:>6} {summary['n_findings']:>5} "
            f"{summary['n_blockers']:>4} {summary['n_advisories']:>4} "
            f"{summary['fired']:>6} {summary['gated']:>6} "
            f"{summary['model_mapping']['recall']:>13.1f}% "
            f"{summary['rule_mapping']['recall']:>12.1f}% "
            f"{'n/a' if precision is None else f'{precision:>11.1f}%'} "
            f"{summary['findings_unadjudicated']:>6} "
            f"{summary['cost_usd']:>7.3f}")
    add("")

    for mapping in MAPPINGS:
        spread = payload["spread"][mapping]
        add("-" * 88)
        add(f"SPREAD -- {mapping} (n = {spread['n_instances']} instances, "
            f"K = {spread['n_replicates']} replicates, {spread['n_pairs']} pairs)")
        add("-" * 88)
        for name, label in (("range", "range (max - min) of the aggregate"),
                            ("sd", "SD of the aggregate across replicates"),
                            ("mad_aggregate", "mean |paired difference| of the aggregate"),
                            ("mad_per_instance", "mean |paired difference| per instance")):
            entry = spread[name]
            add(f"  {label:<44} {entry['point']:>6.2f} pp   "
                f"95% CI [{entry['ci_low']:.2f}, {entry['ci_high']:.2f}]")
        add(f"  {'2 SD':<44} {spread['two_sd']:>6.2f} pp")
        null = spread["null_contrast"]
        add("")
        add("  DERIVED -- what a SIGNED paired contrast at this n returns when the true "
            "effect is zero:")
        add(f"    per-pair signed means: "
            f"{', '.join(f'{v:+.2f}' for v in null['values'])} pp")
        add(f"    SD {null['sd']:.2f} pp (2 SD {2 * null['sd']:.2f});  "
            f"largest |signed mean| {null['max_abs']:.2f} pp")
        add("")
        for pair in spread["pairs"]:
            add(f"  {pair['a']} vs {pair['b']}: aggregate "
                f"{pair['aggregate_difference']:+.2f} pp; mean per-instance "
                f"{pair['mean_per_instance_difference']:+.2f} pp; "
                f"mean |per-instance| {pair['mean_absolute_per_instance_difference']:.2f}; "
                f"max |per-instance| {pair['max_absolute_per_instance_difference']:.1f}; "
                f"identical on {pair['n_instances_identical']}; "
                f"Wilcoxon {pair['wilcoxon']}")
        add("")

    kill = payload["kill"]
    add("=" * 88)
    add("KILL CONDITION (PREREGISTRATION-6 s6): range of the aggregate round-one recall "
        f"> {KILL_POINTS} pp")
    add("=" * 88)
    add(f"  observed range (model mapping): {kill['range']:.2f} pp  ->  "
        f"{'FIRED' if kill['fired'] else 'did not fire'}")
    add(f"  observed range (rule mapping):  {kill['range_rule']:.2f} pp")
    add("")
    add(f"  study 3's +21.5 pp (2.0% -> 23.5%, n = 20) vs 2 SD of this floor "
        f"({payload['spread']['model_mapping']['two_sd']:.2f} pp): "
        f"{'survives' if 21.5 > payload['spread']['model_mapping']['two_sd'] else 'INSIDE THE FLOOR'}")
    add("")
    add("PER-INSTANCE, not summarised away")
    add("-" * 88)
    add(f"{'instance':<34} {'wrong':>5} " +
        " ".join(f"{label.replace('noise-', ''):>7}" for label in payload["labels"]) +
        f" {'range':>7}")
    for entry in payload["instances"]:
        add(f"{entry['instance_id'][-34:]:<34} {entry['n_items_wrong']:>5} " +
            " ".join(f"{entry['recall'][label]:>7.1f}" for label in payload["labels"]) +
            f" {entry['range']:>7.1f}")
    identical = sum(1 for e in payload["instances"] if e["identical_across_replicates"])
    add(f"\n  identical across every replicate: {identical}/{len(payload['instances'])}")
    add(f"  moved by more than 20 pp: "
        f"{sum(1 for e in payload['instances'] if e['range'] > 20)}"
        f"/{len(payload['instances'])}")
    add("")
    add(f"total measured spend (audit + adjudication, from the usage ledgers): "
        f"${payload['cost_usd']:.4f}")
    return "\n".join(lines)


# --------------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--replicate", action="append", required=True,
        help="LABEL=dir[,fill-dir...] -- a replicate and the fill passes that completed "
             "it. Repeat once per replicate.")
    parser.add_argument("--json", default="", help="also write the numbers here")
    parser.add_argument("--ledger-cost", type=float, default=0.0,
                        help="total spend read from the usage ledgers, for the record")
    args = parser.parse_args(argv)

    labels: list[str] = []
    per_replicate: dict[str, dict[str, dict]] = {}
    for spec in args.replicate:
        label, _, joined = spec.partition("=")
        paths = [Path(p).resolve() for p in joined.split(",") if p]
        labels.append(label)
        per_replicate[label] = load_replicate(paths)

    seeded = sorted(set().union(*(set(rows) for rows in per_replicate.values())))
    common = sorted(
        instance for instance in seeded
        if all(instance in per_replicate[label] and answered(per_replicate[label][instance])
               for label in labels))
    excluded = [i for i in seeded if i not in set(common)]

    payload = {
        "study": "6-noise",
        "labels": labels,
        "n_seeded": len(seeded),
        "n_common": len(common),
        "common_instances": common,
        "excluded": excluded,
        "bootstrap": {"resamples": BOOTSTRAP_RESAMPLES, "seed": BOOTSTRAP_SEED,
                      "unit": "instance", "kind": "percentile"},
        "kill_threshold_pp": KILL_POINTS,
        "replicates": [replicate_summary(label, per_replicate[label], common)
                       for label in labels],
        "spread": {mapping: spread_statistics(labels, per_replicate, common, mapping)
                   for mapping in MAPPINGS},
        "instances": instance_table(labels, per_replicate, common, "model_mapping"),
        "cost_usd": args.ledger_cost,
    }
    payload["kill"] = {
        "threshold_pp": KILL_POINTS,
        "range": payload["spread"]["model_mapping"]["range"]["point"],
        "range_rule": payload["spread"]["rule_mapping"]["range"]["point"],
        "fired": payload["spread"]["model_mapping"]["range"]["point"] > KILL_POINTS,
    }

    print(render(payload))
    if args.json:
        Path(args.json).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
