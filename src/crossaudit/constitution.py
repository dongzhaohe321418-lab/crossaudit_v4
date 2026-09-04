"""Distilling spoken requirements into a committed Constitution (P3).

The user says what the project is and what they are afraid of getting wrong.
This module turns that into numbered, severity-tagged rules, shows them, and —
only after a nod — writes them as a file that git versions and receipts cite.

Two properties the distillation must preserve:

* **Nothing is invented silently.** Every drafted rule carries the fragment of
  the user's own words it came from, so a reader can check the translation.
* **The draft is never law until committed.** Audits run against the committed
  file at a commit hash; a draft in memory is a proposal, and the difference is
  the whole of P3.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .errors import ConfigDenial, ProviderDenial

RULE_ID = re.compile(r"^CA-[A-Z]{2,10}-\d{3}$")
SEVERITIES = ("BLOCKER", "ADVISORY")

#: The two projections of one committed rulebook.
#:
#: The FILE stays the single artefact a human edits, the ledger binds and a
#: receipt cites. These are the two *views* derived from it, and they are
#: deliberately not the same text — because the measurement said one text
#: cannot serve both readers. Study 2 (benchmarks/expertlongbench/RESULTS-2.md):
#: rules naming what the work is graded on took the auditor's round-one recall
#: against ground truth from 2.0 % to 15.5 %, and took the generator's first
#: draft from 14.7 to 3.3 F1, because the same file reached both. A grader's
#: checklist read by a writer becomes an outline.
AUDIENCE_AUDITOR = "criteria"
AUDIENCE_GENERATOR = "brief"

#: A rule opts into the writer's brief by carrying this marker inside its block.
#: An HTML comment, so a rulebook stays a document a person reads and an older
#: reader ignores it. Unmarked rules are acceptance criteria: the reviewer's.
BRIEF_MARKER = "<!-- brief -->"

#: Rules that are in the brief without a marker, because they describe the
#: SHAPE of the deliverable rather than grade its content. CA-TASK-001 is
#: protocol law about count, file type, named subject, inclusions and length —
#: a writer that is not told those cannot produce the right artefact at all.
RESERVED_BRIEF_RULES = ("CA-TASK-001",)

#: Rule headings, in the one style every template and `Rule.render` emits. Kept
#: deliberately identical in shape to `auditor.validate.RULE_HEADING`: if the
#: style ever drifts, both stop seeing rules loudly rather than one of them
#: quietly disagreeing with the other about what the rulebook contains.
RULE_HEADING = re.compile(r"^###\s+(CA-[A-Z]+-\d+)", re.M)
#: The period sits INSIDE the emphasis in every template and in `Rule.render`
#: (`**BLOCKER.**`), so a pattern that forgets it silently reports every rule as
#: a BLOCKER — which is the one direction that misinforms a writer.
_SEVERITY_IN_BLOCK = re.compile(r"\*\*(BLOCKER|ADVISORY)\.?\*\*")
#: A standalone horizontal rule closes the rules section in every template
#: here; what follows it is editing guidance for the human, not a rule.
_SECTION_BREAK = re.compile(r"^---\s*$", re.M)


def split_rules(text: str) -> tuple[str, list[tuple[str, str]]]:
    """(preamble, [(rule_id, block)]) for a committed rulebook.

    Format-agnostic on purpose: the shipped templates write
    ``### ID\n**BLOCKER.** <criterion>`` and `Rule.render` writes
    ``### ID\n**BLOCKER.** <title>\n\n<criterion>``. Both are one heading
    followed by a block, and nothing downstream needs to tell them apart.
    """
    marks = list(RULE_HEADING.finditer(text))
    if not marks:
        return text, []
    preamble = text[: marks[0].start()]
    blocks: list[tuple[str, str]] = []
    for index, mark in enumerate(marks):
        end = marks[index + 1].start() if index + 1 < len(marks) else len(text)
        block = text[mark.start():end]
        # The last block would otherwise swallow the file's closing guidance.
        if index + 1 == len(marks) and (cut := _SECTION_BREAK.search(block)):
            block = block[: cut.start()]
        blocks.append((mark.group(1), block))
    return preamble, blocks


def is_brief_rule(rule_id: str, block: str) -> bool:
    """Whether this rule describes the work (brief) or grades it (criteria)."""
    return rule_id in RESERVED_BRIEF_RULES or BRIEF_MARKER in block


def rule_severity(block: str) -> str:
    """The rule's severity, or `unstated` — never a guess dressed as a fact."""
    found = _SEVERITY_IN_BLOCK.search(block)
    return found.group(1) if found else "unstated"


