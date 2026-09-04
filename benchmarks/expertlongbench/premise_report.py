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

import math  # noqa: E402
import random  # noqa: E402

from stats import mean, stdev, wilcoxon_signed_rank, wilson_interval  # noqa: E402

#: Resamples for the paired-difference confidence interval. Fixed, and the RNG is
#: seeded, so the interval is a deterministic function of the recorded rows.
BOOTSTRAP_N = 20000
BOOTSTRAP_SEED = 20261104


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar: the paired test for a binary outcome seen twice.

    ``b`` and ``c`` are the discordant counts -- instances where one arm gated and the
    other did not. Concordant instances carry no information about a difference and are
    correctly ignored. Under the null each discordant instance is a fair coin, so the
    p value is the two-sided binomial tail at p = 1/2.
    """
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def paired_binary(run: dict, arm_a: str, arm_b: str, field: str = "gated"):
    """Per-instance binary outcome for two arms on the same draft."""
    pairs = []
    for instance in scored_instances(run):
        a, b = instance["arms"].get(arm_a), instance["arms"].get(arm_b)
        if not a or not b or not a["ok"] or not b["ok"]:
            continue
        pairs.append((instance["sample_id"], bool(a.get(field)), bool(b.get(field))))
    return pairs


def paired_ci(differences: list[float], confidence: float = 0.95) -> tuple[float, float]:
    """Percentile bootstrap CI for the mean paired difference.

    A bootstrap rather than a t interval because these differences are recall
    differences on 6-item rubrics: they are discrete, bounded, and pile up on zero, so
    the normality the t interval assumes is not available. Resampling is over
    INSTANCES, which is the unit of independence here -- one draft, judged by every arm.
    """
    if not differences:
        return (float("nan"), float("nan"))
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(differences)
    means = []
    for _ in range(BOOTSTRAP_N):
        means.append(sum(differences[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    tail = (1 - confidence) / 2
    return (means[int(tail * BOOTSTRAP_N)], means[min(BOOTSTRAP_N - 1,
                                                      int((1 - tail) * BOOTSTRAP_N))])

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
    add("=== preregistered comparisons (PREREGISTRATION-5.md) ===")
    add("  effect = mean paired difference in recall, percentage points, first arm minus")
    add("  second; CI = 20000-resample percentile bootstrap over instances; p = exact")
    add("  two-sided Wilcoxon signed-rank, ties dropped as the test requires.")
    add("")
    add(f"  {'comparison':22} {'mapping':14} {'n':>3} {'A%':>6} {'B%':>6} "
        f"{'effect':>8} {'95% CI':>18} {'b/w/t':>9} {'p':>8} {'used':>5}")
    for arm_a, arm_b in (("cross", "self"), ("cross", "sibling"), ("sibling", "self")):
        for mapping in ("model_mapping", "rule_mapping"):
            pairs = paired_recall(primary, arm_a, arm_b, mapping)
            if not pairs:
                continue
            diffs = [a - b for _id, a, b in pairs]
            w = wilcoxon_signed_rank(diffs)
            low, high = paired_ci(diffs)
            better = sum(1 for d in diffs if d > 0)
            worse = sum(1 for d in diffs if d < 0)
            add(f"  {arm_a + ' - ' + arm_b:22} {mapping:14} {len(pairs):>3} "
                f"{100 * mean([a for _i, a, _b in pairs]):6.1f} "
                f"{100 * mean([b for _i, _a, b in pairs]):6.1f} "
                f"{100 * mean(diffs):+8.1f} "
                f"{'[' + f'{100 * low:+.1f}, {100 * high:+.1f}' + ']':>18} "
                f"{f'{better}/{worse}/{len(diffs) - better - worse}':>9} "
                f"{w.p_value:8.4f} {w.n_used:>5}")
    add("")
    add("  S1 -- gate rate (PREREGISTRATION-5B). Proportion of instances on which the")
    add("  arm raised at least one BLOCKER. An ADVISORY gates nothing and ships the draft.")
    add(f"  {'comparison':22} {'n':>3} {'A%':>6} {'B%':>6} {'effect':>8} "
        f"{'95% CI':>18} {'b/c':>7} {'McNemar p':>10}")
    for arm_a, arm_b in (("cross", "self"), ("cross", "sibling"), ("sibling", "self")):
        pairs = paired_binary(primary, arm_a, arm_b)
        if not pairs:
            continue
        b = sum(1 for _i, x, y in pairs if x and not y)
        c = sum(1 for _i, x, y in pairs if y and not x)
        diffs = [float(x) - float(y) for _i, x, y in pairs]
        low, high = paired_ci(diffs)
        add(f"  {arm_a + ' - ' + arm_b:22} {len(pairs):>3} "
            f"{100 * mean([float(x) for _i, x, _y in pairs]):6.1f} "
            f"{100 * mean([float(y) for _i, _x, y in pairs]):6.1f} "
            f"{100 * mean(diffs):+8.1f} "
            f"{'[' + f'{100 * low:+.1f}, {100 * high:+.1f}' + ']':>18} "
            f"{f'{b}/{c}':>7} {mcnemar_exact(b, c):10.4f}")
    add("")
    add("  S2 -- blocking recall (PREREGISTRATION-5B): recall over BLOCKER findings only")
    for arm_a, arm_b in (("cross", "self"), ("cross", "sibling")):
        for mapping in ("blocker_model_mapping", "blocker_rule_mapping"):
            pairs = paired_recall(primary, arm_a, arm_b, mapping)
            if not pairs:
                continue
            diffs = [a - b for _id, a, b in pairs]
            w = wilcoxon_signed_rank(diffs)
            low, high = paired_ci(diffs)
            better = sum(1 for d in diffs if d > 0)
            worse = sum(1 for d in diffs if d < 0)
            add(f"  {arm_a + ' - ' + arm_b:22} {mapping.replace('_mapping',''):14} "
                f"{len(pairs):>3} "
                f"{100 * mean([a for _i, a, _b in pairs]):6.1f} "
                f"{100 * mean([b for _i, _a, b in pairs]):6.1f} "
                f"{100 * mean(diffs):+8.1f} "
                f"{'[' + f'{100 * low:+.1f}, {100 * high:+.1f}' + ']':>18} "
                f"{f'{better}/{worse}/{len(diffs) - better - worse}':>9} "
                f"{w.p_value:8.4f} {w.n_used:>5}")
    add("")
    add("  severity mix per arm (what the arm called the things it found)")
    for arm in ARM_ORDER:
        rows_ = [i["arms"][arm] for i in scored_instances(primary)
                 if i["arms"].get(arm) and i["arms"][arm]["ok"]]
        if not rows_:
            continue
        blockers = sum(r["n_blockers"] for r in rows_)
        total = sum(r["n_findings"] for r in rows_)
        add(f"    {arm:8} findings {total:>3}  BLOCKER {blockers:>3}  "
            f"ADVISORY {total - blockers:>3}  "
            f"gated {sum(1 for r in rows_ if r.get('gated')):>2}/{len(rows_)}")
    add("")
    for arm_a, arm_b in (("cross", "self"), ("cross", "sibling")):
        pairs = paired_recall(primary, arm_a, arm_b, "blocker_rule_mapping")
        if not pairs:
            continue
        diffs = [a - b for _id, a, b in pairs]
        w = wilcoxon_signed_rank(diffs)
        low, high = paired_ci(diffs)
        add(f"  {arm_a + ' - ' + arm_b:22} {'blocker_rule':14} {len(pairs):>3} "
            f"{100 * mean([a for _i, a, _b in pairs]):6.1f} "
            f"{100 * mean([b for _i, _a, b in pairs]):6.1f} "
            f"{100 * mean(diffs):+8.1f} "
            f"{'[' + f'{100 * low:+.1f}, {100 * high:+.1f}' + ']':>18} "
            f"{'':>9} {w.p_value:8.4f} {w.n_used:>5}")
    add("")

    # precision intervals, because a collapse there would matter
    add("=== rates with Wilson intervals (rule mapping, all findings) ===")
    add(f"  {'arm':8} {'item precision':>26} {'recall':>26} {'fired':>22} {'gated':>22}")
    for arm in ARM_ORDER:
        t = arm_totals(primary, arm, "rule_mapping")
        if not t["judged"]:
            continue
        def show(hit: int, total: int) -> str:
            if not total:
                return "n/a"
            i = wilson_interval(hit, total)
            return (f"{100 * i.point:.1f}% ({hit}/{total}) "
                    f"[{100 * i.low:.0f},{100 * i.high:.0f}]")
        add(f"  {arm:8} {show(t['wrong_and_named'], t['items_named']):>26} "
            f"{show(t['wrong_and_named'], t['items_wrong']):>26} "
            f"{show(t['fired'], t['judged']):>22} "
            f"{show(t['gated'], t['judged']):>22}")
    add("")
    add("  reply validator rejections per arm (a rejected reply raises no findings):")
    for arm in ARM_ORDER:
        t = arm_totals(primary, arm, "rule_mapping")
        if t["judged"]:
            add(f"    {arm:8} invalid {t['invalid']:>2}  errored {t['errors']:>2}  "
                f"of {t['judged']}")
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
            gated = [100 * arm_totals(restrict(r), arm, "rule_mapping")["gated"]
                     / max(1, len(common)) for _p, r in runs]
            rows.append((f"{arm} GATE RATE (%)", gated))
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
