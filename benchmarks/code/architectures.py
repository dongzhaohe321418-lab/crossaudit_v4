"""The audit architectures this study varies. The model is held fixed; the structure is not.

Study 1 ran one architecture: **holistic** — the auditor is shown the increment and the
rules and returns whatever findings it judges worth raising. That is
``crossaudit.auditor.run.run_audit``, and this module does not reimplement it.

What this module adds is the two architectures that study 1 did not have:

**decomposed** — two phases, mirroring the CLEAR scorer's shape (map per rubric item, then
judge per item) rather than the holistic auditor's:

1. *decompose*: from the task specification alone, enumerate the checkable properties a
   correct implementation must have — signature and contract, edge cases, boundary
   conditions, error handling, stated complexity. One call per **problem**, not per
   instance: the property list is a function of the problem, so every candidate solution to
   the same problem is checked against the identical list.
2. *check*: one call per property, each seeing that property and nothing about the others.
   Aggregate: any property judged VIOLATED is a BLOCKER.

**two-stage** — the self-vendor auditor's findings are shown to the cross-vendor model,
which returns keep/drop per finding.

## The information boundary, which is the property the study rests on

Every prompt-building function here takes **plain strings**, never a
:class:`corpus.Problem`. The hidden suite lives on ``Problem._hidden_test``; a function
that never receives the object cannot reach the attribute, by construction rather than by
discipline. ``tests/test_architectures.py`` proves it two ways: a sentinel test that no
hidden byte appears in any prompt, and a reachability test that runs the whole path against
a problem whose ``_hidden_test`` raises on access.

The decomposer is deliberately shown **less** than the holistic auditor: the specification
only, not the candidate solution. A property list derived from the candidate could be
shaped by the candidate's own mistakes, and a list derived from the hidden tests would make
the recall number meaningless. Neither can happen here.
"""

from __future__ import annotations

import json
import re

#: Cap on properties per problem. Bounds cost and stops a runaway enumeration from making
#: one problem dominate an arm's spend. Preregistered before any arm ran.
MAX_PROPERTIES = 8

VERDICTS = ("SATISFIED", "VIOLATED", "UNCLEAR")


# ---------------------------------------------------------------------------------
# phase 1 — decompose the specification into checkable properties
# ---------------------------------------------------------------------------------

DECOMPOSE_SYSTEM = (
    "You are a meticulous software reviewer preparing a checklist.\n\n"
    "You will be given the specification of a Python function — its signature, its "
    "docstring, and any examples the specification itself states. You will NOT be given "
    "any implementation, and you must not assume one.\n\n"
    "Enumerate the distinct, checkable properties that ANY correct implementation of this "
    "specification must have. Cover, where the specification implies them:\n"
    "- the signature and return contract (types, shape, what is returned when)\n"
    "- the core behaviour the specification describes, split into separable claims\n"
    "- edge cases the specification implies (empty input, single element, duplicates, "
    "zero, negatives, equal elements)\n"
    "- boundary conditions (inclusive vs exclusive bounds, off-by-one, first and last "
    "element, exact ties)\n"
    "- error and special-value handling the specification states or implies\n"
    "- any complexity, ordering, stability or in-place claim the specification makes\n\n"
    "Rules:\n"
    f"- Emit at most {MAX_PROPERTIES} properties. Fewer is correct for a simple "
    "specification; do not pad.\n"
    "- Each property must be independently checkable by reading an implementation, and "
    "must be stated as a concrete requirement, not a topic.\n"
    "- Derive every property from the given specification only. Do not invent "
    "requirements the specification does not state or imply.\n"
    "- Do not restate the same requirement twice in different words.\n\n"
    "Output format: a single JSON array and nothing else. Each element is an object with "
    "keys \"category\" (one of: contract, behaviour, edge_case, boundary, error_handling, "
    "complexity) and \"property\" (one sentence stating the requirement)."
)

DECOMPOSE_USER = "Specification:\n\n```python\n{spec}\n```"


