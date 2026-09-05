"""Turn the gitignored Arm 2 run directory into the committed study record.

EXPERIMENT_RECORD §3 asks for one row per unit of analysis, committed, carrying
every measured quantity — and forbids committing corpus text or model output
that quotes it. Both hold here only because the transcribed value and unit
travel as sha256 digests: an annotation row is otherwise an address (`at`,
`src`), a disposition, two adjudications and a class, none of which is corpus
text. The check's own observation strings QUOTE the value and are therefore
dropped here; they stay in the archived run directory.

    python3 benchmarks/expertlongbench/study7/emit_records.py <run-dir>

Writes `rows.jsonl`, `drafts.jsonl` and `manifest.json` beside this file.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent

#: The one hand correction to the §10 classifier, recorded as data rather than
#: applied silently (deviation 3 in RESULTS-ARM2.md). §10's rule 4 sends any row
#: whose transcribed unit contains a space to "unparsed notation" before rule 5
#: can ask where the pair is. That is right for a unit the check can never match
#: — but `wt %` is in the shipped synonym table and DOES match, so this row's
#: block is the wrong line and nothing else. Keyed by (instance, at, src).
HAND: dict[tuple[str, str, str], str] = {
    ("T03MaterialSEG-10.1002/batt.202200056", "#L26",
     "work/synthesis/RECIPE.md#L14"): "generator wrong locator (wrong line)",
}

ROW_FIELDS = ("instance", "row", "at", "src", "v_sha256", "u_sha256", "v_len",
              "u_len", "disposition", "severity", "locator_kind", "resolved",
              "adj_a", "adj_b", "unit_shortened", "at_valid", "class")
DRAFT_FIELDS = ("instance", "ok", "error", "exit_code", "rounds", "wall_s",
                "prompt_sha256", "output_sha256", "science_sha", "draft_chars",
                "draft_lines", "numbers_present", "fence_blocks",
                "increment_files", "ledger_agrees", "manifest_agrees",
                "ledger_finding_count", "usage", "started_utc")


def digest_tree(root: Path) -> dict[str, str]:
    out = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        out[str(path.relative_to(root))] = hashlib.sha256(
            path.read_bytes()).hexdigest()
    return out


def main(argv=None) -> int:
    run_dir = Path((argv or sys.argv[1:])[0])
    rows, drafts = [], []
    for batch in (1, 2):
        path = run_dir / f"records-b{batch}.jsonl"
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            draft = {k: rec.get(k) for k in DRAFT_FIELDS}
            draft["batch"] = batch
            drafts.append(draft)
            for row in rec.get("rows", []):
                out = {k: row.get(k) for k in ROW_FIELDS}
                out["batch"] = batch
                hand = HAND.get((row["instance"], row["at"], row["src"]))
                out["class_hand"] = hand or row.get("class", "")
                rows.append(out)

    (HERE / "rows.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8")
    (HERE / "drafts.jsonl").write_text(
        "".join(json.dumps(d, ensure_ascii=False) + "\n" for d in drafts),
        encoding="utf-8")

    plans = {p.name: json.loads(p.read_text(encoding="utf-8"))
             for p in sorted(run_dir.glob("plan-b*.json"))}
    archive = Path("~/Documents/Crossaudit/study-data/wt-arm2-runs").expanduser()
    manifest = {
        "study": "study7 — provenance Arm 2",
        "plans": plans,
        "code": {
            "sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(HERE),
                                  capture_output=True, text=True).stdout.strip(),
            "status_porcelain": subprocess.run(
                ["git", "status", "--porcelain"], cwd=str(HERE),
                capture_output=True, text=True).stdout,
            "files": {rel: hashlib.sha256((HERE.parent / rel).read_bytes()).hexdigest()
                      for rel in ("provenance_arm2.py", "provenance_arm2_report.py",
                                  "study7/emit_records.py",
                                  "study7/PREREGISTRATION.md")},
        },
        "data": {
            "task": "T03MaterialSEG",
            "licence": "CC BY-NC-SA 4.0 — not redistributed, not committed",
            "rows": 50,
            "sha256": next(iter(plans.values()))["corpus_sha256"] if plans else "",
        },
        "counts": {"drafts": len(drafts), "annotation_rows": len(rows)},
        "archive": {
            "path": str(archive),
            "exists": archive.is_dir(),
            "sha256_manifest": "MANIFEST-SHA256.json beside the run directory",
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": sys.platform,
        },
        "emitted_utc": datetime.now(timezone.utc).isoformat(),
    }
    (HERE / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"{len(rows)} rows, {len(drafts)} drafts written to {HERE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
