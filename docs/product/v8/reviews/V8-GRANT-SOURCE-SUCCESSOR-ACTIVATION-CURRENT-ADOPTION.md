# Independent Review — Grant-source Successor Activation

- Review class: `PROTECTED`.
- Reviewed range: `33726b31a7f51cf2b6d39d73ff9d69df52e76b6d..cb92b0ffec4dd5b9653dc19b39823d8d0b926985`.
- Candidate commits: `a599d1cdbc5c9c8d6a890456cf5f28d4cf0a3e0a`,
  `cb92b0ffec4dd5b9653dc19b39823d8d0b926985`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact two-path successor preserves historical controller row 001 and rebinds the grant-source
lane from five to eight ordered rows by inserting only the source schema, service and API
prerequisites. All eight task hashes match their current files. The activation-to-schema-adoption
sequence is non-circular; source service, source API and ingestion remain ordered after the schema
candidate is accepted.

Scheme A remains fail-closed. No concrete CNIPA source, URL, query channel, dataset, file, role,
seed or permissive default is introduced. Missing, stale, unreviewed, revoked, ambiguous or
hash/version-mismatched authority remains `409 / NO WRITE / NO LEGAL-STATE CHANGE`. Shared schema,
service, router and SQLite ownership remains serialized.

Fresh independent verification passed: focused pytest `4 passed`, scoped Ruff passed, exact
two-file diff and `git diff --check` passed, and every bound task/source hash recomputed exactly.
The cumulative patch SHA-256 is
`a3fd601b69577862c80e6fc8515b021df4d2371b03977f6c665b445bbb62904c`; the exact two-path Git
tree fingerprint is
`a14e65e7929a6a3f74f1777e6cad479ae716d364d0f89b77bb868abc32e249c7`.
