# Story V8-OVERLAY-DECISION-GATE-JOIN-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Contract commits: `62f33d6`, `c13b90b`.
- Product/test commit: `5c125164`.
- Catalog ID: `FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01` (ordinal `263`).
- Outcome: return the exact persisted 29-entry customer-decision snapshot on every overlay read.

Each invocation reuses its one timezone-naive UTC `generated_at` and caller session for seven
case-scoped commands followed by `form-001..form-022`. Resolved results are copied losslessly;
only the seven frozen 409 codes become independent unresolved entries. Invalid resolver contracts
map to the exact overlay 409, while every other error stops and propagates.

The saved RED proved the empty predecessor. GREEN plus the exact predecessor assertion migration
passed 116 decision/fee/document/center/read-service tests. Scoped Ruff, format and diff checks
passed; independent High review approved P0/P1/P2 all zero.

No gate mutation, source classification, fee/document/pagination, endpoint/UI, schema or adjacent
change is included. Rollback reverts the one product/test commit and this adoption; prior overlay
facts remain accepted.
