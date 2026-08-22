# Independent Review — Grant-evidence Source Carrier Schema

- Review class: `PROTECTED`.
- Reviewed commits: `35a72b5354cec8a1704a3550daddea9085af093f`,
  `14f495db34b537e52441b985c7ab1bae2e5b082c`.
- Current successor prerequisite: `2868a5d7b065a7c7612a636f00c21244a2a0f0e8`.
- Verdict: `APPROVED`.
- P0/P1/P2: `0/0/0`.

The exact five-path candidate implements only the three fail-closed lineage carriers for reviewed
CNIPA source records, versioned GLOBAL source configuration and immutable grant-evidence
candidate provenance. Migration and ORM metadata contain the frozen `26 / 19 / 24` columns with
matching constraints, foreign keys and indexes. The migration has the exact predecessor,
introduces the unique head `v8_grant_source_carrier_01`, and is forward-only.

Scheme A remains configuration-required. The candidate inserts no production source,
configuration, candidate, role or default, and performs no legal-state or lifecycle change.
Source/configuration usability remains owned by later independently accepted services.

Fresh independent verification passed: focused GREEN `3 passed`, scoped Ruff passed, Alembic
reported exactly one head, direct ORM counts were `26 / 19 / 24`, and exact five-path diff checks
passed. The focused serialized SQLite verification covered clean upgrade, reflection,
constraints/FKs/indexes, zero new-table rows, preserved prior data and deletion restrictions.
The exact five-path Git tree fingerprint is
`197a3cfb84f8450021a91c19a290921d3a7ef0edcea4cd248d1db8b550e6e19d`.
