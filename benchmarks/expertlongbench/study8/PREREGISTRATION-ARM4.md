# Study 8 — Arm 4: the shipped check and the shipped skill, on a fresh sample

Preregistered **before any study model call**, on `fusion/evidence-authority`
after the merge of `feat/provenance-slice-3` (a17109e). Binding:
`benchmarks/EXPERIMENT_RECORD.md` §1–§10, `docs/design/PROVENANCE_CHECKS.md`
§6–§8g, `docs/design/CONTAINMENT_RULE.md` §4, D159 ruling 2, D160 rulings 2–3.

D160 ruling 2: `number_source` enters no profile until Arm 4 — *the built check,
the shipped skill, a fresh sample, §8g* — passes. Ruling 3: Arm 4 runs after the
narrowing and E4, because E4 changes the false-blocker rate by construction.
Both landed in slice 3 (nine review rounds; `study9/RESULTS.md`). This arm runs
what ships, as it ships, on instances no earlier arm saw.

---

## 1. Hypothesis, in a form that can come out false

**H4.** With the shipped annotation skill and the shipped `number_source` check
(content addressing, the narrowing, E4), the generator writes annotation rows
whose named location genuinely contains the transcribed `(v, u)` pair, and the
check blocks so few of those correct rows that it has earned a non-overridable
blocker in a default profile.

It comes out false if the check blocks correct annotations at a rate whose
Wilson 95% lower bound exceeds 2% (§4).

## 2. The arm, and what is held fixed

One arm, **S** (shipped). Generator `anthropic:claude-sonnet-4-6`, auditor
`openai:gpt-5.6-terra`, `max_rounds: 1`, the shipped general constitution, the
task's own instruction, the product's generator path in a real scaffolded
project — all as in Arms 2 and 3. `checks: ["number_source"]`, the explicit
one-check list, for the reason Arm 3 §2 gives.

What differs from Arm 3, and nothing else:

1. **The skill is the shipped one**, rendered by the product's own
   `scaffold.annotation_skill_tree(["number_source"])` — byte-identical to what
   `crossaudit init` writes — and committed as `skills/provenance-numbers.md`
   in the project before the run. Its sha256 goes into `plan.json`.
2. **The contract sentence is the shipped one**: `dcl.describe(["number_source"])`
   unmodified, written to `contract-S.txt` and hashed into `plan.json`.
3. **The verifier is the shipped check itself**: `numbers._row_findings`, the
   function `check_number_source` calls per row, run by the harness on the
   audited increment rebuilt from the committed tree — so the disposition the
   harness records is the disposition the product's DCL gave. Nothing under
   `src/` is modified. No gutter, no prompt wrapper.
4. **The sample is fresh**: every T03MaterialSEG row whose id is not among the
   24 in `study8/manifest.json` (Arms 2 and 3). The corpus has 50 rows, so
   **n = 26 drafts**, one per instance, no selection and no seed. The 24 used
   rows are excluded by id, not by position.

## 3. Primary outcome — one number, named in advance

> **Among BLOCKABLE annotation rows whose named location genuinely contains the
> transcribed `(v, u)` pair, the fraction the shipped check BLOCKS.**

Unit of analysis: the annotation row; rows cluster within drafts (§7).

**Blockable** = a row whose `src` is neither `uncited` nor `governed:` and whose
disposition is not the advisory ambiguity (a quotation the file says on more
than one line), exactly as Arm 3 §3.

**"Genuinely contains" is NOT decided by the check.** Arm 3 could use
`contains_pair` as its primary adjudicator because its verifiers differed from
the shipped check in the addressing half; here the check *is* `contains_pair`
on the line the quotation selects, so using it as adjudicator would let the
check agree with itself. The adjudicator is therefore the **frozen gold rule**
(`study8gold/PREREGISTRATION-GOLD.md` §2, R1–R15, Amendment 1), applied by two
labellers blinded to each other and to the verdict, on a sheet that shows only
an opaque id, the located line, `v` and `u`:

* **every BLOCK** is labelled (`C`: the line states the pair; `N`; `?`);
* **a sample of 50 PASSES**, drawn with seed 20261106 from the pass rows, is
  labelled the same way, as the false-pass sensitivity (the earlier gold found
  7.33% [4.14, 12.65] false passes in the pre-slice-3 matcher; slice 3 closed
  that class on the gold, 11 of 11, and this sample says whether it stays
  closed on new text).

Labeller L1 is the author's model session; L2 is an independent model from
another vendor (`codex exec`, read-only, the sheet and the rule only). Cohen's
κ is reported; disagreements are adjudicated by the rule text and recorded;
`?` items are excluded from the primary and counted.

Then: **numerator** = blocks labelled `C`; **denominator** = blocks labelled `C`
+ all passes (passes taken as containing, with the 50-row sample as the stated
correction: the denominator is also reported with passes scaled by the sample's
`C` fraction, as a sensitivity, never as the primary).

