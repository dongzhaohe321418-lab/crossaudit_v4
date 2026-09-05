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

What excluding guidance costs, stated correctly. An earlier version of this
module said no deterministic check reads skill bytes, and pinned it with a grep
over `dcl/` and `auditor/` for the substring "skill". Both the claim and the
test were wrong: handed a skill body, `complete` and `complete-strict` report
`CA-FILE-004` for a `TODO` and `internal` reports `CA-FILE-003` for a broken
relative link — and the grep proved nothing, since a reader spelled
`guidance` would have slipped past it. The grep test is deleted. What is true,
and what `test_no_check_reports_a_finding_against_house_guidance` pins over all
ten registered checks with positive controls, is that guidance is not work
product: those findings were never wanted, so this removes an INPUT no check
should have been given, not a check.

The boundary is exactly two inputs wide — the audited increment and the
configured Constitution — and no wider. `auditor.prompt.build` is a public
function that fences whatever mapping it is handed; this is an ingress rule at
the CLI seam, not a property of the prompt API.

The other half of the boundary is directory IDENTITY. The filters compare git
tree paths; `skills.house_dir` makes the loader mean the same directory, so a
case variant or a symlink cannot make one file guidance to one seam and work to
another. Where a file is NOT guidance it is ordinary work and is audited as
such — that, not absence from the auditor, is the property to assert for
`SKILLS/house.md` and for a stray file named `skills`.
"""
from __future__ import annotations

import hashlib
import os
from contextlib import suppress
from pathlib import Path
from types import SimpleNamespace

import pytest

from crossaudit import generator as gen
from crossaudit import skills as skills_mod
from crossaudit.auditor import dcl_source_digest, run_audit
from crossaudit.auditor import prompt as pm
from crossaudit.cli.main import (_committed_constitution, _is_house_skill,
                                 _materialise_tree_scope, _skills_manifest,
                                 cmd_run)
from crossaudit.cli.main import main as cli_main
from crossaudit.cli import i18n
from crossaudit.config import load as cfg_load
from crossaudit.console import overview
from crossaudit.errors import NO_SCIENCE_COMMIT_CAUSE, ConfigDenial, Denial
from crossaudit.controller import StateStore
from crossaudit.dcl import framework, run_checks
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

    MUTATION KILLED: an over-broad fix on the path this test actually walks —
    an empty `skills.load`, or a `build_prompt` that drops the `skills` block.
    Both redden it.

    NOT killed, and the review was right to say so: filtering inside
    `gitio.materialise`. The generator hand-off reads the WORKING TREE through
    `skills.load`, never `materialise`, so that mutation leaves this green. It
    is caught by
    `test_a_new_skill_moves_the_skills_digest_and_not_the_audited_manifest`,
    which reads `_skills_manifest` — the one skills path that does go through
    `materialise`. Naming a mutation a test does not kill is worse than naming
    none: it is a claim of coverage that is not there.
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
def test_no_check_reports_a_finding_against_house_guidance(cfg, science):
    """What excluding guidance from the increment actually costs.

    The first version of this test grepped `dcl/` and `auditor/` for the
    substring "skill" and concluded that no check reads skill bytes. That
    premise is FALSE and the review reproduced it: hand `internal` a skill body
    with a broken relative link and it reports CA-FILE-003; hand
    `complete-strict` a `TODO` and it reports CA-FILE-004, a BLOCKER. The grep
    also proved nothing — an injected reader using generic `files.items()`
    survived it, and a bare `# skill` comment reddened it.

    The property that IS true, and the one the policy rests on: a house skill is
    guidance, not work product, so no check should ever have been given it. A
    style file is not incomplete for saying TODO. This drives EVERY registered
    check over a root-scoped project whose `skills/house.md` contains both
    triggers, and asserts no finding names a path under `skills/`. The positive
    control on the same bytes proves the checks are not merely inert.

    MUTATION KILLED: drop the house-skill filter from `_outside_the_increment`
    -> both findings appear against `skills/house.md`.
    """
    # The registry is populated by IMPORT, so it must be populated here and not
    # by whichever test happened to run first. The third review found this test
    # failing in a fresh process — `framework.available()` returned the empty
    # set and the guard below fired — while it passed in a full run because
    # something else had already imported the packs. A test whose result depends
    # on file order is not evidence of anything.
    from crossaudit.dcl import (builtin, documents,  # noqa: F401
                                neutral, provenance)

    write_increment(science, GOOD_RESULTS, "Work done.", "increment")
    d = science / skills_mod.SKILLS_DIR
    d.mkdir(parents=True, exist_ok=True)
    (d / "house.md").write_text("[broken](missing.md)\n\nTODO: finish this\n")
    git("add", "--", skills_mod.SKILLS_DIR, cwd=science)
    git("commit", "-q", "-m", "house skill", cwd=science)
    sha = git("rev-parse", "HEAD", cwd=science)

    every = framework.available()
    assert len(every) >= 10, (
        f"the check registry is not fully loaded: {every}. This test asserts a "
        f"property over EVERY registered check, so a partial registry would "
        f"silently narrow what it proves.")
    assert {"internal", "complete-strict"} <= set(every), (
        "the two checks the review reproduced findings with are gone; re-derive "
        "this test against whatever replaced them")

    # Positive control: these bytes DO produce findings when a check is handed
    # them, so a green assertion below cannot come from inert checks.
    raw = {"skills/house.md": (d / "house.md").read_bytes()}
    control = run_checks(raw, ["internal", "complete-strict"], []).as_dict()
    assert [f for f in control["findings"] if f["artifact"].startswith("skills/")], (
        "the premise of this test is gone: these bytes no longer trigger a check")

    files, notes, _scope = _materialise_tree_scope(cfg, sha, None)
    result = run_checks(files, every, notes).as_dict()
    offenders = [f for f in result["findings"]
                 if f.get("artifact", "").startswith(skills_mod.SKILLS_DIR + "/")]
    assert offenders == [], (
        f"a deterministic check judged house guidance as work: {offenders}")


# ---------------------------------------------- the second door D156 did not name
def test_the_run_verb_does_not_treat_a_skill_edit_as_an_increment(
        cfg, science, monkeypatch):
    """`crossaudit run --sha <skill commit>` refuses instead of auditing it.

    D156 named `_materialise_tree_scope` and only that. But `cmd_run` builds its
    own increment from `changed_paths` (`materialise(..., only=science)`) and
    never passes through the scope reader. Reproduced before the fix on a
    root-scoped project: a commit touching `skills/house.md` gave `science_of`
    -> `['skills/house.md']`, so the skill WAS the increment and the auditor was
    asked to judge it.

    The fix puts the skills directory in `prefix_own` — the list that already
    holds the ledger, the state directory and `.github/`, "the loop's own
    artefacts". Pointed at that commit explicitly, `run` now takes the "nothing
    to audit" path, and says which of the two things happened: the refusal names
    guidance rather than reciting "rules, configuration or ledger", none of
    which the person changed.

    Plain `run` behaves DIFFERENTLY and the companion test below covers it.

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
    reason = caught.value.reason
    assert "changed only house guidance under skills/" in reason
    assert "rules, configuration or ledger" not in reason, (
        "the refusal recites categories the person did not touch")
    assert i18n.denial_zh(reason), "the guidance refusal reaches a zh reader in English"

    rows = [r for r in overview.escalations(cfg)]
    assert rows and rows[0]["cause"] == NO_SCIENCE_COMMIT_CAUSE


