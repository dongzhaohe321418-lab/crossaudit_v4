"""number → source: a declared span must resolve and contain the number.

`docs/design/PROVENANCE_CHECKS.md` §2.1/§3.1/§3.4, under D155's surviving rule:
**a model may name evidence; code verifies it exists and says what was claimed;
a model is never asked what the evidence says.**

A text artefact carries one fenced block listing the numbers it wrote and where
each came from:

    ```crossaudit-numbers
    [{"v": "950", "u": "°C", "src": {"file": "work/synthesis/RECIPE.md",
                                     "quote": "Calcine at 950 °C for 1 hour."}},
     {"v": "180", "u": "°C", "src": "uncited"}]
    ```

No field carries a truth value. `v` and `u` transcribe bytes the generator wrote
into its own prose; `src` is an address, and since D159 it is a **content**
address — a file, and a run of characters copied out of one of its lines. The
check asks two mechanical questions and no others:

1. does `src` resolve — is its file in the audited scope, do its declared bytes
   still hash to what it declared, do the quoted characters occur on exactly one
   line of it;
2. does that line contain the transcribed `(value, unit)` pair **inside the
   quoted run**.

The second question is asked in that order for a reason found by review, not by
design: the pair is looked for in the whole LINE and the occurrence is then
required to lie inside the quotation. Reading the quotation on its own instead
crops away the characters that adjoin it, and every boundary rule in this module
— the whole unit token, the sign, the maximal number, `_UNPARSED` — is a rule
about exactly those characters. **The quote says where to look; the line says
what is there.**

**Why the quote and not a line number (D158, D159).** The generator is never
shown line numbers (`generator.py:449-450`), so the line-addressed contract
asked it for a fact it did not have: Arm 2 blocked 24 of 24 drafts and passed 0
of 215 rows (`benchmarks/expertlongbench/RESULTS-ARM2.md`). Arm 3 then ran both
redesigned contracts on the same instances. Content addressing false-blocked 2
of 167 rows (1.20%, Wilson 0.33–4.26%), **both of them the design's own
80-character cap refusing a correct 97- and 104-character quote**, and the model
paraphrased its quote 0 times in 192 (`RESULTS-ARM3.md` §1, §3). So the quote is
copied rather than counted, **there is no length cap**, and the only bound is
that a quote lies within one line — which is what keeps it a span.

**`at` left the contract.** A row used to name the line of its own draft where
the number was written — an address a writer that emits a whole file in one
reply cannot know, and 50 of Arm 2's 215 rows named a line past the end of
their own draft. The address §7 prints back to a person is DERIVED here
(`_derive_at`) from the draft and the transcribed pair instead. A row that still
carries `at` is accepted and its `at` is ignored, so an annotation written under
the old contract does not break.

The same two questions are asked of a `results.json` quantity whose `source`
carries a `#L14` fragment (§2.1's additive widening). That belongs here and not
in `check_provenance`, which decides membership and never opens a file: putting
it there would change an existing check's contract and leave two span
implementations that have to agree. A source with no fragment is untouched.

**Span-scoped, never file-scoped.** Measured on 16 archived drafts
(`benchmarks/expertlongbench/provenance_probe.py`): a *wrong source file*
contains the claimed pair 27.7% of the time (596/2150); a *wrong line of the
right file* contains it 0.0% of the time (0/1825). Checking the file would let a
plausible-but-wrong citation through a quarter of the time — the
inverted-executable-check failure D155 killed, in a new costume. `_quote_span`
is therefore the load-bearing line of this module — it returns the quoted run
and never the file — and it has a test that asserts the check goes green when it
is widened to the whole file. `_span` says the same thing for the `results.json`
locator, which is still a line range.

**The four codes, and which failure wears which.** CA-NUM-001 is *this row
cannot be read, or the file it names is not here*: a malformed row, a value that
is not a number, a `src` that is neither `uncited` nor a file-and-quote, a path
outside the audited scope, a broken sha pin. CA-NUM-002 is *the locator does not
land*: under the line contract, a span that resolves without holding the pair;
under the quote contract, that same failure and the two that are now one step
earlier — a quotation the file does not contain, and one it writes across two
lines. **The quote IS the span**, so a quote that is not there is a wrong span
rather than a missing file, and it carries the wrong-span code; the Arm 3
harness called it CA-NUM-001 because there the quote was still being read as the
locator half. CA-NUM-003 is ADVISORY: `uncited`, or a `governed:` source whose
bytes this project does not keep. CA-NUM-004 is ADVISORY: a quotation the file
says on more than one line. It resolves and it contains the pair; what is
unresolved is *which* occurrence, a property of the source and not a defect in
the annotation, so it is counted, carried to the auditor and never blocks
(`docs/design/PROVENANCE_ADDRESSING.md` §2.2).

Honest boundary, stated the way A4's is (`provenance.py:16-20`):

* This enforces **declared** provenance, never coverage. A number the generator
  did not annotate produces nothing at all, and a document with no fence passes
  vacuously. Whether every number *should* have been annotated is a judgment
  about the text, which is the auditor's tier, not this one.
* `uncited` is not a truth value. It is the generator declining to name a
  location — a fact about the annotation, not a claim about the world — and it
  is ADVISORY: 13.3% of real draft numbers (57/430) are melting points and ionic
  radii that occur in no source, and blocking those would make the product
  refuse to state a well-known constant.
* Containment is exact. Where a source states a value in another form — "a
  third" for 0.33, an hour for 60 min, a value read off a plot — the check must
  not attempt it; such a number is annotated `uncited` and reaches the auditor.
* A `governed:` locator names bytes this project does not retain (§1.2), so the
  check cannot re-read them and says so as an ADVISORY rather than passing in
  silence.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Mapping, NamedTuple

from .framework import ADVISORY, BLOCKER, Finding, register
from .quantities import (declared_inputs, is_number_shape, normalise_number,
                         results_files)

#: A fenced ```crossaudit-numbers block; its body is a JSON array of rows.
_FENCE = re.compile(r"```crossaudit-numbers[^\n]*\n(.*?)\n```", re.S)
#: Every opening, closed or not. A block whose closing fence was never written
#: is not "no annotation" — it is an annotation that went missing, and silence
#: over it is the §5.4 failure in miniature.
_FENCE_OPEN = re.compile(r"```crossaudit-numbers[^\n]*(?:\n|\Z)")
_TEXT_SUFFIXES = (".md", ".txt", ".rst", ".tex")

#: Line numbers are bounded at nine digits. Since D159 the fence carries no line
#: number at all, so this governs the `results.json` locator and the span parser
#: it shares — the one place a line range is still written by a deterministic
#: producer rather than by a model. Not a style rule: `int()` refuses a
#: string of more than 4300 digits outright, so an unbounded `\d+` turns a
#: malformed annotation into an uncaught ValueError escaping `run_checks`. A
#: bounded pattern makes the same input fail the locator match and become an
#: ordinary CA-NUM-001 finding, which is what a malformed annotation is.
#: `[0-9]` and not `\d`: `\d` matches Arabic-Indic and Devanagari digits, which
#: `int()` accepts and which no transcription of committed bytes would ever
#: mean, so `#L٢` was being read as line two. The same discipline the
#: `check_provenance` fragment already had, applied to every locator parser
#: rather than to one of them.
_LINE = r"[0-9]{1,9}"
#: ``<path>[@<sha256>]#L<start>[-L<end>]`` — a span, never a file and never a
#: value. The sha is optional and may be a prefix of at least 8 hex characters,
#: because a committed annotation abbreviates one the way git does.
_SPAN = re.compile(r"(?P<path>[^@#]+?)(?:@(?P<sha>[0-9a-fA-F]{8,64}))?"
                   rf"#L(?P<start>{_LINE})(?:-L(?P<end>{_LINE}))?")
#: The same span fragment where it hangs off a `path@revision` results source.
_SOURCE_FRAGMENT = re.compile(rf"#L(?P<start>{_LINE})(?:-L(?P<end>{_LINE}))?\Z")

#: A bare number, sign and thousands separators included.
#:
#: The sign is not cosmetic: without it `-5 °C` transcribed as `-5` is a
#: non-overridable blocker on a correct citation, and transcribed as `5` it
#: PASSES against a span that says minus five — a wrong number accepted and a
#: right one refused, from one missing character class.
#:
#: A grouped token like ``1,000`` has two honest readings — one thousand, and a
#: "1" that happens to be followed by a comma — and `contains_pair` tries both
#: rather than picking one, because which reading a transcription meant is not
#: something this layer can know and guessing wrong would block correct work.
#: A number as it appears IN A SPAN. One reading per occurrence, and it is the
#: MAXIMAL one — `1,000` is a thousand, never a `1` that happens to be followed
#: by a comma. The same rule as the unit token, for the same reason: a prefix of
#: what the source wrote must not satisfy a transcription of it.
#:
#: Unbounded in every part, deliberately: a
#: capped exponent here does not reject an over-long literal, it TRUNCATES one,
#: and the leftover digits became a unit — `1e10001` read as the number `1e1000`
#: followed by the unit `1`, which passed 100 of 100 exponents swept from 10000
#: to 10099. `normalise_number` applies the bound with `fullmatch`, where the
#: only two answers are "this number" and "not a number".
#:
#: The sign is not cosmetic either: without it `-5 °C` transcribed as `-5` was a
#: non-overridable blocker on a correct citation, and transcribed as `5` it
#: PASSED — a wrong number accepted and a right one refused, from one missing
#: character class. A leading dot is accepted because `normalise_number` accepts
#: `.5`, and an extractor that cannot see what the comparator accepts is a
#: blocker on a form the contract permits.
_NUMBER = re.compile(r"(?<![\w.])([+\-−]?(?:[0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?"
                     r"|\.[0-9]+)(?:[eE][+\-−]?[0-9]+)?)")
#: Any run of whitespace between a number and its unit, or none at all. Plain
#: `\s`, because Python's `\s` on a str pattern is the Unicode definition and
#: already covers U+00A0, U+2003 and U+202F — the three a copied table cell, a
#: typeset paper and a spreadsheet respectively produce. A hand-written list of
#: the ones somebody thought of is how the first two got in and the third did
#: not.
_GAP = r"\s*"

#: What ENDS a unit token. **This list is exhaustive, and everything not in it
#: is token.** It used to be the other way round — a set of characters allowed
#: INSIDE a token — and an allowlist is the same defect as a prefix reading
#: wearing a third hat: any character its author did not think of silently ended
#: the token, so a shorter reading satisfied a longer source. `5 °Cβ` satisfied
#: an annotation of `°C` because β was not on the list, and nothing about β
#: makes it a boundary. Inverting the rule means a character nobody anticipated
#: (`Ω`, `Å`, `′`, `″`, subscripts, `⁄`, a new SI prefix) keeps the token whole
#: instead of cutting it short, and the failure direction is a blocker on a
#: half-transcribed unit rather than a pass on one.
_BOUNDARY = set(',;:!?"\'«»…' + "\u2018\u2019\u201a\u201b\u201c\u201d\u201e\u201f\u2039\u203a"
                + "†‡§¶")
#: The set names three families, and the reason each is in it. Structural
#: punctuation (`,;:!?"'«»…`) never appears inside a unit. Typographic quotes
#: (`\u201c\u201d\u2018\u2019`) are the same thing in a word processor's
#: rendering, and leaving them out made `5 °C\u201d` and `5 °C\u2019s` blockers on
#: ordinary prose. Footnote and note marks (`†‡§¶`) attach to a number in exactly
#: the position a unit would, which is why they have to be named rather than
#: guessed at.
#:
#: `*` and `>` are deliberately NOT boundaries: `*` is multiplication and `>` is
#: comparison, both of which are real notation a unit can contain, and treating
#: them as punctuation would let a shortened unit satisfy a longer source. The
#: contract says so, because the cost is a footnote star reading as unit text.
#:
#: An em or en dash never continues a unit: it separates prose or a range.
_DASHES = set("—–")
_OPENERS, _CLOSERS = set("([{"), set(")]}")

#: Notation this layer does not parse, sitting on the end of a number: a
#: superscript exponent (`10⁵`), or a multiplication sign or caret before a
#: digit (`5×10³`, `10^5`). The number the source states is not the number the
#: scanner just read, so the occurrence is not a match for ANY unit — including
#: the empty one, which is how `10⁵ g` was satisfying an annotation of `10` with
#: no unit. Narrow on purpose: it fires on the number's own continuation and
#: never on a word that merely follows, because "a unitless number may not be
#: followed by anything" would block every `run 5 of 12` in the corpus.
#:
#: **A SPACE before the OPERATOR does not end the continuation, and that hole
#: was a live false pass** (`docs/design/CONTAINMENT_RULE.md` §4, "Out of band,
#: and not an extension", verified against the shipped matcher while that note
#: was written). Matched with no whitespace allowance at all, `3×10⁻²` was
#: refused and `3 × 10⁻²` was not, so `contains_pair("… ≈ 3 × 10⁻² mbar", "3",
#: "")` returned True: the check reporting that a source states three when what
#: it states is 0.03.
#:
#: The allowance is the FIFTH alternative and nothing else moves — the four
#: above are the bytes that shipped — because a whitespace allowance in front of
#: the others makes a footnote into notation. `Participants: 5 ¹`, with
#: `¹ Enrollment count` on the next line, is a superscript separated from a
#: number by a space, and reading it as an exponent turns a correct unitless
#: annotation into a non-overridable blocker. A bare superscript after a space
#: is a footnote mark; only an OPERATOR can be separated from its left operand.
#:
#: Three further conditions, each removing a false blocker a draft of this had:
#:
#: * the whitespace is non-newline (`[^\S\r\n]`), because a superscript or an
#:   operator on the NEXT line of a multi-line span is not this number's
#:   continuation;
#: * **the right operand must carry an exponent marker**, which is what keeps
#:   `5 x 3 grid` prose. An ASCII `x` between two plain integers is a grid, a
#:   window or a matrix, and blocking every one of them to catch a product would
#:   be the false-blocker trade this whole line refuses. `3 × 10⁻²` and
#:   `5 x 10^3` continue into an exponent; `5 x 3` does not, and the difference
#:   is read off the bytes rather than guessed at;
#: * **and that marker must be ADJACENT to the operand it exponentiates.** The
#:   whitespace allowance is in front of the operator and nowhere else. Allowing
#:   it before the marker as well read `Grid dimensions: 5 x 3 ¹` — a footnoted
#:   grid — as five times three-to-the-something, and a sweep of
#:   `<n> x 101 ¹` blocked 100 of 100. It is the same footnote the left-hand
#:   rule already refuses to read as an exponent, met on the other operand, and
#:   the same answer is owed to it: `5 x 10³` is notation, `5 x 10 ³` is a
#:   footnote on a ten.
#:
#: It is a narrowing of the matcher (strictly fewer occurrences match), so it
#: cannot add a false PASS — but it can add a false BLOCKER, which is why the
#: containment note requires it through the same gold as the six extensions and
#: why it was measured there before it shipped
#: (`benchmarks/expertlongbench/study8gold/`).
_SIGNS = r"+\-−±"
_SUPER = r"⁰¹²³⁴⁵⁶⁷⁸⁹"
#: Whitespace that is not a line break: a separated operator stays on its line.
_INLINE = r"[^\S\r\n]"
_UNPARSED = re.compile(
    rf"[{_SUPER}]"                          # 10⁵
    rf"|[{_SIGNS}⁺⁻][{_SUPER}]"             # 10⁻⁵, 10⁺⁵
    rf"|[⁺⁻]"                               # a bare superscript sign
    rf"|[×x*^⋅·]\s*[{_SIGNS}]?\s*[0-9]"     # 5×10³, 5×-10³, 5^−3
    # `3 × 10⁻²`, `5 x 10^3`: a space before the OPERATOR only, and only where
    # the right operand carries an exponent marker ADJACENT to it, so a spaced
    # product of two plain integers stays prose and a spaced superscript stays a
    # footnote mark — on the right operand exactly as on the left one.
    rf"|{_INLINE}+[×x*^⋅·]{_INLINE}*[{_SIGNS}]?{_INLINE}*[0-9]+"
    rf"[{_SUPER}⁺⁻^]")

#: A token of the shape `<unit>-<number><unit>`: a RANGE written closed up, such
#: as the ambient window `(20°C-25°C)`. Whole-token comparison is what stops a
#: prefix satisfying a compound unit, and it also means the `20` in that span
#: carries the token `°C-25°C`, which no honest transcription would ever say. So
#: a range is recognised and split, and only when the two halves are the same
#: unit — `kg-m` and `h-long` are not ranges and keep their whole token.
_RANGE = re.compile(r"(?P<u1>.+?)-(?P<n>[0-9]+(?:\.[0-9]+)?)(?P<u2>.+)\Z")

#: The unit-synonym table §3.1 calls load-bearing, carried over verbatim from
#: the probe that measured it. Measured again against THIS code over the 16
#: archived drafts (`benchmarks/expertlongbench/provenance_arm1.py`): deleting it
#: takes the primary block rate from 7 of 365 (1.92%) to 13 of 365 (3.56%, 95%
#: Wilson 2.09–6.00%) — past §6's 2% kill line — and the six it adds are every
#: draft that wrote `hours`, `minutes` or `wt%` where its source wrote `h`,
#: `min` or `wt %`. The seven that remain either way are all artefacts of the
#: harness's own extraction vocabulary, measured and reported there rather than
#: corrected.
#:
#: It is fixed, and it is small on purpose. Growing it against a failing corpus
#: would be tuning a measurement to pass its own test; entries belong here only
#: when two renderings of a unit are the same unit by definition.
SYNONYMS: dict[str, str] = {
    "hours": "h", "hour": "h",
    "minutes": "min", "minute": "min",
    "wt %": "wt%", "mol %": "mol%",
    "µm": "μm",
}

#: **A SPACE IS NOT WHERE A UNIT ENDS.** D160 ruling 1, from the containment
#: gold: `unit_token` stopped at whitespace, so a bare `°C` satisfied a source
#: writing `°C min⁻¹`, `mg` satisfied `mg h⁻¹` and `K` satisfied `K min⁻¹` — 9 of
#: the gold's 11 false passes (7.33%, `RESULTS-GOLD.md` §3). Slice 2's contract
#: called that reading structural; the gold says it is D157 lesson 2 unfinished,
#: and a prefix never satisfies whatever character precedes it.
#:
#: So a unit reading continues across whitespace while the next token is
#: UNIT-SHAPED, and the two halves of that one rule are: the bare first token no
#: longer satisfies when a continuation follows (a NARROWING — it can remove a
#: pass and never add one), and the whole spaced expression becomes a candidate
#: the annotation can name in full (E4 — a candidate at least as long as the
#: whole token, never shorter).
#:
#: **A token is unit-shaped in ITSELF, not because it carries a marker
#: somewhere.** The first build tested for a marker anywhere in the token — a
#: superscript, a solidus, a middle dot — and review found that reads short prose
#: as a unit: `wet/dry` is a word with a slash, `batch-1` a word with a hyphen,
#: `sample¹` a word with a footnote, and all three turned a correct `(5, g)` into
#: a block. Guards against brackets and long words did not draw the boundary
#: either, because the boundary is not length. A continuation is now an
#: EXPRESSION over named fragments: a fragment, a fragment with an exponent
#: attached, or such atoms joined by a solidus or a middle dot. `min⁻¹` is
#: `min` + `⁻¹`; `wet/dry` is two words.
_FRAGMENT_SPLIT = re.compile(r"[/⁄·⋅]")
#: An exponent ATTACHED to a fragment. ASCII digits need an explicit `^` or a
#: sign, because a bare letter-digit run is a sample label in exactly the place
#: materials prose puts one (`A2`, `S1`, `Fig3`) and reading it as a unit blocks
#: a correct annotation on every one of them. A superscript run stands alone.
_EXPONENT_TAIL = re.compile(r"(?:\^[+\-−]?[0-9]+|[+\-−][0-9]+|[⁺⁻]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)\Z")
#: A solidus or middle dot with nothing either side of it is an OPERATOR, not a
#: unit: it continues an expression and can never end one. `5 g / mL` is one
#: unit written in three tokens; `5 g / 100 mL` runs into a numeral and is not
#: readable at all, which is a block and not a `g /`.
_CONNECTORS = frozenset("/⁄·⋅")

#: The named fragments. **Fixed, small, and knowingly incomplete**, and the
#: incompleteness is now stated honestly in both directions, because review
#: showed the first version of this sentence was false:
#:
#: * BEFORE a join has begun, an omission leaves the shipped behaviour — the
#:   bare token still matches, exactly as it does today;
#: * AFTER a join has begun, an omission is a BLOCK for a fragment of one to
#:   three lower-case letters or any marked one: `5 kg m sr` with `sr` missing
#:   must not hand back `kg m`; the scan stops without a boundary and
#:   `_unit_candidates` returns nothing (see `_spaced_unit`). The first build
#:   returned the joined prefix instead, which is "a prefix never satisfies"
#:   defeated a fourth time;
#: * but a fragment of FOUR OR MORE LETTERS, or a capitalised one, that this
#:   table does not name reads as PROSE, after a join exactly as before one:
#:   `5 kg m mmHg` offers `kg m` the way `5 g mmHg` offers `g` today, because
#:   nothing on the surface separates `mmHg` from `sample`. That is the base's
#:   class, not a new one, and for the entries of that shape listed here —
#:   `mbar`, `Torr`, `sccm`, `mmol`, `Hz`, `Sv` and their like — this table is
#:   the only guard. `tests/test_number_source_check.py` enumerates them.
#:
#: What is excluded is still the argument, because a wrong INCLUSION is a false
#: blocker: no English function word (`of`, `in`, `at`, `per`), no word that is
#: also a unit (`bar`, so `a 5 g bar` stays prose). Bare capitals and element
#: symbols ARE named here — they have to be, or `5 J K⁻¹` cannot read `K⁻¹` —
#: but `_continues_unit` refuses them BARE, so `5 g K` is five grams of
#: potassium and `5 g Pa` is protactinium, both still matching `g`.
_UNIT_FRAGMENTS = frozenset("""
    m cm mm nm pm µm μm km dm
    g kg mg µg μg ng
    s ms µs μs ns ps min h
    L mL µL μL nL dL
    mol mmol µmol μmol nmol
    K A N J W V C F S T H B Y I U O P
    Pa kPa MPa GPa hPa mbar atm Torr torr psi
    Hz kHz MHz GHz rpm
    Wb Bq Gy Sv lm lx cd sr rad kat Ω Å
    eV keV MeV meV kJ mJ kW mW
    mA µA μA nA mV kV µV μV mN kN
    M mM µM μM nM
    wt vol
    sccm slm ppm ppb
    °C °F ° % ‰
