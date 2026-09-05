# Independent cross-vendor review of the ceiling study, round 9 — 2026-09-06

Reviewer: `gpt-6-astra`, read-only, over `study/ceiling` at 4bea383. Numbers
byte-identical to round 8; 42 tests; the generated re-attribution test is
non-vacuous (312 executions, 168 distinct mutated reports, none surviving).
Verdict: **yes with corrections** — the guard's CLAIM exceeds what a lexical
guard can enforce (grammatical ownership in two-family sentences, rates in
words, captions outside scope), and deviation 34's "no published number was
ever wrong" is false as a history (round 2's −0.88/−0.89, round 3's +43.8/+43.7
and 0.924/0.953, the two-seed residual intervals). Resolution for round 10:
narrow the claim to what the checks enforce; record the uncovered cases as
documented boundaries. Verbatim below.

---

**The numbers reproduce unchanged, but the claimed structural closure remains incomplete.** Reviewed `4bea383` against merge base `19bd1615c3d35381c37525721b6d38c5831b1ee5`, with all eight prior reports consulted. No files modified, network used, or detector readings adjudicated.
1. **The guard still accepts false attribution.** Its [subject check](benchmarks/code/tests/test_report_consistency.py:613) requires family words somewhere in the sentence; it does not identify which family owns each claim.
   This replacement leaves **all 21 report tests green**, including the generated mutation test:
   ```text
   Before: The generator's own model does flatten, and far lower:
   After:  The shipped cross-vendor auditor, unlike the generator's own model, does flatten, and far lower:
   ```
   The unchanged continuation now falsely attributes self’s `15.5%`, `17.3%`, `16.6%` asymptote and `24.0%` false-positive rate to the shipped auditor. Reversing the order of the family mentions also passes. **Neither first-token nor grammatical-subject ownership is enforced:** the rule selects an array, then checks token presence.
   The requested attacks produced:
   | In-memory attack | Result |
   |---|---|
   | Insert “The self model has a fitted asymptote of 16.6% [21.7, 45.6].” | **Red**, because the new rate is unbound |
   | Insert “The self model’s fitted asymptote has interval [21.7, 45.6].” | **All 21 green**: an existing cross interval falsely attributed to self |
   | Insert the supplied “self and cross asymptotes are…” sentence | **Red**, because both rates are unbound—not because ownership was parsed correctly |
   | Two-family replacement shown above | **All 21 green** |
   | Insert the wrong-family rate/interval in a caption or footnote outside opening/conclusion | **All 21 green** |
   | Move an existing bound asymptote into a footnote | **Red** through binding liveness and the generated test’s unmutatable assertion |
   | Insert “The self model recalls thirty percent of defects.” in a guarded section | **All 21 green** |
   The opening/conclusion restriction is explicitly stated and accurately implemented. The broader subject-binding and “every rate” assurances exceed its reach. Outside those sections, ordinary intervals generally receive a membership check, not an estimand check. Words expressing rates are invisible to the numeric scanner.
   Describe this as a **lexical editing guard for registered numeral templates**, or extend verification to the unsupported cases before claiming general attribution coverage.
2. **Deviation 34 needs qualification.** Its [“No published number was ever wrong” statement](benchmarks/code/RESULTS-CEILING.md:849) is defensible only when explicitly restricted to the synthetic re-attribution counterexamples from rounds 6–8. It is false as a history of all eight reviews.
   Examples from that history:
   - **Round 2:** prose quoted `[−0.88, +12.08]`; regeneration gave `[−0.89, +12.07]`.
   - **Round 3:** commit `d9bf61e` actually published `[+6.3, +43.8]`; the regenerated endpoint displays as **+43.7**. The subsequent correction is recorded in [CORRECTIONS #21](benchmarks/CORRECTIONS.md:462).
   - **Round 3:** detrimental bootstrap coverage was reported as **0.924**, but the stated scenario gives **0.953**.
   - **Before round 6:** the residual share appeared with both `[40.4, 63.6]` and `[40.0, 63.3]`. These were individually valid bootstrap estimates from different seeds; presenting both as the same canonical interval was inconsistent. Round 6 verified the correction of this and three registered-union interval arrays.
   Suggested qualification: “The synthetic re-attribution counterexamples in rounds 6–8 did not change the committed estimates; earlier numerical and reporting corrections remain documented.”
The other requested verification results are:
- **All 42 tests passed: 21 statistics + 21 report.** Direct invocation under Python 3.13.5; `.venv` and pytest were unavailable. Application and hidden suites were not rerun.
- **Hashes equal round 8 (`b887bb8`):**
  ```text
  numbers.json 412534c7222569ed736cdcb84019a0ff1efdb01273ec2e555312b515463d8ee0
  tables.md    c5e939aac38fc238767dfb918f8cc10b026c9231f59329f7911e5a300c6f7e2e
  ```
  Regeneration returned zero and reproduced both byte-for-byte with credential-like variables unset, sockets disabled, bytecode disabled, and output writes intercepted in memory.
- **The generated test is non-vacuous for its implemented mutation class.** I observed **312 mutation executions: 39 bound rules × eight alternative subjects**, covering 23 arrays. They produce **168 distinct mutated reports**; none equals the baseline, none survives, and no rule is unmutatable. The normalized-to-raw offset map is used.
- **Both protective assertions fire.** Invalid inserted prose triggers “the unmutated report must be clean.” Adding an unreachable binding while keeping the baseline clean triggers “bindings whose subject cannot be mutated.”
- Removing a subject declaration, blanking its family, or setting it to unknown `"generic"` turns the declaration test red. This checks vocabulary membership, not semantic specificity: adding a recognized generic vocabulary containing only `asymptote` and assigning the self-asymptote binding to it leaves the declaration, baseline and generated checks green.
- The **three round-8 counterexamples are committed together in one named regression test** and are rejected. “Seven sentences” is inaccurate: applying the new requirements to round 8 identifies **seven failing rule matches across four distinct sentences**.
- **Duplicating `_pairs` in memory turns the committed AST test red**, reporting `'_pairs': 2`. Its eight files, relative to `benchmarks/code/`, are:
  ```text
  tests/test_report_consistency.py
  tests/test_ceiling_stats.py
  report_ceiling.py
  ceiling/finalise_manifests.py
  ceiling/splice_tables.py
  loop.py
  ceiling.py
  residual_dump.py
  ```
- The attribution table has **ten findings: eight reviewer discoveries and two author discoveries**, with nine numbered entries. Changing “Eight of the nine numbered corrections” to “Seven…” turns the committed attribution test red.
- **`src/` diff and branch-only history are empty** against the merge base. Deviations are exactly **1–35**, monotonically numbered.
**May these numbers be quoted in a paper — yes with corrections, because the numerical artifacts reproduce but the claimed attribution guarantee still accepts false assignments of results to families.**