def test_plain_run_walks_back_past_a_guidance_commit_and_says_so(
        cfg, science, monkeypatch, capsys):
    """Plain `run` does NOT refuse — it audits the newest commit that changed work.

    The first review found the previous test covered only `--sha`. With no
    `--sha`, `cmd_run` walks back through the existing 50-commit window for a
    commit `science_of` accepts, and audits that instead. Stated here because it
    is the behaviour a person actually meets after editing guidance: the run
    proceeds, against the earlier work commit, and the skill is not in it.

    The narration for that walk-back was printed as raw English
    (`"(HEAD is ledger bookkeeping; ...)"`) — untranslated, and wrong besides,
    since a guidance commit is not the ledger. It now goes through the
    catalogue, and `cmd_run` selects the language when one was asked for.

    The second review found the zh half of this test only called `i18n.t()`
    directly, so the mutation it claimed to kill survived: a raw `print()` in
    `cmd_run` never reaches `t()` at all. The zh half now runs the COMMAND
    through `main()` and reads its output.

    Two zh variants, because `_language_for` has two sources and `cmd_run` used
    to honour only one. The third review showed why the environment must count:
    `cmd_init`, `cmd_doctor` and the central denial handler all resolve
    flag -> environment -> English, so under `LANG=zh_CN.UTF-8` a plain `run`
    already printed a Chinese refusal. A narration that stayed English made one
    screen answer in two languages.

    MUTATION KILLED (all three verified): `print(f"...")` back in place of
    `i18n.t("run.walked_back", ...)`; dropping `_speak(args)` from the top of
    `cmd_run` (both variants go English); and gating it on an explicit flag,
    `if getattr(args, "lang", None)`, which leaves the environment variant
    English while the flag variant passes.
    """
    work_sha = write_increment(science, GOOD_RESULTS, "Work done.", "increment")
    _commit_skill(science)
    monkeypatch.chdir(science)

    monkeypatch.setattr(i18n, "_language", "en", raising=False)
    # The provider call is out of this test's scope — the replay transcript for
    # that exact prompt does not exist here, and pinning prompt bytes would make
    # this test fail for reasons that have nothing to do with guidance. What is
    # asserted is which commit `run` SELECTED and how it said so, both of which
    # happen before any provider is reached.
    with suppress(Denial):
        cmd_run(SimpleNamespace(sha=None, json=False, allow_custom_endpoint=False,
                                continue_cycle=None, offline=True, science=None,
                                lang=None))
    out = capsys.readouterr().out
    assert "deterministic checks" in out, "it did not get as far as selecting work"
    assert work_sha[:12] in out, "it did not name the work commit it fell back to"
    assert SENTINEL not in out
    assert "ledger bookkeeping" not in out, (
        "a guidance commit is not ledger bookkeeping")

    # The zh halves, through the command a person actually types. `main()`
    # catches the provider Denial and returns an exit code, so nothing is
    # suppressed here; what is read is the narration it printed on the way.
    expected = i18n.CATALOGUE["zh"]["run.walked_back"].format(sha=work_sha[:12])

    # (a) the explicit flag
    i18n.reset_fallbacks()
    monkeypatch.setattr(i18n, "_language", "en", raising=False)
    capsys.readouterr()
    cli_main(["--lang", "zh", "run"])
    flag_out = capsys.readouterr().out
    assert expected in flag_out, (
        f"`crossaudit --lang zh run` narrated the walk-back in English:\n{flag_out}")

    # (b) the environment, with NO flag — the variant the lead's ruling requires.
    # Higher-priority locale variables are cleared so `LANG` is the one that
    # answers, which is what `i18n.from_environment` reads in order.
    i18n.reset_fallbacks()
    monkeypatch.setattr(i18n, "_language", "en", raising=False)
    monkeypatch.delenv("LC_ALL", raising=False)
    monkeypatch.delenv("LC_MESSAGES", raising=False)
    monkeypatch.setenv("LANG", "zh_CN.UTF-8")
    capsys.readouterr()
    cli_main(["run"])
    env_out = capsys.readouterr().out
    assert expected in env_out, (
        f"a plain `run` under LANG=zh_CN.UTF-8 narrated in English while its "
        f"refusals are Chinese — one screen, two languages:\n{env_out}")
    assert "run.walked_back" not in i18n.fallbacks()


