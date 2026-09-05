"""Study 6 -- turn the gitignored run directories into the committed record.

Copies each replicate's raw JSONL rows and its manifest out of ``runs/`` (which holds
drafts and therefore corpus text) into ``study6/`` (which holds ids, digests, scores and
counts and nothing else), tallies the measured spend from the rows and the adjudication
ledgers, and writes ``MANIFEST-SHA256.json`` so the published record can be checked
against the run directories it came from.

Rows are copied, not regenerated. Nothing here recomputes a measurement.

Usage::

    python benchmarks/expertlongbench/study6/collect.py \\
        --runs benchmarks/expertlongbench/runs \\
        --replicate noise-rep1 --replicate noise-rep2 ...
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def directory_sha256(root: Path) -> tuple[str, int]:
    """A digest over every file's relative path and content, so a run dir is checkable."""
    digest = hashlib.sha256()
    count = 0
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(sha256_file(path).encode("ascii"))
        count += 1
    return digest.hexdigest(), count


def passes_of(runs: Path, label: str) -> list[Path]:
    """A replicate's main pass and every fill pass that completed it, in order."""
    main = runs / label
    fills = sorted((p for p in runs.glob(f"{label}-fill*") if p.is_dir()),
                   key=lambda p: p.name)
    return [main, *fills]


def ledger_total(project_root: Path) -> float:
    """Adjudication spend, from the product's own usage ledger in a run's _host project."""
    ledger = project_root / "_host" / "project" / ".crossaudit" / "usage.jsonl"
    if not ledger.exists():
        return 0.0
    total = 0.0
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            total += float(json.loads(line).get("api_value_usd") or 0.0)
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
    return total


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", required=True)
    parser.add_argument("--replicate", action="append", required=True)
    parser.add_argument("--source", default="study6-source",
                        help="the generated source directory, recorded for provenance")
    args = parser.parse_args(argv)

    runs = Path(args.runs).resolve()
    manifest: dict = {
        "note": "sha256 of every committed record and of the gitignored run directories "
                "they came from. Run directories hold drafts, which quote the corpus, "
                "and are never committed.",
        "study": "6-noise",
        "runs": {},
        "committed": {},
        "cost": {},
    }
    audit_cost = adjudication_cost = 0.0
    calls = 0

    for label in args.replicate:
        for path in passes_of(runs, label):
            if not path.is_dir():
                continue
            digest, files = directory_sha256(path)
            manifest["runs"][path.name] = {
                "absolute_path": str(path),
                "n_files": files,
                "directory_sha256": digest,
            }
            rows_out = HERE / f"{path.name}.rows.jsonl"
            shutil.copyfile(path / "rows.jsonl", rows_out)
            shutil.copyfile(path / "manifest.json", HERE / f"{path.name}.manifest.json")
            for row_line in rows_out.read_text(encoding="utf-8").splitlines():
                if not row_line.strip():
                    continue
                row = json.loads(row_line)
                audit_cost += float((row.get("cost") or {}).get("usd") or 0.0)
                calls += int((row.get("cost") or {}).get("calls") or 0)
            adjudication_cost += ledger_total(path)

    source = runs / args.source
    if source.is_dir():
        digest, files = directory_sha256(source)
        manifest["runs"][source.name] = {
            "absolute_path": str(source),
            "n_files": files,
            "directory_sha256": digest,
            "role": "generated source; drafts and CLEAR verdicts read back from study 3",
        }

    manifest["cost"] = {
        "audit_usd": round(audit_cost, 6),
        "adjudication_usd": round(adjudication_cost, 6),
        "total_usd": round(audit_cost + adjudication_cost, 6),
        "auditor_calls": calls,
        "source": "the product's own usage ledger, via each row's recorded event and "
                  "each run's _host adjudication ledger",
    }
    records = (sorted(HERE.glob("*.jsonl")) + sorted(HERE.glob("*.json"))
               + sorted(HERE.glob("*.txt")) + sorted(HERE.glob("*.sh")))
    for path in records:
        if path.name == "MANIFEST-SHA256.json":
            continue
        manifest["committed"][path.name] = sha256_file(path)

    (HERE / "MANIFEST-SHA256.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest["cost"], indent=2))
    print(f"{len(manifest['committed'])} committed records -> {HERE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
