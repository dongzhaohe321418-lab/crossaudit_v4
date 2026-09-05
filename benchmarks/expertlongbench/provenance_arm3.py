"""Arm 3 — the deciding experiment between the two provenance addressing contracts.

`docs/design/PROVENANCE_ADDRESSING.md` §5, under D158 ruling 3 and the §8g rule.
Preregistered at `benchmarks/expertlongbench/study8/PREREGISTRATION-ARM3.md`,
committed before any study model call.

Arm 2 (`RESULTS-ARM2.md`) killed the shipped contract: 0 of 215 generator-written
annotation rows passed, because the contract asked for two addresses the generator
is never shown. The design named two replacements and priced both on Arm 2's own
archive. This runs them, paired, on the same 24 T03 instances and the same seed:

  **A — numbered rendering.** Every citable file is rendered to the generator with
  a line gutter (width 5, right aligned, ``"| "``), numbered per file 1-based over
  ``split("\\n")`` exactly as ``numbers._span`` indexes. `src` stays ``path#L<n>``.
  `at` is dropped. A file the runtime replaced with a structural outline or a stub
  is NOT numbered and the skill calls it uncitable.

  **B — content addressing.** `src` becomes ``{"file": path, "quote": "<=80 chars
  copied exactly>"}``. Code finds the quote by exact bytes with runs of whitespace
  collapsed on both sides — the one normalisation `normalise_unit` already performs
  — requires uniqueness, and verifies the pair inside the quote. `at` is dropped.

**Nothing under `src/` is modified.** The harness implements both verifiers itself
and reuses `crossaudit.dcl.numbers.contains_pair` and its unit synonym table, so
the verification half is byte-identical to the shipped check and only the
addressing half differs between arms. Contract A's gutter and each arm's
deterministic-contract sentence reach the generator by monkeypatch at the harness
boundary, never by editing the product.

The corpus is CC BY-NC-SA 4.0 and is neither redistributed nor committed: run
directories are gitignored, and the committed row records carry sha256 of the
transcribed value, unit and quote — never the text.

Usage::

    export PYTHONPATH=<worktree>/src
    set -a && . ~/.crossaudit-keys.env && set +a
    python3 benchmarks/expertlongbench/provenance_arm3.py --batch 1 --out <abs>
    python3 benchmarks/expertlongbench/provenance_arm3.py --batch 2 --out <abs>
"""
from __future__ import annotations

import argparse
import hashlib
import json
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
                 CONFIG_TEMPLATE, Options, SCOPE_DIR, choose_samples,
                 constitution_text, git, load_task_rows,
                 load_credentials, verify_corpus)

from crossaudit import generator as gen_mod                        # noqa: E402
from crossaudit.dcl import numbers as num_mod                      # noqa: E402
from crossaudit.dcl.framework import ADVISORY, BLOCKER             # noqa: E402
from provider import role_for                                      # noqa: E402

#: Everything held fixed, in one place, so the report can quote it.
GENERATOR = "anthropic:claude-sonnet-4-6"
AUDITOR = "openai:gpt-5.6-terra"
#: An explicit one-check list, not the `science` profile: Arm 2's 48 incidental
#: CA-META-001 schema blockers are a science-profile artefact on a prose
#: deliverable and the design (§5) excludes them from this record. `number_source`
#: must still be selected, because the annotation skill's `requires_check:` front
#: matter is what gets it rendered into the generator prompt at all.
CHECKS_LIST = ["number_source"]
CHECKS_YAML = json.dumps(CHECKS_LIST)
SEED = 20261104
BATCH1_N = 16
BATCH2_N = 8
BUDGET_USD = 4.00
ARMS = ("A", "B")

#: Contract A's gutter: right-aligned width 5, then "| ". `docs/design/
#: PROVENANCE_ADDRESSING.md` §1.1.
GUTTER = "{:>5}| "
#: Contract B's cap on a quoted span, from the design document §2.1.
QUOTE_MAX = 80

#: The markers `context.outline` writes in place of a file it did not render
#: verbatim (`outline.py:62-70`, `outline.py:_stub`). A file carrying one of
#: these must not be numbered: an outline's line 10 is not the file's line 10,
#: and numbering it manufactures wrong addresses that look right (§4 A.ii).
ELIDED_MARKERS = ("<large file elided:", "<file not shown this round")

SKILLS = {"A": HERE / "study8" / "SKILL_A.md",
          "B": HERE / "study8" / "SKILL_B.md"}
