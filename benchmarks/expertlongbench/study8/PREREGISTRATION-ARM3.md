# Study 8 — Arm 3: the deciding experiment between the two addressing contracts

Preregistered **before any study model call**, on `study/provenance-arm3`
(branched from `fusion/evidence-authority` at `bbceff2`). Binding:
`benchmarks/EXPERIMENT_RECORD.md` §1–§10, `docs/design/PROVENANCE_ADDRESSING.md`
§5, D158 ruling 3.

Arm 2 (`RESULTS-ARM2.md`) killed the shipped contract: **0 of 215** generator-
written annotation rows passed and 24 of 24 drafts were BLOCKED, because the
contract required two addresses the generator is never shown — `src`, a line of
a source file it sees only as raw bytes, and `at`, a line of the draft it is
mid-way through writing. The verifier was wrong about a span zero times. D158
sent the *addressing* half back to design and named two replacements. The design
priced both on Arm 2's own archive with no new generation. This arm runs them.

---

## 1. Hypotheses, in a form that can come out false

**H_A (contract A, numbered rendering).** When every citable file is rendered to
the generator with a line-number gutter and `at` is dropped, the generator writes
`src` line addresses whose named spans genuinely contain the transcribed `(v, u)`
pair, and contract A's verifier blocks so few of those correct annotations that
the addressing contract has earned a non-overridable blocker.

**H_B (contract B, content addressing).** When `src` becomes a file plus a short
quotation copied from it and `at` is dropped, the generator copies bytes it can
see, and contract B's verifier blocks so few correct annotations that the
addressing contract has earned a non-overridable blocker.

Each comes out false if that arm blocks correct annotations at a rate whose
Wilson 95% lower bound exceeds 2%.

## 2. The two arms, and what differs

Same 24 T03MaterialSEG instances as Arm 2, same seed (`20261104`), same generator
(`anthropic:claude-sonnet-4-6`), same auditor (`openai:gpt-5.6-terra`), same
`max_rounds: 1`, same shipped constitution, same task instruction, the product's
own generator path in a real scaffolded project. **One draft per contract per
instance.** Within-instance paired: each instance is its own control and the 24
pairs are the unit of the clustered bootstrap.

Three things differ between the arms, and nothing else:

1. **The skill.** `skills/provenance-numbers.md` is `study8/SKILL_A.md` or
   `study8/SKILL_B.md`, both committed verbatim beside this file, both derived
   from the shipped `scaffold/templates/PROVENANCE_NUMBERS_SKILL.md` with **only
   the addressing instructions changed** — the `v`/`u` rules, the "you name a
   location, you never say what is at it" rule, the `uncited` routing and the
   closing paragraphs are the shipped text. Both delete `at`. It reaches the
   generator by the shipped channel: a committed `skills/*.md` whose front matter
   says `requires_check: number_source`, selected by `skills.select` against the
   project's live `checks:`, rendered by `skills.render`, hashed into the receipt,
   never shown to the auditor.
2. **The deterministic-contract sentence.** `cli/build.py:709` renders
   `dcl.describe(cfg.checks)` into the generator prompt, and the shipped sentence
   describes the shipped grammar. An arm that changes the grammar and leaves that
   sentence alone would hand the generator two contradicting contracts. Each
   arm's sentence is produced by a **committed, targeted substitution** on the
   shipped text (`provenance_arm3._A_SUFFIX`, `_B_EDITS`, `_B_SUFFIX`); both are
   written to `contract-A.txt` / `contract-B.txt` in the run directory and their
   sha256 into `plan.json`. This is part of each arm's definition, not a
   deviation.
3. **Arm A only: the gutter.** `generator.build_prompt` is wrapped at the harness
   boundary so each file in `current` is rendered with `"{:>5}| "` before its
   line, numbered **per file, 1-based over `split("\n")`**, byte-identically to
   how `numbers._span` indexes. **A file the runtime already replaced with a
   structural outline or a stub is passed through unnumbered** (`outline.py`'s
   own markers decide), because an outline's line 10 is not the file's line 10;
   which paths were numbered and which were not is recorded per generator call.
   Arm B needs no prompt change.

**`checks: ["number_source"]`**, an explicit one-check list rather than the
`science` profile, so Arm 2's 48 incidental `CA-META-001` schema blockers stay
out of the record (design §5). `number_source` must still be selected or the
annotation skill is never rendered at all.

**Nothing under `src/` is modified.** Both verifiers are implemented in
`benchmarks/expertlongbench/provenance_arm3.py` and both call
`crossaudit.dcl.numbers.contains_pair` and its fixed unit-synonym table for the
verification half, so that half is byte-identical to the shipped check and only
the addressing half differs.

