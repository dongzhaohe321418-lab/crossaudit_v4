"""Study 15, the wrap-join slice: the frozen Arm 6 rows re-verified on joined source text.

    PYTHONPATH=src python benchmarks/expertlongbench/study15/wrapjoin.py --run <archive>/arm6

`join_wraps` is the preregistered rule (`PREREGISTRATION-WRAPJOIN.md` §1), a pure function
of the text. The driver rebuilds each archived instance's audited increment exactly as Arm
6 did, asserts every row's unjoined verdict equals the recorded one, replaces every source
file (never the draft) by its joined text, and runs the SHIPPED matcher unmodified
(`provenance_arm4.verify_shipped` / `located_line`, which reach `numbers._row_findings` and
`numbers._quote_span`) on that mapping; a located joined line is mapped back to its original
line span. Writes `rows-arm6-wrapjoin.jsonl` and `report-wrapjoin.json`; prints shapes only.
No row is relabelled; the gold is read, never written. Wilson and the draft-clustered
bootstrap are `arm6_rates.py`'s with the seed changed to 20261109 and nothing else.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED, REPS = 20261109, 10_000

# --------------------------------------------------------------- the join rule

_FENCE_LINE = re.compile(r"^(?:`{3,}|~{3,})")
_ATX = re.compile(r"^#(?:[ \t]|#)")
_RULE_LINE = re.compile(r"^([=\-_*])\1{2,}$")
_BULLET = re.compile(r"^[-*+][ \t]")
_ORDERED = re.compile(r"^[0-9]{1,9}[.)][ \t]")


def is_fence_line(line: str) -> bool:
    return bool(_FENCE_LINE.match(line.lstrip()))


def is_structural(line: str) -> bool:
    """Empty, ATX heading, table row, blockquote, code-fence line, setext underline or
    thematic break — a line no wrap continues into or out of.

    Read after the line's LEADING whitespace is removed and nothing else, as the
    preregistration §1 says: `# ` (a trailing space) is a heading, and `--- ` is not a
    rule line because it does not consist of the rule characters and nothing else. The
    first commit of this slice read `strip()` here and deviated; the results say so."""
    s = line.lstrip()
    if not s:
        return True
    return bool(_ATX.match(s) or s.startswith("|") or s.startswith(">")
                or _FENCE_LINE.match(s) or _RULE_LINE.match(s))


def is_block_opening(line: str) -> bool:
    """A bullet or an ordered-list marker: the line starts a block, so the break before
    it is kept even inside a paragraph."""
    if is_structural(line):
        return False
    s = line.lstrip()
    return bool(_BULLET.match(s) or _ORDERED.match(s))


def join_wraps(text: str) -> tuple[str, list[tuple[int, int]]]:
    """Join the hard wraps of `text` under the preregistered rule.

    Returns `(joined_text, mapping)`: `mapping[k] = (start, end)` is the 0-based inclusive
    span of original lines that joined line `k` was made from; the spans partition the
    original lines in order. The break between original lines A and B is joined iff it is
    outside a code fence, neither A nor B is structural, and B is not block-opening; a
    joined break becomes one space (A's trailing and B's leading whitespace dropped).
    """
    lines = text.split("\n")
    joined: list[str] = []
    mapping: list[tuple[int, int]] = []
    in_fence = False
    for i, line in enumerate(lines):
        if (i > 0 and not in_fence and not is_structural(lines[i - 1])
                and not is_structural(line) and not is_block_opening(line)):
            joined[-1] = joined[-1].rstrip() + " " + line.lstrip()
            mapping[-1] = (mapping[-1][0], i)
        else:
            joined.append(line)
            mapping.append((i, i))
        if is_fence_line(line):
            in_fence = not in_fence
    return "\n".join(joined), mapping


# ---------------------------------------------------------------- the intervals
# copied from arm6_rates.py; the seed is this slice's (PREREGISTRATION-WRAPJOIN §4)

def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def draft_bootstrap(by_draft: dict[str, tuple[int, int]]) -> tuple[float, float, int]:
    drafts = list(by_draft)
    rng = random.Random(SEED)
    stats, discarded = [], 0
    for _ in range(REPS):
        k = n = 0
        for _ in range(len(drafts)):
            kk, nn = by_draft[drafts[rng.randrange(len(drafts))]]
            k += kk
            n += nn
        if n == 0:
            discarded += 1
            continue
        stats.append(k / n)
    if not stats:
        return 0.0, 0.0, discarded
    stats.sort()
    return stats[int(0.025 * (len(stats) - 1))], stats[int(0.975 * (len(stats) - 1))], discarded


def rate(name: str, rows, all_drafts: list[str], out: dict | None = None) -> dict:
    """rows: iterable of (draft, in_denominator, in_numerator); every draft a cluster."""
    by = {d: [0, 0] for d in all_drafts}
    k = n = 0
    for draft, in_d, in_k in rows:
        by.setdefault(draft, [0, 0])
        if not in_d:
            continue
        by[draft][1] += 1
        n += 1
        if in_k:
            by[draft][0] += 1
            k += 1
    lo, hi = wilson(k, n)
    blo, bhi, disc = draft_bootstrap({d: (v[0], v[1]) for d, v in by.items()})
    print(f"{name:58s} {k:4d}/{n:<4d} = {100 * k / n if n else float('nan'):6.2f}%  "
          f"Wilson {100 * lo:6.2f}–{100 * hi:6.2f}%  bootstrap {100 * blo:6.2f}–{100 * bhi:6.2f}%"
          + (f"  ({disc} discarded)" if disc else ""))
    entry = {"k": k, "n": n, "wilson": [lo, hi], "bootstrap": [blo, bhi], "discarded": disc}
    if out is not None:
        out[name] = entry
    return entry


# ------------------------------------------------------------------ the driver

def joined_increment(files: dict[str, bytes], draft_path: str):
    """The audited increment with every source file (never the draft) joined.
    Returns (joined_files, mappings) where mappings[key] is join_wraps' mapping."""
    out, mappings = {}, {}
    for key, blob in files.items():
        if key == draft_path:
            out[key] = blob
            continue
        try:
            text = blob.decode("utf-8")
        except UnicodeDecodeError:
            out[key] = blob
            continue
        joined, mapping = join_wraps(text)
        out[key] = joined.encode("utf-8")
        mappings[key] = mapping
    return out, mappings


