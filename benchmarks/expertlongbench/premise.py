"""Study 5 -- does the second opinion have to come from a stranger?

CrossAudit's central claim is that work is judged better when the judge comes from a
*different vendor* than the writer. The heterogeneity invariant (``config.heterogeneity``)
refuses a same-vendor pair, and the README sells that refusal. It has never been measured.

This module measures it. **One** generator writes **one** draft per instance, into a real
git project through the product's real build loop. That single committed draft is then
**judged four ways**, and every judgement is scored against the same CLEAR ground truth:

    self     the same model that wrote it -- same vendor, same weights
    sibling  a different model from the same vendor
    cross    a different vendor -- the shipped configuration
    none     no judgement at all, the floor

Judging the *same* bytes is what makes the arms comparable. Nothing is regenerated per
arm; the only thing that varies between arms is which model reads the draft.

**The heterogeneity bypass lives here and only here.** The product's guard is inside
``crossaudit.auditor.run.run_audit``, and ``self``/``sibling`` cannot exist while it runs.
So this harness does not call ``run_audit``. It calls the *same product functions*
``run_audit`` calls -- ``_materialise_tree_scope``, ``_committed_constitution``,
``run_checks``, ``prompt.build``, ``resilience.complete``, ``parse_reply``,
``validate_reply`` -- in the same order, and skips the one guard. ``src/`` is not touched,
and the product still refuses a same-vendor pair everywhere a user can reach.
``--verify-prompt`` prints the harness prompt digest next to the digest the product's own
audit recorded for the same commit, so "same prompt, different model" is checked rather
than asserted.

The rules are rubric-grade (``rubric_constitution`` from :mod:`run`), not the shipped
general constitution. Under the general rules the auditor is near-silent -- 2.0% recall in
studies 2 and 3 -- and all four arms would look identical because none of them would say
anything. That choice is stated in the results.

Usage::

    export PYTHONPATH=<repo>/src
    python benchmarks/expertlongbench/premise.py --task T03MaterialSEG --n 16 \
        --seed 20261104 --out "$PWD/benchmarks/expertlongbench/runs/premise-rep1"
"""

from __future__ import annotations

import argparse
import contextlib
import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from adjudicate import Adjudicator, Finding  # noqa: E402
from clear import ClearScorer, NAPolicy  # noqa: E402
from provider import CrossAuditClient, missing_credentials, parse_spec, role_for  # noqa: E402
from run import (  # noqa: E402
    OUTPUT_PATH,
    RUNS_DIR,
    bootstrap_project,
    arm_b_task,
    chdir,
    choose_samples,
    constitution_text,
    load_credentials,
    load_task_rows,
    read_round_outputs,
    sha256_text,
    verify_corpus,
    Options,
)
from tasks import Task, get_task  # noqa: E402

#: The four arms, in the order the budget spends them. ``cross`` and ``self`` are the
#: comparison the study exists for, so they are judged first on every instance: if the
#: money runs out mid-run, the primary comparison is complete on every instance recorded.
ARMS = ("cross", "self", "sibling", "none")

#: Waits between attempts when every configured route came back rate-limited. A second
#: study is running against the same credentials, so HTTP 429 is the expected weather
#: here rather than a fault. The product's own resilience layer retries within a call;
#: this waits out a shared quota window, which is a different timescale.
BACKOFF_S = (45, 120, 300, 600)

#: What a saturated provider looks like from here. Two shapes, and the second is the
#: product's own breaker rather than the vendor: after enough 429s the resilience layer
#: opens a circuit and refuses to place the call at all ("cooling down"). Both mean the
#: same thing to this harness -- the call did not reach a model -- and both are safe to
#: retry for exactly that reason.
SATURATED = ("429", "rate limit", "rate_limit", "cooling down", "circuit",
             "too many requests")


def retrying(what: str, call, *args, **kwargs):
    """Place a provider call, waiting out a shared rate-limit window if one is hit.

    Retries ONLY when every route was exhausted -- the provider said 429, or the
    equivalent -- and never on a refusal that is about the request itself. A model that
    answered is never asked again: this wraps calls that could not be placed, so it can
    change how long a number takes to obtain and not what the number is.
    """
    from crossaudit.errors import ProviderDenial

    last: Exception | None = None
    for wait in (*BACKOFF_S, None):
        try:
            return call(*args, **kwargs)
        except ProviderDenial as exc:
            reason = str(getattr(exc, "reason", "") or exc).lower()
            if not any(marker in reason for marker in SATURATED):
                raise
            last = exc
            if wait is None:
                break
            print(f"    rate-limited on {what}; waiting {wait}s", flush=True)
            time.sleep(wait)
    raise last  # type: ignore[misc]


@dataclass
class ArmJudgement:
    """One arm's judgement of one draft."""

    arm: str
    spec: str
    ok: bool = False
    error: str = ""
    fired: bool = False
    verdict: str = ""
    invalid_reason: str = ""
    findings: list[dict] = field(default_factory=list)
    prompt_sha256: str = ""
    cost_usd: float = 0.0
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    #: sha256 of the auditor's reply text. The reply itself is never recorded: it
    #: quotes the increment, which quotes the corpus.
    response_sha256: str = ""
    #: The model id the PROVIDER echoed back, which is not always the one asked for:
    #: a vendor may silently resolve an alias to a dated build. In this study the
    #: model identity is the independent variable, so the echoed string is recorded.
    provider_model: str = ""
    provider_request_id: str = ""
    wall_s: float = 0.0
    repair_attempts: int = 0
    started_utc: str = ""
    finished_utc: str = ""


# --------------------------------------------------------------------------------------
# the audit, minus the one guard
# --------------------------------------------------------------------------------------


