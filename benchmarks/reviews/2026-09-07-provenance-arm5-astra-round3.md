<!-- verbatim: codex exec -m gpt-6-astra, read-only, on study/provenance-arm5 at 6e22161; archived unedited -->

Two report defects remain. The primary result still reproduces: **4/398 = 1.01%; Wilson 0.39–2.56%; draft-clustered bootstrap 0.24–1.97%; PASS**.

1. **The census amendment still overclaims.** [Amendment 1](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm5/benchmarks/expertlongbench/study8/PREREGISTRATION-ARM5.md:156>) says the absence-of-traceable-numbers rationale is true of T04. Replaying the census finds **165 input numbers across 19 instances**, with **12/19 reference values traceable (63.2%)**, including one matching pair with a unit under its extractor. A median of zero does not establish absence. The amendment also leaves §0’s T07 **0%** statement uncorrected; the census reports **39.0%**. These counts do not establish task suitability, but they contradict the categorical rationale.

2. **Arm 4’s comparison interval remains wrong.** [RESULTS §5.1](</private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm5/benchmarks/expertlongbench/RESULTS-ARM5.md:102>) gives 16/206 a Wilson interval of **4.77–12.42%**. Recalculation gives **4.84–12.24%**, matching RESULTS-ARM4. Round 2’s confirmation of that interval was mistaken.

The five claimed fixes otherwise check as follows:

- **§5.7:** verified. The M4 flag has exactly one triggering occurrence, with the stated value, tilde, whitespace and unit-plus-hyphen relationship. The old explanation is explicitly withdrawn.
- **Intervals:** movement **5.92–11.33% / 4.36–12.58%** and annotation **35.38–40.94% / 34.47–41.94%** reproduce. Arm 3’s quoted intervals match its report; zero-event bootstraps reproduce as **0.00–0.00%**. Arm 4 is the exception above.
- **Diff script:** prints **401 located rows**, each tallied once per reading; quotation counts reproduce as **361 / 7 / 33**.
- **Preregistration:** original text remains intact; T01’s **93.3%** and shape/cost correction are supported. The amendment’s broader claim remains defective.
- **Corpus statement:** scan scope is now explicit. I found no source-specific corpus fragments in post-base additions or intervening committed versions.

All 50 successful archived analyses reproduce; rows, manifest, blinded sheet and seeded key reproduce byte-for-byte. All **3,499 archive checksums** verify. Kernel directories, `src/` and `tests/` remain unchanged; `number_source` belongs to no profile.

Conflict retained: **L2 was `gpt-6-astra`; I did not re-label.** Pytest stopped during collection because no writable temporary directory exists. No files were modified.

**not quotable** — the most important remaining reason is that the amended corpus-selection rationale still asserts an absence its own census contradicts.
