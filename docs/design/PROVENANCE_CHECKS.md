# Three provenance checks in the deterministic layer

A design study for D155's surviving rule — *a model may name evidence; code
verifies it exists and says what was claimed; a model never states what the
evidence will say* — applied to the three checks the owner approved on
2026-09-05 (`docs/RESTART.md`, 下一步 §0): **number → source**, **figure →
generating code**, **claim → citation**. Nothing here is built; no model was
called; §6 names the script behind every number.

**The conclusion that shapes everything below.** A locator that names a *file*
is not enough. On the 16 T03 drafts already in `study-data/`, a **wrong** source
file contains the claimed (value, unit) pair **27.7%** of the time (596 of 2150
draws); a locator naming a *line* has a coincidence rate of **0.0%** (0 of
1825). File-scoped annotation would let a plausible-but-wrong citation pass a
quarter of the time — the inverted-executable-check failure in a new costume.
**Every contract below names a span, not a file.**

Not claimed: that any check raises audit recall (§6 tests only soundness and
whether a generator can name a line); that check 3 can be completed (§3.3: it
cannot, today); that any number generalises past one task, one 50-row corpus,
one vendor pair, 16 drafts (`benchmarks/CORRECTIONS.md`, "Withdrawn framing").

## 1. What exists today, and the exact size of the gap

