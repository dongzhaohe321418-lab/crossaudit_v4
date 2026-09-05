#!/usr/bin/env python3
"""Reconstruct the gold-standard labelling sheet from the Arm 3 archive.

`docs/design/CONTAINMENT_RULE.md` §3. The sheet is the ONLY thing a labeller
sees: an opaque item id, the located text, the transcribed value and the
transcribed unit. No matcher verdict, no arm, no instance, no mechanism class,
no disposition. It carries corpus text and is therefore written into the
archive, never into the repository (EXPERIMENT_RECORD §3).

Beside it this writes a KEY — ids and identities only, no corpus text — which is
committed, so every later count is reproducible from a checkout.

    python3 build_sheet.py --runs ~/Documents/Crossaudit/study-data/wt-arm3-runs/arm3 \
                           --out  ~/Documents/Crossaudit/study-data/gold-containment

Locating rule, per item kind:

* `block` / `pass` — the located text is exactly what the Arm 3 verifier read
  (`provenance_arm3.located_text`): for arm A the named line, for arm B the
  whitespace-folded quote. The gold therefore judges the same bytes the matcher
  judged, which is what makes an extension simulation over it meaningful.
* `panel` — a wrong-location draw. The row's `(v, u)` is re-pointed at a
  DIFFERENT line of the same file, drawn at the committed seed from the lines of
  that file that contain at least one digit and are not the row's own line.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent.parent / "src"))

from crossaudit.dcl import numbers as num_mod            # noqa: E402

OUTPUT_PATH = "work/synthesis/explanation.md"
#: The seed for the 150-pass sample and every panel draw. Committed in
#: PREREGISTRATION-GOLD.md before any item was looked at.
SEED = 20260906
N_PASS_SAMPLE = 150
N_PANEL_DRAFTS = 5
#: Wrong-location draws per row of a panel draft (CONTAINMENT_RULE.md §3.2).
N_PANEL_DRAWS = 5

_SPAN = num_mod._SPAN


def flat(text: str) -> str:
    return " ".join(str(text or "").split())


def git(project: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(project), capture_output=True,
                          text=True, check=True).stdout


def tree_files(project: Path, sha: str) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for rel in git(project, "ls-tree", "-r", "--name-only", sha).split("\n"):
        if rel.strip():
            out[rel] = subprocess.run(["git", "show", f"{sha}:{rel}"],
                                      cwd=str(project), capture_output=True,
                                      check=True).stdout
    return out


def audited_increment(project: Path, sha: str, cfg) -> dict[str, bytes]:
    own = {cfg.constitution, "crossaudit.yml", ".gitignore"}
    prefix_own = (cfg.ledger_dir.rstrip("/") + "/", cfg.state_dir.rstrip("/") + "/",
                  ".github/", "skills/")
    changed = git(project, "show", "--pretty=", "--name-only", sha).split("\n")
    picked = [f for f in changed if f.strip() and f not in own
              and not f.startswith(prefix_own)]
    if cfg.scope_dirs:
        picked = [f for f in picked if f.split("/", 1)[0] in cfg.scope_dirs]
    tree = tree_files(project, sha)
    dirs = {str(Path(f).parent) for f in picked} - {".", ""}
    widened = {f for f in tree if str(Path(f).parent) in dirs
               and f not in own and not f.startswith(prefix_own)}
    return {f: tree[f] for f in sorted(widened | set(picked)) if f in tree}


def fence_rows(text: str) -> list[dict]:
    rows: list[dict] = []
    for body in num_mod._FENCE.findall(text):
        try:
            parsed = json.loads(body, parse_float=str, parse_int=str)
        except ValueError:
            continue
        if isinstance(parsed, list):
            rows.extend(r for r in parsed if isinstance(r, dict))
    return rows


def resolve_key(files, annotated: str, named: str) -> str | None:
    if named in files:
        return named
    base = annotated.rsplit("/", 1)[0] if "/" in annotated else ""
    if base and f"{base}/{named}" in files:
        return f"{base}/{named}"
    return None


def decode(files, key):
    try:
        return files[key].decode("utf-8")
    except (KeyError, UnicodeDecodeError):
        return None


def located(arm: str, files, row: dict):
    """`(key, text, line_no|None)`, or None. `provenance_arm3.located_text`'s
    rule; the third element is the 1-based line for arm A, None for arm B."""
    src = row.get("src")
    if arm == "A":
        if not isinstance(src, str) or src == "uncited" or src.startswith("governed:"):
            return None
        locator = src[len("computed:"):] if src.startswith("computed:") else src
        m = _SPAN.fullmatch(locator)
        if m is None:
            return None
        key = resolve_key(files, OUTPUT_PATH, m.group("path"))
        if key is None:
            return None
        body = decode(files, key)
        if body is None:
            return None
        lines = body.split("\n")
        start, end = int(m.group("start")), int(m.group("end") or m.group("start"))
        if start < 1 or end < start or end > len(lines):
            return None
        return key, "\n".join(lines[start - 1:end]), start
    if not isinstance(src, dict):
        return None
    named, quote = src.get("file"), src.get("quote")
    if not isinstance(named, str) or not isinstance(quote, str):
        return None
    key = resolve_key(files, OUTPUT_PATH, named)
    if key is None:
        return None
    body = decode(files, key)
    if body is None:
        return None
    needle = flat(quote)
    if not needle or flat(body).count(needle) != 1:
        return None
    return key, needle, None


def main(argv=None) -> int:
    from crossaudit.config import load as load_cfg

    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)

    items: list[dict] = []          # {kind, instance, arm, row, text, v, u, ...}
    per_draft: dict[tuple[str, str], list[int]] = {}
    file_bodies: dict[tuple[str, str], str] = {}

    for proj_dir in sorted((args.runs / "instances").iterdir()):
        project = proj_dir / "project"
        if not (project / "crossaudit.yml").exists():
            continue
        stem, arm = proj_dir.name.rsplit("__", 1)
        instance = stem.split("-", 1)[1].replace("__", "/")
        cfg = load_cfg(project / "crossaudit.yml")
        sha = git(project, "log", "-1", "--format=%H", "--", OUTPUT_PATH).strip()
        if not sha:
            continue
        files = audited_increment(project, sha, cfg)
        draft = files.get(OUTPUT_PATH, b"").decode("utf-8", "replace")
        for row_no, ann in enumerate(fence_rows(draft)):
            loc = located(arm, files, ann)
            if loc is None:
                continue
            key, text, line_no = loc
            v, u = str(ann.get("v", "")), str(ann.get("u", ""))
            if num_mod.normalise_number(v) is None:
                continue
            verdict = num_mod.contains_pair(text, v, u)
            # Arm 3's own severity: the 80-character cap raised a BLOCKER on two
            # rows whose located text DOES contain the pair (RESULTS-ARM3 §1).
            # D159 ruling 1 removes the cap; they stay in the block corpus
            # because the task freezes "all 53 Arm 3 blocks", and they are the
            # two rows on which the matcher and the arm disagree by construction.
            capped = (arm == "B" and isinstance(ann.get("src"), dict)
                      and isinstance(ann["src"].get("quote"), str)
                      and len(ann["src"]["quote"]) > 80)
            items.append({"kind": "block" if (not verdict or capped) else "pass",
                          "cap": capped,
                          "instance": instance, "arm": arm, "row": row_no,
                          "text": text, "v": v, "u": u,
                          "file": key, "line": line_no, "matcher": verdict})
            per_draft.setdefault((instance, arm), []).append(len(items) - 1)
            body = decode(files, key)
            if body is not None:
                file_bodies[(instance, arm, key)] = body

    rng = random.Random(SEED)
    blocks = [i for i, it in enumerate(items) if it["kind"] == "block"]
    passes = [i for i, it in enumerate(items) if it["kind"] == "pass"]
    sampled = sorted(rng.sample(passes, N_PASS_SAMPLE))

    # --- the wrong-location negative panel -------------------------------
    drafts = sorted(per_draft)
    panel_drafts = sorted(rng.sample(drafts, N_PANEL_DRAFTS))
    panel: list[dict] = []
    for draft_key in panel_drafts:
        for idx in per_draft[draft_key]:
            it = items[idx]
            body = file_bodies.get((it["instance"], it["arm"], it["file"]))
            if body is None:
                continue
            lines = body.split("\n")
            own = it["line"]
            if own is None:            # arm B: the line the quote was copied from
                own = next((n for n, ln in enumerate(lines, 1)
                            if it["text"] in flat(ln)), None)
            cand = [n for n, ln in enumerate(lines, 1)
                    if re.search(r"[0-9]", ln) and n != own]
            if not cand:
                continue
            for pick in sorted(rng.sample(cand, min(N_PANEL_DRAWS, len(cand)))):
                text = lines[pick - 1]
                panel.append({"kind": "panel", "instance": it["instance"],
                              "arm": it["arm"], "row": it["row"], "text": text,
                              "v": it["v"], "u": it["u"], "file": it["file"],
                              "line": pick, "from_line": own, "cap": False,
                              "matcher": num_mod.contains_pair(text, it["v"], it["u"])})

    chosen = [items[i] for i in blocks] + [items[i] for i in sampled] + panel
    order = list(range(len(chosen)))
    rng.shuffle(order)

    sheet, key_rows = [], []
    for pos, src_i in enumerate(order):
        it = chosen[src_i]
        item_id = f"G{pos + 1:04d}"
        sheet.append({"id": item_id, "line": it["text"], "v": it["v"], "u": it["u"]})
        key_rows.append({"id": item_id, "kind": it["kind"], "instance": it["instance"],
                         "arm": it["arm"], "row": it["row"], "file": it["file"],
                         "line": it["line"], "from_line": it.get("from_line"),
                         "matcher": it["matcher"], "cap": it.get("cap", False),
                         "text_sha256": hashlib.sha256(
                             it["text"].encode("utf-8")).hexdigest(),
                         "v_sha256": hashlib.sha256(it["v"].encode("utf-8")).hexdigest(),
                         "u_sha256": hashlib.sha256(it["u"].encode("utf-8")).hexdigest()})

    (args.out / "sheet.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in sheet), encoding="utf-8")
    (HERE / "key.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in key_rows), encoding="utf-8")
    # A human-readable sheet for the labellers, same content, archive only.
    with (args.out / "sheet.txt").open("w", encoding="utf-8") as fh:
        for r in sheet:
            fh.write(f"{r['id']}\nv: {r['v']}\nu: {r['u']}\nline: {r['line']}\n\n")
    print(f"items {len(sheet)}  blocks {len(blocks)}  passes sampled {len(sampled)} "
          f"of {len(passes)}  panel {len(panel)} from {len(panel_drafts)} drafts")
    print(f"sheet -> {args.out/'sheet.jsonl'}   key -> {HERE/'key.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
