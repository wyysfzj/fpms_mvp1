# PE-BE-FE-04

Status: PASS

Scope:
- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/schemas.py`
- `backend/tests/test_annuity_e2e.py`

Changes:
- Added one Batch 3 read/query slice on `/cases/{case_id}/receipts`.
- Receipt response now includes a deduplicated `bills` overview list (id, bill_no, status, amount, balance, issue_date) for the case.
- Added `CaseReceiptBillResponse` and extended `CaseReceiptResponse` with `bills`.
- Added failing-then-passing integration test:
  - `test_case_receipt_endpoint_includes_bills_overview_list`
  - validates bill overview list presence and deduplication semantics.

Validation:
- `cd backend && pytest -q tests/test_annuity_e2e.py -k 'case_receipt_endpoint_includes_bills_overview_list'` (fails before fix, passes after)
- `ruff check backend/app/modules/fees/api.py backend/app/modules/fees/service.py backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k 'receipt or overview or pay_list or gov_payment'`

Notes:
- no schema/migration changes
- no bill write-path redesign
- no dunning / bad-debt / commission logic touched
- no document generation behavior added
