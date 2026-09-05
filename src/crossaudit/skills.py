"""Skills: user-supplied instructions that shape how the generator works.

A skill is a markdown file the project owner writes — a house style, a domain
convention, a checklist, a worked example. It is loaded into the generator's
prompt so the work comes out the way this project wants it, without anyone
having to say so again every round.

The line that makes this safe is worth stating plainly: **a skill changes how
the generator writes, never what it is allowed to write or who judges it.**
Concretely, and enforced here rather than merely asked for:

* **Skills never reach the auditor.** The auditor judges committed artefacts
  against the committed Constitution. A skill that could speak to the auditor
  would be an unversioned rule — the exact thing P3 exists to prevent, since it
  would let the standards move without a dated amendment anybody agreed to.
  Precisely (D156): a skill is never part of the audited **increment** and can
  never be the configured **Constitution** — the two inputs a file could reach
  the auditor by. The increment side is enforced in `cli/main.py`
  (`_is_house_skill`, and `cmd_run`'s `prefix_own`), because the exposure was
  never the hand-off but the audited SCOPE, which read the repository root and
  carried `skills/` into the increment; the Constitution side is refused in
  `config.py` at load. Both compare git tree paths, and `house_dir` below makes
  this module's notion of the directory identical to theirs, so a case variant
  or a symlink cannot make one file guidance to one of them and work to the
  other. Beyond those two inputs the claim is not enforced and is not made:
  `auditor.prompt.build` is a public function that will fence whatever mapping
  it is handed, so this is an ingress rule at the CLI seam, not a property of
  the prompt API.
* **Skills cannot widen the generator's reach.** `scope.dirs` is read from
  configuration, and nothing in a skill file can add to it. A skill saying "also
  edit AUDIT_RULES.md" is a text file with an opinion; the path guard is what
  decides.
* **Skills are committed and hashed into the receipt.** They shape output, so
  they are part of how the work came to be, and I2 says that cannot live only
  in someone's directory. A round run under different skills is a different
  round, and the ledger says so.
* **A skill cannot impersonate the rules.** The prompt fences them apart and
  says which is which: rules bind, skills advise, and where they disagree the
  rules win.
"""
from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path

from .errors import ConfigDenial

SKILLS_DIR = "skills"
MAX_SKILL_BYTES = 60_000
MAX_TOTAL_BYTES = 200_000
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


@dataclass(frozen=True)
class Skill:
    name: str
    path: str
    body: str
    applies_to: tuple[str, ...] = ()

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.body.encode()).hexdigest()

    def matches(self, paths: list[str]) -> bool:
        """A skill with no `applies_to` is always in force; otherwise it waits
        until the round actually touches something it is about."""
        if not self.applies_to:
            return True
        return any(p.startswith(pref) or pref in p for pref in self.applies_to
                   for p in paths)


def _parse(text: str, name: str, rel: str) -> Skill:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    applies: tuple[str, ...] = ()
    body = text
    m = FRONT_MATTER.match(text)
    if m:
        for line in m.group(1).splitlines():
            key, _, value = line.partition(":")
            if key.strip() == "applies_to":
                applies = tuple(v.strip() for v in value.split(",") if v.strip())
        body = text[m.end():]
    return Skill(name=name, path=rel, body=body.strip(), applies_to=applies)