# --------------------------------------- one identity for the guidance directory
def _case_insensitive(root: Path) -> bool:
    """Does this host open `root/'skills'` when the entry is `SKILLS`?"""
    probe = root / "CASEPROBE"
    probe.mkdir()
    try:
        return (root / "caseprobe").is_dir()
    finally:
        probe.rmdir()


def test_a_case_variant_guidance_directory_is_refused_not_silently_split(
        cfg, science):
    """P1: the loader and the filters must mean the same directory.

    Reproduced before the fix, on this host: commit `SKILLS/house.md`;
    `skills.load` opens it through `root / "skills"` (case-insensitive
    filesystem) and returns it as guidance, while git keeps `SKILLS/` and every
    filter compares `"SKILLS" == "skills"` and lets it into the increment. The
    same bytes were guidance to the generator AND work to the auditor.

    Fixed at the loader, once, so there is one identity: `skills.house_dir`
    reads `root`'s real directory entries (`Path.resolve()` does NOT
    canonicalise case on macOS — measured; the obvious `.resolve().name` check
    would have let this P1 through) and refuses a spelling git would not match.
    A refusal, not a silent empty load: answering "you have no guidance" to
    someone looking at a folder full of it is the same class of defect.

    What holds afterwards is NOT "the sentinel is absent from the auditor".
    `SKILLS/house.md` is not guidance, so it is ordinary work, and the auditor
    is shown it AS WORK — the honest outcome of one identity, and what this
    asserts. The premise (that this host would otherwise have loaded it) is
    asserted inline, with a stated reason where the filesystem is
    case-sensitive, rather than living in a test of its own that named no
    mutation.

    MUTATION KILLED: `house_dir` returning `None` instead of raising for a case
    variant -> the loader is silent and the disagreement is merely hidden.
    Also killed: comparing `Path(root/dir).resolve().name` instead of scanning
    `root`'s entries -> no refusal at all on a case-insensitive host.
    """
    write_increment(science, GOOD_RESULTS, "Work done.", "increment")
    (science / "SKILLS").mkdir()
    (science / "SKILLS" / "house.md").write_text(SKILL_BODY)

    if _case_insensitive(science):
        assert (science / "skills").is_dir(), (
            "the exposure this fix closes needs the lowercase path to open")
        assert SENTINEL in (science / "skills" / "house.md").read_text(), (
            "premise: root/'skills' reads SKILLS/house.md on this host")
    else:
        # Not skipped as a whole: the refusal and the work-identity below hold
        # on every host. Only the "would otherwise have been loaded" premise
        # needs a case-insensitive filesystem to be observable at all.
        assert not (science / "skills").exists()

    git("add", "--", "SKILLS", cwd=science)
    git("commit", "-q", "-m", "uppercase guidance", cwd=science)
    sha = git("rev-parse", "HEAD", cwd=science)

    with pytest.raises(ConfigDenial) as caught:
        skills_mod.load(science)
    assert "named exactly 'skills'" in caught.value.reason
    assert "SKILLS" in caught.value.reason, "the refusal must name what to rename"
    assert i18n.denial_zh(caught.value.reason), "refused only in English"

    # One identity: not guidance, therefore work — and audited as work by both
    # routes. Asserting "absent from the auditor" here would assert a property
    # that does not hold and should not.
    files, _notes, _scope = _materialise_tree_scope(cfg, sha, None)
    assert "SKILLS/house.md" in files
    assert SENTINEL in _auditor_prompt(cfg, sha, None), (
        "a file that is not guidance is work, and work is what the auditor reads")
    assert changed_paths(cfg.root, sha) == ["SKILLS/house.md"]