#: Fixed text. It must not vary with the rulebook's content, or the very
#: criteria it exists to withhold would leak back through it.
BRIEF_HEADER = """\
<!-- The writer's projection of the committed rules. The rules file itself is
     unchanged and is what the auditor reads and the receipt binds. -->
This is what your work must satisfy. It carries the requirements that describe
the deliverable itself. It deliberately does not carry the acceptance criteria
the reviewer applies to finished work: those are a checklist for judging, not
an outline to write to. Do the work the task asks for; do not organise it
around rule ids.
"""
BRIEF_NO_SHAPE_RULES = (
    "No rule in this rulebook describes the shape of the deliverable. The task "
    "and the machine-enforced file contract are what fix it.")
BRIEF_ROSTER_HEADER = (
    "You will also be audited against the rules below. Their criteria are the "
    "reviewer's and are not shown here.")


def criteria_projection(text: str) -> str:
    """What the auditor is given: the committed rulebook, byte for byte.

    The identity function, and that is the point. The auditor's view does not
    move under this change — it still sees only committed bytes, and a rulebook
    written to be checkable is exactly what the measurement says it needs. What
    changes is only that such a rulebook no longer reaches the writer as well.
    """
    return text


def brief_projection(text: str) -> str:
    """What the generator is given: the brief, derived from the same bytes.

    The rulebook's own preamble, the full text of every shape rule, and a bare
    roster of the rest. A pure function of the committed file: it adds nothing
    the file does not contain, so nothing the writer is told escapes the
    artefact the receipt binds.
    """
    preamble, blocks = split_rules(text)
    shape = [(rid, block) for rid, block in blocks if is_brief_rule(rid, block)]
    graded = [(rid, block) for rid, block in blocks if not is_brief_rule(rid, block)]

    # The preamble's closing horizontal rule introduced the rules; what follows
    # it here is the brief, so it would introduce the wrong thing.
    parts = [_SECTION_BREAK.sub("", preamble).strip(), BRIEF_HEADER]
    if shape:
        parts.append("## Requirements on the deliverable")
        parts.extend(block.replace(BRIEF_MARKER, "").strip() for _rid, block in shape)
    else:
        parts.append(BRIEF_NO_SHAPE_RULES)
    if graded:
        roster = " · ".join(f"{rid} ({rule_severity(block)})"
                            for rid, block in graded)
        parts.append(f"## Applied to your work by the reviewer\n\n"
                     f"{BRIEF_ROSTER_HEADER}\n\n{roster}")
    return "\n\n".join(part for part in parts if part).rstrip() + "\n"


