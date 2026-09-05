# Study 7 — Arm 2 of the provenance measurement: the generator writes its own annotations

Preregistered **before any study model call**, at `b1756f5de16887b04067bce89a51a5edff5e83f2`
on `study/provenance-arm2` (branched from `fusion/evidence-authority`; provenance slice 1
is `5395cc8` in its history). Binding: `benchmarks/EXPERIMENT_RECORD.md` §1–§10.

Arm 1 (`docs/design/PROVENANCE_CHECKS.md` §6, `provenance_arm1.py`, D157) annotated 16
archived drafts with a probe and blocked 7 of 365 pair-matched citations (1.92%, Wilson
[0.93, 3.91]). All seven were the **probe's** extraction errors (`°C/min` captured as
`°C`, `10⁻²` as `10`). The corpus can no longer separate the verifier's false-blocker
rate from the instrument's. Only a generator writing its own annotations under the
shipped skill can measure the real rate. That is this arm.

---

## 1. Hypothesis, in a form that can come out false

**H.** When the shipped house skill (`scaffold/templates/PROVENANCE_NUMBERS_SKILL.md`)
reaches the generator through the shipped channel, the generator writes
`crossaudit-numbers` annotations whose named spans genuinely contain the transcribed
`(v, u)` pair, and the shipped `number_source` check blocks so few of those correct
annotations that it has earned a non-overridable blocker.

It comes out false if the check blocks correct annotations at a rate whose Wilson 95%
lower bound exceeds 2%.

## 2. Primary outcome — one number, named in advance

**The false-blocker rate on correct annotations:**

> Among generator-written annotation rows whose `src` locator **genuinely contains** the
> transcribed `(v, u)` pair — adjudicated by a deterministic re-read of the named source
> span, never by a model — the fraction for which the shipped check emits a **BLOCKER**.

Unit of analysis: the annotation row. Rows are clustered within drafts, so the Wilson
interval is reported **beside** a draft-clustered bootstrap (§7).

## 3. The kill / pass rule — `PROVENANCE_CHECKS.md` §8g, verbatim

> **Arm 2's kill fires if the interval's lower bound exceeds 2%; Arm 2 passes only if the
> upper bound is below 5%; anything between is reported as inconclusive and the check
> ships ADVISORY-only until a larger n resolves it.**

The interval this rule is read against is the **Wilson 95% interval on the primary**, at
whatever n the study reaches. No other rule is constructed, and no second objective is
promoted to "the result". A result between the two bounds is reported as INCONCLUSIVE and
the report states the n that would resolve it.

## 4. Secondary outcomes, all named in advance

1. **`uncited` rate** — the fraction of rows the generator writes with `src: "uncited"`
   (Arm 1's corpus expectation is ≈13%; much higher means the generator opts out rather
   than annotating).
2. **Correct-block rate** — of all BLOCKERs, the fraction classified as a generator error
   (wrong locator or wrong transcription) rather than a verifier false blocker.
3. **Annotation rate per draft** — rows written / numbers present in the draft prose.
   "Numbers present" is counted by the Arm 1 probe's `NUM` extractor over the draft with
   the fence removed, so the denominator is the same instrument Arm 1 used (26.9 numbers
   per draft) and the two arms remain comparable. Its known limits are Arm 1's.
4. **Cost and tokens added per draft** — from the product's own usage ledger, per
   instance, split generator / auditor.
5. **Unit-shortening** — how often the generator transcribed a unit that is a strict
   prefix of the whole unit token at the named occurrence (`°C` where the source says
   `°C/min`). This is Arm 1's instrument failure, now measured on the generator's side.
6. **Hyphen stratum (D157, open product dial)** — blocks caused by a hyphenated English
   word following the unit (`5 g-sample` → `g`), reported as their own stratum and never
   folded silently into any other number.

## 5. Sensitivity analysis, not a second objective