def joined_line_hits(joined_text: str, quote: str, fold) -> list[int]:
    """The indices of the joined lines whose fold holds the folded quotation —
    `_quote_span`'s line rule, re-stated here only to recover indices, which the shipped
    function does not return."""
    needle = fold(quote)
    if not needle:
        return []
    return [i for i, line in enumerate(joined_text.split("\n")) if needle in fold(line)]


def joined_line_index(joined_text: str, quote: str, fold) -> int | None:
    """The index of the ONE joined line holding the quotation, or None (absent, or on
    more than one joined line)."""
    hits = joined_line_hits(joined_text, quote, fold)
    return hits[0] if len(hits) == 1 else None


def fence_shape(text: str) -> tuple[int, float]:
    """(fence-shaped lines, share of lines inside fence state) — a file with an odd count
    stays unjoined from its last fence line to its end."""
    lines = text.split("\n")
    inside = 0
    state = False
    for line in lines:
        inside += state
        if is_fence_line(line):
            state = not state
    return sum(1 for l in lines if is_fence_line(l)), inside / len(lines)


def fold_index(lines: list[str]) -> list[int]:
    """For the whitespace fold of `"\n".join(lines)`, the index into `lines` of every
    folded character (a joining space is charged to the line it precedes)."""
    idx: list[int] = []
    pending = started = False
    for li, line in enumerate(lines):
        for ch in line:
            if ch.isspace():
                pending = True
                continue
            if pending and started:
                idx.append(li)
            pending = False
            started = True
            idx.append(li)
        pending = True
    return idx


_CURRENCY = "$€£¥"


