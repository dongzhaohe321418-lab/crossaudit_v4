"""number → source: the span a generator names must resolve and contain the number.

`docs/design/PROVENANCE_CHECKS.md` §2.1/§3.1/§3.4, on the right side of D155: the
generator names a locator, code opens the file and looks, and nothing anywhere
asks a model what the evidence says.

D64 — a guard is specified with the mutation that reddens it, and each docstring
below names its own (`tests/test_repair_guard.py:3-7`). One test is the
exception that proves the rule: `test_the_span_and_not_the_file_is_what_is_checked`
asserts its mutation goes **green**, because a check that still passed with the
span widened to the whole file would be checking nothing the design measured.

The fixture is the real shape §4 asks for: a RECIPE.md whose value is on L11, an
explanation.md citing `#L11`, and the wrong-line case citing `#L12`.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from crossaudit.dcl import numbers
from crossaudit.dcl.framework import ADVISORY, BLOCKER, run_checks

#: L11 holds the values; L12 is a neighbouring line of the same file that does
#: not. Both numbers are in the file, so a file-scoped check cannot tell them
#: apart — which is the whole point of §6's 27.7% / 0.0% measurement.
RECIPE = "\n".join([
    "# Synthesis recipe",                       # L1
    "",                                         # L2
    "## Reagents",                              # L3
    "- barium carbonate",                       # L4
    "- titanium dioxide",                       # L5
    "",                                         # L6
    "## Steps",                                 # L7
    "1. Grind the powders under ethanol.",      # L8
    "2. Dry at 80 °C overnight.",               # L9
    "",                                         # L10
    "3. Calcine at 950 °C for 1 hour.",         # L11
    "4. Cool to 25 °C in the furnace.",         # L12
    "",                                         # L13
]) + "\n"

RECIPE_PATH = "work/synthesis/RECIPE.md"
DRAFT_PATH = "work/explanation.md"


def draft(rows: list[dict], prose: str = "Calcined at 950 °C for 1 h.") -> bytes:
    body = json.dumps(rows, ensure_ascii=False)
    return (f"# Explanation\n\n{prose}\n\n"
            f"```crossaudit-numbers\n{body}\n```\n").encode()


def row(value="950", unit="°C", at="#L3", src=f"{RECIPE_PATH}#L11") -> dict:
    return {"v": value, "u": unit, "at": at, "src": src}


def increment(*rows: dict, recipe: str = RECIPE) -> dict[str, bytes]:
    return {RECIPE_PATH: recipe.encode(), DRAFT_PATH: draft(list(rows))}


def findings(files: dict[str, bytes]):
    return run_checks(files, ["number_source"]).findings


# ------------------------------------------------------------- the seven (1/7)
def test_a_locator_naming_the_wrong_line_is_a_blocker():
    """MUTATION (§4 row 1): change `#L11` to `#L12`, where the value lives on
    L11. The check must raise CA-NUM-002 — and the finding must not name the
    rule id in its own words, because the activity stream shows the observation
    (ACTIVITY_STREAM.md rule 12, PROVENANCE_CHECKS.md §7)."""
    good = findings(increment(row(src=f"{RECIPE_PATH}#L11")))
    assert good == [], "the annotation that names the right line must pass"

    bad = findings(increment(row(src=f"{RECIPE_PATH}#L12")))
    assert len(bad) == 1
    f = bad[0]
    assert f.severity == BLOCKER and f.rule == "CA-NUM-002"
    assert f.artifact == DRAFT_PATH
    assert f.observation == (
        'line 3 names work/synthesis/RECIPE.md:12 — "950 °C" is not on that line')
    assert "CA-NUM" not in f.observation and "number_source" not in f.observation


# ------------------------------------------------------------- the seven (2/7)
def test_the_unit_synonym_table_is_load_bearing(monkeypatch):
    """MUTATION (§4 row 2): delete the unit-synonym table. The `hours`/`h`
    fixture reddens — the draft writes "1 h" where L11 says "1 hour", the right
    line, and the annotation becomes a spurious non-overridable blocker.

    §6 measured this as 8 of 373 traceable numbers (2.1%), over the >2% kill
    condition on its own, which is why the table is code and not a footnote."""
    hours = row(value="1", unit="h", src=f"{RECIPE_PATH}#L11")
    assert findings(increment(hours)) == []

    monkeypatch.setattr(numbers, "SYNONYMS", {})
    reddened = findings(increment(hours))
    assert [f.rule for f in reddened] == ["CA-NUM-002"]


# ------------------------------------------------------------- the seven (3/7)
def test_the_span_and_not_the_file_is_what_is_checked(monkeypatch):
    """MUTATION (§4 row 3): widen the span check to the whole file. The
    wrong-line fixture goes **GREEN**, and this test asserts that green.

    It is the only guard here that proves something by passing. §6 measured a
    wrong *file* containing the claimed pair 27.7% of the time (596/2150) and a
    wrong *line* 0.0% (0/1825); if the check still blocked with `_span` widened,
    the span would not be what is doing the work and the whole contract could
    have named files. The fixture cites L12, which holds "25 °C" and not the
    pair; the pair is on L11, elsewhere in the same file. Span-scoped that is a
    blocker, file-scoped it is a pass, and the difference between those two
    readings is the entire contract."""
    wrong_line = increment(row(src=f"{RECIPE_PATH}#L12"))
    assert [f.rule for f in findings(wrong_line)] == ["CA-NUM-002"]

    monkeypatch.setattr(numbers, "_span",
                        lambda text, start, end: text)          # the mutation
    assert findings(wrong_line) == [], (
        "with the span widened to the whole file the wrong line passes; that is "
        "the coincidence rate the span scoping exists to remove")


# ------------------------------------------------------------- the seven (4/7)
def test_a_locator_that_does_not_resolve_is_a_blocker():
    """MUTATION (§3.1): drop the existence half — stop requiring that the path
    be a key of `files` and that the line range be inside it. Each fixture here
    then stops raising CA-NUM-001: the unresolvable path reaches the mapping
    lookup and raises `KeyError` out of `run_checks` rather than reporting, and
    the out-of-range and non-span cases pass. Both are the same defect — a
    citation to a location nobody committed stops being a finding.

    CA-NUM-001 is 'the location is not there'; CA-NUM-002 is 'the location is
    there and the number is not'. Keeping them apart is what lets the stream say
    which of the two happened without printing either id."""
    absent = findings(increment(row(src="work/synthesis/MISSING.md#L11")))
    assert [(f.severity, f.rule) for f in absent] == [(BLOCKER, "CA-NUM-001")]
    assert "not in the audited scope" in absent[0].observation

    past_end = findings(increment(row(src=f"{RECIPE_PATH}#L99")))
    assert [f.rule for f in past_end] == ["CA-NUM-001"]
    assert "ends at line" in past_end[0].observation

    not_a_span = findings(increment(row(src=RECIPE_PATH)))
    assert [f.rule for f in not_a_span] == ["CA-NUM-001"]
    assert "not a line in a file" in not_a_span[0].observation


# ------------------------------------------------------------- the seven (5/7)
def test_uncited_is_advisory_and_an_unannotated_number_is_nothing():
    """MUTATION (§3.4): make `uncited` a blocker, or start reporting numbers
    that carry no annotation row. Either reddens this test, and either would be
    the product refusing to state a well-known constant — 13.3% of real draft
    numbers (57/430) are melting points and ionic radii that occur in no source.

    `uncited` is the generator declining to name a location: a fact about the
    annotation, never a claim about the world. And these checks enforce DECLARED
    provenance, not coverage, so a document with no fence passes vacuously
    (A4's shipped rule, `dcl/provenance.py:19-20`)."""
    result = run_checks(increment(row(src="uncited")), ["number_source"])
    assert result.hard_failures == 0
    assert [(f.severity, f.rule) for f in result.findings] == [(ADVISORY, "CA-NUM-003")]

    vacuous = {RECIPE_PATH: RECIPE.encode(),
               DRAFT_PATH: "# Explanation\n\nCalcined at 950 °C for 1 h.\n".encode()}
    assert run_checks(vacuous, ["number_source"]).findings == []


# ------------------------------------------------------------- the seven (6/7)
def test_the_science_and_research_profiles_name_the_check():
    """MUTATION (§4 row 7): remove `number_source` from either profile. This
    test reddens by name, and the check silently stops running for every project
    that asked for it by profile rather than by list.

    `general` must stay untouched: the light default is the positioning, and a
    memo has no numbers to trace."""
    from crossaudit.dcl.profiles import PROFILES, resolve

    assert resolve("science") == ["schema", "units", "convergence", "provenance",
                                  "number_source"]
    assert resolve("research") == ["parseable", "declared", "internal", "complete",
                                   "source_provenance", "number_source"]
    assert "number_source" not in PROFILES["general"]


# ------------------------------------------------------------- the seven (7/7)
def test_a_science_project_citing_a_nonexistent_input_is_blocked():
    """MUTATION (§1): remove the existence loop at the head of `check_provenance`.
    A science project whose metadata.yml names a missing input and whose
    results.json cites it passes — membership alone asserts that the source is an
    exact MEMBER of the inputs list and never opens the file, so a name that
    names nothing satisfies a check called provenance.

    It lives in `check_provenance` rather than in the neutral pack's `declared`,
    which was the first attempt and was wrong: `check_declared` reads every
    YAML's `sources`, `requires` and `depends_on` as filenames too, so bringing
    it into `science` turned `sources: [doi:10.1234/x]` and
    `requires: [python>=3.11]` into non-overridable blockers on correct work.
    `inputs` is the one key `check_schema` already defines as `path@revision`,
    which is why existence is a fact there and a guess everywhere else."""
    from crossaudit.dcl.profiles import resolve

    meta = b"code_version: v3\ninputs:\n  - data/runs.csv@v3\n"
    results = json.dumps({
        "quantities": [{"name": "yield", "value": 0.42, "unit": "1",
                        "source": "data/runs.csv@v3"}],
        "convergence": {"converged": True}}).encode()
    absent_input = {"experiments/e1/metadata.yml": meta,
                    "experiments/e1/results.json": results}

    blocked = run_checks(absent_input, resolve("science"))
    assert [(f.severity, f.rule) for f in blocked.findings] == [(BLOCKER, "CA-DATA-003")]
    assert "not in the audited scope" in blocked.findings[0].observation

    # The same project with the input actually committed passes, so the guard is
    # the missing file and not the revision suffix — `path@revision` inputs must
    # keep working, which is the whole reason this is scoped to `inputs`.
    present = dict(absent_input, **{"experiments/e1/data/runs.csv": b"yield\n0.42\n"})
    assert run_checks(present, resolve("science")).hard_failures == 0

    # And the keys that are NOT filenames stay out of it: legitimate science
    # metadata must not become a blocker for naming a DOI or a version range.
    legitimate = dict(present, **{"experiments/e1/metadata.yml":
                                  meta + b"sources:\n  - doi:10.1234/example\n"
                                         b"requires:\n  - python>=3.11\n"})
    assert run_checks(legitimate, resolve("science")).findings == []


# ------------------------------------------------------- the rest of the shape
def test_a_span_range_and_a_pinned_sha_both_resolve():
    """MUTATION: ignore the declared sha. A range citation and a byte-pinned one
    both stop meaning anything, and an annotation survives the file changing
    underneath it."""
    import hashlib

    assert findings(increment(row(src=f"{RECIPE_PATH}#L9-L12"))) == []

    sha = hashlib.sha256(RECIPE.encode()).hexdigest()
    assert findings(increment(row(src=f"{RECIPE_PATH}@{sha}#L11"))) == []
    assert findings(increment(row(src=f"{RECIPE_PATH}@{sha[:12]}#L11"))) == []

    stale = findings(increment(row(src=f"{RECIPE_PATH}@{'0' * 12}#L11")))
    assert [f.rule for f in stale] == ["CA-NUM-001"]
    assert "not the ones the annotation pinned" in stale[0].observation


def test_a_computed_locator_is_still_resolved_and_still_read():
    """MUTATION: pass `computed:` through unverified. Every blocker in this
    module becomes evadable by four characters of prefix.

    §3.1 defers `computed:` to §3.2, but only for the CAUSAL half — whether a
    script produced the value is figure_code's question. That the named span
    holds it is this check's, and it is answerable today."""
    ok = findings(increment(row(src=f"computed:{RECIPE_PATH}#L11")))
    assert ok == []
    bad = findings(increment(row(src=f"computed:{RECIPE_PATH}#L12")))
    assert [f.rule for f in bad] == ["CA-NUM-002"]


def test_a_governed_locator_is_advisory_because_the_bytes_are_not_kept():
    """MUTATION: pass a `governed:` locator in silence. The check then reports
    'verified' over evidence it never read.

    §1.2: the broker copies only a tool's declared `evidence_fields` into the
    ledger and `web_fetch`'s text is not among them, so no code in this project
    can re-read a fetched source. Saying so is honest; passing quietly is not."""
    result = run_checks(increment(row(src='governed:' + 'a' * 64 + '#"950 °C"')),
                        ["number_source"])
    assert result.hard_failures == 0
    assert [(f.severity, f.rule) for f in result.findings] == [(ADVISORY, "CA-NUM-003")]
    assert "does not keep" in result.findings[0].observation


@pytest.mark.parametrize("body", [
    "not valid json",
    '{"v": "950"}',
    '[{"v": "950", "u": "°C"}]',
    '["950 °C at RECIPE.md#L11"]',
])
def test_a_malformed_annotation_block_is_a_blocker(body):
    """MUTATION: skip a row whose shape is wrong instead of blocking on it. A
    generator that emits `[{"v": "950"}]` for every number then satisfies the
    check while naming nothing at all — the silent-pass failure §5.4 names."""
    files = {RECIPE_PATH: RECIPE.encode(),
             DRAFT_PATH: f"# E\n\n950 °C\n\n```crossaudit-numbers\n{body}\n```\n".encode()}
    out = findings(files)
    assert out and all(f.severity == BLOCKER and f.rule == "CA-NUM-001" for f in out)


def test_a_span_locator_relative_to_the_annotating_file_resolves():
    """MUTATION: resolve only exact keys. An artefact citing a sibling by its
    own directory's name is blocked for naming the file correctly."""
    assert findings(increment(row(src="synthesis/RECIPE.md#L11"))) == []


def test_a_results_source_may_name_a_span_and_old_values_keep_passing():
    """MUTATION (§2.1): drop the `#` fragment strip in `check_provenance`. Every
    `path@revision#L14` source becomes CA-DATA-003 for not being an exact member
    of the inputs list, and the widening stops being additive.

    Both directions are asserted, because 'additive' is a claim about the values
    already committed, not only about the new ones."""
    meta = b"code_version: v3\ninputs:\n  - runs.csv@v3\n"
    csv = b"yield\n0.42\n"

    def project(source: str) -> dict[str, bytes]:
        return {"experiments/e1/metadata.yml": meta,
                "experiments/e1/runs.csv": csv,
                "experiments/e1/results.json": json.dumps({
                    "quantities": [{"name": "yield", "value": 0.42, "unit": "1",
                                    "source": source}],
                    "convergence": {"converged": True}}).encode()}

    assert run_checks(project("runs.csv@v3"), ["provenance"]).findings == []
    assert run_checks(project("runs.csv@v3#L2"), ["provenance"]).findings == []
    assert run_checks(project("runs.csv@v3#L2-L4"), ["provenance"]).findings == []

    undeclared = run_checks(project("other.csv@v3#L2"), ["provenance"])
    assert [f.rule for f in undeclared.findings] == ["CA-DATA-003"]


def test_the_check_is_registered_with_a_contract_and_wants_no_context():
    """MUTATION: register it with `wants_context=True`. The runner then calls it
    `fn(files, ctx)` and every caller that builds no context has to be widened —
    a kernel edit this check does not need, because it reads committed bytes and
    nothing about the run."""
    from crossaudit.dcl.framework import _WANTS_CONTEXT, available, contracts

    assert "number_source" in available()
    assert _WANTS_CONTEXT["number_source"] is False
    contract = contracts(["number_source"])["number_source"]
    assert "span" in contract and "never coverage" in contract
    assert "correct" in contract          # it says out loud what it does not do


NUMBERS_SKILL = "skills/provenance-numbers.md"
SOURCES_SKILL = "skills/provenance-sources.md"


def test_a_project_whose_checks_read_an_annotation_ships_the_skill_that_asks_for_one():
    """MUTATION (§5.4): stop writing the skill when the check list contains one
    of the annotation checks. `number_source` and `source_provenance` both read
    a block the GENERATOR emits, and nothing in `generator.py` or the
    Constitution asks for one — so the check would pass every document while
    appearing to guard it, which is worse than not having it. `general` enables
    neither and must get no such file.

    It travels the shipped channel and no other: a committed `skills/*.md` that
    `skills.load` reads, `skills.render` puts in the generator prompt, and the
    receipt hashes — never the auditor's prompt, and never a new channel."""
    from crossaudit import skills as skills_mod
    from crossaudit.scaffold import (GENERAL_CHECKS, SCIENCE_CHECKS,
                                     annotation_skill_tree)
    from crossaudit.dcl.profiles import PROFILES

    assert annotation_skill_tree(GENERAL_CHECKS) == {}
    for checks in (SCIENCE_CHECKS, PROFILES["science"], PROFILES["research"]):
        assert NUMBERS_SKILL in annotation_skill_tree(checks)

    body = annotation_skill_tree(SCIENCE_CHECKS)[NUMBERS_SKILL]
    # It tells the generator to transcribe and to locate. It must never ask it
    # to assess (D155).
    assert "```crossaudit-numbers" in body
    assert "uncited" in body and "#L11" in body
    assert "you name a location, you never say what is at it" in body.lower()
    # And it says the unit is compared whole, because a half-transcribed
    # compound unit is now a blocker and the generator has to be told.
    assert "in full" in body and "°C/min" in body

    # It is a legal skill: front matter parses, size is inside the bound, and it
    # renders into the generator block rather than anywhere else.
    skill = skills_mod._parse(body, "provenance-numbers", NUMBERS_SKILL)
    assert len(body.encode()) < skills_mod.MAX_SKILL_BYTES
    assert "crossaudit-numbers" in skills_mod.render([skill])

    # It carries NO `applies_to`, and that is the fix and not an oversight. A
    # round that has written nothing yet selects skills against `cfg.scope_dirs`
    # (`cli/build.py:794`), which is `["experiments"]` — a bare directory name
    # that matches neither `experiments/` nor `work/`, so a freshly scaffolded
    # project's FIRST generation carried no provenance instruction at all and
    # every document passed `number_source` vacuously.
    assert skill.applies_to == ()
    for touched in (["experiments"], ["work"], [], ["experiments/demo/x.md"]):
        assert skills_mod.select([skill], touched) == [skill], touched


@pytest.mark.parametrize("checks,files", [
    (["number_source"], [NUMBERS_SKILL]),
    (["source_provenance"], [SOURCES_SKILL]),
    (["parseable", "declared", "internal", "complete", "source_provenance",
      "number_source"], [NUMBERS_SKILL, SOURCES_SKILL]),
])
def test_the_skill_only_instructs_for_checks_the_project_actually_runs(checks, files):
    """MUTATION: ship one combined file for either check.

    A project configured with only `source_provenance` was handed the whole
    number-annotation contract for a fence nothing would ever read — guidance
    describing a check the project does not have, and output the generator pays
    for every round. One FILE per check, so each can also be gated later."""
    from crossaudit.scaffold import annotation_skill_tree

    assert sorted(annotation_skill_tree(checks)) == sorted(files)
    for path, body in annotation_skill_tree(checks).items():
        assert ("```crossaudit-numbers" in body) is (path == NUMBERS_SKILL)
        assert ("```crossaudit-sources" in body) is (path == SOURCES_SKILL)
        assert "you name a location, you never say what is at it" in body.lower()


def test_a_retained_skill_stops_being_delivered_when_its_check_is_turned_off():
    """MUTATION: drop `requires_check` from the template, or drop the `checks=`
    argument at `cli/build.py:794`.

    Composition happens once, at scaffold time. Turn `number_source` off a month
    later and the committed file is still in `skills/`, still selected, still in
    every generator prompt — describing a fence nothing will read and charging
    for it every round. The gate has to be read on every selection, so it lives
    in the file's own front matter and `skills.select` honours it.

    `checks=None` still selects everything: a person's own hand-written skill
    has no `requires_check`, and an unknown answer must never remove guidance."""
    from crossaudit import skills as skills_mod
    from crossaudit.scaffold import annotation_skill_tree

    tree = annotation_skill_tree(["number_source", "source_provenance"])
    house = [skills_mod._parse(body, path.rsplit("/", 1)[-1][:-3], path)
             for path, body in sorted(tree.items())]
    assert [s.requires_check for s in house] == [("number_source",),
                                                 ("source_provenance",)]

    def names(checks):
        return sorted(s.name for s in skills_mod.select(house, ["src"], checks=checks))

    assert names(["number_source", "source_provenance"]) == ["provenance-numbers",
                                                             "provenance-sources"]
    assert names(["source_provenance"]) == ["provenance-sources"]
    assert names(["parseable"]) == []
    assert names(None) == ["provenance-numbers", "provenance-sources"]

    # A skill a person wrote has no gate and is never dropped by one.
    mine = skills_mod._parse("# house style\n", "house", "skills/house.md")
    assert skills_mod.select([mine], ["src"], checks=[]) == [mine]


# ------------------------------------------------- the review's five, and more
@pytest.mark.parametrize("span,v,u,expected,why", [
    # The five the independent review reproduced against the first commit.
    ("-5 °C",              "-5",  "°C",    [],             "a signed value is a value"),
    ("-5 °C",              "5",   "°C",    ["CA-NUM-002"], "minus five is not five"),
    ("9007199254740992 g", "9007199254740993", "g",
                                           ["CA-NUM-002"], "two integers 2**53 apart"),
    ("5  °C",              "5",   "°C",    [],             "two spaces is whitespace"),
    ("5 mg/mL",            "5",   "mg/mL", [],             "a compound unit is a unit"),
    # The neighbourhood around them, so the fix is a rule and not five patches.
    ("9007199254740992 g", "9007199254740992", "g", [],    "and the true one passes"),
    ("5 °C",          "5",   "°C",    [],             "a non-breaking space"),
    ("5°C",                "5",   "°C",    [],             "no space at all"),
    ("5 m·s^-1",           "5",   "m·s^-1", [],            "a middle-dot compound"),
    ("5 cm-1",             "5",   "cm-1",  [],             "a hyphen exponent"),
    ("5 cm⁻¹",             "5",   "cm⁻¹",  [],             "a superscript exponent"),
    ("+5 g",               "5",   "g",     [],             "a leading plus is dropped"),
    ("0.50 m",             "0.5", "m",     [],             "trailing zeros are dropped"),
    ("05 m",               "5",   "m",     [],             "leading zeros are dropped"),
    ("1,000 rpm",          "1000", "rpm",  [],             "a grouped thousand"),
    ("1,000 rpm",          "1",   "",      ["CA-NUM-002"], "and one is not a thousand"),
    ("cool to 25–106 °C",  "106", "°C",    [],             "an en-dash range"),
    ("range 5-10 m",       "10",  "m",     [],             "a hyphen range"),
    ("1 hour",             "1",   "hours", [],             "the synonym table, raw"),
    ("10 wt % Ni",         "10",  "wt%",   [],             "the split percent"),
    ("5 mm",               "5",   "m",     ["CA-NUM-002"], "a prefix is not the unit"),
    ("5 °C",               "5",   "K",     ["CA-NUM-002"], "a different unit"),
    ("50 °C",              "5",   "°C",    ["CA-NUM-002"], "a substring is not a value"),
])
def test_the_pair_comparison_is_literal_in_both_directions(span, v, u, expected, why):
    """MUTATION: revert `normalise_number` to `float`, drop the sign from
    `_NUMBER`, allow only one space before the unit, or take a single unit
    reading. Each brings back one row of this table.

    Two failure directions, and the table asserts both, because a check that
    only avoided one of them would be worse than none: a BLOCKER on a correct
    transcription is non-overridable damage to correct work, and a PASS on a
    different number is the check saying it verified something it did not."""
    files = {RECIPE_PATH: (span + "\n").encode(),
             DRAFT_PATH: draft([row(value=v, unit=u, src=f"{RECIPE_PATH}#L1")])}
    assert [f.rule for f in findings(files)] == expected, why


def test_a_results_source_span_is_verified_by_this_check_and_not_by_provenance():
    """MUTATION: restore `numbers.py`'s skip of `results.json`, or widen
    `check_provenance` to open the file.

    §2.1 widens a quantity's `source` to `path@revision#L14`, and the review
    found that after the widening NOBODY looked at the line: `check_provenance`
    decides membership and never opens a file — that is its entire contract, and
    changing it would put a second span implementation in a second module that
    then has to agree with this one. So the fragment is verified here, where the
    span logic already lives, with `wants_context=False` intact because this
    reads committed bytes and nothing about the run."""
    meta = b"code_version: v3\ninputs:\n  - runs.csv@v3\n"
    csv = b"run,yield\n1,0.42\n2,0.51\n"

    def project(source: str) -> dict[str, bytes]:
        return {"experiments/e1/metadata.yml": meta,
                "experiments/e1/runs.csv": csv,
                "experiments/e1/results.json": json.dumps({
                    "quantities": [{"name": "yield", "value": 0.42, "unit": "",
                                    "source": source}],
                    "convergence": {"converged": True}}).encode()}

    # `provenance` alone answers membership and says nothing about the line.
    assert run_checks(project("runs.csv@v3#L2"), ["provenance"]).findings == []
    assert run_checks(project("runs.csv@v3#L3"), ["provenance"]).findings == []

    # `number_source` is what opens the file, and both profiles carry the pair.
    assert run_checks(project("runs.csv@v3#L2"), ["number_source"]).findings == []
    wrong = run_checks(project("runs.csv@v3#L3"), ["number_source"])
    assert [f.rule for f in wrong.findings] == ["CA-NUM-002"]
    assert wrong.findings[0].observation.startswith("quantities[0] names runs.csv:3")
    past = run_checks(project("runs.csv@v3#L99"), ["number_source"])
    assert [f.rule for f in past.findings] == ["CA-NUM-001"]

    # A source with no fragment is the world before the widening, untouched.
    assert run_checks(project("runs.csv@v3"), ["number_source"]).findings == []
    from crossaudit.dcl.profiles import PROFILES
    assert {"provenance", "number_source"} <= set(PROFILES["science"])


@pytest.mark.parametrize("locator,note", [
    ("runs.csv@v3", "the shape every existing project already wrote"),
    ("runs.csv@v3#L2", "the widened shape"),
    ("runs.csv@v3#L2-L4", "the widened shape, as a range"),
])
def test_provenance_accepts_only_a_line_fragment_and_nothing_else(locator, note):
    """MUTATION: go back to `src.partition('#')`. `runs.csv@v3#garbage`,
    `runs.csv@v3#`, `runs.csv@v3#other@evil` and `runs.csv@v3#L999` all blocked
    with CA-DATA-003 before the widening and silently passed after it, and a
    committed file legitimately named `runs#raw.csv` — declared and cited
    exactly — started blocking because its source became `runs`.

    The order is the fix: exact membership on the WHOLE string first, then a
    fragment only if that failed, and only `#L<digits>[-L<digits>]` anchored to
    the end."""
    meta = b"code_version: v3\ninputs:\n  - runs.csv@v3\n"
    files = {"experiments/e1/metadata.yml": meta,
             "experiments/e1/runs.csv": b"run,yield\n1,0.42\n2,0.51\n3,0.6\n4,0.7\n",
             "experiments/e1/results.json": json.dumps({
                 "quantities": [{"name": "y", "value": 0.42, "unit": "",
                                 "source": locator}],
                 "convergence": {"converged": True}}).encode()}
    assert run_checks(files, ["provenance"]).findings == [], note


@pytest.mark.parametrize("locator", [
    "runs.csv@v3#garbage", "runs.csv@v3#", "runs.csv@v3#other@evil",
    "runs.csv@v3#L2extra", "runs.csv@v3#l2", "runs.csv#L2",
])
def test_anything_that_is_not_a_line_fragment_still_fails_membership(locator):
    """The other half of the same mutation: these blocked before the widening
    and must still block."""
    meta = b"code_version: v3\ninputs:\n  - runs.csv@v3\n"
    files = {"experiments/e1/metadata.yml": meta,
             "experiments/e1/runs.csv": b"run,yield\n1,0.42\n",
             "experiments/e1/results.json": json.dumps({
                 "quantities": [{"name": "y", "value": 0.42, "unit": "",
                                 "source": locator}],
                 "convergence": {"converged": True}}).encode()}
    assert [f.rule for f in run_checks(files, ["provenance"]).findings] == ["CA-DATA-003"]


def test_a_file_whose_name_contains_a_hash_keeps_passing():
    """MUTATION: strip at the first `#` instead of at an anchored line fragment.
    A committed `runs#raw.csv`, declared and cited byte-for-byte, becomes
    CA-DATA-003 for a source of `runs` — a backward-compatibility break invented
    by the widening, on a filename that was always legal."""
    files = {"experiments/e1/metadata.yml": b"code_version: v3\ninputs:\n  - runs#raw.csv@v3\n",
             "experiments/e1/runs#raw.csv": b"run,yield\n1,0.42\n",
             "experiments/e1/results.json": json.dumps({
                 "quantities": [{"name": "y", "value": 0.42, "unit": "",
                                 "source": "runs#raw.csv@v3"}],
                 "convergence": {"converged": True}}).encode()}
    assert run_checks(files, ["provenance"]).findings == []


# --------------------------------------------- malformed input never escapes
def test_a_malformed_annotation_becomes_a_finding_and_never_an_exception():
    """MUTATION: restore `\\d+` in `_LINE`, or catch only `JSONDecodeError`.

    `int()` refuses a string of more than 4300 digits, so `#L` followed by five
    thousand digits and a JSON integer of five thousand digits both raised an
    uncaught `ValueError` out of `run_checks` — the deterministic layer, which
    runs before any model and decides the verdict, crashing on text a generator
    can emit. A malformed annotation is a finding; it is never an exception."""
    huge = "9" * 5000
    for body in (json.dumps([{"v": "1", "u": "", "at": "#L3",
                              "src": f"{RECIPE_PATH}#L{huge}"}]),
                 '[{"v": ' + huge + ', "u": "", "at": "#L3", '
                 f'"src": "{RECIPE_PATH}#L1"}}]'):
        files = {RECIPE_PATH: RECIPE.encode(),
                 DRAFT_PATH: f"# E\n\n```crossaudit-numbers\n{body}\n```\n".encode()}
        out = findings(files)
        assert out and all(f.rule == "CA-NUM-001" for f in out)


def test_an_unclosed_annotation_block_is_a_finding_not_silence():
    """MUTATION: drop the `_FENCE_OPEN` count. A block that was opened and never
    closed reads as 'this document annotated nothing' and passes vacuously —
    indistinguishable from a document that never annotated, which is exactly the
    silent-pass §5.4 says any slice shipping these checks must not have."""
    unclosed = (f"# E\n\n```crossaudit-numbers\n"
                f'[{{"v": "950", "u": "°C", "at": "#L3", "src": "{RECIPE_PATH}#L11"}}]\n')
    out = findings({RECIPE_PATH: RECIPE.encode(), DRAFT_PATH: unclosed.encode()})
    assert [f.rule for f in out] == ["CA-NUM-001"]
    assert "opened and never closed" in out[0].observation


def test_a_row_that_omits_a_field_cannot_opt_out_of_the_check():
    """MUTATION: go back to `row.get("u", "")`. A row with no `u` was read as
    unitless, so a generator could skip the unit half of the comparison by not
    writing the key — the contract has four fields, and a row with three is not
    a row this check can verify.

    A JSON number for `v` or `u` is still accepted: writing `"v": 950` is a
    transcription, not a judgment, and refusing it would be a non-overridable
    blocker on a well-formed annotation."""
    no_unit = {"v": "950", "at": "#L3", "src": f"{RECIPE_PATH}#L11"}
    out = findings({RECIPE_PATH: RECIPE.encode(), DRAFT_PATH: draft([no_unit])})
    assert [f.rule for f in out] == ["CA-NUM-001"]
    assert "is missing u" in out[0].observation

    numeric = {"v": 950, "u": "°C", "at": "#L3", "src": f"{RECIPE_PATH}#L11"}
    assert findings({RECIPE_PATH: RECIPE.encode(),
                     DRAFT_PATH: draft([numeric])}) == []

    nested = {"v": {"n": 950}, "u": "°C", "at": "#L3", "src": f"{RECIPE_PATH}#L11"}
    bad = findings({RECIPE_PATH: RECIPE.encode(), DRAFT_PATH: draft([nested])})
    assert [f.rule for f in bad] == ["CA-NUM-001"]
    assert "non-text v" in bad[0].observation


def test_a_fresh_science_project_carries_the_skill_in_its_first_prompt(
        tmp_path, monkeypatch):
    """MUTATION: put `applies_to` back on the shipped skill, or stop writing it
    at scaffold time.

    This is the end of the delivery path, asserted end to end because the middle
    of it is where the review found the break. A newly scaffolded project has no
    work yet, so `cli/build.py:794` selects skills against `cfg.scope_dirs` —
    the bare string `"experiments"`, which matches neither `experiments/` nor
    `work/`. Zero skills were selected, the first generation carried no
    instruction to annotate, and `number_source` then passed every document
    vacuously: a check that cannot fire, wearing the name of one that can.

    The assertion is on the rendered generator prompt, not on the file, because
    a committed file nobody reads is exactly the failure being guarded."""
    from crossaudit import generator, skills as skills_mod
    from crossaudit.config import load
    from crossaudit.console import projects

    monkeypatch.delenv("CROSSAUDIT_AUDITOR_KEY", raising=False)
    root = Path(projects.create_project(
        tmp_path,
        {"name": "lab", "description": "Numbers need units and sources.",
         "max_rounds": 3, "auditor_vendor": "openai", "auditor_model": "gpt-5.6-sol",
         "generator_vendor": "anthropic", "generator_model": "claude-sonnet-4-6",
         "github": False, "project_type": "science"},
        lambda *_: None)["root"])
    cfg = load(root / "crossaudit.yml")
    assert "number_source" in cfg.checks

    # Committed, so the receipt binds it and `verify` can re-derive the round.
    assert (root / NUMBERS_SKILL).is_file()
    tracked = subprocess.run(["git", "ls-files", NUMBERS_SKILL], cwd=root,
                             capture_output=True, text=True, check=True).stdout
    assert tracked.strip() == NUMBERS_SKILL

    # The selection `cli/build.py` makes on round 1, when nothing is written yet
    # — including the live check gate it passes.
    house = skills_mod.load(root)
    in_force = skills_mod.select(house, [] or cfg.scope_dirs, checks=cfg.checks)
    assert [s.name for s in in_force] == ["provenance-numbers"]
    assert skills_mod.select(house, cfg.scope_dirs, checks=["parseable"]) == []

    prompt = generator.build_prompt(
        task="write the increment", constitution="# rules\n", current={},
        skills=skills_mod.render(in_force), allowed_dirs=cfg.scope_dirs)
    assert "```crossaudit-numbers" in prompt
    assert "you name a location, you never say what is at it" in prompt.lower()
    # And it arrives as guidance, never as law.
    assert "HOUSE SKILLS" in prompt


# ------------------------------------------- the second review's two root causes
@pytest.mark.parametrize("span,v,u,expected,why", [
    # Round two's regressions, and the sign and compound cases behind them.
    ("1e3 K",   "1e3",  "g",     ["CA-NUM-002"], "the substring fallback ignored the unit"),
    ("1e3 K",   "1e3",  "K",     [],             "and the same pair is a match"),
    ("1e3 K",   "1000", "K",     [],             "exponent and decimal are one number"),
    ("1000 K",  "1e3",  "K",     [],             "in both directions"),
    ("−5 °C",   "-5",   "°C",    [],             "U+2212 MINUS SIGN is a minus"),
    ("−5 °C",   "5",    "°C",    ["CA-NUM-002"], "and minus five is still not five"),
    ("5 mg/mL", "5",    "mg",    ["CA-NUM-002"], "a prefix of a compound unit"),
    ("5 cm-1",  "5",    "cm",    ["CA-NUM-002"], "a prefix of an exponent unit"),
    ("5\u2003°C", "5",  "°C",    [],             "U+2003 EM SPACE"),
    ("5\u202f°C", "5",  "°C",    [],             "U+202F NARROW NO-BREAK SPACE"),
    ("5\u00a0°C", "5",  "°C",    [],             "U+00A0 NO-BREAK SPACE"),
    ("0.42 1",  "0.42", "1",     [],             "a dimensionless numeric unit"),
    ("5 m2",    "5",    "m2",    [],             "an exponent written as a digit"),
    ("about 950", "~950", "°C",  ["CA-NUM-001"], "a value that is not a number"),
    ("about 950", "9-50", "",    ["CA-NUM-001"], "nor is a range"),
])
def test_the_matcher_after_the_second_review(span, v, u, expected, why):
    """MUTATION: restore the substring fallback at the foot of `contains_pair`,
    drop U+2212 from `_NUMBER`, hand-list the whitespace characters instead of
    using `\\s`, or take a non-maximal unit reading. Each brings back one row.

    The fallback is the one that mattered most. A value that failed decimal
    validation fell through to `value in span` and **ignored the unit entirely**,
    so source `1e3 K` satisfied an annotation of `1e3` with unit `g`: the check
    reporting that it had verified a literal pair while accepting a different
    quantity. There is no fallback now — a value that does not normalise is
    CA-NUM-001 — and normalisation is complete enough that legitimate forms do
    not reach that path."""
    files = {RECIPE_PATH: (span + "\n").encode(),
             DRAFT_PATH: draft([row(value=v, unit=u, src=f"{RECIPE_PATH}#L1")])}
    assert [f.rule for f in findings(files)] == expected, why


def test_precision_survives_the_json_parse():
    """MUTATION: parse the fence with a plain `json.loads`.

    Comparing canonical decimal strings buys nothing if the literal was already
    rounded through a double on the way in: `9007199254740993.0` arrives as
    9007199254740992.0 and matches a span that says 9007199254740992. The fence
    and `results.json` are both parsed with `parse_float=str, parse_int=str`, so
    the transcription reaches the comparison as the characters that were
    written."""
    body = ('[{"v": 9007199254740993.0, "u": "g", "at": "#L3", '
            f'"src": "{RECIPE_PATH}#L1"}}]')
    files = {RECIPE_PATH: b"9007199254740992 g\n",
             DRAFT_PATH: f"# E\n\n```crossaudit-numbers\n{body}\n```\n".encode()}
    assert [f.rule for f in findings(files)] == ["CA-NUM-002"]

    exact = body.replace("9007199254740993.0", "9007199254740992.0")
    files[DRAFT_PATH] = f"# E\n\n```crossaudit-numbers\n{exact}\n```\n".encode()
    assert findings(files) == []


@pytest.mark.parametrize("value,unit", [
    (None, "K"), ({"a": 1}, "K"), ([1], "K"), (True, "K"),
    (0.42, {"a": 1}), (0.42, [1]), (0.42, None),
])
def test_a_quantity_this_check_cannot_read_may_not_carry_a_span(value, unit):
    """MUTATION: skip an unreadable value or unit "reported by units", and drop
    the `is_number_shape` gate on the fragment strip in `check_provenance`.

    `check_units` tests that `unit` and `source` are TRUTHY and has never looked
    at `value`. Trusting it meant a quantity with a null value citing line 999
    of a two-line file passed the complete science profile with no finding at
    all — where the code before the span widening blocked it with CA-DATA-003.
    Two independent guards, because one of them believing the other is what
    opened the hole: `check_provenance` only looks past a fragment for a row
    `number_source` can actually go and read, and `number_source` reports a row
    it cannot read rather than skipping it."""
    from crossaudit.dcl.profiles import resolve

    q = {"name": "y", "source": "runs.csv@v3#L999"}
    if value is not None or unit is None:
        q["value"] = value
    q["unit"] = unit
    files = {"experiments/e1/metadata.yml": b"code_version: v3\ninputs:\n  - runs.csv@v3\n",
             "experiments/e1/runs.csv": b"run,y\n1,0.42\n",
             "experiments/e1/results.json": json.dumps(
                 {"quantities": [q], "convergence": {"converged": True}}).encode()}
    result = run_checks(files, resolve("science"))
    assert result.hard_failures >= 1
    assert {"CA-DATA-003", "CA-NUM-001"} <= {f.rule for f in result.findings}


def test_every_file_the_builtin_checks_read_is_a_file_this_one_reads():
    """MUTATION: match the exact basename `results.json` again.

    `builtin._results_files` accepts any path ENDING in `results.json`, so
    `myresults.json` was a file `check_provenance` widened for and
    `number_source` never opened — the compensation missing for exactly the
    files the other check had accepted. One helper, in `dcl/quantities.py`,
    used by both."""
    from crossaudit.dcl.builtin import _results_files
    from crossaudit.dcl.quantities import results_files

    files = {"experiments/e1/metadata.yml": b"code_version: v3\ninputs:\n  - runs.csv@v3\n",
             "experiments/e1/runs.csv": b"run,y\n1,0.42\n",
             "experiments/e1/myresults.json": json.dumps(
                 {"quantities": [{"name": "y", "value": 0.42, "unit": "K",
                                  "source": "runs.csv@v3#L999"}],
                  "convergence": {"converged": True}}).encode()}
    assert _results_files(files) == results_files(files) == ["experiments/e1/myresults.json"]
    assert [f.rule for f in run_checks(files, ["number_source"]).findings] == ["CA-NUM-001"]


def test_a_source_declared_verbatim_is_opaque_to_both_checks():
    """MUTATION: drop the `opaque` set in `_results_findings`.

    Whole-string precedence has to hold in both checks or they contradict each
    other. If somebody literally declares `runs.csv@v3#L999` as an input, then
    `check_provenance` accepts the source as an exact member — a revision string
    that happens to contain a `#` — and `number_source` reading a line number
    out of it would hard-block a shape the other check just approved. Base
    accepted this with only the code_version advisory, and so does head."""
    from crossaudit.dcl.profiles import resolve

    files = {"experiments/e1/metadata.yml":
                 b"code_version: v3\ninputs:\n  - runs.csv@v3#L999\n",
             "experiments/e1/runs.csv": b"run,y\n1,0.42\n",
             "experiments/e1/results.json": json.dumps(
                 {"quantities": [{"name": "y", "value": 0.42, "unit": "K",
                                  "source": "runs.csv@v3#L999"}],
                  "convergence": {"converged": True}}).encode()}
    result = run_checks(files, resolve("science"))
    assert result.hard_failures == 0
    assert [(f.severity, f.rule) for f in result.findings] == [(ADVISORY, "CA-DATA-003")]


@pytest.mark.parametrize("locator,blocks", [
    ("runs.csv@v3#L2", False),
    ("runs.csv@v3#L2\n", True),
    ("runs.csv@v3#L٢", True),
])
def test_the_fragment_is_ascii_and_at_the_absolute_end(locator, blocks):
    """MUTATION: use `$` instead of `\\Z`, or `\\d` instead of `[0-9]`.

    `$` also matches before a final newline, so `runs.csv@v3#L2\\n` was read as a
    line fragment; `\\d` matches Arabic-Indic digits, so `#L٢` was read as line
    two. Neither is a shape a transcription of committed bytes would produce,
    and both used to be CA-DATA-003."""
    files = {"experiments/e1/metadata.yml": b"code_version: v3\ninputs:\n  - runs.csv@v3\n",
             "experiments/e1/runs.csv": b"run,y\n1,0.42\n",
             "experiments/e1/results.json": json.dumps(
                 {"quantities": [{"name": "y", "value": 0.42, "unit": "",
                                  "source": locator}],
                  "convergence": {"converged": True}}).encode()}
    found = [f.rule for f in run_checks(files, ["provenance"]).findings]
    assert (found == ["CA-DATA-003"]) is blocks


@pytest.mark.parametrize("ref,blocks", [
    ("https://example.org/a@v3", False),
    ("HTTPS://example.org/a@v3", False),
    ("ftp://example.org/a@v3", False),
    ("doi:10.1234/example@v3", False),
    ("pkg:pypi/numpy@1.0", False),
    ("data/runs.csv@v3", True),
])
def test_the_existence_check_skips_by_scheme_not_by_a_lowercase_prefix(ref, blocks):
    """MUTATION: go back to `ref.startswith(("http://", "https://"))`.

    A reference that names a scheme is not a file, and the check was looking for
    `HTTPS://…`, `ftp://…`, `doi:…` and `pkg:pypi/numpy` on disk and reporting
    them missing — a non-overridable blocker on metadata that is simply not a
    path. `check_declared` keeps its own base behaviour: widening what IT skips
    would be a weakening of a check that ships in every default project."""
    meta = ("code_version: v3\ninputs:\n  - " + ref + "\n").encode()
    found = [f.rule for f in run_checks({"e/metadata.yml": meta}, ["provenance"]).findings]
    assert (found == ["CA-DATA-003"]) is blocks


def test_a_file_ending_in_an_opening_fence_is_a_finding():
    """MUTATION: require a trailing newline in `_FENCE_OPEN` again. A file whose
    last bytes are the opening fence itself produced no finding, so a truncated
    annotation was indistinguishable from a document that never annotated."""
    for tail in ("```crossaudit-numbers", "```crossaudit-numbers\n"):
        out = findings({RECIPE_PATH: RECIPE.encode(),
                        DRAFT_PATH: ("# E\n\n" + tail).encode()})
        assert [f.rule for f in out] == ["CA-NUM-001"], tail
        assert "opened and never closed" in out[0].observation


@pytest.mark.parametrize("span,v,u,expected,why", [
    ("(20°C-25°C)", "20", "°C",     [],             "a range is not one unit token"),
    ("(20°C-25°C)", "20", "°C-25",  ["CA-NUM-002"], "and its halves are not either"),
    ("99-102 kPa",  "102", "kPa",   [],             "the second half carries the unit"),
    ("99-102 kPa",  "99",  "kPa",   ["CA-NUM-002"], "the first half does not"),
    ("5 cm-1",      "5",  "cm-1",   [],             "a hyphen exponent at end of token"),
    ("5 cm-1",      "5",  "cm",     ["CA-NUM-002"], "and its prefix is still refused"),
    ("5°C/min",     "5",  "°C/min", [],             "a ramp rate is its own unit"),
    ("5°C/min",     "5",  "°C",     ["CA-NUM-002"], "a temperature is not a ramp rate"),
])
def test_a_hyphen_range_is_not_an_exponent(span, v, u, expected, why):
    """MUTATION: drop the lookahead from `_EXPONENT_TAIL`.

    Making the unit token maximal — which is what stops `5 mg/mL` satisfying
    `mg` — read `(20°C-25°C)` as the single unit `°C-25`, so a draft citing
    `20 °C` off a line stating an ambient window was blocked for transcribing it
    correctly. Measured, not hypothesised: it cost 1 of 365 on the archived
    drafts and took the Arm 1 primary rate from 1.64% to 1.92%.

    A hyphen followed by digits and then more unit is a range; a hyphen followed
    by digits and then the end of the token is an exponent. The lookahead is the
    only thing that separates them, and both halves are asserted here because
    loosening it far enough to fix the range would give `cm` back."""
    files = {RECIPE_PATH: (span + "\n").encode(),
             DRAFT_PATH: draft([row(value=v, unit=u, src=f"{RECIPE_PATH}#L1")])}
    assert [f.rule for f in findings(files)] == expected, why


# ------------------------------------- the third review: a prefix never satisfies
@pytest.mark.parametrize("span,v,u,expected,why", [
    # Round three's P1 table: the annotation is a strict PREFIX of the token.
    ("5 m-2s-1",      "5", "m",            ["CA-NUM-002"], "prefix of an exponent compound"),
    ("5 m-2s-1",      "5", "m-2s-1",       [],             "and the whole token matches"),
    ("5 m2s-1",       "5", "m",            ["CA-NUM-002"], "the same without the hyphen"),
    ("10 kg-m",       "10", "kg",          ["CA-NUM-002"], "prefix of a hyphenated unit"),
    ("10 kg-m",       "10", "kg-m",        [],             "and the whole token matches"),
    ("5 g-equivalent", "5", "g",           ["CA-NUM-002"], "prefix of a hyphenated word"),
    ("5 g-equivalent", "5", "g-equivalent", [],            "and the whole token matches"),
    ("2 h-long",      "2", "h",            ["CA-NUM-002"], "prose is not a licence for a prefix"),
    ("2 h-long",      "2", "h-long",       [],             "and the whole token matches"),
    ("3 °C-1",        "3", "°C",           ["CA-NUM-002"], "prefix of a hyphen exponent"),
    ("3 °C-1",        "3", "°C-1",         [],             "and the whole token matches"),
    ("5 m-2 s-1",     "5", "m-2",          [],             "a space ends the token"),
    # A range is split, and only where both halves are the same unit.
    ("(20°C-25°C)",   "20", "°C",          [],             "a closed-up range names one unit"),
    ("(20°C-25°C)",   "25", "°C",          [],             "from either end"),
    ("(20°C-25°C)",   "20", "°C-25°C",     [],             "the whole token is a reading too"),
    ("10 kg-2m",      "10", "kg",          ["CA-NUM-002"], "unequal halves are not a range"),
    ("99-102 kPa",    "102", "kPa",        [],             "the half that carries the unit"),
    ("99-102 kPa",    "99", "kPa",         ["CA-NUM-002"], "and the half that does not"),
    # The exponent bound refuses; it never truncates.
    ("1e10001 g",     "1e1000", "1",       ["CA-NUM-002"], "no leftover digit becomes a unit"),
    ("1e10001 g",     "1e10001", "g",      [],             "and the real pair matches"),
    ("1e100 g",       "1e100", "g",        [],             "an ordinary exponent"),
    ("1e100 g",       "1e9999999", "g",    ["CA-NUM-001"], "past the bound is refused"),
    # Extraction sees every form normalisation accepts.
    (".5 g",          ".5", "g",           [],             "a leading-dot decimal"),
    (".5 g",          "0.5", "g",          [],             "and the same number written out"),
    ("mol/(L·s): 5 mol/(L·s)", "5", "mol/(L·s)", [],       "balanced brackets stay inside"),
    ("at 5 K.",       "5", "K",            [],             "a sentence period ends the token"),
    ("950 °C, then",  "950", "°C",         [],             "so does a comma"),
])
def test_a_prefix_of_the_unit_token_never_satisfies(span, v, u, expected, why):
    """MUTATION: read the unit with a pattern that can return a shorter
    alternative, or cap the exponent inside the SPAN scanner.

    Both were the same defect wearing two hats — something shorter than what the
    source wrote was accepted as what the source wrote. `5 m-2s-1` satisfied an
    annotation of `m`, `10 kg-m` satisfied `kg`, `2 h-long` satisfied `h`; and
    `1e10001` was read as the number `1e1000` followed by the unit `1`, which
    passed 100 of 100 exponents swept from 10000 to 10099.

    The rule is now one rule and it is the same for both halves of the pair: the
    token is extracted whole, to a true boundary, and compared whole-to-whole. A
    bound is a REFUSAL (CA-NUM-001), never a truncation. The only readings that
    may be added are ones LONGER than the token — a range split and the `wt %`
    percent split — so nothing can reintroduce a prefix."""
    files = {RECIPE_PATH: (span + "\n").encode(),
             DRAFT_PATH: draft([row(value=v, unit=u, src=f"{RECIPE_PATH}#L1")])}
    assert [f.rule for f in findings(files)] == expected, why


def test_the_exponent_sweep_that_gave_a_hundred_false_passes():
    """MUTATION: put a digit cap back in `_NUMBER`.

    The review swept exponents 10000–10099 and every one of them was a false
    pass: the scanner consumed four exponent digits and handed the fifth to the
    unit reader. One case would have been a curiosity; a contiguous hundred is a
    grammar defect, so the whole range is the guard."""
    from crossaudit.dcl.numbers import contains_pair

    for exponent in range(10000, 10100):
        digits = str(exponent)
        assert not contains_pair(f"1e{exponent} g", f"1e{digits[:4]}", digits[4:]), exponent
        assert contains_pair(f"1e{exponent} g", f"1e{exponent}", "g"), exponent


@pytest.mark.parametrize("src,at,blocks", [
    (f"{RECIPE_PATH}#L11", "#L3", False),
    (f"{RECIPE_PATH}#L11\n", "#L3", True),
    (f"{RECIPE_PATH}#L١١", "#L3", True),
    (f" {RECIPE_PATH}#L11", "#L3", True),
    (f"{RECIPE_PATH}#L11", "#L3\n", True),
])
def test_a_fenced_locator_is_ascii_and_exact(src, at, blocks):
    """MUTATION: put `\\d` back in `_LINE`, or restore the `.strip()` on `src`
    and `at`.

    The ASCII/absolute-end discipline was applied to the `check_provenance`
    membership test and to nothing else, so the FENCE parser still read `#L٢`
    as line two and still discarded trailing whitespace inside a locator. A
    locator is an address; `work/x.md#L11\\n` is not the address
    `work/x.md#L11`."""
    files = {RECIPE_PATH: RECIPE.encode(),
             DRAFT_PATH: draft([{"v": "950", "u": "°C", "at": at, "src": src}])}
    assert ([f.rule for f in findings(files)] == ["CA-NUM-001"]) is blocks


def test_the_contract_discloses_what_normalisation_does_to_a_number():
    """MUTATION: go back to promising literal containment.

    The contract is the sentence a person reads to decide whether to turn the
    check on, and it is bound into the receipt. Saying "literally contains" while
    treating `1.50` and `1.5` as one number overstates it: the check cannot tell
    a reported precision from a rounded one, and a contract that hides its own
    limit is the overclaim shape this whole line exists to remove."""
    from crossaudit.dcl.framework import contracts

    contract = contracts(["number_source"])["number_source"]
    assert "1.50" in contract and "not significant" in contract
    assert "WHOLE unit token" in contract and "prefix" in contract
    assert "never coverage" in contract and "never judges whether a number is correct" in contract


# ---------------------------- the fourth review: boundaries, not an allowlist
@pytest.mark.parametrize("span,v,u,expected,why", [
    # The three P1 rows: a character the allowlist did not list ended the token.
    ("5 kg.m",   "5", "kg",      ["CA-NUM-002"], "a period inside a unit is not a boundary"),
    ("5 kg.m",   "5", "kg.m",    [],             "and the whole token matches"),
    ("5 wt %/s", "5", "wt %",    ["CA-NUM-002"], "the percent reading runs on to the boundary"),
    ("5 wt %/s", "5", "wt %/s",  [],             "and the whole token matches"),
    ("5 °Cβ",    "5", "°C",      ["CA-NUM-002"], "β is not a boundary; nothing said it was"),
    ("5 °Cβ",    "5", "°Cβ",     [],             "and the whole token matches"),
    # Characters no allowlist author would have listed, all token.
    ("5 Ω′",     "5", "Ω′",      [],             "prime and ohm"),
    ("5 m⁄s",    "5", "m⁄s",     [],             "a fraction slash"),
    ("5 H₂O",    "5", "H₂O",     [],             "a subscript"),
    ("5 Å",      "5", "Å",       [],             "angstrom"),
    ("5 Ω′",     "5", "Ω",       ["CA-NUM-002"], "and a prefix of any of them still fails"),
    # The review's ordinary-prose table: every boundary, enumerated.
    ("(5 °C)",      "5", "°C", [], "an unopened closing bracket"),
    ("5 °C, then",  "5", "°C", [], "a comma"),
    ("5 °C; then",  "5", "°C", [], "a semicolon"),
    ("5 °C: then",  "5", "°C", [], "a colon"),
    ("5 °C.",       "5", "°C", [], "a period at the end of the text"),
    ("5 °C. Then",  "5", "°C", [], "a period before a space"),
    ("5 °C!",       "5", "°C", [], "an exclamation mark — a round-3 prose regression"),
    ("5 °C?",       "5", "°C", [], "a question mark — the same"),
    ("5 °C—",       "5", "°C", [], "an em dash"),
    ("5 °C–",       "5", "°C", [], "an en dash"),
    ('"5 °C"',      "5", "°C", [], "a quotation mark"),
    ("5 °C…",       "5", "°C", [], "an ellipsis"),
    ("5 °C ± 1",    "5", "°C", [], "whitespace, as always"),
    ("5 %",         "5", "%",  [], "a bare percent"),
    ("5%",          "5", "%",  [], "and a closed-up one"),
    ("10 wt % Ni",  "10", "wt%", [], "the percent split still ends at the space"),
    ("5 mol/(L·s)", "5", "mol/(L·s)", [], "balanced brackets stay inside"),
    ("5 mol/(L·s)", "5", "mol/(L",   ["CA-NUM-002"], "and half of one does not"),
    ("at 5 K.",     "5", "K",  [], "a sentence period after a bare unit"),
    ("a 5 g-sample", "5", "g", ["CA-NUM-002"], "a hyphenated word is one token"),
    ("5 °C¹",       "5", "°C", ["CA-NUM-002"], "a superscript belongs to the token"),
    ("5 °C¹",       "5", "°C¹", [],           "so the whole thing matches"),
    # Ranges, unchanged by the inversion.
    ("(20°C-25°C)", "20", "°C", [], "a closed-up range names one unit"),
    ("(20°C-25°C)", "25", "°C", [], "from either end"),
    ("20-25 °C",    "25", "°C", [], "the half that carries the unit"),
    ("20-25 °C",    "20", "°C", ["CA-NUM-002"], "and the half that does not"),
    ("1-2 h",       "2", "h",  [], "the same for a duration"),
    ("20°C–25°C",   "20", "°C", [], "an en-dash range ends the token outright"),
])
def test_the_boundary_list_is_exhaustive_and_everything_else_is_token(
        span, v, u, expected, why):
    """MUTATION: make `_scan` an allowlist of characters permitted INSIDE a unit
    again, or drop `!`/`?`/the dashes from `_BOUNDARY`.

    An allowlist is the prefix defect in a third costume: any character its
    author did not think of ends the token, so a shorter reading satisfies a
    longer source. `5 kg.m` satisfied `kg`, `5 wt %/s` satisfied `wt %`, and
    `5 °Cβ` satisfied `°C` — all three through a `results.json` citation under
    the complete science profile with zero findings, where base blocks.

    Inverted, the failure direction inverts with it: a character nobody
    anticipated keeps the token whole, so the worst case is a blocker on a
    half-transcribed unit rather than a pass on one. The boundaries are
    enumerated here in full because the enumeration IS the contract."""
    files = {RECIPE_PATH: (span + "\n").encode(),
             DRAFT_PATH: draft([row(value=v, unit=u, src=f"{RECIPE_PATH}#L1")])}
    assert [f.rule for f in findings(files)] == expected, why


@pytest.mark.parametrize("at,blocks", [
    ("#L3", False), ("#L2-L4", False), ("#L1-L1", False),
    ("#L0", True), ("#L00", True), ("#L5-L2", True), ("#L3\n", True), ("#L٣", True),
])
def test_the_at_locator_is_validated_the_way_the_src_locator_is(at, blocks):
    """MUTATION: check `at` for syntax only, or discard its range end.

    `#L0` and `#L5-L2` were accepted — a line number that cannot exist and a
    range that runs backwards, both of which this layer refuses in the `src`
    field one line away. `at` is the address the activity stream prints back to
    a person (§7), so an address that cannot exist is a malformed row."""
    files = {RECIPE_PATH: RECIPE.encode(),
             DRAFT_PATH: draft([{"v": "950", "u": "°C", "at": at,
                                 "src": f"{RECIPE_PATH}#L11"}])}
    assert ([f.rule for f in findings(files)] == ["CA-NUM-001"]) is blocks


@pytest.mark.parametrize("source,blocks", [
    ("runs.csv@v3#L2", False),
    (" runs.csv@v3#L2", True),
    ("runs.csv@v3#L2\n", True),
    ("runs.csv@v3#L2 ", True),
])
def test_a_structured_source_holds_its_own_contract_with_no_other_check_on(
        source, blocks):
    """MUTATION: `.strip()` the structured source again.

    A whitespace-padded locator was caught only because `provenance` also runs
    in the science profile. A check that needs another check to hold its own
    contract is root cause 1 in miniature, and `checks: [number_source]` is a
    configuration a project may write."""
    files = {"experiments/e1/metadata.yml": b"code_version: v3\ninputs:\n  - runs.csv@v3\n",
             "experiments/e1/runs.csv": b"run,y\n0.42 K\n",
             "experiments/e1/results.json": json.dumps(
                 {"quantities": [{"name": "y", "value": 0.42, "unit": "K",
                                  "source": source}],
                  "convergence": {"converged": True}}).encode()}
    found = [f.rule for f in run_checks(files, ["number_source"]).findings]
    assert (found == ["CA-NUM-001"]) is blocks


def test_an_exponent_past_the_bound_is_refused_and_not_truncated():
    """MUTATION: allow six exponent digits again.

    The contract said the literal was bounded while `1e999999` passed. The cap
    is what makes "bounded" true, and it is a refusal (CA-NUM-001) rather than a
    truncation — truncation is what handed `1e10001`'s last digit to the unit
    reader."""
    files = {RECIPE_PATH: b"1e999999 g\n",
             DRAFT_PATH: draft([row(value="1e999999", unit="g", src=f"{RECIPE_PATH}#L1")])}
    assert [f.rule for f in findings(files)] == ["CA-NUM-001"]

    ok = {RECIPE_PATH: b"1e99999 g\n",
          DRAFT_PATH: draft([row(value="1e99999", unit="g", src=f"{RECIPE_PATH}#L1")])}
    assert findings(ok) == []


@pytest.mark.parametrize("span,v,u,expected,why", [
    ("10⁵ g",   "10", "",  ["CA-NUM-002"], "a superscript exponent is not read"),
    ("10⁵ g",   "10", "g", ["CA-NUM-002"], "with or without a unit"),
    ("5×10³ g", "5",  "",  ["CA-NUM-002"], "nor is a multiplication sign"),
    ("10^5 g",  "10", "",  ["CA-NUM-002"], "nor a caret"),
    ("run 5 of 12", "5", "", [],           "but a WORD after a number is not notation"),
    ("5 samples",   "5", "", [],           "and neither is a plain noun"),
    ("at 5, then",  "5", "", [],           "nor punctuation"),
    ("5 m·s^-1", "5", "m·s^-1", [],        "a caret inside a unit is untouched"),
])
def test_an_unparsed_numeric_notation_is_not_a_match_for_any_unit(
        span, v, u, expected, why):
    """DECIDED, and this is the statement the review asked for.

    `10⁵ g` and `5×10³ g` were satisfying an annotation of `10` and `5` with an
    EMPTY unit, because the scanner reads the mantissa and an empty unit asks no
    further question. The rule is: an occurrence whose number continues directly
    into notation this layer does not parse — a superscript exponent, a
    multiplication sign or a caret before a digit — is not a match for any unit,
    the empty one included. The source's number is not the number that was read,
    so no annotation of it can be verified against that line.

    The alternative the review offered — treat an empty unit as a mismatch
    whenever the source has a unit — is rejected, and the reason is measurable
    rather than aesthetic. Under a boundary scanner ANY word after a number is a
    token: `run 5 of 12` would make `of` the unit and `Sample 3 was calcined`
    would make `was` one, so that rule would block every legitimately unitless
    annotation whose number is followed by prose — most of them, on this corpus.
    This rule fires on the number's own continuation and never on what merely
    follows it, so it removes the false pass without inventing a false blocker."""
    files = {RECIPE_PATH: (span + "\n").encode(),
             DRAFT_PATH: draft([row(value=v, unit=u, src=f"{RECIPE_PATH}#L1")])}
    assert [f.rule for f in findings(files)] == expected, why


@pytest.mark.parametrize("unit,expected", [
    ("m-2",      []),
    ("m-2 s-1",  ["CA-NUM-002"]),
    ("m-2s-1",   ["CA-NUM-002"]),
    ("m-2·s-1",  ["CA-NUM-002"]),
])
def test_a_unit_containing_a_space_is_read_as_its_first_token(unit, expected):
    """MUTATION: change the shipped wording without changing this.

    This asserts BEHAVIOUR, not strings, because the previous version of this
    guard checked the instruction text and the instruction was wrong: it said
    the checker refuses the first half of `m-2 s-1`, and in fact `m-2` PASSES.
    Whitespace is a boundary, so against `5 m-2 s-1` the token is `m-2` and the
    second half is invisible to the check. That is the one place a partial unit
    satisfies, it is structural, and a documentation test could not have caught
    the contradiction because it never ran the scanner.

    The skill and the contract must now describe exactly this table."""
    files = {RECIPE_PATH: b"5 m-2 s-1\n",
             DRAFT_PATH: draft([row(value="5", unit=unit, src=f"{RECIPE_PATH}#L1")])}
    assert [f.rule for f in findings(files)] == expected


def test_the_shipped_words_say_what_the_scanner_does():
    """The other half of the pair above: the guidance and the contract have to
    describe the behaviour the table just asserted, including the two limits a
    reader would otherwise have to discover by being blocked.

    An empty unit imposes NO unit constraint, so the check can confirm a number
    is present and can never establish that it is unitless; and `*` and `>` are
    not boundaries because multiplication and comparison are notation a unit can
    contain, which costs a footnote star."""
    from crossaudit.dcl.framework import contracts
    from crossaudit.scaffold import annotation_skill_tree

    contract = contracts(["number_source"])["number_source"]
    assert "first token only" in contract and "'m-2 s-1'" in contract
    assert "EMPTY unit imposes no unit constraint" in contract.replace("an EMPTY", "EMPTY")
    assert "never establish that it is unitless" in contract
    assert "'*' and '>'" in contract
    assert contract.count("does not resolve") == 1        # and it reads once

    body = annotation_skill_tree(["number_source"])[NUMBERS_SKILL]
    assert "first token only" in body.lower() or "FIRST token only" in body
    assert "m-2s-1" in body and "uncited" in body


def test_an_empty_unit_imposes_no_constraint_and_the_contract_says_so():
    """MUTATION: make an empty unit mismatch a source that has one.

    Stated rather than assumed, because the review asked for the choice on the
    record. `5 g` annotated `5 / ""` PASSES. Under a boundary scanner any word
    after a number is a token, so the stricter rule would make `of` the unit in
    `run 5 of 12` and block most legitimately unitless annotations. The price is
    that this check can never establish that a source number is unitless, and
    the contract says that in those words."""
    for span in ("5 g", "5 samples", "run 5 of 12", "5"):
        files = {RECIPE_PATH: (span + "\n").encode(),
                 DRAFT_PATH: draft([row(value="5", unit="", src=f"{RECIPE_PATH}#L1")])}
        assert findings(files) == [], span


LEGACY_FIXTURES = Path(__file__).parent / "fixtures" / "legacy_provenance_skills"


@pytest.mark.parametrize("rendering", ["numbers.md", "sources.md", "both.md"])
def test_every_pre_split_rendering_is_recognised_and_removed(tmp_path, rendering):
    """MUTATION: prune on a substring again, or drop one rendering's digest.

    The round-3 composer could emit three files — numbers only, sources only,
    both — and the first migration matched two SUBSTRINGS instead. That deleted
    a hand-written policy whose only crime was quoting the fence name in an
    example, and it missed the source-only rendering entirely, which carries no
    numeric marker at all. Ownership of a generated file is proved by its bytes.

    The fixtures here are the actual round-3 output, and asserting their digests
    against the pinned set is what keeps the set honest: if somebody edits the
    templates and recomputes the constants from the NEW ones, this reddens."""
    from crossaudit.scaffold import (LEGACY_ANNOTATION_DIGESTS,
                                     LEGACY_ANNOTATION_SKILL,
                                     prune_legacy_annotation_skill)

    body = (LEGACY_FIXTURES / rendering).read_bytes()
    assert hashlib.sha256(body).hexdigest() in LEGACY_ANNOTATION_DIGESTS

    legacy = tmp_path / LEGACY_ANNOTATION_SKILL
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_bytes(body)
    assert prune_legacy_annotation_skill(tmp_path) == [LEGACY_ANNOTATION_SKILL]
    assert not legacy.exists()


@pytest.mark.parametrize("kept", [
    # The exact file the first migration deleted.
    "Hand written custom policy\nMy example uses ```crossaudit-numbers; keep my"
    " custom advice.\n",
    "---\nrequires_check: number_source\n---\n```crossaudit-numbers\n```\n",
    "# my own house style\n",
    "```crossaudit-sources\n[]\n```\n",
])
def test_a_file_this_scaffold_did_not_write_is_never_removed(tmp_path, kept):
    """MUTATION: match on "mentions the fence name" instead of on the bytes.

    A person may write anything at `skills/provenance.md`, including a document
    that quotes the fence it is teaching. Deleting that is data loss caused by a
    migration for a file that shipped to nobody."""
    from crossaudit.scaffold import (LEGACY_ANNOTATION_SKILL,
                                     prune_legacy_annotation_skill)

    legacy = tmp_path / LEGACY_ANNOTATION_SKILL
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text(kept)
    assert prune_legacy_annotation_skill(tmp_path) == []
    assert legacy.read_text() == kept


def test_nothing_to_prune_is_not_an_error(tmp_path):
    from crossaudit.scaffold import prune_legacy_annotation_skill

    assert prune_legacy_annotation_skill(tmp_path) == []
    assert prune_legacy_annotation_skill(None) == []


def test_the_removal_is_staged_so_the_setup_commit_records_it(tmp_path, monkeypatch):
    """MUTATION: drop the return value at either creation path.

    Both callers discarded it, so the file was deleted from the working tree
    and left alive in the commit — a migration that runs and does not stick.
    `commit_setup` stages exactly `owned`, so a removal has to travel there.

    The `git add` guard is asserted too: a pathspec that neither exists nor is
    tracked makes `git add` fail, which would turn setup into a denial over an
    untracked leftover."""
    from crossaudit.cli import wizard
    from crossaudit.console import projects
    from crossaudit.scaffold import LEGACY_ANNOTATION_SKILL

    monkeypatch.delenv("CROSSAUDIT_AUDITOR_KEY", raising=False)
    root = Path(projects.create_project(
        tmp_path,
        {"name": "lab", "description": "Numbers need units and sources.",
         "max_rounds": 3, "auditor_vendor": "openai", "auditor_model": "gpt-5.6-sol",
         "generator_vendor": "anthropic", "generator_model": "claude-sonnet-4-6",
         "github": False, "project_type": "science"},
        lambda *_: None)["root"])

    legacy = root / LEGACY_ANNOTATION_SKILL
    legacy.write_bytes((LEGACY_FIXTURES / "both.md").read_bytes())
    subprocess.run(["git", "add", "--", LEGACY_ANNOTATION_SKILL], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t.invalid",
                    "commit", "-qm", "legacy skill"], cwd=root, check=True)

    from crossaudit.scaffold import prune_legacy_annotation_skill
    removed = wizard.tracked_paths(root, prune_legacy_annotation_skill(root))
    assert removed == [LEGACY_ANNOTATION_SKILL]
    wizard.commit_setup(root, removed)
    assert not legacy.exists()
    listed = subprocess.run(["git", "ls-files", "--", LEGACY_ANNOTATION_SKILL],
                            cwd=root, capture_output=True, text=True, check=True)
    assert listed.stdout.strip() == "", "the deletion was not committed"
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=root,
                           capture_output=True, text=True, check=True)
    assert dirty.stdout.strip() == "", dirty.stdout

    # An UNTRACKED leftover is removed but never staged, because `git add` on a
    # pathspec that neither exists nor is tracked is a fatal error.
    legacy.write_bytes((LEGACY_FIXTURES / "both.md").read_bytes())
    assert wizard.tracked_paths(root, prune_legacy_annotation_skill(root)) == []
    assert not legacy.exists()