def projection_digests(text: str) -> dict:
    """What each role received, as digests a verifier re-derives (never trusts)."""
    def sha(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    return {
        "auditor": {"name": AUDIENCE_AUDITOR,
                    "sha256": sha(criteria_projection(text))},
        "generator": {"name": AUDIENCE_GENERATOR,
                      "sha256": sha(brief_projection(text))},
    }

DISTIL_SYSTEM = """You turn a person's description of their project into audit \
rules. You are not writing an essay; you are drafting law that another model \
will apply mechanically to committed files.

Rules of drafting:
- Each rule needs a stable ID (CA-<AREA>-<NNN>, area is 2-10 uppercase letters), \
a severity, and a criterion decidable by reading the artefacts. If a reviewer \
could argue either way about whether a rule was met, either sharpen it or make \
it ADVISORY.
- BLOCKER is for objective defects that must stop the work: internal \
contradiction, missing provenance, unsupported claim, declared-but-absent \
artefact. ADVISORY is for judgement: style, taste, scope, suggestions.
- Draft between 3 and 10 rules. Prefer few sharp rules to many vague ones.
- Every rule must quote the fragment of the user's own words it came from, in \
`from_user`. If a rule follows from the domain rather than from something the \
user said, put the empty string and say so in the criterion.
- Do not invent domain requirements the user did not imply. You are translating, \
not advising.
- Do not draft CA-TASK-001. CrossAudit adds that reserved baseline rule itself so \
every project is required to satisfy the user's committed task.
- Set `brief: true` only for a rule that describes the SHAPE of the deliverable — \
its format, structure, length, which files exist, what must be declared. Those \
are shown to the writer. Everything else is `brief: false`: a criterion a \
reviewer applies to finished work is shown to the reviewer only, because a \
writer handed a grading checklist writes to the checklist instead of the task.

Reply with exactly one JSON object and nothing else:
{"project_summary": "one sentence, the project in the user's own terms",
 "domain": "short label, e.g. literature-review, web-app, contract-review",
 "rules": [{"id": "CA-DATA-001", "severity": "BLOCKER",
            "title": "short imperative title",
            "criterion": "what must hold, decidably",
            "from_user": "the fragment this came from",
            "brief": false}]}"""

AMEND_SYSTEM = """You amend an existing rulebook from a person's instruction. \
You will be given the current rules and one sentence of intent.

Produce the smallest change that satisfies the intent:
- To tighten or add: a new rule, or a sharpened criterion on an existing one.
- To loosen: lower a BLOCKER to ADVISORY, or narrow its criterion. Never delete \
a rule silently; a removal must be stated as such with its reason.
- Keep every untouched rule byte-identical.

Reply with exactly one JSON object and nothing else:
{"intent": "what you understood the person to want",
 "changes": [{"action": "add"|"modify"|"remove", "id": "CA-...",
              "was": "prior criterion or empty", "now": "new criterion or empty",
              "severity": "BLOCKER"|"ADVISORY", "title": "...",
              "why": "one line, tied to what the person said"}]}"""


@dataclass
class Rule:
    id: str
    severity: str
    title: str
    criterion: str
    from_user: str = ""
    #: Whether this rule describes the SHAPE of the deliverable (and so belongs
    #: in the writer's brief) or grades its content (and so is the reviewer's
    #: alone). Default False: a criterion body does not reach the writer unless
    #: someone says it describes the work rather than judges it.
    brief: bool = False

    def validate(self) -> None:
        if not RULE_ID.match(self.id):
            raise ConfigDenial(f"rule id {self.id!r} is not of the form CA-AREA-NNN")
        if self.severity not in SEVERITIES:
            raise ConfigDenial(f"rule {self.id}: severity must be one of {SEVERITIES}")
        if not self.criterion.strip():
            raise ConfigDenial(f"rule {self.id}: a rule with no criterion is not a rule")

    def render(self) -> str:
        origin = (f"\n<!-- from the user: \"{self.from_user.strip()}\" -->"
                  if self.from_user.strip() else "")
        # An HTML comment, invisible where the file is read as Markdown, so the
        # audience of a rule is declared in the artefact a human edits rather
        # than in configuration none of them will find.
        audience = f"\n{BRIEF_MARKER}" if self.brief else ""
        return (f"### {self.id}\n**{self.severity}.** {self.title.strip()}\n\n"
                f"{self.criterion.strip()}{origin}{audience}\n")


def universal_task_rule() -> Rule:
    """The non-optional bridge between a user's task and every audit."""
    return Rule(
        id="CA-TASK-001",
        severity="BLOCKER",
        title="Satisfy the committed task",
        criterion=(
            "When an audit cycle has a committed task, every objectively testable "
            "requirement in that task must be satisfied by the artefacts in scope. "
            "This includes the requested deliverable count, file type or format, "
            "named subject, explicit inclusions or exclusions, and stated length. "
            "A length stated as exact must match exactly. A length stated "
            "approximately is a guide, not a threshold: note it as ADVISORY only "
            "if the artefact departs from it by more than a quarter of the stated "
            "length, and it is not a BLOCKER on its own; a departure so large "
            "that the deliverable is a different thing (a fraction or a multiple "
            "of what was asked) is materially noncompliant under the next "
            "sentence. Someone who writes 'about 300 words' has chosen a word "
            "that does not make 320 wrong. "
            "A missing, substituted, extra, or materially "
            "noncompliant deliverable is a BLOCKER. If no committed task is supplied, "
            "this rule has no additional effect."
        ),
    )


@dataclass
class Draft:
    project_summary: str
    domain: str
    rules: list[Rule]

    def validate(self) -> None:
        if not self.rules:
            raise ConfigDenial("a Constitution with no rules cannot audit anything")
        seen: set[str] = set()
        for r in self.rules:
            r.validate()
            if r.id in seen:
                raise ConfigDenial(f"duplicate rule id {r.id}")
            seen.add(r.id)
        # An advisory-only constitution used to be REFUSED here, on the premise
        # that "nothing can ever gate". That premise was false in two independent
        # ways, and refusing on it made the product unable to be configured to
        # only advise — which is what taught every surface downstream that being
        # valuable means being able to stop someone.
        #
        # 1. The deterministic layer gates on its own. `dcl/framework.py` computes
        #    its own hard_failures and returns BLOCKED without consulting the
        #    constitution at all (it contains no reference to it), and
        #    `auditor/run.py` reads `dcl["total_hard_failures"] > 0 -> BLOCKED`
        #    BEFORE it ever reads the model's verdict. The floor a model cannot
        #    waive was never at risk.
        # 2. `render()` unconditionally prepends CA-TASK-001, which is a BLOCKER.
        #    So the document this check was guarding always contained one anyway,
        #    and the check was testing a property of the draft that the renderer
        #    made moot.
        #
        # No replacement warning is added. The obvious one — "the model reviewer
        # will advise and not block" — would be FALSE while CA-TASK-001 renders as
        # a BLOCKER, and a false reassurance is the thing being removed here.

    def render(self, project: str) -> str:
        head = [
            f"# Constitution — {project}",
            "",
            "Drafted from the project owner's own description and committed here.",
            "Every audit cites the commit that carried this file, so a rule change is",
            "dated and attributable, and takes effect only *between* cycles: no work is",
            "judged against a target that moved under it.",
            "",
            f"**Project.** {self.project_summary.strip()}",
            f"**Domain.** {self.domain.strip()}",
            "",
            "Severities are two. **BLOCKER** is an objective defect and gates the work.",
            "**ADVISORY** is judgement, is recorded, and never gates.",
            "",
            "---",
            "",
        ]
        # CA-TASK-001 is protocol law, not an optional suggestion to the drafting
        # model. Replace any provider-authored rule using its reserved ID so a weak
        # or omitted draft can never disconnect the user's task from the audit.
        rules = [universal_task_rule(),
                 *(r for r in self.rules if r.id != "CA-TASK-001")]
        body = "\n".join(r.render() for r in rules)
        tail = ("\n---\n\n<!-- Amend by talking to CrossAudit: `crossaudit amend "
                "\"from now on ...\"`. Amendments are drafted, shown, confirmed, and "
                "committed; they never take effect mid-cycle. -->\n")
        return "\n".join(head) + body + tail

    @staticmethod
    def from_json(raw: dict) -> "Draft":
        try:
            rules = [Rule(id=str(r["id"]).strip().upper(), severity=str(r["severity"]).strip().upper(),
                          title=str(r["title"]), criterion=str(r["criterion"]),
                          from_user=str(r.get("from_user", "")),
                          brief=bool(r.get("brief", False)))
                     for r in raw["rules"]]
            d = Draft(project_summary=str(raw["project_summary"]),
                      domain=str(raw.get("domain", "unspecified")), rules=rules)
        except (KeyError, TypeError) as exc:
            raise ProviderDenial(f"the drafting model returned an unusable shape: {exc}") from exc
        d.validate()
        return d

    def as_dict(self) -> dict:
        return {"project_summary": self.project_summary, "domain": self.domain,
                "rules": [asdict(r) for r in self.rules]}


def parse_json_reply(text: str) -> dict:
    """Extract the single JSON object from a model reply, tolerating prose around it."""
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"\n?```\s*$", "", s)
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    start, end = s.find("{"), s.rfind("}")
    if start == -1 or end <= start:
        raise ProviderDenial("the drafting model returned no JSON object")
    try:
        return json.loads(s[start:end + 1])
    except json.JSONDecodeError as exc:
        raise ProviderDenial(f"the drafting model returned malformed JSON: {exc}") from exc


