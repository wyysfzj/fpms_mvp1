# PE-BE-QA-01 Evidence Summary

## Task
- Task ID: `PE-BE-QA-01`
- Task file: `tasks/postenhancement/backend/PE-BE-QA-01.md`
- Scope (allowlist):
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/fees/api.py`
  - `backend/app/modules/billing/api.py`

## Implemented
1. Replaced all allowlisted business `HTTPException(..., detail=...)` branches with `raise_business_error(...)`.
2. Preserved HTTP status codes per original branch.
3. Applied canonical error codes from freeze.
4. Preserved success contracts and permission dependencies.
5. Removed now-unused `HTTPException` imports; added `raise_business_error` imports.

## Canonical Mappings Applied
- Cases API:
  - `CASE_INVALID` (400): `case_no is required`
  - `CASE_NO_DUPLICATE` (409): create conflict `case_no already exists`
  - `CASE_NO_DUPLICATE` (400): update validation conflict `case_no already exists`
  - `CASE_NOT_FOUND` (404): case-not-found branches
- Fees API:
  - `FEE_ITEM_NOT_FOUND` (404)
  - `FEE_DRAFT_NOT_FOUND` (404)
- Billing API:
  - `BILL_NOT_FOUND` (404)
  - `CLIENT_NOT_FOUND` (404)
  - `BILL_TEMPLATE_NOT_CONFIGURED` (409)
  - `BILL_TEMPLATE_FILE_MISSING` (500)
  - `PAYMENT_NOT_FOUND` (404)
  - `BILL_INVALID` (400): `client_id is required`
  - `CASE_RECEIPT_NOT_FOUND` (404)

## Verification
- `./scripts/evidence_run.sh PE-BE-QA-01 lint bash -lc 'cd backend && ruff check app/modules/cases/api.py app/modules/fees/api.py app/modules/billing/api.py && ruff format --check app/modules/cases/api.py app/modules/fees/api.py app/modules/billing/api.py'`
  - `rc=0`
- `./scripts/evidence_run.sh PE-BE-QA-01 test bash -lc 'cd backend && pytest -q'`
  - `rc=0` (`141 passed, 3 warnings`)

## Notes
- Business errors now consistently flow through the global error envelope handler.
- No success payload/status behavior was changed.

## Evidence Files
- `artifacts/PE-BE-QA-01/results.jsonl`
- `artifacts/PE-BE-QA-01/summary.md`
- `artifacts/PE-BE-QA-01/git/diff.patch`
