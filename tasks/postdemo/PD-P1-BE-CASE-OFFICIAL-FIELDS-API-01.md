# PD-P1-BE-CASE-OFFICIAL-FIELDS-API-01 — Case official fields API

## Exact Closure Slice

Expose applicant and inventor official fields through existing case create/update/detail/list schemas and APIs so stable official data is maintained in FPMS rather than re-entered in filing/OA packages.

## Explicit Non-Closure

No database migration. No frontend UI. No official work-package API. No CPC XML or official submission.

## Remaining Follow-Up Task IDs

- `PD-P1-FE-CASE-OFFICIAL-FIELDS-01`
- `PD-P1-BE-FILING-PACKAGE-API-01`

## Allowed Files

- `backend/app/modules/cases/api.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_pd_p1_case_official_fields_api.py`
- `tasks/postdemo/PD-P1-BE-CASE-OFFICIAL-FIELDS-API-01.md`
- `artifacts/PD-P1-BE-CASE-OFFICIAL-FIELDS-API-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_pd_p1_case_official_fields_api.py`
- `ruff format backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_pd_p1_case_official_fields_api.py`
- `ruff check backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_pd_p1_case_official_fields_api.py`
- `cd backend && pytest -q tests/test_pd_p1_case_official_fields_api.py`
- `./scripts/task_validate.sh PD-P1-BE-CASE-OFFICIAL-FIELDS-API-01`

## Evidence Path

- `artifacts/PD-P1-BE-CASE-OFFICIAL-FIELDS-API-01/**`

## Acceptance

- Create/update/read paths preserve official applicant/inventor fields.
- Validation requires China-national inventor ID only when the inventor nationality is China, unless the task records a product-confirmed alternate rule.
- Permission and response-envelope conventions remain unchanged.
