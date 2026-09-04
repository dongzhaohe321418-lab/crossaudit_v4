# What every CrossAudit study must record

These measurements are intended for publication. A reader who has never seen this
repository must be able to judge whether a number means what it says, and a
reader with the same keys must be able to reproduce it. That is a higher bar
than "the report explains the result", and it is the bar every study here meets
from now on, including retrospectively.

Nothing in this file is about presentation. It is about what must exist on disk
when a study finishes.

## 1. The claim, written before the run

A study states, before any model is called and in the committed plan:

- the hypothesis, in a form that can come out false;
- the primary outcome — **one** number, named in advance;
- every secondary outcome, also named in advance;
- the arms, what differs between them, and what is held fixed;
- the intended n per arm and why that n;
- the stopping rule (budget, wall clock, or completion).

A number promoted to "the result" after the fact is a different kind of claim,
and it is labelled exploratory wherever it appears.

## 2. Provenance — enough to reconstruct the run

Committed in a machine-readable `manifest.json` per study:

- **code**: the frozen commit sha, and `git status --porcelain` proving the tree
  was clean at freeze; the sha of every file the study itself added;
- **data**: dataset name, version or revision, per-file sha256, row counts, and
  the licence;
- **models**: every model id used and in what role (generator, auditor, extractor,
  judge, adjudicator), the provider and base URL, the sampling parameters, and
  the reasoning-effort setting;
- **seed**: the seed and how instance selection derives from it;
- **time**: UTC start and end of each arm;
- **environment**: Python version, the OS, and the versions of any package the
  measurement depends on.

## 3. Raw records, not just summaries

One **JSONL row per instance per arm**, committed, containing every measured
quantity — never a summary alone. At minimum:

    instance id · arm · round · outcome score(s) · every component the score is
    built from (per-item correct/incorrect, not just the F1) · findings raised,
    with rule, severity and the item each maps to · verdict · tokens in/out ·
    cost · wall time · prompt sha256 · response sha256

**Never commit corpus text, model outputs that contain it, or prompts that embed
it.** Hashes, ids, scores and counts are derived values and are safe; that is
what the record is made of. A study that cannot record its evidence without
redistributing the corpus records the hashes and says where the originals live.

Keep the full run directories on disk and record their absolute paths and a
directory-level sha256 manifest in the report, so the raw material can be
produced on request even though it is not published.

**Not in a temporary directory.** Session scratchpad lives under `/private/tmp`
and the system clears it. The run directories for every study to date are
archived at `~/Documents/Crossaudit/study-data/`, with a per-file manifest
beside them and the directory-level digests committed here as
`ARCHIVE_MANIFEST.json`. Several published numbers have already been re-verified
from that archive, and several planned analyses are replays over it that would
otherwise cost roughly ten times as much.

## 4. Analysis stated so it can be checked

- the test used, and why it suits the data (paired vs unpaired, the distribution
  assumption, the tie handling);
- the **effect size with a confidence interval**, not only a p value;
- the exact p, not a threshold;
- **n for every cell**, including cells that shrank because a run failed;
- the number of comparisons the study made in total, and whether the primary
  outcome was one of them or was selected after looking — this project has now
  run several studies over one task, and that history is part of the multiple-
  comparison picture;
- the noise floor: what the same configuration does when run twice. A difference
  smaller than the run-to-run spread is not a finding, whatever its p value.

## 5. Deviations, in full

Every departure from the plan, listed and numbered, including the boring ones:
a resumed run, a substituted model, a failed API call, a changed timeout, a
sample that errored and was dropped. State for each whether it could bias the
result and in which direction. A study that reports no deviations is a study
that was not watched closely enough.

## 6. Limitations, stated by the author, not left to the reader

At minimum, and permanently, for this project:

- **The CLEAR scorer is a reimplementation from the paper.** The authors released
  no evaluation code, so it has never been diffed against theirs. The only
  external check is that this implementation places frontier models where the
  paper places them on the same task. Any claim resting on CLEAR inherits this.
- **A model-judged ground truth is not ground truth.** Where the outcome is
  scored by a model, say so in the same sentence as the number. Where an outcome
  can be measured without a model — a test that passes or fails — prefer it, and
  say that you did.
- **One task is one task.** A finding on a single domain is a finding about that
  domain until it is repeated elsewhere.
- **Vendor independence is not statistical independence.** Two models from
  different vendors share training data, architecture and human feedback
  conventions. "Cross-vendor" reduces correlated error; it does not create an
  independent oracle, and no number here should be read as if it did.

## 7. Cost

Tokens and money per arm and per instance, from the usage ledger rather than
reconstructed. Where a figure is reconstructed, say so at the figure.

## 8. Reproduction

The exact command, with the environment it needs, that regenerates the study
from a clean checkout at the frozen sha — including how to obtain the dataset,
which this repository does not redistribute.

## 9. A number keeps its interval wherever it travels

Sections 1–8 govern the study. This one governs every later use of its results.

The reports in this project have generally been careful at the point of
computation and careless at the point of quotation: a rate of one-in-one was
published as "100% (1/1), 95% CI [20.7%, 100.0%]" and then travelled into
planning documents as "100%". A second failure is subtler and cost more: a "2.6-point noise floor"
was real and measured, but measured on fixed drafts, and was then applied to
studies in which generation changed. A number carried away from the estimand it
was computed on is as wrong as one with no source. See `CORRECTIONS.md`, whose
own first version got this wrong in the other direction.

So, binding on summaries, decision records, plans and prose, not only on reports:

- A rate quoted without its interval is a defect, the same as a p value quoted
  without its effect size. `73%` and `73% (CI 45–92%)` are different claims.
- A count small enough that its interval reaches an absurd bound is quoted **as
  the count**: "2 of 2", never "100%".
- "Inside the noise floor" may only be written where a replicate arm exists
  **for the same estimand**, and it names the measured spread. A floor measured
  on fixed drafts does not bound a study that changes generation. Without a
  matching replicate the honest form is "run-to-run variation is unmeasured for
  this contrast".
- A claim inherits the narrowest scope of its evidence. An arm that varied a
  model within one vendor licenses a within-vendor statement, whatever question
  it was run to answer.
- When a later study supersedes an earlier number, the earlier number is
  withdrawn in writing, in `CORRECTIONS.md`. A superseded figure that is merely
  not repeated will be repeated.
