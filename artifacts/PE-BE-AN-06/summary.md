# PE-BE-AN-06 Evidence Summary

## Task
- ID: PE-BE-AN-06
- Runbook: `tasks/postenhancement/backend/PE-BE-AN-06.md`

## Scope Compliance
- Product-code changes restricted to allowlist:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`

## Implemented
- Added endpoint: `POST /pay-lists/from-fee-items`.
- Added service: `create_pay_list_from_fee_items(...)`.
- Enforced same client and same currency constraints across selected fee items/drafts.
- Added batch-style result contract:
  - `summary`, `pay_list`, `success`, `failed`.
- Included item-level checks for:
  - missing fee item
  - non-GOV fee type
  - duplicate gov payment registration
  - missing client/currency/case_id
  - scope mismatch (client/currency)
- Creates `PayList` and related `GovPayment` lines for accepted items.

## Verification
- `cd backend && python3 -m py_compile app/modules/annuity/api.py` -> PASS
- `cd backend && python3 -m py_compile app/modules/annuity/service.py` -> PASS
- `cd backend && pytest -q` -> PASS (`141 passed, 3 warnings in 30.24s`)
