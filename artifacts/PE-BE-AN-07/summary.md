# PE-BE-AN-07 Evidence Summary

## Task
- ID: PE-BE-AN-07
- Runbook: `tasks/postenhancement/backend/PE-BE-AN-07.md`

## Scope Compliance
- Product-code changes restricted to allowlist:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`

## Implemented
- Added endpoint: `POST /gov-payments`.
- Permission injection:
  - `_perm: None = Depends(require_perm("GovPayment.Create"))`
- Added service logic: `register_gov_payment(...)`.
  - Duplicate protection (`GOV_PAYMENT_DUPLICATE`, status `409`)
  - Supports registration against existing planned pay-list line or creating a line from fee item if missing
  - Validates pay-list/fee-item scope compatibility
- Added pay-list status recompute helper:
  - recalculates status to `DRAFT` / `PARTIAL` / `PAID` after registration
  - updates `paid_date` and recomputed `total_amount`

## Verification
- `cd backend && python3 -m py_compile app/modules/annuity/api.py` -> PASS
- `cd backend && python3 -m py_compile app/modules/annuity/service.py` -> PASS
- `cd backend && pytest -q` -> PASS (`141 passed, 3 warnings in 30.27s`)
