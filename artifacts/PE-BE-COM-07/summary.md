# PE-BE-COM-07 Evidence Summary

## Task
- ID: `PE-BE-COM-07`
- Runbook: `tasks/postenhancement/backend/PE-BE-COM-07.md`

## Scope Compliance
- Product-code changes restricted to allowlist:
  - `backend/app/modules/commission/api.py`

## Implemented
- Added endpoint: `GET /commission`.
- Permission injection implemented exactly:
  - `_perm: None = Depends(require_perm("Commission.Read"))`
- Required filters supported:
  - `agent_id`
  - `case_id`
  - `status`
  - date range filters:
    - `settleable_date_from` / `settleable_date_to`
    - `created_at_from` / `created_at_to`
- Date-range business validation:
  - invalid range (`from > to`) raises `400` (`COMMISSION_FILTER_INVALID`)
- Pagination and envelope:
  - query params: `page`, `page_size`
  - response envelope: `{items, page, page_size, total}`
- Deterministic ordering:
  - `created_at DESC, id DESC`
- Existing commission rule endpoints (`GET/POST/PUT /commission/rules...`) kept unchanged.

## Verification
- Wrapper lint:
  - `./scripts/evidence_run.sh PE-BE-COM-07 lint bash -lc 'cd backend && ruff check app/modules/commission/api.py && ruff format --check app/modules/commission/api.py'`
  - Result: PASS (`rc=0`)
- Wrapper test:
  - `./scripts/evidence_run.sh PE-BE-COM-07 test bash -lc 'cd backend && pytest -q'`
  - Result: PASS (`141 passed, 3 warnings in 30.58s`)

## Evidence Files
- `artifacts/PE-BE-COM-07/results.jsonl`
- `artifacts/PE-BE-COM-07/summary.md`
- `artifacts/PE-BE-COM-07/git/diff.patch`
