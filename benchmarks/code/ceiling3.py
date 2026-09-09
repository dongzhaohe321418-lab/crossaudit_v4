"""Study 18, ceiling 3 — two Anthropic auditor families on ceiling 1's frozen instances.

Preregistered in ``ceiling3/PREREGISTRATION.md``, committed before the first model call.
A driver over ``explore.py``'s resumable loop, exactly as ``ceiling.py`` is: every reading
is cached keyed by ``(kind, route, draw, instance)`` under ``records/ceiling3/cache`` and
never bought twice. Nothing in ``ceiling.py`` or ``report_ceiling.py`` (frozen, D162) is
modified; the new families are added to ``explore.ROUTES`` at runtime, by this driver only.

    self-strong     holistic audit, anthropic:claude-sonnet-4-6, generator unset   K = 8
    self-frontier   holistic audit, anthropic:claude-opus-4-8,   generator unset   K = 4

Both use the same deliberate same-vendor bypass ceiling 1's ``self`` family used
(``explore.build_project`` leaves ``generator:`` unset when auditor and generator share a
vendor), confined to the harness; ``src/`` is untouched.

    python benchmarks/code/ceiling3.py --plan
    python benchmarks/code/ceiling3.py --run <run-dir> --budget-usd 120
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "expertlongbench"))

import audit as study1  # noqa: E402
import explore  # noqa: E402
from corpus import load_problems  # noqa: E402

RECORDS = HERE / "records"
CEILING3 = RECORDS / "ceiling3"
EXPLORE_CACHE = RECORDS / "explore"
CEILING_CACHE = RECORDS / "ceiling"

#: The new routes (§1). Registered on explore.ROUTES by this driver at import time.
ROUTES = {"self-strong": "anthropic:claude-sonnet-4-6",
          "self-frontier": "anthropic:claude-opus-4-8"}
explore.ROUTES.update(ROUTES)

#: The preregistered ladder (§5): set by budget alone, never by an outcome.
LADDER = ([("self-strong", d) for d in range(1, 5)] + [("self-frontier", 1)]
          + [("self-strong", d) for d in range(5, 9)] + [("self-frontier", d) for d in range(2, 5)])


def in_scope(instances: dict, audit_set: list[str]) -> list[str]:
    return [i for i in audit_set if instances[i]["stratum"] in ("P", "C")]


def load_everywhere(key, scope: set[str]) -> dict[str, dict]:
    """Records from study 7's cache, ceiling 1's cache and this study's, in that order."""
    found: dict[str, dict] = {}
    for directory in (EXPLORE_CACHE, CEILING_CACHE, CEILING3):
        explore.EXPLORE = directory
        found.update(explore.load_detector(key, scope))
    explore.EXPLORE = CEILING3
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--run", help="run dir: study2-inputs/solutions-*.jsonl; projects and ledgers")
    parser.add_argument("--budget-usd", type=float, default=120.0)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--max-passes", type=int, default=6)
    parser.add_argument("--only-family", choices=tuple(ROUTES), default=None)
    args = parser.parse_args(argv)

    explore.EXPLORE = CEILING3
    (CEILING3 / "cache").mkdir(parents=True, exist_ok=True)
    instances = explore.load_instances()
    audit_set = explore.load_audit_set()
    scope = in_scope(instances, audit_set)
    scope_set = set(scope)
    print(f"scope: {len(scope)} instances (P + C) of {len(audit_set)}", flush=True)
    have = {("holistic", f, d): load_everywhere(("holistic", f, d), scope_set) for f, d in LADDER}
    for (f, d) in LADDER:
        n = len(have[("holistic", f, d)])
        if n:
            print(f"  {f} draw {d}: {n:3d} of {len(scope)}", flush=True)
    if args.plan:
        for f, d in LADDER:
            missing = [i for i in scope if i not in have[("holistic", f, d)]]
            print(f"ladder {f} d{d}: {len(missing)} to run")
        return 0
    if not args.run:
        parser.error("--run is required unless --plan")
    run_dir = Path(args.run)

    from run import load_credentials
    load_credentials()
    study1.register_visible_tests_check()
    constitution = study1.shipped_constitution()
    problems = {p.problem_id: p for p in load_problems()}
    solutions: dict[str, dict] = {}
    for batch in ("b1", "b2"):
        for line in (run_dir / f"study2-inputs/solutions-{batch}.jsonl").read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                solutions[f"{batch}:{row['problem_id']}"] = row
    scratch = run_dir / "projects"
    scratch.mkdir(parents=True, exist_ok=True)
    cfg_cache: dict = {}
    spend = explore.Spend(f"ceiling3-{time.strftime('%m%d%H%M%S', time.gmtime())}-")

    for family, draw in LADDER:
        if args.only_family and family != args.only_family:
            continue
        key = ("holistic", family, draw)
        missing = [i for i in scope if i not in have[key]]
        if not missing:
            print(f"ladder {family} d{draw}: already complete")
            continue
        total = spend.total()
        if args.budget_usd and total >= args.budget_usd:
            print(f"\nSTOP: spend ${total:.3f} reached the ${args.budget_usd:.2f} cap; {family} d{draw} not run")
            break
        print(f"\nladder {family} d{draw}: {len(missing)} instances (spend so far ${total:.3f})", flush=True)
        explore.run_detector(key, missing, instances=instances, problems=problems,
                             solutions=solutions, constitution=constitution,
                             cfg_cache=cfg_cache, scratch=scratch, spend=spend,
                             budget_usd=args.budget_usd, workers=args.workers,
                             property_cache_path=run_dir / "study2-inputs/properties.json",
                             max_passes=args.max_passes)
        have[key] = load_everywhere(key, scope_set)
        print(f"  {family} d{draw}: {len(have[key])} of {len(scope)}; spend ${spend.total():.3f}", flush=True)
    print(f"\nceiling-3 spend this invocation: ${spend.total():.4f}", flush=True)
    manifest = {"study": "study18 / ceiling 3", "preregistration": "benchmarks/code/ceiling3/PREREGISTRATION.md",
                "routes": ROUTES, "ladder": LADDER, "scope_n": len(scope),
                "draws_complete": {f"{f}-d{d}": len(have[("holistic", f, d)]) for f, d in LADDER},
                "spend_usd_this_invocation": round(spend.total(), 6),
                "by_run_id": {k: round(v, 6) for k, v in spend.by_run_id().items()},
                "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    (CEILING3 / f"manifest-{manifest['written_utc'].replace(':', '')}.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
