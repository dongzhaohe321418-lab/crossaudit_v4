"""Study 7 — an autonomous loop over audit architectures, scored against model-free truth.

Preregistered in ``explore/PREREGISTRATION.md``; the grid is ``explore/GRID.json`` and was
committed before any model call. This module is the loop, not a script that was run once:
it is resumable, idempotent, and it re-runs nothing it has a record for.

    spec        {detectors: [{kind, model, draw}, ...], aggregate: union|majority|unanimous}
    detector    (kind, route, draw) — a single reading of one instance
    instance    a (batch, problem_id) pair from study 2's frozen audit set

For every spec and every instance in the audit set, the loop composes the aggregate from
its detectors' records. A record comes from one of three places, in this order:

    1. study 1's committed arms       records/study1/arm-*.jsonl
    2. study 2's committed arms       records/study2/arm-*.jsonl
    3. this loop's own cache          records/explore/cache/<detector>.jsonl

Only when all three miss does a model get called, and the reply is cached keyed by
``(kind, route, draw, instance)`` before anything else happens. **That cache is what makes
the loop resumable and what bounds the spend.** Ten of the fifteen preregistered specs are
set operations over records that already existed and cost nothing.

Ground truth is a hidden test suite passing or failing, fixed by study 2's execution and
read from ``records/study2/instances.jsonl``. No model judges any outcome here, and this
study generates no code: nothing is executed, so ``execute.py``'s sandbox has nothing to
run. The flag definition is studies 1 and 2's, unchanged — at least one BLOCKER finding
from the model rung.

Selection is on the explore half, reporting on the confirm half, per the preregistration.
This module computes both and takes no view; ``report_explore.py`` applies the objective.

    python benchmarks/code/explore.py --run runs/study2 --scratch /tmp/explore \
        --grid benchmarks/code/explore/GRID.json --budget-usd 15
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "expertlongbench"))

import architectures as arch  # noqa: E402
import audit as study1  # noqa: E402
import audit2  # noqa: E402
from corpus import load_problems  # noqa: E402

REPO = HERE.parent.parent
RECORDS = HERE / "records"
EXPLORE = RECORDS / "explore"

#: The routes the grid may name. Values are ``vendor:model`` specs the harness resolves
#: through ``provider.role_for``; the cheap tier of the *self* vendor is the self route
#: itself, so there is no separate cheap-self detector.
ROUTES = {
    "cross": "openai:gpt-5.6-terra",
    "self": "anthropic:claude-haiku-4-5-20251001",
    "cheap-cross": "openai:gpt-5.6-luna",
}
GENERATOR_SPEC = "anthropic:claude-haiku-4-5-20251001"

#: Where a detector's records already exist. ``mode`` says how a row names its instance:
#: study 2 rows carry ``instance_id``; study 1 rows carry ``problem_id`` and are batch 1
#: by construction (its solutions are byte-identical to study 2's ``b1``, verified by
#: sha256 in ``verify_sources``).
FREE_SOURCES: dict[tuple[str, str, int], tuple[str, str, str]] = {
    ("holistic", "cross", 1): ("study2/arm-holistic-cross.jsonl", "instance", "study2:holistic-cross"),
    ("holistic", "cross", 2): ("study1/arm-cross.jsonl", "b1problem", "study1:cross"),
    ("holistic", "cross", 3): ("study1/arm-cross-replicate.jsonl", "b1problem", "study1:cross-replicate"),
    ("holistic", "self", 1): ("study2/arm-holistic-self.jsonl", "instance", "study2:holistic-self"),
    ("holistic", "self", 2): ("study1/arm-self.jsonl", "b1problem", "study1:self"),
    ("decomposed", "cross", 1): ("study2/arm-decomposed-cross.jsonl", "instance", "study2:decomposed-cross"),
    ("decomposed", "cross", 2): ("study2/arm-decomposed-replicate.jsonl", "instance", "study2:decomposed-replicate"),
}

#: Arm totals for study 1, whose committed rows carry no per-row cost. A spec that uses
#: one of these detectors has its cost per instance **reconstructed** from the arm total,
#: and every place that number is printed says so (EXPERIMENT_RECORD §7).
STUDY1_ARM_COST = {"study1:cross": ("cross", 235),
                   "study1:cross-replicate": ("cross-replicate", 235),
                   "study1:self": ("self", 235)}

AGGREGATES = ("union", "majority", "unanimous")


# ---------------------------------------------------------------------------------
# small statistics, stated so they can be checked
# ---------------------------------------------------------------------------------

def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """95% Wilson score interval for a binomial proportion, as a (low, high) pair."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar: a binomial sign test on the discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def rate_block(flags: dict[str, bool], ids: list[str]) -> dict:
    k = sum(1 for i in ids if flags.get(i))
    n = len(ids)
    low, high = wilson(k, n)
    return {"k": k, "n": n, "rate": (k / n if n else 0.0),
            "ci95": [round(low, 5), round(high, 5)]}


