# Study 15 — Arm 6: the shipped check on a second domain (T01LegalMDS)

Preregistered **before any study model call**, on `study/provenance-arm6` (branched from
`fusion/evidence-authority` at d8d5210, after the Arm 5 merge and D164). Binding:
`benchmarks/EXPERIMENT_RECORD.md` §1–§10, `docs/design/PROVENANCE_CHECKS.md` §6–§8g, D159
ruling 2, D164 rulings 3–5 (the adjudicator is preregistered here; T01 is the corpus;
results prose describes shapes, every rate carries its intervals, instruments are described
by executing them), and `study8/PREREGISTRATION-ARM5.md` with its three amendments (the
census that chose T01: 93.3% of its reference numbers occur in the input; 0.6% carry a
unit; inputs are number-dense — median 5,067.5 per input — and long).

## 1. Hypotheses, each in a form that can come out false

**H6a (the §8g question on a second domain).** With the shipped skill and the shipped
`number_source` check (D164's matcher), on legal case summaries whose numbers are dates,
amounts, docket and citation numbers, the check blocks so few correct annotation rows that
it stays inside the §8g pass band. It comes out false if the Wilson lower bound exceeds 2%.

**H6b (the one-line rule on hard-wrapped documents).** T01's inputs are wrapped at a median
of 58 characters per line (2,825 lines per input at the cap of §2.4). The contract requires a
quotation to lie within one line. H6b says the generator can still quote within a line
often enough that **the cross-line block rate over addressed rows is at most 20%**. It comes
out false if the Wilson lower bound of that rate exceeds 20% — in which case the check, on
this domain, blocks correct citations for a reason that is the contract's shape and not
the generator's error, and **the check does not enter any profile for prose-wrapped
documents until the line rule is redesigned** (a decision record, not a fix in this arm).
This is the finding this arm is most likely to produce, and it is preregistered so that
it cannot be read as a surprise.

## 2. The arm, and what is held fixed

One arm, **S**, exactly Arm 5's harness (`provenance_arm6.py` imports Arm 4's and Arm 5's):
generator `anthropic:claude-sonnet-4-6`, auditor `openai:gpt-5.6-terra`, `max_rounds: 1`,
the shipped general constitution, `checks: ["number_source"]`, the shipped skill, contract
and per-row verifier, matcher blob in `plan.json`. What differs:

1. **The task is T01LegalMDS**, transcribed from the paper's Appendix B (Table 5 model
   prompt, B.1.5 rubric) at e70b7f5 by copying the PDF's extracted text; the loop's
   instruction names the source as "case documents" and the deliverable as "summary"
   (`Task.source_noun`, `Task.deliverable_noun`; T03's instruction bytes are unchanged
   and asserted so). The source file keeps the harness path `work/synthesis/RECIPE.md`.
2. **The population is every T01 instance whose input is at most 200,000 characters — 33
   of 100** (`study15/arm6_population.txt`), in corpus order, no seed: the cap is the
   generator's context (a 200,000-character file is ~50,000 tokens beside the prompt), and
   the median input in that population is 159,917 characters with 2,966 numbers. n = 33
   drafts. The 67 larger instances are out of scope and said so.
3. **The primary is adjudicated on the QUOTATION** (D164 ruling 3): the located text a
   labeller sees is the quoted run the generator wrote, and "genuinely contains" is judged
   on it under the frozen gold rule. The line-level reading (`contains_pair` on the line
   the quotation selects) is reported beside it as secondary 12, and every row where the
   two disagree is listed with its mechanism.
4. **Budget $30.00** (Arm 5: $0.089 per draft on 626-character inputs; here the inputs are
   ~250× longer, and the generator and auditor both read them — expected ≈ $0.60 per
   draft, ≈ $20). The loop stops after the draft in which cumulative ledger spend exceeds
   the budget; a stopped run reports its n.

## 3. Primary outcome

