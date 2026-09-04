"""Collect each arm's spend from the product's own usage ledger, not a reconstruction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RUN_IDS = {
    "generation": "code-gen-1",
    "cross+checks": "code-crosschecks-1",
    "cross": "code-cross-1",
    "self": "code-self-1",
    "cross-replicate": "code-crossrep-1",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledgers", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    from crossaudit import usage

    totals: dict[str, dict] = {}
    for path in args.ledgers:
        events, _ = usage.read_events(Path(path))
        for event in events:
            run_id = event.get("run_id")
            label = next((k for k, v in RUN_IDS.items() if v == run_id), None)
            if label is None:
                continue
            row = totals.setdefault(label, {"usd": 0.0, "calls": 0, "input": 0, "output": 0})
            row["usd"] += float(event.get("api_value_usd") or 0.0)
            row["calls"] += 1
            row["input"] += int(event.get("input", 0) or 0)
            row["output"] += int(event.get("output", 0) or 0)
    totals["checks"] = {"usd": 0.0, "calls": 0, "input": 0, "output": 0}
    totals["none"] = {"usd": 0.0, "calls": 0, "input": 0, "output": 0}
    totals["TOTAL"] = {
        "usd": sum(v["usd"] for k, v in totals.items() if k != "TOTAL"),
        "calls": sum(v["calls"] for k, v in totals.items() if k != "TOTAL"),
        "input": sum(v["input"] for k, v in totals.items() if k != "TOTAL"),
        "output": sum(v["output"] for k, v in totals.items() if k != "TOTAL"),
    }
    Path(args.out).write_text(json.dumps(totals, indent=2) + "\n", encoding="utf-8")
    for key in sorted(totals):
        row = totals[key]
        print(f"  {key:<18} ${row['usd']:.4f}  {row['calls']} calls  "
              f"{row['input']}/{row['output']} tok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
