"""Builtin deterministic checks, ported from checks/ and made tree-driven.

Each is mechanical: the same bytes always yield the same findings, and nothing
here consults a model. Rule IDs match the shipped Constitution template.
"""
from __future__ import annotations

import json
import re
from typing import Mapping

import yaml

from .framework import (ADVISORY, BLOCKER, Finding, register,
                        scope_started)


def _load_json(files: Mapping[str, bytes], name: str) -> tuple[dict | None, list[Finding]]:
    raw = files.get(name)
    if raw is None:
        return None, []
    try:
        return json.loads(raw.decode("utf-8")), []
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, [Finding(BLOCKER, "CA-META-001", name, f"unparsable JSON: {exc}")]


def _results_files(files: Mapping[str, bytes]) -> list[str]:
    return [p for p in files if p.endswith("results.json")]


#: The one source-locator fragment `check_provenance` will look past: a line
#: span, anchored to the end. Digits are bounded because `int()` refuses a
#: 4301-digit string, and an unbounded pattern is only ever matched here to be
#: discarded. Nothing else containing `#` is treated as a fragment.
_SPAN_FRAGMENT = re.compile(r"#L\d{1,9}(?:-L\d{1,9})?$")


def _declared_inputs(files: Mapping[str, bytes]) -> list[tuple[str, str]]:
    """Every `(metadata path, inputs entry)` pair, in file order."""
    out: list[tuple[str, str]] = []
    for m in sorted(p for p in files if p.endswith("metadata.yml")):
        try:
            doc = yaml.safe_load(files[m].decode("utf-8")) or {}
        except Exception:                                  # reported by check_schema
            continue
        if not isinstance(doc, dict):
            continue
        raw = doc.get("inputs")
        for item in (raw if isinstance(raw, list) else []):
            if isinstance(item, str) and item.strip():
                out.append((m, item.strip()))
    return out


def check_schema(files: Mapping[str, bytes]) -> list[Finding]:
    """Every increment declares metadata and results, and both must parse."""
    out: list[Finding] = []
    if not scope_started(files):
        # Nothing has been started. Reporting two BLOCKERs here told a brand-new
        # user their project was blocked with two hard failures before they had
        # written anything — absence read as failure. The verdict layer reports
        # NOTHING_TO_AUDIT, which is neither pass nor fail.
        return out
    results = _results_files(files)
    if not results:
        out.append(Finding(BLOCKER, "CA-META-001", "increment",
                           "no results.json in the audited scope"))
    metas = [p for p in files if p.endswith("metadata.yml")]
    if not metas:
        out.append(Finding(BLOCKER, "CA-META-001", "increment",
                           "no metadata.yml in the audited scope"))
    for m in metas:
        try:
            doc = yaml.safe_load(files[m].decode("utf-8"))
        except (UnicodeDecodeError, yaml.YAMLError) as exc:
            out.append(Finding(BLOCKER, "CA-META-001", m, f"unparsable YAML: {exc}"))
            continue
        if not isinstance(doc, dict):
            out.append(Finding(BLOCKER, "CA-META-001", m, "metadata is not a mapping"))
            continue
        for req in ("code_version", "inputs"):
            if req not in doc:
                out.append(Finding(BLOCKER, "CA-META-001", m,
                                   f"metadata is missing required field {req!r}"))
        declared = doc.get("inputs")
        if "inputs" in doc and (not isinstance(declared, list)
                                or not all(isinstance(item, str) and "@" in item
                                           and all(part.strip() for part in item.rsplit("@", 1))
                                           for item in declared)):
            out.append(Finding(
                BLOCKER, "CA-META-001", m,
                "metadata inputs must be a list of non-empty 'path@revision' strings"))
    for r in results:
        doc, errs = _load_json(files, r)
        out.extend(errs)
        if doc is not None:
            if "quantities" not in doc:
                out.append(Finding(BLOCKER, "CA-META-001", r,
                                   "results.json has no 'quantities' list"))
            elif not isinstance(doc.get("quantities"), list):
                out.append(Finding(BLOCKER, "CA-META-001", r,
                                   "results.json quantities must be a list"))
    return out


def check_units(files: Mapping[str, bytes]) -> list[Finding]:
    """CA-DATA-001: every numeric entry carries a unit and a source."""
    out: list[Finding] = []
    for r in _results_files(files):
        doc, _ = _load_json(files, r)
        if not isinstance(doc, dict):
            continue
        for i, q in enumerate(doc.get("quantities") or []):
            if not isinstance(q, dict):
                out.append(Finding(BLOCKER, "CA-DATA-001", r,
                                   f"quantities[{i}] is not a mapping"))
                continue
            for field in ("unit", "source"):
                if not q.get(field):
                    out.append(Finding(
                        BLOCKER, "CA-DATA-001", r,
                        f"quantities[{i}] ({q.get('name', '?')}) has no {field}"))
    return out


