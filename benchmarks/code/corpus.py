"""The problems, joined across the three pinned files, with their two suites.

One :class:`Problem` per benchmark item. It knows how to build the two executable
programs (visible and hidden) around a candidate solution, and what the model is shown —
which is the visible half and nothing else. The hidden suite is never rendered into any
prompt; that is the property this whole study rests on.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

import execute  # noqa: E402


@dataclass(frozen=True)
class Problem:
    problem_id: str
    benchmark: str            # "humaneval" | "mbpp"
    entry_point: str
    #: What the generator is shown. For HumanEval, the function stub with its docstring;
    #: for MBPP, the natural-language prompt plus the three visible assertions.
    spec: str
    canonical_solution: str
    _visible_test: str
    _hidden_test: str
    _test_imports: tuple[str, ...] = ()
    _visible_asserts: tuple[str, ...] = ()

    @property
    def visible_instrumented(self) -> bool:
        return self.benchmark == "mbpp"

    def visible_program(self, solution: str) -> str:
        if self.benchmark == "humaneval":
            return execute.humaneval_visible(solution, self._visible_test, self.entry_point)
        return execute.mbpp_visible(solution, list(self._test_imports),
                                    list(self._visible_asserts))

    def hidden_program(self, solution: str) -> tuple[str, bool]:
        if self.benchmark == "humaneval":
            return execute.humaneval_hidden(solution, self._hidden_test, self.entry_point)
        return execute.mbpp_hidden(solution, self._hidden_test, self.entry_point)

    def visible_tests_text(self) -> str:
        """The visible suite as the developer sees it. Safe to show a model."""
        if self.benchmark == "humaneval":
            return self._visible_test
        return "\n".join(self._visible_asserts)


def _read(name: str) -> list[dict]:
    path = DATA / f"{name}.jsonl"
    if not path.exists():
        raise SystemExit(f"{path} is missing; run benchmarks/code/fetch.py")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def load_problems() -> list[Problem]:
    problems: list[Problem] = []

    base = {row["task_id"]: row for row in _read("humaneval_base")}
    for row in _read("humaneval_plus"):
        task_id = row["task_id"]
        problems.append(Problem(
            problem_id=task_id,
            benchmark="humaneval",
            entry_point=row["entry_point"],
            spec=row["prompt"],
            canonical_solution=row["prompt"] + row["canonical_solution"],
            _visible_test=base[task_id]["test"],
            _hidden_test=row["test"],
        ))

    for row in _read("mbpp_plus"):
        entry = execute._mbpp_entry_point(row)
        asserts = tuple(row["test_list"])
        spec = (row["prompt"].strip() + "\n\nYour code must satisfy these tests:\n"
                + "\n".join(asserts) + "\n")
        problems.append(Problem(
            problem_id=f"Mbpp/{row['task_id']}",
            benchmark="mbpp",
            entry_point=entry,
            spec=spec,
            canonical_solution="\n".join(row["test_imports"]) + "\n" + row["code"],
            _visible_test="",
            _hidden_test=row["test"],
            _test_imports=tuple(row["test_imports"]),
            _visible_asserts=asserts,
        ))

    problems.sort(key=lambda p: (p.benchmark, p.problem_id))
    return problems