The primary's denominator is defined by **adjudicator A**, which is the check's own
`contains_pair`. A second, independent, simpler adjudicator **B** is applied to every
resolvable row (§6). The block rate over B's denominator is reported as a **preregistered
sensitivity analysis** with its own interval, clearly labelled. **§3's disposition is read
off the primary only.** B exists so the adjudicator is not silently the thing being
measured, and so the agreement between the two is reportable.

## 6. The two adjudicators

Both are deterministic, both re-read the named span from the committed project tree at the
audited commit, and neither is a model.

* **A (primary).** `crossaudit.dcl.numbers.contains_pair(span, v, u)` — the check's own
  containment test, applied to the span the adjudicator resolves independently of the
  check run.
* **B (independent).** Written in the harness, importing nothing from `src/`: the row is
  B-positive iff `str(v)` is a substring of the span **and** (`u` is empty **or** `str(u)`
  is a substring of the span). No normalisation, no synonym table, no tokenisation, no
  number canonicalisation.

Rows whose `src` is `uncited` or begins with `governed:` carry no locator and are
adjudicated by neither; they are excluded from both denominators and counted under §4.1.
A row whose locator does not resolve (path absent from the audited increment, range
outside the file, malformed locator, malformed row) is A-negative and B-negative by
definition.

The 2×2 agreement table between A and B is reported, and **every disagreement is
hand-inspected**.

## 7. Intervals (§10)

* **Wilson 95% score interval on a binomial proportion of annotation rows** — the
  preregistered interval, and the one §3 is read against. Named as such at every use.
* **Draft-clustered bootstrap 95% percentile interval on the same proportion**, 10,000
  resamples of the 16 (or 24) *drafts* with replacement, reported beside it, because rows
  within a draft are not independent. Where a resample has an empty denominator it is
  discarded and the count of discards is reported.

Every interval is quoted with its method and the quantity it covers, in the same sentence.
Counts small enough that an interval reaches an absurd bound are quoted as the count.

## 8. Design, n, and the pooling rule

* **Corpus.** `T03MaterialSEG.jsonl`, sha256
  `0b525eae93aab406d13e5f90b61afbed575dae7d789e70af6a470a764a2b1af0`, 50 rows,
  CC BY-NC-SA 4.0, not redistributed and never committed.
* **Batch 1 — n = 16.** The **same seed and sample as Arm 1**: `choose_samples(rows, 16,
  seed=20261104)`, which reproduces exactly the 16 instance ids in
  `study-data/wt-revision-runs/armT-scoped/plan.json`, so the two arms are comparable.
