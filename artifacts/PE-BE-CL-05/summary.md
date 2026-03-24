# PE-BE-CL-05 Evidence Summary

## Task
- ID: PE-BE-CL-05
- Runbook: `tasks/postenhancement/backend/PE-BE-CL-05.md`

## Scope Compliance
- Product-code changes restricted to allowlist:
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`

## Implemented
- Added endpoint: `POST /bills/{bill_id}/bad-debt/restore`.
- Permission injection uses required style:
  - `_perm: None = Depends(require_perm("BadDebt.Action"))`
- Added service logic: `restore_bill_from_bad_debt(...)`.
- Deterministic status mapping implemented exactly:
  - `balance == amount` => `UNSETTLED`
  - `0 < balance < amount` => `PARTIALLY_SETTLED`
  - `balance <= 0` => `SETTLED`
- Error semantics:
  - `404` bill not found
  - `409` when bill is not currently `BAD_DEBT`
  - `400` invalid restore preconditions (e.g., inconsistent financial state)
- Existing dunning and bad-debt mark endpoints remain unchanged.

## Verification
- Wrapper lint:
  - `./scripts/evidence_run.sh PE-BE-CL-05 lint bash -lc 'cd backend && ruff check app/modules/collections/api.py app/modules/collections/service.py && ruff format --check app/modules/collections/api.py app/modules/collections/service.py'`
  - Result: PASS (`rc=0`)
- Wrapper test:
  - `./scripts/evidence_run.sh PE-BE-CL-05 test bash -lc 'cd backend && pytest -q'`
  - Result: PASS (`141 passed, 3 warnings in 30.21s`)
