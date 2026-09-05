# Independent cross-vendor review of `fix/skills-not-in-audit` — 2026-09-05

Reviewer: `gpt-6-astra` via Codex CLI, read-only, over 6bf00e6 against
`fusion/evidence-authority`. Commissioned per D153/D156.

Verdict as received: **do not merge**. The two named doors are closed for
canonical paths and no third production route exists; but the loader resolves
the skills directory through the filesystem while the filters compare Git tree
paths, so `SKILLS/` on a case-insensitive host and a symlinked `skills`
directory both put skill bytes in front of the auditor. Also: a skill may be
configured as the constitution; the "no check reads skills" test proves a false
premise (`internal` and `complete-strict` do read a skill body when handed one);
copy omits skills. Receipts verify before and after; no forgery of a normally
recorded receipt. Verbatim below, paths shortened.

---

The two filters close the ordinary lowercase `skills/` routes, but **the claim that no house-skill bytes can reach the auditor is still false**.
Reviewed `6bf00e666fc07783849133fdc887a4f1c28ae560` against `fusion/evidence-authority`. No files changed.
Validation limit: normal pytest execution, including the specifically requested legacy-receipt test, failed during temporary-directory setup because this session is read-only. All eight test functions passed with filesystem, Git, and controller storage adapted in memory. The probes below used production filtering, prompt rendering, checks, and verification; they are not a substitute for a normal-host suite run.
1. **P1 — Case-insensitive skill loading bypasses both case-sensitive filters.**  
   [cli/main.py:297](src/crossaudit/cli/main.py:297), [cli/main.py:1651](src/crossaudit/cli/main.py:1651)
   **Probe:** On a case-insensitive filesystem, commit `SKILLS/house.md` containing the sentinel. `skills.load(root)` accesses that directory through `root / "skills"`, but Git retains `SKILLS/house.md`. Neither `_is_house_skill` nor `prefix_own` excludes it.
   In the in-memory case-insensitive probe, the loader received the sentinel, root-scope audit rendered it, and `run --sha HEAD` audited the uppercase skill itself. I separately confirmed that this host resolves `skills.py` and `SKILLS.py` to the same existing file. This needs a consistent directory-identity policy across loading and exclusion.
2. **P1 — A symlinked skills directory aliases audited work.**  
   [skills.py:83](src/crossaudit/skills.py:83), [skills.py:89](src/crossaudit/skills.py:89), [cli/main.py:1811](src/crossaudit/cli/main.py:1811)
   **Probe:** Make `skills -> work/guidance`, with the sentinel in `work/guidance/house.md`. Commit that setup, then commit an edit only to the target file.
   The loader checks whether each Markdown **file** is a symlink, not whether its base directory is one. It therefore loads the target as house guidance. Full-scope materialisation refuses the committed `skills` symlink, correctly. However, changed-path `run` selects `work/guidance/house.md`; `materialise(..., only=science)` skips the unrelated symlink entry and renders the target bytes. Both outcomes reproduced in memory.
   This is a pre-existing aliasing weakness left open by the claimed boundary fix.
3. **P2 — The Constitution input remains an independent route for a house skill.**  
   [cli/main.py:57](src/crossaudit/cli/main.py:57), [config.py:452](src/crossaudit/config.py:452), [skills.py:16](src/crossaudit/skills.py:16)
   **Probe:** Configure `constitution: skills/house.md`, commit that file with the sentinel, and audit ordinary work.
   Configuration accepts the overlap. The increment filter removes the skill entry, but `_committed_constitution` reads it separately and the sentinel appears inside `CONSTITUTION`. This reproduced through `cmd_audit`.
   This requires explicit owner configuration; it is not silent privilege escalation. Nevertheless, the absolute “Skills never reach the auditor” claim needs either an enforced role-separation rule or a qualification covering this case.
