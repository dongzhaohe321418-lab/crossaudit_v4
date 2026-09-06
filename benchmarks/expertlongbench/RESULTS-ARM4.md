# Arm 4 — the shipped check and the shipped skill, on a fresh sample

Study 8. Preregistered at `benchmarks/expertlongbench/study8/PREREGISTRATION-ARM4.md`,
committed at `1259e22` **before any study model call** (one harness fix at `43ac13d`,
before the first call: a recursion in the bootstrap wrapper). n = **26 T03
instances × 1 arm = 26 drafts** — every corpus row not in Arm 3's plan, excluded
by id, no seed. Generator `anthropic:claude-sonnet-4-6`, auditor
`openai:gpt-5.6-terra`, one round, `checks: ["number_source"]`, the **shipped**
skill (`scaffold.annotation_skill_tree`), the **shipped** contract sentence, the
**shipped** per-row verifier (`numbers._row_findings`), matcher blob
`8dfd07d9c17031a839513db732bc0d760d3ea50a` (the merge of slice 3, a17109e).
All 26 drafts completed; the receipt's `inputs.manifest` equals the reconstructed
increment on **26 of 26**. Spend **$1.9834** of a $3.00 budget.

D160 ruling 2 asked this arm one question: does the check that now ships block so
few correct annotations that it may enter a default profile?

---

## 1. The §8g disposition, and the decision

> **Among BLOCKABLE annotation rows whose named location genuinely contains the
> transcribed `(v, u)` pair — adjudicated by the frozen gold rule, applied by two
> labellers blinded to each other and to the verdict — the fraction the shipped
> check BLOCKS.**

| false-blocker rate | 95% Wilson score interval for that binomial proportion of annotation rows | draft-clustered 95% percentile bootstrap, 10,000 resamples of the 26 drafts | **§8g** |
|---|---|---|---|
| **9 of 189 = 4.76%** | **2.53–8.80%** | 1.00–9.83% | **KILL** |

The rule fixed before the run — *kill if the interval's lower bound exceeds 2%;
pass only if the upper bound is below 5%; anything between is inconclusive* —
reads **KILL**: the lower bound is 2.53%. **`number_source` enters no profile**
(§9 of the preregistration; D159 ruling 2 stands).

**Adjudication.** 60 items on the blinded sheet — every one of the 10 blocks, and
50 of the 180 passes drawn at seed 20261106 — labelled by L1 (the author's
session) and L2 (`gpt-6-astra` through `codex exec`, read-only, the sheet and the
rule only). **κ = 1.000 on the labels, 60 of 60 agree**; no label adjudication was needed
(`study8/L1-arm4.csv`, `L2-arm4.csv`, `GOLD-arm4.csv`). The cited **rule codes
differ on 7 items**: six where a unit is written without a space before it (L1
cited the whitespace fold R4, L2 the identity R2 — the same reading by two
routes) and one hyphen row (L1 R6, L2 R9). `GOLD-arm4.csv` carries L1's codes and
lists the seven; the label is the estimand and no label changes under either code. Nine blocks are `C` — the
located line states the pair under R1–R15 — and one is `N` (the value is not on
the line: a generator error, correctly blocked). **50 of 50 sampled passes are
`C`** (Wilson 92.86–100.00%): no false pass was observed in the 50-row sample —
an interval compatible with up to 7.14% non-`C` among passes — so the
preregistered point sensitivity leaves the denominator at 189. `adjudicator_b` (exact substring, `src/`-free) agrees with
the gold on all 60.

**Why the nine correct rows blocked — each read from the archived line, carried
as `mechanism` in `rows-arm4.jsonl`, `CONTAINMENT_RULE.md` §1's labels:**

| mechanism | rows | the shape of the source text, and what the generator wrote (no source text is quoted here: corpus licence) | the design's disposition |
|---|---:|---|---|
| **M2** range | 5 | a range `a–b U` (four temperatures, one length); the generator annotated the first endpoint with the unit, as gold R7 says it may | **E1**, licensed by the gold (W = 0), not yet shipped |
| **M3** list | 1 | two numerals joined by a word with one trailing unit; the generator annotated the first member, gold R8 | **E2**, licensed, not yet shipped |
| **M10** en-dash exponent — a class no earlier arm and not the gold saw | 2 | a unit whose negative exponent is written with an EN DASH (U+2013), transcribed **byte-exact**; the scanner treats an en dash as a boundary and `_EXPONENT_TAIL` names only `-` and `−`, so the token ends before the exponent and the whole unit is never read | **not E6**: E6 is a rendering fold at comparison time, and its licence does not transfer to a tokenisation change; a new extension with its own W = 0 measurement on the gold, which holds no such row |
| **M4** hyphen after the unit | 1 | a unit joined by a hyphen to the following word; the whole-token rule reads unit and word as one token, gold R6 reads the unit alone | the design's "never do: any hyphen split" — a right block by contract that the gold calls a correct annotation; **1 row** |
| M1b | 1 (the `N`) | a value the line does not hold | a generator error; the block is right |

So the KILL is **the containment design's own prediction** (`CONTAINMENT_RULE.md`
§5: "the rule cannot come near 2% on real scientific prose without reading ranges
and subscripts"), now measured on the shipped check with a real generator: **six of
the nine wrong blocks are E1 and E2 — extensions D160 licensed on the gold and
slice 3 did not include; two are a tokenisation class nothing before this arm had
seen; one is a hyphen the design refuses by rule.** With E1 and E2 shipped, the
residue on this sample would be **3 of 189 = 1.59% (Wilson 0.54–4.57%)**; with the
en-dash class read as well, **1 of 189 = 0.53% (0.09–2.92%)** — projections over the
same rows under matchers that do not exist yet, not measurements; the next arm
measures whatever ships.

