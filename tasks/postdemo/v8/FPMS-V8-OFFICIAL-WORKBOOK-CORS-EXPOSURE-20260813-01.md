# FPMS-V8-OFFICIAL-WORKBOOK-CORS-EXPOSURE-20260813-01

Status: CURRENT_VERIFIED_NOT_ADOPTED
Risk: PROTECTED — API/security boundary
Catalog rows: successor support for 216, 217 and 278; no new catalog row

## Observable outcome

A browser origin already allowed by FPMS CORS can read the exact response metadata emitted by
`POST /pay-lists/{pay_list_id}/official-workbook`, so the existing frontend adapter can validate
the server filename, artifact identity, hashes, input version and CREATED/REUSED disposition and
then start the download.

## Exact closure

- Add `Access-Control-Expose-Headers` for the seven headers actually returned by the approved
  official-workbook endpoint: `Content-Disposition`, `X-FPMS-Artifact-Id`,
  `X-FPMS-Content-SHA256`, `X-FPMS-Template-Version`,
  `X-FPMS-Template-Content-SHA256`, `X-FPMS-Workbook-Input-Version-Id`, and
  `X-FPMS-Workbook-Disposition`.
- Prove the middleware behavior for both configured localhost and expanded loopback origins.

## Non-goals

No route, payload, permission, transaction, workbook, acceptance, payment, ticket, origin,
credential, schema, migration or production-input-gate change. Do not expose a header that the
endpoint does not emit.

## Dependencies

- Approved row216 backend download response.
- Approved row217 frontend response parser.
- Row278 real-browser failure: endpoint returned 201 but no browser download because metadata
  headers were not exposed.

## Allowed paths

- `backend/app/main.py`
- `backend/tests/test_v8_official_workbook_cors_headers.py`
- `tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-CORS-EXPOSURE-20260813-01.md`

## Verification

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_v8_official_workbook_cors_headers.py`
- Scoped lint: `cd backend && .venv/bin/ruff check app/main.py tests/test_v8_official_workbook_cors_headers.py`
- Scope: `git diff --check -- backend/app/main.py backend/tests/test_v8_official_workbook_cors_headers.py tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-CORS-EXPOSURE-20260813-01.md`

## Rollback boundary

Revert the exact story commit; the previous fail-closed browser behavior returns, while backend
workbook generation remains unchanged.