def audit_inputs(cfg, sha: str):
    """Everything the product's audit reads before it places a call.

    Product functions, in the product's order. Returns ``(prompt, constitution, sha256)``.
    """
    from crossaudit.auditor import prompt as prompt_mod
    from crossaudit.broker.routing import evidence_view
    from crossaudit.cli.main import (
        _committed_constitution,
        _committed_task,
        _materialise_tree_scope,
    )
    from crossaudit.dcl import run_checks

    files, notes, _scope = _materialise_tree_scope(cfg, sha, None)
    const_commit = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", cfg.constitution],
        cwd=str(cfg.root), capture_output=True, text=True,
    ).stdout.strip()
    constitution, _raw = _committed_constitution(cfg, const_commit)
    task_text = _committed_task(cfg, sha)
    dcl = run_checks(files, cfg.checks, notes, cfg.plugins).as_dict()
    prompt, _bounded, prompt_sha = prompt_mod.build(
        constitution, const_commit, dcl, files, task_text,
        tool_evidence=evidence_view(cfg),
    )
    return prompt, constitution, prompt_sha, dcl


def judge_once(cfg, sha: str, arm: str, spec: str, run_id: str,
               prepared=None) -> ArmJudgement:
    """Place one arm's audit turn against one committed draft.

    The product's own audit path with ``heterogeneity()`` removed, and nothing else
    removed: the same prompt bytes, the same system message, the same resilience layer,
    the same reply parser, the same rule validator, the same single bounded repair when a
    reply cannot be read at all.
    """
    from crossaudit.auditor import prompt as prompt_mod
    from crossaudit.auditor.validate import (
        NO_JSON_REASON, known_rules, parse_reply, validate_reply,
    )
    from crossaudit.providers import resilience
    from crossaudit import usage

    result = ArmJudgement(arm=arm, spec=spec)
    if arm == "none":
        result.ok = True
        return result

    prompt, constitution, prompt_sha, _dcl = prepared or audit_inputs(cfg, sha)
    result.prompt_sha256 = prompt_sha
    role = role_for(spec)
    result.started_utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()

    def ask(text: str):
        reply = retrying(
            f"the {arm} audit", resilience.complete,
            cfg, "auditor", role, system=prompt_mod.SYSTEM, prompt=text,
            allow_custom=False,
        )
        event = usage.record_reply(
            root=cfg.root, state_dir=cfg.state_dir, role="auditor",
            phase=f"premise-{arm}", vendor=role.vendor, provider=role.provider,
            model=role.model, reply=reply, system=prompt_mod.SYSTEM, prompt=text,
            base_url=role.base_url,
            context={"run_id": run_id, "prices": cfg.prices},
        )
        result.cost_usd += float(event.get("api_value_usd") or 0.0)
        result.calls += 1
        result.input_tokens += int(event.get("input", 0) or 0)
        result.output_tokens += int(event.get("output", 0) or 0)
        result.response_sha256 = getattr(reply, "response_sha256", "") or sha256_text(
            reply.text or "")
        raw = getattr(reply, "raw", None) or {}
        result.provider_model = str(raw.get("model") or "") or result.provider_model
        result.provider_request_id = str(getattr(reply, "request_id", "") or "")
        return reply

    def read(answer):
        parsed, parse_error = parse_reply(answer.text)
        if parse_error is not None:
            return parsed, parse_error, (
                "no_json" if parse_error == NO_JSON_REASON else "malformed_json")
        return parsed, validate_reply(parsed, known_rules(constitution)), ""

    try:
        raw = ask(prompt)
        parsed, invalid, unreadable = read(raw)
        if unreadable:
            # One bounded repair, exactly as the product does it, and only when nothing
            # readable arrived. A reply that parses and then fails a content rule stands
            # rejected with no second turn.
            with contextlib.suppress(Exception):
                repaired = ask(prompt + prompt_mod.repair_note(unreadable))
                result.repair_attempts += 1
                parsed, invalid, unreadable = read(repaired)
        result.ok = True
        if invalid is not None:
            result.invalid_reason = str(invalid)
        else:
            result.verdict = str(parsed.get("verdict", ""))
            result.findings = [
                {
                    "severity": f.get("severity", ""),
                    "rule": f.get("rule", ""),
                    "artifact": f.get("artifact", "?"),
                    "observation": f.get("observation", ""),
                    "tier": "model",
                }
                for f in (parsed.get("findings") or [])
            ]
            result.fired = bool(result.findings)
    except Exception as exc:  # noqa: BLE001 - recorded, never silently scored
        result.error = f"{type(exc).__name__}: {exc}"
    result.wall_s = time.monotonic() - started
    result.finished_utc = datetime.now(timezone.utc).isoformat()
    return result


# --------------------------------------------------------------------------------------
# scoring a judgement against CLEAR
# --------------------------------------------------------------------------------------


