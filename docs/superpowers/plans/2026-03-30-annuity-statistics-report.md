# RPT-ANN Implementation Plan

## Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: chained (BE -> FE)
- evidence_cost: medium

## chosen_runbook
- P0-frontend-heavy-story

## Batch Manifest

### ANNRPT-BE-01
- task file path: `tasks/postenhancement/backend/ANNRPT-BE-01.md`
- closure slice: extend `GET /annuity/tasks` with approved annuity-report filters and summary payload for first-round due/status/year reporting
- explicit non-closure: no schema changes, no frontend changes, no charts/export/predictive reminder analytics, no full payment-linkage expansion
- allowlist:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
  - `backend/app/modules/annuity/schemas.py`
  - `backend/tests/test_annuity_report.py`
- verification:
  - `python3 -m ruff check backend/app/modules/annuity/api.py backend/app/modules/annuity/service.py backend/app/modules/annuity/schemas.py backend/tests/test_annuity_report.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_annuity_report.py`
  - `./scripts/task_validate.sh ANNRPT-BE-01`
- dependency notes: first wave; FE depends on this contract being frozen

### ANNRPT-FE-01
- task file path: `tasks/postenhancement/frontend/ANNRPT-FE-01.md`
- closure slice: complete the first-round annuity statistics report UI in `AnnuityTaskList.vue` with approved filters, summary cards, and existing detail list
- explicit non-closure: no new `AnnuityReport.vue`, no backend changes outside API client/types, no charts/export/predictive reminder analytics, no pay-list/payment linkage UI
- allowlist:
  - `frontend/src/api/annuity.ts`
  - `frontend/src/api/annuity.types.ts`
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`
- verification:
  - `cd frontend && npm run lint -- src/api/annuity.ts src/api/annuity.types.ts src/modules/annuity/pages/AnnuityTaskList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh ANNRPT-FE-01`
- dependency notes: serialize after `ANNRPT-BE-01`

### ANNRPT-QA-01
- task file path: `tasks/postenhancement/backend/ANNRPT-QA-01.md`
- closure slice: gate audit, evidence audit, and story close summary for `RPT-ANN`
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/ANNRPT-BE-01/**`
  - `artifacts/ANNRPT-FE-01/**`
  - `artifacts/ANNRPT-QA-01/**`
- verification:
  - `./scripts/task_validate.sh ANNRPT-BE-01`
  - `./scripts/task_validate.sh ANNRPT-FE-01`
  - `./scripts/task_validate.sh ANNRPT-QA-01`
- dependency notes: final wave after BE and FE pass

## Waves
- Wave 1: `ANNRPT-BE-01`
- Wave 2: `ANNRPT-FE-01`
- Wave 3: `ANNRPT-QA-01`

## Serialized Shared-file Decisions
- `backend/app/modules/annuity/api.py|service.py|schemas.py` are owned only by `ANNRPT-BE-01`
- `frontend/src/api/annuity.ts|annuity.types.ts|AnnuityTaskList.vue` are owned only by `ANNRPT-FE-01`
