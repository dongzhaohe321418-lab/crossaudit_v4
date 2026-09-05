# Independent cross-vendor review of `fix/skills-not-in-audit`, round 4 — 2026-09-05

Reviewer: `gpt-6-astra`, read-only, over ab4183c. Verdict: **do not merge**,
one item: the Windows drive / UNC constitution guard has no test — its effect
can be removed with all 24 cases green. Everything from round 3 confirmed
fixed, including normalised storage reaching the committed reader, registry
isolation, language selection under LANG / --lang / LC_ALL, and a legacy
receipt verifying. Verbatim below, paths shortened.

---

Reviewed `ab4183c45b4ea8eeee3c7b85199829235e68be55` against `fusion/evidence-authority`, read-only. Worktree remains clean.
## Blocking finding
`fixed-but-new-problem`: the Windows absolute-path behavior works, but has no regression test.
The production branch at [config.py:313](src/crossaudit/config.py:313) uses:
```python
posixpath.isabs(const_norm) or PureWindowsPath(const_raw).drive
```
But the absolute-path test at [test_skills_are_not_audited.py:782](tests/test_skills_are_not_audited.py:782) covers only:
- `/abs/skills/house.md`
- `/etc/AUDIT_RULES.md`
There is no test anywhere for a Windows drive or UNC constitution.
Probe: in memory I removed the `PureWindowsPath(...).drive` effect. Every existing constitution case retained its expected result, while both forbidden values became accepted:
```text
C:\x\AUDIT_RULES.md       ACCEPT
\\server\share\x.md       ACCEPT
```
Therefore the Windows/UNC guard can be deleted while all 24 cases in this test file remain unaffected. This violates the repository’s “new behavior has a test” and mutation-evidence requirements.
The accepted aliases `./AUDIT_RULES.md` and `work/./AUDIT_RULES.md` are likewise absent from the checked-in parameter matrix, although their current behavior is correct.
## Round-3 disposition
| Round-3 item | Status | Independent probe |
|---|---|---|
| Case-variant directory | reproduced-as-fixed | Mocked the root directory entry as `SKILLS`; production `house_dir()` refused it and named the required spelling. `_is_house_skill("SKILLS/x.md")` remained false, so it is ordinary work. |
| Symlinked guidance directory | reproduced-as-fixed | Mocked `skills` as a directory symlink; `house_dir()` refused it. `_is_house_skill("work/guidance/house.md")` is false. Relevant `skills.py` code is byte-unchanged since round 3. |
| Constitution guard and stored spelling | fixed-but-new-problem | All requested values behave correctly, and accepted values reach `_committed_constitution()` under canonical paths. New problem: the separate Windows/UNC guard is untested, as above. |
| All-check property isolation | reproduced-as-fixed | Fresh interpreter: registry before imports `0`; after importing the four packs, exactly `10`. Removing imports makes the `>=10` assertion fail. Removing the guidance filter produces findings from `complete`, `complete-strict`, and `internal`; filtered input produces none. |
| Walk-back language | reproduced-as-fixed | Production `cmd_run` with an in-memory Git adapter: `LANG=zh_CN.UTF-8` selected Chinese; `--lang en` selected English; `LC_ALL` took precedence. Gating `_speak` on a flag reddened the environment case; dropping `_speak` or using raw English reddened both Chinese variants. |
| Generator-mutation overclaim | reproduced-as-fixed | Direct `Skill → select → render → generator.build_prompt` retained the guidance sentinel. Generator, skills, Git materialisation, and receipt code are unchanged from round 3; the test still correctly assigns the materialisation mutation to the receipt-digest test. |
| Stray file named `skills` | reproduced-as-fixed | Mocked `skills` as a regular file: loader refusal explicitly says it is audited as ordinary work. Predicate matrix remains `skills=False`, `skills/x=True`, `skillsx/x=False`, `work/skills/x=False`. |
Additional constitution results:
- All nine round-3 refused spellings remain refused.
- `/abs/skills/house.md`, `/etc/passwd`, `C:\x\AUDIT_RULES.md`, and `\\server\share\x.md` are currently refused with distinct English and Chinese text.
- `skills/../AUDIT_RULES.md`, `./AUDIT_RULES.md`, and `work/./AUDIT_RULES.md` normalize respectively to `AUDIT_RULES.md`, `AUDIT_RULES.md`, and `work/AUDIT_RULES.md`; the committed-reader adapter succeeded under those names.
- Twenty canonical path strings were byte-identical after loading. The base stored the original string, while `normpath` was a no-op for all twenty.
- A legacy canonical-path receipt passed the current verifier using committed-object adapters.
- Receipt minting, Git pathspecs, and console rule loading all consume normalized `cfg.constitution`; no downstream code rereads the raw YAML value.
## Test and scope evidence
- `git diff --check`: clean.
- Target collection: exactly 24 cases.
- I could not verify that the 24 cases pass individually or reproduce every documented mutation: this filesystem permits no temporary directory. Ordinary pytest failed before collection; capture-free full collection reached `2699 tests` and then stopped because `test_activity_stream.py` and `test_report_provenance.py` create temporary directories during import.
- Consequently, `2768 passed, 8 skipped` remains an unverified author claim.
- Three-dot branch diff touches seven files under `src/` and `tests/`.
- `auditor/`, `broker/`, `ledger/`, `policy/`, `dcl/`, `receipt/`, and `controller/` are untouched.
**Do not merge.** The single most important reason is that deleting the Windows/UNC absolute-path guard reopens two explicitly forbidden constitution forms while every one of the claimed 24 regression cases remains unaffected.