""".split())
#: Every element symbol, so the collision set is exact rather than guessed. A
#: bare fragment that is one of these needs a structural marker to continue:
#: `5 g K` is potassium, `5 g Pa` protactinium, `5 g C` carbon — ordinary
#: materials prose, and the commonest thing written after a mass. With a marker
#: they are units again (`5 J K⁻¹`, `5 mPa·s`), because no element is written
#: with an exponent in that position.
_ELEMENTS = frozenset("""
    H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni
    Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe
    Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au
    Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf
    Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og
""".split())
#: Short function words, which are the prose a quantity is followed by when the
#: prose is shorter than four characters. Only consulted AFTER a join has begun,
#: to tell a true boundary from a scan that ran out of vocabulary.
_STOPWORDS = frozenset("""
    a an and as at by for from in into is of on or over per than the then to
    under until up using was were with
""".split())
#: How many tokens one unit expression may span. A LOOP GUARD, and since review
#: emphatically not a candidate producer: hitting it truncates the scan and
#: yields no reading at all. Seven-token expressions used to hand back their
#: first six. Consulted only when the next token WOULD CONTINUE the expression:
#: prose, a numeral or a bracket after six tokens is a boundary exactly as it
#: is after two, which the second review found it was not.
_MAX_UNIT_TOKENS = 6
#: The run of whitespace a unit expression may cross. `_INLINE` and not `\s`:
#: Python's `\s` already covers U+00A0, U+2003 and U+202F (a hand-written list of
#: the ones somebody thought of is how the first two got in and the third did
#: not), and excluding the newline is the rule that a continuation stays on its
#: own line — a token on the next line of a multi-line span is the next line's
#: prose, not this number's unit.
_INLINE_GAP = re.compile(rf"{_INLINE}*")


def _fragment(token: str) -> bool:
    """A named unit fragment, under the synonym table's folding — which is what
    covers `hours`, `minutes` and `µm` without listing them twice."""
    return token in _UNIT_FRAGMENTS or normalise_unit(token) in _UNIT_FRAGMENTS


def _unit_atom(token: str) -> bool:
    """A fragment, or a fragment with an exponent attached to it."""
    if _fragment(token):
        return True
    tail = _EXPONENT_TAIL.search(token)
    return bool(tail) and tail.start() > 0 and _fragment(token[:tail.start()])


def _unit_shaped(token: str) -> bool:
    """Whether this token is a unit EXPRESSION in itself: an atom, or atoms
    joined by a solidus or a middle dot. `min⁻¹`, `vol/vol`, `mol⁻¹·K⁻¹·s⁻¹`
    are; `wet/dry`, `batch-1`, `sample¹`, `(heating/cooling` are words."""
    parts = _FRAGMENT_SPLIT.split(token)
    if len(parts) > 1:
        return all(part and _unit_atom(part) for part in parts)
    return bool(token) and _unit_atom(token)


def _continues_unit(token: str) -> bool:
    """Whether this token, separated from a unit reading by whitespace only, is
    part of the same unit expression.

    A word is not a unit fragment — the mirror the whole rule is judged by:
    `5 g sample`, `5 g of powder` and `2 h later` keep matching `g`, `g` and
    `h`. Neither is a bare element symbol or a bare capital: `5 g K` is
    potassium and `5 g A` is a labelled batch far more often than either is a
    unit, so those need a marker (`K⁻¹`, `Pa·s`) before they continue."""
    if not token or not _unit_shaped(token):
        return False
    return not (token in _ELEMENTS or (len(token) == 1 and token.isupper()))


def _is_boundary(token: str) -> bool:
    """Whether the token after a join is the PROSE the unit expression ended
    at, as opposed to a unit this table cannot read.

    Consulted only once a join has begun (`_spaced_unit`), and only for a
    token `_continues_unit` refused, so the answer decides between a reading
    and a block. The prose shapes are ENUMERATED and everything else blocks,
    because the block is the safe failure:

    * nothing, a numeral, an opening bracket;
    * a bare element symbol, a bare capital, a capitalised word — `5 wt % Ni`,
      `5 wt % K`, `5 wt % A`, `5 wt % Sample`: the substance or the label the
      quantity is OF. Decided BEFORE the fragment table is consulted: `K` and
      `Pa` are in that table for the sake of `K⁻¹` and `Pa·s`, and the second
      review found the table consulted first, which blocked `wt %` before
      fifteen elements;
    * a function word (`of`, `at`, `per`), or an alphabetic word of four or
      more letters (`sample`, `later`);
    * a marked word whose stem is longer than a unit symbol (`batch-1`,
      `sample¹`). A stem of one to three letters under an exponent is a unit
      symbol this table does not name (`xyz⁻¹`, and `run-2` with it), and
      blocks;
    * a word carrying a digit or a subscript (`A2`, `H2O`, `Li₂O`);
    * words joined by a solidus with no named fragment among them (`wet/dry`;
      `g/xyz` is a unit half-read, and blocks).

    A short lower-case token that is none of these — `qz`, `sr` were it
    unnamed — is a unit this table does not know, and blocks.

    **What this cannot tell apart, stated rather than hidden:** an alphabetic
    token of four or more letters, or a capitalised one, that is a unit this
    table does not name — `mmHg`, `kcal`, `mrad`, `dbar` — reads as prose, so
    `5 kg m mmHg` offers `kg m`. That is the base's own class at the first
    continuation (`5 g mmHg` matches `g` today and always did), reached after
    a join by the same rule, and no surface test separates `mmHg` from
    `sample`. The fragment table is the guard for those, and the test file
    enumerates which of its entries are guarded by nothing else."""
    if not token:
        return True
    if token[0].isdigit() or token[0] in _OPENERS:
        return True
    if token in _ELEMENTS or (token[0].isupper() and token.isalpha()):
        return True                          # `5 wt % Ni`: a substance, a label
    if token.isalpha():
        return len(token) >= 4 or token.lower() in _STOPWORDS
    tail = _EXPONENT_TAIL.search(token)
    if tail and tail.start() > 0:
        stem = token[:tail.start()]
        return stem.isalpha() and len(stem) >= 4   # `batch-1` a label, `xyz⁻¹` a unit
    if any(ch.isdigit() for ch in token):
        return True                          # `A2`, `H2O`, `Li₂O`
    parts = _FRAGMENT_SPLIT.split(token)
    if len(parts) > 1:
        return all(part.isalpha() for part in parts) and not any(_unit_atom(p) for p in parts)
    return False


def _text(data: bytes) -> str | None:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def normalise_unit(unit: str) -> str:
    """Fold one rendering of a unit onto another. Whitespace only, plus the
    fixed synonym table; nothing here is a conversion."""
    folded = " ".join(str(unit or "").split())
    return SYNONYMS.get(folded, folded)


def _scan(text: str, skip_space: bool) -> tuple[str, str]:
    """One unit token and the remainder, by boundary rather than by allowlist."""
    i = (len(text) - len(text.lstrip())) if skip_space else 0
    depth, start = 0, i
    while i < len(text):
        ch = text[i]
        if ch.isspace() or ch in _BOUNDARY or ch in _DASHES:
            break
        if ch in _OPENERS:
            depth += 1
        elif ch in _CLOSERS:
            if depth == 0:
                break
            depth -= 1
        elif ch == ".":
            # A period is part of the token only where a unit can have one:
            # directly before a letter or a digit (`kg.m`, `mol.L-1`, `a.u`).
            # Anything else — a space, the end of the text, another period,
            # punctuation — ends a sentence, not a unit.
            nxt = text[i + 1:i + 2]
            if not nxt.isalnum():
                break
        i += 1
    return text[start:i], text[i:]


def unit_token(rest: str) -> tuple[str, str]:
    """One WHOLE unit token following a number, and whatever follows it.

    **One token is no longer one unit.** Since D160 ruling 1 the unit reading
    continues across whitespace while the next token is unit-shaped, so this is
    the FIRST token of the expression `_spaced_unit` assembles, and a caller
    that compares against this alone is reintroducing the prefix the gold
    found. `_unit_candidates` is the reading; this is one step of it.

    Runs from the first non-space character to a boundary, and **every
    boundary is enumerated**: whitespace, the end of the text, a closing bracket
    nothing opened, one of `,;:!?"'«»…`, an em or en dash, or a period that is
    not directly before a letter or digit. Everything else is token.

    **Whole token, because a prefix must never satisfy.** Reading the unit with
    a pattern that could return a shorter alternative let `5 m-2s-1` satisfy an
    annotation of `m`, `10 kg-m` satisfy `kg` and `2 h-long` satisfy `h`; the
    allowlist that replaced it let `5 kg.m` satisfy `kg` and `5 °Cβ` satisfy
    `°C`. Four different quantities accepted as one, under a contract that says
    the pair is compared literally.
    """
    return _scan(rest, True)


def _spaced_unit(rest: str) -> tuple[list[str], int, bool]:
    """The whole unit expression following a number: its tokens, where it ends
    in `rest`, and **whether the scan ended at a true boundary**.

    The first token is `unit_token`'s. After it, whitespace is crossed for as
    long as the next token continues the unit — and only NON-NEWLINE whitespace,
    because a token on the next line of a multi-line span is not this number's
    unit, it is the next line's prose.

    One list, both halves of D160 ruling 1: more than one part means the source
    wrote a spaced unit, so the bare first token stops being a reading (the
    narrowing) and the join becomes one (E4).

    **The third value is the repair review demanded, and it is load-bearing.**
    A scan that stops because it hit the token cap, ran into an operator with
    nothing after it, or met a token it can neither continue nor call a
    boundary has NOT read the unit — it has read a PREFIX of it. Handing that
    prefix back made `5 kg m sr` satisfy `kg m` and a seven-token expression
    satisfy its first six: the prefix defect a fourth time, now on the join.
    An incomplete scan yields no candidate at all, so the annotation blocks.
    A single token is always complete, which is the shipped behaviour for
    every line that holds no spaced unit.
    """
    token, after = unit_token(rest)
    if not token:
        return [], 0, True
    parts, end = [token], len(rest) - len(after)
    complete = True
    while True:
        gap = _INLINE_GAP.match(after).end()
        if not gap:
            break                            # a boundary character, or the end
        nxt, remainder = _scan(after[gap:], False)
        if not nxt:
            break                            # whitespace, then nothing to read
        if _continues_unit(nxt) or nxt in _CONNECTORS:
            if len(parts) >= _MAX_UNIT_TOKENS:
                complete = False             # an overflow reads nothing at all
                break
            parts.append(nxt)
            end += gap + len(nxt)
            after = remainder
            continue
        if len(parts) == 1 or _is_boundary(nxt):
            break                            # prose, a numeral, or no join yet
        complete = False                     # a unit this table cannot read
        break
    if parts[-1] in _CONNECTORS:
        complete = False                     # an expression never ends on `/`
    return parts, end, complete


def _unit_candidates(rest: str) -> list[tuple[str, int]]:
    """Every reading of the unit following a number, each with where it ends in
    `rest`: the whole unit expression, plus one reading of a range that is
    shorter only in the sense that it re-reads a token the source glued
    together. **No reading is ever a prefix of what the source wrote.**

    * where the source writes the unit as ONE token, that token — plus a range
      split, so the `20` in `(20°C-25°C)` carries `°C` and not the whole window,
      recognised only where both halves are the same unit;
    * where the source writes it across whitespace (`°C min⁻¹`, `wt %`,
      `kg m`), the WHOLE spaced expression and nothing shorter. That is D160
      ruling 1 in one line: the bare first token is not offered, because the gold
      found `°C` satisfying `°C min⁻¹` nine times in 150 passes, and the join is
      offered, because `°C min⁻¹` is what the source says and an annotation must
      be allowed to say it;
    * where the source writes a spaced unit this module cannot read to its end,
      **nothing**. Neither the join nor the bare token: an unreadable unit is a
      block, and the one thing it must never be is a shorter reading that
      happens to be readable. With the one limit `_is_boundary` states: a
      fragment of four or more letters, or a capitalised one, that the table
      does not name is not "unreadable" to this module, it is a word, and the
      expression before it is offered.

    The percent split (`wt %`) that used to be a special case is now this rule:
    `%` is a continuation like any other, and `wt %/s` is still one expression
    that `wt %` does not satisfy.
    """
    parts, end, complete = _spaced_unit(rest)
    if not parts:
        return []
    if len(parts) > 1:
        return [(" ".join(parts), end)] if complete else []
    token = parts[0]
    out = [(token, end)]
    span = _RANGE.fullmatch(token)
    if span and normalise_unit(span.group("u1")) == normalise_unit(span.group("u2")):
        head = span.group("u1")
        out.append((head, end - len(token) + len(head)))
    return out


def pair_occurrences(span: str, value: str, unit: str):
    """Every occurrence of the transcribed pair in this text, as the half-open
    `(start, end)` character interval covering the number and — where a unit was
    transcribed — the unit reading that satisfied it.

    The positions are the whole reason this is not just a boolean. Under content
    addressing the check has to answer a second question the line contract never
    asked: not only *is the pair here*, but *is it inside the run of characters
    the annotation quoted*. Both answers have to come from ONE scan of the same
    text, or the quote and the line get their own matchers and the two drift —
    which is exactly how the isolated-quote defect below was possible.
    """
    wanted_unit = normalise_unit(unit)
    wanted_value = normalise_number(value)
    if wanted_value is None:
        return
    for m in _NUMBER.finditer(span):
        token = m.group(1)
        if normalise_number(token) != wanted_value:
            continue
        rest = span[m.end():]
        if _UNPARSED.match(rest):
            continue                      # the source's number is not this one
        if not wanted_unit:
            yield m.start(1), m.end(1)
            continue
        for candidate, end in _unit_candidates(rest):
            if normalise_unit(candidate) == wanted_unit:
                # `end` is the candidate's extent in `rest` as the source wrote
                # it, not the length of the reading: a spaced expression joined
                # with single spaces is shorter than the characters it covers,
                # and the interval has to cover them or the quote containment
                # test would accept a quotation that stops inside the unit.
                yield m.start(1), m.end() + end
                break


def contains_pair(span: str, value: str, unit: str) -> bool:
    """Whether the transcribed (value, unit) pair occurs in this text.

    Exact, and deliberately so: the number must appear as a number, and where a
    unit was transcribed it must be the WHOLE unit token following that
    occurrence, under the synonym table. A value stated in words, converted, or
    read off a plot is not matched and must not be — that is what `uncited` is
    for.

    A value that does not normalise returns False and the caller turns that into
    CA-NUM-001. There is no substring fallback: the one that used to be here
    ignored the unit entirely, so source `1e3 K` satisfied an annotation of `1e3`
    with unit `g`.

    One implementation, `pair_occurrences`, so the span contract and the quote
    contract can never disagree about what containment means.
    """
    return any(True for _ in pair_occurrences(span, value, unit))


def _resolve(files: Mapping[str, bytes], annotated: str, path: str) -> str | None:
    """A key of the `files` mapping, or None. Exact first, then relative to the
    annotating artefact's own directory — both deterministic, neither a search."""
    if path in files:
        return path
    base = annotated.rsplit("/", 1)[0] if "/" in annotated else ""
    if base:
        joined = f"{base}/{path}"
        if joined in files:
            return joined
    return None