def test_a_stray_file_named_like_the_guidance_directory_is_audited_as_work(
        cfg, science):
    """The behaviour contradiction the second review found, resolved.

    A regular FILE named `skills` was refused by the loader with a sentence
    claiming it "would be invisible" — while `cmd_run` audited it as ordinary
    work and the increment filter dropped it. Three seams, two answers.

    The behaviour that is right is that a stray file is work. So
    `_is_house_skill` now matches paths UNDER the directory (`len(parts) > 1`),
    never the entry itself, which makes both audit routes agree; and the
    loader's sentence says the true thing: nothing is loaded as guidance, and
    the file is judged as an ordinary file.

    MUTATION KILLED: restore `bool(parts) and parts[0] == SKILLS_DIR` -> the
    root-scope route drops the file while `cmd_run` still audits it, and the two
    routes disagree again.
    """
    write_increment(science, GOOD_RESULTS, "Work done.", "increment")
    (science / skills_mod.SKILLS_DIR).write_text(f"{SENTINEL} not a directory\n")
    git("add", "--", skills_mod.SKILLS_DIR, cwd=science)
    git("commit", "-q", "-m", "stray file", cwd=science)
    sha = git("rev-parse", "HEAD", cwd=science)

    with pytest.raises(ConfigDenial) as caught:
        skills_mod.load(science)
    reason = caught.value.reason
    assert "audited as ordinary work" in reason
    assert "invisible" not in reason, "the refusal states a behaviour that is false"
    assert i18n.denial_zh(reason), "refused only in English"

    files, _notes, _scope = _materialise_tree_scope(cfg, sha, None)
    assert skills_mod.SKILLS_DIR in files, "the root-scope route dropped a work file"
    assert changed_paths(cfg.root, sha) == [skills_mod.SKILLS_DIR]
    # Real guidance is still excluded, so this did not reopen the boundary.
    assert not _is_house_skill(skills_mod.SKILLS_DIR)
    assert _is_house_skill(f"{skills_mod.SKILLS_DIR}/house.md")


