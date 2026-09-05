"""Named check profiles — strictness as a legible dial, not a flat name list.

CrossAudit's identity (independent cross-vendor audit, evidence ledger, signed
receipts, per-call human approval) is always on and domain-agnostic. The
deterministic checks are an OPTIONAL rigor layer on top, and `checks:` in
``crossaudit.yml`` selects how much of it runs. Rather than hand-listing opaque
check names, a project can name a profile:

    off      core audit chain only (no deterministic checks)
    general  the domain-neutral pack — the light default: parses, dangling
             declarations, broken links (advisory), leftover placeholders
             (advisory). Binds no data format; fits code, docs, web, contracts.
    science  structured-science rigor: schema, units, convergence, provenance
             (inputs that exist and are cited exactly).

An explicit list is still accepted verbatim, so a project can compose its own mix
(e.g. the general pack plus ``complete-strict`` to make placeholders hard-fail).
"""
from __future__ import annotations

from ..errors import ConfigDenial

#: Named profiles → the check list each expands to. Kept minimal and honest:
#: exactly the packs that exist today, now addressable by name.
PROFILES: dict[str, list[str]] = {
    "off": [],
    "general": ["parseable", "declared", "internal", "complete"],
    # §1's gap — a quantity citing an input that is listed and does not exist —
    # is closed INSIDE `check_provenance`, not by adding the neutral pack's
    # `declared` here. `declared` reads every YAML's `sources`, `requires` and
    # `depends_on` as filenames as well, so bringing it into science blocked
    # legitimate metadata (`sources: [doi:10.1234/x]`); the profile stays as it
    # was and the check got stronger, which is the direction that is allowed.
    #
    # `number_source` is NOT here, and its absence is D158's first ruling.
    # D157 put it in both profiles; Arm 2
    # (`benchmarks/expertlongbench/RESULTS-ARM2.md`) then ran it against what a
    # real generator writes under the shipped skill and **no annotation row of
    # 215 passed, 24 of 24 drafts BLOCKED** — not because the verifier was
    # wrong about a span (it was wrong zero times in 189 blocks) but because
    # the generator is never shown line numbers (`generator.py:449-450`) and so
    # cannot address the lines the contract asks it to name. A check that
    # blocks every project that enables it does not belong in a profile a
    # project selects by name. It stays REGISTERED and selectable by explicit
    # name (`checks: [..., number_source]`) — nothing is unregistered, and the
    # addressing contract goes back to design (D158 ruling 2) before it may
    # re-enter any profile (ruling 3). This returns both lists to their
    # pre-D157 state; it removes nothing that existed before that day.
    "science": ["schema", "units", "convergence", "provenance"],
    # The general pack plus the opt-in, deterministic citation-provenance check:
    # a report may only cite sources it fetched through a governed research tool.
    "research": ["parseable", "declared", "internal", "complete", "source_provenance"],
}

DEFAULT_PROFILE = "general"


def resolve(value) -> list[str]:
    """Turn a `checks:` value into the concrete check list.

    Accepts a profile name (``"general"``), an explicit list of check names
    (returned verbatim, so custom mixes keep working), or an empty list (which
    means exactly "no checks", never the default). An unknown profile name denies
    rather than silently running the wrong rigor.
    """
    if isinstance(value, str):
        name = value.strip()
        if name not in PROFILES:
            raise ConfigDenial(
                f"unknown check profile {name!r}; choose one of "
                f"{sorted(PROFILES)} or list check names explicitly")
        return list(PROFILES[name])
    if isinstance(value, list):
        if not all(isinstance(item, str) for item in value):
            raise ConfigDenial("checks must be a profile name or a list of check names")
        return list(value)
    raise ConfigDenial("checks must be a profile name or a list of check names")