def _span(text: str, start: int, end: int) -> str | None:
    """The named lines, 1-based and inclusive, or None if the range is not
    inside the file.

    **The `results.json` locator turns on this function**, and only that one
    since D159: the fence no longer names a line range. Returning the whole
    `text` regardless of `start`/`end` is the §4 mutation, and it makes a
    wrong-line citation pass — asserted at
    `tests/test_number_source_check.py::test_a_results_source_span_is_verified_by_this_check_and_not_by_provenance`,
    which applies that mutation and requires the wrong-line row to go green.
    `_quote_span` carries the same guard for the fence.
    """
    lines = text.split("\n")
    if start < 1 or end < start or end > len(lines):
        return None
    return "\n".join(lines[start - 1:end])


def _fold(text) -> str:
    """The one normalisation content addressing performs, on BOTH sides of the
    comparison: every run of whitespace becomes a single space.

    It is `normalise_unit`'s own fold (above) applied to a longer string, and it
    is deliberately the whole list: no case folding, no punctuation stripping,
    no tokenisation. It is what lets a quote survive a line break the writer put
    inside it and a double space the source put inside itself, and nothing more.
    Python folds NBSP, EM SPACE and NARROW NO-BREAK SPACE here because
    `str.split()` splits on every character `str.isspace()` accepts — the same
    reason `contains_pair` reads `5\u00a0°C`.
    """
    return " ".join(str(text or "").split())


