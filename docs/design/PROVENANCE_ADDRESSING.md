# The addressing half of the annotation contract, redesigned

D158 ruling 2. Arm 2 (`benchmarks/expertlongbench/RESULTS-ARM2.md`) blocked 24 of
24 drafts and passed 0 of 215 rows, and the verifier was wrong about a span zero
times. The contract asked for two addresses the generator is never shown: `src`,
a line of a source file, and `at`, a line of the draft it is mid-way through
writing. This specifies the two replacements D158 named, predicts each from Arm
2's own archive with no new generation, and prices the experiment between them.

Every code claim is `file:line` on `fusion/evidence-authority` at `274174f`.
Checked rather than assumed: **D158 ruling 1 has not landed in these bytes** —
`number_source` is still in the `science` and `research` profiles
(`dcl/profiles.py:33`, `:36-37`) and `_row_findings` still validates `at` before
the `uncited` branch (`numbers.py:406-421`), the contradiction §3.4 says cannot
happen; `fix/number-source-not-default` exists with no commit ahead of the base.
Nothing here depends on that hotfix.

## 0. Why `at` cannot survive either contract

`at` is not a hard address, it is an impossible one. The generator emits each
whole file in one reply (`generator.py:75-80`, the output envelope); the line its
number lands on is a function of prose it has not written yet when it writes the
fence. Arm 2: 50 of 215 rows named an `at` outside their own draft, on 14 of 24
drafts. Post-numbering the draft before verification lets *code* check `at` but
does not let the *writer* know it — an unknowable address made into a checkable
wrong one, the same defect with a verifier attached. `at` earns its keep in one
place: it is the address the finding prints back to a person
(`numbers.py:400-404`, `where = f"line {at[0]}"`; docstring at `:356-366`), and
both contracts keep that by *deriving* it, since code holds the draft and the
transcribed value and can locate `v`/`u` in the draft itself.

**Both contracts drop `at` from the row**: `_row_findings`'s four-field gate
(`numbers.py:391`) becomes a three-field gate. That alone removes 50 of Arm 2's
189 blocks and closes the §3.4 violation with no special case for `uncited`.

## 1. Contract A — numbered rendering

### A.1 What changes in the prompt

`generator.build_prompt` renders each workspace file as a `--- <path> ---` banner
followed by its raw bytes, joined over the sorted `current` mapping
(`generator.py:449-450`). A wraps those bytes in a gutter — width 5,
right-aligned, `"| "` — so `RECIPE.md`'s tenth line arrives as
`   10| Calcination: 950 °C for 1 h`. Three constraints, only the first obvious.

1. **Numbering is per file, 1-based over `split("\n")`**, byte-identically to
   `_span` (`numbers.py:341-354`); any other convention makes prompt and checker
   disagree about what line 10 is — the original defect in a uniform.
2. **A file not rendered verbatim must not be numbered.** `_current_work` passes
   the scope through `shape_work` (`cli/build.py:292-323`,
   `context/outline.py:108-134`), which replaces any file over
   `MAX_FILE_BYTES = 48_000` (`outline.py:39`) with a structural outline
   (`outline.py:62-70`) and, past `MAX_WORK_BYTES = 400_000` (`outline.py:45`),
   outlines or stubs more. An outline's line 10 is not the file's line 10, so
   numbering it manufactures wrong addresses that look right — a **new**
   false-blocker path A creates, invisible to Arm 2 because every Arm 2 source
   set is one file of 15–25 lines. Number only files kept full; the skill must
   call an unnumbered file uncitable.
3. **`file_read` output carries no gutter** (`broker/tools_readonly.py:42-56`
   returns `content` and a sha, no line index), so a number obtained through the
   tool is unaddressable under A. `search` *does* return 1-based line numbers
   (`tools_readonly.py:83`) — one round trip per number, and Arm 2's generator
   made no tool call at all.
4. **The skill** (`scaffold/templates/PROVENANCE_NUMBERS_SKILL.md`) keeps its
   `v`/`u` rules verbatim — Arm 2 proved the generator obeys them — deletes its
   `at` paragraph, and gains one sentence, *the number in the gutter is the line;
   copy it, never count it*, and one refusal, *a file shown without a gutter, or
   as an outline, cannot be cited — write `uncited`.*

### A.2 The measured token cost

Through the product's own token path — `ceil(chars/4)`, `usage.py:169`, the
fallback estimator, since no tokenizer library is vendored — over the 24 Arm 2
source sets (`benchmarks/expertlongbench/study7/addressing_sim.py`):

