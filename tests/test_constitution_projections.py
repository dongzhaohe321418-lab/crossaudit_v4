"""One committed rulebook, two projections — and what each side is given.

The measurement behind this file is `benchmarks/expertlongbench/RESULTS-2.md`:
rules that name what the work is graded on took the auditor's round-one recall
against CLEAR ground truth from 2.0% to 15.5%, and took the generator's first
draft from 14.7 to 3.3 CLEAR F1, because `run_loop` handed one file to both.
So the artefact stays one file and the two readers stop getting the same text.
"""
from __future__ import annotations

import hashlib

import pytest

from crossaudit import constitution as const_mod
from crossaudit import generator as gen
from crossaudit.auditor import prompt as audit_prompt
from crossaudit.auditor.validate import known_rules
from crossaudit.constitution import (BRIEF_MARKER, Draft, Rule,
                                     brief_projection, criteria_projection,
                                     is_brief_rule, projection_digests,
                                     split_rules)
from crossaudit.scaffold import read as template

RULES = (
    "# Constitution — demo\n\nSome preamble.\n\n---\n\n"
    "### CA-TASK-001\n**BLOCKER.** satisfy the committed task, one file\n\n"
    "### CA-SHAPE-001\n**BLOCKER.** the report opens with a one-paragraph summary\n"
    f"{BRIEF_MARKER}\n\n"
    "### CA-GRADE-001\n**BLOCKER.** the anneal temperature is justified against the "
    "precursor decomposition onset\n\n"
    "### CA-GRADE-002\n**ADVISORY.** the atmosphere choice cites a source\n\n"
    "---\n\n<!-- editing guidance for the human -->\n"
)


def test_the_auditor_projection_is_the_committed_bytes():
    """Identity, and deliberately so: the auditor's view does not move under
    this change, and it still sees only what was committed."""
    assert criteria_projection(RULES) is RULES
    for name in ("AUDIT_RULES.md", "GENERAL_AUDIT_RULES.md"):
        body = template(name)
        assert criteria_projection(body) == body


def test_the_brief_carries_the_shape_rules_and_not_the_criteria():
    brief = brief_projection(RULES)
    assert "satisfy the committed task, one file" in brief       # reserved shape
    assert "one-paragraph summary" in brief                      # marked shape
    assert "decomposition onset" not in brief                    # graded
    assert "cites a source" not in brief                         # graded
    assert "CA-GRADE-001 (BLOCKER)" in brief                     # named, not spelled
    assert "CA-GRADE-002 (ADVISORY)" in brief


def test_the_brief_adds_nothing_the_rulebook_does_not_contain():
    """A projection, not an author. Every rule id in the brief is a rule id in
    the file, so nothing the writer is told escapes the artefact the receipt
    binds."""
    brief = brief_projection(RULES)
    assert known_rules(RULES) >= known_rules(brief)
    for extra in ("CA-INVENTED-001", "you must", "temperature"):
        if extra not in RULES:
            assert extra not in brief


def test_a_rulebook_of_pure_criteria_leaks_none_of_them():
    """The arm that made the audit work: six BLOCKERs transcribed from the
    task's grading rubric. The writer learns they exist and nothing more."""
    rubric = "\n\n".join(
        f"### CA-RUBRIC-{i:03d}\n**BLOCKER.** grading criterion number {i} in "
        f"exhaustive detail" for i in range(1, 7))
    brief = brief_projection(rubric)
    assert "exhaustive detail" not in brief
    assert const_mod.BRIEF_NO_SHAPE_RULES in brief
    for i in range(1, 7):
        assert f"CA-RUBRIC-{i:03d} (BLOCKER)" in brief


def test_the_generator_prompt_carries_the_brief_and_the_auditor_prompt_the_rules():
    """The split is real at both seams, in the same round, from one file."""
    writer = gen.build_prompt(task="write it", constitution=RULES, current={})
    reviewer, _bounded, _sha = audit_prompt.build(RULES, "c" * 40,
                                                  {"findings": []}, {})
    assert "decomposition onset" in reviewer and "decomposition onset" not in writer
    assert "one-paragraph summary" in reviewer and "one-paragraph summary" in writer


