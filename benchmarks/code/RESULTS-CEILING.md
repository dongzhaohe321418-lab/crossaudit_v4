# The ceiling of AI audit — no improvement from self-audit was established; naming the gap moved flags the most

> **Fifteenth version.** Fourteen independent cross-vendor reviews have read this study. Rounds 1
> and 2 refused quotation approval; **rounds 3 and 4 approved it subject to corrections**,
> all of which were reporting corrections — no analysis has changed since round 2 except
> that round 5 made two code paths bootstrap one estimand under one seed, and no
> point estimate has changed since the first version. Round 5's corrections included one
> substantive discovery: the report was quoting **two different bootstrap intervals for the
> same number**, because two code paths bootstrapped the same estimand under different
> seeds. That is fixed at the source. Round 1 found that the headline's "95% exact" interval had
> 0.416 coverage. Round 2 found that **its replacement was also wrong** — both check
> intervals bounded the nuisance parameter by `(1 − |δ|)/2` instead of `(1 − δ)/2`, which
> is correct only for a non-negative difference and gave 0.075 coverage in the other
> direction — and that the coverage claims made for the replacements were overstated in
> the other direction. Both were right. **No point estimate has changed across any
> version.** Every finding from both rounds is reproduced and answered below, and the
> superseded methods, their measured coverage, and tests that pin them are kept in the
> record.

**The owner's question was: as AI-generated data grows, can AI audit itself to raise
accuracy, and where is the limit? On this evidence, no improvement was established — and
the study was not powered to rule out a small one.**

A generator's own model, auditing its own code and then revising it, changed the fraction
of solutions passing a hidden test suite by **+0.89 percentage points (95% problem-cluster
bootstrap CI [−3.54, +5.88]; Tango [−3.98, +6.06]; exact unconditional [−6.70, +8.48];
exact McNemar p = 1.0000; cluster sign-flip p = 1.0000; n = 112 instances from 96
problems)**. It repaired 3 of 56 wrong solutions and broke 2 of 56 correct ones. **The
preregistered kill condition fires under every one of those intervals**: all four contain
zero.

> **The sentence to carry away.** Self-audit changed accuracy by +0.89 percentage points
> (problem-cluster percentile interval −3.54 to +5.88; 112 instances from 96 problems),
> establishing no improvement; the interval method was changed after analysis, its coverage
> in this clustered design is unvalidated, and modest benefits remain compatible with the
> data.

**What that does and does not mean.** The intervals contain zero on *both* sides, so this
is an inconclusive result, not a demonstration of no effect. At n = 112, with the
worsening rate held at the observed 2/112, the two-sided exact McNemar test had power
**0.32 against a true +5-point improvement, 0.60 against +7.5, and 0.81 against +10**. So
the study could have detected a large effect and did not; it had **limited power to detect
small effects** — 0.32 at +5 points is limited, not zero. **"Self-audit does not raise
accuracy" is not what these data support. "No improvement was established, and an
improvement below about 7 points would probably have been missed" is.**

*The power model, stated because a power figure without its model is meaningless:* 112
**independent** multinomial pairs, worsening probability fixed at 2/112 and improvement
probability 2/112 + δ, so total discordance varies with δ rather than being held at the
observed 5/112. **It is an instance-independent McNemar calculation and is not a power
calculation for the clustered procedure this study actually reports.**

Four further results, in the order they matter.

**1. Reading the same code more times saturates, and not high.** Unioning eight independent
readings by the shipped cross-vendor auditor lifts recall on the defect population from
**10.7% [5.1, 17.4]** to **30.0% (33 of 110) [20.0, 40.7]**, while false positives on
correct code go from **4.5% [2.4, 7.0]** to **16.0% [10.1, 22.3]**. The shipped cross-vendor auditor's fitted
asymptote is 31.5% [21.7, 45.6], **but that curve has not flattened** — the shipped
auditor still gained 1.93 points [1.14, 2.78] from K = 7 to K = 8, failing the
preregistered flattening bar — **so the shipped cross-vendor asymptote of
31.5% [21.7, 45.6] is an extrapolation and its eight-reading 30.0% [20.0, 40.7] is the
number to quote.** The generator's own model does flatten, and far lower:
**15.5% [7.1, 24.9]** at one reading, **17.3% (19 of 110) [8.3, 27.3]** at eight, asymptote
**16.6% [8.1, 26.3]**, at a false-positive rate of **24.0% [17.2, 31.2]**.

**The preregistered primary outcome, A(self) − A(cross) on stratum P, is −14.9 points, 95%
problem-cluster bootstrap CI [−32.1, −2.3]**; the model-free version, the raw difference of
union recalls at eight readings, is **−12.7 points [−25.0, −0.9]**. Both are negative and
both exclude zero. Over the readings actually taken, **the author's own model found less of
its own bad code than a stranger did, and flagged more good code doing it.** Because
`cross`'s curve is still rising, the asymptote comparison is a comparison of one fitted
extrapolation against one flattened fit, and the raw eight-reading difference is the
sturdier of the two.

**2. Repetition is not the lever; the model is one, and the instructions are a bigger one.**
The `self` route is near-deterministic — its eight draws disagree on 0 to 3 of 260
instances, and the closed-loop replicate returned **identical final solutions, flags and
outcomes on all 112 instances**. Eight readings find **two** more defects than the best
single reading (17 → 19). Meanwhile **one reading by the strongest model available
(`gpt-6-astra`, high reasoning) recalls 30.2% [19.3, 42.0] at 9.7% [5.3, 14.5] false
positives, matching eight unioned readings of the shipped auditor on recall at less than
two-thirds of the false-positive cost** (30.0% [20.0, 40.7] at 16.0% [10.1, 22.3]).

The largest effect measured anywhere in this study came from changing what the auditor was
told to look for. One added constitution rule — *find what the visible tests do not
cover* — moved the referent arm's flags on the defect population from 10 of 56 to 25 of
56: **+26.8 points, cluster CI [13.6, 40.4], exact unconditional [+6.3, +43.7], McNemar
p = 0.0003, cluster sign-flip p = 0.0009**. **Two contrasts in this study clear the Bonferroni threshold over the sixteen
comparisons actually computed, and both are this same effect seen two ways**: referent
against cross on stratum-P flags (+26.8 points [13.6, 40.4], p = 2.7 × 10⁻⁴,
cluster p = 8.5 × 10⁻⁴) and
on the pooled P + C flags (+19.6 points [11.7, 27.8], p = 3.0 × 10⁻⁶, cluster
p = 1.0 × 10⁻⁵). **Both are exploratory**: the preregistration named outcome contrasts, not
flag contrasts.

**On accuracy rather than flags, the referent's advantage is not established.** Against its
own baseline the referent arm nets **+8.04 pp, cluster CI [1.77, 15.26], Tango [2.03,
15.27], p = 0.0225, cluster p = 0.0469** — but the exact unconditional interval, the most
conservative of the three, is **[−1.79, +17.41] and contains zero**. And the contrast that
actually isolates the referent, **referent-loop minus cross-loop, is +5.36 pp, cluster CI
[−0.89, +12.07], p = 0.1460** — it does not exclude zero. **The referent demonstrably moves
what the auditor flags; whether that converts into accuracy is not established here.** The
title says "did the most", not "works".

**3. Half the defects were flagged by no reading of any family.** **57 of 110 defective
solutions (51.8%, cluster CI [40.0, 63.3]) were flagged by no reading of any family** — 20
readings, three models, two vendors, one frontier route. Classified by hand under a rule
fixed before the first was opened, **46 of those 57 residual instances (80.7%, problem-cluster CI [66.1, 93.1],
seed 20260919) fail only on an input class the visible test suite never constructs**: the empty list, the negative number,
the two-digit case, the ragged input, the punctuation character. **That is the shape of what
was missed.** A model shown a specification and a test suite has no evidence in front of it
that those classes never appear in what the readers were shown. **This is a statement about the
evidence in front of a reader, not about what a model can or cannot infer**: nothing here
measures whether a model could deduce the missing classes from the specification alone.
What is measured is that these detectors did not flag them over 20 readings, and that the
one intervention that named the gap moved flags more than anything else tried.

**4. The population is hidden-suite non-passes, not confirmed assertion failures.** Seven of
the 110 stratum-P instances fail because the hidden suite **did not terminate**. The
registered analysis keeps the registered population; Table 9 narrows it to the 103
instances with an observed assertion failure, and nothing moves: unions 32 / 18 / 34 against
33 / 19 / 36, and the residual is 54 of 103 (52.4% [40.4, 64.4]) against 57 of 110
(51.8% [40.0, 63.3]).

**Total spend: $13.23 of a $20 budget, plus 4,427,530 tokens on a subscription-billed route
that reports no dollar cost.**

---

## What the review changed

An independent reviewer on a different vendor's model read the committed record at
`f7f515e`, reproduced the numbers, and returned nine findings. All nine reproduced here
before anything was altered. This section is the audit trail; the sections after it are the
corrected report.

| # | Finding | Reproduced | What changed |
|---|---|---|---|
| 1 | The paired interval rescaled a **conditional** Clopper–Pearson by the **observed** discordance fraction, discarding the uncertainty in that fraction. Coverage **0.416**, not 0.95 | coverage = **0.4162688657**, matching the reviewer to 10 digits | Interval replaced. Primary is now the problem-cluster bootstrap; checks are Tango's unconditional score interval and a Berger–Boos-restricted exact unconditional interval. Measured coverages at that round: **0.416 (withdrawn) → 0.960 (Tango) → 0.998 (exact, at n = 40)**; the n = 112 figures the suite pins are 0.416, 0.960 and 0.997 (deviation 34, round 2) |
| 2 | Binary inference ignored problem clusters that the saturation bootstrap already respected | 112 loop instances from **96** problems; 110 P instances from **56** | Every primary interval is now a problem-cluster bootstrap; a cluster sign-flip permutation p sits beside every McNemar p. Reproduced the reviewer's sensitivities exactly: referent-loop 0.0225 → **0.0469**, referent-minus-cross flags 0.0003 → **0.0009** |
| 3 | "In the limit of unlimited readings" where the curve had not flattened; "cannot be seen"; the title's causal claim | cross gains **1.93 pp** from K=7 to K=8 | Extrapolation caveat now carried in the headline, Table 1 (`flat?` column) and the conclusion. "Was not flagged by any reading", never "cannot be seen". Title and headline now lead with the between-arm contrast (+5.36 pp, p = 0.146) |
| 4 | Twelve planned, **16** computed; the highlighted contrast was not among the twelve; "exactly one clears" was false | 16 `p_exact` entries enumerated | Full planned/performed/exploratory inventory in `numbers.json`; one correction family of 16; threshold 0.00313; every flag contrast labelled EXPLORATORY. Five planned mixed/astra asymptote contrasts were **not delivered** — recorded as deviation 15 |
| 5 | Timeouts inside a population described as assertion-confirmed | **7** P timeouts, 3 in the loop sample, 3 in the residual | Population renamed "hidden-suite non-passes, including timeouts"; Table 9 adds the assertion-only sensitivity (103 / 32 / 18 / 34 / residual 54), reproducing the reviewer |
| 6 | Provenance gaps; "no number had left the harness" overstated | `1a66571:tables.md` carries the swapped interval, committed 18:46:39, fixed 18:48:18 | Manifests now carry package versions, per-invocation UTC windows, base URLs, corrected sampling metadata (**the self route sends temperature 0**), the dirty-tree record and re-hashed files. The beta-bug sentence is corrected below |
| 7 | `returned_non_solution` said zero; it is 4/4/2/0. "Bias: none" unsupported | reproduced exactly | Deviations 2, 3 and 5 corrected; bias directions now stated as undetermined where they are |
| 8 | `Mbpp/305` description; "one more defect"; "byte-identical output" | self union adds **two** (17→19); `report_sha256` differs on `b1:HumanEval/35` | Classification description corrected (category unchanged); "adds two"; "identical final solutions, flags and outcomes" |
| 9 | The fitter left its registered bound `A ∈ [0,1]` | `fit_saturation(union_curve([1]*110, 8))` returned **250.4** | Constrained inside the objective, so both bootstrap paths treat the boundary identically. **No quoted estimate moved** |