def score_judgement(adjudicator: Adjudicator, task: Task, judgement: ArmJudgement,
                    judgements_by_key: dict) -> dict:
    """Map an arm's findings onto rubric items and score them against CLEAR.

    Two mappings are recorded for every finding, because they answer the same question with
    different failure modes:

    * ``model`` -- the adjudicator model, as studies 1-3 used, so this study's recall is
      comparable to their 2.0% / 23.5%.
    * ``rule`` -- deterministic. The rubric constitution defines ``CA-RUBRIC-00N`` as
      rubric item N by construction, so citing that rule *is* naming that item, with no
      model in the loop. It exists as a sensitivity check on the model mapper.

    The lookup of CLEAR's verdict is not a model call under either mapping.
    """
    wrong = {k for k, j in judgements_by_key.items() if not j.accuracy_hit}
    per_finding: list[dict] = []
    named_model: set[str] = set()
    named_rule: set[str] = set()
    # A finding that names a real defect but is filed ADVISORY does not gate the
    # increment: the loop admits the work and the draft ships unrevised. So the same
    # rates are computed twice -- over every finding, and over the BLOCKER findings
    # alone, which are the ones the product acts on.
    blocking_model: set[str] = set()
    blocking_rule: set[str] = set()

    for finding in judgement.findings:
        record = {"rule": finding["rule"], "severity": finding["severity"],
                  "artifact": finding["artifact"], "cited_model": [], "cited_rule": [],
                  "note": ""}
        rule = finding["rule"].strip().upper()
        if rule.startswith("CA-RUBRIC-"):
            with contextlib.suppress(ValueError, IndexError):
                index = int(rule.rsplit("-", 1)[1]) - 1
                if 0 <= index < len(task.items):
                    record["cited_rule"] = [task.items[index].key]
        try:
            indices = retrying(
                "the adjudicator", adjudicator.map_finding,
                task,
                Finding(severity=finding["severity"], rule=finding["rule"],
                        artifact=finding["artifact"],
                        observation=finding["observation"], tier="model", round_no=1),
            )
            record["cited_model"] = [task.items[i].key for i in indices]
        except Exception as exc:  # noqa: BLE001
            record["note"] = f"adjudicator call failed: {type(exc).__name__}: {exc}"
        named_model.update(record["cited_model"])
        named_rule.update(record["cited_rule"])
        if finding["severity"] == "BLOCKER":
            blocking_model.update(record["cited_model"])
            blocking_rule.update(record["cited_rule"])
        per_finding.append(record)

    def rates(named: set[str]) -> dict:
        hit = wrong & named
        return {
            "n_named": len(named),
            "n_wrong_and_named": len(hit),
            "n_named_but_correct": len(named - wrong),
            "recall": (len(hit) / len(wrong)) if wrong else None,
            "precision": (len(hit) / len(named)) if named else None,
        }

    return {
        "arm": judgement.arm,
        "spec": judgement.spec,
        "ok": judgement.ok,
        "error": judgement.error,
        "invalid_reason": judgement.invalid_reason,
        "verdict": judgement.verdict,
        "fired": judgement.fired,
        "n_findings": len(judgement.findings),
        "n_blockers": sum(1 for f in judgement.findings if f["severity"] == "BLOCKER"),
        "rules_cited": sorted({f["rule"] for f in judgement.findings if f["rule"]}),
        "n_items": len(judgements_by_key),
        "n_items_wrong": len(wrong),
        "gated": bool(blocking_model or blocking_rule
                      or any(f["severity"] == "BLOCKER" for f in judgement.findings)),
        "model_mapping": rates(named_model),
        "rule_mapping": rates(named_rule),
        "blocker_model_mapping": rates(blocking_model),
        "blocker_rule_mapping": rates(blocking_rule),
        "per_finding": per_finding,
        "cost_usd": judgement.cost_usd,
        "calls": judgement.calls,
        "input_tokens": judgement.input_tokens,
        "output_tokens": judgement.output_tokens,
        "wall_s": judgement.wall_s,
        "prompt_sha256": judgement.prompt_sha256,
        "response_sha256": judgement.response_sha256,
        "provider_model": judgement.provider_model,
        "provider_request_id": judgement.provider_request_id,
        "repair_attempts": judgement.repair_attempts,
        "started_utc": judgement.started_utc,
        "finished_utc": judgement.finished_utc,
    }


# --------------------------------------------------------------------------------------
# the run
# --------------------------------------------------------------------------------------


def generate_draft(scratch: Path, task: Task, row: dict, options: Options,
                   run_id: str) -> tuple[Path, object, dict]:
    """One draft, through the product's real build loop, capped at one round.

    ``max_rounds: 1`` means the loop generates, audits once through the shipped
    cross-vendor path, and stops. The draft is therefore a genuine round-one product
    output, distributionally the same thing study 3's arm X measured -- and the loop's own
    audit is recorded so the harness ``cross`` arm can be checked against it.
    """
    from crossaudit.cli import build as build_mod
    from crossaudit.config import load

    project = bootstrap_project(scratch, task, row, options)
    cfg = load(project / "crossaudit.yml")
    meta: dict = {"exit_code": None, "error": "", "wall_s": 0.0}

    def on_event(event) -> None:
        return None

    on_event.run_id = run_id
    on_event.heartbeat = lambda: None

    started = time.monotonic()
    try:
        with chdir(project):
            meta["exit_code"] = build_mod.run_loop(cfg, arm_b_task(task), on_event=on_event)
    except Exception as exc:  # noqa: BLE001
        meta["error"] = f"{type(exc).__name__}: {exc}"
    meta["wall_s"] = time.monotonic() - started
    return project, cfg, meta


def product_audit_record(project: Path, cfg) -> dict:
    """What the loop's own (shipped, cross-vendor) audit recorded for round one."""
    ledger = project / cfg.ledger_dir
    if not ledger.is_dir():
        return {}
    for cycle_dir in sorted(ledger.iterdir()):
        receipt = cycle_dir / "receipt.json"
        if not receipt.exists():
            continue
        with contextlib.suppress(json.JSONDecodeError, KeyError):
            data = json.loads(receipt.read_text(encoding="utf-8"))
            audit = data.get("audit", {})
            return {
                "cycle_dir": cycle_dir.name,
                "verdict": audit.get("verdict", ""),
                "prompt_sha256": (data.get("inputs") or {}).get("prompt_sha256", ""),
                "constitution_sha256": (data.get("inputs") or {}).get(
                    "constitution_sha256", ""),
                "model": audit.get("model", ""),
                "vendor": audit.get("vendor", ""),
            }
    return {}


