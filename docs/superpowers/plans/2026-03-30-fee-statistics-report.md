# RPT-FEE Implementation Plan

## Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: chained (BE -> FE)
- evidence_cost: medium

## chosen_runbook
- P0-frontend-heavy-story

## Batch Manifest

### FEERPT-BE-01
- task file path: `tasks/postenhancement/backend/FEERPT-BE-01.md`
- closure slice: extend `GET /fees/drafts` with approved fee-report filters and summary payload for first-round service fee / government fee / income reporting
- explicit non-closure: no schema changes, no frontend changes, no charts/export/profit analysis
- allowlist:
  - `backend/app/modules/fees/api.py`
  - `backend/app/modules/fees/service.py`
  - `backend/app/modules/fees/schemas.py`
  - `backend/tests/test_fee_report.py`
- verification:
  - `python3 -m ruff check backend/app/modules/fees/api.py backend/app/modules/fees/service.py backend/app/modules/fees/schemas.py backend/tests/test_fee_report.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_fee_report.py`
  - `./scripts/task_validate.sh FEERPT-BE-01`
- dependency notes: first wave; FE depends on this contract being frozen

### FEERPT-FE-01
- task file path: `tasks/postenhancement/frontend/FEERPT-FE-01.md`
- closure slice: complete the first-round fee statistics report UI in `FeeDraftList.vue` with approved filters, summary cards, and existing detail list
- explicit non-closure: no new `FeeReport.vue`, no backend changes outside API client/types, no charts/export/profit analysis
- allowlist:
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
  - `frontend/src/modules/fees/pages/FeeDraftList.vue`
- verification:
  - `cd frontend && npm run lint -- src/api/fees.ts src/api/fees.types.ts src/modules/fees/pages/FeeDraftList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh FEERPT-FE-01`
- dependency notes: serialize after `FEERPT-BE-01`

### FEERPT-QA-01
- task file path: `tasks/postenhancement/backend/FEERPT-QA-01.md`
- closure slice: gate audit, evidence audit, and story close summary for `RPT-FEE`
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/FEERPT-BE-01/**`
  - `artifacts/FEERPT-FE-01/**`
  - `artifacts/FEERPT-QA-01/**`
- verification:
  - `./scripts/task_validate.sh FEERPT-BE-01`
  - `./scripts/task_validate.sh FEERPT-FE-01`
  - `./scripts/task_validate.sh FEERPT-QA-01`
- dependency notes: final wave after BE and FE pass

## Waves
- Wave 1: `FEERPT-BE-01`
- Wave 2: `FEERPT-FE-01`
- Wave 3: `FEERPT-QA-01`

## Serialized Shared-file Decisions
- `backend/app/modules/fees/api.py|service.py|schemas.py` are owned only by `FEERPT-BE-01`
- `frontend/src/api/fees.ts|fees.types.ts|FeeDraftList.vue` are owned only by `FEERPT-FE-01`