**What did not change: any point estimate.** The asymptotes, the union curves, the primary
difference, the arm nets, the residual counts and the classification are identical to the
first version. What changed is what may be claimed around them.

### What the tenth review changed

Round 10 confirmed the numbers byte-identical, 43 tests, `src/` empty, deviations 1–36, and
the documented-boundary test behaving as specified. It then enumerated, by line, every
remaining sentence claiming more than its check delivers. All were reproduced.

| # | Finding | Reproduced | What changed |
|---|---|---|---|
| 1 | Eleven overclaiming sentences across the report and both test files: "a too-generic subject cannot hide" (a vocabulary of only `asymptote` leaves all 22 green), "every rate", "all real and correct", "any other family", "makes a fourth instance impossible", "wherever the guard is described", "coverage labels cannot drift" (editing a published 0.997 to 0.960 left all green), "15 statistics tests", and an *under*claim — the guard does apply a membership check outside the two sections | all reproduced | Each sentence rewritten to what its check does: the scanner's four numeral formats named; membership distinguished from attribution; the six no-interval declarations qualified; "the generated token-replacement mutations redden" replacing "any other family"; the impossibility claim deleted; the test count corrected to 21 and the simulated methods listed |
| 1b | The coverage labels had nothing checking them | editing 0.997 → 0.960 left all tests green | **Bound, not disclaimed.** `ceiling/measure_coverage.py` measures all eleven figures by exact enumeration into `records/ceiling/coverage.json`; the statistics suite asserts its own measurements equal the artefact, and a new report test asserts both coverage tables equal it. The chain is measurement → artefact → table cells, and the review's drift attack now reddens; an unbracketed, unsigned figure of the literal form `0.ddd` in a sentence containing the letters `cover` is checked for membership among the measured values, not attributed to a method; a coverage described in other words, bracketed, signed, or written as `1.000` is not read |
| 2 | Deviation 34's correction history had four rows; eleven more corrections were omitted, and deviation 31 still carried "no published number was ever wrong" | verified against the review reports | The history is rebuilt **from the review reports**, fifteen rows cited by round, with the committed-artefact swapped-tail interval distinguished from published prose. Deviation 31's copy is withdrawn. Everywhere "no estimate has changed" appeared it now reads "**no empirical point estimate has changed; interval estimates did**" |
| 3 | Nothing stopped the overclaiming vocabulary returning | — | A test fails on seven guarantee words in the report and both test files, each with the round that found it asserted falsely, unless the whole sentence is one of an exact list of allowed sentences, after asterisks, emphasis underscores, backticks and footnote markers are removed — other formatting is not normalised. Writing it found further unqualified uses beyond the review's list; they were rewritten in the same commit and not individually recorded |

### What the ninth review changed

Round 9 confirmed the numbers byte-identical, 42 tests, the 312 mutations non-vacuous (39
rules × 8 subjects, 168 distinct mutated reports, none surviving), both protective
assertions firing, and deviations 1–35. Its finding was not a defect in the guard but in
**what the guard was claimed to do**: the claim exceeded what a lexical check can enforce.
Its instruction — *narrow the claim; do not widen the guard* — is the right one, and this
round follows it.

| # | Finding | Reproduced | What changed |
|---|---|---|---|
| 1 | The guard's stated scope overreached. Four attacks survive it: a two-family sentence that moves ownership by grammar while every token is present; an interval claimed with no numeral beside it (membership-checked only); a rate written in words; and, outside the opening and conclusion, anything but the membership of a recognised interval | all four reproduced green | The scope is now stated exactly, in the module docstring and in the report: **a lexical editing guard for registered numeral templates in the opening and conclusion: every registered rate must carry its bound interval adjacent, and its sentence must name its family. It does not parse grammatical ownership, does not read rates written in words, and applies membership checks only outside those two sections.** The four attacks are committed **green** in `test_documented_uncovered_cases_are_green_and_that_is_the_boundary`, with a docstring explaining each, plus a fifth case asserting what the guard *does* catch. The declaration test now says it checks vocabulary membership, not semantic specificity |
| 2 | Deviation 34's "no published number was ever wrong" is **false as a history** | verified against rounds 2, 3 and 6 | Struck and replaced with a table of the four published numbers that were wrong and corrected. What survives is the narrow true claim: the round 6–8 re-attribution attacks were synthetic and never appeared in a published version, and no empirical point estimate has changed since version one; interval estimates did |
| 3 | "Seven sentences" was miscounted | verified | **Seven failing rule matches across four sentences** |

### What the eighth review changed

Round 8 confirmed hashes equal to round 7, derived seed status, zero duplicates, 37 tests
and byte-identical regeneration — and made the point that mattered: **three consecutive
rounds had found the same class of defect in the same guard, because each round I fixed the
instance.** Three more re-attributions were green: renaming the self-loop arm to cross-loop
(loop nets carried no subject requirement at all), attributing the shipped auditor's
asymptote to the self model (asymptote rules accepted generic words), and the same rename in
the conclusion. All three reproduced.

The fix is structural, not another instance.

| # | Finding | Reproduced | What changed |
|---|---|---|---|
| 1 | Family binding was example-driven: 11 of 23 bound arrays had **no** subject requirement, and several others accepted generic words | all three edits green | **Every** bound array now declares a family/arm subject, enforced by `test_every_bound_rule_declares_a_subject`, which fails on an absent declaration or a family outside `FAMILY_VOCAB` — not on a weak one. A **generated** test rewrites each rule's sentence subject to every other family in turn — **312 mutations** — and requires each to redden; it also asserts the unmutated report is clean and that no rule is unmutatable. **Neither test detects a weak declaration**: the
declaration test checks vocabulary *membership*, and the generated test mutates the tokens
a rule *declares*, so a family whose vocabulary contained only a weak word such as
`asymptote` would satisfy both. **Seven failing rule matches across four sentences** could not name their own subject; those four sentences were rewritten, and the test identified every match. The three counterexamples are committed as named tests as well |
| 2 | The AST duplicate check existed only at review time | duplicating `_pairs` left the suite green | Committed as `test_the_analysis_files_contain_no_duplicate_definitions`, covering eight analysis files; verified to redden on a duplicated `_pairs` |
| 3 | The attribution table lists ten rows; the sentence said nine and "the single exception" | verified | Sentence rewritten to "eight of the nine numbered corrections, plus the author-found beta-tail defect fixed before round 1", and **a test derives those counts from the table** so they cannot drift |

### What the seventh review changed

Round 7 confirmed both artefacts byte-identical to round 6, all prior mutations red, the
34/205 seed count and `+7`, deviations 1–30, 36 tests and byte-identical regeneration, and
approved subject to three narrow corrections. All three reproduced first.

| # | Finding | Reproduced | What changed |
|---|---|---|---|
| 1 | **The binding ignored the sentence's subject.** Splitting one conclusion sentence in two and giving the second a different subject re-attributed astra's one-reading false-positive rate to the shipped auditor's eight readings, with all 15 tests green — the anchor still matched, and matched only once, so uniqueness was silent too | reproduced | Each bound rate must now find, **in its own sentence**, tokens naming the family the array belongs to. The reviewer's edit is committed as a test. The uniqueness rule's known cost — a correctly repeated sentence fails it — is documented in its docstring and accepted rather than loosened |
| 2 | The manifest still said `+1 = 20260909` "does not appear in observed_seeds"; it does | reproduced | **The observation claim is no longer prose.** A `status_derived_from_instrument` block marks every named seed consumed or not, computed from the instrument; only the *reason* a seed is unconsumed is written by a person, and only for seeds the instrument reports absent. This was the second hand-written seed explanation to contradict the instrument, so the class of error is removed rather than the instance |
| 3 | "Six of the nine" should be **eight**; "every defect in this study's statistical machinery" overstates — the beta-tail defect was the author's own find, fixed before round 1; and the test file held **11 duplicated function definitions**, four of them tests | all reproduced | Count corrected, claim narrowed with the beta tail credited to the author in the attribution table, and all 11 duplicates removed — the same silent-override hazard already found in the rule block |

### What the sixth review changed

Round 6 reproduced everything — the four changed arrays equalling their canonical
counterparts, 302 byte-identical, 533 scalars unchanged, five mutations red, 32 seeds over
196 bootstrap calls with the three corrected ranges, 33 tests, byte-identical regeneration
— and approved subject to three corrections. All three reproduced first.

| # | Finding | Reproduced | What changed |
|---|---|---|---|
| 1 | **The reader sentence's interval was never bound.** A declaration claimed the headline mechanism checked it; that mechanism checks a different sentence. Replacing `−3.54 to +5.88` with `+1.00 to +2.00`, or deleting it, left all 12 tests green. And a **reused label** bound a rate to the wrong family: an inserted sentence attributing astra's 9.7% [5.3, 14.5] to the shipped auditor's eight readings (16.0% [10.1, 22.3]) also passed | all three reproduced | The reader sentence is bound to `ceiling2.arms.self-loop.net_primary.ci95`, with its prose "to"-form parsed. Every reused label now carries its discriminating family and reading count. A further test fails if **any binding rule matches more than once** — which is how new prose slips under an existing anchor — and that test immediately found a legitimate duplicate to split. All three counterexamples are committed |
| 2 | **Seed 20260915 is consumed**, not unused: the pooled self−cross flag contrast has 25 non-zero clusters and uses the sampled sign-flip path. The manifest's claim was contradicted by `numbers.json` in plain text | verified | The inventory now instruments **`random.Random` itself**, not one call site, so every generator is counted whatever builds it: **34 seeds over 205 constructions**, against 32 over 196 from the narrower instrument. `+7` is recorded as consumed with its sample size and p |
| 3 | **`CORRECTIONS.md` #25 misattributed discoveries**, crediting tests for what round 4 had explicitly reported | verified against round 4's report | #25 is replaced with a per-item table naming who found each defect. **Eight of the nine numbered corrections** were cross-vendor findings; the ninth was the author's, and only because a reviewer had demanded the mechanism that exposed it. The beta-tail defect, fixed before round 1, was the author's own unprompted find and is listed separately |

While fixing item 1, a defect in the test file itself came to light: **the binding rules had been duplicated**, with the second copy silently overriding the first. Both copies were identical, so no check was wrong — but the file was 142 lines of dead code that could have diverged. Deduplicated.

### What the fifth review changed

Round 5 reproduced everything again — 29 tests, the pre-fix estimator table agreeing across
all three documents, 300 arrays byte-identical, 533 scalars unchanged, 24 events, byte-
identical regeneration — and approved subject to four corrections. All four reproduced
first.

| # | Finding | Reproduced | What changed |
|---|---|---|---|
| 1 | The guard still exempted bare estimates by broad context, and **accepted another quantity's interval**: `(30.0% at 16.0% [10.1, 22.3], with the recall interval [20.0, 40.7])` stayed green because the FP interval sat ten characters from the recall rate | both reproduced | **Every rate the scanner recognises in the opening and conclusion — a numeral followed by `%`, `pp`, `points` or `percentage points` — is now bound to the specific `numbers.json` array its interval must come from** — 36 binding rules, no context exemption; a rate is either bound or explicitly declared, with a reason, as owing no interval. The counterexample, a stripped interval, a value/interval mismatch and **two intervals swapped between rates in one sentence** are all committed as regression tests, and a further test fails if any binding rule stops matching. Fixing this exposed a real defect: **the report quoted [40.4, 63.6] and [40.0, 63.3] for the same residual share**, because `timeout_sensitivity` re-bootstrapped an estimand the residual analysis had already bootstrapped, under a different seed. Both now use the canonical seed and are identical |
| 2 | `superseded_fields_removed` still said `working_tree_at_freeze` was removed, contradicting the record that it was retained | verified in both manifests | The stale block is dropped on every finalisation, so a superseded record cannot outlive its own correction |
| 3 | Seed offsets complete but three **ranges wrong**: curve K given as 8–16 when it is 1–8; mixed and comparator ranges likewise | verified | The inventory is now **generated from the code**: every call to the bootstrap is wrapped during a cheap pass and its seed logged, and the manifest records the observed set (32 seeds over 196 calls). The hand-written entries were corrected to match, and the five named-but-unobserved seeds are each reconciled — two of which turned out to be **retired** by the fix in item 1 |
| 4 | Deviation 18 paired Tango's beneficial coverage with the exact grid's detrimental one in a single unlabelled sentence | verified | Both methods and both scenarios labelled, as the coverage table does |

