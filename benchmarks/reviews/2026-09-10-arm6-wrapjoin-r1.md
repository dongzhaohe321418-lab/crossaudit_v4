# Study 15 wrap-join slice — first independent review (gpt-6-astra), 2026-09-10, target 0e711ce

Two blocking findings at HEAD `0e711ce`. No files modified.

1. **The implementation differs from the preregistered join rule.** [wrapjoin.py:45](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-wrapjoin/benchmarks/expertlongbench/study15/wrapjoin.py:45) uses `strip()` where §1 specifies removing **leading** whitespace only. Consequently, `"# "` loses its heading status, while `"--- "` incorrectly becomes structural.

   This changes joins in **17 archived source files**. Running an independent implementation of the literal preregistration leaves **all 91 row records unchanged**, including the four primary outcomes and kill, but changes total joined lines **21,773 → 21,687** and the minimum joined/original ratio **0.054173 → 0.052416**. Correct the implementation, regenerate the report, and test these whitespace cases.

2. **The reported fragment-scan procedure cannot establish its claim.** The [reproduction command:187](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-wrapjoin/benchmarks/expertlongbench/RESULTS-ARM6-WRAPJOIN.md:187) takes its baseline from HEAD, including every candidate file. Subtracting that baseline necessarily removes any candidate’s matching corpus shingles. Separately, [wrapjoin_scan.py:84](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-wrapjoin/benchmarks/expertlongbench/study15/wrapjoin_scan.py:84) scans candidates line by line, missing five-word runs split across newlines. In-memory synthetic probes confirmed both false-clean paths.

   **I found no corpus leakage in this slice:** my independent whole-file scan of all seven changed files found zero five-word matches against archived sources, and zero residual archive matches after subtracting the **pre-slice `1f6120e` baseline**. Fix the committed scanner and its reproduction command; include the scanner itself among the targets.

The substantive measurements check out:

- The driver reproduced both committed output files **byte for byte**, with only output writes intercepted into memory. All **91 unjoined verdicts** re-derived equal; original row fields and gold labels remain unchanged.
- Matcher blob `620fb3bcc1f57b1888e1cd4b74acd30aa93a10bf`, `provenance_arm4.py`, `src/`, and kernel code are unchanged from `1f6120e`.
- Independent arithmetic reproduced the primary intervals:

| Outcome | Count | 95% Wilson | Draft bootstrap; discarded |
|---|---:|---:|---:|
| Q1 newly located | 24/40 | 44.60–73.65% | 17.65–90.91%; 5 |
| Newly located blocked | 10/24 | 24.47–61.17% | 0–71.43%; 36 |
| Located gold-C blocked | 3/15 | 7.05–45.19% | 0–75%; 15 |
| Crossing after join | 1/87 | 0.20–6.23% | 0–4%; 0 |

The Q1 partition is 24 located, 15 ambiguous, one crossing, zero absent; newly located verdicts are 14 PASS and ten BLOCKER. Both labelled-pass changes are exactly A60011/A60012 becoming ambiguous. The three unclosed-fence files follow the preregistered toggle rule; the remaining crossing row lies inside fence state.

The bound `[0, blocked share]` and **undetermined** interpretation were explicitly preregistered. “Refuted” would overclaim. The shape predicate reproduces the five labelled classes and describes nine currency-prefix candidates plus one M1b-shaped candidate; the results consistently withhold correctness labels from the ten new blocks.

I checked §§1–2 sentence by sentence: their numerical and row-description claims agree with the records. The §0 survey makes outcome (a) **data-informed rather than an independent prospective test**; disclosure preserves its descriptive value. Git confirms preregistration-before-committed-code, but cannot independently establish everything the author previously inspected.

Tests: **50/50 slice tests passed**; benchmark suite **166 passed, two temporary-directory setup errors**. The full product suite likewise stopped on a read-only temporary-directory error. I cannot certify “168 passed” or full-suite green here.

**not quotable — the implemented join rule differs from the binding preregistration on 17 archived files.**
