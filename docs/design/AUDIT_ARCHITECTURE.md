# Where the audit's evidence comes from — a redesign, and what licenses it

Written 2026-09-05, after a measurement round that withdrew every headline
finding this project had. It proposes changing what the model rung is *for*.
Nothing here is built yet; the experiment that can kill it is running.

## 1. The diagnosis

Six architectures have now been measured on this product's audit. Set them side
by side and one thing is obvious:

| change | recall | false positives | domain |
|---|---|---|---|
| decomposition vs holistic | +9.1 pts | +8.0 pts | code, model-free truth |
| union of 2 identical runs | +2.4 pts | +2.3 pts | code, model-free truth |
| union of 2 identical runs | +9.9 pts | (base-rate confounded) | prose |
| two-stage cross filter | −10.9 pts | −1.3 pts | code, model-free truth |
| stronger auditor model, same vendor | +1.8 pts | — | prose, n=10 |
| splitting the rules | +21.5 pts | — | prose |

**Every one of them slides along the same curve.** Recall goes up, false
positives go up by about as much; filter for precision and recall collapses
faster than the false positives do. That is what happens when the interventions
are all the same *kind* of evidence — a model reads text and forms an opinion —
and only its quantity, framing or aggregation changes. Splitting the rules is
the one large mover, and it moved the *referent* rather than the architecture:
it told the auditor what to look for.

And the opinion does not hold still. Four identical replays over the same 20
byte-fixed drafts, same constitution, same auditor, same commit (D154):

- pooled recall reproduces **to the decimal** — 23.5, 19.4, 25.5, 25.5
- per-instance finding count is stable on **2 of 20**
- per-instance BLOCKED/PASS verdict is stable on **14 of 20**

Re-running the identical audit changes whether the work is stopped about **30%**
of the time, and there is no setting for it: the broker already sends
`temperature: 0` to every model whose capability card accepts one, and the
auditor model's card carries `temperature=False` because reasoning models of this
generation accept only their own default.

## 2. What the model rung is actually good at

It is a weak, unstable detector. It is also, measurably, two other things:

- **An interested party, or not one.** A stranger gates **80.0%** of increments
  where the author's own model gates **3.3%** — +76.7 pp, McNemar p = 2.4 × 10⁻⁷,
  23 discordant pairs with none pointing back, and reproduced independently in
  study 6 at 3.3× the findings (160 findings, 160 BLOCKER, zero ADVISORY). This
  is the largest and most reproducible effect the programme has produced.
- **A partial and non-redundant observer.** Of 34 defects flagged by either
  architecture in code, 18 were seen only by decomposition and 8 only by holistic
  review. Different configurations see different things; the union is 30.9%
  against 14.5% for holistic alone.

Note what is *not* on that list. The self-audit is not blind — it named **31.7%**
of the defects CLEAR found against the stranger's **19.8%**, and it was the most
precise arm at 82%. It simply refuses to stop the work. **The generator's own
model is the better detector and the worse judge**, and today's architecture uses
it as neither.

## 3. The proposal as first written — withdrawn the same day

*The section below is kept as written on the morning of 2026-09-05. Its
load-bearing assumption was tested that afternoon and failed. Read it as the
record of a proposal, then read §5a for what killed it and §6 for what stands.*

**The kill condition fired.** Asked for executable checks on the 56 stratum-P
solutions — code, the one domain where an expected value is exactly computable
and the predicate is a single `assert` — the auditor produced a runnable,
discriminating check on **13 of 56 (23.2%, CI 14.1–35.8%)** against a
preregistered bar of 19; the replicate arm gave 11 of 56, and the union of both
runs is still 13. Format was never the constraint: 288 of 288 checks compiled,
96% ran clean, zero sandbox escapes. It fails at the only step that matters, and
it fails **in the wrong direction**: its checks block the known-correct reference
solution on **22 of 56** instances and the defective one they were written for on
**18 of 56**. Inverted checks outnumber discriminating ones 26 to 19. It picks
edge cases well, computes the expected value wrong, and invents specification the
problem never stated and then asserts it. See `benchmarks/code/RESULTS-CHECKS.md`.

Under this proposal each of those would have been a non-overridable BLOCKER on
correct code with no prose for a person to disagree with — because the design
removed the prose on purpose.

### 3 (as written). Nothing blocks that was not executed

Today one model call does two jobs — find things, and decide. The verdict
therefore inherits the sampling noise of the finding step, which is why a 30%
verdict flip follows from an unstable enumeration.

Split them.

**Detection — wide, cheap, unioned, never filtered by agreement.**
Assemble findings from every source that can look, including the generator's own
model (best measured detector) and a decomposed pass (sees different defects).
Union them. Do not intersect, do not vote, do not require corroboration: in
prose, findings the auditor raises on *every* run are correct 45% of the time
against 88% for the rest (Fisher exact p = 0.00138, and the gap holds inside all
four rules that have both). Unanimity there is the signature of a reflex, not of
evidence. **This did not replicate in code** (§5), so the rule is "do not filter
by agreement", not "prefer disagreement".

**Adjudication — deterministic, or it does not block.**
Each finding must be reduced to something the DCL can execute — in code a test,
a property, an assertion; in research a provenance, structure, unit or citation
check, which the DCL already runs. An executed check has a truth value that does
not resample. What cannot be reduced is ranked evidence for a person, not a stop.

