# Story V8-OVERLAY-DECISION-GATE-JOIN-CURRENT-CONTRACT

- Risk: `PROTECTED`
- Outcome: close catalog row `263` by projecting the exact 29 persisted customer-decision
  identities into each overlay invocation without activating or writing any lane.
- Catalog ID: `FPMS-V8-OVERLAY-DECISION-GATE-JOIN-20260712-01`.
- Authority: the row-263 Ultra freeze in its task file and Delta-2; this story binds but does
  not reinterpret that complete contract.
- Dependency: begin only after the row-262 fee-join successor is independently accepted.

## Exact closure

Reuse the single timezone-naive UTC `generated_at` already captured by
`read_lifecycle_overlay` as every resolver command's `as_of`. In the caller session, resolve
seven case-scoped codes in frozen enum order—application draft, grant-year draft, future
annuity, grant evidence source, grant manual review, payment workbook and service-rate
version—then `LEGACY_FORM_CLASS` for `form-001..form-022`. This is exactly 29 calls and the
returned tuple preserves that composite `(gate_code, requested_scope_key)` order. Never request
or output `requested_scope_key=ALL-22`; a resolver-selected legacy fallback may copy
`resolved_scope_key=ALL-22`.

Successful results project losslessly with `RESOLVED`. Only the seven exact frozen resolver
409 codes become independent `UNRESOLVED` entries with the unchanged reason and all nullable
record/source fields null. A 400 `DECISION_GATE_INVALID` becomes 409
`LIFECYCLE_OVERLAY_DECISION_GATE_CONTRACT_INVALID`. Every other business or unexpected error
propagates and stops later calls. Do not retry, query gate rows, duplicate precedence/fallback,
or alter the already-built center/document/fee data.

## Verification and non-goals

The focused test uses the public overlay seam and a resolver spy to prove exact order/count,
transaction identity, one shared clock, direct and `ALL-22` fallback projection, every mapped
error at first/middle/last positions, multiple unresolved entries, fatal stop/propagation and
read-only state. Run it with the accepted overlay contract/center/document/fee and decision-gate
read-service regressions, scoped Ruff/format/diff, then independent High review.

No gate record/revoke, lane activation, source classification, schema, endpoint/UI, pagination,
fee/document change or adjacent cleanup. Rollback reverts only the row-263 service/test change
and its adoption; prior overlay successors remain intact.
