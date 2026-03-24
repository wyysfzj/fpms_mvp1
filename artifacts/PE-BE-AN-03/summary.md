# PE-BE-AN-03 Evidence Summary

## Task
- ID: PE-BE-AN-03
- Runbook: `tasks/postenhancement/backend/PE-BE-AN-03.md`

## Scope Compliance
- Product-code changes restricted to allowlist:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`

## Implemented
- Added endpoint `PUT /annuity/tasks/{task_id}/instruction`.
- Enforced permission dependency via `Depends(require_perm("AnnuityTask.Action"))`.
- Added instruction update service logic with legal transition checks.
- Status semantics implemented:
  - `400`: invalid instruction value or invalid instruction transition
  - `404`: annuity task not found
  - `409`: task in conflict state (terminal status)
- Kept module response style as object/list dict envelopes.

## Verification
- `cd backend && pytest -q` -> PASS (`141 passed, 3 warnings in 30.13s`)
