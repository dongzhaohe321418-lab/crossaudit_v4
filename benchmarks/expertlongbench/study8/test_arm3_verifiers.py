"""The instrument, checked before the arm runs. No model, no key, no corpus.

Arm 3's two verifiers live in the harness (`provenance_arm3.py`), so nothing
under `src/` guards them. These are the §4 mutation fixtures from
`docs/design/PROVENANCE_ADDRESSING.md` written as assertions: each one names the
mutation it would redden, so a verifier that quietly stops discriminating is
caught here rather than in the report.

    python3 benchmarks/expertlongbench/study8/test_arm3_verifiers.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent.parent / "src"))

from provenance_arm3 import (GUTTER, number_text, gutter_build_prompt,   # noqa: E402
                             verify_a, verify_b)

DRAFT = "work/synthesis/explanation.md"
SRC = "work/synthesis/RECIPE.md"

BODY = (
    "# Source material\n"                       # 1
    "\n"                                        # 2
    "Step 1. Dissolve 5 g of precursor.\n"      # 3
    "Step 2. Calcination: 950 C for 1 h.\n"     # 4
    "Step 3. Anneal for 2 hours at 300 C.\n"    # 5
    "Step 4. Dissolve 5 g of precursor.\n"      # 6
)
FILES = {SRC: BODY.encode("utf-8"), DRAFT: b"draft\n"}

FAILURES: list[str] = []


def check(label: str, got, want) -> None:
    if got != want:
        FAILURES.append(f"{label}: got {got!r}, want {want!r}")


def sev(result):
    return (result[0], result[1])


# --------------------------------------------------------------- contract A

check("A: the named line holds the pair",
      sev(verify_a(FILES, DRAFT, {"v": "950", "u": "C", "src": f"{SRC}#L4"})),
      ("PASS", "pass"))
# §4 row 1: `#L11` -> `#L12`.
check("A: one line off is CA-NUM-002",
      sev(verify_a(FILES, DRAFT, {"v": "950", "u": "C", "src": f"{SRC}#L5"})),
      ("BLOCKER", "CA-NUM-002"))
# §4 row 3: widening the span to the whole file must NOT be what A checks — the
# span is checked, and a range that covers the file is a range the writer named.
check("A: a range the writer names is the span it names",
      sev(verify_a(FILES, DRAFT, {"v": "950", "u": "C", "src": f"{SRC}#L1-L6"})),
      ("PASS", "pass"))
check("A: a path outside the increment is CA-NUM-001",
      sev(verify_a(FILES, DRAFT, {"v": "950", "u": "C", "src": "work/nope.md#L4"})),
      ("BLOCKER", "CA-NUM-001"))
check("A: a line past the end is CA-NUM-001",
      sev(verify_a(FILES, DRAFT, {"v": "950", "u": "C", "src": f"{SRC}#L99"})),
      ("BLOCKER", "CA-NUM-001"))
check("A: `at` is not a field and its absence is not a defect",
      sev(verify_a(FILES, DRAFT, {"v": "5", "u": "g", "src": f"{SRC}#L3"})),
      ("PASS", "pass"))
check("A: uncited is advisory",
      sev(verify_a(FILES, DRAFT, {"v": "180", "u": "C", "src": "uncited"})),
      ("ADVISORY", "CA-NUM-003"))
check("A: a row with two fields cannot be checked",
      sev(verify_a(FILES, DRAFT, {"v": "5", "src": f"{SRC}#L3"})),
      ("BLOCKER", "CA-NUM-001"))
# The shared verification half: the synonym table, and no shortened unit.
check("A: hours/h is one unit",
      sev(verify_a(FILES, DRAFT, {"v": "2", "u": "h", "src": f"{SRC}#L5"})),
      ("PASS", "pass"))


# --------------------------------------------------------------- contract B

def q(text, file=SRC, **extra):
    return {"file": file, "quote": text, **extra}


check("B: an exactly copied quote holding the pair passes",
      sev(verify_b(FILES, DRAFT, {"v": "950", "u": "C",
                                  "src": q("Calcination: 950 C for 1 h")})),
      ("PASS", "pass"))
# §4 mutation: alter one character inside the quote -> CA-NUM-001.
check("B: one character changed is CA-NUM-001",
      sev(verify_b(FILES, DRAFT, {"v": "950", "u": "C",
                                  "src": q("Calcinatian: 950 C for 1 h")})),
      ("BLOCKER", "CA-NUM-001"))
# §4 mutation: drop the uniqueness count -> the duplicate fixture stops being
# advisory. Lines 3 and 6 are identical.
check("B: a quote the file holds twice is ADVISORY, never a blocker",
      sev(verify_b(FILES, DRAFT, {"v": "5", "u": "g",
                                  "src": q("Dissolve 5 g of precursor.")})),
      ("ADVISORY", "CA-NUM-004"))
# §4 mutation: drop the contains_pair clause -> a quote that resolves without
# holding the pair goes green.
check("B: a quote that resolves without the pair is CA-NUM-002",
      sev(verify_b(FILES, DRAFT, {"v": "950", "u": "C",
                                  "src": q("Step 3. Anneal for 2 hours")})),
      ("BLOCKER", "CA-NUM-002"))
# §4 mutation: remove the 80-char cap -> the whole-file-as-quote fixture goes
# green, restoring the 27.7% coincidental pass rate.
check("B: a quote over 80 characters cannot be a span",
      sev(verify_b(FILES, DRAFT, {"v": "950", "u": "C", "src": q(BODY.strip())})),
      ("BLOCKER", "CA-NUM-001"))
# §4 mutation: let the matcher accept a PREFIX of the quote.
check("B: a prefix of the quote is not the quote",
      sev(verify_b(FILES, DRAFT, {"v": "950", "u": "C",
                                  "src": q("Calcination: 950 C for 1 h.EXTRA")})),
      ("BLOCKER", "CA-NUM-001"))
# The single normalisation, on both sides: a line break inside the quote is a
# space, and nothing else is folded.
check("B: a newline inside the quote is a space",
      sev(verify_b(FILES, DRAFT, {"v": "950", "u": "C",
                                  "src": q("Calcination:\n  950 C for 1 h")})),
      ("PASS", "pass"))
check("B: case is not folded",
      sev(verify_b(FILES, DRAFT, {"v": "950", "u": "C",
                                  "src": q("calcination: 950 C for 1 h")})),
      ("BLOCKER", "CA-NUM-001"))
check("B: a file outside the increment is CA-NUM-001",
      sev(verify_b(FILES, DRAFT, {"v": "950", "u": "C",
                                  "src": q("Calcination: 950 C for 1 h",
                                           file="work/nope.md")})),
      ("BLOCKER", "CA-NUM-001"))
check("B: a bare span locator is not B's grammar",
      sev(verify_b(FILES, DRAFT, {"v": "950", "u": "C", "src": f"{SRC}#L4"})),
      ("BLOCKER", "CA-NUM-001"))
check("B: uncited is advisory",
      sev(verify_b(FILES, DRAFT, {"v": "180", "u": "C", "src": "uncited"})),
      ("ADVISORY", "CA-NUM-003"))
check("B: hours/h is one unit here too",
      sev(verify_b(FILES, DRAFT, {"v": "2", "u": "h",
                                  "src": q("Anneal for 2 hours at 300 C")})),
      ("PASS", "pass"))
check("B: a shortened unit does not satisfy the whole token",
      sev(verify_b(FILES, DRAFT, {"v": "1", "u": "",
                                  "src": q("Calcination: 950 C for 1 h")})),
      ("PASS", "pass"))


# ---------------------------------------------------------- contract A's gutter

numbered = number_text("alpha\nbeta\ngamma")
check("A: the gutter is 1-based, per file, over split('\\n')",
      numbered.split("\n"),
      [GUTTER.format(1) + "alpha", GUTTER.format(2) + "beta",
       GUTTER.format(3) + "gamma"])

seen: dict = {}


def _inner(**kw):
    seen.update(kw)
    return "prompt"


wrapped = gutter_build_prompt(_inner)
wrapped(current={"work/a.md": "one\ntwo",
                 "work/big.md": "<large file elided: 90000 bytes. Structural "
                                "outline only —>\n--- outline ---\n# h"},
        task="t")
check("A: a verbatim file is numbered",
      seen["current"]["work/a.md"], GUTTER.format(1) + "one\n" + GUTTER.format(2) + "two")
check("A: an elided file is NOT numbered",
      seen["current"]["work/big.md"].startswith("<large file elided:"), True)

if FAILURES:
    print("FAILED:")
    for line in FAILURES:
        print("  " + line)
    raise SystemExit(1)
print("arm 3 verifier fixtures: all pass")