SKILL_PATH = "skills/provenance-numbers.md"


# ------------------------------------------------- the deterministic contract
#
# `cli/build.py:709` renders `dcl.describe(cfg.checks)` into the generator
# prompt. The shipped sentence describes the SHIPPED addressing grammar, so an
# arm that changes the grammar and leaves that sentence alone would hand the
# generator two contradicting contracts. Each arm's sentence is produced by a
# targeted substitution on the shipped text — committed here, so the diff
# between the arms is exactly the addressing half and nothing else.

_A_SUFFIX = (
    " Every file you may cite is rendered to you with its line numbers in a "
    "gutter; a file shown without a gutter, or shown as a structural outline or "
    "a stub, cannot be cited. An annotation row names v, u and src only: the "
    "line of your own artefact is not asked for and is not read.")

_B_SUFFIX = (
    " An annotation row names v, u and src only, and no line number is asked for "
    "anywhere — not for the source and not for your own artefact.")

_B_EDITS = (
    ("block, and every results.json quantity whose source carries a '#L14' span "
     "fragment, must name a span — a path and a line range inside the audited "
     "scope — that resolves and contains the transcribed value and unit.",
     "block must name a source — a path inside the audited scope, and a "
     "quotation of at most 80 characters copied exactly from that file — where "
     "the quotation is found in the file and contains the transcribed value and "
     "unit. Runs of whitespace are collapsed on both sides before the search and "
     "nothing else is normalised."),
    ("A named span that does not resolve or does not "
     "contain the pair is a blocker;",
     "A quotation that is not found in the named file, or that does not contain "
     "the pair, is a blocker; a quotation the named file holds more than once is "
     "ADVISORY (ambiguous) and never blocks;"),
)


def arm_contract(arm: str) -> str:
    """The deterministic-check contract text this arm shows the generator."""
    from crossaudit.dcl import describe

    text = describe(CHECKS_LIST)
    if arm == "A":
        return text + _A_SUFFIX
    for old, new in _B_EDITS:
        if old not in text:
            raise SystemExit(
                "the shipped number_source contract text has moved; arm B's "
                "substitution would silently not apply. Fix the harness, not the "
                f"product. Missing: {old[:60]!r}")
        text = text.replace(old, new)
    return text + _B_SUFFIX


# ------------------------------------------------------ contract A's gutter

#: Filled per generator call so the report can prove the gutter was rendered and
#: name every file it deliberately left unnumbered.
GUTTER_LOG: list[dict] = []


def number_text(text: str) -> str:
    """1-based, per file, over `split("\\n")` — byte-identically to `numbers._span`
    (`numbers.py:341-354`). Any other convention makes prompt and checker disagree
    about what line 10 is, which is the original defect in a uniform."""
    return "\n".join(GUTTER.format(i) + line
                     for i, line in enumerate(text.split("\n"), 1))


def _elided(text: str) -> bool:
    return text.lstrip().startswith(ELIDED_MARKERS)


def gutter_build_prompt(_inner):
    """`generator.build_prompt`, with contract A's gutter on the WORK rendering.

    `current` is consumed in exactly one place (`generator.py:449-450`), so
    transforming it here is the whole of A's prompt change. A file the runtime
    already replaced with an outline or a stub is passed through untouched and
    recorded, because numbering it would manufacture addresses that look right.
    """
    def wrapper(*, current: dict[str, str], **kw):
        numbered, skipped = {}, []
        for path, body in (current or {}).items():
            if _elided(body):
                numbered[path] = body
                skipped.append(path)
            else:
                numbered[path] = number_text(body)
        GUTTER_LOG.append({"numbered": sorted(p for p in numbered
                                              if p not in skipped),
                           "not_numbered": sorted(skipped)})
        return _inner(current=numbered, **kw)
    return wrapper


# ---------------------------------------------------------------- the project

