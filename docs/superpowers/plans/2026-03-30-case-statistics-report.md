# RPT-CASE Implementation Plan

## Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: chained (BE -> FE)
- evidence_cost: medium

## chosen_runbook
- P0-frontend-heavy-story

## Batch Manifest

### CASERPT-BE-01
- task file path: `tasks/postenhancement/backend/CASERPT-BE-01.md`
- closure slice: extend `GET /cases` with approved case-report filters and summary payload for count/status/type/time-range reporting
- explicit non-closure: no schema changes, no frontend changes, no charts/maps/export
- allowlist:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/service.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/tests/test_case_report.py`
- verification:
  - `python3 -m ruff check backend/app/modules/cases/api.py backend/app/modules/cases/service.py backend/app/modules/cases/schemas.py backend/tests/test_case_report.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_case_report.py`
  - `./scripts/task_validate.sh CASERPT-BE-01`
- dependency notes: first wave; FE depends on this contract being frozen

### CASERPT-FE-01
- task file path: `tasks/postenhancement/frontend/CASERPT-FE-01.md`
- closure slice: complete the first-round case statistics report UI in `CaseList.vue` with approved filters, summary cards, and existing detail list
- explicit non-closure: no new `CaseReport.vue`, no charts/maps/export, no backend edits beyond types/API client files
- allowlist:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/CaseList.vue`
- verification:
  - `cd frontend && npm run lint -- src/api/cases.ts src/api/cases.types.ts src/modules/cases/pages/CaseList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh CASERPT-FE-01`
- dependency notes: serialize after `CASERPT-BE-01`

### CASERPT-QA-01
- task file path: `tasks/postenhancement/backend/CASERPT-QA-01.md`
- closure slice: gate audit, evidence audit, and story close summary for `RPT-CASE`
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/CASERPT-BE-01/**`
  - `artifacts/CASERPT-FE-01/**`
  - `artifacts/CASERPT-QA-01/**`
- verification:
  - `./scripts/task_validate.sh CASERPT-BE-01`
  - `./scripts/task_validate.sh CASERPT-FE-01`
  - `./scripts/task_validate.sh CASERPT-QA-01`
- dependency notes: final wave after BE and FE pass

## Waves
- Wave 1: `CASERPT-BE-01`
- Wave 2: `CASERPT-FE-01`
- Wave 3: `CASERPT-QA-01`

## Serialized Shared-file Decisions
- `backend/app/modules/cases/api.py|service.py|schemas.py` are owned only by `CASERPT-BE-01`
- `frontend/src/api/cases.ts|cases.types.ts|CaseList.vue` are owned only by `CASERPT-FE-01`
