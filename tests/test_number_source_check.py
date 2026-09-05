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

import json

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
    have named files. RECIPE.md contains "950 °C" on both L11 and L12, so the
    file-scoped reading cannot separate a careful citation from a careless one."""
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
    be a key of `files` and that the line range be inside it. All three fixtures
    here go green, and a citation to a file nobody committed passes.

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

    assert resolve("science") == ["schema", "units", "convergence", "declared",
                                  "provenance", "number_source"]
    assert resolve("research") == ["parseable", "declared", "internal", "complete",
                                   "source_provenance", "number_source"]
    assert "number_source" not in PROFILES["general"]


# ------------------------------------------------------------- the seven (7/7)
def test_a_science_project_citing_a_nonexistent_input_is_blocked():
    """MUTATION (§1): remove `declared` from the `science` profile. A science
    project whose metadata.yml names a missing input and whose results.json
    cites it passes — `provenance` asserts only that the source is an exact
    MEMBER of the inputs list and never opens the file, and no shipped profile
    held both halves.

    Adding `declared` is safe for revisioned inputs because it strips the
    revision before testing existence: `ref = str(item).split("@")[0].strip()`
    (`dcl/neutral.py:92`). A `path@revision` input is looked up as `path`, so
    turning it on does not flag every science project ever written."""
    from crossaudit.dcl.profiles import resolve

    meta = b"code_version: v3\ninputs:\n  - data/runs.csv@v3\n"
    results = json.dumps({
        "quantities": [{"name": "yield", "value": 0.42, "unit": "1",
                        "source": "data/runs.csv@v3"}],
        "convergence": {"converged": True}}).encode()
    absent_input = {"experiments/e1/metadata.yml": meta,
                    "experiments/e1/results.json": results}

    blocked = run_checks(absent_input, resolve("science"))
    assert blocked.hard_failures >= 1
    assert [f.rule for f in blocked.findings if f.severity == BLOCKER] == ["CA-FILE-002"]

    # The same project with the input actually committed passes, so the guard is
    # the missing file and not the revision suffix.
    present = dict(absent_input, **{"experiments/e1/data/runs.csv": b"yield\n0.42\n"})
    assert run_checks(present, resolve("science")).hard_failures == 0


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


def test_a_project_whose_checks_read_an_annotation_ships_the_skill_that_asks_for_one():
    """MUTATION (§5.4): stop writing `skills/provenance.md` when the check list
    contains one of the annotation checks. `number_source` and
    `source_provenance` both read a block the GENERATOR emits, and nothing in
    `generator.py` or the Constitution asks for one — so the check would pass
    every document while appearing to guard it, which is worse than not having
    it. `general` enables neither and must get no such file.

    It travels the shipped channel and no other: a committed `skills/*.md` that
    `skills.load` reads, `skills.render` puts in the generator prompt, and the
    receipt hashes — never the auditor's prompt, and never a new channel."""
    from crossaudit import skills as skills_mod
    from crossaudit.scaffold import (GENERAL_CHECKS, PROVENANCE_SKILL_PATH,
                                     SCIENCE_CHECKS, annotation_skill_tree)
    from crossaudit.dcl.profiles import PROFILES

    assert annotation_skill_tree(GENERAL_CHECKS) == {}
    for checks in (SCIENCE_CHECKS, PROFILES["science"], PROFILES["research"]):
        assert PROVENANCE_SKILL_PATH in annotation_skill_tree(checks)

    body = annotation_skill_tree(SCIENCE_CHECKS)[PROVENANCE_SKILL_PATH]
    # It names both fences, and it tells the generator to transcribe and to
    # locate. It must never ask it to assess (D155).
    assert "```crossaudit-numbers" in body and "```crossaudit-sources" in body
    assert "uncited" in body and "#L11" in body
    assert "you name a location, you never say what is at it" in body.lower()

    # And it is a legal skill: front matter parses, size is inside the bound,
    # and it renders into the generator block rather than anywhere else.
    skill = skills_mod._parse(body, "provenance", PROVENANCE_SKILL_PATH)
    assert skill.applies_to == ("work/", "experiments/")
    assert len(body.encode()) < skills_mod.MAX_SKILL_BYTES
    assert "crossaudit-numbers" in skills_mod.render([skill])
