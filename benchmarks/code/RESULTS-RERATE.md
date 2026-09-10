# Study 21 — the residual re-rated with the oracle question asked first

Preregistration: `rerate/PREREGISTRATION.md` (committed before any label; seed 20260914).
Raters: L1 the author; L2 `gpt-6-astra` through the Codex CLI, read-only, from the blind sheet
alone. Material: ceiling 1's archived residual dump (68 instances: the 57-instance all-family
residual and the 11 instances only the third family flagged), shown without instance ids, prior
categories or residual membership. No API spend; L2 ran on the Codex subscription.

## The finding

**Under a rule that asks "does the specification determine the expected value?" before "did the
visible suite exercise this input?", the residual is not mostly unexercised edge. It is mostly
oracle-defined.** Consensus of the two raters on the 57 all-family residual instances:

<!-- tables:begin -->
### Table 1 — consensus category of the residual, oracle question first

Unit: the instance; primary interval the problem-cluster percentile bootstrap (seed 20260914, 10,000 resamples); Wilson beside it, too narrow. `disputed` = the two raters differ; counted toward neither category.

| population | n (problems) | category | consensus count | share [95% cluster CI] (Wilson) |
|---|---:|---|---:|---|
| all_families_residual | 57 (34) | `timeout` | 3 | **3 of 57** (5.3% [0.0, 14.3]; Wilson [1.8, 14.4]) |
| all_families_residual | 57 (34) | `ambiguous-oracle` | 44 | **44 of 57** (77.2% [62.1, 91.1]; Wilson [64.8, 86.2]) |
| all_families_residual | 57 (34) | `unexercised-edge` | 2 | **2 of 57** (3.5% [0.0, 10.9]; Wilson [1.0, 11.9]) |
| all_families_residual | 57 (34) | `disputed` | 8 | **8 of 57** (14.0% [3.4, 26.8]; Wilson [7.3, 25.3]) |
| sheet_68 | 68 (40) | `timeout` | 5 | **5 of 68** (7.4% [0.0, 16.7]; Wilson [3.2, 16.1]) |
| sheet_68 | 68 (40) | `ambiguous-oracle` | 46 | **46 of 68** (67.6% [52.2, 82.1]; Wilson [55.8, 77.6]) |
| sheet_68 | 68 (40) | `unexercised-edge` | 9 | **9 of 68** (13.2% [3.0, 25.0]; Wilson [7.1, 23.3]) |
| sheet_68 | 68 (40) | `disputed` | 8 | **8 of 68** (11.8% [2.9, 23.0]; Wilson [6.1, 21.5]) |

### Table 2 — the two raters

| raters | agree | n | Cohen κ (six categories) |
|---|---:|---:|---:|
| L1 (author) vs L2 (`gpt-6-astra`, blind) | 60 | 68 | **0.722** |

| disputed instance | L1 | L2 |
|---|---|---|
| `b1:Mbpp/398` | ambiguous-oracle | unexercised-edge |
| `b1:Mbpp/594` | unexercised-edge | ambiguous-oracle |
| `b1:Mbpp/630` | other | ambiguous-oracle |
| `b1:Mbpp/792` | unexercised-edge | ambiguous-oracle |
| `b2:Mbpp/142` | ambiguous-oracle | unexercised-edge |
| `b2:Mbpp/398` | ambiguous-oracle | unexercised-edge |
| `b2:Mbpp/630` | other | ambiguous-oracle |
| `b2:Mbpp/792` | unexercised-edge | ambiguous-oracle |

### Table 3 — EXPLORATORY: ceiling 1's all-family union recall on an oracle-clean denominator

Assumption stated in the preregistration and repeated here: only the residual was re-rated; the 53 flagged instances are treated as oracle-clean, which they were never checked to be.

| denominator | P | flagged by any draw | union recall at K_max | residual share |
|---|---:|---:|---:|---:|
| registered (ceiling 1) | 110 | 53 | 48.2% | 51.8% |
| oracle-clean (P minus 44 consensus-ambiguous residual instances) | 66 | 53 | 80.3% | 19.7% |
<!-- tables:end -->

The preregistered kill for the sentence "the residual is mostly unexercised edge" fires on both
of its conditions: consensus `ambiguous-oracle` is 44 of 57 (the bar was 30), consensus
`unexercised-edge` is 2 of 57 (the bar was 29). Of the 44, ceiling 1's classification had
called 39 `unexercised-edge` and 5 `spec-misreading`.

What the two raters were agreeing on, in shape: hidden inputs outside the class the
specification names (unsorted arrays for a function specified over sorted ones; dates not in the
stated format; inputs of unequal length for a function specified over parallel lists); hidden
expected values that follow from the dataset's reference implementation and not from the
prose (a truncating zip where the prose says "per digit"; a sentinel returned where the prose
says "check"; a count that includes or excludes the unrotated string); and inputs on which the
prose entails the candidate's value and the hidden suite asserts another. The two consensus
`unexercised-edge` instances are the ones where the prose does determine the value and the
visible suite never built the input (a negative bound; a nested list where a flat one was shown).

## What this does and does not say

1. **The category depends on the rule's ordering — and that is the result.** Ceiling 1's rule
   put `unexercised-edge` fourth from last and `ambiguous-oracle` fifth; this study's rule puts
   the oracle question second. The same 57 instances go 46/57 one way and 44/57 the other. A
   classification that flips with the order of its questions is not a fact about the auditor;
   the paper's claim (2) — "the ceiling is set by unexercised edges" — cannot be quoted in that
   form. What survives both orderings is narrower: the residual consists of hidden failures
   the specification's prose does not let a reader anticipate, either because the prose does
   not determine the value (this study's reading) or because no visible test pointed at the
   input (ceiling 1's).
2. **Raters.** L1 is the author of both rules and of the paper; L2 is a model of the same vendor
   family as one auditor under study. Both were blind to ids and prior categories, and they
   agreed on 60 of 68 with κ 0.722 (six categories). The preregistration asked for a human rater
   who is not the author; none was available. This is the study's largest limitation and it is
   not one more labelling pass can remove.
3. **Duplicates.** The sheet carries two candidates per problem for most problems (the two
   generators), with the same specification and often the same witness; the raters effectively
   read 40 problems. The problem-cluster interval is the one to quote.
4. **The oracle-clean restatement is exploratory and one-sided.** Only the residual was rated.
   If some of the 53 flagged instances are also oracle-defined, both numerator and denominator
   shrink and the 80.3% moves; the registered 48.2% is the quotable recall. Amendment 1 rates the
   flagged instances under the same rule.
5. **Nothing here re-runs an auditor.** Ceiling 1's union recalls, asymptotes and the arm
   differences are untouched; this study changes what the residual is called, not its size.

## Cost

No API spend. L2: one Codex CLI call; L1: one reading of 68 items.
