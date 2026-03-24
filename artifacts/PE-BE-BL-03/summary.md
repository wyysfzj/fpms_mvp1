# PE-BE-BL-03

Status: PASS

Atomic Task File:
- `tasks/postenhancement/backend/PE-BE-BL-03.md`

Covered Items:
- `US-BL-07`
- `FR-BL-09`

Exact Closure Slice:
- payment list read-path now exposes prepayment allocation progress via `allocated_amt`, `unapplied_amt`, `line_count`, and `prepayment_status`, so the existing payment/offset flow can show whether a payment remains in prepayment state.

Explicit Non-Closure:
- does not change offset creation or reversal business rules
- does not change manual bill API contract
- does not change dunning / bad-debt behavior
- does not introduce Batch 5 commission-facing indicators

Incremental Implementation:
- `backend/app/modules/billing/api.py`: enriched `GET /payments` list items with aggregated payment-line allocation fields and a deterministic prepayment status.
- `backend/tests/test_b5_billing_polish.py`: added focused regression proving payment list visibility moves from unallocated prepayment to fully allocated and back after offset reversal.

Dirty Baseline Handling:
- allowlist files were already dirty before this task began.
- acceptance for this task is scoped only to the payment-list prepayment visibility delta recorded after `artifacts/PE-BE-BL-03/baseline_allowlist.diff`.
- historical billing / collections diffs outside this delta are not counted toward this task closure.

Validation:
- `ruff check backend/app/modules/billing/api.py backend/app/modules/billing/service.py backend/app/modules/collections/service.py backend/tests/test_b5_billing_polish.py backend/tests/test_collections_e2e.py`
- `cd backend && pytest -q tests/test_b5_billing_polish.py tests/test_collections_e2e.py -k 'offset or payment or receipt'`

Notes:
- no schema/migration changes
- no Batch 5 spillover
- one backend visibility slice only
