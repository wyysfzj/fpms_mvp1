# 2026-04-05 Annuity Report Success-Rate Implementation Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `resolved by prior semantics freeze`
- `be_fe_coupling`: `shared summary contract across API client and AnnuityTaskList page`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

### `ANNRPT-SUCCESS-BE-01`

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
  - success-rate summary contract and service aggregation
- non-closure
  - no frontend rendering, no grouped success breakdown, no chart/export

### `ANNRPT-SUCCESS-FE-01`

- owner: frontend worker
- allowlist
  - `frontend/src/api/annuity.ts`
  - `frontend/src/api/annuity.types.ts`
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
- verification
  - `cd frontend && npm run lint -- src/api/annuity.ts src/api/annuity.types.ts src/modules/annuity/pages/AnnuityTaskList.vue`
  - `cd frontend && npm run typecheck`
- closure slice
  - render success-rate summary metrics on existing annuity report page
- non-closure
  - no backend aggregation, no grouped success breakdown, no chart/export

### `ANNRPT-SUCCESS-QA-01`

- owner: main thread / QA
- allowlist
  - `artifacts/ANNRPT-SUCCESS-BE-01/**`
  - `artifacts/ANNRPT-SUCCESS-FE-01/**`
  - `artifacts/ANNRPT-SUCCESS-QA-01/**`
  - `tasks/postenhancement/backend/ANNRPT-SUCCESS-QA-01.md`
- verification
  - `./scripts/task_validate.sh ANNRPT-SUCCESS-BE-01`
  - `./scripts/task_validate.sh ANNRPT-SUCCESS-FE-01`
  - `./scripts/task_validate.sh ANNRPT-SUCCESS-QA-01`
- closure slice
  - evidence and exact-closure audit for success-rate residual slice
- non-closure
  - no product-code changes
