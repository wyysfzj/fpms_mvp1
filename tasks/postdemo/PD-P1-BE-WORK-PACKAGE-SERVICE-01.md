# PD-P1-BE-WORK-PACKAGE-SERVICE-01 — Official work-package service rules

## Exact Closure Slice

Add service-layer rules for official work-package status transitions, checklist completion, manifest completeness, receipt hard gate, and manual override audit.

## Explicit Non-Closure

No API route. No frontend. No official-site automation. No fee calculation or letter generation.

## Remaining Follow-Up Task IDs

- `PD-P1-BE-FILING-PACKAGE-API-01`
- `PD-P1-BE-OA-PACKAGE-API-01`
- `PD-P1-BE-RECEIPT-ARCHIVE-API-01`

## Allowed Files

- `backend/app/modules/official_workflows/service.py`
- `backend/app/modules/official_workflows/schemas.py`
- `backend/tests/test_pd_p1_official_work_package_service.py`
- `tasks/postdemo/PD-P1-BE-WORK-PACKAGE-SERVICE-01.md`
- `artifacts/PD-P1-BE-WORK-PACKAGE-SERVICE-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/official_workflows/service.py backend/app/modules/official_workflows/schemas.py backend/tests/test_pd_p1_official_work_package_service.py`
- `ruff format backend/app/modules/official_workflows/service.py backend/app/modules/official_workflows/schemas.py backend/tests/test_pd_p1_official_work_package_service.py`
- `ruff check backend/app/modules/official_workflows/service.py backend/app/modules/official_workflows/schemas.py backend/tests/test_pd_p1_official_work_package_service.py`
- `cd backend && pytest -q tests/test_pd_p1_official_work_package_service.py`
- `./scripts/task_validate.sh PD-P1-BE-WORK-PACKAGE-SERVICE-01`

## Evidence Path

- `artifacts/PD-P1-BE-WORK-PACKAGE-SERVICE-01/`

## Acceptance

- A package cannot close without required receipt/archive evidence unless an override with user, time, reason, and follow-up responsibility is recorded.
- Stable missing official fields are classified as `待维护`; only official transient or unconfirmed ownership fields are classified as `待确认/待补录`.
