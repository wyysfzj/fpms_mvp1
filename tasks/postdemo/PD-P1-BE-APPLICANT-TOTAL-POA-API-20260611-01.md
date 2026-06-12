# PD-P1-BE-APPLICANT-TOTAL-POA-API-20260611-01 — Applicant total POA API

## Exact Closure Slice

Expose applicant-level “总委托书备案编号” through existing applicant create/update/list API schemas and service normalization.

## Explicit Non-Closure

No database migration. No frontend UI. No filing readiness package behavior. No new client/applicant mapping table. No official submission.

## Remaining Follow-Up Task IDs

- `PD-P1-FE-APPLICANT-TOTAL-POA-UI-20260611-01`
- `PD-P1-BE-FILING-TOTAL-POA-READINESS-20260611-01`

## Allowed Files

- `backend/app/modules/masterdata/applicants/schemas.py`
- `backend/app/modules/masterdata/applicants/service.py`
- `backend/app/modules/masterdata/applicants/api.py`
- `backend/tests/test_applicant_masterdata_api.py`
- `backend/tests/test_pd_p1_applicant_total_poa_api.py`
- `tasks/postdemo/PD-P1-BE-APPLICANT-TOTAL-POA-API-20260611-01.md`
- `artifacts/PD-P1-BE-APPLICANT-TOTAL-POA-API-20260611-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/masterdata/applicants/schemas.py backend/app/modules/masterdata/applicants/service.py backend/app/modules/masterdata/applicants/api.py backend/tests/test_applicant_masterdata_api.py backend/tests/test_pd_p1_applicant_total_poa_api.py`
- `ruff format backend/app/modules/masterdata/applicants/schemas.py backend/app/modules/masterdata/applicants/service.py backend/app/modules/masterdata/applicants/api.py backend/tests/test_applicant_masterdata_api.py backend/tests/test_pd_p1_applicant_total_poa_api.py`
- `ruff check backend/app/modules/masterdata/applicants/schemas.py backend/app/modules/masterdata/applicants/service.py backend/app/modules/masterdata/applicants/api.py backend/tests/test_applicant_masterdata_api.py backend/tests/test_pd_p1_applicant_total_poa_api.py`
- `cd backend && pytest -q tests/test_pd_p1_applicant_total_poa_api.py tests/test_applicant_masterdata_api.py`
- `./scripts/task_validate.sh PD-P1-BE-APPLICANT-TOTAL-POA-API-20260611-01`

## Acceptance

- Create/update/list/read responses include `total_power_of_attorney_no`.
- Blank input normalizes to `None`.
- Permission and response semantics stay unchanged.
