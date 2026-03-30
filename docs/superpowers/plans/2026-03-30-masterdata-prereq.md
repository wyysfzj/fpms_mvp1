# MD-PRE Implementation Plan

## Story Shape Classification
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: chained (DB -> BE skeleton -> FE skeleton)
- evidence_cost: medium

## chosen_runbook
- P0-prereq-heavy-story

## Batch Manifest

### MDPRE-DB-01
- task file path: `tasks/postenhancement/backend/MDPRE-DB-01.md`
- closure slice: introduce structured Applicant/Country masterdata carriers and SQLite-safe migration with prerequisite-governed minimal fields and uniqueness/activation rules
- explicit non-closure: no object-level CRUD endpoints, no frontend changes, no selector/case linkage, no delete semantics
- allowlist:
  - `backend/alembic/versions/mdpre_db_01_masterdata_carriers.py`
  - `backend/app/modules/masterdata/applicants/models.py`
  - `backend/app/modules/masterdata/countries/models.py`
  - `backend/tests/test_masterdata_prereq_schema.py`
- verification:
  - `python3 -m ruff check backend/alembic/versions/mdpre_db_01_masterdata_carriers.py backend/app/modules/masterdata/applicants/models.py backend/app/modules/masterdata/countries/models.py backend/tests/test_masterdata_prereq_schema.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_masterdata_prereq_schema.py`
  - `cd backend && PYTHONPATH=. alembic upgrade head`
  - `./scripts/task_validate.sh MDPRE-DB-01`
- dependency notes: first wave; all later skeleton work depends on stable carriers

### MDPRE-BE-01
- task file path: `tasks/postenhancement/backend/MDPRE-BE-01.md`
- closure slice: add shared masterdata backend skeleton for Applicant/Country including module boundaries, shared contract shape, and independent permission namespace wiring without completing CRUD
- explicit non-closure: no frontend changes, no full Applicant CRUD, no full Country CRUD, no selector/case linkage
- allowlist:
  - `backend/app/modules/masterdata/applicants/api.py`
  - `backend/app/modules/masterdata/applicants/schemas.py`
  - `backend/app/modules/masterdata/applicants/service.py`
  - `backend/app/modules/masterdata/countries/api.py`
  - `backend/app/modules/masterdata/countries/schemas.py`
  - `backend/app/modules/masterdata/countries/service.py`
  - `backend/app/api/router.py`
  - `backend/tests/test_masterdata_prereq_contract.py`
- verification:
  - `python3 -m ruff check backend/app/modules/masterdata/applicants/api.py backend/app/modules/masterdata/applicants/schemas.py backend/app/modules/masterdata/applicants/service.py backend/app/modules/masterdata/countries/api.py backend/app/modules/masterdata/countries/schemas.py backend/app/modules/masterdata/countries/service.py backend/app/api/router.py backend/tests/test_masterdata_prereq_contract.py`
  - `cd backend && PYTHONPATH=. pytest -q tests/test_masterdata_prereq_contract.py`
  - `./scripts/task_validate.sh MDPRE-BE-01`
- dependency notes: serialize after `MDPRE-DB-01`

### MDPRE-FE-01
- task file path: `tasks/postenhancement/frontend/MDPRE-FE-01.md`
- closure slice: establish minimal settings/masterdata route entry skeleton for Applicant/Country without shipping full CRUD pages
- explicit non-closure: no object-level CRUD UI, no selector/case linkage, no import/export
- allowlist:
  - `frontend/src/router/index.ts`
  - `frontend/src/modules/settings/pages/MasterDataHome.vue`
  - `frontend/src/modules/settings/pages/ApplicantList.vue`
  - `frontend/src/modules/settings/pages/CountryList.vue`
- verification:
  - `cd frontend && npm run lint -- src/router/index.ts src/modules/settings/pages/MasterDataHome.vue src/modules/settings/pages/ApplicantList.vue src/modules/settings/pages/CountryList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh MDPRE-FE-01`
- dependency notes: serialize after `MDPRE-BE-01`

### MDPRE-QA-01
- task file path: `tasks/postenhancement/backend/MDPRE-QA-01.md`
- closure slice: gate audit, evidence audit, and prerequisite close summary for `MD-PRE`
- explicit non-closure: no product code changes
- allowlist:
  - `artifacts/MDPRE-DB-01/**`
  - `artifacts/MDPRE-BE-01/**`
  - `artifacts/MDPRE-FE-01/**`
  - `artifacts/MDPRE-QA-01/**`
- verification:
  - `./scripts/task_validate.sh MDPRE-DB-01`
  - `./scripts/task_validate.sh MDPRE-BE-01`
  - `./scripts/task_validate.sh MDPRE-FE-01`
  - `./scripts/task_validate.sh MDPRE-QA-01`
- dependency notes: final wave after DB, BE, and FE pass

## Waves
- Wave 1: `MDPRE-DB-01`
- Wave 2: `MDPRE-BE-01`
- Wave 3: `MDPRE-FE-01`
- Wave 4: `MDPRE-QA-01`

## Serialized Shared-file Decisions
- `backend/app/api/router.py` is owned only by `MDPRE-BE-01`
- `frontend/src/router/index.ts` is owned only by `MDPRE-FE-01`
- `backend/app/modules/masterdata/applicants/*` and `backend/app/modules/masterdata/countries/*` are serialized through `MDPRE-BE-01`
