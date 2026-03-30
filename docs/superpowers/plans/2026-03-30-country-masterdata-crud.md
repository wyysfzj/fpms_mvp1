# MD-CTR Implementation Plan

## Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: chained (BE -> FE)
- evidence_cost: medium

## chosen_runbook
- P0-frontend-heavy-story

## Batch Manifest

### MDCTR-BE-01
- task file path: `tasks/postenhancement/backend/MDCTR-BE-01.md`
- closure slice: complete Country backend CRUD contract for create, update, and enable/disable on top of the existing list skeleton and prerequisite governance
- explicit non-closure: no frontend work, no selector/case linkage, no delete/detail/import-export, no schema changes
- allowlist:
  - `backend/app/modules/masterdata/countries/api.py`
  - `backend/app/modules/masterdata/countries/schemas.py`
  - `backend/app/modules/masterdata/countries/service.py`
  - `backend/tests/test_country_masterdata_api.py`
- verification:
  - `python3 -m ruff check backend/app/modules/masterdata/countries/api.py backend/app/modules/masterdata/countries/schemas.py backend/app/modules/masterdata/countries/service.py backend/tests/test_country_masterdata_api.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_country_masterdata_api.py`
  - `./scripts/task_validate.sh MDCTR-BE-01`
- dependency notes: first wave; FE depends on stable contract

### MDCTR-FE-01
- task file path: `tasks/postenhancement/frontend/MDCTR-FE-01.md`
- closure slice: complete Country masterdata management UI in `CountryList.vue` with list, create, edit, and enable/disable on the stable settings route
- explicit non-closure: no selector/case linkage, no import/export, no delete/detail, no new second management page
- allowlist:
  - `frontend/src/api/masterdata.ts`
  - `frontend/src/api/masterdata.types.ts`
  - `frontend/src/modules/settings/pages/CountryList.vue`
- verification:
  - `cd frontend && npm run lint -- src/api/masterdata.ts src/api/masterdata.types.ts src/modules/settings/pages/CountryList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh MDCTR-FE-01`
- dependency notes: serialize after `MDCTR-BE-01`

### MDCTR-QA-01
- task file path: `tasks/postenhancement/backend/MDCTR-QA-01.md`
- closure slice: gate audit, evidence audit, and story close summary for `MD-CTR`
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/MDCTR-BE-01/**`
  - `artifacts/MDCTR-FE-01/**`
  - `artifacts/MDCTR-QA-01/**`
- verification:
  - `./scripts/task_validate.sh MDCTR-BE-01`
  - `./scripts/task_validate.sh MDCTR-FE-01`
  - `./scripts/task_validate.sh MDCTR-QA-01`
- dependency notes: final wave after BE and FE pass

## Waves
- Wave 1: `MDCTR-BE-01`
- Wave 2: `MDCTR-FE-01`
- Wave 3: `MDCTR-QA-01`

## Serialized Shared-file Decisions
- `backend/app/modules/masterdata/countries/api.py|service.py|schemas.py` are owned only by `MDCTR-BE-01`
- `frontend/src/modules/settings/pages/CountryList.vue` is owned only by `MDCTR-FE-01`
- `frontend/src/api/masterdata.ts|masterdata.types.ts` are owned only by `MDCTR-FE-01`
