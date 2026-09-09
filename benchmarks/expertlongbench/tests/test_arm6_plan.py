"""The Arm 6 runner never rewrites a run's plan (review rounds 1–2 of study 15's Arm 6)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import provenance_arm6 as runner  # noqa: E402


def _plan(started: str) -> dict:
    return {"run_id": f"arm6-{started}", "started_utc": started, "code_sha": "abc",
            "git_status": "", "instance_ids": ["a", "b"]}


def test_the_first_start_writes_the_plan_and_a_resume_never_overwrites_it(tmp_path):
    first = _plan("2026-09-07T10:44:36+00:00")
    assert runner.write_plan(tmp_path, first, "contract", "skill") == "plan.json"
    assert json.loads((tmp_path / "plan.json").read_text())["started_utc"] == first["started_utc"]
    assert (tmp_path / "contract-S.txt").exists() and (tmp_path / "skill-S.md").exists()

    resume = _plan("2026-09-07T10:57:33+00:00")
    name = runner.write_plan(tmp_path, resume, "contract", "skill")
    assert name.startswith("plan-resume-") and name.endswith(".json")
    assert json.loads((tmp_path / "plan.json").read_text())["started_utc"] == first["started_utc"], \
        "the resume overwrote the run's plan"
    assert json.loads((tmp_path / name).read_text())["started_utc"] == resume["started_utc"]


def test_two_resumes_in_the_same_second_are_both_kept(tmp_path):
    runner.write_plan(tmp_path, _plan("2026-09-07T10:44:36+00:00"), "c", "s")
    a = runner.write_plan(tmp_path, _plan("2026-09-07T10:57:33.100000+00:00"), "c", "s")
    b = runner.write_plan(tmp_path, _plan("2026-09-07T10:57:33.900000+00:00"), "c", "s")
    assert a != b and (tmp_path / a).exists() and (tmp_path / b).exists()
    assert json.loads((tmp_path / a).read_text())["started_utc"].endswith(".100000+00:00")
    assert json.loads((tmp_path / b).read_text())["started_utc"].endswith(".900000+00:00")
    assert len(list(tmp_path.glob("plan*.json"))) == 3
