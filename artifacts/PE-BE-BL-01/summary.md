# PE-BE-BL-01

Status: PASS

Atomic Task File:
- `tasks/postenhancement/backend/PE-BE-BL-01.md`

Covered Items:
- `US-BL-02`
- `FR-BL-01`
- `FR-BL-03`

Exact Closure Slice:
- `POST /bills/manual` contract hardening only: typed payload, AR/AP direction support, explicit item rows, and deterministic total/status initialization.

Explicit Non-Closure:
- does not close BillCreate frontend parity
- does not close bad-debt or dunning behavior
- does not close prepayment or offset visibility
- does not close bill detail/list query parity

Incremental Implementation:
- `backend/app/modules/billing/schemas.py`: added `BillManualItemSchema` and `BillManualCreateSchema` using Pydantic v2-compatible constraints.
- `backend/app/modules/billing/service.py`: added `create_manual_bill_record` with explicit item-row total calculation and deterministic status initialization via existing status rules.
- `backend/app/modules/billing/api.py`: changed `/bills/manual` to consume typed payload and return manual-bill amount/balance/items in the create response.
- `backend/tests/test_b5_billing_polish.py`: added focused coverage for empty-item rejection, manual AP bill creation with items, and invalid status rejection.

Dirty Baseline Handling:
- allowlist files already had pre-existing dirty diffs before this task began.
- acceptance for this task is scoped only to the manual-bill contract hardening delta recorded after `artifacts/PE-BE-BL-01/baseline_allowlist.diff`.
- historical `get_bill` / `case receipt` diff in the same files is not counted toward this task closure.

Validation:
- `ruff check backend/app/modules/billing/api.py backend/app/modules/billing/service.py backend/app/modules/billing/schemas.py backend/tests/test_b5_billing_polish.py`
- `cd backend && pytest -q tests/test_b5_billing_polish.py -k 'manual_bill'`

Notes:
- no schema/migration changes
- no Batch 5 spillover
- no document generation behavior added
- this is one backend closure slice only