def test_the_projection_is_taken_inside_build_prompt_not_at_the_call_site():
    """A caller that hands `generate` the whole rulebook still cannot hand the
    writer the criteria: the choke point is one function, and there is no
    keyword that opts out of it."""
    seen = {}

    class _Reply:
        text = ("SUMMARY: s\n<<<CROSSAUDIT-OUTPUT-FILE path=\"work/a.md\">>>\nx\n"
                "<<<END-CROSSAUDIT-OUTPUT-FILE>>>\nNOTES:\n")

    def complete(system, prompt):
        seen["prompt"] = prompt
        return _Reply()

    gen.generate(task="t", constitution=RULES, current={}, complete=complete,
                 allowed_dirs=["work"])
    assert "decomposition onset" not in seen["prompt"]


def test_an_unparseable_rulebook_degrades_to_no_criteria_not_to_all_of_them():
    """If the heading style ever drifts, the brief carries the file as its own
    preamble rather than silently classifying criteria as shape. Loud, and on
    the side that does not poison the draft."""
    drifted = "## CA-TASK-001\nnot a rule heading this reader knows\n"
    assert split_rules(drifted) == (drifted, [])
    assert "not a rule heading" in brief_projection(drifted)


def test_marking_and_the_reserved_rule():
    assert is_brief_rule("CA-TASK-001", "### CA-TASK-001\nanything\n")
    assert is_brief_rule("CA-X-001", f"### CA-X-001\nbody\n{BRIEF_MARKER}\n")
    assert not is_brief_rule("CA-X-001", "### CA-X-001\nbody\n")


def test_a_drafted_rule_round_trips_its_audience_through_the_file():
    """The marker survives render -> read, so a human editing the file and the
    drafting model agree on which rules the writer sees."""
    draft = Draft(project_summary="p", domain="d", rules=[
        Rule(id="CA-FORM-001", severity="BLOCKER", title="one file",
             criterion="exactly one Markdown file", brief=True),
        Rule(id="CA-GRADE-003", severity="BLOCKER", title="justified",
             criterion="every number is justified against its source"),
    ])
    rendered = draft.render("demo")
    assert BRIEF_MARKER in rendered
    brief = brief_projection(rendered)
    assert "exactly one Markdown file" in brief
    assert "justified against its source" not in brief
    assert "CA-GRADE-003 (BLOCKER)" in brief


def test_from_json_reads_the_audience_and_defaults_to_the_reviewer():
    draft = Draft.from_json({
        "project_summary": "p", "domain": "d",
        "rules": [{"id": "CA-AA-001", "severity": "BLOCKER", "title": "t",
                   "criterion": "c", "brief": True},
                  {"id": "CA-BB-001", "severity": "BLOCKER", "title": "t",
                   "criterion": "c"}]})
    assert draft.rules[0].brief is True
    assert draft.rules[1].brief is False


def test_the_digests_are_a_pure_function_of_the_committed_bytes():
    digests = projection_digests(RULES)
    assert digests["auditor"] == {
        "name": const_mod.AUDIENCE_AUDITOR,
        "sha256": hashlib.sha256(RULES.encode("utf-8")).hexdigest()}
    assert digests["generator"]["name"] == const_mod.AUDIENCE_GENERATOR
    assert digests["generator"]["sha256"] == hashlib.sha256(
        brief_projection(RULES).encode("utf-8")).hexdigest()
    assert digests["generator"]["sha256"] != digests["auditor"]["sha256"]
    assert projection_digests(RULES) == digests          # deterministic


def test_the_shipped_templates_give_the_writer_shape_and_not_criteria():
    general = brief_projection(template("GENERAL_AUDIT_RULES.md"))
    assert "CA-CONTENT-001 (BLOCKER)" in general
    assert "unresolved placeholder" not in general       # a graded criterion
    assert "locate,\nopen, and use" in general           # marked as shape

    science = brief_projection(template("AUDIT_RULES.md"))
    assert "`results.json` (with a `quantities` list)" in science
    assert "carries a unit and a\nsource" not in science  # CA-DATA-001, graded
    assert "CA-DATA-001 (BLOCKER)" in science
