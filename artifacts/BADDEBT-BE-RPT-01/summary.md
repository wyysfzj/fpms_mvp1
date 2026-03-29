# BADDEBT-BE-RPT-01 Evidence Summary

- Scope: `GET /bills` bad-debt status filter and list-level summary fields only.
- Verification:
  - `ruff check backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/tests/test_billing_bad_debt_reporting.py` -> pass
  - `ruff format backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/tests/test_billing_bad_debt_reporting.py` -> pass
  - `cd backend && pytest -q tests/test_billing_bad_debt_reporting.py` -> pass
- Notes:
  - Existing worktree was dirty, so baseline artifact snapshots were recorded under this task directory.
  - The list response keeps the existing `items`, `page`, `page_size`, and `total` envelope fields and adds top-level bad-debt summary fields.
