"""Fetch the EvalPlus corpora this study measures against, and pin them.

Two datasets, both fetched through the Hugging Face datasets-server rows API so the
harness needs no `datasets`/`pyarrow` dependency:

* ``openai/openai_humaneval``  — HumanEval, MIT. Supplies the **visible** test suite:
  the benchmark's original ``check(candidate)``.
* ``evalplus/humanevalplus``   — HumanEval+, Apache-2.0. Supplies the **hidden** ground
  truth: EvalPlus's expanded ``check(candidate)``, built because the base tests are too
  weak to distinguish correct code from code that merely passes them.
* ``evalplus/mbppplus``        — MBPP+, Apache-2.0. Carries BOTH halves in one row:
  ``test_list`` (the three assertions MBPP shows the model — the visible layer) and
  ``test`` (the expanded hidden suite).

The corpus is NOT committed. ``manifest.json`` pins per-file sha256, revision and row
counts, so a number measured against it is verifiable without redistributing it.

Usage::

    python benchmarks/code/fetch.py            # download and pin
    python benchmarks/code/fetch.py --verify   # fail if disk != manifest
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
MANIFEST = HERE / "manifest_corpus.json"

ROWS_API = "https://datasets-server.huggingface.co/rows"

#: (local name, dataset, config, licence, homepage)
SOURCES = [
    ("humaneval_base", "openai/openai_humaneval", "openai_humaneval", "MIT",
     "https://huggingface.co/datasets/openai/openai_humaneval"),
    ("humaneval_plus", "evalplus/humanevalplus", "default", "Apache-2.0",
     "https://huggingface.co/datasets/evalplus/humanevalplus"),
    ("mbpp_plus", "evalplus/mbppplus", "default", "Apache-2.0",
     "https://huggingface.co/datasets/evalplus/mbppplus"),
]


def _get(url: str, tries: int = 5) -> dict:
    last = None
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - retried, then raised
            last = exc
            time.sleep(2 * (attempt + 1))
    raise SystemExit(f"could not fetch {url}: {last}")


def dataset_revision(dataset: str) -> str:
    info = _get(f"https://huggingface.co/api/datasets/{dataset}")
    return info.get("sha", "")


def download(name: str, dataset: str, config: str) -> Path:
    rows: list[dict] = []
    offset, total = 0, None
    while total is None or offset < total:
        query = urllib.parse.urlencode(
            {"dataset": dataset, "config": config, "split": "test",
             "offset": offset, "length": 100})
        payload = _get(f"{ROWS_API}?{query}")
        total = payload["num_rows_total"]
        batch = [row["row"] for row in payload["rows"]]
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{name}.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true",
                        help="check the data on disk against the pinned manifest")
    args = parser.parse_args(argv)

    if args.verify:
        if not MANIFEST.exists():
            print("no manifest_corpus.json; run fetch.py first", file=sys.stderr)
            return 2
        pinned = json.loads(MANIFEST.read_text(encoding="utf-8"))
        bad = []
        for name, entry in pinned["datasets"].items():
            path = DATA_DIR / f"{name}.jsonl"
            if not path.exists():
                bad.append(f"{name}: missing")
                continue
            actual = sha256_file(path)
            if actual != entry["sha256"]:
                bad.append(f"{name}: {actual} != pinned {entry['sha256']}")
        if bad:
            print("corpus does not match the manifest:\n  " + "\n  ".join(bad),
                  file=sys.stderr)
            return 1
        print("corpus matches the manifest")
        return 0

    entries = {}
    for name, dataset, config, licence, homepage in SOURCES:
        print(f"fetching {dataset} ...", flush=True)
        path = download(name, dataset, config)
        n = sum(1 for _ in path.open(encoding="utf-8"))
        entries[name] = {
            "dataset": dataset,
            "config": config,
            "split": "test",
            "revision": dataset_revision(dataset),
            "rows": n,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "licence": licence,
            "homepage": homepage,
        }
        print(f"  {n} rows, sha256 {entries[name]['sha256'][:16]}…")
    MANIFEST.write_text(
        json.dumps({"fetched_via": ROWS_API, "datasets": entries}, indent=2) + "\n",
        encoding="utf-8")
    print(f"pinned in {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