class _Located(NamedTuple):
    """Where a quotation landed: the whitespace-folded LINE that holds it, and
    every interval of that line the quotation occupies.

    Both halves are needed and neither is enough. The line is what the matcher
    reads, so that a sign, a digit, an exponent or the rest of a unit token
    sitting just outside the quotation is still in front of every boundary rule.
    The intervals are what the matcher's answer is then held to, so that the
    pair it found is the pair the annotation quoted rather than another one
    further along the same line.
    """
    line: str
    spans: tuple[tuple[int, int], ...]


def _quote_span(text: str, quote: str) -> tuple[_Located | None, int]:
    """Where a quotation names, and how many lines of the file hold it.

    **The whole check turns on this function**, exactly as `_span` did under the
    line contract. Returning the whole `text` regardless of the quote is the §4
    mutation, and it makes a quotation of the wrong line pass — see
    `tests/test_number_source_check.py::test_the_quote_and_not_the_file_is_what_is_checked`.

    Line-scoped, and that is the only bound the contract has left (D159 removed
    the 80-character cap, whose two false blockers were correct 97- and
    104-character quotes). A quotation is a run of ONE line: folding the file as
    one string instead would let a "quote" run from the top of a file to the
    bottom, and a file-scoped citation contains the claimed pair by coincidence
    27.7% of the time.

    The count is over LINES and not over occurrences, which is where this parts
    company with the Arm 3 harness's file-wide `flat(file).count(flat(quote))`:
    the same characters twice on ONE line still name that line, and the located
    text is the same text whichever occurrence was meant, so there is nothing
    ambiguous for the auditor to weigh. Twice on TWO lines is the ambiguity the
    design routes to ADVISORY.
    """
    needle = _fold(quote)
    if not needle:
        return None, 0
    found: _Located | None = None
    hits = 0
    for line in text.split("\n"):
        folded = _fold(line)
        at = folded.find(needle)
        if at < 0:
            continue
        hits += 1
        if hits > 1:
            return None, hits
        spans = []
        while at >= 0:
            spans.append((at, at + len(needle)))
            at = folded.find(needle, at + 1)
        found = _Located(folded, tuple(spans))
    return found, hits


