"""Arm 2 of `docs/design/PROVENANCE_CHECKS.md` §6, under the §8g rule.

Arm 1 (`provenance_arm1.py`) ran the SHIPPED check over annotations a PROBE
derived, and reached its limit: every block it found was the probe's own
extraction error, so the corpus cannot separate the verifier's false-blocker
rate from the instrument's (D157). Here the GENERATOR writes the annotations,
under the shipped house skill, reached through the shipped channel — a real
scaffolded science project whose `skills/provenance-numbers.md` is
`scaffold.annotation_skill_tree` verbatim and whose `checks:` is `science`.

Nothing here is prompt-engineered and nothing under `src/` is modified. The
skill is what ships; if it or the check has a defect, that is the finding.

What one instance does:

1. bootstrap the same scratch project `run.py` builds for arm B (same task
   prompt, same RECIPE/deliverable layout), plus the shipped annotation skill
   and `checks: science`;
2. run the product's real loop for ONE round (`max_rounds: 1`), so what is
   measured is the generator's first-pass annotation behaviour and not its
   repair of the check's own blocks;
3. reconstruct the audited increment from the committed tree the way `cmd_run`
   does, run `check_number_source` over it, and CONFIRM the finding set equals
   the one the loop's own `cycles/*/checks.json` recorded — the reconstruction
   is used for per-row attribution, and the loop's ledger is what proves it is
   the shipped disposition;
4. adjudicate every row twice (`study7/PREREGISTRATION.md` §6) and classify
   every block (§10).

The corpus is CC BY-NC-SA 4.0 and is neither redistributed nor committed: run
directories are gitignored, and the committed row records carry sha256 of the
transcribed value and unit, never the text.

Usage::

    export PYTHONPATH=<worktree>/src
    set -a && . ~/.crossaudit-keys.env && set +a
    python3 benchmarks/expertlongbench/provenance_arm2.py --batch 1
    python3 benchmarks/expertlongbench/provenance_arm2.py --batch 2 --out <same-dir>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "src"))

import run as run_mod                                              # noqa: E402
from provenance_probe import NUM                                   # noqa: E402
from run import (INCREMENT_DIR, OUTPUT_PATH, RECIPE_PATH,          # noqa: E402
                 Options, SCOPE_DIR, choose_samples, load_task_rows,
                 load_credentials, verify_corpus)

from crossaudit.dcl import numbers as num_mod                      # noqa: E402
from crossaudit.dcl.framework import ADVISORY, BLOCKER             # noqa: E402
from crossaudit.scaffold import annotation_skill_tree              # noqa: E402

#: Everything held fixed, in one place, so the report can quote it.
GENERATOR = "anthropic:claude-sonnet-4-6"
AUDITOR = "openai:gpt-5.6-terra"
CHECKS = "science"
SEED = 20261104
BATCH1_N = 16
BATCH2_N = 8
BUDGET_USD = 4.00


# ---------------------------------------------------------------- the project

#: arm B's own bootstrap, captured before the patch in `run_instance` so the
#: wrapper below cannot recurse into itself.
_BOOTSTRAP = run_mod.bootstrap_project


def bootstrap_with_skill(scratch: Path, task, row: dict, options: Options) -> Path:
    """`run.py`'s arm-B project, plus the shipped annotation skill.

    The skill arrives by the shipped channel and no other: a committed
    `skills/*.md` written verbatim by `scaffold.annotation_skill_tree`, selected
    by `skills.select` against the project's live `checks:` (its front matter
    says `requires_check: number_source`), rendered into the generator prompt by
    `skills.render`, hashed into the receipt, never shown to the auditor. The
    harness writes the file; it does not write its contents.
    """
    project = _BOOTSTRAP(scratch, task, row, options)
    from crossaudit.dcl.profiles import resolve as resolve_checks

    tree = annotation_skill_tree(resolve_checks(options.checks))
    if not tree:
        raise SystemExit(f"checks={options.checks!r} pulls in no annotation skill; "
                         "the study would measure a generator that was never asked "
                         "to annotate")
    for rel, text in tree.items():
        dest = project / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8", newline="\n")
    subprocess.run(["git", "add", "-A"], cwd=str(project), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "house skills"],
                   cwd=str(project), check=True)
    return project


# -------------------------------------------------- the increment, as cmd_run sees it

def _tree_files(project: Path, sha: str) -> dict[str, bytes]:
    listing = subprocess.run(["git", "ls-tree", "-r", "--name-only", sha],
                             cwd=str(project), capture_output=True, text=True,
                             check=True).stdout.split("\n")
    out: dict[str, bytes] = {}
    for rel in listing:
        if not rel.strip():
            continue
        blob = subprocess.run(["git", "show", f"{sha}:{rel}"], cwd=str(project),
                              capture_output=True, check=True)
        out[rel] = blob.stdout
    return out


def audited_increment(project: Path, sha: str, cfg) -> dict[str, bytes]:
    """The files the DCL was handed, rebuilt from the tree.

    `cmd_run` builds the increment from the commit's CHANGED paths, drops its
    own artefacts (`skills/`, the ledger, the state dir, `.github/`, the
    Constitution, `crossaudit.yml`, `.gitignore`), keeps only paths under
    `scope.dirs`, and then ENCLOSES: every file in the touched directories, from
    the tree, because an increment is a directory. Reimplemented here rather
    than imported because both steps are closures inside `cmd_run` — and
    verified rather than trusted: `run_instance` asserts the `number_source`
    findings over this mapping equal the ones the loop's own ledger recorded.
    """
    own = {cfg.constitution, "crossaudit.yml", ".gitignore"}
    prefix_own = (cfg.ledger_dir.rstrip("/") + "/", cfg.state_dir.rstrip("/") + "/",
                  ".github/", "skills/")
    changed = subprocess.run(
        ["git", "show", "--pretty=", "--name-only", sha], cwd=str(project),
        capture_output=True, text=True, check=True).stdout.split("\n")
    picked = [f for f in changed if f.strip() and f not in own
              and not f.startswith(prefix_own)]
    if cfg.scope_dirs:
        picked = [f for f in picked if f.split("/", 1)[0] in cfg.scope_dirs]
    tree = _tree_files(project, sha)
    dirs = {str(Path(f).parent) for f in picked} - {".", ""}
    widened = {f for f in tree if str(Path(f).parent) in dirs
               and f not in own and not f.startswith(prefix_own)}
    keep = sorted(widened | set(picked))
    return {f: tree[f] for f in keep if f in tree}


def science_commit(project: Path) -> str:
    """The commit the audit read: the newest one that touched the deliverable."""
    log = subprocess.run(["git", "log", "-1", "--format=%H", "--", OUTPUT_PATH],
                         cwd=str(project), capture_output=True, text=True,
                         check=True).stdout.strip()
    return log


def ledger_number_findings(project: Path, cfg) -> list[dict] | None:
    """What the loop's own DCL recorded for `number_source`, or None if no cycle
    directory carries a `checks.json` (the audit never ran)."""
    ledger = project / cfg.ledger_dir
    if not ledger.is_dir():
        return None
    found: list[dict] | None = None
    for cycle in sorted(ledger.iterdir()):
        path = cycle / "checks.json"
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        found = [f for f in data.get("findings", [])
                 if f.get("check") == "number_source"
                 or str(f.get("rule", "")).startswith("CA-NUM")
                 or f.get("implementation_code", "").startswith("CA-NUM")]
    return found


# ------------------------------------------------------------------ the rows

def fence_rows(text: str) -> list[dict]:
    """Every annotation row, read exactly as the shipped check reads them."""
    rows: list[dict] = []
    for body in num_mod._FENCE.findall(text):
        try:
            parsed = json.loads(body, parse_float=str, parse_int=str)
        except ValueError:
            continue
        if isinstance(parsed, list):
            rows.extend(r for r in parsed if isinstance(r, dict))
    return rows


def strip_fences(text: str) -> str:
    return num_mod._FENCE.sub("", text)


def sha(value: str) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def resolve_span(files: dict[str, bytes], annotated: str, src: str):
    """The span a locator names, re-read from the committed tree.

    Returns `(key, start, end, span_text)` or None. Deliberately its own
    resolution rather than the check's, so an adjudication is not the check
    agreeing with itself about which bytes to look at.
    """
    if not isinstance(src, str) or src == "uncited" or src.startswith("governed:"):
        return None
    locator = src[len("computed:"):] if src.startswith("computed:") else src
    m = num_mod._SPAN.fullmatch(locator)
    if not m:
        return None
    named, start = m.group("path"), int(m.group("start"))
    end = int(m.group("end") or start)
    key = named if named in files else None
    if key is None and "/" in annotated:
        joined = f"{annotated.rsplit('/', 1)[0]}/{named}"
        key = joined if joined in files else None
    if key is None:
        return None
    try:
        body = files[key].decode("utf-8")
    except UnicodeDecodeError:
        return None
    lines = body.split("\n")
    if start < 1 or end < start or end > len(lines):
        return None
    return key, start, end, "\n".join(lines[start - 1:end])


def adjudicator_b(span: str, v: str, u: str) -> bool:
    """Independent of everything in `src/`: exact substring, no normalisation.

    Not a better test — a DIFFERENT one, so the primary's denominator is not
    defined solely by the code whose blocking behaviour is being measured.
    """
    if str(v) not in span:
        return False
    return not str(u) or str(u) in span


_HYPHEN_WORD = re.compile(r"\A(?P<unit>[^\s\-–—]+)-(?P<word>[A-Za-z])")


def classify_block(files: dict[str, bytes], draft_path: str, row: dict,
                   adj_a: bool | None, resolved, rule: str = "") -> str:
    """§10 of the preregistration, in order; first match wins.

    §10.1 says in its own parenthesis what its class IS: "exactly CA-NUM-001
    before any span is read" — a malformed row, an `at` outside the artefact, a
    locator that is not a span, a path outside the increment, a pinned sha that
    does not match, a range past the end of the file. Every one of those is
    CA-NUM-001 and none of them is a statement about what the span holds, so
    the rule reads on the finding's own code. Classes 2–6 are the CA-NUM-002
    question — "the span does not hold this pair" — and only that.
    """
    if rule == "CA-NUM-001" or resolved is None:
        return "generator wrong locator (unresolved)"
    if adj_a:
        return "verifier false blocker"
    key, _start, _end, span = resolved
    v, u = str(row.get("v", "")), str(row.get("u", ""))
    wanted_value = num_mod.normalise_number(v)
    wanted_unit = num_mod.normalise_unit(u)

    # 3 — a hyphenated English word directly after the unit (D157's open dial).
    if wanted_value is not None and wanted_unit:
        for m in num_mod._NUMBER.finditer(span):
            if num_mod.normalise_number(m.group(1)) != wanted_value:
                continue
            token, _after = num_mod.unit_token(span[m.end():])
            hy = _HYPHEN_WORD.match(token)
            if hy and num_mod.normalise_unit(hy.group("unit")) == wanted_unit:
                return "hyphenated-word case"

    # 4 — notation the layer does not parse, or a unit with a space in it.
    if " " in " ".join(u.split()) and u.strip():
        return "unparsed notation"
    if wanted_value is None:
        return "unparsed notation"
    for m in num_mod._NUMBER.finditer(span):
        if num_mod.normalise_number(m.group(1)) == wanted_value and \
                num_mod._UNPARSED.match(span[m.end():]):
            return "unparsed notation"

    # 5 — the pair is elsewhere in the named file.
    try:
        body = files[key].decode("utf-8")
    except (KeyError, UnicodeDecodeError):
        body = ""
    if num_mod.contains_pair(body, v, u):
        return "generator wrong locator (wrong line)"

    # 6 — residual.
    return "generator wrong transcription"


def unit_shortened(span: str, v: str, u: str) -> bool:
    """Did the generator transcribe a unit that is a strict PREFIX of the whole
    unit token at an occurrence of its value? Arm 1's failure, generator-side."""
    wanted_value = num_mod.normalise_number(v)
    folded = num_mod.normalise_unit(u)
    if wanted_value is None or not folded:
        return False
    for m in num_mod._NUMBER.finditer(span):
        if num_mod.normalise_number(m.group(1)) != wanted_value:
            continue
        token, _ = num_mod.unit_token(span[m.end():])
        token = num_mod.normalise_unit(token)
        if token != folded and token.startswith(folded):
            return True
    return False