def house_dir(root: Path, directory: str = SKILLS_DIR) -> Path | None:
    """The project's guidance directory, or ``None`` when it has none.

    ONE IDENTITY, resolved here so the whole system shares it. The audited-scope
    filters (`cli/main.py:_is_house_skill`, `cmd_run`'s `prefix_own`) and the
    receipt writers compare literal **git tree paths**: first component exactly
    ``skills``. This loader used to resolve through the **filesystem**, and the
    two notions disagreed in two reproducible ways:

    * On a case-insensitive host (macOS, Windows) ``root / "skills"`` opens a
      directory git records as ``SKILLS/``. The loader took `SKILLS/house.md` as
      guidance; every filter compared ``"SKILLS" == "skills"`` and let it into
      the increment. The same bytes were guidance AND work.
    * ``skills -> work/guidance`` made ``work/guidance/house.md`` guidance to the
      loader and ordinary work to git. The old symlink check tested each .md
      FILE, never the directory it walked, so it saw nothing.

    Rather than teach every filter about aliases, the ambiguity is refused where
    it starts: this directory must be a real directory, named exactly
    ``directory``, sitting directly in ``root``. Anything else is a
    ``ConfigDenial`` naming what to rename — never a silent empty load, which
    would answer "you have no guidance" to someone looking at a folder full of
    it.

    A case-insensitive host cannot be detected from `Path.resolve()`: on macOS it
    returns the path as spelled, not as stored (measured). So the real entry name
    comes from scanning ``root``'s own directory entries, which is exact on every
    filesystem and is one syscall at one level.
    """
    try:
        entries = {e.name for e in os.scandir(root)}
    except OSError:
        return None
    if directory not in entries:
        # Case-insensitive hosts open `root/"skills"` when the entry is
        # `SKILLS`. Absent entirely is not an error; present under another
        # spelling is, because git keeps the spelling and the filters compare it.
        alias = sorted(n for n in entries if n.lower() == directory.lower())
        if alias:
            raise ConfigDenial(
                f"the guidance directory must be named exactly {directory!r}; this "
                f"project has {alias[0]!r}. Git keeps the spelling, so {alias[0]!r} "
                f"would be loaded as guidance and audited as work at the same "
                f"time. Rename it to {directory!r}.")
        return None
    base = root / directory
    if base.is_symlink():
        raise ConfigDenial(
            f"{directory!r} is a symlink. Guidance must be a real directory in "
            f"the project: through a link the same file is guidance here and "
            f"ordinary work to git, and the audit boundary cannot hold both. "
            f"Replace the link with a real {directory!r} directory.")
    if not base.is_dir():
        raise ConfigDenial(
            f"{directory!r} is not a directory. Guidance lives in a real "
            f"{directory!r} directory; a file of that name is neither loaded as "
            f"guidance nor audited as work, so it would be invisible.")
    if base.resolve() != (root.resolve() / directory):
        raise ConfigDenial(
            f"{directory!r} resolves to {base.resolve()}, outside the project's "
            f"own {directory!r}. Guidance must be a real directory in the "
            f"project, so that what is loaded as guidance is exactly what the "
            f"audit boundary excludes.")
    return base


def load(root: Path, directory: str = SKILLS_DIR) -> list[Skill]:
    """Read every skill in the project. Absent directory is not an error."""
    base = house_dir(root, directory)
    if base is None:
        return []
    out: list[Skill] = []
    total = 0
    for p in sorted(base.rglob("*.md")):
        if p.is_symlink():
            raise ConfigDenial(f"refusing a symlinked skill: {p.name}")
        data = p.read_bytes()
        if len(data) > MAX_SKILL_BYTES:
            raise ConfigDenial(
                f"skill {p.name} is {len(data)} bytes (limit {MAX_SKILL_BYTES}); a "
                f"skill is guidance, and one this long crowds out the work itself")
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise ConfigDenial(
                f"the skills total more than {MAX_TOTAL_BYTES} bytes; trim them, or "
                f"scope them with applies_to so each round loads only what it needs")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ConfigDenial(f"skill {p.name} is not UTF-8: {exc}") from exc
        out.append(_parse(text, p.stem, p.relative_to(root).as_posix()))
    return out


def select(skills: list[Skill], touched: list[str]) -> list[Skill]:
    return [s for s in skills if s.matches(touched)]


def render(skills: list[Skill]) -> str:
    """The generator-side block. Fenced and labelled so it cannot pass for law."""
    if not skills:
        return ""
    parts = [
        "HOUSE SKILLS — how this project wants the work done.",
        "These are the owner's guidance, not the rules you are judged by. Where a",
        "skill and a rule disagree, the rule wins and you should say so in notes.",
        "Nothing here widens where you may write.",
        "",
    ]
    for s in skills:
        scope = f" (applies to: {', '.join(s.applies_to)})" if s.applies_to else ""
        parts.append(f"--- skill: {s.name}{scope} ---\n{s.body}\n")
    return "<<<SKILLS\n" + "\n".join(parts) + "SKILLS"


def manifest(skills: list[Skill]) -> dict:
    """What the receipt records: which guidance shaped this round, and its hash."""
    return {s.path: s.digest for s in sorted(skills, key=lambda s: s.path)}


TEMPLATE = """\
---
applies_to: work/
---

# House style

Replace this with how you want the work done. A few things that belong here:

- conventions this project follows that a competent stranger would not guess
- the shape of a good output: sections, length, tone, what to lead with
- worked examples of the kind of thing you want more of
- steps to take before declaring a piece finished

What does not belong here: the standards your work is *judged* by. Those are the
Constitution, and they change by amendment so that a dated, agreed record exists
of what the bar was when something passed. A skill that tries to relax a rule
will be ignored by the auditor, which never sees this file.

`applies_to` above is optional: a comma-separated list of path prefixes. Without
it the skill is in force for every round; with it, only when the round touches
those paths.
"""