def decompose_prompt(spec: str) -> tuple[str, str]:
    """Build the decomposition prompt from the specification **string**.

    Takes ``str``, not ``Problem``: the hidden suite is not merely omitted from this
    prompt, it is unreachable from this function.
    """
    if not isinstance(spec, str):
        raise TypeError("decompose_prompt takes the specification as a string, so that "
                        "the hidden suite is unreachable from this code path")
    return DECOMPOSE_SYSTEM, DECOMPOSE_USER.format(spec=spec)


_JSON_ARRAY = re.compile(r"\[.*\]", re.S)


def parse_properties(text: str) -> list[dict]:
    """Parse the decomposer's reply. A malformed reply yields no properties, not a crash.

    An instance whose decomposition failed is recorded with ``properties: 0`` and counts as
    not flagged, which is the conservative direction: it can only lower this arm's recall.
    """
    match = _JSON_ARRAY.search(text or "")
    if not match:
        return []
    try:
        raw = json.loads(match.group(0))
    except (ValueError, TypeError):
        return []
    if not isinstance(raw, list):
        return []
    out: list[dict] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, dict):
            continue
        prop = str(item.get("property", "")).strip()
        if not prop or prop.lower() in seen:
            continue
        seen.add(prop.lower())
        category = str(item.get("category", "")).strip() or "behaviour"
        out.append({"category": category, "property": prop})
        if len(out) >= MAX_PROPERTIES:
            break
    return out


# ---------------------------------------------------------------------------------
# phase 2 — check one property, alone
# ---------------------------------------------------------------------------------

CHECK_SYSTEM = (
    "You are a meticulous code reviewer checking ONE property of an implementation.\n\n"
    "You will be given a function's specification, a candidate implementation, the test "
    "suite the developer can run, and exactly one property that a correct implementation "
    "must have.\n\n"
    "Decide whether THIS implementation satisfies THIS property. Consider only this "
    "property; other defects are not your concern here and must not change your verdict.\n\n"
    "Reason concretely: trace the implementation on the inputs this property is about, "
    "including the awkward ones. The developer's test suite already passes, so a defect "
    "that exists is one the suite does not cover — do not treat a passing suite as "
    "evidence the property holds.\n\n"
    "Answer VIOLATED only if you can name a specific input or condition on which this "
    "implementation does the wrong thing for this property. If the property holds, answer "
    "SATISFIED. If the specification is genuinely ambiguous about this property, answer "
    "UNCLEAR. Style, naming, and efficiency are never VIOLATED unless the property itself "
    "is about them.\n\n"
    "Output format: a single JSON object and nothing else, with keys \"verdict\" (one of "
    "SATISFIED, VIOLATED, UNCLEAR) and \"evidence\" (one or two sentences; if VIOLATED, "
    "name the input and what the implementation returns on it versus what it must return)."
)

CHECK_USER = (
    "Specification:\n\n```python\n{spec}\n```\n\n"
    "Candidate implementation:\n\n```python\n{solution}\n```\n\n"
    "The developer's test suite (it passes):\n\n```python\n{visible_tests}\n```\n\n"
    "The single property to check:\n\n{category}: {prop}"
)


def check_prompt(spec: str, solution: str, visible_tests: str,
                 category: str, prop: str) -> tuple[str, str]:
    """Build a single-property check prompt. All parameters are strings; see the module docstring."""
    for name, value in (("spec", spec), ("solution", solution),
                        ("visible_tests", visible_tests), ("prop", prop)):
        if not isinstance(value, str):
            raise TypeError(f"check_prompt takes {name} as a string, so that the hidden "
                            f"suite is unreachable from this code path")
    return CHECK_SYSTEM, CHECK_USER.format(
        spec=spec, solution=solution, visible_tests=visible_tests,
        category=category, prop=prop)


_JSON_OBJECT = re.compile(r"\{.*\}", re.S)


