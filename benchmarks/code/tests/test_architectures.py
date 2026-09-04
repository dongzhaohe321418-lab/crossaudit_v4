"""The leakage guard, plus the parsing contracts the arms depend on.

The decomposed arm's recall number means nothing if the hidden suite reached the
decomposer or the per-property checker, directly or indirectly. Two tests prove it did not:

* :func:`test_no_hidden_byte_reaches_any_prompt` — the sentinel test. A problem whose
  hidden suite is a unique string; that string appears in no prompt any architecture builds.
* :func:`test_hidden_suite_is_unreachable_from_the_decompose_path` — the structural test.
  A problem whose ``_hidden_test`` **raises on access**; the whole decompose-and-check path
  runs to completion anyway. Absence of a string can be a coincidence of one fixture.
  A path that completes when the attribute is a landmine cannot reach the attribute.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import architectures as arch  # noqa: E402
from corpus import Problem  # noqa: E402

SENTINEL = "ZZ_HIDDEN_SUITE_SENTINEL_d41d8cd98f00b204_ZZ"

SPEC = 'def add(a: int, b: int) -> int:\n    """Return the sum of a and b."""\n'
SOLUTION = "def add(a, b):\n    return a + b\n"


def _problem_with_hidden(hidden: str) -> Problem:
    return Problem(
        problem_id="Test/1", benchmark="humaneval", entry_point="add",
        spec=SPEC, canonical_solution=SOLUTION,
        _visible_test="assert add(1, 2) == 3\n", _hidden_test=hidden,
    )


class _ExplodingHidden(Problem):
    """A problem whose hidden suite is a landmine: touching it fails the test loudly.

    ``_hidden_test`` is a data descriptor on the class, so it wins over any instance
    attribute and cannot be set by the frozen dataclass ``__init__``. The fixture is
    therefore built with :func:`_arm_the_landmine`, which fills every other field directly.
    """

    @property
    def _hidden_test(self):  # type: ignore[override]
        raise AssertionError(
            "the hidden suite was accessed from a code path that must never reach it")


def _arm_the_landmine() -> "_ExplodingHidden":
    problem = object.__new__(_ExplodingHidden)
    for field, value in (
        ("problem_id", "Test/1"), ("benchmark", "humaneval"), ("entry_point", "add"),
        ("spec", SPEC), ("canonical_solution", SOLUTION),
        ("_visible_test", "assert add(1, 2) == 3\n"),
        ("_test_imports", ()), ("_visible_asserts", ()),
    ):
        object.__setattr__(problem, field, value)
    return problem


def _all_prompts_for(problem: Problem) -> list[str]:
    """Every prompt the decomposed and two-stage architectures build, as the arms build them.

    This mirrors the call sites in ``audit2.py`` exactly: the architectures receive
    ``problem.spec`` and ``problem.visible_tests_text()`` and never the problem itself.
    """
    prompts: list[str] = []
    prompts.extend(arch.decompose_prompt(problem.spec))
    prompts.extend(arch.check_prompt(
        problem.spec, SOLUTION, problem.visible_tests_text(),
        "boundary", "It must return the sum for negative operands."))
    prompts.extend(arch.filter_prompt(
        problem.spec, SOLUTION, problem.visible_tests_text(),
        ["the function ignores negative operands"]))
    return prompts


# ---------------------------------------------------------------------------------
# the leakage guard
# ---------------------------------------------------------------------------------

def test_no_hidden_byte_reaches_any_prompt():
    problem = _problem_with_hidden(f"assert add(2, 2) == 4  # {SENTINEL}\n")
    for prompt in _all_prompts_for(problem):
        assert SENTINEL not in prompt


def test_hidden_suite_is_unreachable_from_the_decompose_path():
    """The structural proof: the path completes even when the attribute detonates."""
    problem = _arm_the_landmine()
    # Sanity: the landmine is actually armed, so a passing test below means something.
    try:
        problem._hidden_test
    except AssertionError:
        pass
    else:  # pragma: no cover
        raise AssertionError("the fixture's hidden suite did not raise; the guard is inert")

    prompts = _all_prompts_for(problem)
    assert len(prompts) == 6
    assert all(isinstance(p, str) and p for p in prompts)


def test_prompt_builders_refuse_a_problem_object():
    """Passing the Problem itself is a type error, not a silent leak."""
    problem = _problem_with_hidden("assert add(2, 2) == 4\n")
    for call in (
        lambda: arch.decompose_prompt(problem),                       # type: ignore[arg-type]
        lambda: arch.check_prompt(problem, SOLUTION, "", "c", "p"),   # type: ignore[arg-type]
        lambda: arch.filter_prompt(problem, SOLUTION, "", ["x"]),     # type: ignore[arg-type]
    ):
        try:
            call()
        except TypeError:
            continue
        raise AssertionError("a prompt builder accepted a Problem; the boundary is not enforced")


def test_the_decomposer_is_not_shown_the_candidate_solution():
    """The property list must be a function of the problem, not of the candidate's mistakes."""
    unique = "def solution_specific_marker_9f2c(): pass"
    _system, user = arch.decompose_prompt(SPEC)
    assert unique not in user
    assert SOLUTION not in user


# ---------------------------------------------------------------------------------
# parsing contracts the arms depend on
# ---------------------------------------------------------------------------------

def test_parse_properties_reads_a_json_array():
    props = arch.parse_properties(
        'here you go:\n[{"category": "edge_case", "property": "empty list returns 0"},'
        ' {"category": "contract", "property": "returns an int"}]')
    assert [p["property"] for p in props] == ["empty list returns 0", "returns an int"]
    assert props[0]["category"] == "edge_case"


def test_parse_properties_deduplicates_and_caps():
    many = ",".join(f'{{"category":"behaviour","property":"p{i}"}}' for i in range(20))
    assert len(arch.parse_properties(f"[{many}]")) == arch.MAX_PROPERTIES
    dupes = '[{"category":"a","property":"same"},{"category":"b","property":"SAME"}]'
    assert len(arch.parse_properties(dupes)) == 1


def test_a_malformed_decomposition_yields_no_properties_rather_than_crashing():
    for bad in ("", "not json at all", "[oops", None):
        assert arch.parse_properties(bad) == []  # type: ignore[arg-type]


def test_parse_check_maps_verdicts_and_defaults_to_unclear():
    assert arch.parse_check('{"verdict":"VIOLATED","evidence":"add(-1,0) returns 1"}'
                            )["verdict"] == "VIOLATED"
    assert arch.parse_check('{"verdict":"satisfied","evidence":""}')["verdict"] == "SATISFIED"
    assert arch.parse_check('{"verdict":"NONSENSE"}')["verdict"] == "UNCLEAR"
    unparsed = arch.parse_check("no json here")
    assert unparsed["verdict"] == "UNCLEAR" and unparsed["parsed"] is False


def test_aggregate_flags_on_any_violation_and_never_on_unclear():
    assert arch.aggregate([{"verdict": "SATISFIED"}, {"verdict": "VIOLATED"}]) is True
    assert arch.aggregate([{"verdict": "SATISFIED"}, {"verdict": "UNCLEAR"}]) is False
    assert arch.aggregate([]) is False


def test_parse_filter_keeps_only_what_the_model_kept():
    kept = arch.parse_filter(
        '[{"index":1,"keep":true,"reason":"real"},{"index":2,"keep":false,"reason":"style"}]', 2)
    assert kept == [True, False]


def test_an_unparseable_filter_reply_keeps_nothing():
    assert arch.parse_filter("garbage", 3) == [False, False, False]
    assert arch.parse_filter("", 2) == [False, False]