# ------------------------------------------------------------- one instance

def usage_split(project: Path, cfg, run_id: str) -> dict:
    from crossaudit import usage

    events, _bad = usage.read_events(cfg.root / cfg.state_dir / usage.LEDGER_NAME)
    mine = [e for e in events if e.get("run_id") == run_id] or events
    def total(pred):
        rows = [e for e in mine if pred(e)]
        return {
            "calls": len(rows),
            "input": sum(int(e.get("input", 0)) for e in rows),
            "output": sum(int(e.get("output", 0)) for e in rows),
            "cost_usd": sum(float(e.get("api_value_usd") or 0.0) for e in rows),
        }
    gen_vendor = GENERATOR.split(":", 1)[0]
    aud_vendor = AUDITOR.split(":", 1)[0]
    return {
        "all": total(lambda e: True),
        "generator": total(lambda e: e.get("vendor") == gen_vendor),
        "auditor": total(lambda e: e.get("vendor") == aud_vendor),
    }


def analyse_project(project: Path, instance: str) -> dict:
    """Everything measured about one instance, from its KEPT project tree.

    Split from the loop so that a correction to the adjudication or to the §10
    classifier is recomputed over the runs already on disk and never re-bills a
    model call — and so that the run step is data collection and nothing else.
    """
    from crossaudit.config import load as load_cfg

    cfg = load_cfg(project / "crossaudit.yml")
    record: dict = {"instance": instance, "rows": []}
    sha_science = science_commit(project)
    record["science_sha"] = sha_science
    if not sha_science:
        record["analysis_error"] = "the loop committed no deliverable"
        return record

    files = audited_increment(project, sha_science, cfg)
    record["increment_files"] = sorted(files)
    draft = files.get(OUTPUT_PATH, b"").decode("utf-8", "replace")
    record["output_sha256"] = sha(draft)
    record["draft_chars"] = len(draft)
    record["draft_lines"] = draft.count("\n") + 1
    record["numbers_present"] = len(NUM.findall(strip_fences(draft)))
    record["fence_blocks"] = len(num_mod._FENCE.findall(draft))

    # The shipped check, over the reconstructed increment...
    findings = num_mod.check_number_source(files)
    record["check_findings"] = [
        {"rule": f.rule, "severity": f.severity, "artifact": f.artifact,
         "observation": f.observation} for f in findings]
    # ...and the loop's own ledger, which is what proves it is the shipped
    # disposition rather than a harness re-enactment of it.
    ledger = ledger_number_findings(project, cfg)
    record["ledger_finding_count"] = None if ledger is None else len(ledger)
    if ledger is not None:
        mine = sorted((f.rule, f.artifact, f.observation) for f in findings)
        theirs = sorted((f.get("implementation_code") or f.get("rule"),
                         f.get("artifact"), f.get("observation"))
                        for f in ledger)
        record["ledger_agrees"] = mine == theirs
    else:
        record["ledger_agrees"] = None

    lines = draft.count("\n") + 1
    for row_no, ann in enumerate(fence_rows(draft)):
        per = num_mod._row_findings(OUTPUT_PATH, files, ann, lines)
        blocked = [f for f in per if f.severity == BLOCKER]
        advisory = [f for f in per if f.severity == ADVISORY]
        src = str(ann.get("src", ""))
        resolved = resolve_span(files, OUTPUT_PATH, src)
        v, u = str(ann.get("v", "")), str(ann.get("u", ""))
        adj_a = adj_b = None
        if resolved is not None:
            adj_a = num_mod.contains_pair(resolved[3], v, u)
            adj_b = adjudicator_b(resolved[3], v, u)
        record["rows"].append({
            "instance": instance,
            "row": row_no,
            "at": str(ann.get("at", "")),
            "src": src,
            "v_sha256": sha(v), "u_sha256": sha(u),
            "v_len": len(v), "u_len": len(u),
            "disposition": (blocked[0].rule if blocked
                            else advisory[0].rule if advisory else "pass"),
            "severity": (BLOCKER if blocked else ADVISORY if advisory else "PASS"),
            "observation": blocked[0].observation if blocked else (
                advisory[0].observation if advisory else ""),
            "locator_kind": ("uncited" if src == "uncited"
                             else "governed" if src.startswith("governed:")
                             else "computed" if src.startswith("computed:")
                             else "span"),
            "resolved": resolved is not None,
            "adj_a": adj_a,
            "adj_b": adj_b,
            "unit_shortened": (unit_shortened(resolved[3], v, u)
                               if resolved is not None else None),
            "class": (classify_block(files, OUTPUT_PATH, ann, adj_a, resolved,
                                     blocked[0].rule) if blocked else ""),
            # WHY the row blocked, split from WHAT the check says about the
            # span: `at` is the address in the artefact the generator was
            # writing, `src` the address of the evidence. A row can name its
            # evidence correctly and still block because it miscounted its own
            # output's lines, and a report that could not tell those apart
            # would have nothing to say about either.
            "at_valid": num_mod._at_span(ann.get("at"), lines) is not None,
        })
    return record


