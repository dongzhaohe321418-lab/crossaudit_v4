<!-- verbatim: codex exec -m gpt-6-astra, read-only, on feat/number-source-science-profile at bf8e802; archived unedited -->

One overclaim remains in [test_number_source_check.py:322](/private/tmp/claude-501/-Users-ericdong/e8f80e28-bc0c-43ea-845e-513b702467fc/scratchpad/wt-profile/tests/test_number_source_check.py:322): unregistering the check does **not** make “the last three assertions redden.” Executed independently:

- `available()` assertion fails.
- Explicit-list `resolve(...)` assertion **passes**.
- Runner assertion raises `ConfigDenial`.

The scaffold-only mutation leaves the profile guard green; profile-only removal fails both profile guards and `science_with_numbers()`, as documented. The source diff since de65f30 is empty.

Eleven focused tests passed with conftest disabled. Disk-backed creation mutations and the full suite remain unverified because fixture setup requires writable temporary storage. No files were modified.

**DO NOT MERGE — the revised mutation documentation still promises detection that execution disproves, violating §3.5.**
