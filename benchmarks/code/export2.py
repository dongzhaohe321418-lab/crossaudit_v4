"""Copy study 2's rows into the committed record, with every corpus quotation removed.

Study 2 adds two text-bearing fields study 1 did not have, and both are dropped here:

* ``blocker_texts`` — the holistic arms' BLOCKER observations and the decomposed arm's
  VIOLATED evidence, kept in the run directory only because the two-stage arms need them
  as input. Model prose about a problem can quote the problem.
* ``properties.json`` — the decomposer's property lists, which paraphrase the corpus's
  specifications. The record keeps each property's sha256 (already on every check row) and
  the per-instance counts, which is what the analysis is made of.

What is committed is derived material: ids, strata, outcome vectors, verdicts, per-property
verdict vectors, counts, hashes, tokens, cost and time.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

#: Free text that can quote the corpus. Replaced by its length and a presence flag.
REDACT = ("error", "solution", "observation")
#: Dropped entirely, replaced by a count.
DROP_LIST = ("blocker_texts",)


def redact(row: dict) -> dict:
    out: dict = {}
    for key, value in row.items():
        if key in DROP_LIST:
            out[key + "_count"] = len(value) if isinstance(value, list) else 0
        elif isinstance(value, dict):
            out[key] = redact(value)
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            out[key] = [redact(v) for v in value]
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

    for path in sorted(run_dir.glob("arm-*.jsonl")):
        rows = [redact(json.loads(l)) for l in
                path.read_text(encoding="utf-8").splitlines() if l.strip()]
        (records / path.name).write_text(
            "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
        print(f"  {path.name}: {len(rows)} rows")

    # instances.jsonl carries ids, strata and solution hashes only — no text.
    for name in ("instances.jsonl",):
        src = run_dir / name
        if src.exists():
            (records / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"  {name}: copied")

    for name in ("audit_set.json", "manifest.json", "numbers.json", "cost.json"):
        src = run_dir / name
        if src.exists():
            (records / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"  {name}: copied")

    # The property lists themselves paraphrase the corpus; only their shape is committed.
    props = run_dir / "properties.json"
    if props.exists():
        data = json.loads(props.read_text(encoding="utf-8"))
        summary = {pid: {"n_properties": len(v["properties"]),
                         "categories": [p["category"] for p in v["properties"]],
                         "property_sha256": [__import__("hashlib").sha256(
                             p["property"].encode("utf-8")).hexdigest()
                             for p in v["properties"]],
                         "prompt_sha256": v.get("prompt_sha256", ""),
                         "response_sha256": v.get("response_sha256", "")}
                   for pid, v in sorted(data.items())}
        (records / "properties_shape.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"  properties_shape.json: {len(summary)} problems decomposed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