def distil(description: str, *, complete) -> Draft:
    """Draft a Constitution from the user's description. `complete` is a provider."""
    if len(description.strip()) < 12:
        raise ConfigDenial(
            "that is too short to draft rules from — say what the project is and "
            "what you are most afraid of getting wrong")
    reply = complete(system=DISTIL_SYSTEM,
                     prompt=f"The project owner says:\n\n{description.strip()}")
    return Draft.from_json(parse_json_reply(reply.text))


def amend(current_rules: str, instruction: str, *, complete) -> dict:
    """Draft the smallest rulebook change satisfying the instruction."""
    if not instruction.strip():
        raise ConfigDenial("an amendment needs an instruction")
    reply = complete(
        system=AMEND_SYSTEM,
        prompt=f"CURRENT RULES\n<<<RULES\n{current_rules}\nRULES\n\n"
               f"THE PERSON SAYS:\n{instruction.strip()}")
    raw = parse_json_reply(reply.text)
    changes = raw.get("changes")
    if not isinstance(changes, list) or not changes:
        raise ProviderDenial("the amendment produced no changes")
    for c in changes:
        if c.get("action") not in ("add", "modify", "remove"):
            raise ProviderDenial(f"unknown amendment action {c.get('action')!r}")
        if not RULE_ID.match(str(c.get("id", ""))):
            raise ProviderDenial(f"amendment names an invalid rule id {c.get('id')!r}")
    return raw