def block_shape(quote: str, v: str, u: str) -> str:
    """A predicate on the quotation, not a label: the shape of a located block.
    `currency-sign-before-value` is M13's shape (Arm 6's three wrong blocks);
    `value-not-in-quotation-as-written` is M1b's; `other` is everything else."""
    forms = [v]
    if re.fullmatch(r"\d+(\.\d+)?", v):
        whole, _, frac = v.partition(".")
        forms.append(f"{int(whole):,}" + (f".{frac}" if frac else ""))
    q = " ".join(quote.split())
    i = next((q.find(f) for f in forms if f in q), -1)
    if i < 0:
        return "value-not-in-quotation-as-written"
    before = q[max(0, i - 2):i]
    if u in _CURRENCY and any(c in before for c in _CURRENCY):
        return "currency-sign-before-value"
    return "other"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="the archive's arm6 directory (read-only)")
    ap.add_argument("--out", default=str(HERE), help="where the two records are written")
    args = ap.parse_args(argv)
    run_dir, out_dir = Path(args.run), Path(args.out)

    sys.path.insert(0, str(HERE.parent))
    import provenance_arm3 as arm3
    import provenance_arm4 as arm4
    from run import OUTPUT_PATH
    from crossaudit.config import load as load_cfg
    from crossaudit.dcl import numbers as num_mod

    rows = [json.loads(l) for l in (HERE / "rows-arm6.jsonl").read_text().splitlines() if l.strip()]
    manifest = json.loads((HERE / "manifest-arm6.json").read_text())
    all_drafts = [d["instance"] for d in manifest["drafts"]]
    gold = {}
    for line in (HERE / "GOLD-arm6.csv").read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        item, label, rule = line.split(",")
        gold[item] = label
    for r in rows:                      # the frozen gold is what the rows already carry
        assert (r["gold_label"] or "") == gold.get(r["gold_item"], ""), r["gold_item"]
    by_key = {(r["instance"], r["row"]): r for r in rows}
    matcher = arm4.matcher_version()
    assert all(r["matcher_version"] == matcher for r in rows), "the shipped matcher blob changed"

    new_rows: list[dict] = []
    file_shapes: list[dict] = []
    seen = 0
    for proj_dir in sorted((run_dir / "instances").iterdir()):
        project = proj_dir / "project"
        if not (project / "crossaudit.yml").exists():
            continue
        instance = proj_dir.name.rsplit("__", 1)[0]
        cfg = load_cfg(project / "crossaudit.yml")
        sha = arm3.science_commit(project)
        files = arm3.audited_increment(project, sha, cfg)
        draft = files.get(OUTPUT_PATH, b"").decode("utf-8", "replace")
        jfiles, mappings = joined_increment(files, OUTPUT_PATH)
        for key, mapping in mappings.items():
            original = files[key].decode("utf-8")
            joined = jfiles[key].decode("utf-8")
            assert num_mod._fold(joined) == num_mod._fold(original)
            fences, inside = fence_shape(original)
            file_shapes.append({"instance": instance, "file": key,
                                "original_lines": original.count("\n") + 1,
                                "joined_lines": len(mapping),
                                "joined_breaks": original.count("\n") + 1 - len(mapping),
                                "fence_lines": fences, "share_inside_fence": inside})
        for row_no, ann in enumerate(arm3.fence_rows(draft)):
            rec = by_key[(instance, row_no)]
            seen += 1
            sev0, rule0, reason0 = arm4.verify_shipped(files, ann, draft)
            assert (sev0, rule0, reason0) == (rec["severity"], rec["disposition"], rec["reason"]), \
                f"{instance} row {row_no}: the unjoined verdict does not reproduce"
            sev, rule, reason = arm4.verify_shipped(jfiles, ann, draft)
            loc = arm4.located_line(jfiles, ann)
            v, u = str(ann.get("v", "")), str(ann.get("u", ""))
            src = ann.get("src")
            span = qspan = None
            adj_a = adj_b = None
            shape = ""
            occurrences = None
            if isinstance(src, dict) and isinstance(src.get("file"), str) and isinstance(src.get("quote"), str):
                jkey = arm3.resolve_key(jfiles, OUTPUT_PATH, src["file"])
                if jkey is not None:
                    occurrences = len(joined_line_hits(jfiles[jkey].decode("utf-8"), src["quote"], num_mod._fold))
            if loc is not None:
                assert occurrences == loc[2] == 1
                key, line, hits = loc
                jtext = jfiles[key].decode("utf-8")
                idx = joined_line_index(jtext, src["quote"], num_mod._fold)
                assert idx is not None and num_mod._fold(jtext.split("\n")[idx]) == line
                span = mappings[key][idx]
                # the quotation's own interval on the folded joined line, mapped back to
                # the original lines it covers (the first interval where a line holds
                # the quotation twice, as the shipped matcher accepts any of them)
                original = files[key].decode("utf-8").split("\n")[span[0]:span[1] + 1]
                located, _ = num_mod._quote_span(jtext, src["quote"])
                fidx = fold_index(original)
                assert len(fidx) == len(line), "the joined line does not fold to its span"
                qs, qe = located.spans[0]
                qspan = (span[0] + fidx[qs], span[0] + fidx[qe - 1])
                adj_a = num_mod.contains_pair(line, v, u)
                adj_b = arm3.adjudicator_b(line, v, u)
                if sev == "BLOCKER":
                    shape = block_shape(src["quote"], v, u)
            new = dict(rec)
            new.update({
                "located_after_join": loc is not None,
                "crosses_after_join": reason == "quote-crosses-line",
                "joined_span_lines": (span[1] - span[0] + 1) if span else None,
                "joined_span_start": (span[0] + 1) if span else None,
                "joined_span_end": (span[1] + 1) if span else None,
                "quote_span_lines": (qspan[1] - qspan[0] + 1) if qspan else None,
                "quote_span_start": (qspan[0] + 1) if qspan else None,
                "quote_span_end": (qspan[1] + 1) if qspan else None,
                "block_shape_after_join": shape,
                "severity_after_join": sev, "disposition_after_join": rule,
                "reason_after_join": reason,
                "occurrences_after_join": occurrences,
                "adj_a_after_join": adj_a, "adj_b_after_join": adj_b,
                "newly_located": (loc is not None) and not rec["resolved_location"],
                "verdict_changed": (sev, reason) != (rec["severity"], rec["reason"]),
            })
            new_rows.append(new)
    assert seen == len(rows) == len(new_rows), (seen, len(rows), len(new_rows))
    new_rows.sort(key=lambda r: (all_drafts.index(r["instance"]), r["row"]))

    addressed = lambda r: r["src_kind"] not in ("uncited", "governed")
    q1 = lambda r: r["mechanism"] == "Q1"
    q2 = lambda r: r["mechanism"] == "Q2"
    located = lambda r: bool(r["located_after_join"])
    newly = lambda r: bool(r["newly_located"])
    blocked_after = lambda r: r["severity_after_join"] == "BLOCKER"
    passed_after = lambda r: r["severity_after_join"] == "PASS"
    ambiguous_after = lambda r: r["reason_after_join"] == "ambiguous"
    labelled_c = lambda r: r["gold_label"] == "C"
    labelled = lambda r: bool(r["gold_label"])

    print(f"rows {len(rows)}; drafts {len(all_drafts)}; seed {SEED}, {REPS} resamples; matcher {matcher[:8]}\n")
    report: dict = {"seed": SEED, "reps": REPS, "matcher_version": matcher,
                    "drafts": len(all_drafts), "rows": len(rows), "rates": {}}
    R = report["rates"]
    print("(a) the 40 Q1 rows after the join")
    a = rate("(a) Q1 rows located after join / Q1 rows", [(r["instance"], q1(r), q1(r) and located(r)) for r in new_rows], all_drafts, R)
    rate("    Q1 rows ambiguous after join (more than one joined line) / Q1 rows", [(r["instance"], q1(r), q1(r) and ambiguous_after(r)) for r in new_rows], all_drafts, R)
    rate("    Q1 rows still crossing after join / Q1 rows", [(r["instance"], q1(r), q1(r) and r["crosses_after_join"]) for r in new_rows], all_drafts, R)
    rate("    Q1 rows absent after join / Q1 rows", [(r["instance"], q1(r), q1(r) and r["reason_after_join"] == "quote-absent") for r in new_rows], all_drafts, R)
    print("\n(b) the newly located rows, by the shipped verdict on joined text (no gold; unlabelled candidates)")
    b_pass = rate("(b) newly located rows PASSED / newly located rows", [(r["instance"], newly(r), newly(r) and passed_after(r)) for r in new_rows], all_drafts, R)
    b_block = rate("(b) newly located rows BLOCKED (pair not in the quoted interval) / newly located rows", [(r["instance"], newly(r), newly(r) and blocked_after(r)) for r in new_rows], all_drafts, R)
    rate("    newly located rows from Q1 / newly located rows", [(r["instance"], newly(r), newly(r) and q1(r)) for r in new_rows], all_drafts, R)
    rate("    newly located rows from Q2 / newly located rows", [(r["instance"], newly(r), newly(r) and q2(r)) for r in new_rows], all_drafts, R)
    rate("    newly located BLOCKED rows with adj_a true (pair elsewhere on the joined line)", [(r["instance"], newly(r) and blocked_after(r), newly(r) and blocked_after(r) and bool(r["adj_a_after_join"])) for r in new_rows], all_drafts, R)
    rate("    newly located BLOCKED rows with adj_b true (value an exact substring of the line)", [(r["instance"], newly(r) and blocked_after(r), newly(r) and blocked_after(r) and bool(r["adj_b_after_join"])) for r in new_rows], all_drafts, R)
    rate("    newly located PASSED rows with adj_b true", [(r["instance"], newly(r) and passed_after(r), newly(r) and passed_after(r) and bool(r["adj_b_after_join"])) for r in new_rows], all_drafts, R)
    print("\n(c) the 19 labelled rows after the join")
    c = rate("(c) §8g after join: gold-C rows BLOCKED / gold-C rows located after join", [(r["instance"], labelled_c(r) and located(r), labelled_c(r) and located(r) and blocked_after(r)) for r in new_rows], all_drafts, R)
    rate("    gold-C rows still located after join / gold-C rows", [(r["instance"], labelled_c(r), labelled_c(r) and located(r)) for r in new_rows], all_drafts, R)
    rate("    labelled rows whose verdict changed / labelled rows", [(r["instance"], labelled(r), labelled(r) and r["verdict_changed"]) for r in new_rows], all_drafts, R)
    rate("    labelled passes still passing / labelled passes", [(r["instance"], labelled(r) and r["severity"] == "PASS", labelled(r) and r["severity"] == "PASS" and passed_after(r)) for r in new_rows], all_drafts, R)
    print("\n(d) crossing after the join")
    d = rate("(d) quote-crosses-line after join / addressed rows", [(r["instance"], addressed(r), addressed(r) and r["crosses_after_join"]) for r in new_rows], all_drafts, R)
    print("\nsecondaries")
    rate("located after join / addressed rows", [(r["instance"], addressed(r), addressed(r) and located(r)) for r in new_rows], all_drafts, R)
    rate("ambiguous after join / addressed rows", [(r["instance"], addressed(r), addressed(r) and ambiguous_after(r)) for r in new_rows], all_drafts, R)
    rate("Q2 rows located after join / Q2 rows", [(r["instance"], q2(r), q2(r) and located(r)) for r in new_rows], all_drafts, R)
    rate("PASS after join / blockable rows", [(r["instance"], addressed(r) and r["severity"] != "ADVISORY", addressed(r) and r["severity"] != "ADVISORY" and passed_after(r)) for r in new_rows], all_drafts, R)
    rate("verdict changed / all rows", [(r["instance"], True, r["verdict_changed"]) for r in new_rows], all_drafts, R)
    spans = Counter(r["joined_span_lines"] for r in new_rows if newly(r))
    report["newly_located_joined_line_span_lines"] = {str(k): v for k, v in sorted(spans.items())}
    print("original lines per located JOINED LINE (the paragraph), newly located rows: " + ", ".join(f"{k}: {v}" for k, v in sorted(spans.items())))
    qspans = Counter(r["quote_span_lines"] for r in new_rows if newly(r))
    report["newly_located_quote_span_lines"] = {str(k): v for k, v in sorted(qspans.items())}
    print("original lines the QUOTATION itself covers, newly located rows: " + ", ".join(f"{k} lines: {v}" for k, v in sorted(qspans.items())))
    shapes = Counter(r["block_shape_after_join"] for r in new_rows if newly(r) and blocked_after(r))
    report["newly_located_block_shapes"] = dict(sorted(shapes.items()))
    print("shapes of the newly located BLOCKS (a predicate on the quotation, not a label): " + ", ".join(f"{k}: {v}" for k, v in sorted(shapes.items())))
    for name, pred in (("currency-sign-before-value", "currency-sign-before-value"),
                       ("value-not-in-quotation-as-written", "value-not-in-quotation-as-written"),
                       ("other", "other")):
        rate(f"    newly located BLOCKS shaped {name} / newly located blocks", [(r["instance"], newly(r) and blocked_after(r), newly(r) and blocked_after(r) and r["block_shape_after_join"] == pred) for r in new_rows], all_drafts, R)
    lab_shapes = Counter(r["block_shape_after_join"] for r in new_rows if labelled(r) and blocked_after(r) and located(r))
    print("shapes of the labelled located BLOCKS after join (check: Arm 6's 3 M13 + 2 M1b): " + ", ".join(f"{k}: {v}" for k, v in sorted(lab_shapes.items())))
    report["labelled_located_block_shapes_after_join"] = dict(sorted(lab_shapes.items()))
    changed = Counter((r["severity"], r["reason"], r["severity_after_join"], r["reason_after_join"])
                      for r in new_rows if r["verdict_changed"])
    report["verdict_transitions"] = [{"before": [a_, b_], "after": [c_, d_], "n": n_} for (a_, b_, c_, d_), n_ in sorted(changed.items())]
    print("verdict transitions (before -> after): " + "; ".join(f"{a_}/{b_} -> {c_}/{d_}: {n_}" for (a_, b_, c_, d_), n_ in sorted(changed.items())))
    ratios = sorted(f["joined_lines"] / f["original_lines"] for f in file_shapes)
    report["file_shapes"] = {"files": len(file_shapes),
                             "joined_over_original_lines": {"min": ratios[0], "median": ratios[len(ratios) // 2], "max": ratios[-1]},
                             "original_lines_total": sum(f["original_lines"] for f in file_shapes),
                             "joined_lines_total": sum(f["joined_lines"] for f in file_shapes)}
    print(f"files joined {len(file_shapes)}: joined/original lines min {ratios[0]:.3f} median {ratios[len(ratios) // 2]:.3f} max {ratios[-1]:.3f}")
    fenced = [f for f in file_shapes if f["fence_lines"]]
    report["file_shapes"]["files_with_fence_shaped_lines"] = len(fenced)
    report["file_shapes"]["files_with_an_odd_fence_count"] = sum(1 for f in fenced if f["fence_lines"] % 2)
    report["file_shapes"]["share_inside_fence"] = {f["instance"]: f["share_inside_fence"] for f in fenced}
    print(f"files with fence-shaped lines {len(fenced)} (odd count, unclosed: {sum(1 for f in fenced if f['fence_lines'] % 2)}); "
          f"share of lines inside fence state: " + ", ".join(f"{f['share_inside_fence']:.3f}" for f in fenced))
    amb = Counter(r["occurrences_after_join"] for r in new_rows if r["reason_after_join"] == "ambiguous")
    report["ambiguous_after_join_occurrences"] = {str(k): v for k, v in sorted(amb.items())}
    print("joined lines holding the quotation, ambiguous rows after join: " + ", ".join(f"{k} lines: {v}" for k, v in sorted(amb.items())))
    nl_drafts = Counter(r["instance"] for r in new_rows if newly(r))
    report["newly_located_per_draft"] = sorted(nl_drafts.values())
    print(f"newly located rows lie in {len(nl_drafts)} drafts: " + ", ".join(str(v) for v in sorted(nl_drafts.values(), reverse=True)))

    # the kill (PREREGISTRATION-WRAPJOIN §3)
    first = a["k"] * 2 >= a["n"]
    bound = b_block["k"] / b_block["n"] if b_block["n"] else None
    second = None if bound is None else (bound <= 3 / 17)
    if not first:
        verdict = "does not stand"
    elif second:
        verdict = "stands"
    else:
        verdict = "undetermined"
    report["kill"] = {"clause_1_at_least_half_of_Q1_located": first, "q1_located": [a["k"], a["n"]],
                      "clause_2_blocked_share_bound_at_or_below_3_of_17": second,
                      "newly_located_blocked": [b_block["k"], b_block["n"]], "bound": bound,
                      "labellable_by_an_existing_rule": 0, "verdict": verdict}
    print(f"\nkill: clause 1 (>= 20 of 40 Q1 located): {first} ({a['k']}/{a['n']}); "
          f"clause 2 (blocked share among newly located <= 3/17 = 17.65%): {second} "
          f"({b_block['k']}/{b_block['n']}); verdict: {verdict}")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "rows-arm6-wrapjoin.jsonl").write_text("".join(json.dumps(r) + "\n" for r in new_rows))
    (out_dir / "report-wrapjoin.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