### What the fourth review changed

Round 4 reproduced everything again — all 25 tests, all four mutations red, all 233
pre-existing arrays byte-identical, all 67 new arrays regenerating (comparator bootstraps
agreeing to 2.8 × 10⁻¹⁷), all 533 version-1 scalars unchanged, the coverage table to twelve
digits, byte-identical regeneration — and approved subject to four written corrections. All
four reproduced here first.

| # | Finding | Reproduced | What changed |
|---|---|---|---|
| 1 | **A coverage label was newly wrong**: the report, Amendment 5 and CORRECTIONS #17 attributed beneficial coverage **0.960 to the pre-fix exact grid**. It is Tango's; the pre-fix exact grid covered **0.997** | re-executing the pre-fix code gives Tango 0.960 / 0.953 and exact grid 0.997 / 0.075 | Fixed in all three places, as a table rather than a sentence. The pre-fix estimators are now **committed as runnable code with their coverages pinned as tests**, so their coverages are re-measured on every run rather than quoted; the eleventh review showed a label could still sit beside the wrong column, and deviation 38 now checks the column order and the `Bin(n, q)` pairs of each header, and the membership of three-decimal figures in coverage sentences. The re-execution also showed something worth saying: **pre-fix Tango covered 0.953 detrimental while still returning wrong intervals** — coverage in the scenarios you happen to test does not certify a method, which is why sign symmetry is what pins this |
| 2 | The withdrawn blanket "2 to 5 points optimistic" **survived in deviation 19**, as that deviation's own conclusion | verified | Struck through in place and marked superseded by deviation 21, rather than deleted — the deviation record should show what it said |
| 3 | Interval completeness still incomplete: opening repetitions, conclusion rates, Table 1's last-step gains | verified | Intervals added everywhere named, and **the rule is now mechanical**: a test requires every rate the scanner recognises in the opening and conclusion to be followed *adjacently* by an interval, or to be explicitly declared, with a reason, as owing no interval. Writing it found two more gaps the review had not listed, including a bare `+26.8 points`. Its own test-of-the-test caught that a first version accepted any later interval in the sentence |
| 4 | Provenance: `working_tree_at_freeze` still present while the record said removed; 24 events described as individually enumerated when ten run-ID groups were listed; seed inventory missing `+50+total`, `+14`, `+15` | verified | The record now distinguishes **removed** (`finalised_at_commit`) from **retained and rewritten** (`working_tree_at_freeze`, kept because it is true); the event block says plainly that it lists **10 run_ids covering 24 events** with their composition; the seed inventory is complete and **cross-checked against every `BOOT_SEED` offset in the code** |

### What the third review changed

Round 3 reproduced everything — five sign-symmetry triples to 5.6 × 10⁻¹⁷, all 143
pre-existing interval arrays, 90 added cluster intervals, the power curve, the two
survivors, the provenance freeze, byte-identical regeneration — and approved quotation
subject to six reporting corrections. All six reproduced here first.

| # | Finding | Reproduced | What changed |
|---|---|---|---|
| 1 | Detrimental bootstrap coverage stated as 0.924; it is **0.953** (0.924 is the sign-reversed beneficial scenario). The blanket "every interval is 2–5 points optimistic" is unsupported. The exact grid's 0.984 depends on inward endpoint rounding | bootstrap 0.923731894539 / 0.953264931806; at (0,44,112) bisection returns **−0.499999993614**, excluding −0.5 | Coverage table rewritten **by method × scenario**; the blanket claim withdrawn and replaced with "coverage under the actual clustered design is **unvalidated**"; the endpoint effect stated with its 0.9895 alternative; the 0.960/0.075 comparison now names its method and both scenarios. A detrimental-direction case added to the bootstrap coverage test |
| 2 | Opening still gave 46/57 as Wilson; Table 9 labelled cluster intervals "Wilson"; Tables 3, 4, 9, opening and conclusion rates lacked intervals; 3/57 shown as 5.3% | seed 20260919 gives [66.1, 93.1]; seed 20260908 gives [66.7, 93.1] | Opening uses the clustered interval **with its seed named**; Table 9 relabelled with Wilson printed beside; intervals added to Table 3's component asymptotes, Table 4's comparators, Table 9's registered rates, and the opening and conclusion; categories under 6 quoted **as counts** |
| 3 | "Could not have detected a small one either way" overstates; the power model was not fully specified | power 0.32 at +5 pp is limited, not zero | Reworded to **"limited power to detect small effects"**; the model is now stated in full — 112 **independent** multinomial pairs, worsening fixed at 2/112, improvement 2/112 + δ — with an explicit note that **it is not a power calculation for the clustered procedure** |
| 4 | Both manifests still carried `finalised_at_commit: f7f515e…` beside the corrective block; 24 unmatched stamps counted by prefix only | verified | Superseded fields **removed**, with a `superseded_fields_removed` record saying why; the dangling "records above" reference repointed at `analysis_freeze`; all 24 unmatched events **enumerated individually** (2 probes, 16 pilot audits, 6 pilot revisions) |
| 5 | **The consistency guard did not bite**: mutating an interval by 0.01 left it green, and `[−99.99, +99.99]` in the headline passed | all four of the reviewer's mutations reproduced as false passes | Guard rewritten: parses `−`/`-`/`+`, compares **at displayed precision with zero tolerance**, and **binds the headline and primary spans to their estimands**. The five mutations now all go red, and **the mutation is committed as a test of the test**. Rewriting it immediately caught two live errors: a prose interval of `[+6.3, +43.8]` where the record says **+43.7**, and a flag contrast whose exact interval was quoted but never stored |
| 6 | `.gitignore` also changed; the threshold appears once live and once historically | verified | Both stated |

### What the second review changed

| # | Finding | Reproduced | What changed |
|---|---|---|---|
| 1 | **Both replacement check intervals used the wrong nuisance upper bound** — `(1 − \|δ\|)/2` instead of `(1 − δ)/2` — and the coverage assurances were overstated | `tango(20,70,112)` returned [−0.539, −0.358] not [−0.577, −0.291]; `exact(0,40,40)` returned [−1, −1] not [−1, −0.8]; detrimental-direction coverage **0.0752249063**, matching the reviewer to ten digits | Bound corrected in both estimators. Detrimental coverage now 0.953 (Tango) and 0.984 (exact). A **sign-symmetry test** and a **detrimental-direction coverage enumeration** are now in the suite. The coverage table is rewritten with measured values in both directions, and states that **the primary bootstrap under-covers by ~2–5 points**; "0.95 nominal by simulation" and "never under-covers" are withdrawn |
| 2 | Clustering unfinished: Table 5b, Table 9 and the opening still used Wilson; Table 7b's † lacked its unconditional interval; Table 6's 0/56 needed a degeneracy note | 46/57 clustered is [66.1, 93.1] against Wilson [68.7, 88.9] | The rates in Tables 2, 4, 5b and 9 now carry a problem-cluster interval, with Wilson shown beside it for comparison. Table 7b gains a Tango column. Table 6 gains the 0/56 note |
| 3 | Title and opening asserted "did not raise accuracy"; mechanism sentence unsupported | interval contains zero on both sides | Title and opening now say **no improvement was established**, with a **power curve**: 0.32 against +5 points, 0.60 against +7.5, 0.81 against +10. The mechanism sentence is replaced by a statement about the corpus, with an explicit disclaimer that nothing here measures what a model could infer |
| 4 | "Exactly one contrast clears" still false — **two** do | referent−cross P flags (2.7 × 10⁻⁴) and pooled flags (3.0 × 10⁻⁶) | Both named, both labelled exploratory. The threshold is stated once in the statistical-analysis subsection and removed from every table |
| 5 | Provenance: `finalised_at_commit` named a commit whose analysis-file hash did not match; windows omitted astra, inherited draws and 22 unstamped events; "start" was first completion; seeds absent from manifests | verified | Field renamed to `finalised_on_parent_commit` with an `analysis_freeze` block explaining how to locate the real freeze; coverage gaps enumerated; timestamps renamed `utc_first_completion` / `utc_last_completion`; unmatched ledger events counted; all seeds recorded; astra's endpoint recorded as unavailable; package versions marked retrospective |
| 6 | Tables 2 and 4 lacked intervals; prose quoted a stale `[−0.88, +12.08]` | regeneration gives [−0.89, +12.07] | Intervals added; every stale quotation corrected; **a new test reads every bracketed interval of the form `[number, number]` with decimal endpoints (`[999, 1000]` is not recognised) and requires it to exist in `numbers.json`** — a membership check, not an attribution check, with historical values allowed by an explicit list |

---

## What was run

Preregistered in [`ceiling/PREREGISTRATION.md`](ceiling/PREREGISTRATION.md), committed at
`d96cdaf`, with amendments 1–2 (the `astra` family) and amendment 3 (the reporting standard)
at `87939d2` — **all before the first model call of this study, including the credential
probe.**

| | |
|---|---|
| audit set | study 2's, unchanged: **290 instances**; this study's scope is P + C = **260** |
| stratum P | passes every visible test, **does not pass the hidden suite** — n = 110 from **56 problems**, and **7 of the 110 are timeouts, not observed assertion failures** |
| stratum C | passes every test — the false-positive population — n = 150 |
| ground truth | a Python interpreter raising `AssertionError`, or failing to terminate. **No model judges anything** |
| solutions | study 2's, byte-identical, **not regenerated** |
| generator | `anthropic:claude-haiku-4-5-20251001`, frozen |
| `cross` | `openai:gpt-5.6-terra`, **K = 8 draws** — capability card `temperature: False`, so no sampling parameter is sent and the route varies run to run |
| `self` | `anthropic:claude-haiku-4-5-20251001`, **K = 8** — capability card permits temperature, so the layer sends **temperature = 0**, and the route is near-deterministic |
| `astra` | `gpt-6-astra` at high reasoning, through the Codex CLI, **K = 4** |
| flag | ≥ 1 BLOCKER finding, exactly as studies 1, 2 and 7 |
| audit path | `crossaudit.auditor.run.run_audit` — the product's real audit, unchanged |
| environment | Python 3.13.5, macOS 26.6.2 arm64; package versions in the manifests |

**The `astra` prompt is the shipped auditor's prompt, byte for byte** — built by the
product's own `auditor.prompt.build`, and its `prompt_sha256` checked against study 2's
committed `holistic-cross` digests: **40 of 40 agree**. It bypasses the provider broker, the
metered ledger and the same-vendor guard, so **it is a measurement of a model, not of the
product path**.

**Baseline check.** All 112 solutions in the ceiling-2 sample were re-executed on this
machine before any arm was scored: **112 of 112 reproduce the stratum study 2 recorded**
(`records/ceiling/baseline_reproduction.json`).

---

## Ceiling 1 — how much these readers saw

### Table 1 — the saturation curve, per family

Unit of analysis: the instance. n = 110 stratum-P instances (recall) and 150 stratum-C instances (false positives), the same instances at every K. Union rate at K is averaged over all C(K_max, K) subsets of that family's draws, exactly.

Each rate in Table 1 carries a 95% **problem-cluster bootstrap** interval; the P population is 110 instances from only **56 problems**, so an interval that treats instances as independent is too narrow. `flat?` says whether the curve met the preregistered flattening bar (last-step gain ≤ 1.0 point); where it did not, **A is an extrapolation** and the raw union at K_max is the number to quote.

