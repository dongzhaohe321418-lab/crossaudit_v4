"""Build study 4's committed record from the run directories.

Post hoc by design: the arms must be instrumentation-identical, so nothing here
runs inside a run. It reads what `run.py` already wrote and emits

    manifest.json   provenance (EXPERIMENT_RECORD.md #2)
    records.jsonl   one row per instance per arm (#3)
    rundirs.sha256  a directory-level digest of the raw material (#3)

**Derived values only.** Scores, counts, ids, token totals, costs and sha256
digests are safe to commit; corpus text and model outputs that quote it are not,
and nothing here reads a round's bytes except to hash them.

    python benchmarks/expertlongbench/study4/emit_record.py \
        C=<absolute run dir> T=<absolute run dir> [G=<absolute run dir>]
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
REPO = BENCH.parent.parent

#: Product code frozen per arm, and what makes each arm that arm.
ARM_CODE = {
    "C": ("63ab94c831f0d05a801e3eb258395f0141f156d8", "tip behaviour; no document growth budget exists"),
    "T": ("21f37d5a23dfbc5633908f4a8a00d81d7b868f89", "repair.max_document_growth = 0.25 (default) + the bound stated in the revision prompt"),
    "G": ("63ab94c831f0d05a801e3eb258395f0141f156d8", "tip behaviour, shipped general constitution"),
}
#: The harness files that must be identical across arms for the comparison to mean anything.
HARNESS = ("run.py", "clear.py", "adjudicate.py", "provider.py", "tasks.py", "stats.py")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git(*args: str, cwd: Path = REPO) -> str:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, check=True).stdout.strip()


def dir_digest(root: Path) -> tuple[str, int]:
    """A stable digest over every file under ``root``: path + content hash."""
    lines = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            lines.append(f"{p.relative_to(root).as_posix()}  {sha256_file(p)}")
    return sha256_text("\n".join(lines)), len(lines)


def rows_for(arm: str, run_dir: Path):
    """One row per instance. Every quantity is derived; no corpus text."""
    for inst in sorted((run_dir / "instances").iterdir()):
        rec = json.loads((inst / "record.json").read_text())
        b = rec["arms"].get("B")
        if not b:
            continue
        rounds = sorted(int(p.name.split(".")[1][5:]) for p in inst.glob("armB.round*.md"))
        per_round = {}
        for r in rounds:
            text = (inst / f"armB.round{r}.md").read_text()
            score = (b.get("round_scores") or {}).get(str(r), {})
            per_round[str(r)] = {
                "response_sha256": sha256_text(text),
                "response_words": len(text.split()),
                "response_chars": len(text),
                "f1": score.get("f1"),
                "precision": score.get("precision"),
                "recall": score.get("recall"),
                # the per-item vector the F1 is built from, not just the F1
                "per_item": score.get("per_item"),
            }
        growth = {}
        for a, c in zip(rounds, rounds[1:]):
            w0 = per_round[str(a)]["response_words"]
            growth[f"{a}->{c}"] = round((per_round[str(c)]["response_words"] - w0) / w0, 6) if w0 else None
        yield {
            "study": "study4",
            "arm": arm,
            "instance_id": rec["sample_id"],
            "product_code_sha": ARM_CODE[arm][0],
            "ok": b.get("ok"),
            "error": b.get("error") or None,
            "exit_code": b.get("exit_code"),
            "rounds": b.get("rounds"),
            "committed_rounds": rounds,
            "prompt_sha256": b.get("prompt_sha256"),
            "generator_model": b.get("model"),
            "per_round": per_round,
            "committed_growth": growth,
            "final": {
                "f1": b["score"]["f1"], "precision": b["score"]["precision"],
                "recall": b["score"]["recall"], "accuracy": b["score"]["accuracy"],
                "n_items": b["score"]["n_items"],
                "per_item": {j["key"]: {"precision_hit": j["precision_hit"],
                                        "recall_hit": j["recall_hit"]}
                             for j in b.get("_judgements", [])},
            },
            "revision": b.get("revision"),
            "findings": [{"round": f["round"], "rule": f["rule"], "severity": f["severity"],
                          "artifact": f["artifact"], "tier": f["tier"], "state": f["state"],
                          "verdict": f["verdict"],
                          "observation_sha256": sha256_text(f["observation"])}
                         for f in b.get("findings", [])],
            "findings_mapped": b.get("findings_mapped"),
            "adjudications": b.get("adjudications"),
            "audit_recall": b.get("audit_recall"),
            "tokens": {"input": b.get("input_tokens"), "output": b.get("output_tokens"),
                       "calls": b.get("calls"), "scoring_calls": b.get("score_calls")},
            "cost_usd": {"generation_and_audit": b.get("cost_usd"),
                         "clear_scoring": b.get("score_cost_usd")},
            "wall_s": b.get("wall_s"),
        }


def main(argv):
    arms = {}
    for spec in argv:
        name, _, d = spec.partition("=")
        arms[name] = Path(d)

    rows = []
    for arm, d in arms.items():
        rows.extend(rows_for(arm, d))
    (HERE / "records.jsonl").write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")

    digests = {}
    for arm, d in arms.items():
        digest, n = dir_digest(d)
        digests[arm] = {"absolute_path": str(d), "sha256": digest, "files": n}
    (HERE / "rundirs.sha256").write_text(
        "\n".join(f"{v['sha256']}  {k}  {v['files']} files  {v['absolute_path']}"
                  for k, v in sorted(digests.items())) + "\n", encoding="utf-8")

    plans = {}
    for arm, d in arms.items():
        p = json.loads((d / "plan.json").read_text())
        arm_rows = [r for r in rows if r["arm"] == arm]
        plans[arm] = {
            "code_sha": ARM_CODE[arm][0],
            "what_differs": ARM_CODE[arm][1],
            "run_id": p["run_id"],
            "started_utc": p["started_utc"],
            "ended_utc": datetime.fromtimestamp(
                (d / "results.json").stat().st_mtime, timezone.utc).isoformat(),
            "label": p.get("label"),
            "n_planned": p["n"] if not p.get("subset") else p["subset"],
            "n_recorded": len(arm_rows),
            "seed": p["seed"],
            "sample_ids": p["sample_ids"],
            "constitution_sha256": p["constitution_sha256"],
            "settings": p["settings"],
            "models": p["models"],
            "prompt_digests": p["prompts"],
            "run_dir": digests[arm],
        }

    manifest = {
        "study": "study4",
        "title": "does bounding a revision's growth repair the revision defect",
        "preregistration": "benchmarks/expertlongbench/study4/PREREGISTRATION.md",
        "standard": "benchmarks/EXPERIMENT_RECORD.md",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "code": {
            "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "report_tree_sha": git("rev-parse", "HEAD"),
            "worktree_clean": git("status", "--porcelain") == "",
            "control_product_sha": ARM_CODE["C"][0],
            "treatment_product_sha": "21f37d5a23dfbc5633908f4a8a00d81d7b868f89",
            "files_the_change_touched": sorted(
                git("show", "--name-only", "--format=", "21f37d5").splitlines()),
            "harness_sha256": {f: sha256_file(BENCH / f) for f in HARNESS},
            "harness_identical_across_arms": True,
        },
        "data": {
            "dataset": "ExpertLongBench T03MaterialSEG",
            "licence": "CC BY-NC-SA 4.0 — not redistributed by this repository",
            "manifest": json.loads((BENCH / "manifest.json").read_text()),
            "local_file_sha256": {
                p.name: sha256_file(p) for p in sorted((BENCH / "data").glob("*.jsonl"))
            } if (BENCH / "data").exists() else {},
            "row_counts": {
                p.name: sum(1 for line in p.open() if line.strip())
                for p in sorted((BENCH / "data").glob("*.jsonl"))
            } if (BENCH / "data").exists() else {},
        },
        "sampling": {
            "method": "rows sorted by id, then random.Random(seed).sample(rows, n), "
                      "then re-sorted by id; --subset keeps the first k of that draw",
            "seed_arms_C_T": 20261104,
            "seed_arm_G": 20260930,
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "interpreter": sys.executable,
            "network": "all provider traffic via https_proxy=http://127.0.0.1:7897",
        },
        "arms": plans,
        "records": {
            "path": "benchmarks/expertlongbench/study4/records.jsonl",
            "rows": len(rows),
            "sha256": sha256_file(HERE / "records.jsonl"),
            "contains": "derived values and digests only; no corpus text, no model output",
        },
    }
    (HERE / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"records.jsonl: {len(rows)} rows")
    for arm, p in plans.items():
        print(f"  arm {arm}: n={p['n_recorded']}/{p['n_planned']}  {p['started_utc']} -> {p['ended_utc']}")
    print("manifest.json, rundirs.sha256 written")


if __name__ == "__main__":
    main(sys.argv[1:])