## 2. Secondary outcomes, as preregistered

| outcome | value | 95% Wilson | draft-clustered bootstrap | note |
|---|---|---|---|---|
| **`uncited` rate** over all rows | **16 of 206 = 7.77%** | 4.84–12.24% | 2.75–13.81% | between Arm 3's A (10.68%) and B (6.80%); no materiality threshold was preregistered and none is claimed |
| resolved over blockable rows | 180 of 190 = 94.74% | 90.58–97.12% | 89.60–98.80% | Arm 3 B: 85.5% blockable |
| ambiguous (quote on more than one line) | 0 of 190 | 0.00–1.98% | 0.00–0.00% | |
| quote absent from the file | 0 of 190 | 0.00–1.98% | 0.00–0.00% | all 190 addressed quotations were found in the named file on one line |
| quote across a line break | 0 of 190 | 0.00–1.98% | 0.00–0.00% | |
| unit shortened | 1 of 190 = 0.53% | 0.09–2.92% | 0.00–1.69% | one row transcribed a strict prefix of the source's unit token |
| annotation rate | 206 rows / 600 numbers present = 34.3% | | | Arm 1's `NUM` extractor over the fence-stripped draft |
| cost per draft | $0.0763 (total $1.9834: generator $1.5412, auditor $0.4422) | | | Arm 3: $0.0628 |
| malformed-envelope re-ask | 13 of 26 drafts | | | counted, not fixed (Arm 3: 7 of 48 rounds) |
| advisory rows | 16 (all `uncited`) | | | no ambiguous row |
| matcher version | one blob id in every row | | | `8dfd07d9…` |

**Every block reason was `pair-not-in-location`.** No row was malformed,
unresolved, absent, cross-line or ambiguous: the addressing contract (D159) held
on 190 of 190 addressed rows, and the whole of the false-blocker rate is the
containment rule meeting source text it does not read.

## 3. What this licenses, and what it does not

* **Licensed:** `number_source` stays out of every profile (D160 ruling 2). The
  addressing half of the contract held on this sample — 0 of 190 absent, cross-line
  or ambiguous, Wilson upper bound 1.98%. The next change is the containment half:
  **E5 + E6, then E1, then E2**, in D160's order, each against the frozen gold with
  W = 0, and a new extension for the en-dash exponent with its own gold rows, then
  **Arm 5** on a further fresh sample (the corpus has
  none left in T03: 50 rows, all now used — Arm 5 needs another task's corpus or
  a re-run on Arm 3's 24 with the changed matcher, stated as such).
* **Not licensed:** the 1.59% and 0.53% projections. They are the same rows
  re-read under matchers that do not exist yet.
* **A finding beside the estimand:** the en-dash exponent is a tokenisation class
  (M10) neither the gold nor Arms 2–3 contained; the gold saw the U+2212 minus and
  the superscript forms only. It does not inherit E6's licence and needs its own
  rows and its own W = 0.

## 4. Deviations from the preregistration

None in the estimand, the rule, the sample, the adjudicators or the budget. Two
to state:

1. A harness defect was fixed before the first model call (`43ac13d`): the first
   attempt recursed in the bootstrap wrapper, which runs before any model call in
   the harness's own order, and its directory was deleted. That order is the only
   evidence; the deleted directory's ledger was not kept, so "no API call" is not
   independently checkable from the committed records.
2. `plan.json` records `git_status_at_start: "?? scratchpad/"` — an untracked
   directory in the worktree, outside the code and the records, present when the
   run began. The code sha is `43ac13d` and the matcher blob is in every row; the
   untracked directory is stated here because the freeze standard is a clean tree.

The preregistration says "n = 26" and 26 ran.

## 5. Reproduction, records and archive

```sh
export PYTHONPATH=<worktree>/src
set -a && . ~/.crossaudit-keys.env && set +a
python3 benchmarks/expertlongbench/provenance_arm4.py --out <abs>
python3 benchmarks/expertlongbench/study8/arm4_sheet.py --runs <abs> --out <sheet-dir>
python3 benchmarks/expertlongbench/provenance_arm4_report.py <abs> --json <abs>/report.json
python3 benchmarks/expertlongbench/study8/emit_records_arm4.py <abs>
```

* Code at `43ac13d` for the run; the sheet, report and emit scripts at the
  commit of this file. Python 3.13.5, darwin.
* Corpus `T03MaterialSEG.jsonl` sha256 `0b525eae…`, 50 rows, CC BY-NC-SA 4.0 —
  **not redistributed and not committed**.
* Committed, corpus-free: `study8/rows-arm4.jsonl` (206 rows: digests, lengths,
  addresses, dispositions, reasons, adjudications, gold label, mechanism, matcher
  version), `study8/manifest-arm4.json`, `study8/key-arm4.jsonl`,
  `study8/L1-arm4.csv`, `L2-arm4.csv`, `GOLD-arm4.csv`.
* Archived, not committed: drafts, project trees, ledgers and the labelling
  sheet under `~/Documents/Crossaudit/study-data/wt-arm4-runs/`
  (`MANIFEST.json` entry `wt-arm4-runs`).