4. **P2 — The “no deterministic check reads skills” test proves a false premise.**  
   [test_skills_are_not_audited.py:324](tests/test_skills_are_not_audited.py:324), [cli/main.py:291](src/crossaudit/cli/main.py:291)
   **Probe:** Pass `{"skills/house.md": b"[broken](missing.md)\nTODO\n"}` to the existing `internal` and `complete-strict` checks.
   They inspect the skill body and produce findings. The new test nevertheless passes because it merely searches Python source under `dcl/` and `auditor/` for the substring `"skill"`.
   An injected, functioning reader using generic `files.items()` also survived the test. Conversely, adding only `# skill` made it fail. Names such as `house_dir` or `guidance` evade it.
   Excluding guidance may be the intended policy, but “no check reads these bytes” and “a test keeps that true” are incorrect explanations.
5. **P3 — Skill-only behavior and its displayed explanation are misstated.**  
   [cli/main.py:1684](src/crossaudit/cli/main.py:1684), [cli/main.py:1703](src/crossaudit/cli/main.py:1703), [test_skills_are_not_audited.py:376](tests/test_skills_are_not_audited.py:376)
   **Probe:** Commit work, then commit only a skill; compare `run --sha HEAD` with plain `run`.
   The explicit-SHA command refuses. Plain `run` searches backward through the existing history window and selects the previous work commit. The test covers only the explicit-SHA case.
   The refusal says “only rules, configuration or ledger,” omitting skills. The executed Chinese translation likewise says “只有规则、配置或账本”. The fallback labels the skill commit “ledger bookkeeping”; that narration is printed directly in English. Console copy at [page.py:5006](src/crossaudit/console/page.py:5006) repeats the same omission in both language catalogues.
6. **P3 — The generator test does not kill every mutation it claims.**  
   [test_skills_are_not_audited.py:141](tests/test_skills_are_not_audited.py:141)
   **Probe:** Filter skills from `gitio.materialise` in memory and run `test_the_generator_still_receives_the_skill`.
   It stays green: the tested generator handoff uses working-tree `skills.load`, not `materialise`. Removing loaded skills or suppressing the generator’s skills block does redden it. The mutation documentation should reflect that distinction.
