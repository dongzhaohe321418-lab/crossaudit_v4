"""D156: a house skill is a generator input and never audited increment data.

`skills.py`'s module docstring has always claimed the invariant outright —
"**Skills never reach the auditor.** ... A skill that could speak to the auditor
would be an unversioned rule — the exact thing P3 exists to prevent". The code
did not honour it. `_materialise_tree_scope` reads every file under the scope
prefixes (the repository ROOT when `scope.dirs` is unset, which is the shape the
`science` fixture and every un-scoped project have), and filtered only paths
containing `TEMPLATE`; `auditor.prompt.render_increment` then fenced the skill
bodies into the auditor's prompt as untrusted increment data. An independent
review reproduced a complete skill inside an auditor prompt.

These tests pin the boundary. Each names the mutation it kills, because a
boundary test that survives the boundary's removal is decoration.

Nothing here weakens a check: no deterministic check reads skill bytes — the
strings "skill"/"skills" do not appear anywhere under `src/crossaudit/dcl/` or
`src/crossaudit/auditor/` (see the grep test at the bottom, which keeps that
true rather than asserting it once in prose).
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from crossaudit import generator as gen
from crossaudit import skills as skills_mod
from crossaudit.auditor import dcl_source_digest, run_audit
from crossaudit.auditor import prompt as pm
from crossaudit.cli.main import (_materialise_tree_scope, _skills_manifest,
                                 cmd_run)
from crossaudit.console import overview
from crossaudit.errors import NO_SCIENCE_COMMIT_CAUSE, ConfigDenial
from crossaudit.controller import StateStore
from crossaudit.dcl import run_checks
from crossaudit.gitio import changed_paths, materialise, parent, resolve
from crossaudit.receipt import build
from crossaudit.receipt.verify import verify

from .conftest import GOOD_RESULTS, git, write_increment

#: A line no scaffold, rule or increment would ever contain, so its presence in
#: a prompt can only have come from the skill file.
SENTINEL = "PINEAPPLE-QUADRANT-7734 the house voice is terse and never hedges"

SKILL_BODY = f"---\napplies_to: experiments/\n---\n\n{SENTINEL}\n"


def _commit_skill(science: Path, name: str = "house", also: tuple = ()) -> str:
    """Commit `skills/<name>.md` carrying the sentinel. Returns the new sha.

    Paths are added by name, never `-A`: a mint in the same test leaves an
    uncommitted report under `cycles/`, and sweeping that into the subject
    commit would move the audited manifest for a reason that has nothing to do
    with skills.
    """
    d = science / skills_mod.SKILLS_DIR
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.md").write_text(SKILL_BODY)
    git("add", "--", skills_mod.SKILLS_DIR, *also, cwd=science)
    git("commit", "-q", "-m", f"house skill {name}", cwd=science)
    return git("rev-parse", "HEAD", cwd=science)


def _auditor_prompt(cfg, sha: str, explicit_scope: str | None) -> str:
    """The real auditor prompt for this commit, through the real seams."""
    files, notes, _scope = _materialise_tree_scope(cfg, sha, explicit_scope)
    dcl = run_checks(files, cfg.checks, notes).as_dict()
    const = (cfg.root / cfg.constitution).read_text()
    cc = git("log", "-1", "--format=%H", "--", cfg.constitution, cwd=cfg.root)
    prompt, _bounded, _digest = pm.build(const, cc, dcl, files)
    return prompt


# --------------------------------------------------------------- 1. root scope
def test_a_root_scoped_project_does_not_show_its_skills_to_the_auditor(cfg, science):
    """The reported defect, at the seam that had it.

    The `science` fixture writes no `scope:` block, so `cfg.scope_dirs is None`
    and `_materialise_tree_scope` falls back to the prefix `""` — the whole
    repository. That is the shape of every project that has not narrowed its
    scope, and it is the shape in which the review reproduced a complete skill
    inside an auditor prompt.

    MUTATION KILLED: remove `_is_house_skill` from `_outside_the_increment`
    (or drop the `_outside_the_increment` filter in `_materialise_tree_scope`
    back to `_is_scaffold_template`) -> the sentinel is present.
    """
    write_increment(science, GOOD_RESULTS, "Work done.", "increment")
    sha = _commit_skill(science)

    files, _notes, _scope = _materialise_tree_scope(cfg, sha, None)
    assert cfg.scope_dirs is None, "the fixture must be root-scoped for this to bite"
    assert "experiments/demo/results.json" in files, "the increment is still audited"
    assert not any(p.startswith("skills/") for p in files)

    prompt = _auditor_prompt(cfg, sha, None)
    assert SENTINEL not in prompt
    assert "skills/house.md" not in prompt


# ----------------------------------------------------------- 2. explicit scope
def test_an_explicit_root_scope_does_not_show_its_skills_to_the_auditor(cfg, science):
    """The exclusion is unconditional, not conditional on the scope being implied.

    `cmd_check`'s working-directory walk carries an `excluded` set that is
    applied only `if not explicit`, and putting the skills exclusion there would
    have left `--scope .` (an explicit scope naming the repository root) still
    handing the auditor the skill. So the filter lives in
    `_materialise_tree_scope` and asks no questions about where the prefix came
    from.

    MUTATION KILLED: make the filter conditional — e.g. guard it with
    `if not explicit_scope:` inside `_materialise_tree_scope`, the shape it
    would have taken had it joined the `excluded` set -> the sentinel is
    present under `--scope .`.
    """
    write_increment(science, GOOD_RESULTS, "Work done.", "increment")
    sha = _commit_skill(science)

    files, _notes, scope = _materialise_tree_scope(cfg, sha, ".")
    assert scope == "."
    assert "experiments/demo/results.json" in files, "an explicit root still audits"
    assert not any(p.startswith("skills/") for p in files)

    assert SENTINEL not in _auditor_prompt(cfg, sha, ".")


# --------------------------------------------------------- 3. the hand-off holds
def test_the_generator_still_receives_the_skill(cfg, science):
    """Closing the auditor's door must not close the generator's.

    A skill exists to shape how the work is written. The whole point of D156 is
    that a skill is a GENERATOR input, so the hand-off — `skills.load` ->
    `select` -> `render` -> `generator.build_prompt(skills=...)`, which is what
    `cli/build.py` does — must be byte-for-byte unaffected by this slice.

    MUTATION KILLED: an over-broad fix — filtering skills inside `skills.load`,
    `gitio.materialise`, or `generator.build_prompt` rather than in the audited
    scope reader -> the sentinel disappears from the generator prompt too.
    """
    write_increment(science, GOOD_RESULTS, "Work done.", "increment")
    _commit_skill(science)

    house = skills_mod.load(cfg.root)
    assert [s.name for s in house] == ["house"]
    in_force = skills_mod.select(house, ["experiments/demo/results.json"])
    rendered = skills_mod.render(in_force)
    assert SENTINEL in rendered

    prompt = gen.build_prompt(
        task="Extend the demo increment.",
        constitution=(cfg.root / cfg.constitution).read_text(),
        current={"experiments/demo/SUMMARY.md": "Work done."},
        skills=rendered)
    assert SENTINEL in prompt


# ------------------------------------------- 4. it is a directory, not a substring
def test_a_file_merely_named_like_a_skill_is_still_audited(cfg, science):
    """`work/skills-notes.md` is work product and the auditor must see it.

    The exclusion is by FIRST PATH COMPONENT against `skills.SKILLS_DIR`. A
    substring test would quietly delete a person's notes file from the audited
    increment — a boundary that swallows work product is a worse defect than the
    one it fixes, and it would do it silently.

    MUTATION KILLED: `return skills_mod.SKILLS_DIR in path` (substring), or
    `in Path(path).parts` (any component, which also eats
    `docs/skills/overview.md` written as documentation) -> `work/skills-notes.md`
    vanishes from the audited files.
    """
    write_increment(science, GOOD_RESULTS, "Work done.", "increment")
    (science / "work").mkdir(exist_ok=True)
    (science / "work" / "skills-notes.md").write_text(
        f"Notes about our skills process. {SENTINEL}\n")
    (science / "docs").mkdir(exist_ok=True)
    (science / "docs" / "skills").mkdir(exist_ok=True)
    (science / "docs" / "skills" / "overview.md").write_text("How we use skills.\n")
    sha = _commit_skill(science, also=("work", "docs"))

    files, _notes, _scope = _materialise_tree_scope(cfg, sha, None)
    assert "work/skills-notes.md" in files
    assert "docs/skills/overview.md" in files
    assert "skills/house.md" not in files

    prompt = _auditor_prompt(cfg, sha, None)
    assert "work/skills-notes.md" in prompt
    assert "docs/skills/overview.md" in prompt


# ------------------------------------------------------- 5. what the receipt says
def _mint(cfg, science: Path, sha: str) -> dict:
    """A receipt for `sha` through the production builder, root-scoped."""
    store = StateStore(cfg.root / cfg.state_dir / "state.json")
    cycle = store.open_or_advance(cfg.science_repo, sha, parent(cfg.root, sha))
    files, notes, scope = _materialise_tree_scope(cfg, sha, None)
    const = (cfg.root / cfg.constitution).read_text()
    cc = git("log", "-1", "--format=%H", "--", cfg.constitution, cwd=cfg.root)
    outcome = run_audit(cfg=cfg, sha=sha, round_=cycle["round"], files=files,
                        notes=notes, constitution=const, constitution_commit=cc,
                        offline=True)
    manifest = {p: hashlib.sha256(b).hexdigest() for p, b in files.items()}
    ldir = cfg.root / cfg.ledger_dir / f"{sha[:12]}-r{cycle['round']}"
    ldir.mkdir(parents=True, exist_ok=True)
    (ldir / "report.md").write_text(outcome.report)
    _s, tree = resolve(cfg.root, sha)
    return build(
        cfg=cfg, subject={"sha": sha, "tree": tree, "scope": scope or "repository"},
        cycle=cycle, manifest=manifest, constitution_path=cfg.constitution,
        constitution_bytes=(cfg.root / cfg.constitution).read_bytes(),
        constitution_commit=cc, dcl_source_sha256=dcl_source_digest(),
        prompt_sha256=outcome.prompt_sha256, checks=cfg.checks,
        skills=_skills_manifest(cfg, sha),
        verdict=outcome.verdict, exchange=outcome.exchange, retention="sealed",
        report_bytes=(ldir / "report.md").read_bytes(), report_commit="",
        cycle_path=str(ldir.relative_to(cfg.root)),
        audit_repo=cfg.audit_repo or "local", mode="local",
        integrity=outcome.integrity)


def test_a_new_skill_moves_the_skills_digest_and_not_the_audited_manifest(cfg, science):
    """Adding a skill is a change of INPUT, not a change of the audited work.

    The receipt does distinguish the two, in two sibling fields under `inputs`,
    and there is no single scalar "audited-scope digest" to assert against —
    `inputs.manifest` is a path -> sha256 map over the audited increment, and
    `inputs.skills` is a path -> sha256 map over the house skills, minted by
    `cli/main.py:_skills_manifest` from the SAME subject commit. So this asserts
    what the receipt actually records rather than a field it does not have:
    `manifest` is unchanged across the two commits, `skills` gains the entry,
    and `skills/house.md` never appears in `manifest`.

    That is the whole receipt consequence of this slice, stated rather than
    papered over: for a project whose audited scope previously included
    `skills/`, its `inputs.manifest` loses those entries from this commit on.

    MUTATION KILLED: over-correcting — making `_skills_manifest` exclude skills
    too (return `{}`), so that a skill removed from the audited scope is
    recorded nowhere at all. The round would then be unreproducible, which is
    I2's whole objection and the reason `inputs.skills` exists.
    """
    before_sha = write_increment(science, GOOD_RESULTS, "Work done.", "increment")
    before = _mint(cfg, science, before_sha)

    after_sha = _commit_skill(science)
    after = _mint(cfg, science, after_sha)

    assert before["inputs"]["manifest"] == after["inputs"]["manifest"], (
        "adding a house skill changed the audited-scope manifest")
    assert not any(p.startswith("skills/") for p in after["inputs"]["manifest"])

    assert before["inputs"]["skills"] == {}
    assert list(after["inputs"]["skills"]) == ["skills/house.md"]
    assert after["inputs"]["skills"]["skills/house.md"] == hashlib.sha256(
        SKILL_BODY.encode("utf-8")).hexdigest()


# ------------------------------------- 6. earlier receipts keep verifying (D156)
def test_a_receipt_written_before_this_slice_still_verifies(cfg, science):
    """`verify` re-derives against the receipt's OWN recorded inputs.

    The receipt consequence is only forward-looking. `receipt/verify.py:406`
    iterates `inputs["manifest"]` — the paths the receipt itself names — and
    re-reads each from the pinned tree. It never re-derives the SCOPE, so a
    receipt minted before this slice, whose manifest lists `skills/house.md`,
    verifies exactly as it always did: the blob is still in the tree under the
    same sha.

    This test builds precisely that receipt — the manifest comes from
    `gitio.materialise` at the repository root, the pre-slice behaviour, with the
    skill still in it — and then verifies it with the filter in force.

    MUTATION KILLED: teaching `verify` to re-derive the audited scope from
    today's configuration instead of reading the receipt's manifest -> every
    receipt written before this slice becomes a forgery. If that had been the
    shape of `verify`, this slice would be a design question, not a fix; it is
    not, and this test keeps it that way.
    """
    write_increment(science, GOOD_RESULTS, "Work done.", "increment")
    sha = _commit_skill(science)

    # Pre-slice materialisation: everything under the root, skills included.
    old_files, notes = materialise(cfg.root, sha, "")
    old_files = {p: b for p, b in old_files.items() if "TEMPLATE" not in p}
    assert "skills/house.md" in old_files, "this must be a genuinely pre-slice manifest"

    store = StateStore(cfg.root / cfg.state_dir / "state.json")
    cycle = store.open_or_advance(cfg.science_repo, sha, parent(cfg.root, sha))
    const = (cfg.root / cfg.constitution).read_text()
    cc = git("log", "-1", "--format=%H", "--", cfg.constitution, cwd=cfg.root)
    outcome = run_audit(cfg=cfg, sha=sha, round_=cycle["round"], files=old_files,
                        notes=notes, constitution=const, constitution_commit=cc,
                        offline=True)
    manifest = {p: hashlib.sha256(b).hexdigest() for p, b in old_files.items()}
    ldir = cfg.root / cfg.ledger_dir / f"{sha[:12]}-r{cycle['round']}"
    ldir.mkdir(parents=True, exist_ok=True)
    (ldir / "report.md").write_text(outcome.report)
    _s, tree = resolve(cfg.root, sha)
    old_receipt = build(
        cfg=cfg, subject={"sha": sha, "tree": tree, "scope": "repository"},
        cycle=cycle, manifest=manifest, constitution_path=cfg.constitution,
        constitution_bytes=(cfg.root / cfg.constitution).read_bytes(),
        constitution_commit=cc, dcl_source_sha256=dcl_source_digest(),
        prompt_sha256=outcome.prompt_sha256, checks=cfg.checks,
        skills=_skills_manifest(cfg, sha),
        verdict=outcome.verdict, exchange=outcome.exchange, retention="sealed",
        report_bytes=(ldir / "report.md").read_bytes(), report_commit="",
        cycle_path=str(ldir.relative_to(cfg.root)),
        audit_repo=cfg.audit_repo or "local", mode="local",
        integrity=outcome.integrity)

    assert "skills/house.md" in old_receipt["inputs"]["manifest"]

    evidence = verify(old_receipt, science_root=science, audit_root=science,
                      expect_repo=cfg.science_repo, expect_sha=sha, cfg=cfg)
    assert evidence["verified"], "an earlier receipt stopped verifying"


# ------------------------------------------------- the claim the fix rests on
def test_no_deterministic_check_reads_skill_bytes():
    """The slice's licence to remove these files from the increment.

    Excluding a file from the audited increment would REMOVE A CHECK if any
    check read it. None does: neither the check layer nor the auditor package
    so much as mentions skills. This is asserted rather than remembered, so a
    future check that starts reading `skills/` fails here and has to argue with
    D156 instead of silently losing its input.
    """
    src = Path(__file__).resolve().parents[1] / "src" / "crossaudit"
    offenders = []
    for pkg in ("dcl", "auditor"):
        for path in sorted((src / pkg).rglob("*.py")):
            if "skill" in path.read_text(encoding="utf-8").lower():
                offenders.append(str(path.relative_to(src)))
    assert offenders == [], (
        f"a check or the auditor now reads skills: {offenders}. Excluding "
        f"skills/ from the audited increment would remove a check; re-open D156.")


# ---------------------------------------------- the second door D156 did not name
def test_the_run_verb_does_not_treat_a_skill_edit_as_an_increment(
        cfg, science, monkeypatch):
    """`crossaudit run` reaches the auditor by a different route, and had the bug.

    D156 named `_materialise_tree_scope` and only that. But `cmd_run` builds its
    own increment from `changed_paths` (`cli/main.py`, `materialise(...,
    only=science)`) and never passes through the scope reader. Reproduced before
    the fix on a root-scoped project: a commit touching `skills/house.md` gave
    `science_of` -> `['skills/house.md']`, so the skill WAS the increment and the
    auditor was asked to judge it. Closing one door and reporting the invariant
    honoured would have been false.

    The fix puts the skills directory in `prefix_own` — the list that already
    holds the ledger, the state directory and `.github/`, "the loop's own
    artefacts". A commit that touches nothing else then falls through to the
    existing "changed no science files" refusal, which is the true answer:
    editing house guidance is not an increment, and this is a setup mistake with
    its own recorded cause, not an audit.

    Driven through `cmd_run` itself rather than through a copy of its filter, so
    the test reads production code.

    MUTATION KILLED: drop `skills_dir + "/"` from `prefix_own` -> `cmd_run`
    audits the skill instead of refusing, and this raises nothing.
    """
    write_increment(science, GOOD_RESULTS, "Work done.", "increment")
    sha = _commit_skill(science)
    assert changed_paths(cfg.root, sha) == ["skills/house.md"]

    monkeypatch.chdir(science)
    with pytest.raises(ConfigDenial) as caught:
        cmd_run(SimpleNamespace(sha=sha, json=False, allow_custom_endpoint=False,
                                continue_cycle=None, offline=True, science=None))
    assert "changed no science files" in caught.value.reason

    rows = [r for r in overview.escalations(cfg)]
    assert rows and rows[0]["cause"] == NO_SCIENCE_COMMIT_CAUSE