* **Pooling rule, fixed here.** If, after batch 1, the money already spent plus 8 ×
  (batch 1's mean per-instance cost) is at or under the **$4** budget, **batch 2 runs**:
  8 further instances, `choose_samples(rows not in batch 1, 8, seed=20261104)`, pooled to
  **n = 24**, and every number in the report is recomputed on the pooled set. The decision
  to pool is made on **budget alone** and is taken before the primary is computed on batch
  1; it is never conditioned on the observed rate. If batch 2 runs, the batch-1-only
  numbers are also reported, so the reader can see the pooling.
* **One generator round per instance** (`max_rounds: 1`). The measurement is the
  generator's first-pass annotation behaviour under the skill; a revision round would
  confound it with repair of the check's own blocks.
* **Held fixed:** generator `anthropic:claude-sonnet-4-6`; auditor `openai:gpt-5.6-terra`
  (the loop requires a cross-vendor auditor; its verdict is not an outcome of this study);
  the shipped `GENERAL_AUDIT_RULES.md` constitution; `checks: science`
  (`schema, units, convergence, provenance, number_source`), which is what
  `crossaudit init` writes for a science project; the shipped house skill written verbatim
  by `crossaudit.scaffold.annotation_skill_tree`; the paper's own T03 model prompt plus
  run.py's two location facts, byte-identical to Arm 1's arm-B instruction.
* **No prompt engineering.** The skill is the shipped template, unmodified. If the skill or
  the check has a defect, that is a finding and it is reported, not fixed. `src/` is not
  modified in this study.

## 9. Stopping rule

The study stops at the first of: (a) all instances of the batches authorised by §8
completed; (b) total study spend reaching **$4.00**, read from the product's usage ledger;
(c) three consecutive instance-level failures with the same cause, which is reported as a
harness failure rather than a result. An instance whose loop errors is retried **once**;
a second failure is recorded as a dropped cell with its cause and named in §5 of the
report.

## 10. Block classification, written before any block is seen

Every BLOCKER-producing row is classified into exactly one class by this deterministic
rule, evaluated in order, first match wins. Every block is then hand-inspected against its
class, and any hand correction is recorded as a numbered deviation with its reason.

1. **generator wrong locator (unresolved)** — the row is malformed (a missing or
   non-scalar field, an empty `v`, a `v` that is not a number, an `at` outside the
   artefact), or `src` is not of the form `path#L…`, or the named path is not in the
   audited increment, or the pinned sha does not match, or the line range is outside the
   file. (These are exactly CA-NUM-001 before any span is read.)
2. **verifier false blocker** — the locator resolves and **adjudicator A says the span
   contains the pair**, and the check blocked anyway. This class is the primary numerator.
3. **hyphenated-word case** — the span holds an occurrence of the value whose following
   unit token has the shape `<u>-<word>`, where `<word>` starts with an ASCII letter and
   `<u>` normalises to the transcribed unit (D157's `5 g-sample`).
4. **unparsed notation** — the span holds an occurrence of the value that the check's
   `_UNPARSED` rule rejects (a superscript exponent, `×10ⁿ`, `^n`), or the transcribed
   unit contains a space (the documented first-token limit), or the transcribed value
   itself contains notation the number pattern cannot read.
5. **generator wrong locator (wrong line)** — the pair, under adjudicator A, occurs
   somewhere else in the **named file** but not in the named span.
6. **generator wrong transcription** — the residual: the pair occurs nowhere in the named
   file.

Classes 3 and 4 are properties of the **contract**, not of either party, and are reported
in their own strata (§4.6, §4 note). Classes 1, 5 and 6 are generator errors — correct
blocks. Class 2 is the verifier's error.

## 11. What is recorded, and what may never be committed

Per annotation row, committed as JSONL: instance id, draft path, `at`, `src`, sha256 of
`v`, sha256 of `u`, their lengths, the shipped check's disposition
(`pass` / `CA-NUM-001` / `CA-NUM-002` / `CA-NUM-003`), adjudicator A, adjudicator B, the
block class, and the unit-shortening flag. **The transcribed values and units themselves
are corpus-derived text and are never committed** — only their digests. Per draft:
instance id, rows, `uncited` count, numbers present, tokens in/out, cost, wall time,
rounds, prompt sha256, output sha256. Run directories (which hold model output quoting the
corpus) are archived to `~/Documents/Crossaudit/study-data/wt-arm2-runs/` with a sha256
manifest, and their absolute paths and digests are recorded in the report.

## 12. Reproduction

    export PYTHONPATH=<worktree>/src
    set -a && . ~/.crossaudit-keys.env && set +a
    cp <corpus> benchmarks/expertlongbench/data/T03MaterialSEG.jsonl   # gitignored
    python3 benchmarks/expertlongbench/provenance_arm2.py --batch 1
    python3 benchmarks/expertlongbench/provenance_arm2_report.py <run-dir> [...]

`provenance_arm2.py` extends the Arm 1 harness rather than replacing it: it reuses
`provenance_arm1.wilson`, the Arm 1 probe's `NUM` extractor for the §4.3 denominator, and
`run.py`'s bootstrap and loop entry, so the two arms share their instrument wherever they
measure the same thing.

## 13. Already done before this document was committed

One **credentials probe**: two 4-token completions (`anthropic:claude-sonnet-4-6`,
`openai:gpt-5.6-terra`), $0.000228 total, in a scratch project outside the worktree. It
touched no corpus row and produced no study datum. It counts against the §9 budget.