Arm 4 §3's definition with the adjudicator of §2.3: among BLOCKABLE rows whose quotation
genuinely contains the transcribed `(v, u)` pair, the fraction the shipped check BLOCKS.
Blockable as Arm 4 §3. **A block whose quotation the file does not hold on one line — the
cross-line class — has no located text, is N by definition for the primary (as in Arms 4–5),
and is counted by H6b.** Two labellers blinded to each other and to the verdict; every block
with a located quotation, and 50 passes drawn with seed 20261108; L1 the author's session,
L2 an independent model from another vendor; κ reported; `?` excluded and counted.

## 4. The kill / pass rules, verbatim

§8g on the primary: *kill if the interval's lower bound exceeds 2%; pass only if the upper
bound is below 5%; anything between is inconclusive.* And H6b's: *the check does not enter
any profile for prose-wrapped documents if the cross-line rate's Wilson lower bound exceeds
20%.* Both are read; both are reported in the first paragraph; H6b's fires independently of
§8g's.

## 5. Secondary outcomes

Arm 5 §5's thirteen, and:

14. **Cross-line rate** (H6b) with intervals, and among cross-line rows the share whose
    pair is present in the named file (paraphrase vs a real citation the line rule
    refuses).
15. **The unit-bearing share** of annotation rows and of blockable rows: how much of this
    domain's load the empty-unit contract carries (the census says 0.6% of reference
    numbers carry a unit).
16. **Date and amount shapes**: the share of transcribed values that are years, day
    numbers, dollar amounts or docket numbers, read from the archived rows by hand after
    labelling and carried as data — because the check's meaning on a date is "the numeral
    occurs in the quotation", and the reader should know how often that is all it says.

## 6. Intervals

Wilson 95% score interval named as such at every use; draft-clustered 95% percentile
bootstrap (10,000 resamples of the drafts, seed 20261108) beside it, for every rate quoted,
secondaries included (D164 ruling 5).

## 7. What is recorded, and what may never be committed

As Arm 5 §8: `study15/rows-arm6.jsonl`, `manifest-arm6.json`, `key-arm6.jsonl`,
`L1-arm6.csv`, `L2-arm6.csv`, `GOLD-arm6.csv`, `report-arm6.json`, the population list by id;
**never corpus text, never a draft, never a quotation, never a fragment in prose** — a
corpus scan runs before every commit of prose. Drafts, projects, the sheet and the log go
to `~/Documents/Crossaudit/study-data/wt-arm6-runs/`.

## 8. Decision, written before the run

* **§8g PASS and H6b holds** → the check's D164 standing extends to a second domain; the
  profile ruling needs no change.
* **§8g PASS and H6b fails** → the check keeps its science-profile standing (T03 is not
  wrapped) and a decision record says the one-line rule does not fit hard-wrapped prose;
  the redesign (a quotation may span a soft wrap) is a preregistered slice of its own.
* **§8g inconclusive or KILL** → as Arm 5 §9, for this domain.

## 9. Reproduction

```sh
export PYTHONPATH=<worktree>/src
set -a && . ~/.crossaudit-keys.env && set +a
python3 benchmarks/expertlongbench/provenance_arm6.py --dry-run --out <abs>
python3 benchmarks/expertlongbench/provenance_arm6.py --out <abs>
python3 benchmarks/expertlongbench/study15/arm6_sheet.py --runs <abs> --out <sheet-dir>
python3 benchmarks/expertlongbench/provenance_arm4_report.py <abs> --arm 6
```

## 10. Limitations known in advance

One generator; L2 a model; the gold rule about characters, on a domain where the numbers
are dates and identifiers; a size-capped population; the checklist quality of the
summaries is not measured (the arm measures the check, not the summary).

## Amendment 1 — 2026-09-07, after attempt 1 and before attempt 2; nothing above is edited