def check_convergence(files: Mapping[str, bytes]) -> list[Finding]:
    """CA-METH-002: unconverged numbers are not results."""
    out: list[Finding] = []
    for r in _results_files(files):
        doc, _ = _load_json(files, r)
        if not isinstance(doc, dict):
            continue
        conv = doc.get("convergence")
        if conv is None:
            continue
        if not isinstance(conv, dict):
            out.append(Finding(BLOCKER, "CA-METH-002", r, "convergence is not a mapping"))
            continue
        if conv.get("converged") is not True:
            out.append(Finding(BLOCKER, "CA-METH-002", r,
                               "convergence.converged is not true"))
        achieved, threshold = conv.get("achieved"), conv.get("threshold")
        if isinstance(achieved, (int, float)) and isinstance(threshold, (int, float)):
            if conv.get("converged") is True and achieved > threshold:
                out.append(Finding(
                    BLOCKER, "CA-METH-002", r,
                    f"converged is true but achieved {achieved} exceeds threshold {threshold}"))
    return out


def check_provenance(files: Mapping[str, bytes]) -> list[Finding]:
    """CA-DATA-003: a declared input must exist, and a quantity's source must be
    among the declared inputs.

    The existence half closes PROVENANCE_CHECKS.md §1: membership alone let a
    quantity cite `data/runs.csv@v3`, listed in metadata.yml, that nobody had
    written — a name that names nothing, passing a check called provenance.

    It lives HERE rather than by adding the neutral pack's `declared` to the
    science profile, which is where this started. `check_declared` reads every
    YAML's `sources`, `requires` and `depends_on` as filenames too, so turning
    it on for science blocked legitimate metadata (`sources: [doi:10.1234/x]`,
    `requires: [python>=3.11]`) — false non-overridable blockers on correct
    work, which is the one failure this whole line exists to avoid. `inputs` is
    the single key whose entries the schema already defines as `path@revision`
    (`check_schema`), so it is the single key where existence is a fact and not
    a guess.
    """
    out: list[Finding] = []
    for meta, item in _declared_inputs(files):
        ref = item.rpartition("@")[0] or item
        if ref.startswith(("http://", "https://")):
            continue
        if not any(p == ref or p.endswith("/" + ref) for p in files):
            out.append(Finding(
                BLOCKER, "CA-DATA-003", meta,
                f"inputs declares {ref!r}, which is not in the audited scope; a "
                f"quantity may not cite an input that was never committed"))
    declared: set[str] = set()
    code_versions: set[str] = set()
    for m in (p for p in files if p.endswith("metadata.yml")):
        try:
            doc = yaml.safe_load(files[m].decode("utf-8")) or {}
        except Exception:                                  # reported by check_schema
            continue
        if isinstance(doc, dict):
            for item in doc.get("inputs") or []:
                if isinstance(item, str):
                    declared.add(item.strip())
            if doc.get("code_version"):
                code_versions.add(str(doc["code_version"]))
    if not declared:
        return out
    for r in _results_files(files):
        doc, _ = _load_json(files, r)
        if not isinstance(doc, dict):
            continue
        for i, q in enumerate(doc.get("quantities") or []):
            if not isinstance(q, dict):
                continue
            src = str(q.get("source") or "")
            if not src:
                continue                                   # reported by check_units
            # Additive widening (PROVENANCE_CHECKS.md §2.1): a source may name a
            # SPAN, `path@revision#L14`, so a number can be traced to the line
            # that holds it and not merely to a file that was declared.
            #
            # Narrow on purpose, and in this order. The exact-membership test on
            # the WHOLE string runs first, so a committed file legitimately named
            # `runs#raw.csv` keeps passing byte-for-byte. Only when that fails is
            # a fragment considered, and only one that is exactly `#L<digits>`
            # (optionally `-L<digits>`) at the very end. Splitting on the first
            # `#` instead — which is what this line did in review — silently
            # accepted `runs.csv@v3#garbage` and `runs.csv@v3#other@evil`, both
            # of which used to block, and broke the hash-named file. Everything
            # that is not that one shape keeps the old behaviour exactly.
            candidate = src
            if candidate not in declared:
                fragment = _SPAN_FRAGMENT.search(candidate)
                if fragment:
                    candidate = candidate[:fragment.start()]
            path, sep, rev = candidate.rpartition("@")
            if not sep or candidate not in declared:
                out.append(Finding(
                    BLOCKER, "CA-DATA-003", r,
                    f"quantities[{i}] source {src!r} is not an exact member of "
                    f"metadata inputs {sorted(declared)!r}"))
            elif rev and code_versions and rev not in code_versions:
                out.append(Finding(
                    ADVISORY, "CA-DATA-003", r,
                    f"quantities[{i}] source revision {rev!r} differs from the declared "
                    f"code_version {sorted(code_versions)}"))
    return out


register("schema", check_schema, "Every audited increment contains parseable metadata.yml "
         "with code_version and an inputs list of 'path@revision' strings, plus parseable "
         "results.json with a quantities list.")
register("units", check_units, "Every entry in results.json quantities is a mapping with "
         "non-empty unit and source fields.")
register("convergence", check_convergence, "When results.json has convergence, it is a "
         "mapping whose converged field is true; numeric achieved must not exceed numeric "
         "threshold.")
register("provenance", check_provenance, "Every local path declared in metadata.yml "
         "inputs exists in the audited scope (an input kept outside the configured "
         "scope directories must be brought into it, or into the increment, to be "
         "seen), and each quantity source exactly equals one 'path@revision' string "
         "in those inputs, optionally followed by a '#L14' span fragment that this "
         "check ignores and number_source verifies; a matching source revision "
         "different from code_version is additionally recorded as advisory.")