def _pair_in_quote(located: _Located, v: str, u: str) -> bool:
    """Whether the transcribed pair is in the quoted run — read in its own line.

    **The quote says WHERE to look; the line says WHAT is there.** Matching the
    quotation in isolation was the shipped defect this rule replaces, and it was
    the prefix defect reborn one level up: every boundary rule in this module
    reads what ADJOINS an occurrence, so cropping the adjoining characters out
    of the text handed to the matcher silently disabled all of them at once.
    Quoting `5 mg` out of `5 mg/mL` satisfied an annotation of `mg`; quoting
    `5 g` out of `-5 g` satisfied five; quoting `5 g` out of `1e+5 g` satisfied
    five again; quoting `3` out of `30 °C` satisfied three; and a sweep of
    `-1 g` … `-100 g` cropped its sign 100 times out of 100. Three separate
    reviews removed those exact readings from the matcher (D157 lesson 2, the
    fifth review's sign rule, the round-6 exponent sign); an isolated quote
    handed all three back.

    So the scan runs over the whole folded line — `_NUMBER`'s lookbehind, the
    sign, the whole-unit-token boundary and `_UNPARSED` all see their context —
    and the occurrence it finds must lie INSIDE the quoted interval. Looking
    anywhere on the line without that clause would be the other bypass: a
    quotation of one phrase satisfied by a number somewhere else on the line.
    """
    return any(start >= qs and end <= qe
               for start, end in pair_occurrences(located.line, v, u)
               for qs, qe in located.spans)