def test_a_symlinked_guidance_directory_is_refused_and_its_target_is_work(
        cfg, science, monkeypatch):
    """P1: `skills -> work/guidance` made one file guidance AND audited work.

    Reproduced before the fix: the loader checked whether each `.md` FILE was a
    symlink, never the directory it walked, so it read `work/guidance/house.md`
    as house guidance. Git records the target under its real path, so
    `cmd_run`'s changed-path route selected `work/guidance/house.md` and rendered
    the sentinel into an auditor prompt.

    After the fix the loader refuses the aliased directory outright, and
    `work/guidance/house.md` is what it plainly is: ordinary audited work. That
    is one identity — not "guidance everywhere", but the same answer from every
    seam.

    MUTATION KILLED: check only `p.is_symlink()` per file (the pre-fix shape)
    and drop the directory checks -> the loader hands back the target as
    guidance.
    """
    write_increment(science, GOOD_RESULTS, "Work done.", "increment")
    (science / "work" / "guidance").mkdir(parents=True)
    (science / "work" / "guidance" / "house.md").write_text(SKILL_BODY)
    os.symlink("work/guidance", science / skills_mod.SKILLS_DIR)
    git("add", "--", "work", skills_mod.SKILLS_DIR, cwd=science)
    git("commit", "-q", "-m", "aliased guidance", cwd=science)
    (science / "work" / "guidance" / "house.md").write_text(SKILL_BODY + "\nmore\n")
    git("add", "--", "work", cwd=science)
    git("commit", "-q", "-m", "edit guidance", cwd=science)
    sha = git("rev-parse", "HEAD", cwd=science)

    with pytest.raises(ConfigDenial) as caught:
        skills_mod.load(science)
    assert "symlink" in caught.value.reason
    assert i18n.denial_zh(caught.value.reason), "refused only in English"

    # The target is work, and is audited as work — the honest reading of a file
    # that lives in the project's own work directory.
    files, _notes = materialise(cfg.root, sha, "", only=["work/guidance/house.md"])
    assert "work/guidance/house.md" in files


def _with_constitution(science: Path, value: str) -> Path:
    path = science / "crossaudit.yml"
    path.write_text(path.read_text().replace("constitution: AUDIT_RULES.md",
                                             f"constitution: {value}"))
    return path


@pytest.mark.parametrize("spelling", [
    "skills/house.md",           # canonical
    "./skills/house.md",         # a leading dot component
    "SKILLS/house.md",           # case variant — accepted before r3
    "Skills/house.md",           # mixed case
    "work/../skills/house.md",   # traversal — accepted before r3
    "skills/../skills/house.md", # traversal that lands back inside
    "skills//house.md",          # a doubled separator
    "skills/nested/house.md",    # deeper
])
def test_the_constitution_may_not_be_a_house_skill(science, spelling):
    """P2: `constitution: skills/house.md` handed the auditor a skill as LAW.

    Reproduced through `cmd_audit`: the increment filter removed
    `skills/house.md`, and `_committed_constitution` then read the same file by
    commit and fenced it into the prompt as the Constitution. The boundary was
    not crossed by accident — it was configured around.

    The first version of the guard compared `PurePosixPath(value).parts` raw,
    which neither folds case nor collapses `..`. The second review reproduced
    two spellings walking straight past it: `SKILLS/house.md` and
    `work/../skills/house.md`. Neither reached the auditor — the committed-file
    reader denies them later — but a guard a different spelling of the same path
    steps over is not a guard. The value is normalised first, and case is folded
    on EVERY host: a constitution spelled `SKILLS/...` is never legitimate, and
    a rule that depends on the developer's filesystem is not a rule.

    MUTATION KILLED: drop `posixpath.normpath` -> the traversal spelling loads;
    drop `.lower()` -> the case spelling loads; delete the check -> all five
    load.
    """
    _with_constitution(science, spelling)
    with pytest.raises(ConfigDenial) as caught:
        cfg_load(science / "crossaudit.yml")
    assert skills_mod.SKILLS_DIR in caught.value.reason
    assert "cannot be both" in caught.value.reason
    assert i18n.denial_zh(caught.value.reason), "refused only in English"


