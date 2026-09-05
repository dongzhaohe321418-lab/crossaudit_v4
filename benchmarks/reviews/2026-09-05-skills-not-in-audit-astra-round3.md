# Independent cross-vendor review of `fix/skills-not-in-audit`, round 3 — 2026-09-05

Reviewer: `gpt-6-astra` (first attempt died at capacity; re-run succeeded),
read-only, over a5ec01e. Verdict: **do not merge**, four small items:
`/abs/skills/house.md` accepted at config load; the accepted pass-through
spelling is stored raw and fails the strict committed-file reader; the
property test depends on registry state from earlier tests; and the
explicit-flag-only language decision is inconsistent with `init`, `doctor`
and the denial handler, which honour the environment. Everything from
round 2 confirmed fixed, full mutation matrix red. Verbatim below.

---

Reviewed `a5ec01eade8794ca9d49cfb826268800cc6a64fc` against `fusion/evidence-authority`, including the round-2 report. No files modified; checkout remains clean.
Validation limit: filesystem writes are prohibited here. Targeted tests used **in-memory filesystem, Git-object, and controller-storage adapters**, retaining production loading, filtering, checks, prompt construction, and receipt verification. `cmd_run` probes recorded its auditor arguments and stopped there. These results do not replace a normal-host suite run.
| Round-2 item | Status | Probe and result |
|---|---|---|
| Case-variant directory | **reproduced-as-fixed** | `SKILLS/house.md` causes loader refusal naming the required spelling. Both audit routes retain it as ordinary work. |
| Symlinked guidance directory | **reproduced-as-fixed** | `skills -> work/guidance` is refused by the loader. A commit containing the symlink fails materialisation before any auditor call; a subsequent target-only edit reaches the auditor as work. |
| Constitution guard | **fixed-but-new-problem** | Case and traversal aliases now fail config load, but `/abs/skills/house.md` still loads. The newly accepted pass-through spelling also remains unusable downstream; details below. |
| All-check property and false docstring | **fixed-but-new-problem** | The docstring is corrected. With checks registered, the property and positive controls pass and removing the filter reddens it. In a fresh process, however, the test fails before exercising the property because the registry is empty. |
| Walk-back language and copy | **reproduced-as-fixed** | Actual `main(["--lang","zh","run"])` produces Chinese walk-back narration. Plain `run` under Chinese `LANG` produces English narration. The rationale’s claim about `init` is incorrect. |
| Generator mutation overclaim | **reproduced-as-fixed** | Empty loading and suppressed generator guidance both redden the handoff test. Filtering `materialise` survives that test, as documented, and reddens the receipt-digest test. |
| Stray file named `skills` | **reproduced-as-fixed** | Loader refusal says it is audited as ordinary work; root-scope materialisation retains it; actual `cmd_run` passes its bytes to the auditor. All three agree. |
The configuration matrix, executed through `config.load()`, was:
| Constitution value | Observed |
|---|---|
| `skills/house.md` | Refused |
| `./skills/house.md` | Refused |
| `SKILLS/house.md` | Refused |
| `Skills/house.md` | Refused |
| `work/../skills/house.md` | Refused |
| `skills/../skills/house.md` | Refused |
| `../skills/house.md` | Refused |
| `/abs/skills/house.md` | **Accepted — required refusal missing** |
| `skills//house.md` | Refused |
| `skills/../AUDIT_RULES.md` | Accepted |
| `work/AUDIT_RULES.md` | Accepted |
| `AUDIT_RULES.md` | Accepted |
The outside-project check at [config.py:307](src/crossaudit/config.py:307) handles `..` and `../`, but never checks for an absolute path. Its first component is `/`, so the subsequent skills comparison also misses it. **I did not reproduce an auditor exposure**; this is an incomplete config-load guard.
Accepting `skills/../AUDIT_RULES.md` is defensible as a location-based policy: its normalized location is outside guidance. However, `Config.constitution` retains the **raw spelling** at line 487. Calling `_committed_constitution()` with that accepted configuration raises `IntegrityDenial` because the strict Git reader requires an exact tree path. Real-repository probes independently confirmed that equivalent traversal spellings fail that reader. Thus the acceptance does not open the auditor boundary, but “a fine rulebook” currently overstates its usability.
The predicate matrix exactly matched the request:
```text
skills                 False
skills/x.md            True
skills/sub/x.md        True
skillsx/x.md           False
work/skills/x.md       False
```
For language selection, the explicit-flag decision is **inconsistent with current `init`, `doctor`, and ordinary denial handling**:
- [`_language_for()` at main.py:375](src/crossaudit/cli/main.py:375) resolves explicit flag → environment → English.
- `cmd_init` at line 1543 and `cmd_doctor` at line 390 call `_speak()` unconditionally.
- The denial handler at line 2210 independently uses `_language_for()`.
- `cmd_run` at line 1650 calls `_speak()` only with an explicit flag.
Under `LANG=zh_CN.UTF-8`, with higher-priority locale variables cleared, the command probes observed Chinese selected at the `init` wizard entry, English walk-back narration for plain `run`, and Chinese guidance-only denial text for plain `run`. Explicit `--lang en` overrode the environment for `init`. The old parser comment cited by the new `cmd_run` comment contradicts executable behavior.
All **15 test functions / 19 parameterized cases passed in file order** under the adapters. The prescribed in-memory mutation results were:
| Test/property | Mutation | Result |
|---|---|---|
| Root scope | Remove house exclusion | Red |
| Explicit root scope | Apply exclusion only to implicit scopes | Red |
| Generator handoff | Empty loader; suppress guidance block | Both red |
| Similar/nested names | Substring exclusion; any-component exclusion | Both red |
| Skills digest | Empty `_skills_manifest` | Red |
| Generator/digest distinction | Filter `materialise` | Handoff green as documented; digest red |
| Legacy receipt | Compare against newly derived scope | Red |
| All-check property | Remove house exclusion | Red |
| Explicit-SHA run | Remove skills prefix | Red |
| Walk-back | Replace catalogue call with current raw English | **Red at the Chinese command-output assertion** |
| Walk-back | Drop `_speak(args)` | **Red at the Chinese command-output assertion** |
| Case variant | Return `None` instead of refusing | Red |
| Case variant | Replace entry scanning with `resolve().name` comparison | Red: expected refusal absent |
| Stray file | Restore `bool(parts)` predicate | Red |
| Directory symlink | Restore per-file-only checks | Red |
| Constitution | Remove normalization; remove case folding; delete guard | All red, including all five guard parameters |
| Pass-through constitution | Compare raw first component | Red |
| Outside-project constitution | Remove traversal check | Red |
The `resolve().name` mutation used case-insensitive filesystem semantics backed by an independent real-host observation: existing `skills.py` and `SKILLS.py` resolve to the same file, while `Path(.../"SKILLS.py").resolve().name` remains `SKILLS.py`.
The property-test isolation issue is at [test_skills_are_not_audited.py:387](tests/test_skills_are_not_audited.py:387): `framework.available()` reads the lazy registry before this test loads the checks. Fresh-process execution fails its “two checks … are gone” assertion; executing `run_checks()` first makes it pass. After registration, all ten checks ran. Positive controls produced `CA-FILE-004` from `complete` and `complete-strict`, and `CA-FILE-003` from `internal`; filtered guidance produced no findings. No positive coverage is claimed for the other seven checks.
The remaining checks held:
- No false refusal through a symlinked project root in the adapter; real-host `house_dir(Path("/var"), "log")` also succeeds through the symlinked root.
- `auditor/`, `broker/`, `ledger/`, `policy/`, `dcl/`, `receipt/`, and `controller/` are untouched by the diff.
- `git diff --check` passes.
- Translation, slot-preservation, and non-orphan denial gates pass directly.
- Executed console JavaScript resolves the updated English and Chinese summaries. No browser walkthrough was performed.
**The claimed 2763 passed, 8 skipped remains unverified.** Normal pytest fails before collection because capture cannot create temporary storage. Capture-free collection reaches **2694 tests**, then stops on temporary-directory errors in `test_activity_stream.py` and `test_report_provenance.py`.
**Do not merge — the single most important reason is that config load still accepts `/abs/skills/house.md`, violating the explicitly required constitution-guard matrix.**