# ------------------ the fifth review: signed notation, and quotes as boundaries
@pytest.mark.parametrize("span,v,u,expected,why", [
    # The review's four rows, plus the structured pair it also reported.
    ("10⁻⁵ g",   "10", "",   ["CA-NUM-002"], "a superscript MINUS exponent"),
    ("10⁺⁵ g",   "10", "",   ["CA-NUM-002"], "a superscript PLUS exponent"),
    ("5×-10³ g", "5",  "",   ["CA-NUM-002"], "an ASCII sign after the operator"),
    ("5^−3 g",   "5",  "",   ["CA-NUM-002"], "a U+2212 sign after the caret"),
    ("10⁻⁵ g",   "10", "⁻⁵", ["CA-NUM-002"], "and naming the exponent as a unit"),
    ("10⁺⁵ g",   "10", "⁺⁵", ["CA-NUM-002"], "in either sign"),
    # The neighbourhood, so this is a rule and not four patches.
    ("5⋅10³ g",  "5", "",  ["CA-NUM-002"], "a dot operator"),
    ("5·10³ g",  "5", "",  ["CA-NUM-002"], "a middle dot operator"),
    ("5*-10³ g", "5", "",  ["CA-NUM-002"], "a signed asterisk product"),
    ("5x±10³ g", "5", "",  ["CA-NUM-002"], "a plus-minus operand"),
    ("10⁵ g",    "10", "", ["CA-NUM-002"], "the unsigned case still blocks"),
    # And nothing that is merely prose or a legitimate unit is caught by it.
    ("run 5 of 12", "5", "",       [], "a word after a number is not notation"),
    ("5 g",         "5", "",       [], "nor is a unit"),
    ("5 m·s^-1",    "5", "m·s^-1", [], "a caret INSIDE a unit is untouched"),
    ("5 cm-1",      "5", "cm-1",   [], "and so is a hyphen exponent"),
    ("5 x 3 grid",  "5", "",       [], "a spaced multiplication sign is prose"),
])
def test_signed_notation_is_unparsed_notation_too(span, v, u, expected, why):
    """MUTATION: drop the sign alternatives from `_UNPARSED`.

    The rule was "a number that continues into notation this layer cannot read
    is not a match for any unit", and it enumerated superscript DIGITS only. So
    `10⁻⁵ g` still satisfied an annotation of `10` with an empty unit, and
    `10 / "⁻⁵"` satisfied it through a `results.json` citation under the
    complete science profile, where base blocks. The sign is part of the
    notation; leaving it out left the same hole one character to the left."""
    files = {RECIPE_PATH: (span + "\n").encode(),
             DRAFT_PATH: draft([row(value=v, unit=u, src=f"{RECIPE_PATH}#L1")])}
    assert [f.rule for f in findings(files)] == expected, why