def bootstrap_arm_project(scratch: Path, task, row: dict, options: Options,
                          arm: str) -> Path:
    """`run.py`'s arm-B project with this arm's skill and one-check list.

    `run.bootstrap_project` is reimplemented rather than wrapped because its
    `checks:` comes straight from `options.checks` and this study needs an
    explicit list there; everything else — the constitution, the config template,
    RECIPE.md, the git shape — is the shipped harness's, called or copied
    verbatim so the two arms differ only where the design says they do.
    """
    project = scratch / "project"
    (project / INCREMENT_DIR).mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=str(project), check=True)
    git("config", "user.email", "bench@crossaudit.invalid", cwd=project)
    git("config", "user.name", "ExpertLongBench harness", cwd=project)

    (project / "AUDIT_RULES.md").write_text(constitution_text(task, options),
                                            encoding="utf-8")
    g, a = role_for(options.generator), role_for(options.auditor)
    (project / "crossaudit.yml").write_text(
        CONFIG_TEMPLATE.format(
            project=task.task_id, max_rounds=options.max_rounds,
            auditor_vendor=a.vendor, auditor_provider=a.provider,
            auditor_model=a.model, auditor_key_env=a.key_env,
            generator_vendor=g.vendor, generator_provider=g.provider,
            generator_model=g.model, generator_key_env=g.key_env,
            scope=SCOPE_DIR, checks=CHECKS_YAML,
            lone_model_blocker=options.lone_model_blocker),
        encoding="utf-8")
    (project / ".gitignore").write_text(".crossaudit/\n", encoding="utf-8")
    (project / RECIPE_PATH).write_text(
        f"# Source material\n\nThis is the material the explanation must be "
        f"justified against. Do not change this file.\n\n{row['input']}\n",
        encoding="utf-8")
    dest = project / SKILL_PATH
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(SKILLS[arm].read_text(encoding="utf-8"),
                    encoding="utf-8", newline="\n")
    subprocess.run(["git", "add", "-A"], cwd=str(project), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "bootstrap"],
                   cwd=str(project), check=True)
    return project


# ------------------------------------------ the increment, as cmd_run sees it

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
    """The files the DCL was handed, rebuilt from the tree — Arm 2's
    reconstruction, unchanged, and checked the same way against the receipt's
    own `inputs.manifest`."""
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
    return subprocess.run(["git", "log", "-1", "--format=%H", "--", OUTPUT_PATH],
                          cwd=str(project), capture_output=True, text=True,
                          check=True).stdout.strip()


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


def flat(text: str) -> str:
    """The one normalisation contract B performs, on BOTH sides: collapse every
    run of whitespace to a single space. `normalise_unit`'s fold
    (`numbers.py:219`) applied to a longer string. Nothing else."""
    return " ".join(str(text or "").split())


def resolve_key(files, annotated: str, named: str) -> str | None:
    """`numbers._resolve`'s rule, written here: exact key, then relative to the
    annotating artefact's directory. Deterministic, never a search."""
    if named in files:
        return named
    base = annotated.rsplit("/", 1)[0] if "/" in annotated else ""
    if base:
        joined = f"{base}/{named}"
        if joined in files:
            return joined
    return None


def _decode(files, key: str) -> str | None:
    try:
        return files[key].decode("utf-8")
    except (KeyError, UnicodeDecodeError):
        return None


# ------------------------------------------------------------ the verifiers
#
# Two dispositions, one verification half. Both call `numbers.contains_pair` and
# nothing else decides whether the located text holds the pair, so the arms
# differ only in how the text is located. Returned as
# (severity, rule, reason) where reason is a machine key for the classifier —
# never an observation string, because observations quote the corpus.

_PASS = ("PASS", "pass", "")


def _row_scalars(row: dict):
    """The shared, arm-independent front of both verifiers: three fields, right
    types, a value that is a number. `at` is gone from both grammars (§0)."""
    missing = [k for k in ("v", "u", "src") if k not in row]
    bad = [k for k in ("v", "u") if k in row
           and not isinstance(row[k], (str, int, float))]
    if missing or bad:
        return None, None, ("BLOCKER", "CA-NUM-001", "malformed:fields")
    v, u = str(row["v"]), str(row["u"])
    if not v.strip():
        return None, None, ("BLOCKER", "CA-NUM-001", "malformed:empty-value")
    if num_mod.normalise_number(v) is None:
        return None, None, ("BLOCKER", "CA-NUM-001", "malformed:not-a-number")
    return v, u, None


