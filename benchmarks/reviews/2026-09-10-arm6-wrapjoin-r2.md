# Study 15 wrap-join slice — second independent review (gpt-6-astra), 2026-09-10, target ef6870f

No blocking findings at **ef6870f**. Both round-one findings are resolved. No files modified.

- **Reproduction:** the driver reproduced both committed outputs byte for byte, with output writes intercepted into memory. All **91 unjoined verdicts** re-derived equal; original row fields and gold labels remain unchanged.
- **Matcher and scope:** matcher blob `620fb3bcc1f57b1888e1cd4b74acd30aa93a10bf`, `provenance_arm4.py`, `src/`, and kernel code are unchanged from `1f6120e`.
- **Join rule:** an independent literal implementation agrees on all 33 sources and 17,576 synthetic cases covering whitespace, headings, tables, lists and fences. The correction changes 17 files’ joins: **21,773 → 21,687 lines**, minimum ratio **0.054173 → 0.052416**; row records remain byte-identical. All three unclosed-fence files follow the preregistered toggle rule; the remaining crossing row lies inside fence state.

Independent arithmetic reproduced:

| Outcome | Count | 95% Wilson | Draft bootstrap; discarded |
|---|---:|---:|---:|
| Q1 located after join | 24/40 | 44.60–73.65% | 17.65–90.91%; 5 |
| Newly located blocked | 10/24 | 24.47–61.17% | 0–71.43%; 36 |
| Located gold-C blocked | 3/15 | 7.05–45.19% | 0–75%; 15 |
| Crossing after join | 1/87 | 0.20–6.23% | 0–4%; 0 |

The Q1 partition is **24 located, 15 ambiguous, one crossing, zero absent**. Newly located verdicts are 14 PASS and ten BLOCKER. A60011/A60012 are exactly the two labelled passes becoming ambiguous.

The results’ first two sections agree with the records. The shape predicate reproduces the five labelled classes and identifies nine M13-shaped candidates plus one M1b-shaped candidate. It supplies no correctness labels, and the results consistently withhold them.

The **`[0, blocked share]` bound and “undetermined” reading are explicitly preregistered**, unchanged since 918b14b. “Refuted” would overclaim. The disclosed survey makes outcome (a) data-informed; its descriptive result remains valid, but it is not independent prospective confirmation. Git establishes committed chronology, not everything the author previously inspected.

The committed scanner command reproduces **667,892 archive / 739,813 baseline / 661,026 archive-only shingles; zero matches**. All candidates are absent from baseline `1f6120e`. My independent whole-file scan also found zero residual matches across **all eight changed files**, including the archived review, and zero direct matches against the 33 source files without subtraction. Decoded archive records also produced no matches. `benchmarks/withdrawn.py` is absent.

Tests: **54/54 slice tests passed; benchmark suite 170 passed, two temporary-directory setup errors**. The full product suite stopped during collection on the same read-only restriction. Full-suite green is not certified.

Reader sentence: “On frozen Arm 6 records, the structural join located 24 of 40 crossing quotations (95% Wilson 44.60–73.65%; draft bootstrap 17.65–90.91%), but ten newly located rows were blocked without gold labels, leaving the preregistered inference undetermined.”

**quotable — the corrected implementation reproduces the preregistered descriptive results and preserves the unresolved correctness question.**