For the requested route census, there are only two production callers of `run_audit`, at `cli/main.py:1067` and `:1819`. The ordinary root-scoped sentinel results were:
| Route | Result |
|---|---|
| `audit` → `_materialise_tree_scope` → checks/prompt | Sentinel absent, including explicit `--scope .`. |
| `run` → changed paths → enclosure → `materialise(only=...)` | Sentinel absent for canonical `skills/house.md`; alias exceptions above. |
| Console → `appservice.run_loop` → `cli.build.run_loop` → `cmd_run` | No separate reader. With `scope.dirs` omitted, build preflight refuses before generation. Configured runs use the same `cmd_run` seam. Console wiring was traced, not exercised through a browser. |
| Generator revision round | Same `cmd_run` seam. Skills enter the generator at `build.py:703,794–806`; revision cautions become audit notes at `:1153`. No direct Markdown skill-body route found there. |
| Auditor response repair | Reuses the existing prompt plus a fixed repair instruction. Sentinel stayed absent. |
| Escalation/decision paths | State transitions and authorized continuation feed the shared run loop. No independent skill reader found. |
| TUI | Setup/rendering primitives, not another audit pipeline. Nothing found. |
| Working-tree `check` | **Reads the sentinel**, but invokes deterministic checks and emits their result; no auditor call. Probe recorded zero auditor calls. |
| `check --sha` | Uses the filtered scope reader; no auditor call. |
| `_committed_task` | Materialises fixed `TASK.md`; no skill sentinel. |
| `_skills_manifest` and verifier `_committed_skills` | Materialise skills for hashes/derivation evidence, not prompt bodies. |
| Constitution input | Separate committed read; overlap finding above. |
| Governed tool evidence | Allowlisted ledger projection, not raw file-read output. No additional raw skill-output route found. |
The public `prompt.build`/`render_increment` functions themselves still accept arbitrary mappings, including `skills/house.md`. The exclusion is a CLI ingress policy, not a property enforced by the prompt API.
For `prefix_own`, the actual workflow behavior is:
| Commit/action | Behavior and assessment |
|---|---|
| Skill plus work edit | Proceeds with work; may include neighboring experiment files through existing enclosure. Correct. |
| Skill only, explicit SHA | Refuses. Correct for a command auditing that commit’s changed work. |
| Skill only, plain `run` | Selects older work, subject to existing cycle/decision guards. Reasonable as an audit convenience, but does not generate a revision using the new skill. |
| Skill edited before a subsequent build | The next build loads guidance through the unchanged loader. A currently running loop loads `house` once, so it does not promise live skill reload between rounds. |
I would not automatically rejudge an already-decided increment merely because guidance changed. The needed correction here is accurate behavior documentation, copy, and coverage.
The remaining path probes were:
| Input | Result |
|---|---|
| `skills/../work/x.md` | Predicate returns true on that literal string. Git normalizes pathspecs and returns canonical tree paths; analogous real-Git probing returned the normalized work path. No traversal bypass found. |
| `./skills/x.md` | `Path.parts` removes `.`; excluded. |
| `SKILLS/x.md` | Not excluded; case-insensitive exposure above. |
| Symlink at `skills` | Full scope refuses; target-alias exposure through changed-path audit described above. |
| `work/skills/x.md` | Retained and rendered, correctly as ordinary work unless aliased into the loader. |
| Different configured skills directory | `Config` has no skills field; a top-level `skills:` key is refused. `skills.load` has a `directory` argument, but shipped callers use its default. |
Receipt handling has **no demonstrated backward-verification regression**. [verify.py:406](src/crossaudit/receipt/verify.py:406) iterates the receipt’s own manifest and hashes blobs from its pinned subject tree. It does not reconstruct that manifest from today’s scope configuration. `cfg` is used elsewhere for controller/isolation checks.
The legacy-receipt test constructs a synthetic old-style manifest containing the skill, uses the current builder, then asserts only `evidence["verified"]`. It passed with in-memory storage. It does not exercise an archived signed receipt, and its cycle has no Constitution pin.
For new receipts:
- `inputs.manifest` excludes canonical skills; `inputs.skills` retains their committed-byte hashes.
- Editing the working skill, or committing a later edit, leaves historical verification valid. Both probes passed, correctly.
- `inputs.skills` is re-derived, but divergence is **informational**, not a denial: [verify.py:264](src/crossaudit/receipt/verify.py:264), [verify.py:566](src/crossaudit/receipt/verify.py:566).
- Forging that field in the test’s unanchored receipt shape returned `verified: true` with `skills: diverged`. Adding the normal controller pin and recorded receipt digest caused the same alteration to be rejected. Signature verification is an additional separate CLI check. **I found no demonstrated forgery of a normally recorded, signed receipt.**
The eight mutation outcomes, using the in-memory adapters, were:
| Test | Mutation result |
|---|---|
| Root scope | Removing house-skill exclusion reddened it. |
| Explicit root | Conditional exclusion reddened it. |
| Generator handoff | Empty loader/suppressed prompt block reddened it; `materialise` filtering survived. |
| Similar/nested names | Substring and any-component filters both reddened it. |
| New skill/receipt digests | Empty `_skills_manifest` reddened it. |
| Old receipt verification | Comparing against newly derived filtered scope reddened it. |
| No deterministic reader | Literal `"skill"` reddened it; functioning indirect reader survived. |
| Run verb | Removing `prefix_own`’s skill entry reached the intercepted audit call instead of refusal. |
Generator loading/rendering code is unchanged by the diff; I found no direct generator-handoff regression. The named kernel directories—`auditor/`, `broker/`, `ledger/`, `policy/`, `dcl/`—are untouched. The skills docstring’s new wording identifies an enforcement location but does **not** narrow its universal claim enough to match the implementation.
**Do not merge — house-skill bytes still reach the auditor through directory aliases, so the central boundary claim is not enforced.**