def verify_a(files, artefact: str, row: dict):
    """Contract A. `src` is `path#L<n>`; the located text is the named span."""
    v, u, bad = _row_scalars(row)
    if bad:
        return bad
    src = row["src"]
    if not isinstance(src, str) or not src:
        return ("BLOCKER", "CA-NUM-001", "malformed:src-type")
    if src == "uncited":
        return ("ADVISORY", "CA-NUM-003", "uncited")
    if src.startswith("governed:"):
        return ("ADVISORY", "CA-NUM-003", "governed")
    locator = src[len("computed:"):] if src.startswith("computed:") else src
    m = num_mod._SPAN.fullmatch(locator)
    if m is None:
        return ("BLOCKER", "CA-NUM-001", "malformed:not-a-span")
    named, start = m.group("path"), int(m.group("start"))
    end = int(m.group("end") or start)
    key = resolve_key(files, artefact, named)
    if key is None:
        return ("BLOCKER", "CA-NUM-001", "unresolved:path")
    declared = (m.group("sha") or "").lower()
    if declared and not hashlib.sha256(files[key]).hexdigest().startswith(declared):
        return ("BLOCKER", "CA-NUM-001", "unresolved:sha")
    body = _decode(files, key)
    if body is None:
        return ("BLOCKER", "CA-NUM-001", "unresolved:not-text")
    lines = body.split("\n")
    if start < 1 or end < start or end > len(lines):
        return ("BLOCKER", "CA-NUM-001", "unresolved:past-end")
    span = "\n".join(lines[start - 1:end])
    if not num_mod.contains_pair(span, v, u):
        return ("BLOCKER", "CA-NUM-002", "pair-not-in-location")
    return _PASS


def verify_b(files, artefact: str, row: dict):
    """Contract B. `src` is `{"file", "quote"[, "sha"]}`; the located text is the
    quote, found in the file by exact bytes with whitespace folded on both sides.

    The disposition order is the design's (§2.2) and is load-bearing: absent is a
    BLOCKER, non-unique is ADVISORY, and only then is the pair looked for.
    """
    v, u, bad = _row_scalars(row)
    if bad:
        return bad
    src = row["src"]
    if isinstance(src, str):
        if src == "uncited":
            return ("ADVISORY", "CA-NUM-003", "uncited")
        if src.startswith("governed:"):
            return ("ADVISORY", "CA-NUM-003", "governed")
        return ("BLOCKER", "CA-NUM-001", "malformed:src-type")
    if not isinstance(src, dict):
        return ("BLOCKER", "CA-NUM-001", "malformed:src-type")
    named, quote = src.get("file"), src.get("quote")
    if not isinstance(named, str) or not named:
        return ("BLOCKER", "CA-NUM-001", "malformed:src-file")
    if not isinstance(quote, str) or not 1 <= len(quote) <= QUOTE_MAX:
        return ("BLOCKER", "CA-NUM-001", "malformed:quote-length")
    key = resolve_key(files, artefact, named)
    if key is None:
        return ("BLOCKER", "CA-NUM-001", "unresolved:path")
    declared = str(src.get("sha") or "").lower()
    if declared:
        if not re.fullmatch(r"[0-9a-f]{8,64}", declared):
            return ("BLOCKER", "CA-NUM-001", "malformed:sha")
        if not hashlib.sha256(files[key]).hexdigest().startswith(declared):
            return ("BLOCKER", "CA-NUM-001", "unresolved:sha")
    body = _decode(files, key)
    if body is None:
        return ("BLOCKER", "CA-NUM-001", "unresolved:not-text")
    needle, hay = flat(quote), flat(body)
    if not needle:
        return ("BLOCKER", "CA-NUM-001", "malformed:quote-length")
    occurrences = hay.count(needle)
    if occurrences == 0:
        return ("BLOCKER", "CA-NUM-001", "quote-absent")
    if occurrences > 1:
        return ("ADVISORY", "CA-NUM-004", "ambiguous")
    if not num_mod.contains_pair(needle, v, u):
        return ("BLOCKER", "CA-NUM-002", "pair-not-in-location")
    return _PASS


VERIFIERS = {"A": verify_a, "B": verify_b}


# ------------------------------------------------------------- adjudication
#
# Deliberately their own resolution rather than the verifier's, so an
# adjudication is not the verifier agreeing with itself about which bytes to
# look at (Arm 2 §6).