| family | K_max | union recall on P at K=1 [95% CI] | at K_max [95% CI] | fitted asymptote A [95% CI] | union FP on C at K=1 [95% CI] | at K_max [95% CI] | last-step gain | flat? |
|---|---:|---|---|---|---|---|---:|:---:|
| `cross` | 8 | 10.7% [5.1, 17.4] | **30.0%** (33/110) [20.0, 40.7] | 31.5% [21.7, 45.6] *(extrapolation)* | 4.5% [2.4, 7.0] | **16.0%** [10.1, 22.3] | 1.93% [1.14, 2.78] | **no** |
| `self` | 8 | 15.5% [7.1, 24.9] | **17.3%** (19/110) [8.3, 27.3] | **16.6%** [8.1, 26.3] | 21.9% [15.5, 28.9] | **24.0%** [17.2, 31.2] | 0.23% [0.00, 0.57] | yes |
| `astra` | 4 | 30.2% [19.3, 42.0] | **32.7%** (36/110) [20.7, 45.0] | **32.5%** [20.5, 44.8] | 9.7% [5.3, 14.5] | **10.7%** [5.9, 16.1] | 0.23% [0.00, 0.69] | yes |
### Table 2 — union recall and union false positives at every K

Unit of analysis: the instance; the same instances at every K, so the columns are repeated measures and not independent samples.


**`cross`** (K_max = 8, n = 110 P instances, 150 C instances)

| K | union recall on P [95% cluster CI] | union FP on C [95% cluster CI] | recall per FP point |
|---:|---|---|---:|
| 1 | 10.7% [5.2, 17.2] | 4.5% [2.4, 7.1] | — |
| 2 | 15.0% [8.3, 22.6] | 7.1% [4.2, 10.3] | 1.67 |
| 3 | 18.3% [11.0, 26.6] | 9.2% [5.7, 13.2] | 1.63 |
| 4 | 21.2% [13.0, 30.0] | 10.9% [6.9, 15.5] | 1.64 |
| 5 | 23.8% [15.1, 33.2] | 12.4% [7.8, 17.6] | 1.65 |
| 6 | 26.0% [17.0, 35.7] | 13.7% [8.7, 19.3] | 1.66 |
| 7 | 28.1% [18.3, 38.4] | 14.9% [9.5, 20.7] | 1.67 |
| 8 | 30.0% [19.8, 40.7] | 16.0% [10.1, 22.1] | 1.68 |

**`self`** (K_max = 8, n = 110 P instances, 150 C instances)

| K | union recall on P [95% cluster CI] | union FP on C [95% cluster CI] | recall per FP point |
|---:|---|---|---:|
| 1 | 15.5% [7.2, 25.1] | 21.9% [15.4, 28.9] | — |
| 2 | 15.9% [7.4, 25.8] | 22.6% [15.9, 29.7] | 0.62 |
| 3 | 16.1% [7.5, 25.7] | 22.9% [16.3, 29.8] | 0.67 |
| 4 | 16.4% [7.6, 26.1] | 23.2% [16.5, 30.2] | 0.71 |
| 5 | 16.6% [7.8, 26.2] | 23.4% [16.6, 30.5] | 0.75 |
| 6 | 16.8% [8.0, 26.6] | 23.6% [16.9, 30.9] | 0.79 |
| 7 | 17.0% [8.1, 27.3] | 23.8% [17.1, 31.0] | 0.83 |
| 8 | 17.3% [8.3, 27.4] | 24.0% [17.3, 31.3] | 0.87 |

**`astra`** (K_max = 4, n = 110 P instances, 150 C instances)

| K | union recall on P [95% cluster CI] | union FP on C [95% cluster CI] | recall per FP point |
|---:|---|---|---:|
| 1 | 30.2% [19.1, 42.0] | 9.7% [5.3, 14.6] | — |
| 2 | 32.0% [20.2, 44.2] | 10.2% [5.4, 15.4] | 3.14 |
| 3 | 32.5% [21.1, 45.0] | 10.5% [5.8, 16.0] | 2.73 |
| 4 | 32.7% [20.7, 45.0] | 10.7% [5.9, 16.2] | 2.50 |
### Table 3 — primary outcome, ceiling 1: A(self) − A(cross)

K_common = 8 draws per family. Positive means the generator's own model can ultimately see more of its own defects than a stranger can. Interval: 95% percentile bootstrap over problem clusters, both curves resampled together.

| stratum | n instances | A(cross) [95% CI] | A(self) [95% CI] | A(self) − A(cross) [95% CI] | raw union difference at K_common [95% CI] |
|---|---:|---|---|---|---|
| P | 110 | 31.5% [21.7, 45.6] | 16.6% [8.1, 26.3] | **-14.9%** [-32.1, -2.3] | -12.7% [-25.0, -0.9] |
| C | 150 | 18.6% [11.6, 29.1] | 23.4% [16.8, 30.6] | **4.8%** [-7.6, 14.3] | 8.0% [-0.7, 16.8] |
### Table 4 — mixed families at matched total draws

Unit of analysis: the instance. Each row spends the same total number of readings; the question is whether spreading them across families beats spending them all inside one.

| combination | total draws | per family | union recall on P [95% cluster CI] | union FP on C [95% cluster CI] | same total inside one family (recall) |
|---|---:|---:|---|---|---|
| `cross+self` | 2 | 1 | 21.3% [12.5, 31.1] | 24.6% [18.2, 31.5] | `cross` 15.0% [8.5, 22.6]; `self` 15.9% [7.4, 25.7] |
| `cross+self` | 4 | 2 | 25.1% [15.7, 35.4] | 26.9% [20.0, 34.0] | `cross` 21.2% [13.0, 30.0]; `self` 16.4% [7.7, 26.3] |
| `cross+self` | 6 | 3 | 28.2% [18.4, 38.4] | 28.5% [21.6, 35.8] | `cross` 26.0% [16.8, 35.9]; `self` 16.8% [8.0, 27.0] |
| `cross+self` | 8 | 4 | 30.7% [20.8, 41.3] | 29.9% [23.1, 37.3] | `cross` 30.0% [20.0, 40.5]; `self` 17.3% [8.2, 27.5] |
| `cross+self` | 10 | 5 | 32.9% [22.5, 43.8] | 31.1% [23.9, 38.5] | — |
| `cross+self` | 12 | 6 | 34.8% [24.3, 45.9] | 32.2% [24.9, 39.8] | — |
| `cross+self` | 14 | 7 | 36.6% [25.8, 47.9] | 33.2% [25.7, 41.1] | — |
| `cross+self` | 16 | 8 | 38.2% [27.3, 49.5] | 34.0% [26.3, 42.0] | — |
| `cross+self+astra` | 3 | 1 | 37.5% [25.9, 49.8] | 29.7% [22.6, 37.2] | `cross` 18.3% [10.9, 26.4]; `self` 16.1% [7.7, 25.8]; `astra` 32.5% [20.7, 44.8] |
| `cross+self+astra` | 6 | 2 | 40.6% [28.5, 53.0] | 31.3% [23.9, 38.9] | `cross` 26.0% [16.8, 35.9]; `self` 16.8% [8.0, 27.0] |
| `cross+self+astra` | 9 | 3 | 42.3% [30.4, 54.5] | 32.4% [25.0, 40.3] | — |
| `cross+self+astra` | 12 | 4 | 43.6% [31.7, 55.6] | 33.4% [26.1, 41.2] | — |
| `cross+astra` | 2 | 1 | 31.3% [20.1, 43.1] | 11.2% [6.6, 16.5] | `cross` 15.0% [8.5, 22.6]; `astra` 32.0% [20.2, 44.2] |
| `cross+astra` | 4 | 2 | 34.0% [22.4, 45.9] | 12.6% [7.7, 18.0] | `cross` 21.2% [13.0, 30.0]; `astra` 32.7% [20.9, 45.0] |
| `cross+astra` | 6 | 3 | 35.6% [24.2, 47.4] | 13.7% [8.6, 19.3] | `cross` 26.0% [16.8, 35.9] |
| `cross+astra` | 8 | 4 | 36.8% [25.2, 48.2] | 14.7% [9.5, 20.4] | `cross` 30.0% [20.0, 40.5] |
| `self+astra` | 2 | 1 | 36.5% [24.8, 49.0] | 28.3% [21.3, 35.8] | `self` 15.9% [7.4, 25.7]; `astra` 32.0% [20.2, 44.2] |
| `self+astra` | 4 | 2 | 38.5% [26.1, 51.2] | 29.5% [22.0, 37.1] | `self` 16.4% [7.7, 26.3]; `astra` 32.7% [20.9, 45.0] |
| `self+astra` | 6 | 3 | 39.2% [26.9, 52.0] | 30.1% [22.6, 37.9] | `self` 16.8% [8.0, 27.0] |
| `self+astra` | 8 | 4 | 39.5% [27.0, 52.3] | 30.5% [23.3, 38.4] | `self` 17.3% [8.2, 27.5] |
---

## What no reading flagged

### Table 5 — the residual: stratum-P defects no draw ever flagged

| population | families | total draws | n P instances (problems) | never flagged | share [95% cluster CI] | [95% Wilson, too narrow] |
|---|---|---:|---:|---:|---|---|
| broker_families_only | cross, self | 16 | 110 (56) | **68** | **61.8%** [50.9, 72.7] | [52.5, 70.4] |
| all_families | cross, self, astra | 20 | 110 (56) | **57** | **51.8%** [40.0, 63.3] | [42.6, 60.9] |
### Table 5b — what the residual defects are

Categories and their order were fixed in the preregistration (§1.5) before the first residual instance was read; each instance takes the first category that applies. Unit: the instance; the primary interval is the problem-cluster bootstrap, with Wilson shown beside it for comparison only.

| population | n residual (problems) | category | count | share [95% cluster CI] | [95% Wilson, too narrow] |
|---|---:|---|---:|---|---|
| broker_families_only | 68 (40) | `unexercised-edge` | 55 | **80.9%** [67.6, 92.5] | [70.0, 88.5] |
| broker_families_only | 68 (40) | `spec-misreading` | 8 | **11.8%** [2.9, 23.0] | [6.1, 21.5] |
| broker_families_only | 68 (40) | `timeout` | 5 | **5 of 68** — quoted as a count, not a rate | — |
| all_families | 57 (34) | `unexercised-edge` | 46 | **80.7%** [66.1, 93.1] | [68.7, 88.9] |
| all_families | 57 (34) | `spec-misreading` | 8 | **14.0%** [3.4, 26.9] | [7.3, 25.3] |
| all_families | 57 (34) | `timeout` | 3 | **3 of 57** — quoted as a count, not a rate | — |
---

## Ceiling 2 — whether the loop raised accuracy

The loop is `frozen solution → run_audit → (if BLOCKED) the product's own revision → hidden
suite`, over a frozen, paired 112-instance sample (56 P, 56 C, seed 20260907, **96 distinct
problems**). Generation is not repeated. The revision prompt is the product's own.

**The primary outcome is unconditional on whether a revision occurred** — `CORRECTIONS.md`
item 9 is this project's largest retraction and it is exactly the error of conditioning on a
consequence of the treatment.

### Table 6 — ceiling 2: the closed loop, per arm

Unit of analysis: the instance, paired before/after on the same instance; the resampling unit is the problem. Net is unconditional on whether a revision occurred.

The primary interval is the **problem-cluster bootstrap**; Tango's unconditional score interval and the exact unconditional interval (Berger-Boos restricted) are checks that ignore clustering. `p` is exact McNemar (instances independent); `p_clu` is a cluster-level sign-flip permutation test beside it. 112 instances come from **96 problems**.

A rate of **0/56** carries a bootstrap interval of [0.0, 0.0] for the same reason: with no positive instance to resample, the bootstrap cannot move. Read it as the count **0 of 56**, and its Wilson bound [0.0, 6.4] for a rate.

**†** — every discordant pair points the same way, so the percentile bootstrap cannot produce a resample of the opposite sign and its bound at zero is an artefact of the method. Read the Tango or exact unconditional interval on that row. This is `CORRECTIONS.md` item 4 applying to the replacement as it applied to what it replaced.

