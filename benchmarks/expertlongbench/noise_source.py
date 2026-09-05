"""Study 6 -- present study 3's archived arm-X drafts to ``premise.py --rejudge``.

Study 6 measures one thing: how much the shipped cross-vendor audit's round-one
behaviour moves when **nothing** moves except the provider. The drafts are fixed bytes
that were written once, in study 3's arm X, and their CLEAR ground truth was computed
once, in the same run. Neither is recomputed here -- re-scoring would spend money to
reproduce a number already on disk and would add the scorer's nondeterminism to a
measurement that exists to isolate the auditor's.

``premise.py --rejudge`` already does exactly this replay, and study 5's audit-only floor
(SD 2.59 pp over 11 drafts) was measured with it. Reusing it unchanged is what makes
study 6's number comparable to that one rather than merely adjacent to it. All this
module does is present study 3's run directory in the shape ``--rejudge`` reads.

Two things it does that a pure format shim would not, both of them checks:

* it recomputes the audit prompt digest for every instance, **offline**, by rebuilding
  the tree the way ``rebuild_project`` will and calling the product's own
  ``audit_inputs``. That digest goes into the source record, so every replicate's
  ``prompt_digest_matches_source`` is a real assertion that all replicates judged
  byte-identical input -- not an assumption;
* it refuses to run if the seeded sample does not reproduce the archive's 20 ids.

The archive is treated as read-only. Nothing under ``study-data/`` is written or moved.

**No corpus text leaves the gitignored run directory.** ``drafts`` quote the corpus, so
they are written under ``runs/`` only. The digest table this module also emits carries
ids, digests and counts, which is what may be committed.

Usage::

    export PYTHONPATH=<repo>/src
    python benchmarks/expertlongbench/noise_source.py \\
        --archive /Users/ericdong/Documents/Crossaudit/study-data/wt-split-runs/armX-split \\
        --out "$PWD/benchmarks/expertlongbench/runs/study6-source"
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from premise import audit_inputs, rebuild_project  # noqa: E402
from run import (  # noqa: E402
    Options,
    choose_samples,
    constitution_text,
    load_task_rows,
    sha256_text,
    verify_corpus,
)
from tasks import get_task  # noqa: E402

#: The arm whose prompt digest the source record carries. ``run_rejudge`` reads
#: ``arms[0]``'s digest as the expected one, and study 6 judges with ``cross`` alone.
SOURCE_ARM = "cross"

#: The one line of the audit prompt that is NOT a function of the audited bytes.
#:
#: ``prompt.build`` stamps the commit that versioned the rules -- ``CONSTITUTION @ <sha>``
#: -- so an audit can cite the standard it applied. A git commit id is a function of the
#: tree AND the commit timestamp, so rebuilding the same tree a second later yields the
#: same rules, the same recipe, the same draft, the same check results, and a different
#: line here. That makes ``run_rejudge``'s ``prompt_digest_matches_source`` fire on every
#: instance of every replicate, which is why this module records a digest over the prompt
#: with this line normalised as well: THAT one is stable, and it is the one that means
#: "the auditor read the same thing".
CONSTITUTION_STAMP = "CONSTITUTION @ "


def normalised_prompt(prompt: str) -> str:
    """The prompt with the rules-commit stamp replaced by a constant.

    Everything the auditor is asked to judge survives; only the provenance pointer to
    the rules file is flattened. Two prompts equal under this function differ in nothing
    a model could act on.
    """
    return "\n".join(
        f"{CONSTITUTION_STAMP}<normalised>" if line.startswith(CONSTITUTION_STAMP)
        else line
        for line in prompt.splitlines()
    )


def study6_options(task_id: str, n: int, seed: int, checks: str) -> Options:
    """The Options ``premise.py`` itself builds, so the rebuilt tree is the same tree.

    Every field that reaches ``bootstrap_project`` -- the constitution flavour, the
    checks profile, the models named in ``crossaudit.yml`` -- is copied from
    ``premise.main``. If those drift apart the prompt digests stop matching, which is
    the failure this module is built to make visible rather than silent.
    """
    return Options(
        task_id=task_id, n=n, seed=seed,
        generator="anthropic:claude-sonnet-4-6",
        auditor="openai:gpt-5.6-terra",
        judge="openai:gpt-5.6-terra",
        mapper="openai:gpt-5.6-terra",
        adjudicator="openai:gpt-5.6-terra",
        max_rounds=1, checks=checks, lone_model_blocker="block",
        na_policy="literal", arms="B", out="", audit_rules="rubric",
        subset=0, label="study6-source",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--archive", required=True,
                        help="study 3's arm-X run directory (read-only)")
    parser.add_argument("--out", required=True, help="absolute path; must be gitignored")
    parser.add_argument("--task", default="T03MaterialSEG")
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20260930)
    parser.add_argument("--checks", default="general")
    parser.add_argument("--round", type=int, default=1,
                        help="which of the archived rounds to replay. 1 by default: a "
                             "silent auditor at round one is what ends the loop.")
    parser.add_argument("--digest-table", default="",
                        help="where to write the committable id/digest/count table")
    parser.add_argument(
        "--only-unreached-in", default="",
        help="a replicate's run directory. Restrict this source to the instances whose "
             "audit call NEVER REACHED A PROVIDER there, so the replicate can be "
             "completed by retrying exactly those. This is retry plumbing, not a "
             "filter on results: an instance qualifies only when ``ok`` is false, i.e. "
             "no model answered and there is no outcome to have selected on. An "
             "instance whose auditor answered -- with findings, with none, or with a "
             "reply the validator rejected -- is never re-asked.")
    args = parser.parse_args(argv)

    archive = Path(args.archive).resolve()
    out_dir = Path(args.out).resolve()
    task = get_task(args.task)
    corpus_sha = verify_corpus(args.task)

    rows = choose_samples(load_task_rows(args.task), args.n, args.seed)
    rows_by_id = {row["id"]: row for row in rows}

    archive_plan = json.loads((archive / "plan.json").read_text(encoding="utf-8"))
    archive_ids = list(archive_plan["sample_ids"])

    if sorted(rows_by_id) != sorted(archive_ids):
        raise SystemExit(
            "the seeded sample is not the archive's sample, so the rebuilt trees would "
            "not be the trees study 3 audited:\n"
            f"  seeded  : {sorted(rows_by_id)}\n"
            f"  archived: {sorted(archive_ids)}")
    if archive_plan.get("corpus_sha256") != corpus_sha:
        raise SystemExit(
            f"the corpus on disk ({corpus_sha[:16]}...) is not the corpus study 3 ran "
            f"against ({str(archive_plan.get('corpus_sha256'))[:16]}...)")

    options = study6_options(args.task, args.n, args.seed, args.checks)
    constitution_sha = sha256_text(constitution_text(task, options))
    if constitution_sha != archive_plan.get("constitution_sha256"):
        raise SystemExit(
            "the rubric constitution has changed since study 3, so the auditor would be "
            f"reading different rules:\n  now: {constitution_sha}\n"
            f"  then: {archive_plan.get('constitution_sha256')}")

    # Restriction happens AFTER every provenance check, so a retry source is still
    # proved to be the archive's sample, corpus and constitution before it is narrowed.
    unreached: list[str] = []
    if args.only_unreached_in:
        replicate = json.loads(
            (Path(args.only_unreached_in) / "results.json").read_text(encoding="utf-8"))
        unreached = [
            instance["sample_id"]
            for instance in replicate["instances"]
            if not ((instance.get("arms") or {}).get(SOURCE_ARM) or {}).get("ok")
        ]
        if not unreached:
            print(f"{Path(args.only_unreached_in).name}: every audit reached a "
                  "provider; nothing to retry")
            return 0
        archive_ids = [i for i in archive_ids if i in set(unreached)]
        print(f"restricted to {len(archive_ids)} instance(s) whose audit call never "
              f"reached a provider in {Path(args.only_unreached_in).name}", flush=True)

    shutil.rmtree(out_dir, ignore_errors=True)
    (out_dir / "instances").mkdir(parents=True)
    scratch_root = out_dir / "_prepare"

    records: list[dict] = []
    table: list[dict] = []
    for position, sample_id in enumerate(archive_ids, start=1):
        safe = sample_id.replace("/", "__")
        source = archive / "instances" / safe
        draft_path = source / f"armB.round{args.round}.md"
        score_path = source / f"armB.round{args.round}.score.json"
        if not draft_path.exists() or not score_path.exists():
            print(f"[{position}/{len(archive_ids)}] {sample_id}: no round "
                  f"{args.round} on disk; skipped", flush=True)
            continue

        draft = draft_path.read_text(encoding="utf-8")
        score = json.loads(score_path.read_text(encoding="utf-8"))
        draft_sha = sha256_text(draft)

        # The prompt digest, computed the way every replicate will compute it, with no
        # model call anywhere in this path.
        scratch = scratch_root / safe
        shutil.rmtree(scratch, ignore_errors=True)
        scratch.mkdir(parents=True)
        project, cfg, sha = rebuild_project(scratch, task, rows_by_id[sample_id],
                                            options, draft)
        prompt, _constitution, prompt_sha, dcl = audit_inputs(cfg, sha)
        normalised_sha = sha256_text(normalised_prompt(prompt))
        # A second rebuild of the same tree, so the record says how much of the prompt
        # is actually stable rather than asserting that it is. Every line but the rules
        # stamp must survive, and the count of survivors is committed.
        second = scratch_root / f"{safe}-again"
        shutil.rmtree(second, ignore_errors=True)
        second.mkdir(parents=True)
        _project2, cfg2, sha2 = rebuild_project(second, task, rows_by_id[sample_id],
                                                options, draft)
        prompt2, _c2, _sha2, _d2 = audit_inputs(cfg2, sha2)
        shutil.rmtree(second, ignore_errors=True)
        prompt_lines = len(prompt.splitlines())
        lines_differing = sum(
            1 for a, b in zip(prompt.splitlines(), prompt2.splitlines()) if a != b
        ) + abs(prompt_lines - len(prompt2.splitlines()))
        normalised_stable = normalised_prompt(prompt) == normalised_prompt(prompt2)
        shutil.rmtree(scratch, ignore_errors=True)

        instance_dir = out_dir / "instances" / safe
        instance_dir.mkdir(parents=True, exist_ok=True)
        (instance_dir / "draft.md").write_text(draft, encoding="utf-8")

        wrong = sorted(k for k, v in score["per_item"].items()
                       if not (v["precision_hit"] and v["recall_hit"]))
        records.append({
            "sample_id": sample_id,
            "draft_sha256": draft_sha,
            "draft_score": score,
            "generation": {"reused_from": str(archive), "cost_usd": 0.0, "wall_s": 0.0,
                           "exit_code": None},
            # run_rejudge reads arms[0]'s prompt_sha256 as the digest every replicate
            # must reproduce. It is computed above, offline, from the same functions.
            "arms": {SOURCE_ARM: {"prompt_sha256": prompt_sha}},
        })
        table.append({
            "sample_id": sample_id,
            "round": args.round,
            "draft_sha256": draft_sha,
            "draft_bytes": len(draft.encode("utf-8")),
            "audit_prompt_sha256": prompt_sha,
            "audit_prompt_sha256_normalised": normalised_sha,
            "audit_prompt_lines": prompt_lines,
            "audit_prompt_lines_differing_on_rebuild": lines_differing,
            "audit_prompt_stable_under_normalisation": normalised_stable,
            "n_items": score["n_items"],
            "n_items_wrong": len(wrong),
            "items_wrong": wrong,
            "clear_f1": score["f1"],
            "dcl_hard_failures": dcl.get("total_hard_failures"),
        })
        print(f"[{position}/{len(archive_ids)}] {sample_id}: draft "
              f"{draft_sha[:12]} prompt {prompt_sha[:12]} wrong {len(wrong)}"
              f"/{score['n_items']}", flush=True)

    shutil.rmtree(scratch_root, ignore_errors=True)

    plan = {
        "study": "6-noise",
        "role": "source directory for premise.py --rejudge; generated, not measured",
        "built_utc": datetime.now(timezone.utc).isoformat(),
        "archive": str(archive),
        "archive_run_id": archive_plan.get("run_id"),
        "archive_label": archive_plan.get("label"),
        "task": args.task,
        "corpus_sha256": corpus_sha,
        "n": len(records),
        "seed": args.seed,
        "round_replayed": args.round,
        "restricted_to_unreached_in": args.only_unreached_in or None,
        "unreached_ids": unreached or None,
        "constitution_sha256": constitution_sha,
        "sample_ids": [r["sample_id"] for r in records],
        "code_sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(HERE),
                                   capture_output=True, text=True).stdout.strip(),
    }
    (out_dir / "results.json").write_text(
        json.dumps({"plan": plan, "instances": records}, indent=2, ensure_ascii=False)
        + "\n", encoding="utf-8")
    (out_dir / "plan.json").write_text(
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.digest_table:
        Path(args.digest_table).write_text(
            json.dumps({"plan": plan, "instances": table}, indent=2, ensure_ascii=False)
            + "\n", encoding="utf-8")

    total_wrong = sum(t["n_items_wrong"] for t in table)
    print(f"\n{len(records)} instances -> {out_dir}")
    print(f"rubric items wrong across the sample: {total_wrong} "
          f"(the denominator of every recall below)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
