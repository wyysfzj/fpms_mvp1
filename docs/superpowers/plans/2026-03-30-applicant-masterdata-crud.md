# MD-APP Implementation Plan

## Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: chained (BE -> FE)
- evidence_cost: medium

## chosen_runbook
- P0-frontend-heavy-story

## Batch Manifest

### MDAPP-BE-01
- task file path: `tasks/postenhancement/backend/MDAPP-BE-01.md`
- closure slice: complete Applicant backend CRUD contract for create, update, and enable/disable on top of the existing list skeleton and prerequisite governance
- explicit non-closure: no frontend work, no selector/case linkage, no delete/detail/import-export, no schema changes
- allowlist:
  - `backend/app/modules/masterdata/applicants/api.py`
  - `backend/app/modules/masterdata/applicants/schemas.py`
  - `backend/app/modules/masterdata/applicants/service.py`
  - `backend/tests/test_applicant_masterdata_api.py`
- verification:
  - `python3 -m ruff check backend/app/modules/masterdata/applicants/api.py backend/app/modules/masterdata/applicants/schemas.py backend/app/modules/masterdata/applicants/service.py backend/tests/test_applicant_masterdata_api.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_applicant_masterdata_api.py`
  - `./scripts/task_validate.sh MDAPP-BE-01`
- dependency notes: first wave; FE depends on stable contract

### MDAPP-FE-01
- task file path: `tasks/postenhancement/frontend/MDAPP-FE-01.md`
- closure slice: complete Applicant masterdata management UI in `ApplicantList.vue` with list, create, edit, and enable/disable on the stable settings route
- explicit non-closure: no selector/case linkage, no import/export, no delete/detail, no new second management page
- allowlist:
  - `frontend/src/api/masterdata.ts`
  - `frontend/src/api/masterdata.types.ts`
  - `frontend/src/modules/settings/pages/ApplicantList.vue`
- verification:
  - `cd frontend && npm run lint -- src/api/masterdata.ts src/api/masterdata.types.ts src/modules/settings/pages/ApplicantList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh MDAPP-FE-01`
- dependency notes: serialize after `MDAPP-BE-01`

### MDAPP-QA-01
- task file path: `tasks/postenhancement/backend/MDAPP-QA-01.md`
- closure slice: gate audit, evidence audit, and story close summary for `MD-APP`
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/MDAPP-BE-01/**`
  - `artifacts/MDAPP-FE-01/**`
  - `artifacts/MDAPP-QA-01/**`
- verification:
  - `./scripts/task_validate.sh MDAPP-BE-01`
  - `./scripts/task_validate.sh MDAPP-FE-01`
  - `./scripts/task_validate.sh MDAPP-QA-01`
- dependency notes: final wave after BE and FE pass

## Waves
- Wave 1: `MDAPP-BE-01`
- Wave 2: `MDAPP-FE-01`
- Wave 3: `MDAPP-QA-01`

## Serialized Shared-file Decisions
- `backend/app/modules/masterdata/applicants/api.py|service.py|schemas.py` are owned only by `MDAPP-BE-01`
- `frontend/src/modules/settings/pages/ApplicantList.vue` is owned only by `MDAPP-FE-01`
- `frontend/src/api/masterdata.ts|masterdata.types.ts` are owned only by `MDAPP-FE-01`