def parse_check(text: str) -> dict:
    """Parse one property verdict. An unparseable reply is UNCLEAR, which does not flag."""
    match = _JSON_OBJECT.search(text or "")
    if not match:
        return {"verdict": "UNCLEAR", "evidence": "", "parsed": False}
    try:
        raw = json.loads(match.group(0))
    except (ValueError, TypeError):
        return {"verdict": "UNCLEAR", "evidence": "", "parsed": False}
    if not isinstance(raw, dict):
        return {"verdict": "UNCLEAR", "evidence": "", "parsed": False}
    verdict = str(raw.get("verdict", "")).strip().upper()
    if verdict not in VERDICTS:
        verdict = "UNCLEAR"
    return {"verdict": verdict,
            "evidence": str(raw.get("evidence", "")).strip(),
            "parsed": True}


def aggregate(checks: list[dict]) -> bool:
    """The decomposed arm's flag: any property judged VIOLATED is a BLOCKER.

    UNCLEAR does not flag. That mirrors the product, where ADVISORY never gates, and it is
    the conservative choice for this arm's false-positive rate.
    """
    return any(c.get("verdict") == "VIOLATED" for c in checks)


# ---------------------------------------------------------------------------------
# two-stage — the cross-vendor model filters the self-vendor model's findings
# ---------------------------------------------------------------------------------

FILTER_SYSTEM = (
    "You are a senior reviewer triaging findings another reviewer raised about a Python "
    "function.\n\n"
    "You will be given the specification, the implementation, the test suite the developer "
    "can run (it passes), and a numbered list of findings. For each finding, decide whether "
    "it identifies a REAL defect in this implementation with respect to the specification.\n\n"
    "Keep a finding only if you can confirm the defect yourself by tracing the code — name "
    "the input on which the implementation does the wrong thing. Drop findings that are "
    "speculative, that describe style or efficiency rather than incorrect behaviour, that "
    "restate the specification without identifying a defect, or that are simply wrong about "
    "what the code does. The developer's suite passing is not evidence a finding is wrong: "
    "a real defect here is one the suite does not cover.\n\n"
    "Output format: a single JSON array and nothing else, one object per finding IN THE "
    "GIVEN ORDER, with keys \"index\" (the finding's number), \"keep\" (true or false) and "
    "\"reason\" (one sentence)."
)

FILTER_USER = (
    "Specification:\n\n```python\n{spec}\n```\n\n"
    "Implementation:\n\n```python\n{solution}\n```\n\n"
    "The developer's test suite (it passes):\n\n```python\n{visible_tests}\n```\n\n"
    "Findings to triage:\n\n{findings}"
)


def filter_prompt(spec: str, solution: str, visible_tests: str,
                  findings: list[str]) -> tuple[str, str]:
    """Build the two-stage filter prompt. Strings only; see the module docstring."""
    for name, value in (("spec", spec), ("solution", solution),
                        ("visible_tests", visible_tests)):
        if not isinstance(value, str):
            raise TypeError(f"filter_prompt takes {name} as a string, so that the hidden "
                            f"suite is unreachable from this code path")
    listed = "\n\n".join(f"{i}. {text}" for i, text in enumerate(findings, start=1))
    return FILTER_SYSTEM, FILTER_USER.format(
        spec=spec, solution=solution, visible_tests=visible_tests, findings=listed)


def parse_filter(text: str, count: int) -> list[bool]:
    """Which findings survive. An unparseable reply keeps nothing.

    Dropping on a parse failure is the conservative direction for the filtered arm's
    recall, and it is stated in advance rather than chosen after the scores were seen.
    """
    match = _JSON_ARRAY.search(text or "")
    kept = [False] * count
    if not match:
        return kept
    try:
        raw = json.loads(match.group(0))
    except (ValueError, TypeError):
        return kept
    if not isinstance(raw, list):
        return kept
    for position, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        try:
            index = int(item.get("index", position + 1)) - 1
        except (TypeError, ValueError):
            index = position
        if 0 <= index < count:
            kept[index] = bool(item.get("keep", False))
    return kept
