# PD-P1-DB-APPLICANT-TOTAL-POA-20260611-01 — Applicant total POA data carrier

## Exact Closure Slice

Add a SQLite-compatible applicant masterdata carrier for the customer-confirmed “总委托书备案编号” so the value is maintained once per official applicant and reused by cases through `T_CaseApplicant.applicant_id`.

## Explicit Non-Closure

No API behavior. No frontend UI. No filing readiness logic. No client/applicant mapping table. No CPC/OA direct submit.

## Remaining Follow-Up Task IDs

- `PD-P1-BE-APPLICANT-TOTAL-POA-API-20260611-01`
- `PD-P1-BE-FILING-TOTAL-POA-READINESS-20260611-01`
- `PD-P1-FE-APPLICANT-TOTAL-POA-UI-20260611-01`

## Allowed Files

- `backend/app/modules/masterdata/applicants/models.py`
- `backend/alembic/versions/pd_p1_db_06_applicant_total_poa.py`
- `backend/tests/test_pd_p1_applicant_total_poa_carrier.py`
- `tasks/postdemo/PD-P1-DB-APPLICANT-TOTAL-POA-20260611-01.md`
- `artifacts/PD-P1-DB-APPLICANT-TOTAL-POA-20260611-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/masterdata/applicants/models.py backend/alembic/versions/pd_p1_db_06_applicant_total_poa.py backend/tests/test_pd_p1_applicant_total_poa_carrier.py`
- `ruff format backend/app/modules/masterdata/applicants/models.py backend/alembic/versions/pd_p1_db_06_applicant_total_poa.py backend/tests/test_pd_p1_applicant_total_poa_carrier.py`
- `ruff check backend/app/modules/masterdata/applicants/models.py backend/alembic/versions/pd_p1_db_06_applicant_total_poa.py backend/tests/test_pd_p1_applicant_total_poa_carrier.py`
- `cd backend && pytest -q tests/test_pd_p1_applicant_total_poa_carrier.py`
- `./scripts/task_validate.sh PD-P1-DB-APPLICANT-TOTAL-POA-20260611-01`

## Acceptance

- `Applicant` model exposes nullable `total_power_of_attorney_no`.
- Alembic head creates the same column on `t_applicant` without PG-only SQL.
- The field is applicant-level and not added to `Case` as a long-term补录 carrier.
