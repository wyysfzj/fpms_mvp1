# BE-A-APPLICANT-DATA-MODEL-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Add persisted Applicant `applicant_type` backend data support, expose it through the existing applicant schema/API create-read-update paths where applicable, seed dev applicant type values for DS-AP-equivalent applicants, and add targeted backend tests proving applicant type can be created, read, updated, or seeded according to the existing API patterns.

## Explicit Non-Closure

- Do not implement applicant kind mismatch service rules.
- Do not modify `backend/app/modules/cases/service.py`.
- Do not implement pytest automation handlers.
- Do not modify frontend UI.
- Do not modify skeleton data.
- Do not broaden the task into TC-A-008 date/number rules.

## Remaining Follow-Up Task IDs

- BE-A-APPLICANT-KIND-RULE-01
- A-AUTO-PY-A-APPLICANT-RULES-P0-02
- PRODUCT-A-APPLICANT-TYPE-MODEL-CONFIRM-01 if product values beyond INDIVIDUAL and ENTITY are needed

## Allowed Files

- `tasks/backend/data_model/BE-A-APPLICANT-DATA-MODEL-01.md`
- `backend/app/modules/masterdata/applicants/models.py`
- `backend/app/modules/masterdata/applicants/schemas.py`
- `backend/app/modules/masterdata/applicants/api.py`
- `backend/scripts/seed_dev.py`
- `backend/tests/test_applicant_data_model.py`
- `backend/tests/test_applicant_masterdata_api.py`
- `backend/tests/test_masterdata_prereq_schema.py`
- `backend/tests/test_masterdata_prereq_contract.py`
- `backend/alembic/versions/**`
- `artifacts/BE-A-APPLICANT-DATA-MODEL-01/**`

## Verification Commands

- `cd backend && python3 -m ruff check --fix app/modules/masterdata/applicants/models.py app/modules/masterdata/applicants/schemas.py app/modules/masterdata/applicants/api.py scripts/seed_dev.py tests/test_applicant_data_model.py tests/test_applicant_masterdata_api.py tests/test_masterdata_prereq_schema.py tests/test_masterdata_prereq_contract.py`
- `cd backend && python3 -m ruff format app/modules/masterdata/applicants/models.py app/modules/masterdata/applicants/schemas.py app/modules/masterdata/applicants/api.py scripts/seed_dev.py tests/test_applicant_data_model.py tests/test_applicant_masterdata_api.py tests/test_masterdata_prereq_schema.py tests/test_masterdata_prereq_contract.py`
- `cd backend && python3 -m ruff check app/modules/masterdata/applicants/models.py app/modules/masterdata/applicants/schemas.py app/modules/masterdata/applicants/api.py scripts/seed_dev.py tests/test_applicant_data_model.py tests/test_applicant_masterdata_api.py tests/test_masterdata_prereq_schema.py tests/test_masterdata_prereq_contract.py`
- `cd backend && pytest tests/test_applicant_data_model.py -q`
- `cd backend && pytest tests/test_applicant_masterdata_api.py tests/test_masterdata_prereq_schema.py tests/test_masterdata_prereq_contract.py -q`
- `cd backend && alembic upgrade head && python3 scripts/seed_dev.py` if a migration is added
- `./scripts/evidence_run.sh BE-A-APPLICANT-DATA-MODEL-01 task_gate ./scripts/task_validate.sh BE-A-APPLICANT-DATA-MODEL-01`

## Evidence Path

- `artifacts/BE-A-APPLICANT-DATA-MODEL-01/`