def probe_models(cfg, specs_wanted: list[str], run_id: str) -> dict:
    """Ask every model this run needs to answer one trivial question, before spending.

    Study 5's first attempt lost four instances' drafts and both noise-floor replicates
    to a credit balance that ran out mid-run, and it lost them one at a time, each after
    paying for a generation. A run that cannot finish should fail on its first second,
    loudly, for a few tenths of a cent -- not silently over an hour.

    Raises SystemExit naming every spec that did not answer. Returns what each one cost.
    """
    from crossaudit.providers import resilience

    results: dict[str, dict] = {}
    failed: list[str] = []
    for spec in specs_wanted:
        if not spec:
            continue
        role = role_for(spec)
        try:
            reply = resilience.complete(
                cfg, "probe", role,
                system="Answer with one word.", prompt="Reply with the single word: ok",
                allow_custom=False)
            results[spec] = {"ok": True, "answered": bool((reply.text or "").strip())}
        except Exception as exc:  # noqa: BLE001 - the whole point is to report it
            results[spec] = {"ok": False,
                             "error": f"{type(exc).__name__}: {str(exc)[:300]}"}
            failed.append(spec)
    if failed:
        lines = [f"  {spec}: {results[spec]['error']}" for spec in failed]
        raise SystemExit(
            "PREFLIGHT FAILED -- not starting a run that cannot finish.\n"
            + "\n".join(lines)
            + "\n\nEvery model this run needs must answer before any instance is "
              "generated. Fix the credential or the credit balance and run again.")
    print("preflight: " + ", ".join(f"{spec} ok" for spec in results), flush=True)
    return results


def environment() -> dict:
    """Versions the measurement depends on. Absent packages are recorded as absent."""
    import platform
    from importlib import metadata

    versions: dict[str, str] = {}
    for name in ("anthropic", "openai", "httpx", "requests", "urllib3", "certifi"):
        try:
            versions[name] = metadata.version(name)
        except Exception:  # noqa: BLE001 - "not installed" is itself the record
            versions[name] = "absent"
    return {
        "python": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "os": f"{platform.system()} {platform.release()}",
        "machine": platform.machine(),
        "packages": versions,
    }


def code_provenance() -> dict:
    """The frozen sha, and proof the tree was clean when it was frozen."""
    def git_out(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=str(HERE), capture_output=True,
                              text=True).stdout

    porcelain = git_out("status", "--porcelain").strip()
    files = {}
    for name in ("premise.py", "premise_report.py", "run.py", "clear.py",
                 "adjudicate.py", "tasks.py", "provider.py", "stats.py"):
        path = HERE / name
        if path.exists():
            files[f"benchmarks/expertlongbench/{name}"] = sha256_text(
                path.read_text(encoding="utf-8"))
    return {
        "frozen_sha": git_out("rev-parse", "HEAD").strip(),
        "git_status_porcelain": porcelain,
        "tree_clean": porcelain == "",
        "study_file_sha256": files,
    }


def dataset_provenance(task_id: str) -> dict:
    """What the corpus is, where it came from, and that it has not moved."""
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    entry = dict(manifest.get("tasks", {}).get(task_id, {}))
    entry["task_id"] = task_id
    entry["rows_on_disk"] = len(load_task_rows(task_id))
    entry["licence"] = manifest.get("licence") or manifest.get("license") or (
        "CC BY-NC-SA 4.0 (ExpertLongBench); not redistributed by this repository")
    entry["source"] = manifest.get("source", "")
    return entry


def model_roles(options: Options, specs_by_arm: dict, arms: list[str]) -> dict:
    """Every model id and the role it played. In this study the ids ARE the variable."""
    def described(spec: str) -> dict:
        if not spec:
            return {"spec": "", "note": "no model: this arm places no call"}
        role = role_for(spec)
        return {
            "spec": spec, "vendor": role.vendor, "provider": role.provider,
            "model": role.model, "base_url": role.base_url or "provider default",
            "key_env": role.key_env,
            "reasoning_effort": role.reasoning_effort or "provider default",
            # The adapters take temperature from the model's capability card and
            # `resilience.complete` exposes no seed, so neither is settable here.
            "temperature": "capability-card default; not settable through this seam",
            "seed": "not exposed by the provider layer",
        }

    return {
        "generator": described(options.generator),
        "auditor_by_arm": {arm: described(specs_by_arm[arm]) for arm in arms},
        "clear_mapper": described(options.mapper),
        "clear_judge": described(options.judge),
        "adjudicator": described(options.adjudicator),
    }


#: One JSONL row per instance per arm. Derived values only: ids, hashes, counts and
#: scores. No corpus text, no model output, no prompt.
ROWS_NAME = "rows.jsonl"


