"""Copy a run's rows into the committed record, with every corpus quotation removed.

Generated solutions reproduce the problem prompts, and a failing assertion's message
quotes the dataset's own inputs and expected outputs. Neither may be committed. What is
committed is the derived material the record is made of: ids, strata, outcome vectors,
verdicts, counts, hashes, tokens, cost and time.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

#: Free text that can quote the corpus. Replaced by its length and a hash.
REDACT = ("error", "solution", "observation")


def redact(row: dict) -> dict:
    out = {}
    for key, value in row.items():
        if isinstance(value, dict):
            out[key] = redact(value)
        elif key in REDACT and isinstance(value, str):
            out[key + "_chars"] = len(value)
            out[key + "_present"] = bool(value)
        else:
            out[key] = value
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--records", required=True)
    args = parser.parse_args(argv)

    run_dir, records = Path(args.run), Path(args.records)
    records.mkdir(parents=True, exist_ok=True)
    for path in sorted(run_dir.glob("*.jsonl")):
        if path.name == "solutions.jsonl":
            rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
                    if l.strip()]
            keep = [{k: v for k, v in redact(r).items()
                     if k not in ("solution_chars", "solution_present")}
                    | {"solution_chars": len(r.get("solution", ""))}
                    for r in rows]
            (records / path.name).write_text(
                "\n".join(json.dumps(r, sort_keys=True) for r in keep) + "\n",
                encoding="utf-8")
            continue
        rows = [redact(json.loads(l))
                for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        (records / path.name).write_text(
            "\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n", encoding="utf-8")
        print(f"  {path.name}: {len(rows)} rows")
    for name in ("manifest.json", "audit_set.json", "cost.json", "numbers.json"):
        source = run_dir / name
        if source.exists():
            (records / name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