@pytest.mark.parametrize("spelling, stored", [
    # A path that only PASSES THROUGH the guidance directory. Normalising
    # changed this case: the raw first-component check refused it, for the wrong
    # reason (the literal first component was `skills`).
    (f"{skills_mod.SKILLS_DIR}/../AUDIT_RULES.md", "AUDIT_RULES.md"),
    # The two `.`-carrying spellings. Their behaviour was already correct; the
    # fourth review asked for the matrix to SAY so, which is the point of a
    # matrix — an untested correct behaviour is indistinguishable from luck.
    ("./AUDIT_RULES.md", "AUDIT_RULES.md"),
    ("work/./AUDIT_RULES.md", "work/AUDIT_RULES.md"),
])
def test_an_accepted_constitution_is_stored_normalised_and_stays_readable(
        science, spelling, stored):
    """An accepted spelling must also be a USABLE one.

    The guard is about where the file is, not how the path was typed, so a value
    that merely passes through `skills/` is legitimate. The third review then
    found that acceptance was hollow: `Config.constitution` kept the RAW
    spelling, and `_committed_constitution` raised `IntegrityDenial: ... does
    not identify exactly one file`, because the git reader wants an exact tree
    path. A value that passes configuration and fails the auditor is worse than
    a refusal — it fails later, further from the person who wrote it.

    So `Config` stores the NORMALISED path, and each case here is carried all
    the way to the committed reader rather than stopping at "it loads".
    `normpath` is a no-op on a canonical path, so nothing that already worked
    changes; what it fixes is every equivalent spelling of a legitimate
    location.

    MUTATION KILLED: check the raw value instead of the normalised one -> the
    pass-through spelling is refused. And: store `raw["constitution"]` instead
    of `const_norm` -> all three load and the committed reader denies them.
    """
    if "/" in stored:
        target = science / stored
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((science / "AUDIT_RULES.md").read_text())
        git("add", "--", str(Path(stored).parent), cwd=science)
        git("commit", "-q", "-m", "rules in a subdirectory", cwd=science)

    _with_constitution(science, spelling)
    cfg = cfg_load(science / "crossaudit.yml")
    assert cfg.constitution == stored, (
        f"{spelling!r} was stored as {cfg.constitution!r}; the committed reader "
        f"wants an exact tree path and will refuse anything else")

    sha = git("rev-parse", "HEAD", cwd=science)
    text, data = _committed_constitution(cfg, sha)
    assert data and text.strip(), "the accepted constitution could not be read"


@pytest.mark.parametrize("spelling", [
    "/abs/skills/house.md",      # accepted before r4: first component is "/"
    "/etc/AUDIT_RULES.md",       # not guidance at all, still not a tree path
    # Windows forms. `posixpath.isabs` says False for both — a drive letter is
    # not a leading "/" and neither is a UNC share — so they need the separate
    # `PureWindowsPath(...).drive` arm, which the fourth review found untested:
    # it removed that arm and both of these became ACCEPTED while all 24 cases
    # in this file stayed green. Reproduced before adding them.
    "C:\\x\\AUDIT_RULES.md",  # drive letter
    "\\\\server\\share\\x.md",  # UNC share
])
def test_an_absolute_constitution_is_refused(science, spelling):
    """A Constitution is a path INSIDE the tree, cited by commit.

    The third review found `/abs/skills/house.md` loading: its first component
    after normalisation is `/`, so the guidance comparison missed it, and the
    traversal check never looked at absolute paths at all. It walked past both.
    No auditor exposure was reproduced — the committed reader refuses it later —
    but an absolute path names a file on one machine's disk, which no receipt
    can bind and no verifier can re-read, so config load is where it belongs.

    MUTATION KILLED: drop the `posixpath.isabs` check -> the two POSIX
    spellings load. Drop the `PureWindowsPath(const_raw).drive` check -> both
    WINDOWS forms load. Two arms, two mutations: `isabs` is False for a drive
    letter and for a UNC share, so neither arm covers the other and a single
    parametrisation over one of them proves nothing about the other.
    """
    _with_constitution(science, spelling)
    with pytest.raises(ConfigDenial) as caught:
        cfg_load(science / "crossaudit.yml")
    assert "absolute path" in caught.value.reason
    assert i18n.denial_zh(caught.value.reason), "refused only in English"


def test_a_constitution_outside_the_project_is_refused(science):
    """A path that leaves the repository cannot be a committed, commit-cited file.

    Added with the normalisation above: collapsing `..` is only half the job if
    a value that still escapes after collapsing is then accepted.

    MUTATION KILLED: drop the `..` check after normalisation -> `../elsewhere.md`
    loads.
    """
    _with_constitution(science, "../elsewhere/AUDIT_RULES.md")
    with pytest.raises(ConfigDenial) as caught:
        cfg_load(science / "crossaudit.yml")
    assert "outside the project" in caught.value.reason
    assert i18n.denial_zh(caught.value.reason), "refused only in English"
