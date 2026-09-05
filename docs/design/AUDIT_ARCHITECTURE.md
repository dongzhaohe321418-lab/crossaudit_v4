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

## 3. The proposal: nothing blocks that was not executed

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

Detection at K draws costs K×, on the cheaper half of the problem: the literature
puts judging well above enumerating in difficulty (+0.29 F1, stable across a 24×
parameter range), so the detectors need not be the expensive model. Against that,
one cost disappears: the adjudicator model agreed with the deterministic mapping
on **130 of 130** findings it mapped, so on this constitution it buys nothing but
latency and rate-limit failures.

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

## 6. If the pre-test kills it

The design degrades rather than collapsing. Without executable checks, what
remains is still an improvement on today and is fully measured: union-of-K
detection including the generator's own model, no agreement filter, the
adjudicator model dropped, and the verdict routed to escalation rather than an
unstable automatic stop. That buys recall and a stable disposition without
requiring the model to produce anything it has not already been shown to produce.