def located_text(arm: str, files, artefact: str, row: dict):
    """`(key, text, occurrences)` for the location this row names, or None.

    None means the row names no location this study can re-read: `uncited`,
    `governed:`, a malformed row, an unresolvable path, a range outside the file,
    or (B) a quote the file does not contain. Such a row is A-negative and
    B-negative by definition, exactly as in Arm 2 §6.
    """
    src = row.get("src")
    if arm == "A":
        if not isinstance(src, str) or src == "uncited" or src.startswith("governed:"):
            return None
        locator = src[len("computed:"):] if src.startswith("computed:") else src
        m = num_mod._SPAN.fullmatch(locator)
        if m is None:
            return None
        key = resolve_key(files, artefact, m.group("path"))
        if key is None:
            return None
        body = _decode(files, key)
        if body is None:
            return None
        lines = body.split("\n")
        start = int(m.group("start"))
        end = int(m.group("end") or start)
        if start < 1 or end < start or end > len(lines):
            return None
        return key, "\n".join(lines[start - 1:end]), 1
    if not isinstance(src, dict):
        return None
    named, quote = src.get("file"), src.get("quote")
    if not isinstance(named, str) or not isinstance(quote, str):
        return None
    key = resolve_key(files, artefact, named)
    if key is None:
        return None
    body = _decode(files, key)
    if body is None:
        return None
    needle = flat(quote)
    if not needle:
        return None
    occurrences = flat(body).count(needle)
    if occurrences == 0:
        return None
    return key, needle, occurrences


def adjudicator_b(text: str, v: str, u: str) -> bool:
    """Independent of everything in `src/`: exact substring, no normalisation.
    Arm 2's, unchanged, so the two studies share the sensitivity instrument."""
    if str(v) not in text:
        return False
    return not str(u) or str(u) in text


def unit_shortened(text: str, v: str, u: str) -> bool:
    """Did the generator transcribe a unit that is a strict PREFIX of the whole
    unit token at an occurrence of its value? Arm 1's failure, generator-side."""
    wanted_value = num_mod.normalise_number(v)
    folded = num_mod.normalise_unit(u)
    if wanted_value is None or not folded:
        return False
    for m in num_mod._NUMBER.finditer(text):
        if num_mod.normalise_number(m.group(1)) != wanted_value:
            continue
        token, _ = num_mod.unit_token(text[m.end():])
        token = num_mod.normalise_unit(token)
        if token != folded and token.startswith(folded):
            return True
    return False


# -------------------------------------------------------- block classification
#
# §10 of the preregistration, evaluated in order, first match wins, written
# before any block was seen.

def named_file_key(arm: str, files, artefact: str, row: dict) -> str | None:
    src = row.get("src")
    if arm == "A":
        if not isinstance(src, str) or src in ("uncited",) or src.startswith("governed:"):
            return None
        locator = src[len("computed:"):] if src.startswith("computed:") else src
        m = num_mod._SPAN.fullmatch(locator)
        return resolve_key(files, artefact, m.group("path")) if m else None
    if not isinstance(src, dict) or not isinstance(src.get("file"), str):
        return None
    return resolve_key(files, artefact, src["file"])


def classify_block(arm: str, files, artefact: str, row: dict, reason: str,
                   adj_a, location, outlined: set[str]) -> tuple[str, str]:
    """Returns `(class, detail)`. `detail` is recorded data, never a class."""
    v, u = str(row.get("v", "")), str(row.get("u", ""))
    key = named_file_key(arm, files, artefact, row)

    # 1 — the location resolves and adjudicator A says it holds the pair.
    if location is not None and adj_a:
        return "verifier wrong", reason
    # 2 — a row the arm's grammar cannot read at all.
    if reason.startswith("malformed:"):
        return "malformed row", reason
    # 3 — the cited file was not rendered verbatim to this generator.
    if key is not None and key in outlined:
        return "outline-replaced file", reason
    # 4 — notation the layer documents that it cannot represent.
    if " " in num_mod.normalise_unit(u) and u.strip():
        return "unparsed notation", "unit-contains-space"
    wanted = num_mod.normalise_number(v)
    if location is not None and wanted is not None:
        for m in num_mod._NUMBER.finditer(location[1]):
            if num_mod.normalise_number(m.group(1)) == wanted and \
                    num_mod._UNPARSED.match(location[1][m.end():]):
                return "unparsed notation", "unparsed-after-value"
    # 5 — the location is not unique. Advisory by routing, so this can only be
    #     reached if a future change makes it block; kept so the table is total.
    if reason == "ambiguous":
        return "ambiguous", reason
    body = _decode(files, key) if key else None
    pair_in_file = bool(body) and num_mod.contains_pair(body, v, u)
    # 6 — B only: the quote is not there by exact bytes, but the pair is.
    if arm == "B" and reason == "quote-absent":
        return ("paraphrase" if pair_in_file else "generator wrong file",
                "quote-absent")
    # 7 — the named file is not in the increment, or holds the pair nowhere.
    if key is None:
        return "generator wrong file", reason or "unresolved:path"
    if not pair_in_file:
        return "generator wrong file", reason
    # 8 — the pair is in the named file, but not where the row said it was.
    return "generator wrong line/quote", reason


