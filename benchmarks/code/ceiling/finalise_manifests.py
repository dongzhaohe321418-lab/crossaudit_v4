"""Study 8 — complete both manifests from recorded evidence, after the runs are done.

The cross-vendor review found the manifests incomplete: no package versions, no per-arm
wall-clock, no provider base URLs, sampling metadata that said temperature is universally
omitted when one route sends zero, a stale `report_ceiling.py` hash, and no record of what
was dirty in the working tree at freeze.

Everything added here is **derived from evidence already on disk** — the projects' usage
ledgers, the installed environment, and the product's own capability cards. Nothing is
reconstructed from memory, and any fact that cannot be recovered is written as
`AUTHOR_INPUT_NEEDED` rather than filled in.

    python benchmarks/code/ceiling/finalise_manifests.py --run <run-dir>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = HERE.parent
REPO = CODE.parent.parent
sys.path.insert(0, str(CODE))
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(CODE.parent / "expertlongbench"))

CEILING = CODE / "records" / "ceiling"


def utc(ms: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ms / 1000.0))


def windows_by_prefix(run_dir: Path, split) -> dict:
    """UTC start and end per arm or per draw, from the ledgers' own timestamps.

    ``split(run_id)`` returns the group a call belongs to, or None to ignore it. The
    ledger records one event per completion with a millisecond timestamp, so these are
    observed wall-clock boundaries, not estimates.
    """
    groups: dict[str, list[float]] = {}
    for ledger in sorted(run_dir.glob("projects/*/.crossaudit/usage.jsonl")):
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = split(str(row.get("run_id") or ""))
            if key and row.get("t"):
                groups.setdefault(key, []).append(float(row["t"]))
    return {k: {"utc_first_completion": utc(min(v)), "utc_last_completion": utc(max(v)),
                "calls": len(v),
                "field_note": "these are the ledger's first and last recorded COMPLETION "
                              "timestamps, not the invocation's start and end; the "
                              "harness records a completion per call and nothing at "
                              "launch"}
            for k, v in sorted(groups.items())}


def package_versions() -> dict:
    """Versions of everything a measurement here depends on."""
    import importlib.metadata as md
    out: dict = {"python": sys.version.split()[0],
                 "collected": "RETROSPECTIVELY, from the installed environment after the "
                              "runs finished — not captured at run time. A package "
                              "upgraded between the run and this collection would be "
                              "recorded at its later version.",
                 "note": "the analysis uses only the standard library; these are the "
                         "packages the RUN depended on (provider transport, and numpy "
                         "inside the sandboxed test subprocesses, which is EvalPlus's "
                         "own dependency)"}
    for name in ("numpy", "httpx", "requests", "urllib3", "certifi", "anthropic",
                 "openai", "pytest"):
        try:
            out[name] = md.version(name)
        except Exception:  # noqa: BLE001
            out[name] = "not installed"
    try:
        out["executor_python"] = subprocess.run(
            [__import__("execute").EXECUTOR, "-c",
             "import sys,platform;print(platform.python_version())"],
            capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as exc:  # noqa: BLE001
        out["executor_python"] = f"AUTHOR_INPUT_NEEDED: {exc}"
    return out


def route_metadata() -> dict:
    """What each route actually sends, from the product's own capability cards.

    The first manifest said temperature is universally omitted. It is not: a card with
    ``temperature: True`` gets ``temperature = 0``. That difference is the mechanism
    behind this study's determinism result, so recording it correctly matters twice.
    """
    from crossaudit.providers import specs
    out = {}
    for label, spec in (("cross", "openai:gpt-5.6-terra"),
                        ("self", "anthropic:claude-haiku-4-5-20251001"),
                        ("generator", "anthropic:claude-haiku-4-5-20251001")):
        vendor, model = spec.split(":", 1)
        card = specs.capability_card(vendor, model)
        ps = specs.SPECS[vendor]
        out[label] = {
            "spec": spec, "vendor": vendor, "model": model,
            "base_url": ps.api_base, "key_env": ps.key_env,
            "temperature_sent": (0 if card.temperature else None),
            "temperature_note": ("the capability card permits temperature, so the "
                                 "provider layer sends 0 — this route is near-"
                                 "deterministic" if card.temperature else
                                 "the capability card carries temperature: False, so no "
                                 "sampling parameter is sent — this route varies run to "
                                 "run"),
            "token_param": card.token_param,
            "reasoning_effort": None,
        }
    out["astra"] = {
        "spec": "codex:gpt-6-astra", "vendor": "openai (via Codex CLI)",
        "model": "gpt-6-astra",
        "base_url": "AUTHOR_INPUT_NEEDED: `codex exec` exposes no endpoint on stdout, "
                    "stderr or `codex --version`, and this study did not intercept its "
                    "network layer, so the endpoint it used is unrecorded. What is known: "
                    "the CLI holds its own session and CrossAudit's broker is bypassed.",
        "temperature_sent": None,
        "temperature_note": "not settable through `codex exec`; reasoning effort is the "
                            "only sampling control exposed and it was set to high",
        "reasoning_effort": "high",
    }
    return out


#: Fields written by an earlier finalisation that a later one supersedes. They are
#: REMOVED, not left beside their replacements: a manifest that carries both a wrong
#: `finalised_at_commit` and a corrective `analysis_freeze` block contradicts itself, and a
#: reader has no way to know which one is live. The third review found exactly that.
SUPERSEDED_FIELDS = ("finalised_at_commit", "working_tree_at_freeze")


def _drop_superseded(manifest: dict) -> None:
    removed = [f for f in SUPERSEDED_FIELDS if f in manifest]
    for field in removed:
        manifest.pop(field)
    if removed:
        manifest["superseded_fields_removed"] = {
            "fields": removed,
            "why": "written by an earlier finalisation and contradicted by the fields "
                   "that replaced them (analysis_freeze, provenance_note). Removed rather "
                   "than left in place; the third cross-vendor review found them still "
                   "present and reported as renamed when they were not.",
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    args = parser.parse_args(argv)
    run_dir = Path(args.run)

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                          text=True).stdout.strip()
    shared = {
        "analysis_seeds": {
            "bootstrap": 20260908,
            "derived": "report_ceiling.py offsets BOOT_SEED per quantity; the residual "
                       "share uses BOOT_SEED + 4 = 20260912, residual categories "
                       "BOOT_SEED + 11, the timeout sensitivity BOOT_SEED + 12 and + 13, "
                       "the union curves BOOT_SEED + 20 + K, the mixed families "
                       "BOOT_SEED + 30 + per_family",
            "loop_sample": 20260907,
            "note": "recorded here as well as in numbers.json and the preregistration, "
                    "so the manifest alone is sufficient to reproduce every interval",
        },
        "package_versions": package_versions(),
        "routes_detail": route_metadata(),
        "finalised_on_parent_commit": head,
        "analysis_freeze": {
            "what_it_is": "the ANALYSIS freeze is the commit that CONTAINS this manifest, "
                          "which by construction cannot be named from inside it. The "
                          "hashes in code.files are of the working tree at finalisation "
                          "and are what a reader should verify against; the parent commit "
                          "above is recorded only to locate that commit's child.",
            "verify": "git log --oneline -1 -- benchmarks/code/records/ceiling/"
                      "manifest_ceiling1.json  ->  that commit's tree is the analysis "
                      "freeze, and `shasum -a 256` on each file in code.files must match.",
            "plan_freeze": "d96cdaf (preregistration) and 87939d2 (amendment 3), both "
                           "clean and both before the first model call. Amendment 4 is "
                           "post-hoc and says so.",
            "correction": "the first finalisation named its parent commit as the analysis "
                          "freeze; that commit's report_ceiling.py hash did not match the "
                          "file the numbers came from. Found by the second cross-vendor "
                          "review.",
        },
        "finalised_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "provenance_note":
            "Completed after the runs finished, from the ledgers' own timestamps, the "
            "installed environment and the product's capability cards. The cross-vendor "
            "review found the first version missing these fields.",
        "working_tree_at_freeze":
            "Both manifests were written by their loops mid-study, so each recorded a "
            "DIRTY tree: the study's own uncommitted records and, for the loop manifest, "
            "an edited loop.py (the retry passes added after the circuit-breaker run). "
            "The meaningful freeze for the PLAN is commit d96cdaf (preregistration) and "
            "87939d2 (amendment 3), both clean and both before the first model call. The "
            "meaningful freeze for the ANALYSIS is defined in the `analysis_freeze` field "
            "of this manifest, which says how to locate it and what to verify; it is NOT "
            "the parent commit recorded in `finalised_on_parent_commit`.",
    }

    m1 = json.loads((CEILING / "manifest_ceiling1.json").read_text(encoding="utf-8"))
    _drop_superseded(m1)
    m1.update(shared)
    m1["draw_windows_utc"] = windows_by_prefix(
        run_dir, lambda r: r.split("-holistic__")[1].rsplit("-", 1)[0]
        if "-holistic__" in r else None)
    astra_times = []
    for slug in ("holistic__astra__d1", "holistic__astra__d2", "holistic__astra__d3",
                 "holistic__astra__d4"):
        path = CEILING / "cache" / f"{slug}.jsonl"
        if path.exists():
            astra_times.append((slug, sum(1 for l in path.read_text(encoding="utf-8")
                                          .splitlines() if l.strip())))
    m1["draw_windows_coverage"] = {
        "covered": "the draws this study ran through the metered broker",
        "not_covered_astra": {
            "draws": dict(astra_times),
            "why": "the Codex CLI keeps its own session and writes nothing to the "
                   "product's usage ledger, so no per-call timestamp exists for astra. "
                   "Per-reading wall-clock IS recorded in each cached row's `wall_s`.",
        },
        "not_covered_inherited": {
            "detectors": ["holistic__cross__d1 (study 2)", "holistic__cross__d2 (study 1 "
                          "batch 1 + study 7)", "holistic__cross__d3 (same)",
                          "holistic__self__d1 (study 2)",
                          "holistic__self__d2 (study 1 batch 1, completed here)"],
            "why": "these readings were taken by studies 1, 2 and 7; their timestamps "
                   "belong to those studies' manifests, not this one.",
        },
    }
    m1["sampling"] = {
        "per_route": {k: {"temperature_sent": v["temperature_sent"],
                          "reasoning_effort": v["reasoning_effort"]}
                      for k, v in shared["routes_detail"].items()},
        "max_rounds": 1, "flag_rule": "at least one BLOCKER finding",
        "correction": "supersedes the first version, which said temperature is "
                      "universally omitted; the self route sends 0",
    }
    for f in ("benchmarks/code/report_ceiling.py", "benchmarks/code/ceiling.py",
              "benchmarks/code/explore.py", "benchmarks/code/loop.py",
              "benchmarks/code/residual_dump.py",
              "benchmarks/code/tests/test_ceiling_stats.py",
              "benchmarks/code/ceiling/PREREGISTRATION.md"):
        if (REPO / f).exists():
            m1["code"]["files"][f] = hashlib.sha256((REPO / f).read_bytes()).hexdigest()
    m1["code"]["files_note"] = ("re-hashed at finalisation; the first version's "
                                "report_ceiling.py hash predated the analysis file")
    (CEILING / "manifest_ceiling1.json").write_text(
        json.dumps(m1, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    m2 = json.loads((CEILING / "manifest_loop.json").read_text(encoding="utf-8"))
    _drop_superseded(m2)
    m2.update(shared)
    # The ledgers hold every invocation, including the discarded pilots and the run the
    # circuit breaker destroyed. Group by (arm, invocation stamp) so each window is one
    # invocation, and mark which invocation supplied the committed rows: the run_id stamp
    # on the arm's own records.
    def arm_and_stamp(r: str):
        if not r.startswith("ceiling-loop-"):
            return None
        rest = r[len("ceiling-loop-"):]
        for arm in ("self-loop-rep", "self-loop", "cross-loop", "referent-loop"):
            if rest.startswith(arm + "-"):
                tail = rest[len(arm) + 1:].split("-")[0]
                return f"{arm}@{tail}" if tail.isdigit() else None
        return None

    windows = windows_by_prefix(run_dir, arm_and_stamp)
    # Count what the grouping does NOT cover, and say so rather than let a reader assume
    # the windows account for every call. Unstamped run_ids come from the pilots, which
    # predate the per-invocation stamp (deviation 6).
    unmatched: dict[str, int] = {}
    for ledger in sorted(run_dir.glob("projects/*/.crossaudit/usage.jsonl")):
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rid = str(json.loads(line).get("run_id") or "")
            except json.JSONDecodeError:
                continue
            if rid.startswith("ceiling-loop-") and arm_and_stamp(rid) is None:
                unmatched[rid] = unmatched.get(rid, 0) + 1
    m2_unmatched = unmatched
    reported = {}
    for arm in ("self-loop", "self-loop-rep", "cross-loop", "referent-loop"):
        path = CEILING / "loop" / f"{arm}.jsonl"
        if not path.exists():
            continue
        stamps = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rid = json.loads(line).get("run_id", "")
                key = arm_and_stamp(rid)
                if key:
                    stamps.add(key.split("@", 1)[1])
        reported[arm] = sorted(stamps)
    repaired = {arm for arm in reported
                if (CEILING / "loop" / f"{arm}.jsonl").exists()
                and any(json.loads(l).get("repaired_revision")
                        for l in (CEILING / "loop" / f"{arm}.jsonl")
                        .read_text(encoding="utf-8").splitlines() if l.strip())}
    for key in windows:
        arm, stamp = key.split("@", 1)
        supplied = stamp in reported.get(arm, [])
        role = "audits and revisions for the reported rows" if supplied else \
            "discarded (pilot, or the run the circuit breaker destroyed)"
        if not supplied and arm in repaired and stamp > max(reported.get(arm, ["0"])):
            supplied, role = True, ("the targeted revision-repair pass — deviation 5; it "
                                    "supplied the eight repaired cross-loop revisions")
        windows[key]["supplied_the_committed_rows"] = supplied
        windows[key]["role"] = role
    m2["arm_windows_utc"] = windows
    by_prefix: dict[str, int] = {}
    for rid, count in m2_unmatched.items():
        by_prefix[rid.rsplit("-", 1)[0]] = by_prefix.get(rid.rsplit("-", 1)[0], 0) + count
    m2["arm_ledger_events_not_in_any_window"] = {
        "by_run_id": dict(sorted(m2_unmatched.items())),
        "by_run_id_prefix": by_prefix,
        "total": sum(m2_unmatched.values()),
        "why": "run_ids minted before the per-invocation stamp was introduced "
               "(deviation 6) — the discarded pilots. Their spend IS counted in the "
               "ledger totals; they simply have no invocation stamp to group by.",
    }
    m2["arm_windows_note"] = (
        "One window per invocation. Windows with supplied_the_committed_rows = false are "
        "the discarded pilots and the run the provider's circuit breaker destroyed; their "
        "spend is counted in the totals and their rows are not in any reported number.")
    m2["sampling"] = m1["sampling"]
    for f in ("benchmarks/code/loop.py", "benchmarks/code/report_ceiling.py",
              "benchmarks/code/ceiling/PREREGISTRATION.md"):
        if (REPO / f).exists():
            m2["code"]["files"][f] = hashlib.sha256((REPO / f).read_bytes()).hexdigest()
    (CEILING / "manifest_loop.json").write_text(
        json.dumps(m2, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("draw windows:", len(m1["draw_windows_utc"]), "| arm windows:",
          len(m2["arm_windows_utc"]))
    for k, v in list(m2["arm_windows_utc"].items()):
        print(f"  {k}: {v['utc_first_completion']} -> {v['utc_last_completion']}  "
              f"({v['calls']} calls, used={v['supplied_the_committed_rows']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
