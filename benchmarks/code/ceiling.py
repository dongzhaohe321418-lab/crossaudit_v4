"""Study 8, ceiling 1 — the saturation curve: how much a detector family can ever see.

Preregistered in ``ceiling/PREREGISTRATION.md`` §1, committed before the first model call.

This module is **not a second harness**. It is a driver over ``explore.py``'s resumable
loop and its detector cache: ``explore.load_detector`` finds every record a detector
already has (study 1's arms, study 2's arms, study 7's cache, this study's cache) and
``explore.run_detector`` runs only what is missing, caching each reading keyed by
``(kind, route, draw, instance)`` before anything else happens. **A cached draw is never
re-run.** The only thing changed here is where new caches are written
(``records/ceiling/cache``) and which instances are in scope.

Two families run through the product's provider broker:

    cross   holistic audit, openai:gpt-5.6-terra          — the shipped cross-vendor auditor
    self    holistic audit, anthropic:claude-haiku-4-5    — the generator's own model

and one runs outside it (amendments 1 and 2):

    astra   holistic audit, gpt-6-astra at high reasoning, through the Codex CLI

``astra`` sends the **same prompt bytes** the broker would send — the same SYSTEM prompt,
the same constitution, the same deterministic-check output, the same increment — and is
parsed by the same reply validator, so its findings are commensurable with the others'.
It bypasses the broker, the metered ledger and the heterogeneity guard entirely, so it is
**a measurement of a model, not of the product path**, and is labelled that way wherever
it appears. It is run with stdin as its only input from a scratch directory outside the
worktree, read-only, so nothing it might read can reach the solutions or the hidden tests.

Scope is stratum P (110) and stratum C (150) — 260 instances. Stratum F is not extended
by this study (deviation 1); the three existing draws that cover it are unaffected.

    python benchmarks/code/ceiling.py --plan
    python benchmarks/code/ceiling.py --run <run-dir> --budget-usd 13
    python benchmarks/code/ceiling.py --run <run-dir> --astra --astra-price 20
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "expertlongbench"))

import audit as study1  # noqa: E402
import explore  # noqa: E402
from corpus import Problem, load_problems  # noqa: E402

REPO = HERE.parent.parent
RECORDS = HERE / "records"
CEILING = RECORDS / "ceiling"

#: Where this study's new detector caches are written. ``explore.EXPLORE`` is pointed
#: here for the duration; study 7's cache is still read, so a reading it already has is
#: never bought twice.
CEILING_CACHE = CEILING
EXPLORE_CACHE = RECORDS / "explore"

ASTRA_MODEL = "gpt-6-astra"
ASTRA_ROUTE = "astra"

#: The preregistered ladder (§1.6). Each entry is (family, draw). K_max is set by budget
#: alone: the loop walks this list in order and stops on the cap. The leaderboard is
#: never consulted while deciding whether to extend.
LADDER: list[tuple[str, int]] = [
    ("self", 2),                                   # complete study 1's partial draw
    ("cross", 4), ("cross", 5), ("self", 3), ("self", 4), ("self", 5),   # K = 5 both
    ("cross", 6), ("self", 6),
    ("cross", 7), ("self", 7),
    ("cross", 8), ("self", 8),
]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def in_scope(instances: dict[str, dict], audit_set: list[str]) -> list[str]:
    """Stratum P and stratum C — the recall population and the false-positive population."""
    return [i for i in audit_set if instances[i]["stratum"] in ("P", "C")]


def load_detector_everywhere(key: tuple[str, str, int], scope: set[str]) -> dict[str, dict]:
    """Every record this detector has, from study 7's cache and this study's alike.

    ``explore.load_detector`` reads the committed study-1/study-2 arms plus whichever
    cache directory ``explore.EXPLORE`` names. Both directories are consulted here, so a
    reading study 7 already paid for is never bought again.
    """
    found: dict[str, dict] = {}
    for directory in (EXPLORE_CACHE, CEILING_CACHE):
        explore.EXPLORE = directory
        found.update(explore.load_detector(key, scope))
    explore.EXPLORE = CEILING_CACHE
    return found


# ---------------------------------------------------------------------------------
# the astra family — the same prompt bytes, outside the broker
# ---------------------------------------------------------------------------------

#: `codex exec` writes its banner, its skills-budget warning and its token-usage line to
#: **stderr**, and the model's reply alone to stdout, so the two never have to be
#: separated by judgement. The reply is taken from stdout by a fixed rule (the last fenced
#: block, else the outermost brace-balanced object); the token count is read from stderr
#: and is the only cost signal this route gives. Verified on a real audit prompt: stdout
#: was the 121-byte JSON reply and nothing else.
_TOKENS = re.compile(r"tokens\s+used\s*[:\n ]\s*([0-9][0-9,]*)", re.I)
_FENCE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.S)

#: The bounded repair instruction, fixed and never reply-derived — the same shape the
#: product's own one-attempt repair uses (auditor/run.py).
ASTRA_REPAIR = ("\n\nYour previous reply could not be read as JSON. Reply now with "
                "exactly one JSON object and no other text, in the schema above.")


def astra_extract(stdout: str) -> tuple[str, int | None]:
    """(the reply the validator should see, tokens used or None).

    Deterministic and stated in advance. Preference order: the last fenced block, else
    the outermost brace-balanced JSON object. A reply neither shape can recover is
    returned verbatim so the validator rejects it and the instance is recorded as a
    failed reading rather than silently dropped.
    """
    tokens = None
    match = _TOKENS.search(stdout)
    if match:
        try:
            tokens = int(match.group(1).replace(",", ""))
        except ValueError:
            tokens = None
    blocks = _FENCE.findall(stdout)
    if blocks:
        return blocks[-1].strip(), tokens
    start = stdout.find("{")
    if start >= 0:
        depth, in_string, escape = 0, False, False
        for index in range(start, len(stdout)):
            char = stdout[index]
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return stdout[start:index + 1], tokens
    return stdout.strip(), tokens


def astra_prompt(cfg, problem: Problem, solution: str, constitution: str) -> tuple[str, str]:
    """The audit prompt the broker would send, byte for byte, plus its sha256.

    Built by the product's own ``auditor.prompt.build`` over the product's own
    deterministic-check output, so an ``astra`` reading differs from a ``cross`` reading
    in the model and the transport and in nothing else. ``--check-prompt`` proves it
    against study 2's committed ``prompt_sha256``.
    """
    from crossaudit.auditor import prompt as prompt_mod
    from crossaudit.dcl import run_checks

    files = study1.increment_files(problem, solution)
    dcl = run_checks(files, cfg.checks, [], cfg.plugins).as_dict()
    text, _bounded, digest = prompt_mod.build(
        constitution, "frozen", dcl, files, task=problem.spec)
    return text, digest


def astra_one(cfg, problem: Problem, solution: str, inst: dict, constitution: str,
              draw: int, scratch: Path, timeout: float) -> dict:
    """One `astra` reading: the identical prompt, over stdin, to a read-only Codex run."""
    from crossaudit.auditor import prompt as prompt_mod
    from crossaudit.auditor.validate import known_rules, parse_reply, validate_reply

    row = {"instance_id": inst["instance_id"], "batch": inst["batch"],
           "problem_id": inst["problem_id"], "stratum": inst["stratum"],
           "kind": "holistic", "route": ASTRA_ROUTE, "draw": draw,
           "model_spec": f"codex:{ASTRA_MODEL}",
           "detector": f"holistic__{ASTRA_ROUTE}__d{draw}"}
    try:
        user, digest = astra_prompt(cfg, problem, solution, constitution)
    except Exception as exc:  # noqa: BLE001
        row.update({"ok": False, "error": f"prompt: {type(exc).__name__}: {exc}"})
        return row
    row["prompt_sha256"] = digest
    payload = prompt_mod.SYSTEM + "\n\n" + user
    started = time.monotonic()
    try:
        done = subprocess.run(
            ["codex", "exec", "-m", ASTRA_MODEL,
             "-c", 'model_reasoning_effort="high"',
             "--sandbox", "read-only", "--skip-git-repo-check", "-"],
            input=payload, cwd=str(scratch), capture_output=True, text=True,
            timeout=timeout)
    except subprocess.TimeoutExpired:
        row.update({"ok": False, "error": f"codex timeout after {timeout:.0f}s",
                    "wall_s": round(time.monotonic() - started, 2)})
        return row
    except Exception as exc:  # noqa: BLE001
        row.update({"ok": False, "error": f"{type(exc).__name__}: {exc}",
                    "wall_s": round(time.monotonic() - started, 2)})
        return row
    row["wall_s"] = round(time.monotonic() - started, 2)
    if done.returncode != 0:
        row.update({"ok": False,
                    "error": f"codex exit {done.returncode}: {(done.stderr or '')[:300]}"})
        return row
    text, _ = astra_extract(done.stdout or "")
    _, tokens = astra_extract(done.stderr or "")
    row["tokens_used"] = tokens
    row["response_sha256"] = sha256_text(done.stdout or "")
    reply, parse_error = parse_reply(text)
    if parse_error is not None:
        # The product gives an unreadable reply exactly one bounded repair attempt
        # against the same route (auditor/run.py). Mirrored here so an ``astra``
        # reading is not penalised by a transport the other families do not use.
        row["repair_attempted"] = True
        try:
            done = subprocess.run(
                ["codex", "exec", "-m", ASTRA_MODEL,
                 "-c", 'model_reasoning_effort="high"',
                 "--sandbox", "read-only", "--skip-git-repo-check", "-"],
                input=payload + ASTRA_REPAIR, cwd=str(scratch), capture_output=True,
                text=True, timeout=timeout)
        except Exception as exc:  # noqa: BLE001
            row.update({"ok": False, "error": f"repair: {type(exc).__name__}: {exc}"})
            return row
        text, _ = astra_extract(done.stdout or "")
        _, tokens2 = astra_extract(done.stderr or "")
        row["tokens_used"] = (tokens or 0) + (tokens2 or 0)
        reply, parse_error = parse_reply(text)
    if parse_error is not None or reply is None:
        row.update({"ok": False, "error": f"unreadable reply: {parse_error}"})
        return row
    invalid = validate_reply(reply, known_rules(constitution))
    findings = reply.get("findings") or []
    blockers = [f for f in findings if f.get("severity") == "BLOCKER"]
    row.update({
        "ok": True, "error": "",
        "verdict": reply.get("verdict", ""),
        "invalid_reason": invalid or "",
        "model_findings": len(findings), "model_blockers": len(blockers),
        "dcl_blockers": 0,
        # The flag definition is studies 1, 2 and 7's, unchanged: at least one BLOCKER.
        "flagged": bool(blockers),
        "rules": sorted({f.get("rule", "") for f in blockers}),
        "finding_sha256": [sha256_text(f.get("observation", "")) for f in blockers],
        "finding_chars": [len(f.get("observation", "")) for f in blockers],
        "cost_usd": None,          # this route bills a subscription; tokens are the signal
    })
    return row


def run_astra(draw: int, todo: list[str], *, instances, problems, solutions, constitution,
              cfg, scratch: Path, workers: int, timeout: float,
              max_calls: int = 0) -> tuple[int, int]:
    """Run `astra` draw ``draw`` over ``todo``, caching each reading as it lands."""
    slug = f"holistic__{ASTRA_ROUTE}__d{draw}"
    cache_path = CEILING_CACHE / "cache" / f"{slug}.jsonl"
    failed_path = CEILING_CACHE / "cache" / f"{slug}.failed.jsonl"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if max_calls:
        todo = todo[:max_calls]
    lock = threading.Lock()
    written = 0
    tokens_total = 0

    def one(iid: str) -> dict:
        inst = instances[iid]
        return astra_one(cfg, problems[inst["problem_id"]], solutions[iid]["solution"],
                         inst, constitution, draw, scratch, timeout)

    with ThreadPoolExecutor(max_workers=workers) as pool, \
            cache_path.open("a", encoding="utf-8") as handle, \
            failed_path.open("a", encoding="utf-8") as failures:
        for done, row in enumerate(pool.map(one, todo), start=1):
            with lock:
                if row.get("ok"):
                    handle.write(json.dumps(row, sort_keys=True) + "\n")
                    handle.flush()
                    written += 1
                    tokens_total += int(row.get("tokens_used") or 0)
                else:
                    failures.write(json.dumps(
                        {"instance_id": row["instance_id"], "detector": slug,
                         "error": (row.get("error") or "")[:300]}, sort_keys=True) + "\n")
                    failures.flush()
            if done % 10 == 0 or done == len(todo):
                print(f"    {slug}: {done}/{len(todo)}  ok {written}  "
                      f"tokens {tokens_total:,}", flush=True)
    return written, tokens_total


# ---------------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default="", help="the run dir: solutions, property cache")
    parser.add_argument("--budget-usd", type=float, default=13.0)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--max-passes", type=int, default=6)
    parser.add_argument("--plan", action="store_true",
                        help="what is missing and what it would cost; spend nothing")
    parser.add_argument("--check-prompt", action="store_true",
                        help="prove the astra prompt bytes equal the shipped auditor's")
    parser.add_argument("--astra", action="store_true", help="run the astra family")
    parser.add_argument("--astra-draws", type=int, default=4)
    parser.add_argument("--astra-price", type=int, default=0,
                        help="run only this many instances of astra draw 1, to price it")
    parser.add_argument("--astra-workers", type=int, default=4)
    parser.add_argument("--astra-timeout", type=float, default=600.0)
    parser.add_argument("--astra-scope", default="all", choices=("all", "confirm"),
                        help="all 260 P/C instances, or study 7's committed confirm half")
    args = parser.parse_args(argv)

    explore.EXPLORE = CEILING_CACHE
    (CEILING_CACHE / "cache").mkdir(parents=True, exist_ok=True)

    instances = explore.load_instances()
    audit_set = explore.load_audit_set()
    scope = in_scope(instances, audit_set)
    scope_set = set(scope)
    print(f"scope: {len(scope)} instances (P + C) of {len(audit_set)}", flush=True)

    families = {"cross": [("holistic", "cross", d) for d in range(1, 9)],
                "self": [("holistic", "self", d) for d in range(1, 9)]}
    have = {k: load_detector_everywhere(k, scope_set)
            for keys in families.values() for k in keys}
    for family, keys in families.items():
        for k in keys:
            n = len(have[k])
            if n:
                print(f"  {family} draw {k[2]}: {n:3d} of {len(scope)}", flush=True)

    if args.plan:
        for family, draw in LADDER:
            key = ("holistic", family, draw)
            missing = [i for i in scope if i not in have[key]]
            print(f"ladder {family} d{draw}: {len(missing)} to run")
        return 0

    run_dir = Path(args.run) if args.run else None
    if run_dir is None:
        parser.error("--run is required unless --plan")

    from run import load_credentials
    load_credentials()
    study1.register_visible_tests_check()
    constitution = study1.shipped_constitution()
    problems = {p.problem_id: p for p in load_problems()}
    solutions: dict[str, dict] = {}
    for batch in ("b1", "b2"):
        for line in (run_dir / f"study2-inputs/solutions-{batch}.jsonl").read_text(
                encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                solutions[f"{batch}:{row['problem_id']}"] = row
    scratch = run_dir / "projects"
    scratch.mkdir(parents=True, exist_ok=True)
    cfg_cache: dict = {}
    spend = explore.Spend("ceiling-")

    if args.check_prompt or args.astra:
        from crossaudit.config import load
        cross_project = explore.build_project(scratch, ("holistic", "cross", 0), constitution)
        cross_cfg = load(cross_project / "crossaudit.yml")

    if args.check_prompt:
        committed = {}
        for line in (RECORDS / "study2/arm-holistic-cross.jsonl").read_text(
                encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                committed[row["instance_id"]] = row.get("prompt_sha256", "")
        agree = disagree = 0
        for iid in scope[:40]:
            inst = instances[iid]
            _text, digest = astra_prompt(cross_cfg, problems[inst["problem_id"]],
                                         solutions[iid]["solution"], constitution)
            if digest == committed.get(iid):
                agree += 1
            else:
                disagree += 1
                print(f"  MISMATCH {iid}: {digest[:16]} != {committed.get(iid, '')[:16]}")
        print(f"prompt bytes: {agree} agree, {disagree} disagree "
              f"(against study 2's committed holistic-cross prompt_sha256)")
        return 0

    if args.astra:
        astra_scope = scope
        if args.astra_scope == "confirm":
            split = json.loads((EXPLORE_CACHE / "split.json").read_text(encoding="utf-8"))
            astra_scope = [i for i in scope if split["halves"].get(i) == "confirm"]
            print(f"astra scope: study 7's confirm half, {len(astra_scope)} instances")
        astra_scratch = run_dir / "astra-scratch"
        astra_scratch.mkdir(parents=True, exist_ok=True)
        grand_tokens = 0
        for draw in range(1, args.astra_draws + 1):
            key = ("holistic", ASTRA_ROUTE, draw)
            existing = load_detector_everywhere(key, set(astra_scope))
            missing = [i for i in astra_scope if i not in existing]
            if not missing:
                print(f"astra draw {draw}: complete ({len(existing)})")
                continue
            print(f"\nastra draw {draw}: {len(missing)} to run", flush=True)
            written, tokens = run_astra(
                draw, missing, instances=instances, problems=problems,
                solutions=solutions, constitution=constitution, cfg=cross_cfg,
                scratch=astra_scratch, workers=args.astra_workers,
                timeout=args.astra_timeout, max_calls=args.astra_price)
            grand_tokens += tokens
            print(f"astra draw {draw}: {written} landed, {tokens:,} tokens", flush=True)
            if args.astra_price:
                break
        print(f"\nastra tokens this invocation: {grand_tokens:,}")
        write_manifest(instances, scope, spend, run_dir, astra_tokens=grand_tokens)
        return 0

    for family, draw in LADDER:
        key = ("holistic", family, draw)
        missing = [i for i in scope if i not in have[key]]
        if not missing:
            print(f"ladder {family} d{draw}: already complete")
            continue
        total = spend.total()
        if args.budget_usd and total >= args.budget_usd:
            print(f"\nSTOP: ceiling-1 spend ${total:.3f} reached the "
                  f"${args.budget_usd:.2f} cap; {family} d{draw} not run")
            break
        print(f"\nladder {family} d{draw}: {len(missing)} instances "
              f"(spend so far ${total:.3f})", flush=True)
        explore.run_detector(key, missing, instances=instances, problems=problems,
                             solutions=solutions, constitution=constitution,
                             cfg_cache=cfg_cache, scratch=scratch, spend=spend,
                             budget_usd=args.budget_usd, workers=args.workers,
                             property_cache_path=run_dir / "study2-inputs/properties.json",
                             max_passes=args.max_passes)
        have[key] = load_detector_everywhere(key, scope_set)
    print(f"\nceiling-1 spend this invocation: ${spend.total():.4f}", flush=True)
    write_manifest(instances, scope, spend, run_dir)
    return 0


def write_manifest(instances: dict, scope: list[str], spend: explore.Spend,
                   run_dir: Path, astra_tokens: int = 0) -> None:
    """Everything a reviewer needs to re-issue an identical request."""
    import platform
    from crossaudit.auditor import prompt as prompt_mod

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                          text=True).stdout.strip()
    porcelain = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                               capture_output=True, text=True).stdout
    codex_version = ""
    try:
        codex_version = subprocess.run(["codex", "--version"], capture_output=True,
                                       text=True, timeout=30).stdout.strip()
    except Exception:  # noqa: BLE001
        codex_version = "AUTHOR_INPUT_NEEDED: codex --version did not answer"
    path = CEILING / "manifest_ceiling1.json"
    prior = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    detectors = {}
    for family in ("cross", "self", ASTRA_ROUTE):
        for draw in range(1, 9):
            key = ("holistic", family, draw)
            records = load_detector_everywhere(key, set(scope))
            if records:
                detectors[explore.detector_slug(key)] = {
                    "records": len(records), "scope_n": len(scope),
                    "sources": sorted({r["source"] for r in records.values()})}
    manifest = {
        "study": "ceiling (study 8), ceiling 1 — the saturation curve",
        "code": {"commit": head, "status_porcelain": porcelain,
                 "files": {f: hashlib.sha256((REPO / f).read_bytes()).hexdigest()
                           for f in ("benchmarks/code/ceiling.py",
                                     "benchmarks/code/explore.py",
                                     "benchmarks/code/report_ceiling.py",
                                     "benchmarks/code/ceiling/PREREGISTRATION.md")
                           if (REPO / f).exists()}},
        "routes": {**explore.ROUTES, ASTRA_ROUTE: f"codex:{ASTRA_MODEL}"},
        "generator": explore.GENERATOR_SPEC,
        "astra": {"model": ASTRA_MODEL, "reasoning_effort": "high",
                  "transport": "codex exec, stdin only, --sandbox read-only "
                               "--skip-git-repo-check",
                  "codex_version": codex_version,
                  "bypasses": "the product's provider broker, its metered usage ledger "
                              "and its same-vendor heterogeneity guard; a measurement of "
                              "a model, not of the product path",
                  "tokens_this_invocation": astra_tokens},
        "prompts": {"auditor_system_sha256": sha256_text(prompt_mod.SYSTEM),
                    "auditor_system_text": prompt_mod.SYSTEM,
                    "constitution_sha256": sha256_text(study1.shipped_constitution())},
        "sampling": {"temperature": "not sent; the auditor capability card carries "
                                    "temperature=False (D154)",
                     "max_rounds": 1,
                     "flag_rule": "at least one BLOCKER finding"},
        "data": {"audit_set_sha256": hashlib.sha256(
                     (RECORDS / "study2/audit_set.json").read_bytes()).hexdigest(),
                 "instances_sha256": hashlib.sha256(
                     (RECORDS / "study2/instances.jsonl").read_bytes()).hexdigest(),
                 "scope": "stratum P and C", "scope_n": len(scope),
                 "corpus": json.loads((HERE / "manifest_corpus.json").read_text(
                     encoding="utf-8"))},
        "detectors": detectors,
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "must_match_to_reproduce": [
            "records/study2/audit_set.json sha256", "records/study2/instances.jsonl sha256",
            "the corpus revisions in manifest_corpus.json", "the model ids in routes",
            "auditor_system_sha256 and constitution_sha256",
            "the flag rule (>= 1 BLOCKER)"],
        "does_not_matter": [
            "worker count", "wall-clock time", "the machine and OS",
            "the order the ladder ran in", "the scratch directory path"],
        "spend_usd_this_invocation": round(spend.total(), 6),
        "spend_usd_by_run_id": {k: round(v, 6) for k, v in sorted(spend.by_run_id().items())},
        "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if prior:
        manifest["spend_usd_cumulative"] = round(
            prior.get("spend_usd_cumulative", 0.0) + manifest["spend_usd_this_invocation"], 6)
        manifest["astra_tokens_cumulative"] = (
            prior.get("astra_tokens_cumulative", 0) + astra_tokens)
    else:
        manifest["spend_usd_cumulative"] = manifest["spend_usd_this_invocation"]
        manifest["astra_tokens_cumulative"] = astra_tokens
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