# ---------------------------------------------------------------------------------
# the substrate
# ---------------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_instances() -> dict[str, dict]:
    rows = {}
    for line in (RECORDS / "study2/instances.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row["instance_id"]] = row
    return rows


def load_audit_set() -> list[str]:
    return json.loads((RECORDS / "study2/audit_set.json").read_text(encoding="utf-8"))["instance_ids"]


def build_split(audit_set: list[str], instances: dict[str, dict], seed: int) -> dict:
    """Stratified explore/confirm halves, fixed by seed, computed once and committed.

    Stratified on ``(stratum, batch)`` so both halves carry proportionate P, C and F from
    both generation batches. Deterministic given the seed: the ids are sorted before the
    shuffle, so the split does not depend on file order.
    """
    rng = random.Random(seed)
    halves: dict[str, str] = {}
    buckets: dict[tuple[str, str], list[str]] = {}
    for iid in audit_set:
        inst = instances[iid]
        buckets.setdefault((inst["stratum"], inst["batch"]), []).append(iid)
    for key in sorted(buckets):
        ids = sorted(buckets[key])
        rng.shuffle(ids)
        for index, iid in enumerate(ids):
            halves[iid] = "explore" if index % 2 == 0 else "confirm"
    return {"seed": seed, "method": "stratified on (stratum, batch); "
                                    "random.Random(seed).shuffle over sorted ids; alternate",
            "halves": halves}


# ---------------------------------------------------------------------------------
# detectors
# ---------------------------------------------------------------------------------

def detector_key(det: dict) -> tuple[str, str, int]:
    return (det["kind"], det["model"], int(det["draw"]))


def detector_slug(key: tuple[str, str, int]) -> str:
    return f"{key[0]}__{key[1]}__d{key[2]}"


def detector_spec(key: tuple[str, str, int]) -> str:
    return ROUTES[key[1]]


def load_detector(key: tuple[str, str, int], audit_set: set[str]) -> dict[str, dict]:
    """Every record this detector already has, from the committed arms and the cache.

    Returns ``instance_id -> {flagged, cost_usd, source, cost_reconstructed}``. A record
    found here is never re-run; that is the whole point of the cache.
    """
    found: dict[str, dict] = {}
    source = FREE_SOURCES.get(key)
    if source:
        path, mode, label = source
        for line in (RECORDS / path).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            iid = row["instance_id"] if mode == "instance" else f"b1:{row['problem_id']}"
            if iid not in audit_set:
                continue
            if not row.get("ok", True):
                continue
            found[iid] = {"flagged": bool(row["flagged"]),
                          "cost_usd": row.get("cost_usd"),
                          "source": label,
                          "cost_reconstructed": "cost_usd" not in row}
    cache = EXPLORE / "cache" / f"{detector_slug(key)}.jsonl"
    if cache.exists():
        for line in cache.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("ok") and row["instance_id"] in audit_set:
                found[row["instance_id"]] = {"flagged": bool(row["flagged"]),
                                             "cost_usd": row.get("cost_usd", 0.0),
                                             "source": "explore:cache",
                                             "cost_reconstructed": False}
    return found


# ---------------------------------------------------------------------------------
# running a detector that has no record
# ---------------------------------------------------------------------------------

def build_project(root: Path, key: tuple[str, str, int], constitution: str) -> Path:
    """A real crossaudit project for this detector, from study 1's own config template.

    Where the auditor's vendor equals the generator's, ``generator:`` is left unset so the
    product's same-vendor gate has nothing to compare against — the identical deliberate
    bypass studies 1 and 2 recorded for their ``self`` arms, confined to the harness. The
    guard in ``src/`` is not touched.
    """
    from provider import role_for

    project = root / f"project-{detector_slug(key)}"
    (project / "work" / "solution").mkdir(parents=True, exist_ok=True)
    auditor = role_for(detector_spec(key))
    generator = role_for(GENERATOR_SPEC)
    generator_block = ""
    if auditor.vendor != generator.vendor:
        generator_block = audit2.GENERATOR_BLOCK.format(
            vendor=generator.vendor, provider=generator.provider,
            model=generator.model, key_env=generator.key_env)
    (project / "crossaudit.yml").write_text(audit2.CONFIG_TEMPLATE.format(
        auditor_vendor=auditor.vendor, auditor_provider=auditor.provider,
        auditor_model=auditor.model, auditor_key_env=auditor.key_env,
        generator_block=generator_block, checks="general"), encoding="utf-8")
    (project / "AUDIT_RULES.md").write_text(constitution, encoding="utf-8")
    return project


class Spend:
    """Cumulative model spend for this study, read from the projects' usage ledgers."""

    def __init__(self, run_prefix: str) -> None:
        self.prefix = run_prefix
        self.ledgers: list[Path] = []
        self._lock = threading.Lock()

    def add_ledger(self, path: Path) -> None:
        with self._lock:
            if path not in self.ledgers:
                self.ledgers.append(path)

    def by_run_id(self) -> dict[str, float]:
        from crossaudit import usage
        totals: dict[str, float] = {}
        with self._lock:
            ledgers = list(self.ledgers)
        for ledger in ledgers:
            if not ledger.exists():
                continue
            events, _ = usage.read_events(ledger)
            for event in events:
                run_id = str(event.get("run_id") or "")
                if run_id.startswith(self.prefix):
                    totals[run_id] = totals.get(run_id, 0.0) + float(event.get("api_value_usd") or 0.0)
        return totals

    def total(self) -> float:
        return sum(self.by_run_id().values())


def run_detector(key: tuple[str, str, int], missing: list[str], *, instances, problems,
                 solutions, constitution, cfg_cache, scratch: Path, spend: Spend,
                 budget_usd: float, workers: int, property_cache_path: Path) -> int:
    """Run the instances this detector has no record for, caching each one as it lands.

    Each instance gets its own ``run_id`` so its cost is read back from the usage ledger
    exactly rather than apportioned — ``run_id`` is one of the ledger's context fields, so
    this needs no change to the product's provider layer.
    """
    from crossaudit.config import load

    slug = detector_slug(key)
    cache_path = EXPLORE / "cache" / f"{slug}.jsonl"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    project = build_project(scratch, key, constitution)
    cfg = cfg_cache.setdefault(slug, load(project / "crossaudit.yml"))
    from crossaudit import usage as usage_mod
    spend.add_ledger(cfg.root / cfg.state_dir / usage_mod.LEDGER_NAME)

    client = None
    property_cache: dict = {}
    if key[0] == "decomposed":
        from provider import CrossAuditClient
        client = CrossAuditClient(cfg=cfg, phase=f"explore-{slug}", run_id=f"{spend.prefix}{slug}")
        if property_cache_path.exists():
            property_cache = json.loads(property_cache_path.read_text(encoding="utf-8"))

    # P, then C, then F: the primary outcome lives on P and the stopping rule is a budget,
    # so an early halt truncates a secondary outcome rather than the primary one.
    priority = {"P": 0, "C": 1, "F": 2}
    todo = sorted(missing, key=lambda i: (priority[instances[i]["stratum"]], i))
    handle_lock = threading.Lock()
    halted = threading.Event()
    written = 0

    def one(index_iid: tuple[int, str]) -> dict | None:
        index, iid = index_iid
        if halted.is_set():
            return None
        inst = instances[iid]
        problem = problems[inst["problem_id"]]
        solution = solutions[iid]["solution"]
        run_id = f"{spend.prefix}{slug}-{index}"[:64]
        if key[0] == "holistic":
            row = audit2.holistic_one(cfg, problem, solution, inst, constitution, run_id, slug)
        else:
            row = audit2.decomposed_one(client, detector_spec(key), problem, solution, inst,
                                        property_cache, property_cache_path)
        row["run_id"] = run_id
        row["detector"] = slug
        row["kind"], row["route"], row["draw"] = key[0], key[1], key[2]
        row["model_spec"] = detector_spec(key)
        row.pop("blocker_texts", None)     # never commit model text that quotes the corpus
        row.pop("checks", None)
        return row

    with ThreadPoolExecutor(max_workers=workers) as pool, \
            cache_path.open("a", encoding="utf-8") as handle:
        for done, row in enumerate(pool.map(one, list(enumerate(todo))), start=1):
            if row is None:
                continue
            with handle_lock:
                handle.write(json.dumps(row, sort_keys=True) + "\n")
                handle.flush()
                written += 1
            if done % 10 == 0 or done == len(todo):
                total = spend.total()
                print(f"    {slug}: {done}/{len(todo)}  ${total:.3f}", flush=True)
                if budget_usd and total >= budget_usd:
                    print(f"    STOP: spend ${total:.3f} reached the ${budget_usd:.2f} cap")
                    halted.set()

    # Stamp each cached row with the cost the ledger actually recorded for its run_id.
    costs = spend.by_run_id()
    rows = [json.loads(l) for l in cache_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    for row in rows:
        if row.get("run_id") in costs:
            row["cost_usd"] = round(costs[row["run_id"]], 8)
    cache_path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows),
                          encoding="utf-8")
    return written


