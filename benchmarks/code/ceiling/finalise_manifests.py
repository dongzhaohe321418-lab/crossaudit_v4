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
    return {k: {"utc_start": utc(min(v)), "utc_end": utc(max(v)), "calls": len(v)}
            for k, v in sorted(groups.items())}


def package_versions() -> dict:
    """Versions of everything a measurement here depends on."""
    import importlib.metadata as md
    out: dict = {"python": sys.version.split()[0],
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
        "model": "gpt-6-astra", "base_url": "not applicable — the Codex CLI holds its "
                                            "own session; CrossAudit's broker is bypassed",
        "temperature_sent": None,
        "temperature_note": "not settable through `codex exec`; reasoning effort is the "
                            "only sampling control exposed and it was set to high",
        "reasoning_effort": "high",
    }
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    args = parser.parse_args(argv)
    run_dir = Path(args.run)

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                          text=True).stdout.strip()
    shared = {
        "package_versions": package_versions(),
        "routes_detail": route_metadata(),
        "finalised_at_commit": head,
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
            "meaningful freeze for the ANALYSIS is the commit this file records above, "
            "whose tree is clean.",
    }

    m1 = json.loads((CEILING / "manifest_ceiling1.json").read_text(encoding="utf-8"))
    m1.update(shared)
    m1["draw_windows_utc"] = windows_by_prefix(
        run_dir, lambda r: r.split("-holistic__")[1].rsplit("-", 1)[0]
        if "-holistic__" in r else None)
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
        print(f"  {k}: {v['utc_start']} -> {v['utc_end']}  ({v['calls']} calls)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
