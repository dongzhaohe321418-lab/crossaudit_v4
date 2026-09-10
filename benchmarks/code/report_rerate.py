"""Study 21 — the residual re-rated with the oracle question asked first.

Reads the two raters' label files and the blind sheet's key, joins them to ceiling 1's
residual classification (for residual membership and the problem cluster), and writes
records/rerate/numbers.json and tables.md. Interval helpers are ceiling 1's (Wilson and
the problem-cluster percentile bootstrap); the seed is this study's own.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_ceiling import cluster_bootstrap_ci, wilson  # noqa: E402

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records" / "rerate"
CEILING = HERE / "records" / "ceiling"
BOOT_SEED = 20260914
BOOT_REPS = 10_000
CATEGORIES = ["timeout", "ambiguous-oracle", "unexercised-edge", "spec-misreading",
              "wrong-algorithm", "other"]
P_INSTANCES = 110          # ceiling 1 stratum P (RESULTS-CEILING.md Table 5)
RESIDUAL_ALL = 57          # all-family residual (Table 5)
KILL_AMBIGUOUS_AT_LEAST = 30
KILL_EDGE_BELOW = 29


def problem_of(instance: str) -> str:
    return instance.split(":", 1)[1]


def read_labels(path: Path) -> dict[str, str]:
    with open(path, encoding="utf-8") as fh:
        rows = {r["id"]: r["label"].strip() for r in csv.DictReader(fh)}
    bad = sorted(v for v in rows.values() if v not in CATEGORIES)
    if bad:
        raise ValueError(f"{path.name}: labels outside the preregistered set: {bad}")
    return rows


def cohen_kappa(a: dict[str, str], b: dict[str, str]) -> float:
    ids = sorted(a)
    n = len(ids)
    agree = sum(a[i] == b[i] for i in ids) / n
    ca, cb = Counter(a[i] for i in ids), Counter(b[i] for i in ids)
    expected = sum(ca[c] * cb[c] for c in CATEGORIES) / (n * n)
    return 1.0 if expected == 1.0 else (agree - expected) / (1 - expected)


def rate_block(hits: dict[str, int], seed: int) -> dict:
    """Share with both intervals; hits maps instance -> 0/1."""
    k, n = sum(hits.values()), len(hits)
    by_cluster: dict[str, list[int]] = {}
    for inst, h in hits.items():
        by_cluster.setdefault(problem_of(inst), []).append(h)
    lo, hi = cluster_bootstrap_ci(by_cluster, BOOT_REPS, seed)
    wl, wh = wilson(k, n)
    return {"count": k, "n": n, "problems": len(by_cluster), "share": 100 * k / n,
            "cluster_ci": [100 * lo, 100 * hi], "wilson": [100 * wl, 100 * wh]}


def build() -> dict:
    key = {r["id"]: r["instance"] for r in map(json.loads, (RECORDS / "key.jsonl").read_text().splitlines())}
    l1 = read_labels(RECORDS / "L1.csv")
    l2 = read_labels(RECORDS / "L2.csv")
    assert set(l1) == set(l2) == set(key), "the label files and the key disagree on ids"
    classification = json.load(open(CEILING / "residual_classification.json"))["classification"]
    residual = {inst for inst, v in classification.items() if not v["found_by_astra_only"]}
    assert len(residual) == RESIDUAL_ALL, len(residual)
    inst_l1 = {key[i]: l1[i] for i in key}
    inst_l2 = {key[i]: l2[i] for i in key}
    consensus = {inst: inst_l1[inst] if inst_l1[inst] == inst_l2[inst] else "disputed" for inst in inst_l1}
    out = {
        "study": "rerate", "seed": BOOT_SEED, "reps": BOOT_REPS, "categories": CATEGORIES,
        "n_sheet": len(key), "n_residual": len(residual),
        "agreement": {"agree": sum(inst_l1[i] == inst_l2[i] for i in inst_l1), "n": len(inst_l1),
                      "kappa": cohen_kappa(l1, l2)},
        "disputed": sorted(i for i in inst_l1 if consensus[i] == "disputed"),
        "disputed_labels": {i: [inst_l1[i], inst_l2[i]] for i in inst_l1 if consensus[i] == "disputed"},
        "marginals": {"L1": dict(Counter(inst_l1.values())), "L2": dict(Counter(inst_l2.values()))},
        "populations": {},
        "prior_classification_of_consensus_ambiguous": dict(Counter(
            classification[i]["category"] for i in residual if consensus[i] == "ambiguous-oracle")),
    }
    for name, pop in (("all_families_residual", residual), ("sheet_68", set(inst_l1))):
        block = {"n": len(pop), "problems": len({problem_of(i) for i in pop}), "consensus": {}}
        for j, cat in enumerate(CATEGORIES + ["disputed"]):
            hits = {i: int(consensus[i] == cat) for i in sorted(pop)}
            block["consensus"][cat] = rate_block(hits, BOOT_SEED + j)
        out["populations"][name] = block
    res = out["populations"]["all_families_residual"]["consensus"]
    amb, edge = res["ambiguous-oracle"]["count"], res["unexercised-edge"]["count"]
    out["kill"] = {
        "rule": f"consensus ambiguous-oracle >= {KILL_AMBIGUOUS_AT_LEAST} of {RESIDUAL_ALL}, "
                f"or consensus unexercised-edge < {KILL_EDGE_BELOW} of {RESIDUAL_ALL}",
        "ambiguous": amb, "edge": edge,
        "fires": amb >= KILL_AMBIGUOUS_AT_LEAST or edge < KILL_EDGE_BELOW,
    }
    flagged = P_INSTANCES - RESIDUAL_ALL
    out["exploratory_oracle_clean"] = {
        "assumption": "only the residual was re-rated; the 53 flagged instances are treated as "
                      "oracle-clean, which they were never checked to be",
        "flagged": flagged, "P": P_INSTANCES, "consensus_ambiguous_in_residual": amb,
        "P_clean": P_INSTANCES - amb,
        "union_recall_registered": 100 * flagged / P_INSTANCES,
        "union_recall_oracle_clean": 100 * flagged / (P_INSTANCES - amb),
        "residual_share_oracle_clean": 100 * (RESIDUAL_ALL - amb) / (P_INSTANCES - amb),
    }
    return out


def fmt(b: dict) -> str:
    return (f"**{b['count']} of {b['n']}** ({b['share']:.1f}% [{b['cluster_ci'][0]:.1f}, "
            f"{b['cluster_ci'][1]:.1f}]; Wilson [{b['wilson'][0]:.1f}, {b['wilson'][1]:.1f}])")


def render_tables(n: dict) -> str:
    lines = ["### Table 1 — consensus category of the residual, oracle question first", "",
             "Unit: the instance; primary interval the problem-cluster percentile bootstrap "
             f"(seed {n['seed']}, {n['reps']:,} resamples); Wilson beside it, too narrow. "
             "`disputed` = the two raters differ; counted toward neither category.", "",
             "| population | n (problems) | category | consensus count | share [95% cluster CI] (Wilson) |",
             "|---|---:|---|---:|---|"]
    for name, block in n["populations"].items():
        for cat in n["categories"] + ["disputed"]:
            b = block["consensus"][cat]
            if b["count"] == 0:
                continue
            lines.append(f"| {name} | {block['n']} ({block['problems']}) | `{cat}` | {b['count']} | {fmt(b)} |")
    a = n["agreement"]
    lines += ["", "### Table 2 — the two raters", "",
              "| raters | agree | n | Cohen κ (six categories) |", "|---|---:|---:|---:|",
              f"| L1 (author) vs L2 (`gpt-6-astra`, blind) | {a['agree']} | {a['n']} | **{a['kappa']:.3f}** |",
              "", "| disputed instance | L1 | L2 |", "|---|---|---|"]
    for inst, (x, y) in sorted(n["disputed_labels"].items()):
        lines.append(f"| `{inst}` | {x} | {y} |")
    e = n["exploratory_oracle_clean"]
    lines += ["", "### Table 3 — EXPLORATORY: ceiling 1's all-family union recall on an oracle-clean denominator", "",
              f"Assumption stated in the preregistration and repeated here: {e['assumption']}.", "",
              "| denominator | P | flagged by any draw | union recall at K_max | residual share |",
              "|---|---:|---:|---:|---:|",
              f"| registered (ceiling 1) | {e['P']} | {e['flagged']} | {e['union_recall_registered']:.1f}% | "
              f"{100 * n['n_residual'] / e['P']:.1f}% |",
              f"| oracle-clean (P minus {e['consensus_ambiguous_in_residual']} consensus-ambiguous residual instances) | "
              f"{e['P_clean']} | {e['flagged']} | {e['union_recall_oracle_clean']:.1f}% | {e['residual_share_oracle_clean']:.1f}% |"]
    return "\n".join(lines) + "\n"


def main() -> None:
    n = build()
    RECORDS.mkdir(parents=True, exist_ok=True)
    (RECORDS / "numbers.json").write_text(json.dumps(n, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (RECORDS / "tables.md").write_text(render_tables(n), encoding="utf-8")
    k = n["kill"]
    print(f"kill fires: {k['fires']} (ambiguous {k['ambiguous']}, edge {k['edge']}); κ {n['agreement']['kappa']:.3f}")


if __name__ == "__main__":
    main()