def reanalyse(out_dir: Path, batch: int) -> int:
    """Recompute every record's measured half from the kept project trees."""
    path = out_dir / f"records-b{batch}.jsonl"
    kept = [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rewritten = []
    for old in kept:
        project = (out_dir / "instances" /
                   old["instance"].replace("/", "__") / "project")
        fresh = analyse_project(project, old["instance"])
        merged = {k: v for k, v in old.items() if k in (
            "instance", "ok", "error", "exit_code", "rounds", "wall_s",
            "prompt_sha256", "started_utc", "usage")}
        merged.update(fresh)
        rewritten.append(merged)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n"
                            for r in rewritten), encoding="utf-8")
    print(f"reanalysed {len(rewritten)} record(s) in {path}")
    return 0


def run_instance(out_dir: Path, task, row: dict, options: Options,
                 run_id: str) -> dict:
    # The loop entry is `run.py`'s, unchanged; only the project it starts from
    # gains the shipped skill. Patched here rather than by editing `run.py`,
    # so arm B's own committed harness keeps its behaviour byte for byte.
    run_mod.bootstrap_project, original = bootstrap_with_skill, run_mod.bootstrap_project
    try:
        return _run_instance(out_dir, task, row, options, run_id)
    finally:
        run_mod.bootstrap_project = original


