# Independent cross-vendor review of Study 8 Arm 4, round 3 (final) — 2026-09-06

Reviewer: `gpt-5.6-sol` (astra at capacity; the standing fallback),
read-only, over 1cbc0ab. Verdict: **yes, quotable** — "the preregistered
9/189 KILL result and every corrected interval now independently reproduce
from the unchanged, corpus-free records without a remaining material
overclaim." Both projection intervals, the 0/50 bound and the `uncited`
placement recomputed; `rows-arm4.jsonl` blob unchanged across the three
rounds; no corpus text in any committed surface; the excerpt-bearing object
absent from history, reflogs and unreachable objects. One note: "nothing else
changed" held for the Arm 4 files, not for the whole branch (a ceiling
handbook edit intervened). Verbatim below; paths shortened to the repository
root.

---

## Third-review verdict
No remaining overclaim found in the four reviewed Arm 4 passages.
- Wilson 95%, `3/189`: **0.5413–4.5621%**, correctly reported as **0.54–4.56%**.
- Wilson 95%, `1/189`: **0.0935–2.9357%**, correctly reported as **0.09–2.94%** in [RESULTS-ARM4.md](<benchmarks/expertlongbench/RESULTS-ARM4.md:69>).
- Wilson upper bound for `0/50`: **7.1348%**, supporting D161’s “no false pass was observed in the 50-row sample … up to 7.14% compatible” wording in [DECISIONS.md](<docs/DECISIONS.md:7323>).
- RESTART now correctly places 7.77% between Arm 3 A, `25/234 = 10.68%`, and B, `14/206 = 6.80%`, in [RESTART.md](<docs/RESTART.md:318>).
- [CORRECTIONS.md](<benchmarks/CORRECTIONS.md:335>) accurately records all three round-2 incompletions and their correction.
`rows-arm4.jsonl` is unchanged: its Git blob is `6ebc3db9…` at `c18a367`, `d98be57`, and `1cbc0ab`; content SHA-256 remains `f1e80ce8…`. No code or Arm 4 machine record changed. There is one unrelated intervening RESTART edit for the ceiling study, so “nothing else changed” is true of the Arm 4 correction itself, not literally of the entire branch since `c18a367`.
No Arm 4 corpus text was found in the committed surfaces: structured records contain hashes, lengths, identifiers, classifications, and metadata only; CSVs contain IDs, labels, and rule codes; prose uses abstract shapes. The abandoned excerpt-bearing object is absent from reachable history, reflogs, and unreachable objects. Direct comparison with the licensed corpus was impossible because the corpus and archive were unavailable.
**May this report be quoted as the Arm 4 result? Yes.** The single most important reason is that the preregistered **9/189 KILL result and every corrected interval now independently reproduce from the unchanged, corpus-free records without a remaining material overclaim.**