def emit_rows(out_dir: Path, record: dict, task: Task) -> None:
    """Append this instance's per-arm raw rows. Called once per completed instance."""
    score = record.get("draft_score") or {}
    per_item = score.get("per_item") or {}
    ground_truth = {
        key: {
            "precision_hit": value["precision_hit"],
            "recall_hit": value["recall_hit"],
            # CLEAR's accuracy criterion: mutual containment. This is the vector the
            # auditor is scored against, and it is what "wrong" means everywhere below.
            "correct": bool(value["precision_hit"] and value["recall_hit"]),
        }
        for key, value in per_item.items()
    }
    generation = record.get("generation") or {}
    with (out_dir / ROWS_NAME).open("a", encoding="utf-8") as handle:
        for arm, entry in (record.get("arms") or {}).items():
            row = {
                "study": "5-premise",
                "instance_id": record["sample_id"],
                "arm": arm,
                "auditor_spec": entry.get("spec", ""),
                # One round by construction: this study judges a draft, it does not
                # revise it, so there is no round two to record.
                "round": 1,
                "draft_sha256": record.get("draft_sha256", ""),
                "audit_sha": record.get("audit_sha", ""),
                "clear": {
                    "f1": score.get("f1"), "accuracy": score.get("accuracy"),
                    "precision": score.get("precision"), "recall": score.get("recall"),
                    "n_items": score.get("n_items"),
                    "per_item": ground_truth,
                    "n_items_wrong": entry.get("n_items_wrong"),
                },
                "audit": {
                    "ok": entry.get("ok"), "error": entry.get("error", ""),
                    "verdict": entry.get("verdict", ""),
                    "invalid_reason": entry.get("invalid_reason", ""),
                    "fired": entry.get("fired"), "gated": entry.get("gated"),
                    "n_findings": entry.get("n_findings"),
                    "n_blockers": entry.get("n_blockers"),
                    "repair_attempts": entry.get("repair_attempts", 0),
                },
                "findings": [
                    {
                        "rule": f["rule"], "severity": f["severity"],
                        "artifact": f["artifact"],
                        # Two mappings from finding to rubric item, and for each the
                        # ground-truth verdict on every item it named.
                        "items_model_mapping": f["cited_model"],
                        "items_rule_mapping": f["cited_rule"],
                        "item_was_wrong": {
                            key: (not ground_truth[key]["correct"])
                            for key in set(f["cited_model"]) | set(f["cited_rule"])
                            if key in ground_truth
                        },
                        "note": f.get("note", ""),
                    }
                    for f in (entry.get("per_finding") or [])
                ],
                "scored": {
                    "model_mapping": entry.get("model_mapping"),
                    "rule_mapping": entry.get("rule_mapping"),
                    "blocker_model_mapping": entry.get("blocker_model_mapping"),
                    "blocker_rule_mapping": entry.get("blocker_rule_mapping"),
                },
                "cost": {
                    "usd": entry.get("cost_usd"), "calls": entry.get("calls"),
                    "input_tokens": entry.get("input_tokens"),
                    "output_tokens": entry.get("output_tokens"),
                },
                "wall_s": entry.get("wall_s"),
                "started_utc": entry.get("started_utc", ""),
                "finished_utc": entry.get("finished_utc", ""),
                "prompt_sha256": entry.get("prompt_sha256", ""),
                "response_sha256": entry.get("response_sha256", ""),
                "provider_model_echoed": entry.get("provider_model", ""),
                "provider_request_id": entry.get("provider_request_id", ""),
                # Shared by every arm on this instance: one draft, judged four ways.
                "generation": {
                    "cost_usd": generation.get("cost_usd"),
                    "wall_s": generation.get("wall_s"),
                    "exit_code": generation.get("exit_code"),
                    "product_audit": generation.get("product_audit"),
                },
                "n_rubric_items": len(task.items),
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def ledger_cost(cfg, run_id: str, phases: set[str] | None = None) -> float:
    from crossaudit import usage

    events, _bad = usage.read_events(cfg.root / cfg.state_dir / usage.LEDGER_NAME)
    total = 0.0
    for event in events:
        if event.get("run_id") != run_id:
            continue
        if phases is not None and event.get("phase") not in phases:
            continue
        total += float(event.get("api_value_usd") or 0.0)
    return total


@dataclass(frozen=True)
class StoredJudgement:
    """One rubric item's CLEAR verdict, read back from a completed run.

    A re-judge does not re-score the draft: the draft is byte-identical, so its ground
    truth is too. Re-running CLEAR would spend money to reproduce a number already on
    disk and would add the scorer's own nondeterminism to a measurement that is trying
    to isolate the auditor's.
    """

    key: str
    precision_hit: bool
    recall_hit: bool

    @property
    def accuracy_hit(self) -> bool:
        return self.precision_hit and self.recall_hit


def rebuild_project(scratch: Path, task: Task, row: dict, options: Options,
                    draft: str) -> tuple[Path, object, str]:
    """Reconstruct the tree a completed instance was judged against, from its draft.

    Same bootstrap, same constitution, same recipe, same path for the deliverable, then
    one commit. The audit prompt is a pure function of that tree, so the digest must come
    out equal to the one the original run recorded -- and the caller checks that it does
    rather than assuming it.
    """
    project = bootstrap_project(scratch, task, row, options)
    (project / OUTPUT_PATH).write_text(draft, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=str(project), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "draft"], cwd=str(project), check=True)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(project),
                         capture_output=True, text=True).stdout.strip()
    from crossaudit.config import load

    return project, load(project / "crossaudit.yml"), sha


