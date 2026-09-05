#!/usr/bin/env python3
"""Simulate the two candidate addressing contracts on Arm 2's archived drafts.

`docs/design/PROVENANCE_ADDRESSING.md`. No model calls, no new generation: this
reads the 24 archived Arm 2 projects, re-parses the ```crossaudit-numbers fences
the generator already wrote, and asks — with the SHIPPED matcher
(`crossaudit.dcl.numbers.contains_pair`), never a new one — three questions the
archive can answer for free:

  A. **Numbered rendering.** If the generator's `src` line index is off by a
     per-draft constant, and showing it line numbers removes exactly that
     constant, how many of the span rows then name a line that contains the
     transcribed pair? Two readings are reported: the draft's MODAL offset
     (what numbering would plausibly fix) and the per-draft offset that maximises
     landings (an upper bound no prompt change can beat).

  B. **Content addressing.** Does the FILE the generator named contain the pair
     on exactly ONE line? That is B's ceiling: a quote copied around the pair can
     only be resolved unambiguously when there is one place to resolve it to. A
     stricter variant is also reported — whether some window of <= QUOTE_MAX
     characters containing the pair is a UNIQUE substring of the file — because
     that is what B's matcher would actually do.

  T. **Token cost of numbering.** The scope files of each instance rendered the
     way `generator.build_prompt` renders them (`generator.py:449-450`), with and
     without a line-number gutter, measured through the product's own token path
     (`usage.py:169`, ceil(chars/4)), and expressed against the generator input
     tokens the run's own usage ledger reports.

**Corpus-free by construction.** The corpus is CC BY-NC-SA and is not
redistributed (RESULTS-ARM2 §10). This script reads the read-only archive at a
path given on the command line and prints ids, counts and booleans only: no
draft text, no source text, no transcribed value or unit, no quote. Adding a
print of any span to this file would make its output undistributable.

Usage:

    PYTHONPATH=<worktree>/src python3 benchmarks/expertlongbench/study7/addressing_sim.py \
        ~/Documents/Crossaudit/study-data/wt-arm2-runs/arm2 [--json out.json]
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import re
import sys

from crossaudit.dcl.numbers import _AT, _FENCE, _SPAN, contains_pair

#: The archived harness's layout (`benchmarks/expertlongbench/run.py:71-74`).
SCOPE_DIR = "work"
DRAFT_PATH = "work/synthesis/explanation.md"

#: Contract B's cap on a quoted span, from the design document.
QUOTE_MAX = 80

#: The gutter contract A would render: right-aligned width 5, then "| ".
GUTTER = "{:>5}| "


# ----------------------------------------------------------------------------
# reading the archive
# ----------------------------------------------------------------------------

def instances(archive: pathlib.Path) -> list[pathlib.Path]:
    root = archive / "instances"
    return sorted(p for p in root.iterdir() if (p / "project").is_dir())


def scope_files(project: pathlib.Path) -> dict[str, str]:
    """Every text file under the audited scope, keyed as the prompt keys them."""
    base = project / SCOPE_DIR
    out: dict[str, str] = {}
    for p in sorted(base.rglob("*")):
        if p.is_file() and not p.is_symlink():
            try:
                out[p.relative_to(project).as_posix()] = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
    return out


def fence_rows(text: str) -> list[dict]:
    rows: list[dict] = []
    for body in _FENCE.findall(text):
        try:
            parsed = json.loads(body, parse_float=str, parse_int=str)
        except ValueError:
            continue
        if isinstance(parsed, list):
            rows.extend(r for r in parsed if isinstance(r, dict))
    return rows


def resolve(files: dict[str, str], annotated: str, named: str) -> str | None:
    """`numbers._resolve`, over a str mapping."""
    if named in files:
        return named
    base = annotated.rsplit("/", 1)[0] if "/" in annotated else ""
    joined = f"{base}/{named}" if base else ""
    return joined if joined in files else None


# ----------------------------------------------------------------------------
# the two simulations
# ----------------------------------------------------------------------------

def true_lines(lines: list[str], v: str, u: str) -> list[int]:
    """Every 1-based line of the file whose text contains the transcribed pair."""
    return [i for i, line in enumerate(lines, 1) if contains_pair(line, v, u)]


def unique_quote_exists(line: str, v: str, u: str, body: str) -> bool:
    """Whether some window of <= QUOTE_MAX chars of `line` that still contains the
    pair occurs exactly once in the whole file.

    This is contract B's matcher run backwards: B asks the generator for such a
    window, so the question the archive can answer is whether one is available to
    copy. Whitespace is collapsed on both sides first, which is the single
    normalisation §3.3 already performs on a quoted span.
    """
    flat_body = " ".join(body.split())
    flat_line = " ".join(line.split())
    if len(flat_line) <= QUOTE_MAX:
        return contains_pair(flat_line, v, u) and flat_body.count(flat_line) == 1
    for start in range(0, len(flat_line) - QUOTE_MAX + 1):
        window = flat_line[start:start + QUOTE_MAX]
        if contains_pair(window, v, u) and flat_body.count(window) == 1:
            return True
    return False


def analyse_instance(project: pathlib.Path, instance: str) -> dict:
    files = scope_files(project)
    draft = files.get(DRAFT_PATH, "")
    draft_lines = draft.count("\n") + 1
    record = {
        "instance": instance,
        "draft_lines": draft_lines,
        "rows": 0, "span_rows": 0, "uncited": 0, "unresolved_locator": 0,
        "at_past_end": 0,
        # B
        "b_file_contains": 0, "b_unique_line": 0, "b_unique_quote": 0,
        "b_ambiguous": 0, "b_absent": 0,
        # A
        "a_named_line_lands": 0, "a_modal_lands": 0, "a_best_lands": 0,
        "modal_offset": None, "best_offset": None, "offsets": [],
        "single_offset_draft": False,
        # A ∩ B, on the same rows
        "both": 0, "a_only": 0, "b_only": 0, "neither": 0,
    }
    rows = fence_rows(draft)
    record["rows"] = len(rows)
    spans: list[tuple[int, list[int], list[str], str, str, str]] = []
    for row in rows:
        if any(k not in row for k in ("v", "u", "at", "src")):
            continue
        at = _AT.fullmatch(str(row["at"] or ""))
        if at is not None:
            start = int(at.group("start"))
            end = int(at.group("end") or start)
            if start < 1 or end < start or end > draft_lines:
                record["at_past_end"] += 1
        else:
            record["at_past_end"] += 1
        src = str(row["src"])
        if src == "uncited" or src.startswith("governed:"):
            record["uncited"] += 1
            continue
        locator = src[len("computed:"):] if src.startswith("computed:") else src
        m = _SPAN.fullmatch(locator)
        if m is None:
            record["unresolved_locator"] += 1
            continue
        key = resolve(files, DRAFT_PATH, m.group("path"))
        if key is None:
            record["unresolved_locator"] += 1
            continue
        v, u = str(row["v"]), str(row["u"])
        named = int(m.group("start"))
        body = files[key]
        lines = body.split("\n")
        hits = true_lines(lines, v, u)
        record["span_rows"] += 1
        spans.append((named, hits, lines, v, u, body))

        # --- contract B ------------------------------------------------------
        if hits:
            record["b_file_contains"] += 1
        if len(hits) == 1:
            record["b_unique_line"] += 1
            if unique_quote_exists(lines[hits[0] - 1], v, u, body):
                record["b_unique_quote"] += 1
        elif len(hits) > 1:
            record["b_ambiguous"] += 1
        else:
            record["b_absent"] += 1

        # --- contract A, as shipped -----------------------------------------
        end = int(m.group("end") or named)
        if any(named <= h <= end for h in hits):
            record["a_named_line_lands"] += 1

    # --- contract A, offsets -------------------------------------------------
    offsets: list[int] = []
    for named, hits, *_ in spans:
        if hits:
            # nearest true line; ties break toward the smaller absolute offset,
            # then toward the positive one (the direction Arm 2 measured).
            offsets.append(min((h - named for h in hits), key=lambda d: (abs(d), -d)))
    record["offsets"] = sorted(offsets)
    if offsets:
        counts = collections.Counter(offsets)
        top = max(counts.values())
        modal = min((o for o, c in counts.items() if c == top), key=abs)
        record["modal_offset"] = modal
        record["single_offset_draft"] = len(counts) == 1
        record["a_modal_lands"] = sum(
            1 for named, hits, *_ in spans if (named + modal) in hits)
        candidates = {h - named for named, hits, *_ in spans for h in hits}
        best, best_n = 0, 0
        for delta in sorted(candidates, key=lambda d: (abs(d), -d)):
            n = sum(1 for named, hits, *_ in spans if (named + delta) in hits)
            if n > best_n:
                best, best_n = delta, n
        record["best_offset"], record["a_best_lands"] = best, best_n
        for named, hits, *_ in spans:
            a = (named + modal) in hits
            b = len(hits) == 1
            key = "both" if (a and b) else "a_only" if a else "b_only" if b else "neither"
            record[key] += 1
    else:
        record["neither"] = record["span_rows"]
    return record


# ----------------------------------------------------------------------------
# the token cost of numbering
# ----------------------------------------------------------------------------

def tokens(text: str) -> int:
    """The product's own token path for an unreported call (`usage.py:169`)."""
    return math.ceil(len(text) / 4)