| arm | n (problems) | BLOCKED (P / C) | changed | fixed on P | broken on C | **net change** [95% cluster CI] | Tango CI | exact-unc. CI | p | p_clu |
|---|---:|---:|---:|---|---|---|---|---|---:|---:|
| `self-loop` | 112 (96) | 10 / 13 | 19 | 3/56 [0.0, 14.5] | 2/56 [0.0, 9.1] | **+0.89 pp** [-3.54, 5.88] (b=3, c=2) | [-3.98, 6.06] | [-6.70, 8.48] | 1.0000 | 1.0000 |
| `self-loop-rep` | 112 (96) | 10 / 13 | 19 | 3/56 [0.0, 14.5] | 2/56 [0.0, 9.1] | **+0.89 pp** [-3.54, 5.88] (b=3, c=2) | [-3.98, 6.06] | [-6.70, 8.48] | 1.0000 | 1.0000 |
| `cross-loop` | 112 (96) | 10 / 3 | 12 | 3/56 [0.0, 13.8] | 0/56 [0.0, 0.0] | **+2.68 pp** [0.00, 7.14] † (b=3, c=0) | [-0.73, 7.58] | [-4.46, 9.64] | 0.2500 | 0.5000 |
| `referent-loop` | 112 (96) | 25 / 10 | 35 | 11/56 [8.9, 31.7] | 2/56 [0.0, 9.1] | **+8.04 pp** [1.77, 15.26] (b=11, c=2) | [2.03, 15.27] | [-1.79, 17.41] | 0.0225 | 0.0469 |
### Table 7 — paired contrasts between arms

Outcome: whether the instance passes the hidden suite after one round. Unit: the instance, paired across arms; resampled by problem. Both discordant counts shown.

| contrast | n (problems) | discordant (b / c) | difference [95% cluster CI] | Tango CI | p | p_clu |
|---|---:|---:|---|---|---:|---:|
| self-loop minus cross-loop, hidden-test pass after one round | 112 (96) | 3 / 5 | -1.79 pp [-7.83, 4.39] | [-7.79, 3.81] | 0.7266 | 0.7812 |
| referent-loop minus cross-loop, hidden-test pass after one round | 112 (96) | 9 / 3 | +5.36 pp [-0.89, 12.07] | [-0.82, 12.36] | 0.1460 | 0.1826 |
| self-loop minus self-loop-rep, hidden-test pass after one round | 112 (96) | 0 / 0 | +0.00 pp [0.00, 0.00] | [-3.32, 3.32] | 1.0000 | 1.0000 |
### Table 7b — what the arms flag, paired and split by stratum

The mechanism behind any net effect. On stratum P a flag is a defect caught; on stratum C it is a false alarm. Unit: the instance, paired across arms; resampled by problem.

**Every row here is EXPLORATORY**: the preregistered twelve named outcome contrasts, not flag contrasts. They are reported because the mechanism matters, and they are labelled at every occurrence.

| contrast | stratum | n (problems) | flagged by each | discordant (b / c) | difference [95% cluster CI] | Tango CI | p | p_clu |
|---|---|---:|---|---:|---|---|---:|---:|
| `self-loop` vs `cross-loop` | P | 56 (41) | 10 vs 10 | 7 / 7 | +0.00 pp [-15.52, 16.07] | [-13.83, 13.83] | 1.0000 | 1.0000 |
| `self-loop` vs `cross-loop` | C | 56 (55) | 13 vs 3 | 12 / 2 | +17.86 pp [5.45, 30.36] | [5.47, 31.13] | 0.0129 | 0.0129 |
| `referent-loop` vs `cross-loop` | P | 56 (41) | 25 vs 10 | 16 / 1 | +26.79 pp [13.56, 40.35] | [14.45, 40.17] | 0.0003 | 0.0009 |
| `referent-loop` vs `cross-loop` | C | 56 (55) | 10 vs 3 | 7 / 0 | +12.50 pp [5.17, 21.82] † | [5.28, 23.63] | 0.0156 | 0.0156 |
| `self-loop` vs `self-loop-rep` | P | 56 (41) | 10 vs 10 | 0 / 0 | +0.00 pp [0.00, 0.00] | [-6.42, 6.42] | 1.0000 | 1.0000 |
| `self-loop` vs `self-loop-rep` | C | 56 (55) | 13 vs 13 | 0 / 0 | +0.00 pp [0.00, 0.00] | [-6.42, 6.42] | 1.0000 | 1.0000 |
---

## Statistical analysis

**Unit of analysis: the instance; the resampling and permutation unit: the problem.** The
loop's 112 instances come from **96 problems**; stratum P's 110 instances come from only
**56**. Where problems repeat across generation batches their instances are not independent,
so **every primary interval is a percentile bootstrap over whole problem clusters**
(10,000 resamples, seed 20260908) and **every McNemar p is accompanied by a cluster-level
sign-flip permutation p**. Wilson intervals are still printed where they were, marked as too
narrow. K draws over the same instances are repeated measures, never K × n observations.

**The interval that was withdrawn, and why.** The first version reported a Clopper–Pearson
interval for the direction probability *conditional on the discordant pairs*, rescaled by the
*observed* discordance fraction D/n. Conditioning is legitimate for McNemar's test; it is not
legitimate for an interval on the unconditional risk difference, because D/n is itself
estimated and its uncertainty is discarded. Enumerating D ~ Binomial(112, 0.1) with every
discordance beneficial gives that construction a coverage of **0.4162688657** where 0.95 was
claimed. It is retained in `numbers.json` as `withdrawn_conditional_ci95` with that number
attached, and `tests/test_ceiling_stats.py` pins that number on a reconstruction of the method, which keeps the figure checkable; it does not prevent the method from being re-implemented.

**What replaced it, and what its coverage actually is.** Every figure below is measured at
**this study's own n = 112**, by exact enumeration over the binomial rather than by
simulation. **The two scenarios are different and their numbers are not interchangeable** —
a previous version quoted the beneficial figure as if it were the detrimental one.

| method | role | `D ~ Bin(112, 0.1)`, all beneficial, true δ = +0.10 | `C ~ Bin(112, 0.5)`, all detrimental, true δ = −0.50 |
|---|---|---:|---:|
| conditional × observed D/n | **withdrawn** | **0.416** | not computed |
| problem-cluster percentile bootstrap (idealised) | **primary** | **0.924** | **0.953** |
| Tango's unconditional score interval | check | **0.960** | **0.953** |
| exact unconditional, Berger–Boos restricted, grid-approximated | check | **0.997** | **0.984** |

**What these numbers do and do not license.** They are coverage *of these two estimands in
these two scenarios*, with independent instances. They are **not** a coverage statement for
every estimand in this report, and — this is the important limitation — **the coverage of
the primary interval under this study's actual clustered design is unvalidated.** The
finite committed simulation gives the bootstrap **0.933 with 112 independent instances and
0.897 with 56 perfectly correlated pairs**, which is suggestive of a loss under clustering
and is not a validation of it. An earlier version of this report asserted that every
interval here is "2 to 5 points optimistic"; that was a generalisation the evidence does
not support and it is withdrawn. What can be said: **the idealised bootstrap under-covers
in the beneficial scenario (0.924 against 0.95), the two check intervals do not, and no
scenario tested here reproduces the clustered design the study actually used.**

**The exact check is grid-approximated, and its coverage depends on endpoint rounding.**
The supremum over the nuisance is taken on a 41-point grid with no bound on what a finer
grid would add, so it is not a proven exact interval and no claim that it "never
under-covers" is made. Its **0.984** is coverage of the intervals the function *returns*:
at `(b, c, n) = (0, 44, 112)` the grid test accepts δ = −0.5 with p = 0.0507, but bisection
returns a lower endpoint of **−0.499999993614**, which excludes −0.5 by 6.4 × 10⁻⁹. Counting
that instance as covered would give **0.9895** instead. The figure is therefore sensitive to
inward rounding at the endpoint, and is quoted as measured rather than as a guarantee.

**Both check intervals carried a nuisance-bound defect until the second review found it.**
They bounded the nuisance `q = p_c` by `(1 − |δ|)/2` where the feasible bound is
`(1 − δ)/2`. The two are equal for a non-negative difference and diverge sharply for a
negative one, so the defect was invisible in the direction this study's own results point.
Re-executing the pre-fix code gives:

| pre-fix method | beneficial `D ~ Bin(112, 0.1)` | detrimental `C ~ Bin(112, 0.5)` |
|---|---:|---:|
| Tango, pre-fix | 0.960 | **0.953** |
| exact grid, pre-fix | 0.997 | **0.075** |

**Two things follow, and an earlier version of this paragraph got the first wrong by
attributing 0.960 to the exact grid; 0.960 is Tango's.** First, the *coverage* collapse was
confined to the exact grid: pre-fix Tango still covered 0.953 in the detrimental scenario.
Second, adequate coverage did not make Tango's *intervals* right —
`tango_score_interval(20, 70, 112)` returned [−0.539, −0.358] where the correct interval is
[−0.577, −0.291]. **A method can carry a real defect and still pass a coverage check in the
scenarios you happen to test**, which is why a sign-symmetry test, not a coverage number, is
what now pins this. Fixed; detrimental-direction coverage is now **0.953 (Tango) and 0.984
(exact grid)**. A **sign-symmetry test** —
swapping b and c must negate and reverse the interval — now pins it, because that asymmetry
is the defect's fingerprint and was invisible in the direction this study's own results
happen to point.

**One caveat travels with the bootstrap.** Where every discordant pair points the same way,
a percentile bootstrap cannot generate a resample of the opposite sign, so a bound at zero
is an artefact. Rows where this fires are marked **†** and the unconditional intervals are
quoted instead.

**Union curves** are averaged over all C(K_max, K) subsets exactly, by the identity that an
instance flagged by k of K_max draws is missed by a random K-subset with probability
C(K_max − k, K)/C(K_max, K). Checked against explicit enumeration of every subset on 20
randomised cases.

**The saturation fit** is least squares on the K = 1 … K_max points, with **A constrained to
[0, 1] inside the objective**; for fixed τ the model is linear in A, so the fit reduces to a
one-dimensional search over τ. Goodness of fit and the raw union at K_max are reported beside
every asymptote, and an asymptote from a curve that has not flattened is labelled an
extrapolation everywhere it appears.

**Multiple comparisons.** Two primary outcomes, each declared singly in the preregistration
before any model call, are **not** corrected. **The preregistration planned twelve
comparisons; sixteen were computed.** The correction family is "every contrast reported with
a p value", size **16**, Bonferroni threshold **0.00313**, stated once and applied
everywhere. **Five planned comparisons — the mixed and `astra` asymptote contrasts — were not
delivered as specified** and are recorded as unmeasured (deviation 15). Every flag contrast
is **exploratory**, because the plan named outcome contrasts. The full
planned / performed / exploratory inventory is machine-readable in
`numbers.json → comparison_inventory`. The threshold is stated **once** here and appears
once more in the historical correction table above; both are intended. **Two** contrasts
clear the corrected threshold, and they are the same effect measured two
ways: `referent-loop` − `cross-loop` on stratum-P flags (p = 2.7 × 10⁻⁴, cluster
8.5 × 10⁻⁴) and on pooled flags (p = 3.0 × 10⁻⁶, cluster 1.0 × 10⁻⁵). Both are exploratory.

**Software.** No SciPy or NumPy is used for any inferential quantity; the regularised
incomplete beta, the Clopper–Pearson inversion, the exact McNemar tail, Tango's score
interval, the exact unconditional inversion, the cluster bootstrap, the sign-flip test, the
saturation fit and the beta-binomial likelihood are implemented in `report_ceiling.py` in
the standard library. `tests/test_ceiling_stats.py` (22 tests) checks each against brute
force, against a defining property, or by recovery of a planted value, **including exact coverage enumerations for Tango,
the exact grid and the idealised bootstrap in both the beneficial and detrimental
scenarios, and for the withdrawn conditional interval in the beneficial scenario only** — the cluster bootstrap is checked by simulation
rather than enumeration, and no coverage figure is computed for any other quantity. One real defect was caught by that file, a swapped beta tail; the
coverage failure above was found by the first review and has been pinned there since.

