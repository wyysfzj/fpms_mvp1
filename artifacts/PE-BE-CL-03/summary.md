# PE-BE-CL-03 Evidence Summary

## Task
- ID: PE-BE-CL-03
- Runbook: `tasks/postenhancement/backend/PE-BE-CL-03.md`

## Scope Compliance
- Product-code changes restricted to allowlist:
  - `backend/app/modules/collections/api.py`

## Implemented
- Added endpoint `GET /dunning` with query + pagination.
- Supported filters:
  - `round_no`, `status`, `client_id`
- Pagination params:
  - `page`, `page_size`
- Permission injection exactly:
  - `_perm: None = Depends(require_perm("Dunning.Read"))`
- Response envelope:
  - `{items, page, page_size, total}`
- Included key dunning fields in each item:
  - `id`, `dunning_no`, `client_id`, `round_no`, `to_date`, `currency`, `total_amount`, `status`, `sent_date`, `remark`, `created_at`, `updated_at`
- Existing `POST /dunning` behavior remains unchanged.

## Verification
- Wrapper lint:
  - `./scripts/evidence_run.sh PE-BE-CL-03 lint bash -lc 'cd backend && ruff check app/modules/collections/api.py && ruff format --check app/modules/collections/api.py'`
  - First run failed due format check; file formatted and rerun passed.
- Wrapper test:
  - `./scripts/evidence_run.sh PE-BE-CL-03 test bash -lc 'cd backend && pytest -q'`
  - Passed (`141 passed, 3 warnings`).
