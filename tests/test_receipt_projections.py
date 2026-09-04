"""The receipt says which projection of the rulebook each role received.

One artefact is still bound — the committed constitution, by path, by content
hash and by commit. What is added is the answer to a question that could not
be asked while there was only one text: the auditor read all of it, and the
writer read a brief derived from it. Both digests are RE-DERIVED by verify from
the blob it reads at the pinned commit, so the block is checked, never trusted.
"""
from __future__ import annotations

import pytest

from crossaudit.constitution import projection_digests
from crossaudit.errors import IntegrityDenial
from crossaudit.receipt.schema import validate
from crossaudit.receipt.verify import verify

from .test_receipt_tool_evidence import _mint


def _verify(cfg, science, sha, receipt):
    return verify(receipt, science_root=science, audit_root=science,
                  expect_repo=cfg.science_repo, expect_sha=sha, cfg=cfg)


def test_a_minted_receipt_records_both_projections_and_verifies(cfg, science):
    sha, receipt = _mint(cfg, science, with_tools=False)
    rules = (science / cfg.constitution).read_text()

    assert receipt["projections"] == projection_digests(rules)
    assert receipt["projections"]["auditor"]["name"] == "criteria"
    assert receipt["projections"]["generator"]["name"] == "brief"
    # Two readers, two texts. If these ever coincide the split is not happening.
    assert (receipt["projections"]["auditor"]["sha256"]
            != receipt["projections"]["generator"]["sha256"])
    # The artefact the ledger binds is unchanged: still one file, one hash.
    assert receipt["inputs"]["constitution_sha256"]
    assert receipt["inputs"]["constitution_commit"]
    assert _verify(cfg, science, sha, receipt)["verified"]


def test_the_auditor_projection_is_the_bound_constitution_itself(cfg, science):
    """The identity, proven against the receipt's own content hash — so
    "the auditor sees only committed bytes" is a checkable claim, not a comment."""
    import hashlib
    sha, receipt = _mint(cfg, science, with_tools=False)
    rules = (science / cfg.constitution).read_bytes()
    assert (receipt["projections"]["auditor"]["sha256"]
            == hashlib.sha256(rules).hexdigest()
            == receipt["inputs"]["constitution_sha256"])
    assert _verify(cfg, science, sha, receipt)["verified"]


@pytest.mark.parametrize("role", ["auditor", "generator"])
def test_a_forged_projection_is_refused(cfg, science, role):
    """Mutation: drop the re-derivation in verify.py — a receipt claiming the
    writer was handed something this rulebook does not produce verifies."""
    sha, receipt = _mint(cfg, science, with_tools=False)
    receipt["projections"][role]["sha256"] = "f" * 64
    with pytest.raises(IntegrityDenial, match=f"{role}'s constitution projection"):
        _verify(cfg, science, sha, receipt)


def test_a_renamed_projection_is_refused(cfg, science):
    sha, receipt = _mint(cfg, science, with_tools=False)
    receipt["projections"]["generator"]["name"] = "criteria"
    with pytest.raises(IntegrityDenial, match="generator's constitution projection"):
        _verify(cfg, science, sha, receipt)


def test_a_receipt_written_before_the_block_existed_still_verifies(cfg, science):
    """Absence is legal. Every receipt already in a ledger predates two readers
    and must keep verifying — which is why this is not in REQUIRED_INPUTS."""
    sha, receipt = _mint(cfg, science, with_tools=False)
    del receipt["projections"]
    assert validate(receipt)
    assert _verify(cfg, science, sha, receipt)["verified"]


@pytest.mark.parametrize("bad", [
    "not a mapping",
    {"auditor": {"name": "criteria", "sha256": "a" * 64}},          # no generator
    {"auditor": {"name": "criteria", "sha256": "a" * 64},
     "generator": {"name": "brief", "sha256": "short"}},
    {"auditor": {"name": "", "sha256": "a" * 64},
     "generator": {"name": "brief", "sha256": "b" * 64}},
    {"auditor": "criteria",
     "generator": {"name": "brief", "sha256": "b" * 64}},
])
def test_a_malformed_block_is_refused_by_the_schema(cfg, science, bad):
    sha, receipt = _mint(cfg, science, with_tools=False)
    receipt["projections"] = bad
    with pytest.raises(IntegrityDenial):
        validate(receipt)