| | tokens |
|---|---|
| source sets, plain / numbered | 4,516 (mean 188) / 5,292 (mean 220) |
| **delta** | **+776 = +17.2%** (min +26, median +32, max +44 per instance) |
| against one generator prompt, provider-reported | **+0.7%** (108,334 input tokens over 24) |

The transferable quantity is not 776; it is **7 characters per rendered line**.
This corpus's source lines average 41 characters, so the surcharge is 17% of
source bytes, 9% on 80-character code, more on wrapped prose — paid on every
file, every round, for the project's life, and on Arm 2's evidence paid twice:
the loop sent 1.92 generator prompts per instance (§6).

## 2. Contract B — content addressing

### B.1 The grammar

No line number anywhere. `src` becomes an object — e.g.
`{"file": "work/synthesis/RECIPE.md", "quote": "Calcination: 950 °C for 1 h"}`:

    src := "uncited"
         | {"file": <path>, "quote": <string, 1..80 chars>}
         | {"file": <path>, "quote": <…>, "sha": <8..64 hex>}      (optional pin)

`file` resolves exactly as today (`numbers._resolve`, `numbers.py:328-338`: exact
key, then relative to the annotating artefact's directory — deterministic, never
a search); `sha` keeps the existing pin semantics (`numbers.py:456-462`);
`governed:` and `computed:` keep their dispositions (`numbers.py:425-435`).

### B.2 The matcher

One normalisation, the one the module already performs: collapse every run of
whitespace to a single space, on **both** sides — `normalise_unit`'s fold
(`numbers.py:219`, `" ".join(str(unit or "").split())`) applied to a longer
string, which is what lets a quote survive the source's line wrapping. Nothing
else: no case folding, no punctuation stripping, no tokenisation. Then:

```
occurrences = flat(file).count(flat(quote))
occurrences == 0                -> BLOCKER  CA-NUM-001   (not in the file)
occurrences  > 1                -> ADVISORY CA-NUM-004   (ambiguous)
not contains_pair(quote, v, u)  -> BLOCKER  CA-NUM-002   (quote lacks the pair)
otherwise                       -> pass
```

`contains_pair` is unchanged (`numbers.py:296-326`) and runs against the quote,
not the file: **the quote is the span**, so every property the span rule bought
stays bought — the whole-unit-token rule (`numbers.py:249-266`), the synonym
table (`numbers.py:201-207`), the maximal-number reading.

**80 characters, and why a cap at all.** Uncapped, a "quote" that is the whole
file is a file-scoped citation in disguise, and §5 measured that cost: a wrong
source file contains the claimed pair 27.7% of the time (596/2150) against 0.0%
line-scoped (0/1825). The cap keeps B a span contract; 80 is the value §3
simulated, where it never bound. Smaller caps are untested here.

**Ambiguity is ADVISORY, and this is load-bearing.** §3.4's rule is that only a
*named locator* can block — one that does not resolve, or resolves without
containing the value. A quote occurring twice resolves and contains the value;
what is unresolved is *which* occurrence, a property of the source and not a
defect in the annotation. Blocking it would be a non-overridable stop on a
correct transcription of a repetitive source — D155's shape exactly. It routes
where `uncited` routes: counted, carried to the auditor, never blocking.

**The D155 check.** The model copies bytes it read and states nothing about them.
`quote` is the same object as §2.3's `crossaudit-claims` quoted span, blessed by
the design for the identical reason — and absent from the code: no
`claim_citation` or `figure_code` check is registered under `src/crossaudit/dcl/`
(only `numbers.py`), consistent with §8f. B does not add a grammar; it
**collapses two planned grammars into one**, with one matcher and one mutation
set for both.

**The skill.** `v`/`u` unchanged; `src` becomes *copy the shortest run of
characters from the file — 80 at most — that you can see contains both the number
and its unit, and paste it. Copy it, do not retype it. If you cannot, or the file
says what you copied more than once and you cannot make it longer, write
`uncited`.*

## 3. The prediction, from Arm 2's archive, no new model call

`benchmarks/expertlongbench/study7/addressing_sim.py` re-parses the 24 archived
drafts with the **shipped** matcher (`numbers.contains_pair`) and prints counts
only. It reproduces every Arm 2 figure it can be checked against — 215 rows, 32
`uncited`, 183 span rows, 159 file-contains (86.9%), 7 landing as shipped, 50
`at` outside the draft, 15 of 23 measurable drafts on one constant offset, median
offset +4 — the evidence that it reads what Arm 2 read.