def test_signed_notation_blocks_through_a_structured_citation_too():
    """The same rule where the review found it: a `results.json` quantity, under
    every check the science profile resolves to."""
    from crossaudit.dcl.profiles import resolve

    files = {"experiments/e1/metadata.yml": b"code_version: v3\ninputs:\n  - runs.csv@v3\n",
             "experiments/e1/runs.csv": "run,y\n10⁻⁵ g\n".encode(),
             "experiments/e1/results.json": json.dumps(
                 {"quantities": [{"name": "y", "value": 10, "unit": "⁻⁵",
                                  "source": "runs.csv@v3#L2"}],
                  "convergence": {"converged": True}}).encode()}
    assert [f.rule for f in run_checks(files, resolve("science")).findings] == ["CA-NUM-002"]


@pytest.mark.parametrize("mark", list("‘’‚‛“”„‟‹›«»†‡§¶"))
def test_quotes_and_footnote_marks_end_a_unit_token(mark):
    """MUTATION: take the typographic quotes or the note marks back out.

    `5 °C”` and `5 °C’s` blocked on `°C` — a word processor's closing quote and
    an English possessive turning into unit text — and `5 °C†` and `5 °C§`
    blocked wherever a footnote is marked. Inverting the scanner made the
    boundary list the whole contract, so a boundary left out of it is a blocker
    on ordinary prose. Every direction of single and double quote is listed by
    codepoint, because several are indistinguishable from ASCII by eye."""
    files = {RECIPE_PATH: f"5 °C{mark}\n".encode(),
             DRAFT_PATH: draft([row(value="5", unit="°C", src=f"{RECIPE_PATH}#L1")])}
    assert findings(files) == [], mark