def number(text: str) -> str:
    lines = text.split("\n")
    return "\n".join(GUTTER.format(i) + line for i, line in enumerate(lines, 1))


def render(files: dict[str, str], numbered: bool) -> str:
    """`generator.build_prompt`'s WORK rendering (`generator.py:450`), verbatim
    but for the optional gutter."""
    return "\n".join(
        f"--- {p} ---\n{number(c) if numbered else c}" for p, c in sorted(files.items()))


def generator_input_tokens(project: pathlib.Path) -> tuple[int, int]:
    """(largest single generator prompt, total generator input) from the run's
    own usage ledger — provider-reported, not estimated."""
    path = project / ".crossaudit" / "usage.jsonl"
    biggest = total = 0
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("role") == "generator":
                n = int(row.get("input") or 0)
                biggest, total = max(biggest, n), total + n
    return biggest, total


def token_cost(project: pathlib.Path, instance: str) -> dict:
    files = scope_files(project)
    # The set the generator MAY CITE is the scope minus its own deliverable: at
    # round 1 the draft does not exist yet, and contract A numbers sources.
    sources = {p: c for p, c in files.items() if p != DRAFT_PATH}
    plain, marked = render(sources, False), render(sources, True)
    biggest, total = generator_input_tokens(project)
    return {
        "instance": instance,
        "source_files": len(sources),
        "source_lines": sum(c.count("\n") + 1 for c in sources.values()),
        "plain_tokens": tokens(plain),
        "numbered_tokens": tokens(marked),
        "delta_tokens": tokens(marked) - tokens(plain),
        "reported_generator_input_max": biggest,
        "reported_generator_input_total": total,
    }


