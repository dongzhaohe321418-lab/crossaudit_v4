"""What a declaration may look like, and what a check may do when it cannot read one.

Two things, both raised by the independent review of the provenance slice.

**The existence half of `provenance` (PROVENANCE_CHECKS.md §1).** `check_provenance`
asserted that a quantity's source was an exact MEMBER of `metadata.yml` `inputs`
and never opened a file, so a project could cite `data/runs.csv@v3`, list it, not
have it, and pass. The fix verifies existence for `inputs` — and ONLY `inputs`,
because that is the one key `check_schema` already defines as `path@revision`.

**`check_declared`'s shapes.** The first attempt at §1 was to add the neutral
pack's `declared` to the science profile. That check reads every YAML's
`sources`, `requires` and `depends_on` as filenames too, and it had two
pre-existing defects that the wider exposure surfaced: a scalar value was walked
character by character, and a non-string entry raised `TypeError` out of
`run_checks`. Both live in the pack every project runs by default, so they are
fixed here whether or not any profile ever widens.

D64: each guard names the mutation that reddens it.
"""
from __future__ import annotations

import json

import pytest

from crossaudit.dcl.framework import BLOCKER, run_checks
from crossaudit.dcl.neutral import check_declared

META = b"code_version: v3\ninputs:\n  - data/runs.csv@v3\n"
RESULTS = json.dumps({
    "quantities": [{"name": "yield", "value": 0.42, "unit": "1",
                    "source": "data/runs.csv@v3"}],
    "convergence": {"converged": True}}).encode()


def increment(**extra: bytes) -> dict[str, bytes]:
    return {"experiments/e1/metadata.yml": META,
            "experiments/e1/results.json": RESULTS, **extra}


# ----------------------------------------------------- provenance: existence
def test_provenance_verifies_that_a_declared_input_exists():
    """MUTATION: delete the `_declared_inputs` loop at the head of
    `check_provenance`. A quantity citing an input nobody committed passes."""
    absent = run_checks(increment(), ["provenance"])
    assert [(f.severity, f.rule) for f in absent.findings] == [(BLOCKER, "CA-DATA-003")]
    assert absent.findings[0].artifact == "experiments/e1/metadata.yml"

    present = run_checks(
        increment(**{"experiments/e1/data/runs.csv": b"yield\n0.42\n"}), ["provenance"])
    assert present.findings == []


def test_provenance_reads_only_inputs_as_filenames():
    """MUTATION: widen the existence loop to `sources`, `requires` or
    `depends_on` — which is what adding the neutral `declared` check to the
    science profile did. A DOI and a version range become non-overridable
    blockers on correct work, and that is the failure this whole line exists to
    avoid, not a stricter check."""
    meta = META + (b"sources:\n  - doi:10.1234/example\n"
                   b"requires:\n  - python>=3.11\n"
                   b"depends_on:\n  - some-service\n")
    files = increment(**{"experiments/e1/metadata.yml": meta,
                         "experiments/e1/data/runs.csv": b"yield\n0.42\n"})
    assert run_checks(files, ["provenance"]).findings == []


def test_an_https_input_is_not_looked_for_on_disk():
    """MUTATION: drop the URL guard. A declared remote input becomes a missing
    file, which it is not."""
    meta = b"code_version: v3\ninputs:\n  - https://example.org/runs.csv@v3\n"
    assert run_checks({"experiments/e1/metadata.yml": meta}, ["provenance"]).findings == []


# ------------------------------------------------------- declared: the shapes
def test_a_scalar_declaration_is_one_entry_not_a_string_to_walk():
    """MUTATION: restore `for item in doc.get(key) or []`. A scalar
    `sources: runs.csv@v3` is iterated character by character and produces one
    BLOCKER per letter — 'declares 'r', which is not in the audited scope'."""
    out = check_declared({"m.yml": b"sources: runs.csv@v3\n"})
    assert [(f.severity, f.observation) for f in out] == [
        (BLOCKER, "sources declares 'runs.csv', which is not in the audited scope")]
    assert check_declared({"m.yml": b"sources: runs.csv@v3\n",
                           "runs.csv": b"x\n"}) == []


@pytest.mark.parametrize("yaml_text,ref", [
    (b"requires: 3\n", "3"),
    (b"requires:\n  - 3\n", "3"),
    (b"inputs:\n  a: b\n", "a"),
    (b"sources:\n  - true\n", "True"),
])
def test_a_declaration_this_check_cannot_read_blocks_and_never_raises(yaml_text, ref):
    """MUTATION: iterate `doc.get(key) or []` again. `requires: 3` raises
    TypeError straight out of `run_checks` — a shape a person can legitimately
    write crashing the one layer that is supposed to never guess.

    **Severity is base severity, and that is the correction.** An earlier draft
    reported an unreadable shape as ADVISORY, which turned `requires: [3]` from
    a BLOCKER on the missing path `'3'` into something that permits PASS. Small,
    and still a weakening of a kernel check, which this layer does not get to
    do. Every entry is `str()`-coerced and keeps the base outcome; a dict still
    yields its keys, exactly as base did; the only thing that changes is that a
    scalar is one entry instead of a crash or a walk over its letters."""
    out = check_declared({"m.yml": yaml_text})
    assert [(f.severity, f.rule) for f in out] == [(BLOCKER, "CA-FILE-002")]
    assert repr(ref) in out[0].observation
    # It must reach `run_checks` as a finding rather than as an exception.
    result = run_checks({"m.yml": yaml_text}, ["declared"])
    assert result.hard_failures == 1


def test_an_unreadable_entry_still_passes_when_the_path_it_names_exists():
    """The other half: coercion is not a licence to block. A committed file
    named `3` satisfies `requires: [3]`, as it did on base."""
    assert check_declared({"m.yml": b"requires:\n  - 3\n", "3": b"x\n"}) == []


def test_a_revisioned_path_still_has_its_revision_stripped():
    """MUTATION: stop splitting on `@`. Every `path@revision` declaration in
    every project becomes a missing file — the reason this check was safe to
    consider for science in the first place (`neutral.py`, `split("@")[0]`)."""
    assert check_declared({"m.yml": b"inputs:\n  - runs.csv@v3\n",
                           "runs.csv": b"x\n"}) == []
    missing = check_declared({"m.yml": b"inputs:\n  - runs.csv@v3\n"})
    assert [f.rule for f in missing] == ["CA-FILE-002"]
