# Study 21 — the residual re-rated with the oracle question asked first

Preregistration: `rerate/PREREGISTRATION.md` (committed before any label; seed 20260914;
Amendment 1 committed after the residual result and before any flagged label). Raters: L1 the
author; L2 `gpt-6-astra` through the Codex CLI, read-only, from the blind sheets alone. Material:
ceiling 1's archived residual dump (68 instances: the 57-instance all-family residual and the 11
instances only the third family flagged) and, under Amendment 1, the 53 stratum-P instances some
draw did flag, built with the same dumper. Both sheets show an opaque id, the specification, the
visible suite, the candidate, the canonical solution and the witness (the first failing hidden
inputs with expected and actual values) — not the instance id, the prior category, or whether
any draw flagged the instance. No API spend; L2 ran on the Codex subscription.

## The finding

**Under a rule that asks "does the specification determine the expected value?" before "did the
visible suite exercise this input?", the residual is not mostly unexercised edge. It is mostly
oracle-defined — and so is a large part of what the auditors flagged.**

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
| flagged_P | 53 (33) | `timeout` | 4 | **4 of 53** (7.5% [0.0, 17.6]; Wilson [3.0, 17.9]) |
| flagged_P | 53 (33) | `ambiguous-oracle` | 24 | **24 of 53** (45.3% [28.3, 63.3]; Wilson [32.7, 58.5]) |
| flagged_P | 53 (33) | `unexercised-edge` | 23 | **23 of 53** (43.4% [25.0, 60.7]; Wilson [31.0, 56.7]) |
| flagged_P | 53 (33) | `disputed` | 2 | **2 of 53** (3.8% [0.0, 10.0]; Wilson [1.0, 12.8]) |

### Table 2 — the two raters (disputed instances from both sheets)

| raters | agree | n | Cohen κ (six categories) |
|---|---:|---:|---:|
| L1 (author) vs L2 (`gpt-6-astra`, blind) | 60 | 68 | **0.722** |

| disputed instance | L1 | L2 |
|---|---|---|
| `b1:Mbpp/142` | ambiguous-oracle | unexercised-edge |
| `b1:Mbpp/398` | ambiguous-oracle | unexercised-edge |
| `b1:Mbpp/594` | unexercised-edge | ambiguous-oracle |
| `b1:Mbpp/630` | other | ambiguous-oracle |
| `b1:Mbpp/792` | unexercised-edge | ambiguous-oracle |
| `b2:Mbpp/142` | ambiguous-oracle | unexercised-edge |
| `b2:Mbpp/398` | ambiguous-oracle | unexercised-edge |
| `b2:Mbpp/594` | unexercised-edge | ambiguous-oracle |
| `b2:Mbpp/630` | other | ambiguous-oracle |
| `b2:Mbpp/792` | unexercised-edge | ambiguous-oracle |

| raters, flagged sheet | agree | n | Cohen κ |
|---|---:|---:|---:|
| L1 vs L2 | 51 | 53 | **0.933** |

