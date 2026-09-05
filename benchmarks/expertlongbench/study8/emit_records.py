#!/usr/bin/env python3
"""Turn the Arm 3 run directory into the committed record set.

`benchmarks/EXPERIMENT_RECORD.md` §3: one JSONL row per annotation row per arm
and one per draft, carrying every measured quantity — and **never corpus text**.
The transcribed value, unit and quoted span are corpus-derived and appear only as
sha256 digests and lengths; addresses (a path, a path plus a line number) carry no
corpus text and are recorded whole.

It also computes the hand-inspection **substratum** of every block. The
preregistered §10 class is computed by the harness and is what the report's
disposition table uses; the substratum is a second, deterministic reading of the
same block that says *what the source actually writes at the named place* —
reported beside the class, as data, exactly as Arm 2 reported its rule-as-written
counts beside its one hand correction.

    PYTHONPATH=<worktree>/src python3 \\
        benchmarks/expertlongbench/study8/emit_records.py <run-dir>
"""
from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent.parent / "src"))

from provenance_arm3 import (audited_increment, fence_rows,       # noqa: E402
                             located_text, science_commit)
from crossaudit.dcl import numbers as num                         # noqa: E402

OUT = "work/synthesis/explanation.md"
DASH = set("-–—")

#: The substratum vocabulary, fixed here rather than per block.
SUBSTRATA = ("over-80-char quote", "range-or-list", "formula-subscript",
             "unit-rendered-differently", "unit-word-not-symbol",
             "hyphen-compound", "unparsed-notation",
             "value-absent-from-location", "value-not-a-number",
             "no location", "other")


def substratum(text: str, v: str, u: str) -> str:
    """What the source writes where the annotation points, in one word.

    Deterministic and first-match-wins, over the located text only. It never
    changes a disposition or a preregistered class; it exists so "the pair is not
    at that place" can be read as the several different things it turned out to
    be.
    """
    wanted = num.normalise_number(v)
    if wanted is None:
        return "value-not-a-number"
    hits = [m for m in num._NUMBER.finditer(text)
            if num.normalise_number(m.group(1)) == wanted]
    if not hits:
        # The digits are there but the number scanner will not read them as a
        # number: a stoichiometric subscript glued to an element symbol
        # (`LiNi0.8Co0.2O2`), which `_NUMBER`'s `(?<![\w.])` correctly refuses.
        for m in re.finditer(re.escape(v.strip()), text):
            pre = text[:m.start()]
            if pre and (pre[-1].isalpha() or pre[-1].isdigit()):
                return "formula-subscript"
        return "value-absent-from-location"
    for m in hits:
        rest = text[m.end():]
        token, _ = num.unit_token(rest)
        head = token[:1]
        if re.match(r"\s*[-–—,]\s*[0-9]", rest) or (
                head and head in DASH and re.match(r"[-–—][0-9]", token)):
            return "range-or-list"          # `800–1050 °C`, `0, 20, 40, 80 wt.%`
        if head and head in DASH:
            return "hyphen-compound"        # `2.54-cm diameter` (D157's mirror)
        if num._UNPARSED.match(rest):
            return "unparsed-notation"      # `3 × 10⁻² mbar`
        if token and token.isalpha() and \
                num.normalise_unit(token) != num.normalise_unit(u):
            return "unit-word-not-symbol"   # `900 degrees` annotated `900 °C`
        if token and num.normalise_unit(token) != num.normalise_unit(u):
            return "unit-rendered-differently"   # `°C min⁻¹` vs `°C/min`
    return "other"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 2
    run = pathlib.Path(argv[0])
    from crossaudit.config import load as load_cfg

    records = [json.loads(line) for b in (1, 2)
               for line in (run / f"records-b{b}.jsonl").read_text(
                   encoding="utf-8").splitlines() if line.strip()]

    rows_out, drafts_out = [], []
    substrata = collections.Counter()
    for rec in records:
        safe = rec["instance"].replace("/", "__")
        project = run / "instances" / f"{safe}__{rec['arm']}" / "project"
        cfg = load_cfg(project / "crossaudit.yml")
        files = audited_increment(project, science_commit(project), cfg)
        draft = files.get(OUT, b"").decode("utf-8", "replace")
        anns = fence_rows(draft)
        for r in rec["rows"]:
            ann = anns[r["row"]]
            v, u = str(ann.get("v", "")), str(ann.get("u", ""))
            location = located_text(rec["arm"], files, OUT, ann)
            sub = ""
            if r["severity"] == "BLOCKER":
                sub = ("over-80-char quote" if r["class"] == "verifier wrong"
                       else substratum(location[1], v, u) if location
                       else "no location")
                substrata[(rec["arm"], sub)] += 1
            rows_out.append({**{k: r[k] for k in (
                "instance", "arm", "row", "src_kind", "src_addr", "quote_len",
                "quote_sha256", "v_sha256", "u_sha256", "v_len", "u_len",
                "severity", "disposition", "reason", "resolved_location",
                "occurrences", "location_file", "adj_a", "adj_b",
                "unit_shortened", "pair_in_named_file", "class",
                "class_detail")}, "substratum": sub})
        drafts_out.append({k: rec.get(k) for k in (
            "instance", "arm", "ok", "error", "exit_code", "rounds", "wall_s",
            "prompt_sha256", "started_utc", "science_sha", "output_sha256",
            "draft_chars", "draft_lines", "numbers_present", "fence_blocks",
            "shipped_check_blocks", "manifest_agrees", "increment_files",
            "outlined_paths", "gutter", "usage")})

    (HERE / "rows.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows_out),
        encoding="utf-8")
    (HERE / "drafts.jsonl").write_text(
        "".join(json.dumps(d, ensure_ascii=False) + "\n" for d in drafts_out),
        encoding="utf-8")

    plan = json.loads((run / "plan-b1.json").read_text(encoding="utf-8"))
    plan2 = json.loads((run / "plan-b2.json").read_text(encoding="utf-8"))
    manifest = {
        "study": "study8 / Arm 3",
        "preregistration": "benchmarks/expertlongbench/study8/PREREGISTRATION-ARM3.md",
        "code_sha": plan["code_sha"],
        "git_status_at_freeze": plan["git_status"],
        "corpus": {"name": "T03MaterialSEG.jsonl",
                   "sha256": plan["corpus_sha256"], "rows": 50,
                   "licence": "CC BY-NC-SA 4.0, not redistributed"},
        "seed": plan["seed"],
        "models": plan["models"],
        "settings": plan["settings"],
        "skills_sha256": plan["skills"],
        "contract_sha256": plan["contracts"],
        "instance_ids": plan["instance_ids"] + plan2["instance_ids"],
        "python": plan["python"], "platform": plan["platform"],
        "started_utc": {"batch1": plan["started_utc"],
                        "batch2": plan2["started_utc"]},
        "rows_recorded": len(rows_out), "drafts_recorded": len(drafts_out),
        "records_sha256": {
            "rows.jsonl": hashlib.sha256(
                (HERE / "rows.jsonl").read_bytes()).hexdigest(),
            "drafts.jsonl": hashlib.sha256(
                (HERE / "drafts.jsonl").read_bytes()).hexdigest()},
    }
    (HERE / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"{len(rows_out)} rows, {len(drafts_out)} drafts")
    for arm in ("A", "B"):
        print(f"arm {arm} block substrata:")
        for name in SUBSTRATA:
            n = substrata.get((arm, name), 0)
            if n:
                print(f"  {name:<30} {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