def run_rejudge(source: Path, task: Task, rows_by_id: dict, options: Options,
                plan: dict, out_dir: Path, run_id: str, arms: list[str],
                specs_by_arm: dict) -> int:
    """Judge an already-completed run's drafts again, changing nothing but the attempt.

    This is the auditor's own run-to-run variance with the draft and the ground truth
    both held fixed. It is NOT the preregistered noise floor, which also varies the
    generation; it is the part of that floor still obtainable when the generator's
    vendor has no credit left.
    """
    from crossaudit.config import load

    host = out_dir / "_host"
    shutil.rmtree(host, ignore_errors=True)
    host.mkdir(parents=True, exist_ok=True)
    source_results = json.loads((source / "results.json").read_text(encoding="utf-8"))
    completed = [i for i in source_results["instances"]
                 if i.get("draft_score") and i.get("arms")]
    host_project = bootstrap_project(host, task, rows_by_id[completed[0]["sample_id"]],
                                     options)
    host_cfg = load(host_project / "crossaudit.yml")
    adjudicator = Adjudicator(
        CrossAuditClient(cfg=host_cfg, phase="adjudication", run_id=run_id),
        model=options.adjudicator)

    records: list[dict] = []
    mismatches = 0
    for position, source_record in enumerate(completed, start=1):
        sample_id = source_record["sample_id"]
        print(f"[{position}/{len(completed)}] {sample_id}", flush=True)
        draft = (source / "instances" / sample_id.replace("/", "__")
                 / "draft.md").read_text(encoding="utf-8")
        if sha256_text(draft) != source_record.get("draft_sha256"):
            print("    draft digest does not match the record; skipped", flush=True)
            continue
        by_key = {
            key: StoredJudgement(key, value["precision_hit"], value["recall_hit"])
            for key, value in source_record["draft_score"]["per_item"].items()
        }
        scratch = out_dir / "_scratch" / sample_id.replace("/", "__")
        shutil.rmtree(scratch, ignore_errors=True)
        scratch.mkdir(parents=True)
        try:
            project, cfg, sha = rebuild_project(
                scratch, task, rows_by_id[sample_id], options, draft)
            prepared = audit_inputs(cfg, sha)
            original = ((source_record.get("arms") or {}).get(arms[0]) or {}).get(
                "prompt_sha256", "")
            same_prompt = prepared[2] == original
            if not same_prompt:
                mismatches += 1
            record: dict = {
                "sample_id": sample_id,
                "draft_sha256": source_record["draft_sha256"],
                "audit_sha": sha,
                "draft_score": source_record["draft_score"],
                "draft_score_cost_usd": 0.0,
                "generation": {"cost_usd": 0.0, "wall_s": 0.0, "exit_code": None,
                               "reused_from": str(source)},
                "prompt_digest_matches_source": same_prompt,
                "arms": {},
            }
            for arm in arms:
                judgement = judge_once(cfg, sha, arm, specs_by_arm[arm], run_id,
                                       prepared=prepared)
                record["arms"][arm] = score_judgement(adjudicator, task, judgement,
                                                      by_key)
                summary = record["arms"][arm]
                print(f"    {arm:8} prompt_same={same_prompt} "
                      f"findings={summary['n_findings']:2} "
                      f"recall={summary['rule_mapping']['recall']} "
                      f"${summary['cost_usd']:.3f}", flush=True)
            record["judging_cost_usd"] = sum(
                a["cost_usd"] for a in record["arms"].values())
        except Exception as exc:  # noqa: BLE001
            print(f"    instance abandoned: {type(exc).__name__}: {str(exc)[:180]}",
                  flush=True)
            shutil.rmtree(scratch, ignore_errors=True)
            continue
        shutil.rmtree(scratch, ignore_errors=True)
        records.append(record)
        _write_index(out_dir, plan, records)
        emit_rows(out_dir, record, task)

    plan["rejudge_prompt_digest_mismatches"] = mismatches
    plan["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (out_dir / "manifest.json").write_text(
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\ndone. {len(records)} instances re-judged, {mismatches} prompt-digest "
          f"mismatches -> {out_dir}", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--task", default="T03MaterialSEG")
    parser.add_argument("--n", type=int, default=16)
    parser.add_argument("--seed", type=int, default=20261104)
    parser.add_argument("--subset", type=int, default=0,
                        help="keep only the first SUBSET of the seeded sample, so a "
                             "replicate runs on a strict subset of the main run")
    parser.add_argument(
        "--target-complete", type=int, default=0,
        help="stop once this many instances are COMPLETE -- drafted, scored and judged "
             "by every arm. The seeded sample is the headroom: instances that fail cost "
             "attempts, not analysed n. 0 runs the whole sample.")
    parser.add_argument(
        "--no-probe", action="store_true",
        help="skip the preflight that asks every model to answer before spending. "
             "Only for a rerun whose providers were just verified.")
    parser.add_argument("--generator", default="anthropic:claude-sonnet-4-6")
    parser.add_argument("--cross", default="openai:gpt-5.6-terra",
                        help="the shipped configuration: a different vendor")
    parser.add_argument("--self", dest="self_spec", default="",
                        help="defaults to the generator itself (same vendor, same weights)")
    parser.add_argument("--sibling", default="anthropic:claude-opus-4-8",
                        help="a different model from the generator's own vendor")
    parser.add_argument("--judge", default="openai:gpt-5.6-terra")
    parser.add_argument("--mapper", default="")
    parser.add_argument("--adjudicator", default="")
    parser.add_argument("--na-policy", default=NAPolicy.LITERAL.value,
                        choices=[p.value for p in NAPolicy])
    parser.add_argument("--checks", default="general")
    parser.add_argument("--arms", default=",".join(ARMS))
    parser.add_argument("--out", default="")
    parser.add_argument("--label", default="premise")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--rejudge", default="",
        help="a completed run directory. Judge ITS drafts again with --arms, reusing "
             "its CLEAR ground truth. Generates nothing and re-scores nothing: the "
             "auditor's own run-to-run variance with everything else held fixed.")
    parser.add_argument("--verify-prompt", action="store_true",
                        help="print the harness prompt digest beside the digest the "
                             "product's own audit recorded for the same commit")
    args = parser.parse_args(argv)

    load_credentials()
    task = get_task(args.task)
    corpus_sha = verify_corpus(args.task)
    rows = choose_samples(load_task_rows(args.task), args.n, args.seed)
    full_sample = [row["id"] for row in rows]
    if args.subset:
        rows = rows[: args.subset]

    self_spec = args.self_spec or args.generator
    specs_by_arm = {"cross": args.cross, "self": self_spec, "sibling": args.sibling,
                    "none": ""}
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    for arm in arms:
        if arm not in ARMS:
            raise SystemExit(f"unknown arm {arm!r}; known: {', '.join(ARMS)}")

    judge = args.judge
    options = Options(
        task_id=args.task, n=len(rows), seed=args.seed, generator=args.generator,
        auditor=args.cross, judge=judge, mapper=args.mapper or judge,
        adjudicator=args.adjudicator or judge, max_rounds=1, checks=args.checks,
        lone_model_blocker="block", na_policy=args.na_policy, arms="B", out=args.out,
        audit_rules="rubric", subset=args.subset, label=args.label,
    )

    generator_vendor, _ = parse_spec(args.generator)
    cross_vendor, _ = parse_spec(args.cross)
    sibling_vendor, _ = parse_spec(args.sibling)
    self_vendor, _ = parse_spec(self_spec)
    # The arms must actually be what they are named. A "sibling" that is a different
    # vendor, or a "cross" that is the same one, would silently make the study measure
    # nothing, so it is refused here rather than discovered in the numbers.
    if cross_vendor == generator_vendor:
        raise SystemExit(f"--cross must be a different vendor from --generator "
                         f"(both {generator_vendor}); that arm IS the vendor difference")
    if sibling_vendor != generator_vendor:
        raise SystemExit(f"--sibling must share the generator's vendor "
                         f"({generator_vendor}), not {sibling_vendor}")
    if self_vendor != generator_vendor or self_spec != args.generator:
        raise SystemExit("--self must be the generator itself: same vendor, same weights")
    if args.sibling == args.generator:
        raise SystemExit("--sibling must be a DIFFERENT model from the generator")

    wanted = sorted({args.generator, args.cross, args.sibling, self_spec,
                     options.judge, options.mapper, options.adjudicator})
    missing = missing_credentials(wanted)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = (Path(args.out) if args.out
               else RUNS_DIR / f"{args.task}-{args.label}-{run_id}").resolve()

    plan = {
        "study": "5-premise",
        "run_id": run_id,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "task": args.task,
        "corpus_sha256": corpus_sha,
        "n": len(rows),
        "seed": args.seed,
        "subset": args.subset,
        "sample_ids": [row["id"] for row in rows],
        "full_sample_ids": full_sample,
        "label": args.label,
        "arms": arms,
        "arm_models": {arm: specs_by_arm[arm] for arm in arms},
        "models": {"generator": args.generator, "judge": options.judge,
                   "mapper": options.mapper, "adjudicator": options.adjudicator},
        "settings": {"max_rounds": 1, "checks": args.checks,
                     "na_policy": args.na_policy, "audit_rules": "rubric"},
        "constitution_sha256": sha256_text(constitution_text(task, options)),
        "code_sha": code_provenance()["frozen_sha"],
        "missing_credentials": missing,
        # EXPERIMENT_RECORD s2: enough to reconstruct the run without this machine.
        "prereg": "benchmarks/expertlongbench/PREREGISTRATION-5.md",
        "code": code_provenance(),
        "dataset": dataset_provenance(args.task),
        "models_detailed": model_roles(options, specs_by_arm, arms),
        "sampling": {
            "seed": args.seed,
            "n_seeded": args.n,
            "subset": args.subset,
            "selection": "rows sorted by id, then random.Random(seed).sample(rows, n), "
                         "then re-sorted by id; --subset keeps the first k of that",
        },
        "environment": environment(),
        "target_complete": args.target_complete,
        "stopping_rule": "run to completion of the seeded sample, or stop and report "
                         "when the study's share of the US$20 two-study budget is "
                         "spent, whichever comes first",
    }

    if args.dry_run or missing:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        if missing:
            print("\nno live run; missing:\n  " + "\n  ".join(missing), file=sys.stderr)
            return 2
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "plan.json").write_text(
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"run {run_id}: {args.task}, n={len(rows)}, seed={args.seed} -> {out_dir}",
          flush=True)
    if not plan["code"]["tree_clean"]:
        print("WARNING: the tree was NOT clean at freeze; manifest records what "
              "was uncommitted", file=sys.stderr, flush=True)

    if args.rejudge:
        plan["rejudge_source"] = str(Path(args.rejudge).resolve())
        (out_dir / "manifest.json").write_text(
            json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return run_rejudge(Path(args.rejudge).resolve(), task,
                           {row["id"]: row for row in rows}, options, plan, out_dir,
                           run_id, arms, specs_by_arm)
    code = _execute(task, rows, options, plan, out_dir, run_id, arms, specs_by_arm,
                    resume=args.resume, verify_prompt=args.verify_prompt,
                    target_complete=args.target_complete, probe=not args.no_probe)
    plan["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (out_dir / "manifest.json").write_text(
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return code


def _execute(task: Task, rows: list[dict], options: Options, plan: dict, out_dir: Path,
             run_id: str, arms: list[str], specs_by_arm: dict, *, resume: bool,
             verify_prompt: bool, target_complete: int = 0, probe: bool = True) -> int:
    from crossaudit.config import load

    host = out_dir / "_host"
    if not resume:
        shutil.rmtree(host, ignore_errors=True)
    host.mkdir(parents=True, exist_ok=True)
    if (host / "project" / "crossaudit.yml").exists():
        host_project = host / "project"
    else:
        host_project = bootstrap_project(host, task, rows[0], options)
    host_cfg = load(host_project / "crossaudit.yml")

    if probe:
        plan["preflight"] = probe_models(
            host_cfg,
            sorted({options.generator, options.mapper, options.judge,
                    options.adjudicator, *(specs_by_arm[a] for a in arms)}),
            run_id)
        (out_dir / "manifest.json").write_text(
            json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    scorer = ClearScorer(
        CrossAuditClient(cfg=host_cfg, phase="clear-scoring", run_id=run_id),
        mapper_model=options.mapper, judge_model=options.judge,
        na_policy=NAPolicy(options.na_policy),
    )
    adjudicator = Adjudicator(
        CrossAuditClient(cfg=host_cfg, phase="adjudication", run_id=run_id),
        model=options.adjudicator,
    )

    records: list[dict] = []
    already: set[str] = set()
    index_path = out_dir / "results.json"
    if resume and index_path.exists():
        with contextlib.suppress(json.JSONDecodeError, KeyError):
            records = json.loads(index_path.read_text(encoding="utf-8"))["instances"]
            already = {r["sample_id"] for r in records}
        plan.setdefault("run_ids", [plan["run_id"]])
        plan["run_ids"].append(run_id)
        (out_dir / "plan.json").write_text(
            json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"resuming: {len(already)} of {len(rows)} already recorded", flush=True)

    def one_instance(row: dict) -> dict | None:
        """Everything for one instance, or ``None`` if it could not be completed.

        A ``None`` is deliberately NOT recorded: an instance that died because the
        provider was saturated has to stay eligible for a resume, and a record would
        make the resume skip it forever. The generation already paid for is lost, which
        is the cheaper of the two mistakes.
        """
        sample_id = row["id"]
        reference = {k: str(v) for k, v in row["human_reference_checklist"].items()}
        record: dict = {"sample_id": sample_id}

        scratch = out_dir / "_scratch" / sample_id.replace("/", "__")
        shutil.rmtree(scratch, ignore_errors=True)
        scratch.mkdir(parents=True)
        project, cfg, meta = generate_draft(scratch, task, row, options, run_id)

        round_outputs = read_round_outputs(project)
        draft = round_outputs.get("1", "")
        record["generation"] = {
            **meta,
            "n_rounds_committed": len(round_outputs),
            "cost_usd": ledger_cost(cfg, run_id),
            "product_audit": product_audit_record(project, cfg),
        }
        if not draft.strip():
            record["error"] = meta.get("error") or "the loop produced no round-one draft"
            shutil.rmtree(scratch, ignore_errors=True)
            return record

        # The commit the draft landed in: what every arm audits.
        audit_sha = subprocess.run(
            ["git", "log", "--reverse", "--format=%H", "--", OUTPUT_PATH],
            cwd=str(project), capture_output=True, text=True).stdout.split()[0]
        record["audit_sha"] = audit_sha
        record["draft_sha256"] = sha256_text(draft)

        # Ground truth, once. Every arm is scored against this same judgement set.
        scored = retrying("CLEAR scoring", scorer.score, task, sample_id, draft,
                          reference)
        record["draft_score"] = scored.score.to_json()
        record["draft_score_cost_usd"] = scored.cost.cost_usd
        by_key = {j.key: j for j in scored.score.judgements}

        prepared = audit_inputs(cfg, audit_sha)
        if verify_prompt:
            print(f"    harness prompt sha {prepared[2][:16]}  "
                  f"product {record['generation']['product_audit'].get('prompt_sha256','')[:16]}",
                  flush=True)

        record["arms"] = {}
        for arm in arms:
            judgement = judge_once(cfg, audit_sha, arm, specs_by_arm[arm], run_id,
                                   prepared=prepared)
            record["arms"][arm] = score_judgement(adjudicator, task, judgement, by_key)
            summary = record["arms"][arm]
            print(f"    {arm:8} findings={summary['n_findings']:2} "
                  f"recall={summary['model_mapping']['recall']} "
                  f"${summary['cost_usd']:.3f}", flush=True)

        record["judging_cost_usd"] = sum(a["cost_usd"] for a in record["arms"].values())
        # Model outputs quote the corpus and are never committed: they live under the
        # gitignored run directory only.
        instance_dir = out_dir / "instances" / sample_id.replace("/", "__")
        instance_dir.mkdir(parents=True, exist_ok=True)
        (instance_dir / "draft.md").write_text(draft, encoding="utf-8")
        (instance_dir / "record.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        shutil.rmtree(scratch, ignore_errors=True)
        return record

    def n_complete() -> int:
        return sum(1 for r in records if r.get("arms") and r.get("draft_score"))

    for position, row in enumerate(rows, start=1):
        sample_id = row["id"]
        if sample_id in already:
            continue
        if target_complete and n_complete() >= target_complete:
            print(f"target of {target_complete} complete instances reached; "
                  f"{len(rows) - position + 1} seeded instances left unrun", flush=True)
            break
        print(f"[{position}/{len(rows)}] {sample_id}  "
              f"(complete so far: {n_complete()})", flush=True)
        try:
            record = one_instance(row)
        except Exception as exc:  # noqa: BLE001 - printed, not recorded; see one_instance
            print(f"    instance abandoned: {type(exc).__name__}: "
                  f"{str(exc)[:200]}", flush=True)
            shutil.rmtree(out_dir / "_scratch" / sample_id.replace("/", "__"),
                          ignore_errors=True)
            continue
        if record is None:
            continue
        records.append(record)
        _write_index(out_dir, plan, records)
        if record.get("arms"):
            emit_rows(out_dir, record, task)

    print(f"\ndone. {len(records)} instances recorded, {n_complete()} complete "
          f"-> {out_dir}", flush=True)
    return 0


def _write_index(out_dir: Path, plan: dict, records: list[dict]) -> None:
    (out_dir / "results.json").write_text(
        json.dumps({"plan": plan, "instances": records}, indent=2, ensure_ascii=False)
        + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