def _run_instance(out_dir: Path, task, row: dict, options: Options,
                  run_id: str) -> dict:
    safe = row["id"].replace("/", "__")
    scratch = out_dir / "instances" / safe
    scratch.mkdir(parents=True, exist_ok=True)
    started = time.time()
    result = run_mod.run_arm_b(scratch, task, row, options, run_id)
    project = scratch / "project"

    record: dict = {
        "instance": row["id"],
        "ok": result.ok,
        "error": result.error,
        "exit_code": result.exit_code,
        "rounds": result.rounds,
        "wall_s": round(result.wall_s, 2),
        "prompt_sha256": result.prompt_sha256,
        "started_utc": datetime.fromtimestamp(started, timezone.utc).isoformat(),
    }
    from crossaudit.config import load as load_cfg

    cfg = load_cfg(project / "crossaudit.yml")
    record["usage"] = usage_split(project, cfg, run_id)
    record.update(analyse_project(project, row["id"]))
    return record


# ------------------------------------------------------------------ the study

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batch", type=int, default=1, choices=[1, 2])
    ap.add_argument("--out", default="", help="run directory (absolute)")
    ap.add_argument("--task", default="T03MaterialSEG")
    ap.add_argument("--only", default="", help="comma-separated instance ids (a retry)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--reanalyse", action="store_true",
                    help="recompute the measured half of every record already in "
                         "--out from its kept project tree. No model call, no "
                         "spend: an adjudication or classification correction is "
                         "replayed over the runs on disk, never re-billed.")
    args = ap.parse_args(argv)
    if args.reanalyse:
        if not args.out:
            raise SystemExit("--reanalyse needs --out")
        return reanalyse(Path(args.out), args.batch)

    load_credentials()
    from tasks import get_task

    task = get_task(args.task)
    corpus_sha = verify_corpus(args.task)
    rows = load_task_rows(args.task)
    batch1 = choose_samples(rows, BATCH1_N, SEED)
    ids1 = [r["id"] for r in batch1]
    if args.batch == 1:
        chosen = batch1
    else:
        rest = [r for r in rows if r["id"] not in set(ids1)]
        chosen = choose_samples(rest, BATCH2_N, SEED)
    if args.only:
        wanted = set(args.only.split(","))
        chosen = [r for r in chosen if r["id"] in wanted]

    out_dir = Path(args.out) if args.out else (
        run_mod.RUNS_DIR / f"arm2-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    if not out_dir.is_absolute():
        raise SystemExit("--out must be absolute: the loop chdirs into each project")
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"arm2-b{args.batch}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"

    options = Options(
        task_id=args.task, n=len(chosen), seed=SEED, generator=GENERATOR,
        auditor=AUDITOR, judge=AUDITOR, mapper=AUDITOR, adjudicator=AUDITOR,
        max_rounds=1, checks=CHECKS, lone_model_blocker="block",
        na_policy="literal", arms="B", out=str(out_dir),
        audit_rules="general", subset=0, label=f"arm2-b{args.batch}")

    plan = {
        "run_id": run_id, "batch": args.batch, "task": args.task,
        "corpus_sha256": corpus_sha, "seed": SEED,
        "instance_ids": [r["id"] for r in chosen],
        "models": {"generator": GENERATOR, "auditor": AUDITOR},
        "settings": {"max_rounds": 1, "checks": CHECKS,
                     "audit_rules": "general", "scope": SCOPE_DIR,
                     "increment_dir": INCREMENT_DIR, "output": OUTPUT_PATH,
                     "recipe": RECIPE_PATH},
        "skill": {rel: hashlib.sha256(text.encode()).hexdigest()
                  for rel, text in annotation_skill_tree(
                      __import__("crossaudit.dcl.profiles",
                                 fromlist=["resolve"]).resolve(CHECKS)).items()},
        "code_sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(HERE),
                                   capture_output=True, text=True).stdout.strip(),
        "git_status": subprocess.run(["git", "status", "--porcelain"], cwd=str(HERE),
                                     capture_output=True, text=True).stdout,
        "python": sys.version.split()[0], "platform": sys.platform,
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / f"plan-b{args.batch}.json").write_text(
        json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in plan.items() if k != "git_status"}, indent=2))
    if args.dry_run:
        return 0

    # A run that appends: an id already recorded is skipped, so a retry names
    # only what failed (--only) and nothing already measured is re-billed.
    records_path = out_dir / f"records-b{args.batch}.jsonl"
    done = set()
    if records_path.exists() and not args.only:
        done = {json.loads(l)["instance"] for l in
                records_path.read_text(encoding="utf-8").splitlines() if l.strip()}
    spend = 0.0
    for index, row in enumerate(chosen, start=1):
        if row["id"] in done:
            print(f"[{index}/{len(chosen)}] {row['id']} — already recorded")
            continue
        print(f"[{index}/{len(chosen)}] {row['id']} …", flush=True)
        record = run_instance(out_dir, task, row, options, run_id)
        with records_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        spend += float(record.get("usage", {}).get("all", {}).get("cost_usd", 0.0))
        blocks = sum(1 for r in record["rows"] if r["severity"] == BLOCKER)
        print(f"    ok={record['ok']} rows={len(record['rows'])} "
              f"blocks={blocks} numbers={record.get('numbers_present')} "
              f"ledger_agrees={record.get('ledger_agrees')} "
              f"cost=${record.get('usage', {}).get('all', {}).get('cost_usd', 0):.4f} "
              f"(batch so far ${spend:.3f})")
        if spend > BUDGET_USD:
            print("STOPPING: the preregistered budget is spent")
            break
    print(f"batch {args.batch} spend ${spend:.4f}; records at {records_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
