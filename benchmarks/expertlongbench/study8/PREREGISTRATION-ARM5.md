# Study 8 — Arm 5: the shipped check, after the containment extensions, on every T03 instance

Preregistered **before any study model call**, on `study/provenance-arm5` (branched from
`fusion/evidence-authority` at b7e2128, after the merge of slice 8). Binding:
`benchmarks/EXPERIMENT_RECORD.md` §1–§10, `docs/design/PROVENANCE_CHECKS.md` §6–§8g,
`docs/design/CONTAINMENT_RULE.md` §4, D159 ruling 2, D160 rulings 2–3, **D161 rulings 1–4**,
and `PREREGISTRATION-ARM4.md`, which this arm repeats with the changes of §2.

D161 ruling 1 took the KILL branch on Arm 4 (9 of 189, Wilson 2.53–8.80%) and ruling 2
ordered the containment extensions, each measured on the frozen gold with W = 0; they are
all shipped or ruled (slices 4–8: E5, E6, E1, E2, E3 shipped; M10 measured and not shipped).
Ruling 3 said Arm 5 runs after they land, "on a fresh sample … either from another
ExpertLongBench task with its own preregistration, or re-runs Arm 3's 24 with the changed
matcher and says so." **This arm takes the second option, and says so** (§2.4): the other
six public tasks were censused on 2026-09-07 and none carries numbers a provenance check
can trace — T04 has none, T07's input is a SMILES string and T08's a sequence (0% of the
description's numbers occur in the input), T11's references carry one number (the label),
T06's transcripts spell most of theirs, and T01 is 250,000 characters of legal record per
instance whose numbers are dates and docket numbers with no unit. The census script and
its counts are in `study8/arm5_census.txt`.

## 1. Hypothesis, in a form that can come out false

**H5.** With the shipped annotation skill and the shipped `number_source` check as it
ships after slices 4–8, the generator writes annotation rows whose named location
genuinely contains the transcribed `(v, u)` pair, and the check blocks so few of those
correct rows that it has earned a non-overridable blocker in a default profile.

It comes out false if the check blocks correct annotations at a rate whose Wilson 95%
lower bound exceeds 2% (§4). It is **expected to come out true**: Arm 4's nine wrong
blocks were 5 × E1, 1 × E2, 2 × M10, 1 × hyphen-after-unit; E1 and E2 now ship, so the
residual classes are M10 and the hyphen, 3 of 189 on Arm 4's text (1.59%, Wilson
0.54–4.56%). At Arm 5's n the pass band (upper bound < 5%) is reachable: at ~380 blockable
rows, up to ~10 wrong blocks pass and 11–13 are inconclusive. That is the expectation, not
the result; a generator writing new shapes under the extended matcher is what this arm
measures.

## 2. The arm, and what is held fixed

One arm, **S** (shipped), exactly Arm 4's: generator `anthropic:claude-sonnet-4-6`,
auditor `openai:gpt-5.6-terra`, `max_rounds: 1`, the shipped general constitution, the
task's own instruction, the product's generator path in a real scaffolded project,
`checks: ["number_source"]`; the shipped skill rendered by `annotation_skill_tree`,
the shipped contract sentence from `dcl.describe`, the shipped per-row verifier
`numbers._row_findings` on the audited increment rebuilt from the committed tree; nothing
under `src/` modified, no wrapper. `provenance_arm5.py` imports Arm 4's harness and
changes only what follows.

1. **The matcher is the one that ships now**: `numbers.py` at this branch's base (blob in
   `plan.json`, and in every row as `matcher_version`), after E5, E6, E1, E2, E3 and the
   M10 sentence. Arm 4 ran the merge of slice 3.
2. **The skill and the contract are the ones that ship now** — they gained sentences in
   slices 4–8 (ranges, lists, subscripts, en-dash exponents); their sha256 goes into
   `plan.json` beside Arm 4's for the diff to be visible.
