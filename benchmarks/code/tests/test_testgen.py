"""Study 16's harness contracts: the flag logic is pure, the executor path is real.

The executor is a separate interpreter (``execute.EXECUTOR``); tests that need it are
skipped where it is absent, and say so, rather than pretending to have run.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import architectures as arch  # noqa: E402
import execute  # noqa: E402
import testgen  # noqa: E402

HAVE_EXECUTOR = os.access(execute.EXECUTOR, os.X_OK)

CORRECT = "def add(a, b):\n    return a + b\n"
WRONG_ON_NEGATIVES = "def add(a, b):\n    return abs(a) + abs(b)\n"
HANGS = "def add(a, b):\n    while True:\n        pass\n"


def _run(failed, timed_out=False):
    return {"failed": list(failed), "timed_out": timed_out, "total": 3, "wall_s": 0.0, "error": ""}


# --- the flag logic, pure ------------------------------------------------------------

def test_a_failing_generated_test_flags_and_validation_keeps_it_when_the_canonical_passes():
    v = testgen.judge(["t0", "t1", "t2"], candidate=_run([1]), canonical=_run([]))
    assert v["flagged_testgen"] and v["flagged_validated"]
    assert v["n_dropped_by_validation"] == 0 and v["n_validated"] == 3


def test_a_wrong_test_is_dropped_by_validation_so_only_the_unvalidated_arm_flags():
    # test 1 fails on the canonical solution too: it encodes a misreading, not a defect
    v = testgen.judge(["t0", "t1", "t2"], candidate=_run([1]), canonical=_run([1]))
    assert v["flagged_testgen"] is True
    assert v["flagged_validated"] is False
    assert v["n_dropped_by_validation"] == 1 and v["n_validated"] == 2


def test_no_failure_flags_nothing_and_an_empty_suite_cannot_flag():
    v = testgen.judge(["t0"], candidate=_run([]), canonical=_run([]))
    assert not v["flagged_testgen"] and not v["flagged_validated"]
    v = testgen.judge([], candidate=_run([]), canonical=_run([]))
    assert not v["flagged_testgen"] and not v["flagged_validated"]


def test_a_candidate_timeout_flags_and_an_unusable_canonical_disarms_the_validated_arm():
    v = testgen.judge(["t0"], candidate=_run([0], timed_out=True), canonical=_run([]))
    assert v["flagged_testgen"] and v["flagged_validated"]
    v = testgen.judge(["t0"], candidate=_run([0]), canonical=_run([0], timed_out=True))
    assert v["flagged_testgen"] and not v["flagged_validated"] and v["canonical_unusable"]


def test_arm_flags_compose_over_records_and_respect_a_missing_comparator():
    row = {"flagged_testgen": True, "flagged_validated": False, "hc_flagged": False}
    assert testgen.arm_flag("testgen", row) and not testgen.arm_flag("testgen-validated", row)
    assert testgen.arm_flag("hc_u_testgen", row) is True
    row["hc_flagged"] = None
    assert testgen.arm_flag("hc", row) is None and testgen.arm_flag("hc_u_testgen", row) is None


def test_the_ceiling_residual_classes_are_read_by_instance():
    classes = testgen.residual_classes()
    assert classes, "the ceiling study's classification is a committed record"
    assert all(k.startswith(("b1:", "b2:")) for k in classes)
    assert "unexercised-edge" in set(classes.values())


# --- the executor path, real ---------------------------------------------------------

@pytest.mark.skipif(not HAVE_EXECUTOR, reason=f"executor absent: {execute.EXECUTOR}")
def test_generated_tests_run_separately_and_report_which_failed():
    tests = ["assert add(1, 2) == 3", "assert add(-1, -1) == -2", "assert add(0, 0) == 0"]
    good = testgen.run_generated(CORRECT, [], tests)
    bad = testgen.run_generated(WRONG_ON_NEGATIVES, [], tests)
    assert good["failed"] == [] and not good["timed_out"]
    assert bad["failed"] == [1] and not bad["timed_out"]
    assert testgen.judge(tests, bad, good)["flagged_validated"] is True


@pytest.mark.skipif(not HAVE_EXECUTOR, reason=f"executor absent: {execute.EXECUTOR}")
def test_a_hanging_candidate_times_out_rather_than_hanging_the_harness(monkeypatch):
    monkeypatch.setattr(testgen, "TIMEOUT_S", 2.0)
    out = testgen.run_generated(HANGS, [], ["assert add(1, 1) == 2"])
    assert out["timed_out"] and out["failed"] == [0]


@pytest.mark.skipif(not HAVE_EXECUTOR, reason=f"executor absent: {execute.EXECUTOR}")
def test_an_uncompilable_test_never_reaches_the_executor():
    kept, dropped = arch.compilable(["assert add(1, 1) ==", "assert add(1, 1) == 2"])
    assert dropped == 1
    out = testgen.run_generated(CORRECT, [], kept)
    assert out["failed"] == [] and out["total"] == 1