| | rows of 183 | |
|---|---|---|
| **B — pair on exactly ONE line of the named file** | **142** | **77.6%** |
| B — and a unique ≤80-char quote containing it exists | 142 | 77.6% |
| B — pair on >1 line → ADVISORY / nowhere → BLOCKER | 17 / 24 | 9.3% / 13.1% |
| **A — lands after the draft's modal offset** | **150** | **82.0%** |
| A — best possible per-draft offset / as shipped | 150 / 7 | 82.0% / 3.8% |

1. **B's strict test cost nothing over the loose one**: wherever the pair sits on
   a unique line, a unique ≤80-character quote around it exists — 142 = 142. The
   cap is not the binding constraint on this corpus.
2. **A's modal offset equals A's best offset on every draft**, so the offset is
   genuinely a constant and "numbering removes it" is the right model of what A
   buys — but it is a model: 150 is what A gets *if* a writer shown a gutter
   copies it, and nothing in the archive can prove that.
3. **B's 77.6% is not a model.** It is a property of the corpus and the shipped
   matcher, and asks of the writer only that it copy bytes it can see — the half
   of the contract Arm 2 measured it doing perfectly.
4. **The two disagree on 26 rows, structurally.** Both resolve 133; A alone
   resolves 17 (exactly the ambiguous rows — a line number distinguishes
   duplicate lines, a quote cannot); B alone resolves 9 (drafts whose offset is
   not a clean constant); neither resolves 24.
5. **Against §6's secondary kill — "fewer than 80% of emitted rows resolve and
   contain" — the ADVISORY routing of ambiguity decides the outcome.** Over all
   183 rows B is 142/183 = 77.6% and *fails* the gate before a model is ever run;
   over the rows the contract can block (183 − 17 advisory = 166) B is
   **142/166 = 85.5%** and A is 150/183 = 82.0%. Preregister that before the arm
   runs, not after.

## 4. False blockers each contract still leaves, and the D64 mutations

**A.** (i) A writer that loses the gutter over a long file and names an adjacent
line — reading beats counting but does not eliminate it; unmeasurable here, where
sources are 15–25 lines. (ii) Any citation into an outlined or stubbed file
(`outline.py:62-70`), which A must forbid by rule or it manufactures wrong
addresses. (iii) Any number obtained through `file_read`
(`tools_readonly.py:42-56`), which carries no gutter. (iv) A source whose line
breaks move between the round that read it and the round that verifies it.

**B.** (i) **Paraphrase** — the model retypes instead of copying, and a
one-character drift is a blocker. This is B's whole risk, the archive cannot
measure it, and it is what the experiment buys. (ii) A pair whose value and unit
are more than 80 characters apart (a table row whose unit lives in a header):
zero here, non-zero somewhere. (iii) A quote whose only unique form crosses a
construct the whitespace fold does not reach.

**D64 mutations** (named in the check's docstring, per
`tests/test_repair_guard.py:3-7`). §4's rows 1–3 survive under A unchanged.

| contract | mutation that must redden it |
|---|---|
| A | drop the gutter from `build_prompt`'s WORK rendering → the prompt test asserting every rendered source line carries `<n>\| ` reddens (no model needed); number an elided file too → the fixture asserting an outlined file is rendered **without** a gutter reddens |
| A | §4's rows 1 and 3, kept verbatim: `#L11`→`#L12` → CA-NUM-002; widen the span to the whole file → the wrong-line fixture goes green |
| B | alter one character inside the quote → CA-NUM-001 |
| B | drop the uniqueness count → the duplicate-quote fixture stops being advisory and passes |
| B | let the matcher accept a prefix of the quote → the shortened-quote fixture goes green (the defect `unit_token` has been fixed three times, `numbers.py:249-266`) |
| B | drop the `contains_pair(quote, …)` clause → a quote that resolves without holding the pair goes green |
| B | remove the 80-char cap → the whole-file-as-quote fixture goes green, restoring §5's 27.7% coincidental pass |
| both | delete the unit-synonym table → the `hours`/`h` fixture reddens (§4 row 2, kept); remove the check from the profile → the profile test reddens by name |

## 5. The experiment that decides it

**Design.** The same 24 T03 instances, same seed, same vendor pair,
`max_rounds: 1`, two arms, one draft each: **A** (§1) and **B** (§2).
Within-instance paired, so each instance is its own control and the 24 pairs are
the unit of the clustered bootstrap.