3. **Budget $5.00** (Arm 4 spent $1.98 on 26 drafts).
4. **The sample is every corpus row, n = 50 drafts**, in corpus order, no selection and
   no seed. Two strata are named in advance and reported separately as secondaries:
   the **26 Arm 4 instances**, a replicate of Arm 4 under the changed matcher and skill
   (the same instances, a fresh draft each — the generator is stochastic, so this is a
   replicate of the arm, not of the drafts); and the **24 Arms 2–3 instances**, which the
   shipped skill has never been run on (Arms 2–3 used the candidate skills A and B).
   Neither stratum is fresh in ruling 3's first sense, and the results say so in the
   first paragraph.

## 3. Primary outcome — one number, named in advance

Arm 4 §3 verbatim: **among BLOCKABLE annotation rows whose named location genuinely
contains the transcribed `(v, u)` pair, the fraction the shipped check BLOCKS**, over all
50 drafts. Blockable as Arm 4 §3. "Genuinely contains" is decided by the **frozen gold
rule** (`study8gold/PREREGISTRATION-GOLD.md` §2, R1–R15, Amendment 1) applied by two
labellers blinded to each other and to the verdict on a sheet showing only an opaque id,
the located line, `v` and `u`: **every BLOCK** and **a sample of 50 PASSES** drawn with
seed 20261107. L1 is the author's session; L2 an independent model from another vendor
(`codex exec`, read-only, the sheet and the rule only). κ reported; disagreements
adjudicated by the rule text and recorded; `?` excluded from the primary and counted.
Numerator and denominator as Arm 4 §3, with the same sensitivity.

## 4. The kill / pass rule — `PROVENANCE_CHECKS.md` §8g, verbatim

> **The kill fires if the interval's lower bound exceeds 2%; the arm passes only if the
> upper bound is below 5%; anything between is reported as inconclusive and the check
> ships ADVISORY-only until a larger n resolves it.**

Read against the Wilson 95% interval on the primary over all 50 drafts; the
draft-clustered bootstrap beside it. **The strata of §2.4 do not decide anything**: they
are reported, and a stratum that would read differently from the whole is reported as
such.

## 5. Secondary outcomes, all named in advance

Arm 4 §5's ten, plus:

11. **The two strata** (§2.4): the primary and the `uncited` rate on each, with intervals.
12. **Paired with Arm 4 on the 26 replicate instances**: blocks per instance under Arm 4
    and under Arm 5, and the mechanism of every Arm 5 block against Arm 4's nine — which
    classes returned, which did not, and any class not seen before, each with its
    M-label; M10 rows are expected and are the disclosed limit, not a finding.
13. **What the extensions did on this text**: every Arm 5 block re-run through the
    Arm 4 matcher blob (`8dfd07d9…`) in memory, and every Arm 5 pass likewise, so the
    number of rows the extensions moved on a real generator's output is a count beside
    the gold's R = 33 (E5 1 + E6 2 + E1 14 + E2 5 + E3 11).

## 6. Intervals

Arm 4 §6: Wilson 95% score interval named as such at every use; draft-clustered 95%
percentile bootstrap (10,000 resamples of the 50 drafts, seed 20261107) beside it.

## 7. n, budget and the stopping rule

n = 50 drafts. Budget **$5.00**; expected spend ≈ $3.80 at Arm 4's $0.076 per draft. The
loop stops after the draft in which cumulative ledger spend exceeds the budget; a stopped
run reports its n. An errored draft is recorded, excluded from every rate, and counted.

## 8. What is recorded, and what may never be committed

As Arm 4 §8: `study8/rows-arm5.jsonl`, `manifest-arm5.json`, `key-arm5.jsonl`,
`L1-arm5.csv`, `L2-arm5.csv`, `GOLD-arm5.csv` — ids, digests, dispositions, labels,
mechanisms, matcher version; **never corpus text, never a draft, never a quotation**.
Drafts, projects and sheets go to `~/Documents/Crossaudit/study-data/wt-arm5-runs/`.

