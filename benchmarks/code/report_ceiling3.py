"""Study 18 — apply ceiling 3's preregistered outcomes to the records, and nothing else.

Reads the same records ``report_ceiling.py`` reads (study 1/2 arms, study 7's cache,
ceiling 1's cache) plus ``records/ceiling3/cache``; reuses ``report_ceiling``'s curve, fit,
bootstrap and interval helpers unchanged. Families: ceiling 1's three and the two new ones.

    python benchmarks/code/report_ceiling3.py            -> records/ceiling3/numbers.json
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import explore  # noqa: E402
import report_ceiling as rc  # noqa: E402

RECORDS = HERE / "records"
CEILING3 = RECORDS / "ceiling3"
FAMILIES = ("cross", "self", "astra", "self-strong", "self-frontier")
BOOT_SEED = 20260910          # preregistration §2
BOOTSTRAP = 10_000
CACHES = (RECORDS / "explore", RECORDS / "ceiling", CEILING3)

explore.ROUTES.update({"self-strong": "anthropic:claude-sonnet-4-6",
                       "self-frontier": "anthropic:claude-opus-4-8"})


def load_draws(scope: set[str]) -> dict[str, dict]:
    out: dict[str, dict] = {f: {} for f in FAMILIES}
    for family in FAMILIES:
        for draw in range(1, 9):
            key = ("holistic", family, draw)
            found: dict[str, dict] = {}
            for directory in CACHES:
                explore.EXPLORE = directory
                found.update(explore.load_detector(key, scope))
            complete = {i: bool(r["flagged"]) for i, r in found.items() if i in scope}
            if len(complete) == len(scope):
                out[family][draw] = complete
            elif complete:
                out[family][f"partial-{draw}"] = complete
    explore.EXPLORE = CEILING3
    return out


def load_any_finding(scope: set[str]) -> dict[str, dict[int, dict[str, bool]]]:
    """EXPLORATORY — not preregistered. ``family -> draw -> instance -> any finding``.

    The preregistered flag is "at least one BLOCKER" (studies 1, 2, 7, 8). Study 18's
    Anthropic families returned findings graded ADVISORY on many instances and BLOCKER on
    few, so a second, looser rule — "at least one finding of any severity" — is computed
    beside it to separate "does not see" from "sees and does not block". Reads the same
    record files ``explore.load_detector`` reads, taking ``model_findings`` from each row.
    """
    out: dict[str, dict[int, dict[str, bool]]] = {f: {} for f in FAMILIES}
    for family in FAMILIES:
        for draw in range(1, 9):
            key = ("holistic", family, draw)
            found: dict[str, bool] = {}
            src = explore.FREE_SOURCES.get(key)
            if src:
                path, mode, _label = src
                for line in (RECORDS / path).read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        row = json.loads(line)
                        iid = row["instance_id"] if mode == "instance" else f"b1:{row['problem_id']}"
                        if iid in scope and row.get("ok", True):
                            found[iid] = int(row.get("model_findings", 0) or 0) > 0
            for directory in CACHES:
                cache = directory / "cache" / f"{explore.detector_slug(key)}.jsonl"
                if cache.exists():
                    for line in cache.read_text(encoding="utf-8").splitlines():
                        if line.strip():
                            row = json.loads(line)
                            if row.get("ok") and row["instance_id"] in scope:
                                found[row["instance_id"]] = int(row.get("model_findings", 0) or 0) > 0
            if len(found) == len(scope):
                out[family][draw] = found
    return out


def family_block(draws: dict, ids: list[str], instances: dict, k_max: int) -> dict:
    complete = [d for d in sorted(k for k in draws if isinstance(k, int))][:k_max]
    sub = {d: draws[d] for d in complete}
    ks = rc.counts_per_instance(sub, ids)
    curve = rc.union_curve(ks, k_max)
    fit = rc.fit_saturation(curve)
    by_problem: dict[str, list[int]] = {}
    for i, k in zip(ids, ks):
        by_problem.setdefault(instances[i]["problem_id"], []).append(k)
    boot_A, boot_raw = rc.bootstrap_asymptote(by_problem, k_max, BOOTSTRAP, BOOT_SEED)
    union_flags = {i: any(sub[d].get(i) for d in complete) for i in ids}
    # The saturation fit is meaningless on a curve that is near zero at every K: the
    # least-squares A runs to its bound with a huge tau (a line through the origin), and
    # the number says nothing about the family. Preregistration §2 makes the raw union the
    # primary; the fit is reported only when the K_max union is at least 5%.
    estimable = bool(curve) and curve[-1] >= 0.05
    return {"k_max": k_max, "draws_used": complete,
            "curve": curve,
            "fit_estimable": estimable,
            "fit_note": None if estimable else "curve below 5% at K_max: asymptote not estimable (A runs to a bound)",
            "union_at_kmax": rc.clustered_rate(union_flags, ids, instances, BOOTSTRAP, BOOT_SEED),
            "single_draw_mean": curve[0] if curve else None,
            "fit": ({"A": fit["A"], "tau": fit["tau"], "r2": fit["r2"],
                     "A_ci95_cluster": [rc.percentile(boot_A, 0.025), rc.percentile(boot_A, 0.975)]}
                    if estimable else {"A": None, "tau": None, "r2": None, "A_ci95_cluster": [None, None]}),
            "flattening_gain_last_step": (curve[-1] - curve[-2]) if len(curve) >= 2 else None}


def paired_union_difference(draws_a: dict, draws_b: dict, k: int, ids: list[str], instances: dict) -> dict:
    """Union-at-K recall of A minus B on the same instances, problem-cluster bootstrap and sign-flip."""
    da = [d for d in sorted(x for x in draws_a if isinstance(x, int))][:k]
    db = [d for d in sorted(x for x in draws_b if isinstance(x, int))][:k]
    by_problem: dict[str, list[float]] = {}
    ka = kb = 0
    for i in ids:
        fa = any(draws_a[d].get(i) for d in da); fb = any(draws_b[d].get(i) for d in db)
        ka += fa; kb += fb
        by_problem.setdefault(instances[i]["problem_id"], []).append(float(fa) - float(fb))
    lo, hi = rc.cluster_bootstrap_ci(by_problem, BOOTSTRAP, BOOT_SEED)
    b = sum(1 for i in ids if any(draws_a[d].get(i) for d in da) and not any(draws_b[d].get(i) for d in db))
    c = sum(1 for i in ids if not any(draws_a[d].get(i) for d in da) and any(draws_b[d].get(i) for d in db))
    return {"k": k, "n": len(ids), "a_union": ka / len(ids), "b_union": kb / len(ids),
            "difference_points": 100 * (ka - kb) / len(ids),
            "cluster_ci95_points": [100 * lo, 100 * hi],
            "a_only": b, "b_only": c, "mcnemar_exact_p": rc.mcnemar_exact(b, c),
            "signflip": rc.signflip_p(by_problem)}


def main() -> int:
    instances = rc.load_instances()
    audit_set = rc.load_audit_set()
    scope = [i for i in audit_set if instances[i]["stratum"] in ("P", "C")]
    draws = load_draws(set(scope))
    P = [i for i in scope if instances[i]["stratum"] == "P"]
    C = [i for i in scope if instances[i]["stratum"] == "C"]
    out: dict = {"study": "study18 / ceiling 3", "bootstrap": {"seed": BOOT_SEED, "reps": BOOTSTRAP, "unit": "problem"},
                 "n_P": len(P), "n_C": len(C), "families": {}}
    kmax = {}
    for f in FAMILIES:
        complete = sorted(k for k in draws[f] if isinstance(k, int))
        kmax[f] = len(complete)
        if not complete:
            out["families"][f] = {"k_max": 0, "note": "not run",
                                  "partial": sorted(str(k) for k in draws[f] if not isinstance(k, int))}
            continue
        out["families"][f] = {"P": family_block(draws[f], P, instances, len(complete)),
                              "C": family_block(draws[f], C, instances, len(complete)),
                              "k_max": len(complete)}
        fp = out["families"][f]["C"]["curve"]; rec = out["families"][f]["P"]["curve"]
        out["families"][f]["exchange_rate_recall_per_fp"] = (
            ((rec[-1] - rec[0]) / (fp[-1] - fp[0])) if len(rec) > 1 and fp[-1] != fp[0] else None)

    def contrast(a: str, b: str, k: int, stratum: list[str]) -> dict | None:
        if kmax.get(a, 0) < k or kmax.get(b, 0) < k:
            return {"note": f"needs K={k} in both; have {kmax.get(a, 0)} and {kmax.get(b, 0)}"}
        return paired_union_difference(draws[a], draws[b], k, stratum, instances)

    kc = min(kmax.get("self-strong", 0), kmax.get("cross", 0))
    out["primary_H18b_self_strong_minus_cross_P"] = contrast("self-strong", "cross", kc, P) if kc else {"note": "no self-strong draw yet"}
    out["primary_at_k"] = kc
    out["H18a_self_strong_minus_self_P"] = contrast("self-strong", "self", min(kmax.get("self-strong", 0), kmax.get("self", 0)) or 1, P)
    out["H18b_C_false_positives"] = contrast("self-strong", "cross", kc, C) if kc else None
    kf = min(kmax.get("self-frontier", 0), kmax.get("astra", 0))
    out["H18c_frontier_minus_astra_P_k1"] = contrast("self-frontier", "astra", 1, P) if kf >= 1 else {"note": "no self-frontier draw yet"}
    out["H18c_frontier_minus_astra_P_kmax"] = contrast("self-frontier", "astra", kf, P) if kf >= 1 else None
    out["H18c_frontier_minus_astra_C_kmax"] = contrast("self-frontier", "astra", kf, C) if kf >= 1 else None

    # the one number that speaks to auditing rather than to an auditor: P instances no
    # draw of any family ever flagged
    never = [i for i in P if not any(draws[f][d].get(i) for f in FAMILIES for d in draws[f] if isinstance(d, int))]
    total_draws = sum(kmax.values())
    out["never_flagged_by_any_family"] = {
        "k": len(never), "n": len(P), "rate": len(never) / len(P), "total_draws": total_draws,
        "families_with_draws": {f: kmax[f] for f in FAMILIES if kmax[f]},
        "wilson95": list(rc.wilson(len(never), len(P))),
        "cluster_ci95": list(rc.cluster_bootstrap_ci(
            {instances[i]["problem_id"]: [] for i in P} | _by_problem({i: (i in never) for i in P}, instances), BOOTSTRAP, BOOT_SEED)),
        "instance_ids": never}
    # mixed at matched total draws: cross + self-strong, K/2 each
    if kmax.get("self-strong", 0) >= 1:
        out["mixed_cross_self_strong"] = {}
        for total in (2, 4, 6, 8):
            per = total // 2
            if kmax["cross"] >= per and kmax["self-strong"] >= per:
                m = rc.mixed_curve(draws, ["cross", "self-strong"], P, per)
                out["mixed_cross_self_strong"][f"K={total}"] = m
    # EXPLORATORY: the same curves under "any finding" instead of "at least one BLOCKER"
    any_draws = load_any_finding(set(scope))
    out["EXPLORATORY_any_finding_rule"] = {
        "note": "not preregistered; flag = model_findings > 0 (any severity); separates 'does not see' from 'sees and does not block'",
        "families": {}}
    for f in FAMILIES:
        complete = sorted(k for k in any_draws[f] if isinstance(k, int))
        if not complete:
            continue
        sub = {d: any_draws[f][d] for d in complete}
        entry = {"k_max": len(complete)}
        for label, ids in (("P", P), ("C", C)):
            ks = rc.counts_per_instance(sub, ids)
            curve = rc.union_curve(ks, len(complete))
            union_flags = {i: any(sub[d].get(i) for d in complete) for i in ids}
            entry[label] = {"curve": curve, "single_draw_mean": curve[0],
                            "union_at_kmax": rc.clustered_rate(union_flags, ids, instances, BOOTSTRAP, BOOT_SEED)}
        out["EXPLORATORY_any_finding_rule"]["families"][f] = entry
    never_any = [i for i in P if not any(any_draws[f][d].get(i) for f in FAMILIES for d in any_draws[f] if isinstance(d, int))]
    out["EXPLORATORY_any_finding_rule"]["never_any_finding_by_any_family_P"] = {
        "k": len(never_any), "n": len(P), "rate": len(never_any) / len(P), "wilson95": list(rc.wilson(len(never_any), len(P)))}
    # cost per reading from this study's caches
    costs = {}
    for f in ("self-strong", "self-frontier"):
        for d in range(1, 9):
            path = CEILING3 / "cache" / f"holistic__{f}__d{d}.jsonl"
            if path.exists():
                rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
                if rows:
                    costs[f"{f}-d{d}"] = {"n": len(rows), "usd": round(sum(float(r.get("cost_usd") or 0) for r in rows), 4)}
    out["cost_by_draw"] = costs
    CEILING3.mkdir(parents=True, exist_ok=True)
    (CEILING3 / "numbers.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for f in FAMILIES:
        e = out["families"][f]
        if e.get("k_max"):
            p, c = e["P"], e["C"]
            print(f"{f:14s} K={e['k_max']}  P union {100*p['union_at_kmax']['rate']:.1f}% "
                  f"[{100*p['union_at_kmax']['cluster_ci95'][0]:.1f}, {100*p['union_at_kmax']['cluster_ci95'][1]:.1f}]  "
                  f"A={('%.1f%%' % (100*p['fit']['A'])) if p['fit_estimable'] else 'n/e'}  C union {100*c['union_at_kmax']['rate']:.1f}%  "
                  f"single {100*(p['single_draw_mean'] or 0):.1f}%")
        else:
            print(f"{f:14s} not run")
    pr = out["primary_H18b_self_strong_minus_cross_P"]
    if "difference_points" in pr:
        print(f"\nPRIMARY (K={pr['k']}): self-strong − cross on P = {pr['difference_points']:+.1f} points "
              f"[{pr['cluster_ci95_points'][0]:+.1f}, {pr['cluster_ci95_points'][1]:+.1f}]  "
              f"a-only {pr['a_only']} b-only {pr['b_only']} McNemar p={pr['mcnemar_exact_p']:.3f} "
              f"sign-flip p={pr['signflip']['p']:.3f}")
    nv = out["never_flagged_by_any_family"]
    print(f"never flagged by any family: {nv['k']}/{nv['n']} = {100*nv['rate']:.1f}% over {nv['total_draws']} draws")
    ex = out["EXPLORATORY_any_finding_rule"]
    print("\nEXPLORATORY any-finding rule (not preregistered):")
    for f, e in ex["families"].items():
        print(f"  {f:14s} K={e['k_max']}  P union {100*e['P']['union_at_kmax']['rate']:.1f}%  single {100*e['P']['single_draw_mean']:.1f}%  "
              f"C union {100*e['C']['union_at_kmax']['rate']:.1f}%  single {100*e['C']['single_draw_mean']:.1f}%")
    na = ex["never_any_finding_by_any_family_P"]
    print(f"  never any finding by any family: {na['k']}/{na['n']} = {100*na['rate']:.1f}%")
    return 0


def _by_problem(flags: dict, instances: dict) -> dict:
    by: dict[str, list[float]] = {}
    for i, v in flags.items():
        by.setdefault(instances[i]["problem_id"], []).append(1.0 if v else 0.0)
    return by


if __name__ == "__main__":
    raise SystemExit(main())