def _derive_at(text: str, v: str, u: str) -> int | None:
    """The line of the annotating artefact where this pair was written, or None.

    D158 dropped `at` from the row because a generator writing a whole file in
    one reply cannot know where its own sentence will land — but the address is
    still what §7 prints back to a person, so code derives it: it holds the
    draft and the transcription, and can look. The fence bodies are blanked
    first (newline for newline, so the numbering does not move) or every row
    would locate itself in its own annotation.
    """
    blanked = _FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    for number, line in enumerate(blanked.split("\n"), 1):
        if contains_pair(line, v, u):
            return number
    return None


#: How much of a quotation a finding prints. The contract caps no quote (D159),
#: so a whole file can arrive as one; the observation is still a line a person
#: reads. The bound is on the REPORT and never on the comparison.
_QUOTE_SHOWN = 72


def _shown_quote(quote: str) -> str:
    folded = _fold(quote)
    if len(folded) > _QUOTE_SHOWN:
        folded = folded[:_QUOTE_SHOWN] + "…"
    return repr(folded)


#: A transcribed value or unit may arrive as a string or as a JSON number: a
#: generator writing `"v": 950` has still transcribed, not judged, and refusing
#: it would be a non-overridable blocker on a well-formed annotation.
_SCALAR = (str, int, float)


def _row_findings(path: str, files: Mapping[str, bytes], row: dict,
                  text: str) -> list[Finding]:
    # All three fields, present. `u` was previously allowed to be absent and
    # read as unitless, which let a row opt out of the half of the check that
    # compares units by simply not writing the key — the contract says three
    # fields, so a row with two is not a row this check can verify.
    #
    # THREE, not four: `at` left the contract with D159, and a row that still
    # carries one is accepted with its `at` ignored. Dropping a required field
    # only ever widens what is accepted, so an annotation written under the old
    # contract keeps passing; asking for it would be asking the generator for
    # an address it cannot know, which is what Arm 2 measured failing.
    missing = [k for k in ("v", "u", "src") if k not in row]
    bad = [k for k in ("v", "u") if k in row and not isinstance(row[k], _SCALAR)]
    bad += [k for k in ("src",) if k in row and not isinstance(row[k], (str, dict))]
    if missing or bad:
        detail = ("is missing " + ", ".join(missing) if missing
                  else "has a non-text " + ", ".join(bad))
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"a source annotation {detail}; each row names v, u and "
                        f"src, and a row that names fewer cannot be checked")]
    v, u = str(row["v"]), str(row["u"])
    src = row["src"]
    shown = f'"{v} {u}"' if u else f'"{v}"'
    # Derived, never asked for: the generator is not shown its own line numbers
    # and is no longer asked to guess them (D158/D159, §0 of the addressing
    # design). Where the draft does not state the pair in prose the finding says
    # so in words rather than inventing a line.
    at = _derive_at(text, v, u)
    # "the row" where the draft does not state the pair in prose at all: an
    # honest nothing beats a line number code has no evidence for, and the row
    # is still identified by the value the same sentence goes on to quote.
    where = f"line {at}" if at is not None else "the row"

    # **`uncited` never blocks — D158 ruling 1, and `PROVENANCE_CHECKS.md`
    # §2.1/§3.4 as written.** This branch used to sit BELOW the `at` and value
    # validation, so a row that declined to name any evidence at all still
    # became a non-overridable BLOCKER when it miscounted its own address. Six
    # of Arm 2's 215 generator-written rows did exactly that
    # (`benchmarks/expertlongbench/RESULTS-ARM2.md` §3) — the design's stated
    # contract violated inside the contract that was failing.
    #
    # The ordering was the defect, not the severity. A row that names no source
    # gives this layer nothing to open and nothing to look for, so there is
    # nothing in it that can fail; §3.4's table has exactly one disposition for
    # it, ADVISORY, counted and carried to the auditor, who is the reader that
    # can weigh an unsourced number.
    #
    # Nothing is waved through in silence, though: whatever the row got wrong is
    # said in the same ADVISORY's own observation, which is the text §7 prints
    # to a person. Advisory and visible, never blocking.
    if src == "uncited":
        wrong = []
        if not v.strip():
            wrong.append("it transcribes no number")
        elif normalise_number(v) is None:
            wrong.append(f"it transcribes {v!r}, which is not a number")
        malformed = f" (the row is also malformed: {'; '.join(wrong)})" if wrong else ""
        return [Finding(ADVISORY, "CA-NUM-003", path,
                        f"{where} names no source for {shown}; passed to the "
                        f"auditor{malformed}")]

    if not v.strip():
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        "a source annotation has an empty number or location; each "
                        "row names v, u and src")]
    if normalise_number(v) is None:
        # A transcription that is not a number cannot be looked for. It used to
        # fall through to a substring test that ignored the unit entirely, so
        # source `1e3 K` satisfied an annotation of `1e3` with unit `g`.
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} transcribes {v!r}, which is not a number; write the "
                        f"number alone, or name no source with \"uncited\"")]

    if isinstance(src, str):
        if src.startswith("governed:"):
            # §1.2: the fetched text is not retained anywhere, so code cannot
            # re-read it. Saying so is honest; passing in silence would not be.
            return [Finding(ADVISORY, "CA-NUM-003", path,
                            f"{where} names a fetched source for {shown}, whose text "
                            f"this project does not keep; passed to the auditor")]
        # Every other string is the old line-addressed locator, or a typo. It is
        # refused rather than parsed: the contract is a file and a quotation
        # copied out of it, and a check that also accepted `path#L11` would be
        # two contracts with one name.
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} names {src!r} for {shown}, which is not a file and "
                        f"a quotation from it (expected "
                        f'{{"file": "path/to/file.md", "quote": "…"}})')]
    return _verify_quote(path, files, src, v, u, shown, where)


