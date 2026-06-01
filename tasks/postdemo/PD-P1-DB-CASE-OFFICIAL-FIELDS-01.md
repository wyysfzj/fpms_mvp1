# PD-P1-DB-CASE-OFFICIAL-FIELDS-01 — Case applicant/inventor official field carriers

## Exact Closure Slice

Add SQLite-safe data carriers for official submission fields on case applicant and case inventor rows: applicant nationality, certificate type, certificate number, official postcode, applicant entity kind override, inventor nationality, and China-national inventor ID number.

## Explicit Non-Closure

No FastAPI endpoint changes. No frontend changes. No official work-package, attachment manifest, CPC XML, OA reply, fee, or letter behavior.

## Remaining Follow-Up Task IDs

- `PD-P1-BE-CASE-OFFICIAL-FIELDS-API-01`
- `PD-P1-FE-CASE-OFFICIAL-FIELDS-01`

## Allowed Files

- `tasks/postdemo/PD-P1-DB-CASE-OFFICIAL-FIELDS-01.md`
- `backend/app/modules/cases/models.py`
- `backend/app/modules/cases/schemas.py`
- `backend/alembic/versions/pd_p1_db_01_case_official_fields.py`
- `backend/tests/test_pd_p1_case_official_fields_schema.py`
- `artifacts/PD-P1-DB-CASE-OFFICIAL-FIELDS-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/cases/models.py backend/app/modules/cases/schemas.py backend/tests/test_pd_p1_case_official_fields_schema.py`
- `ruff format backend/app/modules/cases/models.py backend/app/modules/cases/schemas.py backend/tests/test_pd_p1_case_official_fields_schema.py`
- `ruff check backend/app/modules/cases/models.py backend/app/modules/cases/schemas.py backend/tests/test_pd_p1_case_official_fields_schema.py`
- `cd backend && pytest -q tests/test_pd_p1_case_official_fields_schema.py`
- `./scripts/task_validate.sh PD-P1-DB-CASE-OFFICIAL-FIELDS-01`

## Evidence Path

- `artifacts/PD-P1-DB-CASE-OFFICIAL-FIELDS-01/`

## Acceptance

- Migration uses SQLite-compatible column types and `CURRENT_TIMESTAMP` only if timestamps are introduced.
- Existing case applicant/inventor tests still pass.
- New tests prove create/read schema carriers can represent the official fields without using submit-time补录.
