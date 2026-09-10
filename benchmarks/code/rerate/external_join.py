"""Study 21 Amendment 3 — join this study's frozen labels to the external sources.

    python benchmarks/code/rerate/external_join.py

Writes records/rerate/external.json. No model call, no spend, no corpus text.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(CODE))
from external_labels import EVALPLUS_SPECIAL_ORACLE, RICHTER  # noqa: E402
import report_rerate as rr  # noqa: E402

RECORDS = CODE / "records" / "rerate"


def consensus_by_task() -> dict[str, dict]:
    """This study's consensus label per TASK, from the frozen per-instance labels."""
    inst_l1, inst_l2 = rr.read_sheet("key.jsonl", "L1.csv", "L2.csv")
    f_l1, f_l2 = rr.read_sheet("key-flagged.jsonl", "L1-flagged.csv", "L2-flagged.csv")
    l1 = {**inst_l1, **f_l1}
    l2 = {**inst_l2, **f_l2}
    per_task: dict[str, list[str]] = {}
    for iid in l1:
        label = l1[iid] if l1[iid] == l2[iid] else "disputed"
        per_task.setdefault(iid.split(":", 1)[1], []).append(label)
    out = {}
    for task, labels in per_task.items():
        agreed = labels[0] if len(set(labels)) == 1 else "split across batches"
        out[task] = {"labels": sorted(labels), "task_label": agreed}
    return out


def main() -> int:
    ours = consensus_by_task()
    rows = []
    for source, table in (("richter2607.01953", RICHTER),
                          ("evalplus/_special_oracle.py", EVALPLUS_SPECIAL_ORACLE)):
        for task, what in sorted(table.items()):
            mine = ours.get(task)
            rows.append({"source": source, "task": task, "their_class": what,
                         "in_our_P": mine is not None,
                         "our_task_label": (mine or {}).get("task_label"),
                         "our_instance_labels": (mine or {}).get("labels")})
    joined = [r for r in rows if r["in_our_P"]]
    tasks_joined = sorted({r["task"] for r in joined})
    concordant = [t for t in tasks_joined
                  if ours[t]["task_label"] == rr.CATEGORIES[1]]          # ambiguous-oracle
    discordant = [t for t in tasks_joined if t not in concordant]
    out = {
        "study": "rerate / Amendment 3",
        "note": "one-sided by construction: neither source claims to be exhaustive, so a task "
                "they do not list is not evidence that its specification is sound",
        "labels_frozen_before_the_external_search": {
            "L1.csv": "d98f0c1", "L1-flagged.csv": "3aa97aa", "L2-R.csv": "e654452"},
        "n_external_tasks": len({r["task"] for r in rows}),
        "n_joined_to_our_P": len(tasks_joined),
        "n_concordant": len(concordant), "n_discordant": len(discordant),
        "concordant_tasks": concordant, "discordant_tasks": discordant,
        "discordant_detail": [r for r in joined if r["task"] in discordant],
        "by_source": {s: {"listed": sum(1 for r in rows if r["source"] == s),
                          "joined": sum(1 for r in joined if r["source"] == s),
                          "concordant": sum(1 for r in joined if r["source"] == s
                                            and r["task"] in concordant)}
                      for s in {r["source"] for r in rows}},
        "our_label_distribution_on_joined": dict(Counter(ours[t]["task_label"] for t in tasks_joined)),
        "rows": rows,
    }
    (RECORDS / "external.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n",
                                           encoding="utf-8")
    print(f"external tasks {out['n_external_tasks']}, joined {out['n_joined_to_our_P']}, "
          f"concordant {out['n_concordant']}, discordant {out['n_discordant']}: {discordant}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
