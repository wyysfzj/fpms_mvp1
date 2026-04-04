# 2026-04-05 Annuity Report Amount Implementation Plan

- Story Shape Classification
  - `shared_file_density`: medium
  - `prereq_dependency_density`: medium
  - `be_fe_coupling`: medium
  - `evidence_cost`: medium
- `chosen_runbook`: `P0-frontend-heavy-story`

## Batch Manifest

### `ANNRPT-AMOUNT-BE-01`

- owner: backend worker
- allowlist
  - `backend/app/modules/annuity/service.py`
  - `backend/app/modules/annuity/schemas.py`
  - `backend/tests/test_annuity_report.py`
- verification
  - `python3 -m ruff format backend/app/modules/annuity/schemas.py backend/app/modules/annuity/service.py backend/tests/test_annuity_report.py`
  - `python3 -m ruff check backend/app/modules/annuity/api.py backend/app/modules/annuity/service.py backend/app/modules/annuity/schemas.py backend/tests/test_annuity_report.py`
  - `cd backend && pytest -q tests/test_annuity_report.py`
- closure slice
  - grouped amount summary contract and service aggregation for `client / country / year`
- non-closure
  - no frontend rendering, no success-rate, no export/chart

### `ANNRPT-AMOUNT-FE-01`

- owner: frontend worker
- allowlist
  - `frontend/src/api/annuity.ts`
  - `frontend/src/api/annuity.types.ts`
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
- verification
  - `cd frontend && npm run lint -- src/api/annuity.ts src/api/annuity.types.ts src/modules/annuity/pages/AnnuityTaskList.vue`
  - `cd frontend && npm run typecheck`
- closure slice
  - render grouped amount summaries in existing annuity report page
- non-closure
  - no backend aggregation, no success-rate, no chart/export

### `ANNRPT-AMOUNT-QA-01`

- owner: main thread / QA
- allowlist
  - `artifacts/ANNRPT-AMOUNT-BE-01/**`
  - `artifacts/ANNRPT-AMOUNT-FE-01/**`
  - `artifacts/ANNRPT-AMOUNT-QA-01/**`
  - `tasks/postenhancement/backend/ANNRPT-AMOUNT-QA-01.md`
- verification
  - `./scripts/task_validate.sh ANNRPT-AMOUNT-BE-01`
  - `./scripts/task_validate.sh ANNRPT-AMOUNT-FE-01`
  - `./scripts/task_validate.sh ANNRPT-AMOUNT-QA-01`
- closure slice
  - evidence and exact-closure audit for grouped amount residual slice
- non-closure
  - no product-code changes

## Serialized Ownership

- `backend/app/modules/annuity/service.py|schemas.py|backend/tests/test_annuity_report.py` must be owned by BE wave first.
- `frontend/src/api/annuity.ts|annuity.types.ts|AnnuityTaskList.vue` must be owned by FE wave after backend contract lands.
