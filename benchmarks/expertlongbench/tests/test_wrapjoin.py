"""The wrap-join rule of study 15's wrap-join slice (`PREREGISTRATION-WRAPJOIN.md` §1):
which breaks are joined, which are kept, the mapping, the round trip — and that the
SHIPPED matcher, unmodified, locates a two-line quotation once the file is joined."""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "study15"))

from wrapjoin import join_wraps, joined_increment, joined_line_index  # noqa: E402


def _fold(text: str) -> str:
    return " ".join(text.split())


# ------------------------------------------------------------------ join cases

@pytest.mark.parametrize("text", [
    "alpha beta gamma\ndelta epsilon",                   # a plain hard wrap
    "ends with a stop.\nNext sentence starts capital",   # punctuation and case are not read
    "   leading indent\n   continues indented",          # indentation is not a marker
    "first line 2024\n12 lines later",                   # a digit-led line is not a list item
    "first line\nQ. a letter and a stop is not a marker",
    "first line\n(a) a parenthesised enumerator is not a marker",
    "first line\n1.5 is a number, not an ordered marker",
    "first line\n1.no space after the stop",
])
def test_joined_breaks(text):
    joined, mapping = join_wraps(text)
    assert joined.count("\n") == 0, (text, joined)
    assert mapping == [(0, 1)]
    assert _fold(joined) == _fold(text)


def test_a_joined_break_becomes_one_space_and_drops_the_edges_whitespace():
    joined, _ = join_wraps("alpha   \n   beta")
    assert joined == "alpha beta"


@pytest.mark.parametrize("text", [
    "a\n\nb",                       # a blank line
    "a\n# heading",                 # ATX heading after
    "# heading\na",                 # ATX heading before
    "a\n## second-level",
    "a\n- bullet",                  # bullets
    "a\n* bullet",
    "a\n+ bullet",
    "a\n1. ordered",                # ordered-list markers
    "a\n12) ordered",
    "a\n| cell | cell |",           # table rows
    "| cell |\na",
    "a\n> quoted",                  # blockquote
    "a\n---",                       # thematic break / setext underline
    "===\na",
    "a\n```",                       # a fence line
])
def test_kept_breaks(text):
    joined, mapping = join_wraps(text)
    assert joined == text, (text, joined)
    assert mapping == [(0, 0), (1, 1)] or (text.count("\n") == 2 and mapping == [(0, 0), (1, 1), (2, 2)])


def test_no_break_inside_a_code_fence_is_joined():
    text = "para one\ncontinues\n```\ncode line\nanother\n```\npara two\ncontinues"
    joined, mapping = join_wraps(text)
    assert joined == "para one continues\n```\ncode line\nanother\n```\npara two continues"
    assert mapping == [(0, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 7)]


def test_a_wrapped_list_item_is_joined_but_the_next_item_is_not():
    text = "- first item wrapped\n  onto a second line\n- second item"
    joined, mapping = join_wraps(text)
    assert joined == "- first item wrapped onto a second line\n- second item"
    assert mapping == [(0, 1), (2, 2)]


def test_a_hash_without_a_space_is_not_a_heading():
    joined, _ = join_wraps("docket\n#12345 continues")
    assert joined == "docket #12345 continues"


# --------------------------------------------------------------- the mapping

def _random_doc(rng: random.Random, n: int) -> str:
    pool = ["plain words here", "more plain text", "", "# heading", "- bullet", "3. item",
            "| a | b |", "> quote", "```", "---", "   indented text", "12 digit led"]
    return "\n".join(rng.choice(pool) for _ in range(n))


@pytest.mark.parametrize("seed", range(20))
def test_mapping_partitions_the_original_lines_and_every_joined_line_folds_to_its_span(seed):
    rng = random.Random(seed)
    text = _random_doc(rng, rng.randrange(1, 40))
    original = text.split("\n")
    joined, mapping = join_wraps(text)
    jl = joined.split("\n")
    assert len(jl) == len(mapping)
    # the spans partition the original lines, in order
    expect = 0
    for start, end in mapping:
        assert start == expect and end >= start
        expect = end + 1
    assert expect == len(original)
    # round trip: every joined line folds to the fold of the original lines it maps to
    for k, (start, end) in enumerate(mapping):
        assert _fold(jl[k]) == _fold("\n".join(original[start:end + 1]))
    assert _fold(joined) == _fold(text)


def test_empty_and_single_line_texts():
    assert join_wraps("") == ("", [(0, 0)])
    assert join_wraps("one line") == ("one line", [(0, 0)])
    assert join_wraps("\n") == ("\n", [(0, 0), (1, 1)])


# ---------------------------------------- the shipped matcher on joined files

def test_the_shipped_matcher_unmodified_locates_a_two_line_quotation_after_the_join():
    """`located_line` and `verify_shipped` are Arm 4's functions over `numbers._quote_span`
    and `numbers._row_findings`; nothing is patched. Before the join the quotation crosses
    a line break (BLOCKER, quote-crosses-line); after it the row is located and passes."""
    sys.path.insert(0, str(HERE.parent))
    import provenance_arm4 as arm4
    from run import OUTPUT_PATH
    from crossaudit.dcl import numbers as num_mod

    source = ("# Title\n\nThe court awarded the plaintiff a sum of\n"
              "12,500 dollars on the third day of the hearing.\n\nAnother paragraph.\n")
    files = {OUTPUT_PATH: b"draft\n", "work/synthesis/RECIPE.md": source.encode()}
    row = {"v": "12,500", "u": "dollars",
           "src": {"file": "work/synthesis/RECIPE.md",
                   "quote": "a sum of 12,500 dollars on the third"}}
    assert arm4.verify_shipped(files, row, "draft\n") == ("BLOCKER", "CA-NUM-002", "quote-crosses-line")
    assert arm4.located_line(files, row) is None

    jfiles, mappings = joined_increment(files, OUTPUT_PATH)
    assert jfiles[OUTPUT_PATH] == b"draft\n"                        # the draft is never joined
    assert arm4.verify_shipped(jfiles, row, "draft\n") == ("PASS", "pass", "")
    loc = arm4.located_line(jfiles, row)
    assert loc is not None and loc[2] == 1
    joined_text = jfiles["work/synthesis/RECIPE.md"].decode()
    idx = joined_line_index(joined_text, row["src"]["quote"], num_mod._fold)
    assert idx is not None
    assert mappings["work/synthesis/RECIPE.md"][idx] == (2, 3)     # original lines 3–4, 1-based


def test_joined_line_index_is_none_when_the_quotation_is_absent_or_on_two_lines():
    assert joined_line_index("alpha beta\ngamma", "delta", _fold) is None
    assert joined_line_index("alpha beta\nalpha beta", "alpha", _fold) is None
    assert joined_line_index("alpha beta\ngamma", "alpha", _fold) == 0