@pytest.mark.parametrize("mark", ["*", ">"])
def test_multiplication_and_comparison_stay_inside_the_token(mark):
    """The deliberate other side, stated in the contract: `*` and `>` are
    notation a unit can contain, so they are NOT boundaries. The cost is that a
    footnote star reads as unit text, and that cost is named rather than traded
    away — making them boundaries would let a shortened unit satisfy a longer
    source, which is the defect this whole line has been closing."""
    files = {RECIPE_PATH: f"5 °C{mark}\n".encode(),
             DRAFT_PATH: draft([row(value="5", unit="°C", src=f"{RECIPE_PATH}#L1")])}
    assert [f.rule for f in findings(files)] == ["CA-NUM-002"]
    whole = {RECIPE_PATH: f"5 °C{mark}\n".encode(),
             DRAFT_PATH: draft([row(value="5", unit=f"°C{mark}", src=f"{RECIPE_PATH}#L1")])}
    assert findings(whole) == []


@pytest.mark.parametrize("at,blocks", [
    ("#L3", False), ("#L2-L4", False),
    ("#L1-L1000000", True), ("#L999", True), ("#L0", True), ("#L5-L2", True),
])
def test_the_at_locator_must_be_inside_the_artefact_that_carries_it(at, blocks):
    """MUTATION: drop the `end > lines` clause from `_at_span`.

    `at` was validated for syntax, then for positivity and order, and each time
    it stayed one clause behind `src`: `#L1-L1000000` passed on an eight-line
    draft while the identical `src` was CA-NUM-001. Two locator parsers in one
    module must not disagree about what a line number is."""
    files = {RECIPE_PATH: RECIPE.encode(),
             DRAFT_PATH: draft([{"v": "950", "u": "°C", "at": at,
                                 "src": f"{RECIPE_PATH}#L11"}])}
    assert ([f.rule for f in findings(files)] == ["CA-NUM-001"]) is blocks


@pytest.mark.parametrize("value,canonical", [
    ("1e000005", "1e5"), ("1e5", "1e5"), ("1e0000000000005", "1e5"),
    ("1e-000005", "1e-5"), ("1e99999", "1e99999"),
    ("1e100000", None), ("1e0999999", None),
])
def test_the_exponent_cap_is_on_magnitude_not_on_padding(value, canonical):
    """MUTATION: count exponent characters again.

    `1e000005` was CA-NUM-001 and `1e99999` was fine — the padding deciding, not
    the number. A cap that a literal can trip by being written verbosely is not
    a cap on anything."""
    from crossaudit.dcl.quantities import normalise_number

    assert normalise_number(value) == canonical