**Preregistration.** `benchmarks/code/ceiling/PREREGISTRATION.md` at `d96cdaf`, amendment 3
at `87939d2`, both before the first model call including the credential probe.

---

## Sensitivity: the population definition

### Table 9 — sensitivity: stratum P without the timeouts

The registered population is every hidden-suite non-pass, which **includes 7 instances whose suite did not terminate**. This table narrows it to instances with an observed assertion failure. The registered analysis is unchanged; this is a sensitivity check, and it is EXPLORATORY.

| family | union recall, registered P (n = 110) [95% cluster CI] | union recall, assertion-failure P only (n = 103) [95% cluster CI] | [95% Wilson, too narrow] |
|---|---|---|---|
| `cross` (K = 8) | 33/110 (30.0%) [20.0, 40.7] | **32/103** (31.1%) [20.4, 42.2] | [22.9, 40.5] |
| `self` (K = 8) | 19/110 (17.3%) [8.3, 27.3] | **18/103** (17.5%) [7.8, 27.9] | [11.3, 25.9] |
| `astra` (K = 4) | 36/110 (32.7%) [20.7, 45.0] | **34/103** (33.0%) [20.4, 45.6] | [24.7, 42.6] |
| **residual (never flagged)** | 57/110 (51.8%) [40.0, 63.3] | **54/103** (52.4%) [40.4, 64.4] | [42.9, 61.8] |

The 3 timeouts that sit inside the residual are `b1:Mbpp/267`, `b2:Mbpp/267`, `b2:Mbpp/765`.
---

## What it cost

### Table 8 — what it cost

From the product's own usage ledgers, per call, not reconstructed. The `astra` route bills a subscription and reports only tokens, so it consumes none of the dollar budget and is quoted in tokens.

| part | model spend | astra tokens |
|---|---:|---:|
| ceiling1 | $9.5238 | 4,427,530 |
| ceiling2 | $3.7083 | — |
| **total** | **$13.2321** | 4,427,530 |
---

## Deviations from the plan, numbered, with the direction of each bias

**1. Stratum F is not extended.** New draws cover P (110) and C (150) — 260 of 290. F is a
sanity check, not an outcome. *Bias: none on either primary outcome.*

**2. The reviser is shown the solution alone, not the whole working tree.** An 8-instance
pilot found that with the visible test file in `current`, the reviser answered test-file
findings by rewriting the tests — 3 of 3 revisions returned the solution byte-identical and
a modified `tests_visible.py`. From that point `current` is the solution alone; the **audit**
increment is unchanged, so audit prompts stay byte-identical to studies 1, 2 and 7's.

*Correction and honest labelling.* The first version said non-solution files "are discarded
and counted (the count is 0 in every arm after the change)". **That is false**: the counts
are **self-loop 4, self-loop-rep 4, cross-loop 2, referent-loop 0**, and all ten touched the
test file. They were discarded, so no reported outcome used them, but they show the reviser
still reached for the test file about 9% of the time it revised. And this change is
**outcome-informed protocol adaptation on reused instances**: the configuration was altered
after observing pilot behaviour on 8 instances that are part of the 112 later analysed. It
removes a failure mode and so plausibly favours the loop, but *the direction is not
established*, and a preregistered configuration would not have needed the change.

**3. The first full run of ceiling 2 was destroyed by the provider's circuit breaker and
discarded entirely.** Failed audits: **21 of 112 `self-loop`, 93 `self-loop-rep`, 109
`cross-loop`, 107 `referent-loop`**. `loop.py` had no retry passes; it now has bounded ones,
and a failed audit is never cached. Every arm was re-run from scratch.

*Correction.* The first version said "bias: none". **That is not established.** A complete
re-run avoids selecting on which instances happened to succeed, which is the main hazard,
but neutrality also requires that the failures were unrelated to the instances' potential
outcomes. The failures were provider-side cooldowns, which is *consistent* with
independence and does not prove it. **Direction of bias: undetermined.** The discarded rows
are archived and were not used.

**4. Two 8-instance pilots of `self-loop` were run and discarded.** The first exposed
deviation 2, the second validated the fix. Spend counted.

**5. Eight `cross-loop` revisions died inside a breaker cooldown and were repaired.** A
targeted repair re-issued only those eight, reusing the cached audit report so the audit
draw is untouched; all eight then succeeded, in a separate invocation recorded in the
manifest. *Correction:* the first version said a failed revision "necessarily biases the
arm's net downward". **Too strong** — a revision that had succeeded could equally have
broken a correct solution. What is certain is that a provider-killed revision is recorded
identically to a revision that changed nothing, which is a fidelity defect regardless of
direction. **Direction: undetermined; the repair removes the ambiguity.**

**6. Cost attribution was corrected mid-study** by stamping every `run_id` with a
per-invocation timestamp. Only the discarded pilots were affected.

**7. `self` draw 2 is study 1's `self` arm, and it covered batch 1 only** — 88 of the 260
in-scope instances; the other 172 were run here. Same heterogeneity study 7 recorded as its
deviation 2. *Bias: either direction; the determinism result is corroborated on both this
across-day pair and the within-minutes replicate.*

**8. `astra` was preregistered as amendment 1 while the Codex CLI refused the model
(`0.150.1`), and enabled as amendment 2 when it was upgraded (`0.153.4`).**

**9. The first 20-instance `astra` pricing batch was discarded** because `codex exec` writes
its token line to **stderr** and the harness read stdout. Re-run inside draw 1.

**10. `astra` bypasses the product entirely** — no broker, no metered ledger, no same-vendor
gate. Prompt bytes proved identical to the shipped auditor's (40 of 40).

**11. The same-vendor bypass is inherited and used**, as in studies 1, 2 and 7. **`src/` is
not touched by this study.**

*How to verify that, correctly.* This branch was cut at `19bd161`, and
`fusion/evidence-authority` has since advanced (the D156 skills slice). A diff against the
branch **tip** therefore shows changes — they are the base branch's, not this study's, and
reading them as this study's would be a false positive. The check that means what it says
is against the **merge base**:

```sh
git diff --stat "$(git merge-base fusion/evidence-authority HEAD)"..HEAD -- src/   # empty
git log --oneline "$(git merge-base fusion/evidence-authority HEAD)"..HEAD -- src/ # empty
```

Both are empty. This study's commits touch **`benchmarks/` and `.gitignore`** only — the
`.gitignore` line excludes the fetched corpus, which is not redistributed.

**12. Transient provider failures cost wall-clock throughout and changed no result.** Final
coverage is **260 of 260 on all 20 draws**, and every ceiling-2 arm covers all 112 instances.

**13. Two preregistered residual categories were never assigned** (`wrong-algorithm`,
`ambiguous-oracle`), because the rule's ordering absorbs disputable-oracle cases into
`unexercised-edge`. Applied as written; consequence stated at the table.

**14. The `astra` manifest's `spend_usd_cumulative` counts only broker calls.** `astra` makes
none, so its rows contribute $0.00 and 4,427,530 tokens.

**15. Five planned comparisons were not delivered as specified.** Preregistration §3.2 and
amendment 3 §5 name the `mixed` and `astra` **asymptote** contrasts (planned items 2, 3, 10,
11, 12). Table 4 reports **raw union rates at matched total draws** instead, with no fitted
contrast and no interval. **Those five comparisons are unmeasured in this study**, and the
mixed-family rows are descriptive and exploratory. Found by the cross-vendor review.

**16. The published interval method was replaced after publication.** The first committed
version of this report used a conditional-times-observed-D construction with 0.416 coverage.
It was found by the cross-vendor review, reproduced, withdrawn, and replaced. All point
estimates are unchanged. **Erroneous numbers did enter a committed artefact**: see below.

**17. Provenance was completed after the runs.** Package versions, per-invocation UTC
windows, provider base URLs, corrected sampling metadata and re-hashed analysis files were
added by `ceiling/finalise_manifests.py` from the ledgers and the installed environment. Both
manifests were originally written mid-run and recorded dirty working trees; the clean freezes
are `d96cdaf`/`87939d2` for the plan and the finalisation commit for the analysis.

**18. The replacement interval methods were themselves defective, and were fixed after the
second review.** Both `tango_score_interval` and `exact_unconditional_interval` bounded the
nuisance `q = p_c` by `(1 − |δ|)/2` where the feasible bound is `(1 − δ)/2`. Equal for a
non-negative difference; badly wrong for a negative one. Measured consequence, **by method
and by scenario**, because an earlier version of this deviation paired one method's
beneficial figure with the other's detrimental one: pre-fix **Tango** covered **0.960**
beneficial and **0.953** detrimental; the pre-fix **exact grid** covered **0.997**
beneficial and **0.075** detrimental. The coverage collapse was the exact grid's alone —
and Tango, whose coverage was fine, still returned intervals off by nearly 4 points at each
end (`tango_score_interval(20, 70, 112)`). **No number in this
study was affected** — every paired difference here has b ≥ c except `self-loop − cross-loop`
(b = 3, c = 5), whose Tango interval was recomputed and is unchanged to the displayed
precision — but the method was wrong and would have been wrong for anyone reusing it.
Fixed, with a sign-symmetry test and a two-directional coverage enumeration added.
*Direction of bias on this study's results: none detectable; on a future study with
predominantly detrimental discordances: severe.*

**19. Coverage claims for the replacements were overstated, in the opposite direction to
deviation 16.** The second version said the primary bootstrap was "0.95 nominal by
simulation" and that the exact unconditional check "never under-covers". Neither is true:
the idealised bootstrap covers **0.924** at this n, the committed simulation gives 0.933
and 0.897, and the exact check is **grid-approximated** with no bound on the missed
supremum. Both claims are withdrawn and replaced by measured numbers in both directions.
~~*Every interval in this report should be read as approximately 2 to 5 points
optimistic.*~~ **Superseded by deviation 21.** That sentence, written as this deviation's
own conclusion, is the same over-generalisation the deviation was recording: it takes two
independent-instance scenarios and applies them to every estimand under a clustered design.
The supportable statement is in deviation 21 and in the coverage section — **coverage under
the actual clustered design is unvalidated**, and the per-method, per-scenario figures are
the only coverage claims this study makes.

**20. The report's tables were re-spliced after the second review.** Between the second and
third versions the prose was edited but the tables were not re-generated into the document,
so for a period the committed report carried round-1 tables beside round-2 prose. Caught
while answering the review; every generated table in this version is the current generated output — a test splices the committed `tables.md` into the report and requires no change — and
`tests/test_report_consistency.py` now checks the numbers in prose. **What that check is,
exactly:** a lexical editing guard for registered numeral templates in the opening and
conclusion: every registered rate must carry its bound interval adjacent, and its sentence
must name its family. It does not parse grammatical ownership, does not read rates written
in words, and applies membership checks only outside those two sections. Four attacks it
cannot see are committed green and explained in
`test_documented_uncovered_cases_are_green_and_that_is_the_boundary`, so the boundary lives
in the tests.

**21. Coverage figures were mislabelled by scenario, and generalised beyond what was
measured.** The third version gave the detrimental-direction bootstrap coverage as 0.924,
which is the *beneficial* scenario's number; it is **0.953**. It also asserted that every
interval in the study is "2 to 5 points optimistic" — a generalisation from two scenarios
with independent instances to every estimand under a clustered design. Both are corrected;
**coverage under the actual clustered design remains unvalidated**, and that is now stated
rather than papered over. *Direction: the mislabelling made the primary interval look worse
than measured in one scenario; the generalisation made every other interval look worse than
evidence supports. Neither changed a result.*

