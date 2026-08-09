# Story V8-OVERLAY-CENTER-QUERY-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Contract commits: `a239cf3`, `adc08d4`, `94b3a5c`, `34fb5a4`.
- Product commits: `a71adf9`, `cac66ae`, `4d8c2e0`.
- Catalog ID: `FPMS-V8-OVERLAY-CENTER-QUERY-20260712-01` (ordinal `260`).
- Outcome: one read-only activity-ledger projection supplies the centered lifecycle snapshot
  and ordered three-lane milestones at one frozen revision.

The service treats a fully unmanaged legacy case as revision zero, validates exact query
boundaries, reconstructs center state only from lifecycle activities, preserves document and
fee milestones with empty center-change mappings, and projects deterministic evidence links.
Current reads fail closed on gaps, overflow, invalid enums, lane mutations or case/ledger
projection mismatch. Explicit historical reads validate only their frozen `1..R` range, so a
later bad activity cannot rewrite an earlier snapshot.

The initial RED failed during collection because the service module did not exist. Focused
GREEN reached `16 passed`; scoped Ruff, format and diff checks passed. Independent High review
rejected two candidates for historical/current revision-boundary gaps. Both were corrected and
the three-commit product range was approved with P0/P1/P2 all zero.

No document/fee/work-package/task join, decision-gate resolution, pagination, endpoint, UI,
schema, write, flush, commit or rollback is included. Rollback reverts the three product
commits and this ledger adoption; later overlay owners remain separate successor stories.