# ------------------------------------------------------------- one instance

def usage_split(project: Path, cfg, run_id: str) -> dict:
    from crossaudit import usage

    events, _bad = usage.read_events(cfg.root / cfg.state_dir / usage.LEDGER_NAME)
    mine = [e for e in events if e.get("run_id") == run_id] or events

    def total(pred):
        rows = [e for e in mine if pred(e)]
        return {"calls": len(rows),
                "input": sum(int(e.get("input", 0)) for e in rows),
                "output": sum(int(e.get("output", 0)) for e in rows),
                "cost_usd": sum(float(e.get("api_value_usd") or 0.0) for e in rows)}

    gen_vendor = GENERATOR.split(":", 1)[0]
    aud_vendor = AUDITOR.split(":", 1)[0]
    out = {"all": total(lambda e: True),
           "generator": total(lambda e: e.get("vendor") == gen_vendor),
           "auditor": total(lambda e: e.get("vendor") == aud_vendor)}
    # The malformed-envelope re-ask (RESULTS-ARM2 §6) shows up as a SECOND
    # generator-role call in a one-round run. Counted per arm, not fixed.
    out["generator_role_calls"] = sum(
        1 for e in mine if str(e.get("role", "")) == "generator")
    return out


def analyse_project(project: Path, instance: str, arm: str,
                    gutter: list[dict] | None = None) -> dict:
    """Everything measured about one instance-arm, from its KEPT project tree."""
    from crossaudit.config import load as load_cfg

    cfg = load_cfg(project / "crossaudit.yml")
    record: dict = {"instance": instance, "arm": arm, "rows": []}
    sha_science = science_commit(project)
    record["science_sha"] = sha_science
    if not sha_science:
        record["analysis_error"] = "the loop committed no deliverable"
        return record

    files = audited_increment(project, sha_science, cfg)
    record["increment_files"] = sorted(files)
    record["manifest_agrees"] = None
    for cycle in sorted((project / cfg.ledger_dir).glob("*/receipt.json")):
        manifest = json.loads(cycle.read_text(encoding="utf-8")).get(
            "inputs", {}).get("manifest", {})
        record["manifest_agrees"] = manifest == {
            k: hashlib.sha256(v).hexdigest() for k, v in files.items()}

    draft = files.get(OUTPUT_PATH, b"").decode("utf-8", "replace")
    record["output_sha256"] = sha(draft)
    record["draft_chars"] = len(draft)
    record["draft_lines"] = draft.count("\n") + 1
    record["numbers_present"] = len(NUM.findall(strip_fences(draft)))
    record["fence_blocks"] = len(num_mod._FENCE.findall(draft))

    # What the SHIPPED check would have said, recorded as data. It verifies a
    # grammar neither arm writes, so it is never an outcome of this study; it is
    # here because a reader will ask, and because it proves the arms' rows are
    # not accidentally the shipped shape.
    record["shipped_check_blocks"] = sum(
        1 for f in num_mod.check_number_source(files) if f.severity == BLOCKER)

    if gutter is not None:
        record["gutter"] = gutter
        record["outlined_paths"] = sorted(
            {p for call in gutter for p in call["not_numbered"]})
    else:
        record["gutter"] = []
        record["outlined_paths"] = []
    outlined = set(record["outlined_paths"])

    verify = VERIFIERS[arm]
    for row_no, ann in enumerate(fence_rows(draft)):
        severity, rule, reason = verify(files, OUTPUT_PATH, ann)
        v, u = str(ann.get("v", "")), str(ann.get("u", ""))
        src = ann.get("src")
        location = located_text(arm, files, OUTPUT_PATH, ann)
        adj_a = adj_b = None
        if location is not None:
            adj_a = num_mod.contains_pair(location[1], v, u)
            adj_b = adjudicator_b(location[1], v, u)
        if isinstance(src, dict):
            kind = "quote"
            src_file = str(src.get("file", ""))
            quote_len = len(src["quote"]) if isinstance(src.get("quote"), str) else None
            quote_sha = sha(src["quote"]) if isinstance(src.get("quote"), str) else ""
        else:
            text = str(src)
            kind = ("uncited" if text == "uncited"
                    else "governed" if text.startswith("governed:")
                    else "computed" if text.startswith("computed:")
                    else "span")
            src_file, quote_len, quote_sha = text, None, ""
        record["rows"].append({
            "instance": instance, "arm": arm, "row": row_no,
            "src_kind": kind,
            # For A the locator IS the address and carries no corpus text; for B
            # only the path and the quote's digest and length are recorded.
            "src_addr": src_file if kind != "quote" else src_file,
            "quote_len": quote_len, "quote_sha256": quote_sha,
            "v_sha256": sha(v), "u_sha256": sha(u),
            "v_len": len(v), "u_len": len(u),
            "severity": severity, "disposition": rule, "reason": reason,
            "resolved_location": location is not None,
            "occurrences": location[2] if location else None,
            "location_file": location[0] if location else "",
            "adj_a": adj_a, "adj_b": adj_b,
            "unit_shortened": (unit_shortened(location[1], v, u)
                               if location is not None else None),
            "pair_in_named_file": _pair_in_named_file(arm, files, ann, v, u),
            "class": (classify_block(arm, files, OUTPUT_PATH, ann, reason,
                                     adj_a, location, outlined)[0]
                      if severity == BLOCKER else ""),
            "class_detail": (classify_block(arm, files, OUTPUT_PATH, ann, reason,
                                            adj_a, location, outlined)[1]
                             if severity == BLOCKER else ""),
        })
    return record