def _verify_quote(path: str, files: Mapping[str, bytes], src: dict,
                  v: str, u: str, shown: str, where: str) -> list[Finding]:
    """Resolve one quotation and look in it. The half of the check that opens a
    file, under content addressing.

    The disposition order is the design's (`PROVENANCE_ADDRESSING.md` §2.2) and
    it is load-bearing: absent is a BLOCKER, non-unique is an ADVISORY, and only
    then is the pair looked for — so an ambiguous source can never be a
    non-overridable stop on a correct transcription (D155's shape).
    """
    named, quote = src.get("file"), src.get("quote")
    if not isinstance(named, str) or not named.strip():
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} names a source for {shown} with no file; a citation "
                        f"is a file and a quotation copied out of it")]
    if not isinstance(quote, str) or not _fold(quote):
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} names {named} for {shown} with no quotation; a "
                        f"citation is a file and a quotation copied out of it")]
    # `computed:` names a path in this increment exactly as the plain form does.
    # Whether a script CAUSED that value is figure_code's question (§3.2); that
    # the named quotation holds it is still this one's, and answering it here
    # closes the alternative of evading every locator check with a prefix.
    if named.startswith("computed:"):
        named = named[len("computed:"):]
    key = _resolve(files, path, named)
    if key is None:
        # Traversal, an absolute path and a symlinked path are all refused by
        # the same clause and for the same reason: the mapping holds the audited
        # scope, resolution is two dictionary lookups, and this layer never
        # touches a filesystem it could be walked out of.
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} cites {named} for {shown}, which is not in the "
                        f"audited scope")]
    declared_sha = src.get("sha")
    if declared_sha is not None:
        if not isinstance(declared_sha, str) or not re.fullmatch(
                r"[0-9a-fA-F]{8,64}", declared_sha):
            return [Finding(BLOCKER, "CA-NUM-001", path,
                            f"{where} cites {named} for {shown} with a pin that is not "
                            f"a sha256 prefix of at least 8 hex characters")]
        actual = hashlib.sha256(files[key]).hexdigest()
        if not actual.startswith(declared_sha.lower()):
            return [Finding(BLOCKER, "CA-NUM-001", path,
                            f"{where} cites {named} for {shown}, but that file's bytes "
                            f"are not the ones the annotation pinned")]
    body = _text(files[key])
    if body is None:
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} cites {named} for {shown}, which is not readable "
                        f"text")]
    located, hits = _quote_span(body, quote)
    said = _shown_quote(quote)
    if hits == 0:
        if _fold(quote) in _fold(body):
            # The file says it, across a line break. Named separately because
            # the writer's remedy differs: quote less, rather than quote right.
            return [Finding(BLOCKER, "CA-NUM-002", path,
                            f"{where} quotes {said} for {shown}, which {named} writes "
                            f"across a line break; a quotation is a run of one line")]
        return [Finding(BLOCKER, "CA-NUM-002", path,
                        f"{where} quotes {said} for {shown}, and {named} does not "
                        f"contain those characters")]
    if hits > 1:
        return [Finding(ADVISORY, "CA-NUM-004", path,
                        f"{where} quotes {said} for {shown}, which {named} says on "
                        f"{hits} lines, so it names no one place; passed to the "
                        f"auditor")]
    if not _pair_in_quote(located, v, u):
        return [Finding(BLOCKER, "CA-NUM-002", path,
                        f"{where} quotes {said} from {named} — {shown} is not in it")]
    return []


def _verify_locator(path: str, files: Mapping[str, bytes], locator: str,
                    v: str, u: str, shown: str, where: str,
                    src: str) -> list[Finding]:
    """Resolve one span and look in it. The half of the check that opens a file.

    Shared by the fenced annotation and by a `results.json` quantity whose
    `source` carries a `#L…` fragment, so there is exactly one implementation of
    "does the named span hold this pair" and exactly one mutation that reddens
    both.
    """
    m = _SPAN.fullmatch(locator)
    if not m:
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} names {src!r} for {shown}, which is not a line in a "
                        f"file (expected path#L14 or path#L14-L16)")]

    named, start = m.group("path"), int(m.group("start"))
    end = int(m.group("end") or start)
    lines = f"{named}:{start}" if end == start else f"{named}:{start}-{end}"
    key = _resolve(files, path, named)
    if key is None:
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} names {lines} for {shown}, which is not in the "
                        f"audited scope")]
    declared_sha = (m.group("sha") or "").lower()
    if declared_sha:
        actual = hashlib.sha256(files[key]).hexdigest()
        if not actual.startswith(declared_sha):
            return [Finding(BLOCKER, "CA-NUM-001", path,
                            f"{where} names {lines} for {shown}, but that file's bytes "
                            f"are not the ones the annotation pinned")]
    body = _text(files[key])
    if body is None:
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} names {lines} for {shown}, which is not readable text")]
    span = _span(body, start, end)
    if span is None:
        last = len(body.split("\n"))
        return [Finding(BLOCKER, "CA-NUM-001", path,
                        f"{where} names {lines} for {shown}, but that file ends at "
                        f"line {last}")]
    if not contains_pair(span, v, u):
        tail = "is not on that line" if end == start else "is not in those lines"
        return [Finding(BLOCKER, "CA-NUM-002", path,
                        f"{where} names {lines} — {shown} {tail}")]
    return []