# ----------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("archive", type=pathlib.Path,
                    help="the read-only Arm 2 archive root (…/wt-arm2-runs/arm2)")
    ap.add_argument("--json", type=pathlib.Path, default=None,
                    help="also write the per-instance records here")
    args = ap.parse_args(argv)

    records, costs = [], []
    for inst in instances(args.archive):
        name = re.sub(r"^T03MaterialSEG-", "", inst.name).replace("__", "/")
        project = inst / "project"
        records.append(analyse_instance(project, name))
        costs.append(token_cost(project, name))

    span = sum(r["span_rows"] for r in records)
    rows = sum(r["rows"] for r in records)

    def pct(n: int, d: int) -> str:
        return f"{n}/{d} = {100.0 * n / d:.1f}%" if d else f"{n}/0"

    print(f"drafts                                    {len(records)}")
    print(f"annotation rows                           {rows}")
    print(f"  uncited / governed                      {sum(r['uncited'] for r in records)}")
    print(f"  locator did not resolve                 "
          f"{sum(r['unresolved_locator'] for r in records)}")
    print(f"  `at` outside its own draft              "
          f"{sum(r['at_past_end'] for r in records)}")
    print(f"span rows (the denominator)               {span}")
    print()
    print("CONTRACT B — content addressing")
    print(f"  named file contains the pair            "
          f"{pct(sum(r['b_file_contains'] for r in records), span)}")
    print(f"  …on exactly ONE line  (B's ceiling)     "
          f"{pct(sum(r['b_unique_line'] for r in records), span)}")
    print(f"  …and a unique <={QUOTE_MAX}-char quote exists  "
          f"{pct(sum(r['b_unique_quote'] for r in records), span)}")
    print(f"  pair on >1 line (B must call ambiguous)  "
          f"{pct(sum(r['b_ambiguous'] for r in records), span)}")
    print(f"  pair nowhere in the named file           "
          f"{pct(sum(r['b_absent'] for r in records), span)}")
    print()
    print("CONTRACT A — numbered rendering")
    print(f"  named line already lands (as shipped)   "
          f"{pct(sum(r['a_named_line_lands'] for r in records), span)}")
    print(f"  lands after the draft's MODAL offset    "
          f"{pct(sum(r['a_modal_lands'] for r in records), span)}")
    print(f"  lands after the BEST per-draft offset   "
          f"{pct(sum(r['a_best_lands'] for r in records), span)}")
    single = [r for r in records if r["single_offset_draft"]]
    measurable = [r for r in records if r["modal_offset"] is not None]
    print(f"  drafts with one constant offset         "
          f"{len(single)}/{len(measurable)} measurable")
    med = sorted(o for r in records for o in r["offsets"])
    if med:
        print(f"  median row offset                       "
              f"{med[len(med) // 2]:+d}")
    print()
    print("A vs B on the SAME rows (A = modal offset lands, B = unique line)")
    for key, label in (("both", "both would resolve"),
                       ("a_only", "only A (duplicate line, B ambiguous)"),
                       ("b_only", "only B (offset not a clean constant)"),
                       ("neither", "neither")):
        print(f"  {label:<39} {pct(sum(r[key] for r in records), span)}")
    print()
    print("TOKEN COST OF NUMBERING (product token path: ceil(chars/4))")
    plain = sum(c["plain_tokens"] for c in costs)
    marked = sum(c["numbered_tokens"] for c in costs)
    deltas = sorted(c["delta_tokens"] for c in costs)
    print(f"  source set, plain                       {plain} tokens "
          f"(mean {plain / len(costs):.0f}/instance)")
    print(f"  source set, numbered                    {marked} tokens "
          f"(mean {marked / len(costs):.0f}/instance)")
    print(f"  delta                                   +{marked - plain} tokens "
          f"= +{100.0 * (marked - plain) / plain:.1f}%")
    print(f"  per instance                            "
          f"min +{deltas[0]}, median +{deltas[len(deltas) // 2]}, max +{deltas[-1]}")
    src_lines = sum(c["source_lines"] for c in costs)
    src_chars = sum(c["plain_tokens"] for c in costs) * 4
    print(f"  the scaling law                         "
          f"+{len(GUTTER.format(1))} chars per rendered line; this corpus's source "
          f"lines average {src_chars / src_lines:.0f} chars, so the surcharge is "
          f"{100.0 * len(GUTTER.format(1)) * src_lines / src_chars:.0f}% of the "
          f"source bytes and scales as 7/L for a corpus of line length L")
    biggest = sum(c["reported_generator_input_max"] for c in costs)
    total_in = sum(c["reported_generator_input_total"] for c in costs)
    if biggest:
        print(f"  vs one generator prompt (reported)      "
              f"+{100.0 * (marked - plain) / biggest:.1f}% "
              f"({biggest} input tokens over {len(costs)} instances)")
    if total_in:
        print(f"  vs ALL generator input (reported)       "
              f"+{100.0 * (marked - plain) * (total_in / biggest) / total_in:.1f}% "
              f"per prompt; the run sent {total_in / biggest:.2f} prompts/instance, "
              f"so the surcharge is paid that many times")

    if args.json:
        args.json.write_text(json.dumps(
            {"rows": records, "cost": costs}, indent=1, sort_keys=True) + "\n",
            encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