| verb | shipped where | covers |
|---|---|---|
| a model **names** a location | `dcl/builtin.py:82-99` (`units`: every `results.json` quantity carries `unit` and `source`); `dcl/provenance.py:31` (A4's ` ```crossaudit-sources ` fence) | JSON quantities; declared citations |
| code verifies it **exists** | `dcl/neutral.py:71-99` (`declared`, CA-FILE-002: every yaml `inputs`/`sources`/`requires`/`depends_on` local path is in scope); `dcl/provenance.py:67-73` (CA-SOURCE-001: every declared id is in the governed set) | yaml declarations; citations |
| code verifies it **says what was claimed** | **nowhere** | — |

`dcl/builtin.py:127-163` (`provenance`, CA-DATA-003) sits between the first two:
a quantity's `source` must be an *exact member* of `metadata.yml` `inputs`, but
the file is never opened and the value never looked for. So `provenance` gives
membership and `declared` gives existence — and **no shipped profile contains
both** (`dcl/profiles.py:24-31`), so under `checks: science` a quantity may name
`data/runs.csv@v3` that is listed in `metadata.yml` and does not exist. One line
in `profiles.py` closes that, and it is worth fixing on its own.

### 1.1 A4, precisely

The contract is ` ```crossaudit-sources `, body a JSON array of 64-hex source
ids (`dcl/provenance.py:31`, documented at `README.md:1069-1074`). "Governed"
means a `tool_result` row for `web_fetch`/`paper_search`
(`receipt/sources.py:32`) with `status == "succeeded"`, whose
`payload["source_ids"]` are unioned at check time over the **live** ledger
(`receipt/sources.py:84-107`); `web_fetch`'s id is `digest({"content": text})`
over the extracted text (`broker/tools_research.py:292-297`), `paper_search`'s
is over public identity only (`:154-163`). The context is built only when the
check is enabled (`auditor/run.py:254-259`, `cli/main.py:839-842`) and consumed
via `wants_context=True` (`dcl/framework.py:201`).

**Who tells the generator to emit the fence: nobody in this codebase.** It
appears nowhere in `generator.py` or `constitution.py`, and no `brief_projection`
module exists. `README.md:1079-1081` states the mechanism: "A `research` project
asks the generator to emit that block (via a house skill or the task's acceptance
criteria)." The house skill is the shipped vehicle (`skills.py:1-27` — committed,
hashed into the receipt, shapes the generator, never reaches the auditor).
**That is the right home for all three contracts below, and it needs no change
to the generator or the constitution.**

### 1.2 The structural blocker for check 3

**The fetched text is not retained anywhere.** The broker copies only a tool's
declared `evidence_fields` into the ledger (`broker/__init__.py:170-177`), and
neither `web_fetch`'s `text` nor `paper_search`'s results are in those tuples
(`broker/tools_research.py:368-369`, `:376-377`). No content cache exists; the
raw text is returned for one turn's in-context use (`broker/routing.py:282-306`)
and is then gone. So for a governed external source **code cannot re-read the
bytes and therefore cannot verify "contains support" at all** — not because the
property is semantic, but because the evidence is absent. It is a deliberate
invariant (`broker/registry.py:40-43`); §3.3 prices changing it.

## 2. The annotation contract

One shape for all three: one thing to learn, one parser. **A locator is a span,
never a file, and never a value.**

    <path>[@<blob-sha>]#L<start>[-L<end>]      an in-increment span
    governed:<64-hex id>#"<quoted span>"       a governed source
    computed:<path>#L<start>[-L<end>]          a value this run produced
    uncited                                    no source named

`uncited` is not a truth value: it is the generator declining to name a location
— a fact about the annotation, not a claim about the world. It never blocks.

### 2.1 number → source

One fenced block per text artefact containing numbers:

````markdown
```crossaudit-numbers
[{"v": "950", "u": "°C", "at": "#L14", "src": "work/synthesis/RECIPE.md#L11"},
 {"v": "1",   "u": "h",  "at": "#L14", "src": "work/synthesis/RECIPE.md#L11"},
 {"v": "180", "u": "°C", "at": "#L9",  "src": "uncited"}]
```
````

`at` is a span in the enclosing file, `src` a locator. **No field carries a
truth value**: `v`/`u` transcribe bytes the generator itself wrote, `at` and
`src` are addresses; it is never asked whether 950 °C is correct, nor what
`RECIPE.md:11` says. Structured quantities reuse the shipped format unchanged —
a `results.json` `source` (`dcl/builtin.py:82-99`) goes from `path@revision` to
`path@revision#L…`, additive, and old values keep passing the shipped check
(`dcl/builtin.py:155`, `src.rpartition("@")`).

### 2.2 figure → generating code

In `metadata.yml`, beside the `inputs` list `check_schema` already requires
(`dcl/builtin.py:59-68`). Every field is an address or an argv; nothing asks what
the figure shows or what the script will print.

```yaml
figures:
  - path:    work/fig/yield.png
    code:    work/analysis/plot_yield.py@e3b0c442…
    inputs: [work/data/runs.csv@a94a8fe5…]
    command: ["python", "work/analysis/plot_yield.py"]
```

### 2.3 claim → citation

**A4's fence is the contract; reuse it verbatim.** The id array in
` ```crossaudit-sources ` (`dcl/provenance.py:31`) is unchanged; the only
addition is an optional per-claim block whose quoted span transcribes bytes the
generator read — not a paraphrase, not a judgment. Code checks byte-equality,
and §3.3 says when it can.

````markdown
```crossaudit-claims
[{"at": "#L22", "src": "governed:9f86d081…#\"calcined at 810 °C for 36 h\""},
 {"at": "#L31", "src": "work/papers/li2023.txt#L204-L206"}]
```
````

## 3. The verification, deterministically — and where determinism ends

### 3.1 number → source

*Exists* = `src`'s path is a key of the `files` mapping the DCL is handed
(`dcl/framework.py:172`) and the line range is inside it. *Says what was claimed*
= the normalised (value, unit) pair occurs **within the named span**.

```
src == "uncited"         -> ADVISORY, counted                        (§3.4)
src startswith computed: -> defer to §3.2
path not in files, or declared sha mismatch -> BLOCKER CA-NUM-001
normalise(v,u) not in extract_pairs(span)   -> BLOCKER CA-NUM-002
a number with no annotation row             -> ADVISORY, counted
```

`normalise` is a fixed synonym table (`hours→h`, `minutes→min`, `wt %→wt%`,
`µm→μm`, …). **Load-bearing, and measured**: without it, 8 of 430 T03 draft
numbers (1.9%) fail on unit rendering alone while naming the right line — eight
spurious non-overridable blockers per 16 drafts.

**Where determinism ends.** "Contains this number" is exact for a table cell, a
CSV field, a JSON value, a short structured span. It is *not* exact where the
source states the value in another form — "a third" for 0.33, "an hour" for
60 min, a value read off a plot, a rounding. The check must not attempt these:
such a number is annotated `uncited`, lands in the evidence tier, and the
auditor may raise it under the existing `lone_model_blocker` dial
(`auditor/authority.py:243-247`). **It never blocks.**

### 3.2 figure → generating code

*Exists* = `path`, `code` and every `inputs` entry are keys of `files`, each
declared blob sha equalling `sha256` of the committed bytes. *Says what was
claimed* — three tiers, only the first two of which may block:

| tier | statement | deterministic? |
|---|---|---|
| **A. pinned** | figure, script and inputs are all in the increment at exactly these bytes | yes — hashes over committed bytes |
| **B. executed** | a `run_check` `tool_result` in this run's ledger has `command == command` and `exit_code == 0` | yes — argv and exit code are ledgered (`broker/tools_command.py:108`) |
| **C. reproduced** | re-running `command` in a clean checkout emits a byte-identical figure | **no** |

Tier B is today's ceiling and is lower than it sounds: `run_check` runs an argv
in the project root and **anything it writes to disk is not ledgered** — only
`file_write` produces a path/`post_sha256` record (`broker/tools_write.py:182`),
and a subprocess bypasses it. The ledger can say *this command succeeded during
this run*, never *this command produced this figure*, and the contract string
must say so in those words. The causal link is tier A's hash pinning plus the
human-approved argv.

Tier C must not ship as a blocker. Re-execution is deterministic only if the run
is repeatable, and figure pipelines commonly are not: PNG metadata carries a
creation date unless suppressed, fonts render differently across environments,
unseeded RNG and thread-scheduled float reduction differ across runs. A mismatch
would be a non-overridable BLOCKER on correct work — the shape D155 exists to
prevent. Evidence tier, opt-in, never the ladder.

### 3.3 claim → citation

**In-increment source** (a committed paper text, a dataset, a prior report):
identical to §3.1 with a string instead of a number. *Exists* = path in `files`;
*says what was claimed* = the quoted span is a byte-exact substring of the named
line range after whitespace normalisation. **Available today, no kernel change.**

**Governed external source**: A4's shipped half — the declared id is in
`governed_source_ids` — is unchanged (`dcl/provenance.py:67-73`). The second
half is **not implementable today**, because the fetched text is never retained
(§1.2): check 3's remainder is blocked by absent bytes, not by semantics.

*What would have to be true.* `web_fetch` would have to retain its extracted
text where code can re-read it; because the source id is exactly
`digest({"content": text})` (`broker/tools_research.py:292-297`), a check could
recompute the id from the retained bytes and confirm the quoted span is a
substring — deterministic, and stronger than "the id was fetched". Two homes,
neither free. **In the increment** (`work/sources/<id>.txt`, committed): `verify`
re-derives it from committed bytes, which is what the brief asks — but
third-party text enters the repository, a licensing and privacy decision rather
than an engineering one, and this project's own corpus (CC BY-NC-SA, no
redistribution) is the standing example of why. **In a gitignored cache**: no
licensing change, but the evidence is not in committed bytes, so `verify` cannot
re-derive the finding.

**Recommendation: do not build the governed half.** Ship check 3 over
in-increment sources only, leave A4's governed half as it is, and put retention
to the owner separately with its licensing cost stated — saying which half is
honest, as A4's docstring already does (`dcl/provenance.py:16-20`).

### 3.4 The rule that keeps all three on the right side of D155

**Only a named locator can block.**

| the generator did | disposition |
|---|---|
| named a locator that does not resolve, or resolves without containing the value | **BLOCKER**, CONFIRMED (`dcl/framework.py:92`) |
| annotated `uncited` | ADVISORY, counted, carried to the auditor |
| left a number/claim/figure unannotated | ADVISORY, counted, carried to the auditor |

A document with no annotations passes vacuously — A4's shipped rule
(`dcl/provenance.py:19-20`): these checks enforce *declared* provenance, not
*coverage*, and coverage is a model judgment.

## 4. Fit to the DCL

Three registry entries — `number_source` (`wants_context=False`), `figure_code`
and `claim_citation` (both `True`). No new subsystem; no change to `auditor/`,
`broker/`, `ledger/` or `policy/` semantics.

**Profiles** (`dcl/profiles.py:24-31`) — additive, `general` untouched, so no
existing project changes behaviour: `science` gains `number_source` and
`figure_code`, `research` gains `number_source` and `claim_citation`, plus §1's
`declared`/`provenance` fix.

**CheckContext** (`dcl/framework.py:68-77`) gains two defaulted fields, leaving
every existing caller unaffected: `run_commands` (`(argv, exit_code)` pairs from
succeeded `run_check` tool_results) and `source_texts` (empty unless §3.3's
retention decision is made). The guard at `auditor/run.py:255` widens from
`"source_provenance" in cfg.checks` to any of the four names — one condition,
additive; `cli/main.py:840` takes the same edit.

**Lifecycle.** Findings are `Finding(BLOCKER, "CA-NUM-002", path, …)` with the
default `state=CONFIRMED` (`dcl/framework.py:87-92`), counted by `hard_failures`
(`:111-113`), read by the ladder at `auditor/run.py:441-442` **before** any model
reply — so a deterministic blocker means the model's verdict is never reached
(`:457-459` sits in the `elif` chain below it).

**Receipt.** No schema change. Findings reach `records_from_audit` with
`producer="check:number_source"` and `producer_digest=dcl_digest`
(`auditor/authority.py:202-203`); a CONFIRMED BLOCKER becomes a
`blocking_evidence_id` (`:252-253`), validated by `validate_block` and
re-derived by the verifier (`receipt/verify.py:469-478`). **The new module's own
bytes are bound for free**: `dcl_source_digest` hashes every `.py` under
`crossaudit/dcl/` (`auditor/run.py:112-157`) into `inputs.dcl_source_sha256`
(`receipt/build.py:198-209`), so a later `verify` proves *which version of the
check* produced the block — subject to the limit true of every check, that
`verify` re-derives bindings rather than re-running them
(`receipt/verify.py:384-583`).

**Repair guard.** No change — it screens the staged diff
(`repair_guard.py:522-633`, wired at `cli/build.py:1076-1118`) and is decoupled
from the registry. One later slice: *deleting an annotation row* is this check's
`assert`-deletion, and belongs in that pattern set.

**Mutations (D64 — a guard is specified with its mutation),** each named in its
docstring per `tests/test_repair_guard.py:3-7`:

| check | mutation that must redden it |
|---|---|
| `number_source` | change `#L11` to `#L12` where the value lives on L11 → CA-NUM-002 |
| `number_source` | delete the unit-synonym table → the `hours`/`h` fixture reddens |
| `number_source` | widen the span check to whole-file → the wrong-line fixture goes **green** (proves the span, not the file, is what is checked) |
| `figure_code` | flip one byte of the fixture `.csv` without updating its declared sha → CA-FIG-001 |
| `figure_code` | drop the `exit_code == 0` clause → the failed-run fixture goes green |
| `claim_citation` | alter one character inside the quoted span → CA-CITE-001 |
| all three | remove the check from the profile → the profile test reddens by name |

## 5. What breaks it

**1. A generator that annotates everything with a plausible-looking but wrong
location** — the inverted-executable-check analogue, and the reason for §2's
span rule. Two things separate it from what killed the withdrawn proposal.
*Direction*: a wrong assertion blocks correct work, whereas a wrong locator
fails against the generator's own annotation — the annotation is condemned, not
the artefact. *Residual, measured*: file-scoped, a wrong source contains the
claimed pair **27.7%** of the time (596/2150); line-scoped, **0.0%** (0/1825).
Right behaviour, and only because the locator is a span.

**2. A number that legitimately has no source.** Not an edge case: **13.3%** of
T03 draft numbers (57 of 430) do not occur in the source at all, and reading them
shows what they are — melting points, ionic radii, decomposition and boiling
temperatures: parametric recall, the class most likely to be wrong and least
likely to be checkable. Routed to `uncited` → ADVISORY → the auditor's prompt;
**it does not block**. Right: blocking would make the product refuse to state a
well-known constant, and a threshold on the `uncited` count would be an
arbitrary number pretending to be a measurement.

**3. A figure whose code is non-deterministic.** Tier C never blocks (§3.2) and
hashes and a ledgered exit code do not resample, so the check is silent.

**4. A document type where none of this applies** — a memo, a plan, a README.
Two shipped defences: profile gating (`general` unchanged) and vacuous pass. The
failure mode to name out loud is the opposite one: **a project turns the check
on, the generator is never told to annotate, and the check passes every document
while appearing to guard them.** That is live for A4 today (§1.1) — `checks:
research` without a house skill cannot fire. Any slice shipping these three ships
the house skill in `scaffold/templates/` beside them, or it ships a name that lies.

**5. A generator that annotates only what it can source.** Passes; coverage is
not enforced (§3.4). Accepted, and stated in the contract string: "every
*declared* provenance holds", never "every number is sourced".

## 6. The measurement that would decide it

### Arm 1 — the verifier, on bytes this project already has ($0, no model calls)

**Data.** The 16 read-only `armB.round1.md` drafts under
`study-data/wt-revision-runs/armT-scoped/instances/`, against each instance's
source procedure in `benchmarks/expertlongbench/data/T03MaterialSEG.jsonl` — in
a live run, the committed `work/synthesis/RECIPE.md`. 430 numeric claims.

**Primary outcome: the false-blocker rate** — of numbers that do trace to the
source, the fraction the verifier fails. **Kill condition: > 2%**, a
false-positive constraint matching the exploration loop's preregistered shape,
because a non-overridable blocker on correct work is the failure this line
exists to avoid. *Already run*: the naive matcher fails 8 of 373 traceable
numbers (**2.1%**) on unit rendering alone — **killed as specified**. The
synonym table takes those 8 to 0, which is why it is in the algorithm and the
mutation list, not a footnote.

**Secondary outcome, which decides the contract's shape:** the coincidental-pass
rate — how often a *wrong* locator still contains the claimed pair. Measured:
file-scoped **27.7%** (596/2150, 5 wrong-source draws per number); line-scoped
**0.0%** (0/1825, 5 wrong-line draws per traceable number; mean 11.4 source
lines per file). Preregister the line-scoped rate at **≤ 5%**; above that the
check cannot tell a careless annotation from a careful one and has not earned a
blocker. Reproduce in ~2 s, no keys, network or model, from a checkout holding
the gitignored corpus (or with `CROSSAUDIT_T03_CORPUS` set):
`python3 benchmarks/expertlongbench/provenance_probe.py`.

### Arm 2 — the generator, with the annotation skill (≈$3, 16 instances)

Regenerate the same 16 instances with a house skill carrying §2.1's contract,
model, constitution and seed fixed. Archived per-instance cost (`record.json`,
`cost_usd` 0.166 at 2 rounds) puts 16 instances at ≈ **$2.70**.

**Primary outcome:** the fraction of emitted annotation rows that **resolve and
contain** — how often the generator names a location correctly when asked only
to name one. **Kill condition: < 80%.** Below that its blockers are mostly noise
and the check belongs in the evidence tier, not the ladder. That is deliberately
an easier bar than the 33% that killed the executable-check proposal, because
naming a line is an easier act than computing an expected value — and if it
turns out **not** to be, that is the finding, and it kills this the same way.

**Secondary:** the `uncited` rate (expect ≈13%; much higher means the generator
is opting out rather than annotating, a silent failure the check cannot catch);
and draft quality against the CLEAR scorer with its interval, read against study
5B's floor of **SD 1.84 F1** (`benchmarks/CORRECTIONS.md` item 10).

**Not measurable with what this project has.** Checks 2 and 3 have no substrate:
T03 has no figures and no citations, and no archived study produces either.
Their arm-2 equivalent needs a purpose-built project, scoped separately rather
than smuggled into this preregistration. **Cross-vendor review before
publication or before any default moves** (D153): harness, matcher and
statistics go to a different vendor's model read-only, and anything it reports
is reproduced from `study-data/` before it is accepted.

## 7. Cost to the user

**What the generator does extra.** One fenced block per artefact. On the 16 T03
drafts: **26.9 numbers per draft** (median 22.5, max 62), a block of **≈2.0 KB**
(median 1.7 KB) against a **6.6 KB** draft — **31% more output bytes**, ≈**511
output tokens** (max 1170). Cents per round; the real costs are latency and
crowding the prose, which arm 2's secondary outcome measures.

**What the user sees when a check fails.** One Do row, one number, no identifier
(`docs/design/ACTIVITY_STREAM.md`, rules 4, 5, 12). Opened, the detail is one
line per failure — the artefact line, the location it named, what was not there;
no rule id, no `CA-NUM-002`, no sha, no check name outside it. The round's
Outcome row is the existing BLOCKED row with its existing count: no new row
shape and no new event kind, satisfying rule 6 by not needing it. The `uncited`
count is a **Note** row — muted, no action, never a badge of zero (rule 3).

    ◆ 已核对来源 · 3 处对不上 · 2 秒                          [›]
    ◆ Checked sources · 3 don't match · 2s                    [›]
      explanation.md:14  names RECIPE.md:11 — "950 °C" is not on that line
    · 4 处数字未注明来源，已交给审计员
    · 4 numbers with no source named, passed to the auditor
