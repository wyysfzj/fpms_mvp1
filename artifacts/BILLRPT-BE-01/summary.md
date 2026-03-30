# BILLRPT-BE-01 Evidence Summary

## Scope
- Backend-only billing report contract slice for `GET /bills`.
- Added reporting filters, nested summary block, and aging metadata.

## Closure completed
- `GET /bills` now supports the billing report/list contract for the first-round report slice.
- Query support added for client, status/bill_status, currency, bill date range, aging bucket, overdue, and bad debt filters.
- Response now includes a stable `summary` block while preserving legacy top-level bad-debt fields.
- List items are enriched with overdue / aging metadata for the follow-up FE slice.

## Verification
- `python3 -m ruff check backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/tests/test_billing_report.py` ✅
- `cd backend && PYTHONPATH=. pytest -q tests/test_billing_report.py` ✅
- `./scripts/task_validate.sh BILLRPT-BE-01` ✅

## Notes
- No schema changes.
- No frontend edits.
- Legacy bad-debt summary fields remain present at the top level.