def _results_findings(path: str, files: Mapping[str, bytes], data: bytes,
                      opaque: frozenset) -> list[Finding]:
    """The structured half: a `results.json` quantity whose `source` names a span.

    §2.1 widens a quantity's `source` from `path@revision` to
    `path@revision#L…`. `check_provenance` decides membership and never opens a
    file — that is its whole contract — so without this nobody would look at the
    line, and the widening would have accepted a claim no code checks. A source
    with no `#L…` fragment is the world before the widening and is left exactly
    as it was.

    Two rules learned from the review, both of which had made the compensation
    partial rather than real:

    * **A row this cannot read is a finding, never a skip.** It used to skip a
      value of the wrong shape "reported by units", and `check_units` has never
      looked at `value` at all — so a null value citing line 999 of a two-line
      file passed the complete science profile in silence.
    * **Whole-string precedence.** If the entire source string is itself an
      exact declared input, someone declared a revision that happens to contain
      `#L…`; it is opaque, and `check_provenance` already accepted it as a
      member. Reading a fragment out of it here would block on a shape the
      other check just approved.
    """
    out: list[Finding] = []
    text = _text(data)
    if text is None:
        return out
    try:
        # As in the fence: no literal is rounded through a float before the
        # canonical-decimal comparison sees it.
        doc = json.loads(text, parse_float=str, parse_int=str)
    except ValueError:
        return out                              # reported by parseable / schema
    if not isinstance(doc, dict) or not isinstance(doc.get("quantities"), list):
        return out
    for i, q in enumerate(doc["quantities"]):
        if not isinstance(q, dict):
            continue
        raw_src = q.get("source")
        if not isinstance(raw_src, str):
            continue                            # not a locator; provenance blocks it
        # NOT stripped, and a source that only differs by whitespace is this
        # check's finding rather than another check's. `provenance` catches a
        # whitespace-padded source too, and a check that relies on that is root
        # cause 1 again: `number_source` must hold its own contract with no
        # other check enabled.
        src = raw_src
        if src != src.strip() and _SOURCE_FRAGMENT.search(src.strip()):
            out.append(Finding(
                BLOCKER, "CA-NUM-001", path,
                f"quantities[{i}] source {raw_src!r} names a line but is not an "
                f"exact address; a locator carries no surrounding whitespace"))
            continue
        if src in opaque:
            continue                            # declared verbatim, so opaque
        fragment = _SOURCE_FRAGMENT.search(src)
        if not fragment:
            continue
        where = f"quantities[{i}]"
        v, u = q.get("value"), q.get("unit")
        if not is_number_shape(v) or not isinstance(u, str):
            out.append(Finding(
                BLOCKER, "CA-NUM-001", path,
                f"{where} names a line for a value this check cannot read; a "
                f"quantity citing a line needs a numeric value and a text unit"))
            continue
        v, u = str(v), str(u)
        named = src[:fragment.start()].rpartition("@")[0] or src[:fragment.start()]
        shown = f'"{v} {u}"' if u else f'"{v}"'
        out.extend(_verify_locator(
            path, files, named + fragment.group(0), v, u, shown, where, src))
    return out


def check_number_source(files: Mapping[str, bytes]) -> list[Finding]:
    """CA-NUM-001/002: a number's declared source span must resolve and contain it."""
    out: list[Finding] = []
    # The same discovery the builtin checks use, so a file they read is never a
    # file this one silently ignores: `myresults.json` was recognised by
    # `_results_files` and not by the exact-basename test that used to be here.
    structured = set(results_files(files))
    # A source string declared verbatim as an input is opaque (see below).
    opaque = frozenset(item for _meta, item in declared_inputs(files))
    for path, data in sorted(files.items()):
        if path in structured:
            out.extend(_results_findings(path, files, data, opaque))
            continue
        if not path.endswith(_TEXT_SUFFIXES):
            continue
        text = _text(data)
        if text is None:
            continue
        bodies = _FENCE.findall(text)
        if len(_FENCE_OPEN.findall(text)) > len(bodies):
            # An opening with no closing fence. Reading it as "no annotation"
            # would let a truncated or hand-mangled block pass vacuously, which
            # is indistinguishable from a document that never annotated at all.
            out.append(Finding(
                BLOCKER, "CA-NUM-001", path,
                "a crossaudit-numbers block was opened and never closed; its "
                "annotation cannot be read"))
        for body in bodies:
            try:
                # Every literal arrives as text. `json.loads` would otherwise
                # round `9007199254740993.0` through a double before the string
                # comparison ever saw it, so the precision the canonical-decimal
                # comparison exists to preserve would already be gone.
                rows = json.loads(body, parse_float=str, parse_int=str)
            except ValueError as exc:
                # ValueError, not JSONDecodeError: a literal with more than
                # 4300 digits raises the plain base class, and letting it escape
                # `run_checks` turned a malformed annotation into a crash.
                out.append(Finding(
                    BLOCKER, "CA-NUM-001", path,
                    f"a crossaudit-numbers declaration does not parse as JSON: {exc}"))
                continue
            if not isinstance(rows, list) or not all(
                    isinstance(r, dict) for r in rows):
                out.append(Finding(
                    BLOCKER, "CA-NUM-001", path,
                    "a crossaudit-numbers declaration must be a JSON array of "
                    "{v, u, src} rows"))
                continue
            for row in rows:
                out.extend(_row_findings(path, files, row, text))
    return out


register("number_source", check_number_source,
         "Opt-in: every number a text artefact declares in a ```crossaudit-numbers "
         "block, and every results.json quantity whose source carries a '#L14' span "
         "fragment, must name a location in the audited scope that resolves and "
         "contains the transcribed value and unit. A fenced row is {v, u, src}, and "
         "src is either 'uncited' or {\"file\": a path in the audited scope, "
         "\"quote\": characters copied from ONE line of that file}; a row that also "
         "carries the older 'at' field is accepted and its 'at' is ignored. The "
         "quote IS the span: it is located by exact characters with every run of "
         "whitespace folded to a single space on both sides, it has NO length "
         "limit, and the only bound is that it lie within one line. A quotation the "
         "file does not contain, one the file writes across a line break, and one "
         "that is found but does not hold the pair are each a blocker; a quotation "
         "the file says on MORE THAN ONE line is advisory and never blocks, because "
         "which occurrence was meant is a property of the source rather than a "
         "defect in the annotation. A results.json source still names a line range, "
         "because a deterministic producer writes that one. The value is compared "
         "as a number and not as text (leading and trailing zeros "
         "and exponent notation are not significant, so 1.50, 1.5 and 15e-1 are one "
         "number and a reported precision is not preserved); the unit must equal the "
         "WHOLE unit token following that number, under a fixed synonym table, so a "
         "prefix of a compound unit never satisfies it. A SPACE IS NOT WHERE A UNIT "
         "ENDS: where the token after the number is followed by whitespace and a "
         "unit-shaped continuation (a superscript, an exponent tail such as 's-1', "
         "a solidus, a middle dot, a percent sign, or a known unit fragment), the "
         "unit is the WHOLE spaced expression, so a source saying 'm-2 s-1' is not "
         "satisfied by 'm-2' and is satisfied by 'm-2 s-1'. Write the unit exactly "
         "as the source writes it, spaces included. A WORD is not a continuation, "
         "so '5 g sample' still matches 'g' and '2 h later' still matches 'h'; "
         "neither is a substance or a label, so '5 wt % Ni' has the unit 'wt %' "
         "and '5 g K' still matches 'g'. Where the spaced expression runs past "
         "what the check can read - more tokens than it scans, an operator with "
         "nothing after it, or a short or marked fragment it does not name - it "
         "reports NO reading and the row BLOCKS; it never falls back to the part "
         "it managed to read, because that part is a prefix. One limit is stated "
         "rather than hidden: an unnamed fragment of four or more letters, or a "
         "capitalised one, reads as a WORD, so '5 kg m mmHg' offers 'kg m' exactly "
         "as '5 g mmHg' offers 'g', and the fragment table is the only guard "
         "there. "
         "Punctuation ends a unit "
         "token, but '*' and '>' do not, because multiplication and comparison are "
         "notation a unit can contain. An EMPTY unit imposes no unit constraint at "
         "all — '5' annotated with no unit matches a source saying '5 g' — so the "
         "check can confirm that a number is present and can never establish that "
         "it is unitless. A named location that does not resolve or does not "
         "contain the pair is a blocker; 'uncited' is advisory "
         "and never blocks; a number nobody annotated is not this check's business. "
         "It enforces DECLARED provenance, never coverage, and never judges whether "
         "a number is correct.")