def apply_amendment(constitution: str, change_set: dict) -> str:
    """Apply drafted changes to the rulebook text, appending a dated amendment log.

    Rules are edited in place so the file stays readable, and every change is
    also appended to an amendment section, because a rulebook whose history is
    invisible is one nobody can be held to.
    """
    text = constitution
    for c in change_set["changes"]:
        rid, action = c["id"], c["action"]
        block = (f"### {rid}\n**{c.get('severity', 'BLOCKER')}.** {c.get('title', '').strip()}\n\n"
                 f"{c.get('now', '').strip()}\n")
        pattern = re.compile(rf"^### {re.escape(rid)}\n.*?(?=^### |\Z)", re.M | re.S)
        exists = pattern.search(text) is not None
        # The add/modify distinction is the drafting model's guess about state,
        # not ground truth: "modify" of a missing rule appends, so symmetrically
        # "add" of an existing rule replaces. The one intolerable outcome is a
        # change that edits nothing while the Amendments log below records it as
        # applied — a ledger claiming history that never happened.
        if action == "add":
            if exists:
                text = pattern.sub(block + "\n", text)
            else:
                marker = "\n---\n\n<!-- Amend by talking"
                text = (text.replace(marker, "\n" + block + marker)
                        if marker in text else text + "\n" + block)
        elif action == "modify":
            text = pattern.sub(block + "\n", text) if exists else text + "\n" + block
        elif action == "remove":
            text = pattern.sub("", text)
    log = ["\n\n## Amendments\n"] if "## Amendments" not in text else []
    log.append(f"\n**{change_set.get('intent', 'amendment').strip()}**\n")
    for c in change_set["changes"]:
        log.append(f"- `{c['id']}` {c['action']}: {c.get('why', '').strip()}")
    return text + "\n".join(log) + "\n"


def write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8", newline="\n")
    return path
