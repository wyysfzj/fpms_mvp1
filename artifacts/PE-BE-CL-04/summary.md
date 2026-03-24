# PE-BE-CL-04 Evidence Summary

## Task
- ID: PE-BE-CL-04
- Runbook: `tasks/postenhancement/backend/PE-BE-CL-04.md`

## Scope Compliance
- Product-code changes restricted to allowlist:
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`

## Implemented
- Added endpoint: `POST /bills/{bill_id}/bad-debt`.
- Permission injection (parameter style):
  - `_perm: None = Depends(require_perm("BadDebt.Action"))`
- Added service logic: `mark_bill_bad_debt(...)`.
  - `404` when bill is not found
  - `409` when bill already in `BAD_DEBT`
  - `400` when not eligible:
    - `balance <= 0`
    - bill in terminal invalid states (`SETTLED`, `CANCELLED`, `VOID`, `WRITEOFF`)
- Success updates bill status to `BAD_DEBT` and returns key bill fields.
- Existing dunning endpoints (`POST /dunning`, `GET /dunning`) remain intact.

## Verification
- Wrapper lint step:
  - `./scripts/evidence_run.sh PE-BE-CL-04 lint bash -lc 'cd backend && ruff check app/modules/collections/api.py app/modules/collections/service.py && ruff format --check app/modules/collections/api.py app/modules/collections/service.py'`
  - Result: PASS (`rc=0`)
- Wrapper test step:
  - `./scripts/evidence_run.sh PE-BE-CL-04 test bash -lc 'cd backend && pytest -q'`
  - Result: PASS (`141 passed, 3 warnings in 30.21s`)
