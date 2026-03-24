# PE-FE-BL-03

Status: PASS

Atomic Task File:
- `tasks/postenhancement/frontend/PE-FE-BL-03.md`

Covered Items:
- `US-BL-07`
- `FR-BL-09`

Exact Closure Slice:
- frontend payment visibility now surfaces prepayment allocation progress by showing a payment's prepayment status and unapplied amount in `PaymentList`, plus a minimal explanatory hint in `PaymentCreate`.

Explicit Non-Closure:
- does not redesign offset dialog or offset list behavior
- does not change manual bill page parity
- does not change dunning pages
- does not add commission-facing indicators

Incremental Implementation:
- `frontend/src/api/billing.types.ts`: added payment visibility fields for `allocated_amt`, `unapplied_amt`, `line_count`, and `prepayment_status`.
- `frontend/src/api/billing.ts`: mapped backend payment visibility fields into the frontend payment list model.
- `frontend/src/modules/billing/pages/PaymentList.vue`: added prepayment status and unapplied amount columns.
- `frontend/src/modules/billing/pages/PaymentCreate.vue`: added minimal UX hint and success copy for prepayment state.

Dirty Baseline Handling:
- allowlist files were already dirty before this task began.
- acceptance for this task is scoped only to the payment prepayment-visibility delta recorded after `artifacts/PE-FE-BL-03/baseline_allowlist.diff`.
- historical billing API/type diffs outside this slice are not counted toward this task closure.

Validation:
- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`

Notes:
- no Batch 5 spillover
- no document generation behavior added
- one frontend visibility slice only
