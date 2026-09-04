# Study 5 — preregistration

Written and committed **before any model was called under the frozen sha**, per
`benchmarks/EXPERIMENT_RECORD.md` §1. Results go to `RESULTS-5.md`. Anything this file
does not name in advance is labelled **exploratory** wherever it appears there.

An earlier, unregistered trial of this harness ran and was discarded; see
`RESULTS-5.md` Deviations, which lists it in full along with the OpenAI quota failure
that ended it. No result from it is carried forward, and nothing in this file was chosen
after seeing it.

---

## The hypothesis

CrossAudit's central claim is that work is judged better when the judge comes from a
**different vendor** than the writer. The heterogeneity invariant (`config.heterogeneity`)
refuses a same-vendor generator/auditor pair, and the README sells that refusal as the
core of the protocol. It has never been measured.

**H1.** On T03MaterialSEG, an auditor from a different vendor than the generator names
more of the defects in a draft than an auditor that *is* the generator.

**H1 can come out false**, and the two ways it can are both live. Study 2 found that
replacing the auditor with a stronger model from the same vendor moved recall from 2.0%
to 3.8% — model identity barely mattered. If vendor identity matters as little, `cross`
and `self` will be indistinguishable, and the invariant is not buying what the README
says it buys. That result is reported first if it occurs, and is not re-run.

**H0.** `cross` and `self` recall are equal.

## Primary outcome — one number, named now

> **The paired difference in round-one audit recall against CLEAR ground truth,
> `cross` minus `self`, over the same drafts**, where recall for an arm on an instance is

    (rubric items CLEAR scored wrong that some finding of that arm named)
    ---------------------------------------------------------------------
              (rubric items CLEAR scored wrong in that draft)

and a finding is mapped to rubric items by the **adjudicator model**, which is the mapping
studies 1–3 used, so this number is comparable to their 2.0% and 23.5%.

Reported as a mean paired difference in percentage points, with a 95% confidence interval
and an exact two-sided Wilcoxon signed-rank p, on the instances where at least one item
was wrong.

## Secondary outcomes, named now

1. Same paired difference, `cross` − `sibling`, and `sibling` − `self`.
2. The same three comparisons under the **deterministic rule mapping** (`CA-RUBRIC-00N`
   *is* rubric item N by construction, no model in the loop), as a sensitivity check on
   the adjudicator model.
3. **Item precision** per arm — of the items an arm named, the fraction CLEAR had in fact
   scored wrong — with a Wilson interval. Precision was 100% in studies 1–2 and 73% in
   study 3; a collapse would matter and is watched for.
4. **Firing rate**: instances where the arm said anything at all.
5. **Gating rate**: instances where the arm raised at least one BLOCKER. A finding filed
   ADVISORY does not gate the increment, so an arm can name a real defect and still ship
   the draft unchanged. Recall restricted to BLOCKER findings is reported beside it.
6. **The noise floor** (study B, below).

## Arms

One generator writes **one** draft per instance through the product's real build loop,
capped at one round. That single committed draft is then judged four ways. Judging the
same bytes is what makes the arms comparable; **nothing is regenerated per arm.**

| arm | who judges | vendor vs. generator |
|---|---|---|
| `cross` | `openai:gpt-5.6-terra` — the shipped configuration | different |
| `self` | `anthropic:claude-sonnet-4-6` — the generator itself | same vendor, same weights |
| `sibling` | `anthropic:claude-opus-4-8` | same vendor, different model |
| `none` | nothing | — |

**Held fixed across arms:** the draft, the committed tree, the constitution and its
commit, the deterministic-check output, the audit prompt (byte-identical — the harness
prints its digest beside the digest the product's own audit recorded for the same commit,
and the study fails if they differ), the system message, the reply parser and rule
validator, the CLEAR ground truth, and the adjudicator. **Varying:** which model receives
the prompt. That is the whole experiment.

`none` is the floor. It places no call, so its recall is 0 by construction. It is not a
comparison; it is the statement of what a draft that is never judged gets named about it.

## Rules: rubric-grade, on purpose

The constitution is generated from the task's own evaluation rubric, not the shipped
general one. Under the general rules the auditor is near-silent — 2.0% recall in studies
2 and 3 — and **all four arms would look identical because none of them would say
anything**, which would be a null result about the constitution masquerading as a null
result about vendors. This is a deliberate departure from the shipped default and is
restated at the top of the results.

## The heterogeneity bypass

`self` and `sibling` cannot exist while `config.heterogeneity` runs, and the guard is
inside `crossaudit.auditor.run.run_audit`. The harness therefore does not call
`run_audit`; it calls the same product functions `run_audit` calls, in the same order,
and skips the one guard. **`src/` is not modified.** The product still refuses a
same-vendor pair everywhere a user can reach it. If the arms had required weakening the
guard, the study would have stopped and said so instead.

## n, and why

**n = 16** instances for study A, drawn with seed `20261104` from the task's 50 rows
(sorted by id, sampled, re-sorted). Study 3 used 20 at roughly US$0.12 per instance for a
single arm; this study judges four times per instance, and 16 keeps all four arms inside
the study's share of a US$20 two-study budget with room for the replicates below. A
larger n that cannot afford `cross` is worth less than a smaller n that completes it,
which is why the arms are ordered `cross`, `self`, `sibling`, `none` and every instance is
judged by all four before the next is generated.

**Study B — the noise floor.** The identical configuration is repeated **three times on
the same 8 instances** (the first 8 of the same seeded sample), changing nothing that the
harness can control. The provider layer exposes no seed and temperature comes from the
model's capability card, so what varies is provider nondeterminism — which is exactly the
variance every previously published delta in this project has been read against without
being measured. The run-to-run standard deviation of each arm mean is reported, and
every earlier finding is stated as surviving it or not.

n = 8 for the replicates is a cost decision taken now: three passes at 8 costs about what
one pass at 24 costs, and the quantity being estimated is a spread across runs, not a
difference across instances.

## Stopping rule

Run to completion of the seeded sample. Stop early and report what completed if the
study's share of the **US$20 across both studies** is spent; spend is read from the
product's own usage ledger, not reconstructed. No arm is dropped to buy more instances,
and no instance is dropped after its scores are seen.

## Multiple comparisons

This study makes **7** preregistered inferential comparisons: three paired recall tests
under the adjudicator mapping (H1 plus two secondaries) and the same three under the rule
mapping, plus the noise-floor spread. The primary outcome is named above and was not
selected after looking. This is also the fifth study over the same task and the same 50
rows, and that history is part of the multiple-comparison picture; it is restated in the
results rather than left for a reader to reconstruct.

## What would change the conclusion

- If `cross` − `self` is smaller than the run-to-run standard deviation from study B, the
  difference is not a finding whatever its p value, and the results say so in the first
  paragraph.
- If the harness prompt digest ever differs from the product's for the same commit, the
  arms are not judging the same thing and the study is void.
- If an arm's replies fail the rule validator materially more often than another's, its
  recall is not comparable and that is reported rather than absorbed.