**22. The consistency guard introduced in deviation 20 did not work.** The third review
demonstrated that mutating a quoted interval by 0.01 left it green, and that replacing the
headline interval with `[−99.99, +99.99]` also passed: it rounded to one decimal, allowed
0.051 of slack, ignored the Unicode minus and leading `+`, and accepted any interval in the
file regardless of estimand. **The claim in deviation 20 that it "fails the build if any
interval quoted in prose is absent" was false.** Rewritten to compare at displayed precision
with zero tolerance and to bind the headline and primary spans to their estimands; the
mutations are now committed as a test of the test. Rewriting it immediately found two live
errors — a prose interval quoted as `[+6.3, +43.7]` had been written `+43.8`, and a flag
contrast's exact interval was quoted in prose but never stored in the record.

**23. Table splicing is now a command, not a habit.** Twice the prose was edited without
re-generating the tables into the document, leaving the report a version behind its own
numbers; the third review caught the second occurrence. `ceiling/splice_tables.py` does it
in one step and warns if a generated table is missing from the report.

**24. A coverage figure was attributed to the wrong method.** The third version's account
of the nuisance-bound defect said the *exact grid* covered 0.960 in the beneficial
direction. **0.960 is Tango's**; the pre-fix exact grid covered 0.997 beneficial and 0.075
detrimental. Corrected in the report, Amendment 5 and `CORRECTIONS.md` #17, and the pre-fix
estimators are now committed as runnable code with their coverages asserted. Since the
tenth review, the report's coverage tables are themselves **bound to a measured artefact**
(`records/ceiling/coverage.json`), so a printed coverage figure that differs from the measurement reddens — and since the eleventh review so does a swapped or mis-parameterised column header, or an unbracketed, unsigned figure of the literal form `0.ddd` in a sentence containing the letters `cover` that is not among the measured values (membership; a figure is not attributed to a method, and figures in any other form are not read). *Direction: the error understated how well the
pre-fix exact grid did in one direction and obscured that the collapse was confined to that
one method. It changed no result.*

**25. The interval-completeness rule is now mechanical, and it found gaps four reviews had
not.** Bare rates in the opening and conclusion were corrected by hand after each of the
first four reviews. A test now requires every rate **the scanner recognises** — a numeral
followed by `%`, `pp`, `points` or `percentage points` — in those two sections to be
followed adjacently by an interval, or to be explicitly declared, with a reason, as owing
no interval — a count, an exact quantity, a nominal confidence level, the separately
checked headline, or an approximate reading of the power curve.
Writing it exposed **two further gaps no reviewer had listed** — a bare `+26.8 points` in
the opening and a `51.8%` whose interval sat too far away to read as attached — and its
test-of-the-test exposed that a first version of the rule accepted any interval later in
the sentence, including one belonging to a different rate.

**26. Two code paths bootstrapped the same estimand under different seeds, and the report
quoted both.** The residual share (57 of 110) was computed once by the residual analysis
(seed 20260912 → [40.0, 63.3]) and again by the timeout sensitivity's registered column
(seed 20260923 → [40.4, 63.6]), and the report quoted each in different places as *the*
interval for that number. The same was true of the registered union recalls. **Both now
reuse the canonical seed**, so Table 9's registered column is identical to Tables 1 and 5
rather than a second bootstrap of the same thing. Found while binding every recognised rate in the
opening and conclusion to its own key — no reviewer had caught it, and no earlier guard
could have, because both intervals were real numbers present in the record.

**27. The seed inventory is now generated from the code rather than written by hand.**
Hand-written ranges were wrong twice: `+50+total` was listed as a contiguous range when
only totals 2, 3, 4, 6 and 8 occur, and the union-curve range was given as K = 8..16 when
the curve uses K = 1..8. Every bootstrap call is now wrapped during a cheap pass and its
seed recorded; the manifest carries the observed set (32 seeds across 196 calls) and
reconciles every hand-written entry against it.

**28. The single sentence the report asks a reader to carry away was the one sentence no
check covered.** A declaration in the consistency guard said the reader sentence's interval
was verified by the mechanism that binds the headline; that mechanism binds a different
sentence. The interval could be replaced with a fabricated range, or removed, with every
test passing. Fixed by binding it explicitly and parsing its prose "to"-form. *There is no
bias direction here: the sentence was correct throughout. What was wrong was the claim that
anything was checking it.*

**29. A binding label was reused across families, so a rate could be bound to another
family's array.** A rule anchored on the words "cost (" matched any family's
false-positive cost. The sixth review inserted a sentence attributing `astra`'s
one-reading 9.7% [5.3, 14.5] to the shipped auditor's eight readings — whose value is
16.0% [10.1, 22.3] — and it passed. Every reused label now carries its family and reading
count, and a test fails if any rule matches more than once.

**30. The seed inventory instrumented one call site instead of the constructor, and so
declared a consumed seed unused.** Both manifests said no contrast exceeds 22 non-zero
clusters and `BOOT_SEED + 7` is never drawn. `numbers.json` recorded, in the same commit,
that the pooled self−cross flag contrast has 25 non-zero clusters and used "sampled,
200000 draws, seed 20260915". The instrument now wraps `random.Random` itself: **34 seeds
over 205 constructions**. *A claim contradicted by the file it shipped beside is the
cheapest kind of defect to prevent and this study shipped it twice — see also deviation 26.*

**31. A rate could be re-attributed by moving its clause into a new sentence.** The
binding rules checked where a rate sat, not what its sentence was about, so splitting one
conclusion sentence in two and giving the second a different subject silently transferred
`astra`'s one-reading false-positive rate to the shipped auditor's eight readings. Every
bound rate now requires its own sentence to name the family its array belongs to. *This
particular attack was synthetic and never appeared in a published version; for the values
that were published wrong and corrected, see the table in deviation 34 — an earlier version
of this sentence asserted that none ever was, which is false.*

**32. A hand-written seed explanation contradicted the instrument for the second time.**
Deviation 30 recorded one such contradiction; the same commit contained another, stating
that seed 20260909 "does not appear in observed_seeds" when it does. Hand-written
observation claims about seeds are now **removed entirely**: consumed-or-not is derived
from the instrument, and prose is confined to explaining why an unconsumed seed is
unconsumed.

**33. The consistency test file contained eleven duplicated function definitions**, four of
them test functions, each silently overriding its twin. All pairs were byte-identical, so
no check was wrong — but this is the second time duplication has appeared in that file
after string-level surgery, and the hazard is the one already recorded in deviation 26.
Removed, with an `ast`-based check used to confirm none remain.

**34. The subject binding was example-driven for three rounds.** Rounds 6, 7 and 8 each
found a rate that could be re-attributed by editing prose, and rounds 6 and 7 were each
fixed as an instance. Round 8 established the pattern: **11 of 23 bound arrays had no
subject requirement at all**, and the asymptote rules accepted generic words, so three
further re-attributions were green. Every bound array now declares a family or arm subject,
a test fails on an absent declaration or an unknown family, and **a generated test
produces 312 re-attribution mutations from the rule table and requires every one to
redden**. Neither test detects a *weak* declaration — the first checks vocabulary
membership, the second mutates only the tokens a rule declares. **Seven
failing rule matches across four sentences** could not name their own subject and those
sentences were rewritten — the test named every one.

*The scope of this deviation, stated precisely because an earlier version of it overreached.*
The synthetic re-attribution counterexamples in rounds 6–8 did not change the committed
estimates; earlier numerical and reporting corrections remain documented. **"No published
number was ever wrong" — which this deviation and deviation 31 previously asserted — is
false as a history**, and the ninth and tenth reviews were right to strike it.

