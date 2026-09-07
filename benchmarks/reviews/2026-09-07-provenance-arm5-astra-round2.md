<!-- verbatim: codex exec -m gpt-6-astra, read-only, on study/provenance-arm5 at 476105c; archived unedited -->

The primary result reproduces: **4/398 = 1.01%; 95% Wilson 0.39–2.56%; draft-clustered bootstrap 0.24–1.97%; PASS**. The report still needs corrections.

The six claimed fixes check out as follows:

1. **Corpus leakage:** I found no source-specific fragments in the branch’s additions or intervening commits. Source-derived `git log --all -S` searches found no post-base hits; `4801eae` is unavailable. Ordinary short-word overlaps remain, so “nothing” should not mean literally zero n-gram overlap.
2. **Seed and intervals:** `--arm 5` selects `20261107`. The committed report JSON reproduces exactly, including primary and uncited intervals. Both strata’s Wilson and bootstrap intervals independently reproduce.
3. **Matcher comparison:** quotation-level **361 / 7 / 33** and line-level **361 / 6 / 34** reproduce. However, the script incorrectly prints **802 located rows**, counting both readings together, at [arm5_matcher_diff.py:81](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm5/benchmarks/expertlongbench/study8/arm5_matcher_diff.py:81).
4. **Taxonomy:** emitter and records consistently use **M12**; M11 retains its existing meaning.
5. **Start state:** logged plan fields match the restored plan; the added note propagates into the manifest. This correctly discloses the missing actual-start status—it does not establish a clean start.
6. **Other corrections:** R7, four instances, the two distinct M4 shapes, `edda6da`, Arm 4’s uncited interval, removal of the materiality claim, and the sheet-builder seed are confirmed. RESULTS corrects the census rationale; the frozen preregistration retains the erroneous rationale and needs an explicit erratum.

Remaining report defects:

- **The unit-shortening explanation is false.** [RESULTS §5.7](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-arm5/benchmarks/expertlongbench/RESULTS-ARM5.md:110) says the M4 flag finds a digit inside another number. Executing the instrument shows its sole triggering occurrence is the **exact transcribed value**, immediately preceded by a tilde and followed by whitespace; the unit token begins with the transcribed unit plus a hyphen. The flag concerns the hyphen-glued unit/prose token.
- **Round 1’s interval-completeness finding remains partly open.** The 8.2% matcher-movement rate and 38.1% annotation rate still lack intervals. The quoted Arm 3 uncited rates lack intervals, and the zero-event secondaries omit their computed bootstrap intervals. These remain inconsistent with the registered reporting requirements.

All 50 successful archived analyses reproduce. The emitter reproduces the committed rows and manifest byte-for-byte; the blinded sheet and seeded sample reconstruct exactly. Labels agree 57/57 with eight rule-code differences. All **3,499 archive checksums** verify. Kernel directories, `src/`, and `tests/` are unchanged; `number_source` remains outside every profile.

Conflict retained: **L2 was `gpt-6-astra`; I did not re-label.** Pytest stopped during collection because the read-only sandbox has no writable temporary directory. No files were modified.

**not quotable** — the most important remaining reason is that §5.7 still misstates what its recorded unit-shortening evidence actually shows.
