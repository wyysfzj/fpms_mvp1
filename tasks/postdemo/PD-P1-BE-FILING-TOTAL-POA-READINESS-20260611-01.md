# PD-P1-BE-FILING-TOTAL-POA-READINESS-20260611-01 — Filing total POA readiness

## Exact Closure Slice

Enhance filing preparation readiness so a case linked to applicant masterdata can reuse applicant-level “总委托书备案编号”, while unlinked or missing values are reported as maintenance/mapping pending.

## Explicit Non-Closure

No database migration. No applicant CRUD API changes. No frontend UI. No XML generation. No official direct submit.

## Remaining Follow-Up Task IDs

- `PD-P1-E2E-ANSWER-DELTA-LIVE-20260611-01`
- `PD-P1-QA-FULLSCOPE-ANSWER-DELTA-20260611-01`

## Allowed Files

- `backend/app/modules/official_workflows/schemas.py`
- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_pd_p1_filing_total_poa_readiness.py`
- `tasks/postdemo/PD-P1-BE-FILING-TOTAL-POA-READINESS-20260611-01.md`
- `artifacts/PD-P1-BE-FILING-TOTAL-POA-READINESS-20260611-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/official_workflows/schemas.py backend/app/modules/official_workflows/service.py backend/tests/test_pd_p1_filing_total_poa_readiness.py`
- `ruff format backend/app/modules/official_workflows/schemas.py backend/app/modules/official_workflows/service.py backend/tests/test_pd_p1_filing_total_poa_readiness.py`
- `ruff check backend/app/modules/official_workflows/schemas.py backend/app/modules/official_workflows/service.py backend/tests/test_pd_p1_filing_total_poa_readiness.py`
- `cd backend && pytest -q tests/test_pd_p1_filing_total_poa_readiness.py`
- `./scripts/task_validate.sh PD-P1-BE-FILING-TOTAL-POA-READINESS-20260611-01`

## Acceptance

- Filing readiness reports total POA as READY when the first/linked applicant has `total_power_of_attorney_no`.
- Filing readiness reports mapping pending when no case applicant is linked to applicant masterdata.
- Filing readiness reports missing maintenance when linked applicant has no total POA, without treating it as submit-package补录.