**Disposition — a function of evidence, not a model's verdict.**
Executed failures block, as today, deterministically. Unexecuted findings
escalate or report, per the existing `authority.lone_model_blocker` dial.

The invariant today is *"a failed deterministic check blocks whatever the model
says."* The proposal extends it to *"only a failed deterministic check blocks."*
The rung order does not move, the ladder is not rewritten, and the kernel is
untouched: the model still proposes and code still decides. There is already one
shipped instance of exactly this shape — A4's `governed_source_ids` paired with
`check_source_provenance`.

## 4. What this costs, and what it gives up

It gives up the model's power to hard-stop work on its own. Measured, that power
is a coin flip 30% of the time. What replaces it is escalation — the
Observe-shaped default D142 declined to adopt on argument alone, now with a
number attached. It ships as a dial with the default unchanged, and the default
moves on measurement, per D144.

Detection at K draws costs K×. The argument first written here — that detection
is the cheaper half of the problem, so the detectors need not be the expensive
model — **was measured and is wrong**: three draws of the cheap tier cost 1.9× a
single shipped draw and found less (16.4% against 20.0% recall, 9.5% against
6.8% false positives), one of only two dominated specs in the exploration grid.
Whatever the literature says about enumerating being easier than judging, this
auditor's cheap sibling does not enumerate well enough to be worth its calls.
Against that, one cost does disappear: the adjudicator model agreed with the
deterministic mapping on **130 of 130** findings it mapped, so on this
constitution it buys nothing but latency and rate-limit failures.

## 5. What is not established, stated before anyone builds on it

- **The prose "free lunch" is an artifact and I withdrew it before it became a
  finding.** Union of K appeared to raise recall *and* precision in prose. But
  98 of 120 rubric items in that sample were wrong, so a randomly named item is
  81.7% likely to be correct-to-flag; the apparent precision gain is dilution
  against a high base rate. In code, with model-free ground truth, union of 2
  buys +2.4 recall for +2.3 false positives — proportional, no free lunch. The
  recall gain is real in both domains; the precision gain is not.
- **The anti-corroboration result is prose-only.** In code, intersection improved
  the recall-to-false-positive ratio rather than worsening it. Do not build a
  tier on it.
- **Whether the auditor can write a discriminating executable check at all is
  unknown**, and it is the load-bearing assumption. The pre-test is running now
  over the 56 stratum-P solutions, preregistered kill condition: **fewer than one
  third producing a runnable, discriminating check ends this proposal.**
- **A wrong executable check is worse than an opinion**, because the
  deterministic layer will act on it without hedging. The pre-test measures that
  rate too.
- Everything above about prose is one task, one 50-row corpus, one vendor pair,
  and a CLEAR reimplementation. See `benchmarks/CORRECTIONS.md`.

## 5a. The line that survives the kill

The pre-test drew a boundary sharper than the proposal it killed.

The product already ships one place where a model's output becomes deterministic
evidence: A4's `governed_source_ids` with `check_source_provenance`. There the
model **names** a piece of evidence and code verifies that it **exists**. The
model is never asked what the evidence will say. That boundary held; it is
untouched by anything measured today.

The withdrawn proposal crossed it. It asked the model to supply the predicate
**and its expected value** — to state what the evidence will say — and that is
the step it gets wrong a quarter of the time (25.4% of runnable checks, CI
18.8–33.4%, fail on the known-correct solution). The same instinct that finds a
good edge case invents a specification to go with it, and no prompt separates
the two, because they are one act.

So the rule is: **ask the model to name evidence, never to state its value.**
A model may say "the claim on line 40 rests on source 7"; code checks that
source 7 exists and is governed. A model may not say "`f('')` returns `False`"
and have code enforce it. Every future proposal that turns a model's output into
a non-overridable block is checked against this line first.

One more thing the pre-test showed, which reframes D154: execution did not
remove the resampling, it moved it. Zero of 56 replies were byte-identical
across runs; the executed outcome agreed on 54 of 56, but *which correct code
got blocked* flipped on 8 of 56. Determinism downstream of a sampled proposal is
a stable answer to an unstable question.

## 6. What stands

Take the withdrawn proposal, remove the part that asked the model for a truth
value, and what remains is measured and is the design:

- **Detection is wide and unioned.** Every source that can look, including the
  generator's own model, which is the best detector measured. Union; never
  filter by agreement. The recall gain is real in both domains, at a
  proportional false-positive cost — no free lunch, and the cost is the number
  the exploration loop is now pricing under a preregistered constraint.
- **The adjudicator model is dropped.** 130 of 130 agreements with the
  deterministic mapping; it bought latency and rate-limit failures.
- **A model-only finding does not stop work by itself.** It is ranked evidence,
  and the existing `authority.lone_model_blocker` dial decides whether it drives
  a revision or a person. That dial's default is the owner's call (D144, D154);
  what engineering supplies is that the automatic stop it would replace is a
  coin flip 30% of the time.
- **The DCL is the only thing that blocks on its own**, exactly as today. The
  invariant does not change; what changes is the recognition that the model
  rung cannot be made to join it by handing it an `assert`.

What this does not do is raise the ceiling on what the audit can *prove*. Every
measured architecture is still an opinion about text, and the only measured way
to move recall by more than a few points — telling the auditor what to look for,
+21.5 pp — is a referent, not a structure. The next architectural question is
therefore not "how should the model look" but "what can be handed to it that is
already known to be true", and that is a product question about what a project
can supply, not an audit question.
