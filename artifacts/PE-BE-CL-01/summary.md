# PE-BE-CL-01 Evidence Summary

## Task
- ID: PE-BE-CL-01
- Runbook: `tasks/postenhancement/backend/PE-BE-CL-01.md`

## Scope Compliance
- Product-code changes restricted to allowlist:
  - `backend/app/modules/collections/service.py`

## Implemented
- Added overdue filtering service: `filter_overdue_bills(...)`.
  - cutoff rule: `due_date <= to_date`
  - positive outstanding rule: `balance > 0`
  - optional client scope and status include/exclude controls
- Added dunning snapshot generation service: `generate_dunning_batches(...)`.
  - groups overdue bills by `client_id + currency`
  - creates dunning head (`Dunning`) and line snapshots (`DunningLine`)
  - head `total_amount` equals sum of line outstanding snapshots
- Added idempotent generation behavior for same cutoff + eligible snapshot.
  - deterministic snapshot signature hash
  - re-run with identical input reuses existing batch and avoids duplicate head/line creation
  - optional strict conflict mode returns 409 semantics
- Kept error handling pattern with `raise_business_error` and consistent semantics.

## Verification
- Evidence wrapper lint step:
  - `./scripts/evidence_run.sh PE-BE-CL-01 lint bash -lc 'cd backend && ruff check app/modules/collections/service.py && ruff format --check app/modules/collections/service.py'`
  - First run failed due formatting check; file formatted; second run passed.
- Evidence wrapper test step:
  - `./scripts/evidence_run.sh PE-BE-CL-01 test bash -lc 'cd backend && pytest -q'`
  - Passed (`141 passed, 3 warnings`).
