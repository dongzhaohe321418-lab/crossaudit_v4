"""Run a candidate solution against a test suite and return an outcome vector.

**No model touches anything in this file.** Every number the study calls ground truth
comes out of here: a Python interpreter either raised AssertionError on a given input or
it did not. That is the whole reason the code domain was chosen over prose.

Two suites per problem:

* **visible** — what the developer can see. HumanEval: the benchmark's original
  ``check()``. MBPP: the three assertions the prompt shows the model.
* **hidden** — EvalPlus's expanded suite, the ground truth. Its tail is always
  ``for i, (inp, exp) in enumerate(zip(inputs, results)): assertion(...)``, which this
  module rewrites into a collecting loop so a failure is reported as *which inputs*
  failed, not merely *that* the suite failed. When the pattern is absent the suite runs
  verbatim and the vector degrades to a single pass/fail — recorded as ``mode``.

Execution is a subprocess with a wall-clock timeout, a fresh temp cwd, and stdout
discarded. Candidate code is untrusted, so nothing here imports it into this process.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

#: The interpreter that runs candidate code. Needs numpy (EvalPlus suites import it) and
#: is deliberately NOT the interpreter running the harness.
EXECUTOR = os.environ.get(
    "CROSSAUDIT_BENCH_EXECUTOR",
    "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3")

DEFAULT_TIMEOUT = 30.0

_LOOP = re.compile(
    r"^(?P<indent>[ \t]*)for i, \(inp, exp\) in enumerate\(zip\(inputs, results\)\):\s*$",
    re.M)

#: Appended in place of the suite's own final loop. Reports every failing index rather
#: than stopping at the first, and treats an exception on one input exactly as a failure
#: on that input — which is what "the hidden test does not pass" means.
_COLLECTOR = """
{indent}__failures = []
{indent}for i, (inp, exp) in enumerate(zip(inputs, results)):
{indent}    try:
{indent}        {call}
{indent}    except BaseException:
{indent}        __failures.append(i)
{indent}import json as __json, sys as __sys
{indent}__sys.stderr.write("__CROSSAUDIT_VECTOR__" + __json.dumps(
{indent}    {{"total": len(inputs), "failed": __failures}}) + "\\n")
"""


@dataclass
class SuiteResult:
    """What one suite did. ``passed`` is the only field a verdict may rest on."""
    passed: bool
    total: int = 0
    failed_indices: list[int] = field(default_factory=list)
    #: "vector" (per-input outcomes recovered) or "binary" (whole-suite pass/fail only).
    mode: str = "binary"
    error: str = ""
    timed_out: bool = False
    wall_s: float = 0.0

    def as_dict(self) -> dict:
        return asdict(self)


def _run(program: str, timeout: float) -> tuple[int, str, str, bool]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "candidate_run.py"
        path.write_text(program, encoding="utf-8")
        try:
            done = subprocess.run(
                [EXECUTOR, str(path)], cwd=tmp, capture_output=True, text=True,
                timeout=timeout,
                env={**os.environ, "PYTHONHASHSEED": "0", "OMP_NUM_THREADS": "1"})
        except subprocess.TimeoutExpired:
            return 124, "", "timeout", True
        return done.returncode, done.stdout, done.stderr, False


def _vector_from_stderr(stderr: str) -> dict | None:
    for line in stderr.splitlines():
        if line.startswith("__CROSSAUDIT_VECTOR__"):
            try:
                return json.loads(line[len("__CROSSAUDIT_VECTOR__"):])
            except json.JSONDecodeError:
                return None
    return None


def instrument_plus_suite(test_code: str, call: str) -> tuple[str, bool]:
    """Rewrite the EvalPlus trailing loop into a collecting one.

    Returns (code, instrumented). Everything from the loop header to the end of the
    suite is replaced: the loop is always the last statement in these suites, and the
    body is a single ``assertion(...)`` call whose shape we supply, so nothing after it
    is lost. If the header is not found the code is returned untouched.
    """
    matches = list(_LOOP.finditer(test_code))
    if not matches:
        return test_code, False
    last = matches[-1]
    head = test_code[: last.start()]
    indent = last.group("indent")
    return head + _COLLECTOR.format(indent=indent, call=call), True


def run_suite(program: str, *, timeout: float = DEFAULT_TIMEOUT,
              instrumented: bool) -> SuiteResult:
    import time
    started = time.monotonic()
    code, _out, err, timed_out = _run(program, timeout)
    wall = time.monotonic() - started
    if timed_out:
        return SuiteResult(passed=False, error="timeout", timed_out=True, wall_s=wall)
    vector = _vector_from_stderr(err) if instrumented else None
    if vector is not None:
        return SuiteResult(
            passed=(code == 0 and not vector["failed"]),
            total=vector["total"], failed_indices=vector["failed"],
            mode="vector", wall_s=wall,
            error="" if code == 0 else err.strip()[-400:])
    return SuiteResult(
        passed=(code == 0), mode="binary", wall_s=wall,
        error="" if code == 0 else err.strip()[-400:])


# ---------------------------------------------------------------------------------
# per-benchmark programs
# ---------------------------------------------------------------------------------

def humaneval_visible(solution: str, base_test: str, entry_point: str) -> str:
    return f"{solution}\n\n{base_test}\n\ncheck({entry_point})\n"


def humaneval_hidden(solution: str, plus_test: str, entry_point: str) -> tuple[str, bool]:
    body, instrumented = instrument_plus_suite(plus_test, "assertion(candidate(*inp), exp, 0)")
    return f"{solution}\n\n{body}\n\ncheck({entry_point})\n", instrumented


def mbpp_visible(solution: str, test_imports: list[str], asserts: list[str]) -> str:
    """Each visible assertion is attempted separately, so the vector is per-assertion."""
    imports = "\n".join(test_imports)
    lines = "\n".join(
        f"    ({json.dumps(a)}),"
        for a in asserts)
    return (
        f"{solution}\n\n{imports}\n\n"
        f"__asserts = [\n{lines}\n]\n"
        f"__failures = []\n"
        f"for i, __src in enumerate(__asserts):\n"
        f"    try:\n"
        f"        exec(compile(__src, '<visible>', 'exec'), globals())\n"
        f"    except BaseException:\n"
        f"        __failures.append(i)\n"
        f"import json as __json, sys as __sys\n"
        f"__sys.stderr.write('__CROSSAUDIT_VECTOR__' + __json.dumps("
        f"{{'total': len(__asserts), 'failed': __failures}}) + '\\n')\n")


def mbpp_hidden(solution: str, plus_test: str, entry_point: str) -> tuple[str, bool]:
    body, instrumented = instrument_plus_suite(
        plus_test, f"assertion({entry_point}(*inp), exp, 0)")
    return f"{solution}\n\n{body}\n", instrumented


def self_test() -> int:
    """Sanity: the canonical solutions must pass both suites. Costs nothing."""
    here = Path(__file__).resolve().parent
    ok = True
    base = {json.loads(l)["task_id"]: json.loads(l)
            for l in (here / "data/humaneval_base.jsonl").read_text().splitlines()}
    for line in (here / "data/humaneval_plus.jsonl").read_text().splitlines()[:5]:
        row = json.loads(line)
        solution = row["prompt"] + row["canonical_solution"]
        vis = run_suite(humaneval_visible(solution, base[row["task_id"]]["test"],
                                          row["entry_point"]), instrumented=False)
        program, inst = humaneval_hidden(solution, row["test"], row["entry_point"])
        hid = run_suite(program, instrumented=inst)
        status = "ok" if (vis.passed and hid.passed) else "FAIL"
        if status == "FAIL":
            ok = False
        print(f"{row['task_id']:16} visible={vis.passed} hidden={hid.passed} "
              f"mode={hid.mode} n={hid.total} {status}")
    for line in (here / "data/mbpp_plus.jsonl").read_text().splitlines()[:5]:
        row = json.loads(line)
        solution = row["code"]
        entry = _mbpp_entry_point(row)
        vis = run_suite(mbpp_visible(solution, row["test_imports"], row["test_list"]),
                        instrumented=True)
        program, inst = mbpp_hidden(solution, row["test"], entry)
        hid = run_suite(program, instrumented=inst)
        status = "ok" if (vis.passed and hid.passed) else "FAIL"
        if status == "FAIL":
            ok = False
        print(f"MBPP/{row['task_id']:11} visible={vis.passed} hidden={hid.passed} "
              f"mode={hid.mode} n={hid.total} entry={entry} {status}")
    return 0 if ok else 1


#: MBPP+'s own hidden suite names the function it calls, in its trailing
#: ``assertion(<entry_point>(*inp), exp, 0)``. That is authoritative; parsing the visible
#: assertions instead picks up wrappers (``math.isclose(volume_sphere(10), ...)`` yields
#: ``isclose``) and silently scores the wrong function. Matches all 378 MBPP+ rows.
_ASSERTION_CALL = re.compile(r"assertion\(\s*([A-Za-z_]\w*)\s*\(\*inp")


def _mbpp_entry_point(row: dict) -> str:
    match = _ASSERTION_CALL.search(row["test"])
    if not match:
        raise ValueError(f"no entry point recoverable for MBPP/{row['task_id']}")
    return match.group(1)


if __name__ == "__main__":
    sys.exit(self_test())
