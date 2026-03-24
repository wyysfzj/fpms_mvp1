# PE-BE-CL-02 Evidence Summary

## Task
- ID: PE-BE-CL-02
- Runbook: `tasks/postenhancement/backend/PE-BE-CL-02.md`

## Scope Compliance
- Product-code changes restricted to allowlist:
  - `backend/app/modules/collections/api.py`

## Implemented
- Added endpoint: `POST /dunning`.
- Added request model with frozen-contract fields:
  - required: `to_date`
  - optional: `client_id`, `client_ids`, `include_statuses`, `exclude_statuses`, `strict_conflict`
- Permission injection uses required parameter style:
  - `_perm: None = Depends(require_perm("Dunning.Create"))`
- Endpoint delegates to service:
  - `generate_dunning_batches(...)`
- Success response is HTTP 200 with service envelope:
  - `{ "summary": ..., "batches": [...] }`

## Verification
- Wrapper lint step:
  - `./scripts/evidence_run.sh PE-BE-CL-02 lint bash -lc 'cd backend && ruff check app/modules/collections/api.py && ruff format --check app/modules/collections/api.py'`
  - Result: PASS (`rc=0`)
- Wrapper test step:
  - `./scripts/evidence_run.sh PE-BE-CL-02 test bash -lc 'cd backend && pytest -q'`
  - Result: PASS (`141 passed, 3 warnings in 30.31s`)