### 2.1 Contract A's verifier

`src` is `"uncited"`, `governed:…`, or `path#L<n>` / `path#L<n>-L<m>` with the
optional `@<sha>` pin. The locator resolves as `numbers._resolve` resolves
(exact key, then relative to the annotating artefact's directory); the span is
the named lines; the disposition is `contains_pair(span, v, u)`. Unresolvable
locator, malformed row, non-number `v`, range outside the file, failed pin →
BLOCKER `CA-NUM-001`. Pair not in the span → BLOCKER `CA-NUM-002`. `uncited` and
`governed:` → ADVISORY `CA-NUM-003`, always, whatever else the row says.

### 2.2 Contract B's verifier

`src` is `"uncited"`, `governed:…`, or `{"file": path, "quote": <1..80 chars>}`
with an optional `"sha"` pin. One normalisation, on **both** sides: every run of
whitespace collapsed to a single space (`normalise_unit`'s fold applied to a
longer string). Then, **in this order**, which is load-bearing:

    occurrences == 0                -> BLOCKER  CA-NUM-001   (not in the file)
    occurrences  > 1                -> ADVISORY CA-NUM-004   (ambiguous)
    not contains_pair(quote, v, u)  -> BLOCKER  CA-NUM-002   (quote lacks the pair)
    otherwise                       -> pass

Malformed row, unresolvable path, a quote outside 1..80 characters, a failed pin
→ BLOCKER `CA-NUM-001`.

The verifiers' §4 mutation fixtures are committed and run before the arm:
`study8/test_arm3_verifiers.py`.

## 3. Primary outcome — one number per arm, named in advance

> **Among the arm's BLOCKABLE annotation rows whose named location genuinely
> contains the transcribed `(v, u)` pair — adjudicated by a deterministic re-read
> of that location, never by a model — the fraction the arm's verifier BLOCKS.**

Unit of analysis: the annotation row. Rows cluster within drafts, so the Wilson
interval is reported **beside** a draft-clustered bootstrap (§7).

**Gate denominator: blockable rows.** B's ambiguous rows are ADVISORY by routing
— they resolve and contain the value; what is unresolved is *which* occurrence, a
property of the source and not a defect in the annotation — so they route where
`uncited` routes and are **excluded from the denominator**, exactly as
`PROVENANCE_ADDRESSING.md` §3.5 instructs, and stated here before the arm runs.
Rows whose `src` is `uncited` or `governed:` are excluded from both arms'
denominators for the same reason. The rate over the denominator *including*
ambiguous rows is printed as a labelled sensitivity, and §4's disposition is not
read off it.

## 4. The kill / pass rule — `PROVENANCE_CHECKS.md` §8g, verbatim, per arm

> **The kill fires if the interval's lower bound exceeds 2%; the arm passes only
> if the upper bound is below 5%; anything between is reported as inconclusive
> and the check ships ADVISORY-only until a larger n resolves it.**

Read against the **Wilson 95% interval on that arm's primary**, at whatever n the
arm reaches. The draft-clustered bootstrap is reported beside it. No other rule
is constructed and no secondary is promoted to "the result". Where a denominator
is thin the number is quoted as the count (EXPERIMENT_RECORD §9).

## 5. Secondary outcomes, all named in advance

Per arm unless said otherwise.

1. **Rows resolved** — the fraction of rows for which the arm's verifier finds
   the address and the pair (disposition `pass`). Reported over **blockable** rows
   and over **addressed** rows (addressed = not `uncited`, not `governed:`),
   each beside the design §3 simulated ceiling it is the measured counterpart of:
   **A 150/183 = 82.0%**; **B 142/166 = 85.5% blockable, 142/183 = 77.6%
   addressed**. An arm materially below its own prediction has falsified its own
   mechanism (design §5).
2. **`uncited` rate** over all rows (Arm 2 measured 14.88%).
3. **Ambiguous rate** (B): addressed rows whose quote occurs more than once.
4. **Paraphrase rate** (B): addressed rows whose quote is **not** found by exact
   whitespace-folded bytes while the pair **is** present somewhere in the named
   file. This is the failure the design says would change its recommendation, and
   it is reported against the design's predicted 13.1% absent-quote rate with the
   part attributable to source absence separated from the part attributable to
   retyping.
5. **Token cost and money per draft per arm**, from the product's own usage
   ledger, split generator / auditor, never reconstructed.
6. **Annotation rate**: rows written / numbers present in the draft prose, the
   latter by Arm 1's `NUM` extractor over the fence-stripped draft, so all three
   arms share the denominator's instrument and its known blind spots.
7. **Unit shortening** — a transcribed unit that is a strict prefix of the whole
   unit token at an occurrence of its value. Arm 2 measured **zero in 183 rows**;
   the expectation here is zero.
8. **Outline-replaced files** — how many citable files this corpus caused the
   runtime to render as an outline or a stub, i.e. how often A's known new hazard
   is even reachable. Any block on a citation into such a file is its own class
   (§9) and is reported explicitly.
9. **The malformed-envelope re-ask**, counted per arm as drafts placing more than
   one generator-role call in a one-round run. Arm 2 saw it on 23 of 24 rounds at
   ≈¼ of generator spend. **It is counted, not fixed** — fixing it inside this
   study would change the generator path the arms are being compared on.

## 6. The two adjudicators

Both deterministic, both re-reading the named location from the committed project
tree at the audited commit, neither a model, and **both resolving the location
themselves** rather than asking the verifier which bytes it looked at.

* **A (primary).** `crossaudit.dcl.numbers.contains_pair(location, v, u)`.
* **B (independent).** Written in the harness, importing nothing from `src/`:
  positive iff `str(v)` is a substring of the located text **and** (`u` is empty
  **or** `str(u)` is a substring of it). No normalisation, no synonyms, no
  tokenisation, no number canonicalisation. Arm 2's, unchanged.

The **located text** is the named span (A) or the whitespace-folded quote as the
file holds it (B). A row that names no location this study can re-read —
`uncited`, `governed:`, malformed, an unresolvable path, a range outside the
file, or (B) a quote the file does not contain — is A-negative and B-negative by
definition. The 2×2 agreement table is reported per arm and every disagreement is
hand-inspected.

## 7. Intervals (EXPERIMENT_RECORD §10)

* **Wilson 95% score interval on a binomial proportion of annotation rows** — the
  preregistered interval, the one §4 is read against, named as such at every use.
* **Draft-clustered 95% percentile bootstrap on the same proportion**, 10,000
  resamples of the drafts, beside it; resamples with an empty denominator are
  discarded and the count of discards reported.

## 8. The comparison, and the decision rule — both written before the run

**Paired by instance**, on the resolved-row fraction (§5.1), over blockable rows
and over addressed rows:

* **Exact McNemar on the discordant pair directions** — for each instance, the
  sign of (A's resolved fraction − B's); the exact two-sided binomial test on the
  discordant signs. (Identical in this form to the exact paired sign test; named
  as both, because the pairing is at the instance and not at the row.)
* **Draft-clustered sign-flip randomisation** beside it on the mean paired
  difference, 10,000 draws, each instance's whole difference flipping together;
  with a paired percentile bootstrap 95% interval for that mean difference.

Also reported: the false-blocker rate side by side with both intervals.

**The decision rule, fixed here:**

1. Prefer the arm that passes §8g.
2. **If both pass**, prefer the higher resolved fraction over blockable rows —
   **unless the difference lies inside the paired interval**, in which case the
   arms are not separated by this study on that outcome and the recommendation
   falls to the design's own standing argument (cost, structure, `PROVENANCE_
   ADDRESSING.md` §7), which is stated as such and not as a measurement.
3. **If exactly one passes**, build that one.
4. **If neither passes**, report that and recommend **against both**, and say
   what the data require of the next design.

## 9. Block classification, written before any block is seen

Every BLOCKER-producing row is classified into exactly one class, evaluated in
order, first match wins. Every block is then hand-inspected against its class and
any hand correction is recorded as a numbered deviation with its reason.

1. **verifier wrong** — the location resolves and adjudicator A says it contains
   the pair, and the arm blocked anyway. This class is the primary's numerator.
2. **malformed row** — the row's fields the arm's grammar cannot read at all: a
   missing or non-scalar `v`/`u`, an empty or non-numeric `v`, a `src` that is not
   this arm's shape, a quote outside 1..80 characters, a malformed pin. *Added to
   the seven classes the task named, here, before any block was seen, because
   neither contract's grammar guarantees a well-formed row and a class list with
   no home for one would force a silent miscoding.*
3. **outline-replaced file** — the cited file was rendered to this generator as a
   structural outline or a stub in the round that produced the draft. A's known
   new hazard, isolated so it can never hide inside another class.
4. **unparsed notation** — the transcribed unit still contains a space **after**
   the shipped synonym fold (so `wt %`, which the table folds to `wt%` and which
   does match, is not miscoded here — this is Arm 2's hand correction turned into
   a rule and fixed before any block was seen), or the located text holds an
   occurrence of the value that the check's `_UNPARSED` rule rejects.
5. **ambiguous** — the named location occurs more than once. Advisory by routing,
   so it can only be reached if a later change makes it block; kept so the table
   is total.
6. **paraphrase** (B) — the quote is not found in the named file by exact
   whitespace-folded bytes, and the pair **is** present somewhere in that file.
7. **generator wrong file** — the named path is not in the audited increment, or
   it resolves and the pair occurs nowhere in it. (A B row whose quote is absent
   and whose pair is also absent from the file lands here, not in 6.)
8. **generator wrong line/quote** — the pair occurs in the named file but not
   where the row said it was.

Classes 1 is the verifier's error; 3, 4 and 5 are properties of the contract; 2,
6, 7 and 8 are generator errors. Each block's machine reason string is recorded
beside its class as data.

## 10. n, budget and the stopping rule

* **Corpus.** `T03MaterialSEG.jsonl`, sha256
  `0b525eae93aab406d13e5f90b61afbed575dae7d789e70af6a470a764a2b1af0`, 50 rows,
  CC BY-NC-SA 4.0, not redistributed and never committed.
* **n = 24 instances × 2 arms = 48 drafts**, the same 24 as Arm 2: batch 1 is
  `choose_samples(rows, 16, seed=20261104)`, batch 2 is
  `choose_samples(rows not in batch 1, 8, seed=20261104)`.
* **Budget $4.00**, read from the product's own usage ledger. Arm 2 spent
  $0.0741/instance, so 48 rounds is ≈$3.56 before B's ≈180 extra output tokens per
  draft; the design's own $3 estimate assumed the re-ask fix, which §5.9 forbids
  this study from landing.
* **Paired ordering.** Instances run in seeded order and **both arms of an
  instance run back to back**, so a budget stop leaves complete pairs. The unit of
  the comparison is the pair; half a pair is not a datum and is excluded from
  every paired figure (and reported).
* **Stopping rule.** The study stops at the first of: (a) all 24 pairs complete;
  (b) study spend reaching $4.00; (c) three consecutive instance-level failures
  with the same cause, reported as a harness failure rather than a result. An
  instance-arm whose loop errors is retried **once**; a second failure is a
  dropped cell, named with its cause in the report's deviations.

## 11. What is recorded, and what may never be committed

Per annotation row, committed as JSONL: instance id, arm, row index, `src` kind,
the address itself where it carries no corpus text (a path, a path plus a line
number), the **sha256 and length** of the quote, of `v` and of `u`, the
disposition, the machine reason, both adjudications, the occurrence count, the
block class and detail, and the unit-shortening flag. **The transcribed values,
units and quoted spans are corpus-derived text and are never committed** — only
their digests and lengths. Per draft: instance, arm, rows, numbers present, the
gutter log (which paths were numbered and which were not), tokens, cost, wall
time, rounds, prompt sha256, output sha256, and whether the receipt's
`inputs.manifest` equals the reconstructed increment.

Run directories hold model output that quotes the corpus; they are gitignored and
archived to `~/Documents/Crossaudit/study-data/wt-arm3-runs/` with a per-file
sha256 manifest whose digests are recorded in the report.

## 12. Reproduction

    export PYTHONPATH=<worktree>/src
    set -a && . ~/.crossaudit-keys.env && set +a
    cp <corpus> benchmarks/expertlongbench/data/T03MaterialSEG.jsonl   # gitignored
    python3 benchmarks/expertlongbench/study8/test_arm3_verifiers.py
    python3 benchmarks/expertlongbench/provenance_arm3.py --batch 1 --out <abs>
    python3 benchmarks/expertlongbench/provenance_arm3.py --batch 2 --out <abs>
    python3 benchmarks/expertlongbench/provenance_arm3_report.py <abs>

## 13. Already done before this document was committed

One **credentials probe**: two completions of a few tokens each
(`anthropic:claude-sonnet-4-6`, `openai:gpt-5.6-terra`) in a scratch project
outside the worktree, ≈$0.0002. It touched no corpus row and produced no study
datum. It counts against the §10 budget. Declared here before this file was
committed, as Arm 2 declared its own.

## 14. Limitations known in advance

* One task, one corpus, one vendor pair, one round — as Arm 2. Nothing here
  generalises past T03MaterialSEG with this generator.
* **Both arms' primary adjudicator is the verifier's own containment test**
  applied to an independently resolved location. Without `at`, each arm's
  disposition and its adjudication now differ only in *how the location is
  resolved*, so a near-zero false-blocker rate is the expected outcome and is
  weak evidence on its own. That is why §5.1 exists and why the design calls the
  resolved fraction "the real discriminator"; §4's disposition is still read off
  the primary, as preregistered.
* No control arm without an annotation skill, so the cost the contract *adds* is
  not measured; what is measured is the total and each arm's share.
* Run-to-run variation is unmeasured for this contrast: no replicate arm exists
  for this estimand.
