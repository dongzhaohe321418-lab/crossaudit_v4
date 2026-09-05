# Independent cross-vendor review of provenance slice 1, round 6 — 2026-09-05

Reviewer: `gpt-6-astra`, read-only, over 07c15b1. Verdict: **do not merge**
for one new regression: the exponent normaliser maps both `+` and `-` to
`-`, so `1e+5 ≡ 1e-5` (100/100 wrong on a 1–100 sweep; round-5 code blocked
all 100). Everything from round 5 confirmed fixed, including pruning by pinned
digest and the reviewer's agreement that all seven Arm 1 blocks are
harness-annotation errors and Arm 1 has reached its measurement limit.
Verbatim below, paths shortened.

---

**Do not merge.** Reviewed `07c15b18` against `fusion/evidence-authority` at `ea8c2a50`, including the round-5 report. No files were modified.
**P1 — The exponent fix introduces incorrect numeric equivalence.** At [quantities.py:123](src/crossaudit/dcl/quantities.py:123), both explicit exponent signs become `"-"`:
```python
sign, digits = ("-", exponent[1:]) if exponent[0] in "+-" else ("", exponent)
```
Consequently, `normalise_number("1e+5") == "1e-5"`. I reproduced these results through both fenced annotations and structured citations under the **complete science profile**:
| Source | Annotation value / unit | Result |
|---|---|---|
| `1e+5 g` | `1e-5 / g` | **Incorrect PASS** |
| `1e-5 g` | `1e+5 / g` | **Incorrect PASS** |
| `100000 g` | `1e+5 / g` | Incorrect BLOCK |
| `1e+5 g` | `100000 / g` | Incorrect BLOCK |
A contiguous exponent sweep from **1 through 100** produced **100 incorrect passes and 100 equivalent-value blockers**. Git-loaded round-5 code blocked all 100 incorrect pairs. This is a new regression.
“BLOCK” below means `CA-NUM-002`, unless another rule is named.
| Round-5 item / requested verification | Disposition | Probe and result |
|---|---|---|
| Signed notation | **reproduced-as-fixed** | All four requested signed-prefix cases BLOCK; structured `10 / "⁻⁵"` also BLOCKS under complete science. Additionally, 72 operator/sign/spacing combinations and four superscript-sign continuations all BLOCK. |
| Legacy pruning | **reproduced-as-fixed in memory-backed execution; actual staging unverified** | Rebuilt all three historical renderings, checked fixture bytes and pinned hashes, exercised both creation paths’ actual statements, intercepted staging arguments, and ran the digest mutation described below. |
| Quote and footnote boundaries | **reproduced-as-fixed** | All requested quote/note cases PASS on `°C`; all 16 enumerated quote/note marks also PASS under complete science. `*` and `>` BLOCK shortened `°C`, as specified. Full prose sweep results below. |
| Enclosing-artifact `at` bounds | **reproduced-as-fixed** | On an exactly four-line artifact: `#L1-L1000000` → `CA-NUM-001`; `#L4-L4` → PASS; `#L5` → `CA-NUM-001`. |
| `m-2 s-1` guidance | **reproduced-as-fixed** | Executed all four behavior rows and the shipped-wording test: `m-2` PASS; `m-2 s-1`, `m-2s-1`, and `m-2·s-1` BLOCK. |
| Exponent cutoff | **fixed-but-new-problem** | `1e000005` and `1e99999` PASS; `1e100000` → `CA-NUM-001`. Explicit positive exponents now acquire a negative sign, producing the P1 above. |
| Compatibility differentials | **reproduced-as-fixed on reconstructed corpora** | 216 helper mappings, 96 declaration mappings, and 40 fenced + 40 structured locator cases: zero differences against round 5. Declaration mappings also match base. |
| Arm 1 | **reproduced-as-fixed for the reported measurements** | Actual harness: **7/365 = 1.92%, Wilson [0.93, 3.91]**; secondary **3/8**. Removing synonyms in memory gives **13/365**. Independently inspected the seven blocked draft annotations. |
| Kernel changes / full suite | **Kernel restriction confirmed; full-suite claim unverified** | Protected directories unchanged except the additive auditor display-name entry. Full-suite collection fails on unavailable temporary directories; focused results below. |
The requested signed-notation neighborhood behaves as follows:
| Source | Value / unit | Result |
|---|---|---|
| `run 5 of 12` | `5 / ""` | PASS |
| `5 x 3 grid` | `5 / ""` | PASS |
| `5 m·s^-1` | `5 / m·s^-1` | PASS |
| `5 cm-1` | `5 / cm-1` | PASS |
| `5 ± 0.1 g` | `5 / g` | BLOCK |
| `5·10³ g` | `5 / ""` | BLOCK |
| `5 ⋅ 3` | `5 / ""` | PASS |
| `10^5 g` | `10 / ""` | BLOCK |
| `2⁵ g` | `2 / ""` | BLOCK |
| `5 −3 g` | `5 / ""` | PASS |
| `5 −3 g` | `5 / g` | BLOCK |
The spaced-operator passes follow the stated direct-continuation contract. Empty-unit `5 / ""` against `5 g` also passes, matching the disclosed choice.
For pruning, I executed the historical composer using templates loaded from **`da8ddfe`**. Its numbers-only, sources-only, and combined outputs exactly equal the committed fixtures. Their SHA-256 digests exactly equal the pinned set:
```text
numbers  1fda0d9187c1de90f6ad571f450e0a678f7c119ae6b7302e9cb087108eaeafef
sources  967213437932ca9fc7d62a6f67d8c7332be48d496df0b40c7bb76e2b9ca5fc90
both     36c79202e7a9de020c31303d6821fddd80854ef3cf08a95e116e5efd3d1f2d40
```
The round-5 hand-written fence-name counterexample survives, as does each fixture with an extra newline. Across **two creation paths × three renderings × tracked/untracked states**, memory-backed execution removed exactly `skills/provenance.md`, preserved the adjacent file, and included the removed path in `owned` and the intercepted `git add` arguments only when tracked.
Changing the historical numbers template and recomputing constants **in memory** makes the fixture-digest assertion fail for `numbers` and `both`. Actual `git status` evidence of staged deletion is **not established**: creating a test repository or changing its index would violate this session’s read-only constraint. The committed staging test also exercises pruning manually after creation; it does not inject a legacy file through both creation paths.
The complete round-5 prose sweep retains its expected behavior:
- `°C` passes before `)`, `).`, `…`, `—and`, `–25 °C`, `»`, `”`, `’s`, `]`, `}`, `†`, `§`, `‡`, `¶`, `„`, `:`, `;`, sentence-period-plus-space, tab, NBSP, em space, `!`, and `?`. `(5 °C).` passes too.
- `/`, `>`, `*`, `.then`, and `.5` remain literal continuations: shortened `°C` blocks, and the corresponding complete token passes.
- `5 g.`, `5 g.\n`, `5 kg.m`, `5 mol.L-1`, and unitless `pH 7.` pass with their expected annotations.
- The earlier structured `kg.m`, `wt %/s`, and `°Cβ` regressions remain fixed: short units BLOCK, complete units PASS.
The differential programs were **reconstructed**, because the round-5 report contains counts and descriptions but no original executable probe. Their matching counts do not establish that they are the identical historical inputs.
For Arm 1, **I agree all seven current primary blocks are harness-annotation errors**: six truncate ramp-rate units, and one extracts `10 / ""` from draft text containing **`3 × 10⁻² mbar`**. I checked the actual draft lines and named source lines individually. Synthetic draft-only probes also confirm the truncation diagnostic changes when `10` becomes `10⁻²`, or `°C` becomes `°C/min`.
I agree this fixed corpus and extractor have reached their limit for interpreting the remaining numerator as verifier false blockers. They still provide regression evidence; they cannot establish general correctness or a general false-blocker rate. The newly reproduced positive-exponent defect is outside what this measurement detects.
The claimed **3015 passed, 8 skipped** remains unverified here. With bytecode, pytest cache, and capture writes disabled, full-suite collection stopped on two temporary-directory errors. Focused execution yielded **280 passed, 1 filesystem-related failure, 22 filesystem-test deselections**. Those passes include the new behavior and contract tests. `git diff --check` passed, and the working tree remained clean.
Broker, ledger, policy, receipt, and controller directories are unchanged against base; `auditor/` only adds the display name. DCL has substantive changes, and the exponent regression prevents an additive-correctness sign-off.
**Do not merge — the single most important reason is that explicit positive exponents now become negative exponents, allowing numerically wrong citations to PASS the complete science profile.**