Test-retest on the 11 instances both sheets carry (rated twice, blind both times, the flagged sheet's label used): L1 same 11 of 11, L2 same 11 of 11.

### Table 3 — ceiling 1's all-family union recall on the oracle-clean denominator (Amendment 1 secondary)

Rule: Amendment 1: (53 − a_f) / (110 − a_r − a_f); disputed count as not ambiguous. Interval: problem-cluster bootstrap over the 110 P instances' (flagged, ambiguous) pairs, seed 20260924; Wilson beside it.

| denominator | P | flagged by any draw | union recall at K_max [95% cluster CI] (Wilson) | residual share |
|---|---:|---:|---|---:|
| registered (ceiling 1) | 110 | 53 | 48.2% | 51.8% |
| oracle-clean (minus 44 residual + 24 flagged consensus-ambiguous) | 42 | 29 | **69.0%** [50.0, 86.4] (Wilson [54.0, 80.9]) | 31.0% |

### Table 4 — POST HOC: ceiling 1's union recall by the defect's consensus category

Asked after Table 1's flagged counts were seen; not preregistered. Recall = flagged by any of the 20 draws.

| consensus category | n P instances (problems) | flagged | recall [95% cluster CI] (Wilson) |
|---|---:|---:|---|
| `timeout` | 7 (4) | 4 | **4 of 7** (57.1% [14.3, 100.0]; Wilson [25.0, 84.2]) |
| `ambiguous-oracle` | 68 (34) | 24 | **24 of 68** (35.3% [22.1, 50.0]; Wilson [25.0, 47.2]) |
| `unexercised-edge` | 25 (13) | 23 | **23 of 25** (92.0% [75.0, 100.0]; Wilson [75.0, 97.8]) |
| `disputed` | 10 (5) | 2 | **2 of 10** (20.0% [0.0, 40.0]; Wilson [5.7, 51.0]) |
<!-- tables:end -->

The preregistered kill for the sentence "the residual is mostly unexercised edge" fires on both
of its conditions: consensus `ambiguous-oracle` is 44 of 57 (the bar was 30), consensus
`unexercised-edge` is 2 of 57 (the bar was 29). Of the 44, ceiling 1's classification had
called 39 `unexercised-edge` and 5 `spec-misreading`.

Amendment 1's secondary: among the 53 flagged P instances the consensus is 24 `ambiguous-oracle`
and 23 `unexercised-edge`, so the oracle-clean denominator is 42 instances, of which 29 were
flagged — union recall 69.0% [50.0, 86.4] against the registered 48.2%. The registered number
stays the quotable recall; this one says what it would be if the 68 consensus-ambiguous instances
were struck from P.

The post-hoc split (Table 4) is the sentence the two preregistered numbers point at: of the 25
P instances both raters call spec-determined-and-unexercised, the twenty draws flagged 23; of the
68 both call oracle-defined, 24. It is post hoc — asked after the flagged counts were seen — and
it is a description of one substrate under one rule, not a preregistered estimate.

What the two raters were agreeing on, in shape: hidden inputs outside the class the
specification names (unsorted arrays for a function specified over sorted ones; dates not in the
stated format; inputs of unequal length for a function specified over parallel lists); hidden
expected values that follow from the dataset's reference implementation and not from the
prose (a truncating zip where the prose says "per digit"; a sentinel returned where the prose
says "check"; a count that includes or excludes the unrotated string; a name filter stricter
than the prose's); and inputs on which the prose entails the candidate's value and the hidden
suite asserts another. The consensus `unexercised-edge` instances are the ones where the prose
does determine the value and the visible suite never built the input (a negative bound; a nested
list where a flat one was shown; floor division where the prose says division; an unhashable
element; a duplicate the count must pair).

## What this does and does not say

1. **The category depends on the rule's ordering — and that is the result.** Ceiling 1's rule
   put `unexercised-edge` second and `ambiguous-oracle` fifth; this study's rule puts the oracle
   question second. The same 57 instances go 46/57 one way and 44/57 the other. A classification
   that flips with the order of its questions is not a fact about the auditor; the paper's claim
   (2) — "the ceiling is set by unexercised edges" — cannot be quoted in that form. What survives
   both orderings is narrower: the residual consists of hidden failures the specification's prose
   does not let a reader anticipate, either because the prose does not determine the value (this
   study's reading) or because no visible test pointed at the input (ceiling 1's).
2. **Raters and blinding.** L1 is the author of both rules and of the paper; L2 is a model of the
   same vendor family as one auditor under study. Both were blind to ids, prior categories and
   flag status *within* a sheet; L1 was not blind to *which* sheet was which (the residual sheet
   was built and read first, the flagged sheet second, under Amendment 1), L2 was. The 11
   instances both sheets carry were rated twice by both raters with identical labels (Table 2's
   retest line), which bounds but does not remove the concern. Agreement 60 of 68 with κ 0.722 on
   the residual sheet and 51 of 53 with κ 0.933 on the flagged sheet. The preregistration asked
   for a human rater who is not the author; none was available. This is the study's largest
   limitation and it is not one more labelling pass can remove.
3. **Duplicates.** Each sheet carries two candidates per problem for most problems (the two
   generators), with the same specification and often the same witness; the raters effectively
   read 40 and 33 problems. The problem-cluster interval is the one to quote.
4. **What "ambiguous-oracle" means here.** The rule's test is whether one sentence from the
   specification's own words entails the expected value and excludes the candidate's. It is
   deliberately generous to the candidate: an oracle that is stricter than the prose, silent on
   the input class, or contradicted by the prose all land here. A reader who thinks the dataset's
   reference implementation is the specification will call most of these unexercised edges, as
   ceiling 1 did.
5. **Nothing here re-runs an auditor.** Ceiling 1's union recalls, asymptotes and the arm
   differences are untouched; this study changes what the residual is called, not its size.

## Cost

No API spend. L2: two Codex CLI calls; L1: two readings, 68 and 53 items.
