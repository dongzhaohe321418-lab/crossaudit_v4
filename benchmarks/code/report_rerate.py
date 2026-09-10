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


def read_sheet(key_name: str, l1_name: str, l2_name: str) -> tuple[dict, dict]:
    key = {r["id"]: r["instance"] for r in map(json.loads, (RECORDS / key_name).read_text().splitlines())}
    l1 = read_labels(RECORDS / l1_name)
    l2 = read_labels(RECORDS / l2_name)
    assert set(l1) == set(l2) == set(key), f"{key_name}: the label files and the key disagree on ids"
    return {key[i]: l1[i] for i in key}, {key[i]: l2[i] for i in key}


def oracle_clean_recall(flagged: set[str], ambiguous: set[str], p_instances: list[str], seed: int) -> dict:
    """Amendment 1's secondary: (flagged − ambiguous) / (P − ambiguous), problem-cluster bootstrap
    over the P instances' (flagged, ambiguous) pairs. Disputed instances count as not ambiguous."""
    pairs = {inst: (int(inst in flagged), int(inst in ambiguous)) for inst in p_instances}
    by_cluster: dict[str, list[tuple[int, int]]] = {}
    for inst, pr in pairs.items():
        by_cluster.setdefault(problem_of(inst), []).append(pr)
    def stat(rows):
        num = sum(f for f, a in rows if not a)
        den = sum(1 for f, a in rows if not a)
        return 100 * num / den if den else None
    point = stat(list(pairs.values()))
    import random
    rng = random.Random(seed)
    clusters = sorted(by_cluster)
    draws = []
    for _ in range(BOOT_REPS):
        rows = []
        for _ in range(len(clusters)):
            rows.extend(by_cluster[clusters[rng.randrange(len(clusters))]])
        v = stat(rows)
        if v is not None:
            draws.append(v)
    draws.sort()
    lo, hi = draws[int(0.025 * len(draws))], draws[min(len(draws) - 1, int(0.975 * len(draws)))]
    n_clean = sum(1 for f, a in pairs.values() if not a)
    k_clean = sum(f for f, a in pairs.values() if not a)
    wl, wh = wilson(k_clean, n_clean)
    return {"flagged_clean": k_clean, "P_clean": n_clean, "recall": point, "cluster_ci": [lo, hi],
            "wilson": [100 * wl, 100 * wh], "seed": seed}