## 9. Decision, written before the run

* **PASS** → `number_source` may enter the `science` profile (D159 ruling 2), in a
  separate change with its own review; this arm does not make that change.
* **Inconclusive** → ADVISORY-only in any profile; the next study is a larger n or a
  second task family (T01, the only other task with traceable numbers, with its own
  preregistration and a budget matched to its 250,000-character inputs).
* **KILL** → the check stays out of every profile; the blocks are classified and go
  back to the containment design.

## 10. Reproduction

```sh
export PYTHONPATH=<worktree>/src
set -a && . ~/.crossaudit-keys.env && set +a
python3 benchmarks/expertlongbench/provenance_arm5.py --dry-run --out <abs>
python3 benchmarks/expertlongbench/provenance_arm5.py --out <abs>
python3 benchmarks/expertlongbench/provenance_arm5.py --reanalyse --out <abs>
python3 benchmarks/expertlongbench/study8/arm5_sheet.py --runs <abs> --out <sheet-dir>
python3 benchmarks/expertlongbench/provenance_arm4_report.py <abs> --arm 5
```

## 11. Limitations known in advance

Arm 4 §11's, and: the instances are not fresh (§2.4), so a generator that memorised
nothing across runs is assumed and not checked; one task family still; the T01 option
was censused and deferred, not refused.

## Amendment 1 — 2026-09-07, after the second review; nothing above is edited

**Erratum to §0's census rationale.** §0 says none of the other six public tasks "carries
numbers a provenance check can trace". The census table this file cites shows T01LegalMDS
with 93.3% of its reference numbers occurring in the input: T01 *is* traceable. The reason
T01 was not chosen is its shape and cost — 250,000 characters of legal record per instance,
and numbers that are dates and docket numbers with no unit — and RESULTS-ARM5 says so; §9's
"inconclusive" branch already names T01 as the next corpus. The four tasks the sentence is
true of are T04, T07, T08 and T11; T06 writes most of its numbers in words.

## Amendment 2 — 2026-09-07, after the third review; Amendment 1 stands as written

**Amendment 1 overclaimed in the same direction as §0.** It said §0's sentence is "true of
T04, T07, T08 and T11". The census table says otherwise: T04's references hold 19 numbers
in all, 12 of them (63.2%) occurring in the input, one with a unit — a median of zero
numbers per input is not absence; T07's description numbers occur in the input 39.0% of
the time (§0 also says "0–39%", and the 0% is T08's, not T07's); T11's 155 reference
numbers are 47.1% traceable. The categorical rationale — "no numbers a provenance check
can trace" — is withdrawn for every task. **The rationale that the census supports** is
density and units: the shipped check reads `(value, unit)` pairs against a source line,
and T03 is the only public task whose inputs are number-dense (median 16.5 numbers per
input against 0 for T04, T06, T07, T08 and 10 for T11's traces) *and* whose quantities
carry units (T04 26%, T06 20%, every other task ≤ 1.3%, T03's procedures throughout). T01 is
traceable (93.3%) and unit-less, and deferred for shape and cost as Amendment 1 says.

## Amendment 3 — 2026-09-07, after the fourth review; Amendments 1–2 stand as written

Amendment 2 called T01 "unit-less" and said T03 is "the only public task" that is both
number-dense and unit-bearing. The census says: T01's inputs carry a median of 5,067
numbers — denser than T03's 16.5 — and 43 of its 6,938 reference numbers (0.6%, 22 of them
percentages) carry a unit the extractor recognises. "Unit-less" is withdrawn for "0.6%
with a unit", and "only T03" for "T03 is the task whose inputs are number-dense and whose
quantities carry units throughout; no other public task combines the two at that level".
The deferral of T01 rests on shape, cost and unit density, none of which is categorical.