**The published values the reviews found wrong, and their corrections**, each cited to the
round that found it. A selected inventory, built from the review reports and not from
memory: it holds what the reports state and claims no completeness beyond them (the false
test count of round 11 is recorded in CORRECTIONS #30 and below).

| round | published | corrected to | kind |
|---:|---|---|---|
| 1 | `returned_non_solution` counts stated as **0 in every arm** | **4 / 4 / 2 / 0** | count |
| 1 | the `self` family's eight readings add "**one more** defect" | **two** (17 → 19) | count |
| 1 | "**exactly one** contrast clears the corrected threshold" | **two** (referent−cross P flags and pooled flags) | inference |
| 1 | comparisons planned as **twelve** | **sixteen** performed (four arm nets, three final-outcome contrasts, nine flag contrasts) | count |
| 1 | the paired interval's coverage taken as its nominal **0.95** | **0.416** measured | coverage |
| 2 | `referent−cross` net interval **`[−0.88, +12.08]`** | **`[−0.89, +12.07]`** | interval |
| 2 | bootstrap coverage taken as its nominal 0.95 | finite simulation **0.933** with 112 independent instances, **0.897** with 56 correlated pairs | coverage |
| 2 | exact-unconditional coverage **0.998** quoted for n = 112 | measured at **n = 40, q = 0.15**; the n = 112 figure is **0.997** | coverage |
| 3 | referent P-flag exact interval upper bound **`+43.8`** | **`+43.7`** | interval |
| 3 | detrimental bootstrap coverage quoted as **0.924** | **0.953** for that scenario | coverage |
| 4 | beneficial coverage **0.960** attributed to the pre-fix exact grid | **0.997**; 0.960 is Tango's | coverage |
| 4 | `manifest_loop.json`'s 24 unmatched events described as **individually enumerated** | **ten run-ID groups**, listed as such, totalling 24 events — the total was right | inventory |
| 5 | seed-inventory ranges: curve `K = 8..16`; contiguous comparator range; mixed-family seeds | `K = 1..8` (seeds 20260929–20260936); totals **2, 3, 4, 6, 8** only; mixed-family seeds **20260939–20260946** | inventory |
| 6 | residual share published as both **`[40.4, 63.6]`** and `[40.0, 63.3]` | **`[40.0, 63.3]`** | interval |
| 6 | three registered-union intervals **`[20.0, 40.5]`**, **`[8.2, 27.3]`**, **`[20.9, 45.5]`** | **`[20.0, 40.7]`**, **`[8.3, 27.3]`**, **`[20.7, 45.0]`** | interval |
| 6 | seed `BOOT_SEED + 7` declared never drawn | **consumed**: 25 non-zero clusters, 200,000 sampled draws | inventory |
| 7 | seed 20260909 stated not to appear in `observed_seeds` | it does | inventory |
| 7 | attribution: "six of the nine" reviewer findings | **eight** | count |
| 8 | the expanded attribution table described as **nine** findings with one author exception | **ten findings: eight reviewer, two author** — "eight of the nine" was right for the numbered set | count |
| 9 | "seven report sentences" rewritten | **seven failing rule matches across four sentences** | count |
| 11 | "21 statistics tests" | **22** | count |
| 11 | a build reported as "**46 tests pass**" | **one failed** (CORRECTIONS #30) | count |

Separately, and distinguished because it never reached prose: the swapped Clopper–Pearson
tail put **`[+3.16, −1.93]`** into a committed *artefact* (`tables.md` at `1a66571`) for 99
seconds before the fix at `7dc2620`. It appeared in no published report.

What is true, and is all that was meant: **the re-attribution attacks of rounds 6 to 8 were
synthetic edits that never appeared in a published version, and no empirical point estimate
— no asymptote, union, net, count or classification — has changed since the first version.
Interval estimates did change**: the four rows above marked *interval*, plus every interval
recomputed when the method was replaced in rounds 2 and 3.

**35. A check that only ran at review time is not a check.** The AST duplicate scan that
found deviation 33's eleven duplicates was run by hand and never committed, so the suite
stayed green when a function was duplicated. It is now a test over every Python module under
`benchmarks/code`, covering functions, classes, and assignments to names — plain, annotated,
and names inside tuple targets; attribute and subscript targets are not definitions —
verified to redden on a duplicated helper and on a second annotated `RATE_RULES`, and to
visit the coverage module and the statistics tests.

**36. The guard's claim exceeded what it enforces, and the claim — not the guard — was
wrong.** Nine rounds of review had steadily widened this study's consistency checks; the
ninth found that the accompanying description had outrun them. A lexical guard cannot parse
grammatical ownership, cannot read a rate written in words, and cannot see a claim that
carries an interval but no numeral. Outside the opening and conclusion it applies a
membership check and nothing more — a fabricated interval of the recognised form in a caption is
still rejected, but nothing there is bound to a subject.
The scope is now stated in those terms in the module docstring and in the report's
description of the guard — a test asserts each full quotation of that sentence is identical
to the docstring's; other passages describe parts of the guard and are not bound to it — and the four
surviving attacks are committed as **passing** tests with an explanation of why each is out
of reach — so the boundary is discoverable from the suite rather than from a review report.
*This is the first round in which the correct response was to make a claim smaller rather
than a mechanism larger, and it took a reader to see it.*

**37. Eleven sentences claimed more than their checks delivered, and one claimed less.**
The tenth review enumerated them by line. The pattern across rounds 9 and 10 is the same:
the mechanisms were sound within a scope and the prose around them was not. Each is now
written to what its check does — the rate scanner's four numeral formats are named,
membership is distinguished from attribution, the six declarations that bind nothing are
qualified, and the impossibility claim is deleted because the documented-boundary test
contradicts it. One correction went the other way: the guard *does* apply a membership check
outside the opening and conclusion, and saying it "does not police" that text understated it.

**38. The report's coverage figures had nothing checking them, and are now bound to a
measurement.** Editing a published coverage figure from 0.997 to 0.960 left every test
green: the statistics suite measured coverage and the report quoted coverage, with nothing
between them. `ceiling/measure_coverage.py` now measures all eleven figures by exact
enumeration into `records/ceiling/coverage.json`; the statistics suite asserts its
measurements equal that artefact — all eleven figures since the eleventh review, which found
three compared by nobody — and a report test asserts both coverage tables, their column
order and `Bin(n, q)` parameters equal it, and every unbracketed, unsigned figure of the
literal form `0.ddd` in a sentence containing the letters `cover` is one of its values or of
an explicit historical list (the n = 40 figure and the finite-simulation figures). That
last is a membership check with a literal trigger and a literal token form: a figure is not
attributed to a method or scenario, and a coverage written with two decimals, as `1.000`,
in words, with a sign, inside brackets, or in a sentence that describes coverage without
the word ("contains the true parameter in … of repetitions") is not read. *The review
offered the alternative of disclaiming the claim instead; binding it was the better answer
because the claim is one worth being able to make.*

**39. A vocabulary check now guards the guarantee words themselves.** Seven words — "every
rate", "cannot hide", "impossible", "guaranteed", "all real and correct", "any other
family", "wherever" — fail the build in the report and both test files unless the whole
sentence containing them is one of an exact list of allowed sentences. Allowances are
sentences, not substrings, so a new sentence cannot inherit an old one's. Sentences are
read after asterisks, emphasis underscores, backticks and footnote markers are removed and
whitespace is collapsed; other formatting — HTML, entities, zero-width characters — is not
normalised, and the generator `report_ceiling.py` and its `tables.md` are scanned with the
report, because the twelfth review found the generator still emitting the sentence round 11
had failed on. Each word is on the
list because a review found it asserted falsely at least once, and the reason is recorded
beside it. Writing the check found further unqualified uses the review's line-by-line list
had not reached; they were rewritten in the same commit and not individually recorded. The
eleventh review found the first version of this check exempting quoted spans and stopping at
its own marker, so a quoted assertion or anything after the marker survived — and found it
red on one sentence of a build that had been reported green; both are closed, and the test
count reported for a build is the runner's own summary line. *This is the crudest mechanism in the study and the one
most likely to converge, which is why it is here.*

### The beta-tail defect, stated exactly

The first version said a swapped Clopper–Pearson tail was "caught by my own tests" and that
"no number had left the harness". **The second half is wrong.** The swapped interval was
written into a committed artefact: `git show 1a66571:benchmarks/code/records/ceiling/tables.md`
contains the headline as `[+3.16, −1.93]`, committed at **18:46:39**, and the fix landed at
**18:48:18** — **99 seconds later**. The erroneous numbers existed in a committed results file
for that interval. They never reached the report, which was first committed at 20:55:51, after
the fix. The correct statement is: **an erroneous number entered a committed artefact for 99
seconds and was corrected before any prose quoted it.**

---

## Limitations

- **One corpus of short, self-contained Python functions is not a repository.**
- **One generator is one generator.**
- **Vendor independence is not statistical independence.**
- **The asymptote is a fitted quantity, and `cross`'s is an extrapolation from a curve that
  is still rising.** No arithmetic separates "never findable" from "findable with very small
  probability" out of eight draws. The residual classification describes what was missed by
  these readers; it establishes nothing about what is findable in principle.
- **`astra` measures a model, not the product.**
- **Round one only.** Every loop arm revises once.
- **The population is hidden-suite non-passes.** Seven of 110 P instances are timeouts. The
  sensitivity analysis moves nothing, but the label matters.
- **The corpus's own oracle is disputable in most of the residual** — 40 of 57, exploratory.
- **The loop's run-to-run variation across time is unmeasured.** The replicate measured route
  determinism, not stability.
- **Deviation 2 is outcome-informed protocol adaptation** on instances that are also in the
  analysed sample.
- **Nine studies over two tasks**, one author, one harness, overlapping assumptions.
- **The `self` arms bypass a product guarantee** the product refuses to ship.

---

## What this study licenses, and what it does not

**It licenses**: that on this corpus, the `self-loop` arm — the generator's own model
auditing and revising its own code — produced no measurable gain in hidden-test accuracy
(+0.89 pp, cluster CI [−3.54, +5.88], every interval spanning zero); that over eight readings each, its union recall was **below** a cross-vendor
stranger's (raw −12.7 points [−25.0, −0.9]) while its false-positive rate was higher
(24.0% [17.2, 31.2] against 16.0% [10.1, 22.3]); that
repetition saturates quickly, and on a temperature-0 route almost immediately; that one
frontier reading matched eight shipped readings on recall (30.2% [19.3, 42.0] against
30.0% [20.0, 40.7]) at lower false-positive cost (9.7% [5.3, 14.5] against 16.0%
[10.1, 22.3]); and
that **51.8% [40.0, 63.3] of this defect population (57 of 110) was flagged by no reading
of any family**, dominated by inputs the visible tests never construct.

**It does not license** the claim that those defects cannot be found. It shows that these
detectors, over 20 readings, did not find them.

**It does not license** "the referent works". It licenses "**the referent moved what the
auditor flagged, by more than anything else tried** (+26.8 points on stratum-P flags,
cluster CI [13.6, 40.4], exploratory, clearing the corrected threshold), **and whether that
converts into accuracy is not established**" (+5.36 pp against `cross-loop`, cluster CI
[−0.89, +12.07], p = 0.146). It licenses running that arm
again, larger, as a primary outcome.

**It does not license** replacing the shipped auditor with `astra`, nor any statement about
the mixed-family asymptotes, which were planned and not measured.

### Where this sits beside the earlier record

`CORRECTIONS.md` item 11 withdrew "the cross-vendor auditor sees more" and replaced it with
"a stranger is less tolerant", on prose, at n = 30, where self-audit recalled 31.7% against
cross's 19.8%. **On code, with model-free ground truth and eight readings each, the ordering
at eight readings is the other way round**: `self` 17.3% against `cross` 30.0%. Different
task, different ground truth, different estimand. The honest summary is that **the direction
of the self/cross recall gap is task-dependent and has now gone both ways**, while the
false-positive half has gone the same way every time: the self-auditor flags more correct
work (24.0% against 16.0% here; 13 of 56 against 3 of 56 in the loop).

Study 7 concluded that the architecture is not the lever. This study adds: **the number of
readings is not the lever either; the model is one; and the instructions moved flags more
than either — without a demonstrated effect on accuracy.**

---

## Reproduction

```sh
export PYTHONPATH="$(git rev-parse --show-toplevel)/src"
python benchmarks/code/fetch.py            # the corpus is not redistributed

# ceiling 2 — the closed loop, four arms over one frozen 112-instance sample
python benchmarks/code/loop.py --probe --run <run-dir>
python benchmarks/code/loop.py --run <run-dir> --workers 3 --budget-usd 5
python benchmarks/code/loop.py --run <run-dir> --repair-revisions

# ceiling 1 — the saturation ladder, and the astra family
python benchmarks/code/ceiling.py --plan
python benchmarks/code/ceiling.py --run <run-dir> --check-prompt   # prompt bytes, no cost
python benchmarks/code/ceiling.py --run <run-dir> --budget-usd 13 --workers 3
python benchmarks/code/ceiling.py --run <run-dir> --astra --astra-draws 4

# every generated number in this file (numbers.json, tables.md) from committed records, no key and no network — Table 9 alone reads the archived run directory (--run)
python benchmarks/code/report_ceiling.py
python benchmarks/code/ceiling/finalise_manifests.py --run <run-dir>
python benchmarks/code/residual_dump.py --run <run-dir> --population all_families

# the statistics, including the coverage simulations
python -m pytest benchmarks/code/tests/test_ceiling_stats.py
```

`report_ceiling.py` regenerates Tables 1–9 for $0.00; the two coverage tables come from
`ceiling/measure_coverage.py`, and deviation 34's correction table is written from the review
reports. It reads the archived run
directory only for the timeout sensitivity (Table 9); without it that table says
`AUTHOR_INPUT_NEEDED` and nothing else changes. It will not reproduce byte-identically from
an empty *detector* cache: the `cross` route samples. `--no-exact-unconditional` skips the
one expensive check interval.

### What a re-run must match, and what does not matter

**Must match exactly:** the audit-set and instance digests, the three corpus revisions in
`manifest_corpus.json`, the model ids, the auditor SYSTEM prompt sha256, the constitution
sha256, the referent rule's sha256 and text, the flag rule (≥ 1 BLOCKER), the temperature
each route sends, and the seeds (20260907 sample, 20260908 bootstrap).

**Does not matter:** worker count, wall-clock, machine, ladder order, scratch path, retry
passes.

### The committed record

`benchmarks/code/records/ceiling/`: `cache/holistic__<family>__d<K>.jsonl` (detector ×
instance), `cache/*.failed.jsonl`, `loop/<arm>.jsonl` (arm × instance),
`loop/solutions-<arm>.jsonl` (**the revised solutions themselves**), `loop_sample.json`,
`residual_classification.json`, `numbers.json`, `tables.md`, `manifest_ceiling1.json`,
`manifest_loop.json`, `baseline_reproduction.json`.

The revised solutions are committed because EvalPlus is redistributable and ceiling 2's
primary outcome re-scores from them with no key and no network. **No finding prose is
committed.**

Run directories are archived at `~/Documents/Crossaudit/study-data/wt-ceiling-runs/` and are
registered in the programme-wide archive index, `benchmarks/ARCHIVE_MANIFEST.json`, under
`studies/wt-ceiling-runs`:

| record | value |
|---|---|
| this study's own per-file manifest | `MANIFEST.sha256`, **178 files**, digest `e5ef7227567c4fc44268624c73623eaf0eae8d44d8b423aa322c335a3aa6acbc` |
| the programme index's entry | **179 files**, `directory_sha256` `ecdb86464e0ce6d1bcddb470586f008b60ff72d2901b0aecfdd9cc6cb5a41245`, 8,197,800 bytes |

**The two counts differ by one on purpose and neither is wrong.** The index's counting rule
covers every regular file under the study directory *including the archive's own
`MANIFEST.sha256`*; this study's figure excludes that file, because a manifest cannot list
its own digest. Both are verifiable on disk: `find . -type f | wc -l` gives 179 and
`find . -type f ! -name MANIFEST.sha256 | wc -l` gives 178.

**Provenance note on the index entry:** it was added to `fusion/evidence-authority` after
this study branch was cut, so `benchmarks/ARCHIVE_MANIFEST.json` *on this branch* does not
yet contain it. It is reachable at
`git show fusion/evidence-authority:benchmarks/ARCHIVE_MANIFEST.json`, and will be present
here on merge. The digests above were read from that file, not asserted.