1. **Attempt 1 (run `arm6-20260907T061203Z`) escalated 8 of 8 instances in round 1** and was
   stopped by the author after the eighth; `ATTEMPT-1.md` records the cause read from the
   product's code: an outlined source (over `MAX_FILE_BYTES`) needs a `file_read` tool call,
   the generator narrates the call beside the envelope, and the single re-ask restated the
   file envelope. The eight records stay in the archive (`arm6-attempt1-escalated/`) and are
   reported as the arm's first attempt; they carry no rows and enter no rate.
2. **The product changed between attempts**: `fix/envelope-re-ask` (the re-ask restates the
   envelope the reply attempted; the parser unchanged), reviewed cross-vendor and merged
   before attempt 2; its commit is in attempt 2's `plan.json` as `code_sha`, and D165 records
   the ruling. Attempt 2 measures the product after that merge — a product-path fix, not a
   change to the check, the skill, the contract or the matcher (their sha256s in the plan
   are asserted equal to attempt 1's).
3. **The eight instances of attempt 1 were re-run once under the fix as the fix's probe**
   (`PROBE-envelope-fix.md`, archive `probe-envelope-fix/`), from the fix's tree at 066a7a1 +
   the Arm 6 commits. Attempt 2 **does not run them a third time**: their probe records and
   project directories are copied into attempt 2's run directory before it starts, so the
   runner records them as done, and attempt 2 runs the remaining 25. The eight therefore
   count in attempt 2's rates exactly as the other 25 do — same product code path, same
   skill, contract and matcher — with the one difference that their run predates the
   review's merge; if the review changes the fix, they are re-run instead.
4. **What the probe previewed is not a result and is not pre-empted here**: 3 of 8 drafts
   with a fence, 9 rows, 0 passes, 3 cross-line. H6b's bar (20%) and §8g stand as written;
   the annotation rate (secondary 8) is reported with intervals and, if it is below Arm 5's
   by more than the intervals allow, said in the first paragraph. `file_read` returns up to
   512 KiB (`gitio.MAX_BLOB_BYTES`), so every source in the population was returned whole;
   a low annotation rate is the generator's, not a truncated read's.

## Amendment 2 — 2026-09-07, before attempt 2; Amendment 1 stands as written

Amendment 1 §3 said the eight probe instances would count in attempt 2 unless the review
changed the fix. **The review changed the fix** (rounds 1–3 of `fix/envelope-re-ask`: the
compute re-ask's schema, routing by an envelope attribute rather than message text, an
opened-and-never-closed envelope treated as that envelope's failure, the reordered-marker
form), so the probe archive measured a parser that is not the one that merges. Per §3's own
rule, **attempt 2 runs all 33 instances under the merged product**; the probe stays in the
archive as the fix's evidence and enters no rate. The run directory seeded from the probe
was set aside unused (`wt-arm6-runs/arm6-seed-unused/`, with its note) before attempt 2.

## Amendment 3 — 2026-09-07, during attempt 2; Amendments 1–2 stand as written

Attempt 2 (run directory `wt-arm6-runs/arm6`, started at code bd491d5's Arm 6 branch after
the envelope fix merged) was **paused by the author after instance 12 of 33**: 6 drafts
completed; 6 instances escalated in round 1 with no generator call and no spend — the
first (instance 3) on a transport error (an SSL EOF from the provider), the next five on
the provider's HTTP 400 "credit balance is too low" — the Anthropic generator key's credit
was exhausted mid-run. Nothing about the product or the harness failed; the run was stopped
so the remaining instances would not be recorded as outages.

**Resumption rule, fixed now:** when credit is restored, the six outage records are moved
out of `records.jsonl` into `records-outage.jsonl` (kept, counted in the results as
"provider outages, re-run"), their instance directories set aside, and the runner resumes
the same run directory, which records the 6 completed drafts as done and runs the other
27. The results report 33 drafts with the outage count beside them; an instance that
fails again for a product reason is recorded and counted as the preregistration says.