# ---------------------------------------------------------------------------------
# composition and scoring
# ---------------------------------------------------------------------------------

def compose(aggregate: str, flags: list[bool]) -> bool:
    if aggregate == "union":
        return any(flags)
    if aggregate == "unanimous":
        return bool(flags) and all(flags)
    if aggregate == "majority":
        return sum(1 for f in flags if f) * 2 > len(flags)
    raise ValueError(f"unknown aggregate {aggregate!r}")


def score_spec(spec: dict, detectors: dict[tuple, dict[str, dict]], audit_set: list[str],
               instances: dict[str, dict], split: dict, study1_costs: dict) -> tuple[dict, list[dict]]:
    keys = [detector_key(d) for d in spec["detectors"]]
    flags: dict[str, bool] = {}
    rows: list[dict] = []
    covered: list[str] = []
    for iid in audit_set:
        per = [detectors[k].get(iid) for k in keys]
        if any(p is None for p in per):
            continue
        covered.append(iid)
        value = compose(spec["aggregate"], [bool(p["flagged"]) for p in per])
        flags[iid] = value
        rows.append({
            "spec_id": spec["id"], "instance_id": iid,
            "stratum": instances[iid]["stratum"], "batch": instances[iid]["batch"],
            "half": split["halves"][iid], "flagged": value,
            "detector_flags": {detector_slug(k): bool(p["flagged"]) for k, p in zip(keys, per)},
            "detector_sources": {detector_slug(k): p["source"] for k, p in zip(keys, per)},
        })

    def ids(half: str | None, stratum: str) -> list[str]:
        return [i for i in covered
                if instances[i]["stratum"] == stratum
                and (half is None or split["halves"][i] == half)]

    per_instance_cost = 0.0
    reconstructed: list[str] = []
    for k in keys:
        recs = [r for r in detectors[k].values()]
        costs = [r["cost_usd"] for r in recs if r.get("cost_usd") is not None]
        if any(r.get("cost_reconstructed") for r in recs) or not costs:
            label = FREE_SOURCES.get(k, ("", "", ""))[2]
            arm = STUDY1_ARM_COST.get(label)
            if arm:
                per_instance_cost += study1_costs[arm[0]]["usd"] / arm[1]
                reconstructed.append(detector_slug(k))
                continue
        per_instance_cost += sum(costs) / len(costs) if costs else 0.0

    entry = {
        "spec_id": spec["id"], "label": spec["label"], "aggregate": spec["aggregate"],
        "detectors": [detector_slug(k) for k in keys],
        "detector_specs": [detector_spec(k) for k in keys],
        "n_detectors": len(keys),
        "coverage": len(covered), "audit_set_n": len(audit_set),
        "cost_usd_per_instance": round(per_instance_cost, 6),
        "cost_reconstructed_for": reconstructed,
        "scored_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    for half in ("explore", "confirm", "all"):
        h = None if half == "all" else half
        entry[half] = {stratum: rate_block(flags, ids(h, stratum)) for stratum in ("P", "C", "F")}
    entry["_flags"] = flags
    return entry, rows


# ---------------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", default=str(HERE / "explore/GRID.json"))
    parser.add_argument("--run", default=str(HERE / "runs/study2"),
                        help="study 2's run dir: solutions and the property cache")
    parser.add_argument("--scratch", default="/tmp/explore-arms")
    parser.add_argument("--budget-usd", type=float, default=15.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--force", action="store_true",
                        help="re-score specs already on the leaderboard (never re-runs a "
                             "detector that has a cached record)")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what is missing and what it would cost; spend nothing")
    parser.add_argument("--probe", action="store_true",
                        help="one cheap call per route, to prove the credentials resolve")
    parser.add_argument("--free-only", action="store_true",
                        help="score only what existing records already support; run nothing")
    parser.add_argument("--allow-partial", action="store_true",
                        help="write a leaderboard row for a spec that does not cover the "
                             "whole audit set. Off by default: a partial row would be "
                             "scored on a different population from the rest of the grid.")
    args = parser.parse_args(argv)

    grid = json.loads(Path(args.grid).read_text(encoding="utf-8"))
    EXPLORE.mkdir(parents=True, exist_ok=True)
    (EXPLORE / "cache").mkdir(parents=True, exist_ok=True)

    instances = load_instances()
    audit_set = load_audit_set()
    audit_ids = set(audit_set)

    split_path = EXPLORE / "split.json"
    if split_path.exists():
        split = json.loads(split_path.read_text(encoding="utf-8"))
    else:
        split = build_split(audit_set, instances, int(grid["split_seed"]))
        split_path.write_text(json.dumps(split, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    counts: dict[str, dict[str, int]] = {}
    for iid in audit_set:
        counts.setdefault(split["halves"][iid], {}).setdefault(instances[iid]["stratum"], 0)
        counts[split["halves"][iid]][instances[iid]["stratum"]] += 1
    print(f"split (seed {split['seed']}): "
          + "  ".join(f"{h}={counts[h]}" for h in sorted(counts)), flush=True)

    keys = sorted({detector_key(d) for spec in grid["specs"] for d in spec["detectors"]})
    detectors = {k: load_detector(k, audit_ids) for k in keys}
    missing = {k: [i for i in audit_set if i not in detectors[k]] for k in keys}
    for k in keys:
        print(f"detector {detector_slug(k):48s} have {len(detectors[k]):3d}  "
              f"missing {len(missing[k]):3d}", flush=True)

    if args.dry_run:
        print(f"\ndry run: {sum(len(v) for v in missing.values())} detector-instances to run")
        return 0

    study1_costs = json.loads((RECORDS / "study1/cost.json").read_text(encoding="utf-8"))
    spend = Spend("explore-")

    todo_keys = [] if args.free_only else [k for k in keys if missing[k]]
    if todo_keys or args.probe:
        from run import load_credentials
        load_credentials()
        study1.register_visible_tests_check()
        constitution = study1.shipped_constitution()
        problems = {p.problem_id: p for p in load_problems()}
        run_dir = Path(args.run)
        solutions: dict[str, dict] = {}
        for batch in sorted({inst["batch"] for inst in instances.values()}):
            for line in (run_dir / f"solutions-{batch}.jsonl").read_text(
                    encoding="utf-8").splitlines():
                if line.strip():
                    row = json.loads(line)
                    solutions[f"{batch}:{row['problem_id']}"] = row
        scratch = Path(args.scratch)
        scratch.mkdir(parents=True, exist_ok=True)
        cfg_cache: dict = {}

        if args.probe:
            probe(grid, scratch, constitution, cfg_cache, spend)
            return 0

        for k in todo_keys:
            if spend.total() >= args.budget_usd:
                print(f"budget ${args.budget_usd:.2f} reached; {detector_slug(k)} not run")
                break
            print(f"\nrunning {detector_slug(k)}: {len(missing[k])} instances", flush=True)
            run_detector(k, missing[k], instances=instances, problems=problems,
                         solutions=solutions, constitution=constitution,
                         cfg_cache=cfg_cache, scratch=scratch, spend=spend,
                         budget_usd=args.budget_usd, workers=args.workers,
                         property_cache_path=run_dir / "properties.json")
            detectors[k] = load_detector(k, audit_ids)
        print(f"\nmodel spend this invocation: ${spend.total():.4f}", flush=True)

    leaderboard = EXPLORE / "leaderboard.jsonl"
    already: dict[str, dict] = {}
    if leaderboard.exists() and not args.force:
        for line in leaderboard.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                already[row["spec_id"]] = row

    entries: list[dict] = []
    all_rows: list[dict] = []
    for spec in grid["specs"]:
        if spec["id"] in already:
            print(f"spec {spec['id']:14s} already scored, skipping (--force to redo)")
            entries.append(already[spec["id"]])
            continue
        entry, rows = score_spec(spec, detectors, audit_set, instances, split, study1_costs)
        if entry["coverage"] < entry["audit_set_n"] and not args.allow_partial:
            # A partial spec would be scored on a different population from the rest of
            # the grid, and the leaderboard is idempotent — writing it would freeze the
            # wrong number in place. Leave it unscored and say so.
            print(f"spec {spec['id']:14s} UNSCORED: covers {entry['coverage']} of "
                  f"{entry['audit_set_n']} instances (a detector is still missing)")
            continue
        entries.append(entry)
        all_rows.extend(rows)
        c = entry["confirm"]
        print(f"spec {spec['id']:14s} coverage {entry['coverage']:3d}  "
              f"confirm P {c['P']['k']:3d}/{c['P']['n']:3d}  "
              f"C {c['C']['k']:3d}/{c['C']['n']:3d}  "
              f"${entry['cost_usd_per_instance']:.4f}/inst", flush=True)

    if all_rows or args.force:
        mode = "w" if args.force else "a"
        with (EXPLORE / "rows.jsonl").open(mode, encoding="utf-8") as handle:
            for row in all_rows:
                handle.write(json.dumps(row, sort_keys=True) + "\n")
    with leaderboard.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps({k: v for k, v in entry.items() if not k.startswith("_")},
                                    sort_keys=True) + "\n")

    write_manifest(grid, split, detectors, entries, spend)
    return 0


def probe(grid: dict, scratch: Path, constitution: str, cfg_cache: dict, spend: Spend) -> None:
    """One cheap call per route before any budget is committed. Two studies died on
    exhausted credit; this proves the credentials resolve and the routes answer."""
    from crossaudit.config import load
    from crossaudit import usage as usage_mod
    from provider import CrossAuditClient

    for alias in sorted({d["model"] for spec in grid["specs"] for d in spec["detectors"]}):
        key = ("holistic", alias, 0)
        project = build_project(scratch, key, constitution)
        cfg = load(project / "crossaudit.yml")
        spend.add_ledger(cfg.root / cfg.state_dir / usage_mod.LEDGER_NAME)
        client = CrossAuditClient(cfg=cfg, phase="explore-probe", run_id="explore-probe")
        reply = client.complete(model=ROUTES[alias], system="Answer in one word.",
                                user="Say READY.")
        print(f"probe {alias:12s} {ROUTES[alias]:34s} -> {reply.text.strip()[:40]!r}  "
              f"${reply.cost_usd:.6f}", flush=True)
    print(f"probe spend ${spend.total():.6f}")


def write_manifest(grid: dict, split: dict, detectors: dict, entries: list[dict],
                   spend: Spend) -> None:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                          text=True).stdout.strip()
    porcelain = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                               capture_output=True, text=True).stdout
    files = ["benchmarks/code/explore.py", "benchmarks/code/explore/GRID.json",
             "benchmarks/code/explore/PREREGISTRATION.md",
             "benchmarks/code/report_explore.py"]
    manifest = {
        "study": "explore (study 7)",
        "grid_id": grid["grid_id"],
        "code": {"commit": head, "status_porcelain": porcelain,
                 "files": {f: (sha256_file(REPO / f) if (REPO / f).exists() else None)
                           for f in files}},
        "data": {"audit_set": "benchmarks/code/records/study2/audit_set.json",
                 "audit_set_sha256": sha256_file(RECORDS / "study2/audit_set.json"),
                 "instances_sha256": sha256_file(RECORDS / "study2/instances.jsonl"),
                 "corpus": json.loads((HERE / "manifest_corpus.json").read_text(encoding="utf-8"))
                 if (HERE / "manifest_corpus.json").exists() else None},
        "models": {"routes": ROUTES, "generator": GENERATOR_SPEC,
                   "roles": {"detector": "auditor", "judge": "none — ground truth is a "
                                                             "hidden test suite"}},
        "seed": {"split": split["seed"], "method": split["method"]},
        "environment": {"python": sys.version.split()[0], "platform": sys.platform},
        "detectors": {detector_slug(k): {"records": len(v),
                                         "sources": sorted({r["source"] for r in v.values()})}
                      for k, v in sorted(detectors.items())},
        "spend_usd_by_run_id_prefix": round(spend.total(), 6),
        "specs_scored": [e["spec_id"] for e in entries],
        "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (EXPLORE / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                                           encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