**Budget.** Arm 2 spent $0.0741/instance ($0.0568 generator, $0.0173 auditor), so
48 rounds is $3.56 — **over the $3 line**, because the loop spends a generation
call on the malformed-envelope re-ask on 96% of rounds, ≈$0.014 each
(RESULTS-ARM2 §6). Two ways under the line, chosen before the run: **land the
re-ask fix first** (a separate slice regardless), 48 × $0.043 + 48 × $0.0173 ≈
**$2.89**; or **run 20 instances per arm**, ≈ **$2.97**, losing 4 pairs. Prefer
the first. A's surcharge is +32 input tokens/instance (≈$0.0001), B's ≈180 output
tokens/draft (≈$0.12 over the arm). Set `checks: ["number_source"]` so Arm 2's 48
incidental `CA-META-001` blockers (deviation 7) stay out of the record.

**Preregistered pass/kill, per arm, §8g verbatim on the primary** — of the rows
whose locator genuinely contains the pair, adjudicated by deterministic re-read:
*kill if the 95% interval's lower bound exceeds 2%; pass only if the upper bound
is below 5%; anything between is inconclusive and the check ships ADVISORY-only.*
Print the clustered bootstrap beside the Wilson interval and quote the count
where the denominator is thin, per §9.

**Preregistered secondary, and the real discriminator:** the fraction of
blockable rows that resolve and contain, against §6's 80% line — predicted
**85.5% for B**, **82.0% for A**. An arm materially below its prediction has
falsified its own mechanism, and that is the kill that matters. **A kills** below
~70%: the gutter did not remove the constant offset, and addressing by line is
not a prompt problem. **B kills** if byte-exact quotes fail materially above the
predicted 13.1% *for reasons other than source ambiguity* — the model
paraphrased, and B's premise is that it copies. Record per row whether the quote
(B) or line (A) was **absent, ambiguous, or wrong**, so a failure is attributable
without a second study.

**What each outcome licenses.** Both pass → take B, on cost and on §3's
structural argument, keeping A's gutter in reserve for the 9.3% ambiguous rows.
B passes, A fails → build B, question closed. A passes, B fails → build A, pay
the 17%, forbid citation into outlined files by rule. Both fail → the contract is
not an addressing problem, `number_source` stays ADVISORY-only permanently, and
the D157/D158 sequence has found its floor.

## 6. What Arm 2 also said, carried in

* **`uncited` never blocks, whatever any other field says.** Not yet true in
  these bytes (`numbers.py:406-421`); dropping `at` (§0) makes it true
  structurally rather than by a reordered branch.
* **The generator writes compound units in full when told to** — 0 of 183 rows
  shortened a unit. Unit shortening is not a generator failure mode, `v`/`u` is
  not the half to change, and the space-inside-a-unit clause stays the documented
  limit it is.
* **The loop spent its one free format re-ask on 23 of 24 rounds** — ≈¼ of
  generator spend, and a second malformation in the same round would have ended
  the run with no repair left. A separate slice, named only for §5's budget.
* **The hyphen stratum produced 0 blocks in 24 drafts**; D157's dial stays open
  and neither contract touches it.

## 7. Recommendation

**Build B.** D158 ruled that no address the model cannot know may be required of
it, and A does not satisfy that ruling — it makes the address *copyable* rather
than *knowable*, a better prompt for the same contract, bought with 7 characters
on every line of every file in every round forever, a rule forbidding citation
into any outlined file, and a silent mismatch with `file_read`. B asks of the
writer only what Arm 2 measured it doing perfectly: transcribing bytes it read,
183 rows of 183 with the unit at full length. Its ceiling is lower on the raw
denominator (77.6% vs 82.0%) and higher on the denominator that matters once
ambiguity is advisory where §3.4 says it belongs (85.5% vs 82.0%); it fails
toward `uncited` where A fails toward a blocker; and it collapses §2.1's and
§2.3's grammars into one matcher with one mutation set, the whole remaining shape
of this design. Drop `at` under either contract — it is the half of the failure
no prompt can reach.

**The one thing that would change it:** evidence that this generator paraphrases
rather than copies. If B's arm shows byte-exact quote failures well above the
predicted 13.1%, with the excess attributable to retyped rather than absent text,
B's premise is false, A's 82% is the only reachable number, and the 17% is worth
paying. That is what §5's arm B measures, and why both arms run rather than this
recommendation being built directly.
