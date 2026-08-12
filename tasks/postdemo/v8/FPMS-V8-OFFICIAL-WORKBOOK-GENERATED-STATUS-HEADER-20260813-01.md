# FPMS-V8-OFFICIAL-WORKBOOK-GENERATED-STATUS-HEADER-20260813-01

Status: CURRENT_VERIFIED_NOT_ADOPTED
Risk: PROTECTED — evidence-lineage API response
Catalog rows: successor support for 216, 217, 218 and 278; no new catalog row

## Observable outcome

The official-workbook HTTP response carries the server-owned generation status already returned by
the generation service, allowing the approved frontend adapter/UI to display `GENERATED` without
deriving it from HTTP status, download success, PayList state, acceptance, payment or ticket facts.

## Exact closure

- Emit `X-FPMS-Generated-Status` from `GenerateOfficialPaymentWorkbookResult.generated_status`.
- Expose that newly emitted header to already allowed browser origins.
- Prove both created and reused responses carry the server value while preserving existing status,
  permission, response, transaction and compensation behavior.

## Non-goals

No generation-service, artifact, workbook, gate, permission, request, acceptance, payment, ticket,
schema, migration, UI, origin, credential, method or allowed-request-header change.

## Allowed paths

- `backend/app/modules/annuity/api.py`
- `backend/app/main.py`
- `backend/tests/test_v8_official_payment_workbook_api.py`
- `backend/tests/test_v8_official_workbook_cors_headers.py`
- `tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-GENERATED-STATUS-HEADER-20260813-01.md`

## Verification

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_v8_official_payment_workbook_api.py tests/test_v8_official_workbook_cors_headers.py`
- Scoped lint: `cd backend && .venv/bin/ruff check app/modules/annuity/api.py app/main.py tests/test_v8_official_payment_workbook_api.py tests/test_v8_official_workbook_cors_headers.py`
- Scope: `git diff --check -- backend/app/modules/annuity/api.py backend/app/main.py backend/tests/test_v8_official_payment_workbook_api.py backend/tests/test_v8_official_workbook_cors_headers.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-GENERATED-STATUS-HEADER-20260813-01.md`

## Rollback boundary

Revert the exact successor commit; generation remains functional but the browser again receives no
authoritative generated-status header.