## 4. The kill / pass rule — `PROVENANCE_CHECKS.md` §8g, verbatim

> **The kill fires if the interval's lower bound exceeds 2%; the arm passes only
> if the upper bound is below 5%; anything between is reported as inconclusive
> and the check ships ADVISORY-only until a larger n resolves it.**

Read against the Wilson 95% interval on the primary, at whatever n the arm
reaches; the draft-clustered bootstrap is reported beside it; a thin denominator
is quoted as the count (EXPERIMENT_RECORD §9). No other rule is constructed.
Arm 3 measured A 0/183 and B 2/167 on the *candidate* contracts; this is the
first measurement of the shipped one.

## 5. Secondary outcomes, all named in advance

1. **`uncited` rate** over all rows, against Arm 3's 10.68% (A) and 6.80% (B).
   `CONTAINMENT_RULE.md` §4 names this the failure to watch: the skill's `(c)`
   sentence routes unreadable units to `uncited`, and a materially higher rate
   would mean the block rate was bought by opting out.
2. **Rows resolved** (disposition pass) over blockable and over addressed rows.
3. **Ambiguous rate**: addressed rows whose quotation the file says on more than
   one line (ADVISORY by routing).
4. **Quote-absent rate** and **cross-line rate**: addressed rows the file does
   not contain by folded characters, and rows whose quotation the file writes
   across a line break; each split by whether the pair is present somewhere in
   the named file (paraphrase vs wrong file).
5. **Mechanism** of every block, `CONTAINMENT_RULE.md` §1's M-labels, read from
   the archived drafts by hand after labelling and carried as data in
   `rows.jsonl`; the **substratum** (`study8/emit_records.py`) beside it.
6. **Matcher version**: the git blob id of `src/crossaudit/dcl/numbers.py` at
   the run's code sha, in every row.
7. **Unit shortening** (Arm 3 §5.7), expected zero.
8. **Annotation rate**: rows written / numbers present, Arm 1's `NUM` extractor.
9. **Cost per draft**, generator/auditor split, from the product's ledger; the
   **malformed-envelope re-ask** count (drafts with more than one generator-role
   call in a one-round run), counted and not fixed.
10. **`adjudicator_b`** (exact substring, `src/`-free) on every located line, as
    the sensitivity instrument the gold study disqualified as a primary
    (`CONTAINMENT_RULE.md` §3); its 2×2 against the gold labels is reported.

## 6. Intervals (EXPERIMENT_RECORD §10)

Wilson 95% score interval on a binomial proportion of annotation rows for every
rate, named as such at every use; beside it a draft-clustered 95% percentile
bootstrap (10,000 resamples of the 26 drafts, seed 20261106). Coverage of the
Wilson interval under clustering is not claimed; the bootstrap is the check.

## 7. n, budget and the stopping rule

n = 26 drafts (§2.4). Budget **$3.00**; Arm 3 cost $0.0628 per draft, so the
expected spend is ≈ $1.63. The loop stops after the draft in which cumulative
ledger spend exceeds the budget; a stopped run reports its n and nothing is
extrapolated. A draft whose loop errors is recorded and excluded from every
rate, and counted.

## 8. What is recorded, and what may never be committed

As Arm 3 §11: `study8/rows-arm4.jsonl` and `study8/manifest-arm4.json` with
digests, lengths, addresses, dispositions, reasons, adjudications, labels,
mechanism and matcher version — **never corpus text, never a draft, never a
quotation**. Drafts, project trees and the labelling sheets go to
`~/Documents/Crossaudit/study-data/wt-arm4-runs/` (CC BY-NC-SA 4.0, not
redistributed). The gold labels' `L1.csv` / `L2.csv` / adjudication carry ids
and labels only and are committed.

## 9. Decision, written before the run

* **PASS** → `number_source` may enter the `science` profile (D159 ruling 2),
  in a separate change with its own review; this arm does not make that change.
* **Inconclusive** → the check ships ADVISORY-only in any profile; a larger n is
  the next study, not a wider interval.
* **KILL** → the check stays out of every profile; the blocks are classified
  (§5.5) and the classes go back to the containment design.

The `uncited` secondary cannot change the disposition, but a rate materially
above Arm 3's is reported in the first paragraph of the results, not the last.

## 10. Reproduction

```sh
export PYTHONPATH=<worktree>/src
set -a && . ~/.crossaudit-keys.env && set +a
python3 benchmarks/expertlongbench/provenance_arm4.py --dry-run --out <abs>
python3 benchmarks/expertlongbench/provenance_arm4.py --out <abs>
python3 benchmarks/expertlongbench/provenance_arm4.py --reanalyse --out <abs>
```

## 11. Limitations known in advance

Same generator and auditor as Arms 2–3, so this measures one generator's
transcription discipline; one task family (T03); L2 is a model, not a domain
expert, and the gold rule is a rule about characters, not about chemistry;
passes outside the 50-row sample are taken as containing; the `uncited` route
is a legitimate contract outcome that this arm counts and cannot judge.