def _pair_in_named_file(arm: str, files, row: dict, v: str, u: str):
    key = named_file_key(arm, files, OUTPUT_PATH, row)
    if key is None:
        return None
    body = _decode(files, key)
    return None if body is None else num_mod.contains_pair(body, v, u)


def run_instance(out_dir: Path, task, row: dict, options: Options, run_id: str,
                 arm: str) -> dict:
    """One instance under one arm, with that arm's patches in force."""
    from crossaudit.cli import build as build_mod

    GUTTER_LOG.clear()
    contract = arm_contract(arm)
    saved_bootstrap = run_mod.bootstrap_project
    saved_describe = build_mod.describe_checks
    saved_prompt = gen_mod.build_prompt
    run_mod.bootstrap_project = (
        lambda scratch, t, r, o: bootstrap_arm_project(scratch, t, r, o, arm))
    build_mod.describe_checks = lambda _checks: contract
    if arm == "A":
        gen_mod.build_prompt = gutter_build_prompt(saved_prompt)
    try:
        safe = row["id"].replace("/", "__")
        scratch = out_dir / "instances" / f"{safe}__{arm}"
        scratch.mkdir(parents=True, exist_ok=True)
        started = time.time()
        result = run_mod.run_arm_b(scratch, task, row, options, run_id)
        project = scratch / "project"
        record: dict = {
            "instance": row["id"], "arm": arm, "ok": result.ok,
            "error": result.error, "exit_code": result.exit_code,
            "rounds": result.rounds, "wall_s": round(result.wall_s, 2),
            "prompt_sha256": result.prompt_sha256,
            "started_utc": datetime.fromtimestamp(started, timezone.utc).isoformat(),
        }
        from crossaudit.config import load as load_cfg

        cfg = load_cfg(project / "crossaudit.yml")
        record["usage"] = usage_split(project, cfg, run_id)
        record.update(analyse_project(project, row["id"], arm,
                                      [dict(c) for c in GUTTER_LOG]))
        return record
    finally:
        run_mod.bootstrap_project = saved_bootstrap
        build_mod.describe_checks = saved_describe
        gen_mod.build_prompt = saved_prompt


def reanalyse(out_dir: Path, batch: int) -> int:
    """Recompute every record's measured half from the kept project trees. No
    model call, no spend."""
    path = out_dir / f"records-b{batch}.jsonl"
    kept = [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rewritten = []
    for old in kept:
        safe = old["instance"].replace("/", "__")
        project = out_dir / "instances" / f"{safe}__{old['arm']}" / "project"
        fresh = analyse_project(project, old["instance"], old["arm"],
                                old.get("gutter"))
        merged = {k: v for k, v in old.items() if k in (
            "instance", "arm", "ok", "error", "exit_code", "rounds", "wall_s",
            "prompt_sha256", "started_utc", "usage")}
        merged.update(fresh)
        rewritten.append(merged)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n"
                            for r in rewritten), encoding="utf-8")
    print(f"reanalysed {len(rewritten)} record(s) in {path}")
    return 0


