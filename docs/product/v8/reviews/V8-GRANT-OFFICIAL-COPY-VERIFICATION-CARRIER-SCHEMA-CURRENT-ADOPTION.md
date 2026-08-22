# Independent Review — Grant Official-copy Verification Carrier Schema

- Review class: `PROTECTED`.
- Reviewed story range: `4ce83c5..f4d593b`.
- Implementation commit: `f4d593bad6ef13f54ede95348d3edd69ebfdb81d`.
- Task SHA-256:
  `5fe74f006b9dd1a4c8d684ce08455595cda5e0ce265736e75c80c3b3b669ab25`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact four-path story adds one empty, forward-only SQLite carrier for the official-copy
acquisition and two-verifier event chain. The 23-column ORM and migration agree on all six
`ON DELETE RESTRICT` references, three uniqueness constraints, six fail-closed checks and the one
query index. No source, role, user, membership, event or business default is inserted.

The carrier binds each event to the immutable raw-evidence version, selected reviewed source and
institution role configuration. It stores actors, action time, reasons, original reference,
acquisition method and all required hashes. It does not implement stage progression, role
membership, actual-user separation, legal-state confirmation or any fee/lifecycle side effect;
those remain later service responsibilities.

Fresh independent verification passed: focused schema pytest `4 passed`, scoped Ruff passed,
Alembic reported exactly `v8_grant_official_copy_01 (head)`, and exact range diff-check passed.
The exact four-path Git tree fingerprint is
`bab8e16dd35a518a45fca6ad17e09370fedd294e1b9e38b0b3050aceb4e35d98`.