def build() -> dict:
    inst_l1, inst_l2 = read_sheet("key.jsonl", "L1.csv", "L2.csv")
    f_l1, f_l2 = read_sheet("key-flagged.jsonl", "L1-flagged.csv", "L2-flagged.csv")
    # The residual sheet's 11 exploratory instances (flagged by the third family only) are
    # flagged P instances, so both sheets carry them: the flagged sheet's label is the one used
    # (Amendment 1's), and the pair of readings is reported as each rater's test-retest.
    overlap = sorted(set(f_l1) & set(inst_l1))
    retest = {"n": len(overlap),
              "L1_same": sum(inst_l1[i] == f_l1[i] for i in overlap),
              "L2_same": sum(inst_l2[i] == f_l2[i] for i in overlap),
              "changes": {i: {"L1": [inst_l1[i], f_l1[i]], "L2": [inst_l2[i], f_l2[i]]}
                          for i in overlap if inst_l1[i] != f_l1[i] or inst_l2[i] != f_l2[i]}}
    l1 = {**inst_l1, **f_l1}; l2 = {**inst_l2, **f_l2}
    classification = json.load(open(CEILING / "residual_classification.json"))["classification"]
    residual = {inst for inst, v in classification.items() if not v["found_by_astra_only"]}
    assert len(residual) == RESIDUAL_ALL, len(residual)
    flagged = set(f_l1)
    assert len(flagged) == P_INSTANCES - RESIDUAL_ALL and not (flagged & residual)
    consensus = {inst: l1[inst] if l1[inst] == l2[inst] else "disputed" for inst in l1}
    consensus_sheet68 = {inst: inst_l1[inst] if inst_l1[inst] == inst_l2[inst] else "disputed" for inst in inst_l1}
    out = {
        "study": "rerate", "seed": BOOT_SEED, "reps": BOOT_REPS, "categories": CATEGORIES,
        "n_sheet": len(inst_l1), "n_residual": len(residual), "n_flagged_sheet": len(f_l1),
        "agreement": {"agree": sum(inst_l1[i] == inst_l2[i] for i in inst_l1), "n": len(inst_l1),
                      "kappa": cohen_kappa(inst_l1, inst_l2)},
        "agreement_flagged": {"agree": sum(f_l1[i] == f_l2[i] for i in f_l1), "n": len(f_l1),
                              "kappa": cohen_kappa(f_l1, f_l2)},
        "disputed": sorted(i for i in inst_l1 if consensus[i] == "disputed"),
        "disputed_labels": {i: [l1[i], l2[i]] for i in l1 if consensus[i] == "disputed"},
        "marginals": {"L1": dict(Counter(inst_l1.values())), "L2": dict(Counter(inst_l2.values()))},
        "marginals_flagged": {"L1": dict(Counter(f_l1.values())), "L2": dict(Counter(f_l2.values()))},
        "populations": {},
        "retest_on_the_11_overlapping_instances": retest,
        "prior_classification_of_consensus_ambiguous": dict(Counter(
            classification[i]["category"] for i in residual if consensus[i] == "ambiguous-oracle")),
    }
    for name, pop in (("all_families_residual", residual), ("sheet_68", set(inst_l1)), ("flagged_P", flagged)):
        block = {"n": len(pop), "problems": len({problem_of(i) for i in pop}), "consensus": {}}
        cons = consensus_sheet68 if name == "sheet_68" else consensus
        for j, cat in enumerate(CATEGORIES + ["disputed"]):
            hits = {i: int(cons[i] == cat) for i in sorted(pop)}
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
    amb_f = out["populations"]["flagged_P"]["consensus"]["ambiguous-oracle"]["count"]
    ambiguous = {i for i in l1 if consensus[i] == "ambiguous-oracle" and (i in residual or i in flagged)}
    sec = oracle_clean_recall(flagged, ambiguous, sorted(residual | flagged), BOOT_SEED + 10)
    reg = json.load(open(CEILING / "numbers.json"))["ceiling1"]["residual"]["all_families"]["share_block"]
    assert reg["k"] == RESIDUAL_ALL and reg["n"] == P_INSTANCES
    sec.update({"rule": "Amendment 1: (53 − a_f) / (110 − a_r − a_f); disputed count as not ambiguous",
                "a_r": amb, "a_f": amb_f, "flagged": len(flagged), "P": P_INSTANCES,
                "union_recall_registered": 100 * len(flagged) / P_INSTANCES,
                "union_recall_registered_cluster_ci": [100 * (1 - reg["cluster_ci95"][1]), 100 * (1 - reg["cluster_ci95"][0])],
                "union_recall_registered_wilson": [100 * (1 - reg["wilson95"][1]), 100 * (1 - reg["wilson95"][0])],
                "calibration": "the bootstrap for this conditional estimand has no committed coverage simulation; uncalibrated",
                "residual_share_oracle_clean": 100 * (RESIDUAL_ALL - amb) / (P_INSTANCES - amb - amb_f)})
    out["oracle_clean_secondary"] = sec
    # POST HOC (not in the preregistration or Amendment 1): ceiling 1's union recall split by the
    # consensus category of the defect — asked after the flagged sheet's counts were seen.
    by_cat = {}
    for j, cat in enumerate(CATEGORIES + ["disputed"]):
        members = [i for i in sorted(residual | flagged) if consensus[i] == cat]
        if not members:
            continue
        by_cat[cat] = rate_block({i: int(i in flagged) for i in members}, BOOT_SEED + 20 + j)
    out["recall_by_consensus_category_POST_HOC"] = by_cat
    # Amendment 2: L2 re-run on one combined, identity-stripped sheet of the 110 P instances.
    key_r = {r["id"]: r["instance"] for r in map(json.loads, (RECORDS / "key-R.jsonl").read_text().splitlines())}
    l2r_raw = read_labels(RECORDS / "L2-R.csv")
    assert set(l2r_raw) == set(key_r), "L2-R.csv and key-R.jsonl disagree on ids"
    l2r = {key_r[i]: l2r_raw[i] for i in key_r}
    assert set(l2r) == residual | flagged
    first_l2 = {**inst_l2, **f_l2}           # L2's first labels, the flagged sheet's for the 11 overlaps
    cons_r = {i: l1[i] if l1[i] == l2r[i] else "disputed" for i in l2r}
    amb_r_res = sum(1 for i in residual if cons_r[i] == "ambiguous-oracle")
    edge_r_res = sum(1 for i in residual if cons_r[i] == "unexercised-edge")
    amb_r_fl = sum(1 for i in flagged if cons_r[i] == "ambiguous-oracle")
    ambiguous_r = {i for i in l2r if cons_r[i] == "ambiguous-oracle"}
    sec_r = oracle_clean_recall(flagged, ambiguous_r, sorted(residual | flagged), BOOT_SEED + 30)
    by_cat_r = {}
    for j, cat in enumerate(CATEGORIES + ["disputed"]):
        members = [i for i in sorted(residual | flagged) if cons_r[i] == cat]
        if members:
            by_cat_r[cat] = rate_block({i: int(i in flagged) for i in members}, BOOT_SEED + 40 + j)
    out["reblinded_L2_AMENDMENT_2"] = {
        "n": len(l2r),
        "L2_retest": {"same": sum(first_l2[i] == l2r[i] for i in l2r), "n": len(l2r),
                      "kappa_first_vs_reblinded": cohen_kappa({i: first_l2[i] for i in l2r}, l2r),
                      "changes": {i: [first_l2[i], l2r[i]] for i in sorted(l2r) if first_l2[i] != l2r[i]}},
        "L1_vs_L2R": {"agree": sum(l1[i] == l2r[i] for i in l2r), "n": len(l2r),
                      "kappa": cohen_kappa({i: l1[i] for i in l2r}, l2r)},
        "marginals_L2R": dict(Counter(l2r.values())),
        "residual_consensus": dict(Counter(cons_r[i] for i in residual)),
        "flagged_consensus": dict(Counter(cons_r[i] for i in flagged)),
        "kill_restated": {"ambiguous": amb_r_res, "edge": edge_r_res,
                          "fires": amb_r_res >= KILL_AMBIGUOUS_AT_LEAST or edge_r_res < KILL_EDGE_BELOW},
        "oracle_clean_secondary_restated": {**sec_r, "a_r": amb_r_res, "a_f": amb_r_fl},
        "recall_by_consensus_category_POST_HOC_restated": by_cat_r,
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
    for name in ("all_families_residual", "sheet_68", "flagged_P"):   # fixed order; JSON sorts keys
        block = n["populations"][name]
        for cat in n["categories"] + ["disputed"]:
            b = block["consensus"][cat]
            if b["count"] == 0:
                continue
            lines.append(f"| {name} | {block['n']} ({block['problems']}) | `{cat}` | {b['count']} | {fmt(b)} |")
    a = n["agreement"]
    lines += ["", "### Table 2 — the two raters (disputed instances from both sheets)", "",
              "| raters | agree | n | Cohen κ (six categories) |", "|---|---:|---:|---:|",
              f"| L1 (author) vs L2 (`gpt-6-astra`, blind) | {a['agree']} | {a['n']} | **{a['kappa']:.3f}** |",
              "", "| disputed instance | L1 | L2 |", "|---|---|---|"]
    for inst, (x, y) in sorted(n["disputed_labels"].items()):
        lines.append(f"| `{inst}` | {x} | {y} |")
    af = n["agreement_flagged"]; rt = n["retest_on_the_11_overlapping_instances"]
    lines += ["", "| raters, flagged sheet | agree | n | Cohen κ |", "|---|---:|---:|---:|",
              f"| L1 vs L2 | {af['agree']} | {af['n']} | **{af['kappa']:.3f}** |",
              "", f"Test-retest on the {rt['n']} instances both sheets carry (rated twice, blind both times, "
              f"the flagged sheet's label used): L1 same {rt['L1_same']} of {rt['n']}, L2 same {rt['L2_same']} of {rt['n']}."]
    e = n["oracle_clean_secondary"]
    lines += ["", "### Table 3 — ceiling 1's all-family union recall on the oracle-clean denominator (Amendment 1 secondary)", "",
              f"Rule: {e['rule']}. Interval: problem-cluster bootstrap over the {e['P']} P instances' (flagged, ambiguous) "
              f"pairs, seed {e['seed']}; Wilson beside it.", "",
              "| denominator | P | flagged by any draw | union recall at K_max [95% cluster CI] (Wilson) | residual share |",
              "|---|---:|---:|---|---:|",
              f"| registered (ceiling 1) | {e['P']} | {e['flagged']} | {e['union_recall_registered']:.1f}% "
              f"[{e['union_recall_registered_cluster_ci'][0]:.1f}, {e['union_recall_registered_cluster_ci'][1]:.1f}] "
              f"(Wilson [{e['union_recall_registered_wilson'][0]:.1f}, {e['union_recall_registered_wilson'][1]:.1f}]) | "
              f"{100 * n['n_residual'] / e['P']:.1f}% |",
              f"| oracle-clean (minus {e['a_r']} residual + {e['a_f']} flagged consensus-ambiguous) | "
              f"{e['P_clean']} | {e['flagged_clean']} | **{e['recall']:.1f}%** [{e['cluster_ci'][0]:.1f}, {e['cluster_ci'][1]:.1f}] "
              f"(Wilson [{e['wilson'][0]:.1f}, {e['wilson'][1]:.1f}]) | {e['residual_share_oracle_clean']:.1f}% |",
              "", f"The registered interval is the complement of ceiling 1's residual-share interval. The oracle-clean "
              f"interval is a bootstrap of a conditional estimand: {e['calibration']}."]
    bc = n["recall_by_consensus_category_POST_HOC"]
    lines += ["", "### Table 4 — POST HOC: ceiling 1's union recall by the defect's consensus category", "",
              "Asked after Table 1's flagged counts were seen; not preregistered. Recall = flagged by any of the 20 draws.", "",
              "| consensus category | n P instances (problems) | flagged | recall [95% cluster CI] (Wilson) |", "|---|---:|---:|---|"]
    for cat in CATEGORIES + ["disputed"]:   # fixed order; JSON sorts keys
        if cat not in bc:
            continue
        b = bc[cat]
        lines.append(f"| `{cat}` | {b['n']} ({b['problems']}) | {b['count']} | {fmt(b)} |")
    r = n["reblinded_L2_AMENDMENT_2"]; rt = r["L2_retest"]; lv = r["L1_vs_L2R"]; kr = r["kill_restated"]; sr = r["oracle_clean_secondary_restated"]
    lines += ["", "### Table 5 — Amendment 2: L2 re-run on one identity-stripped sheet of all 110 P instances", "",
              "The first sheets carried the instance id and L2's second prompt named the sheet (found by the first review); "
              "this pass strips both. L1's labels are unchanged (L1 cannot be re-blinded).", "",
              "| quantity | value |", "|---|---|",
              f"| L2 first labels vs re-blinded, same | {rt['same']} of {rt['n']} (κ {rt['kappa_first_vs_reblinded']:.3f}) |",
              f"| L1 vs re-blinded L2, agree | {lv['agree']} of {lv['n']} (κ {lv['kappa']:.3f}) |",
              f"| residual consensus (L1 × L2 re-blinded) | " + ", ".join(f"`{c}` {r['residual_consensus'].get(c, 0)}" for c in CATEGORIES + ["disputed"] if r['residual_consensus'].get(c)) + " |",
              f"| flagged consensus (L1 × L2 re-blinded) | " + ", ".join(f"`{c}` {r['flagged_consensus'].get(c, 0)}" for c in CATEGORIES + ["disputed"] if r['flagged_consensus'].get(c)) + " |",
              f"| §3 kill restated | ambiguous {kr['ambiguous']} of 57, edge {kr['edge']} of 57 — {'fires' if kr['fires'] else 'does not fire'} |",
              f"| oracle-clean recall restated | {sr['flagged_clean']} of {sr['P_clean']} = **{sr['recall']:.1f}%** [{sr['cluster_ci'][0]:.1f}, {sr['cluster_ci'][1]:.1f}] (Wilson [{sr['wilson'][0]:.1f}, {sr['wilson'][1]:.1f}]) |"]
    bcr = r["recall_by_consensus_category_POST_HOC_restated"]
    lines += ["", "| post-hoc split restated | n | flagged | recall [95% cluster CI] (Wilson) |", "|---|---:|---:|---|"]
    for cat in CATEGORIES + ["disputed"]:
        if cat in bcr:
            b = bcr[cat]
            lines.append(f"| `{cat}` | {b['n']} | {b['count']} | {fmt(b)} |")
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
