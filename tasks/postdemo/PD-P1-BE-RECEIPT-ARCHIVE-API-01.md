# PD-P1-BE-RECEIPT-ARCHIVE-API-01 — Receipt archive API

## Exact Closure Slice

Add backend API behavior for receipt/archive metadata: attach receipt PDF or merged PDF to a package, record receiving case number, submitter, receive time, received file list, archive status, and manual override.

## Explicit Non-Closure

No receipt auto-download. No OCR/extraction. No automatic official confirmation. No frontend implementation.

## Remaining Follow-Up Task IDs

- `PD-P1-FE-RECEIPT-ARCHIVE-01`
- `PD-P1-QA-FULLSCOPE-E2E-01`

## Allowed Files

- `backend/app/modules/official_workflows/api.py`
- `backend/app/modules/official_workflows/schemas.py`
- `backend/app/modules/official_workflows/service.py`
- `backend/app/api/router.py`
- `backend/app/modules/rbac/service.py`
- `backend/tests/test_pd_p1_receipt_archive_api.py`
- `tasks/postdemo/PD-P1-BE-RECEIPT-ARCHIVE-API-01.md`
- `artifacts/PD-P1-BE-RECEIPT-ARCHIVE-API-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/official_workflows backend/app/api/router.py backend/app/modules/rbac/service.py backend/tests/test_pd_p1_receipt_archive_api.py`
- `ruff format backend/app/modules/official_workflows backend/app/api/router.py backend/app/modules/rbac/service.py backend/tests/test_pd_p1_receipt_archive_api.py`
- `ruff check backend/app/modules/official_workflows backend/app/api/router.py backend/app/modules/rbac/service.py backend/tests/test_pd_p1_receipt_archive_api.py`
- `cd backend && pytest -q tests/test_pd_p1_receipt_archive_api.py`
- `./scripts/task_validate.sh PD-P1-BE-RECEIPT-ARCHIVE-API-01`

## Evidence Path

- `artifacts/PD-P1-BE-RECEIPT-ARCHIVE-API-01/`

## Acceptance

- Closing a filing package or OA package requires receipt/archive metadata unless override is recorded.
- Override stores actor, reason, timestamp, and follow-up responsibility.