# ------------------------------------------------------------------ the study

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batch", type=int, default=1, choices=[1, 2])
    ap.add_argument("--out", default="", help="run directory (absolute)")
    ap.add_argument("--task", default="T03MaterialSEG")
    ap.add_argument("--only", default="", help="comma-separated instance ids (a retry)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--reanalyse", action="store_true")
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
        run_mod.RUNS_DIR / f"arm3-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    if not out_dir.is_absolute():
        raise SystemExit("--out must be absolute: the loop chdirs into each project")
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"arm3-b{args.batch}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"

    options = Options(
        task_id=args.task, n=len(chosen), seed=SEED, generator=GENERATOR,
        auditor=AUDITOR, judge=AUDITOR, mapper=AUDITOR, adjudicator=AUDITOR,
        max_rounds=1, checks=CHECKS_YAML, lone_model_blocker="block",
        na_policy="literal", arms="B", out=str(out_dir),
        audit_rules="general", subset=0, label=f"arm3-b{args.batch}")

    plan = {
        "run_id": run_id, "batch": args.batch, "task": args.task,
        "corpus_sha256": corpus_sha, "seed": SEED,
        "instance_ids": [r["id"] for r in chosen],
        "arms": list(ARMS),
        "models": {"generator": GENERATOR, "auditor": AUDITOR},
        "settings": {"max_rounds": 1, "checks": CHECKS_LIST,
                     "audit_rules": "general", "scope": SCOPE_DIR,
                     "increment_dir": INCREMENT_DIR, "output": OUTPUT_PATH,
                     "recipe": RECIPE_PATH, "gutter": GUTTER,
                     "quote_max": QUOTE_MAX},
        "skills": {arm: hashlib.sha256(
            SKILLS[arm].read_bytes()).hexdigest() for arm in ARMS},
        "contracts": {arm: hashlib.sha256(
            arm_contract(arm).encode("utf-8")).hexdigest() for arm in ARMS},
        "code_sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(HERE),
                                   capture_output=True, text=True).stdout.strip(),
        "git_status": subprocess.run(["git", "status", "--porcelain"], cwd=str(HERE),
                                     capture_output=True, text=True).stdout,
        "python": sys.version.split()[0], "platform": sys.platform,
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / f"plan-b{args.batch}.json").write_text(
        json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    for arm in ARMS:
        (out_dir / f"contract-{arm}.txt").write_text(
            arm_contract(arm) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in plan.items() if k != "git_status"}, indent=2))
    if args.dry_run:
        return 0

    records_path = out_dir / f"records-b{args.batch}.jsonl"
    done = set()
    if records_path.exists() and not args.only:
        done = {(json.loads(l)["instance"], json.loads(l)["arm"]) for l in
                records_path.read_text(encoding="utf-8").splitlines() if l.strip()}
    spend = 0.0
    stop = False
    # Paired by instance and run A-then-B inside it, so a budget stop leaves
    # COMPLETE PAIRS: the comparison's unit is the pair, and half a pair is not
    # a datum. Preregistered in §9.
    for index, row in enumerate(chosen, start=1):
        if stop:
            break
        for arm in ARMS:
            if (row["id"], arm) in done:
                print(f"[{index}/{len(chosen)}] {row['id']} arm {arm} — recorded")
                continue
            print(f"[{index}/{len(chosen)}] {row['id']} arm {arm} …", flush=True)
            record = run_instance(out_dir, task, row, options, run_id, arm)
            with records_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            spend += float(record.get("usage", {}).get("all", {}).get("cost_usd", 0.0))
            blocks = sum(1 for r in record["rows"] if r["severity"] == BLOCKER)
            passes = sum(1 for r in record["rows"] if r["severity"] == "PASS")
            print(f"    ok={record['ok']} rows={len(record['rows'])} "
                  f"pass={passes} blocks={blocks} "
                  f"gencalls={record.get('usage', {}).get('generator_role_calls')} "
                  f"cost=${record.get('usage', {}).get('all', {}).get('cost_usd', 0):.4f} "
                  f"(run so far ${spend:.3f})")
        if spend > BUDGET_USD:
            print("STOPPING: the preregistered budget is spent")
            stop = True
    print(f"batch {args.batch} spend ${spend:.4f}; records at {records_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
