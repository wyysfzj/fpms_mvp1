# PD-P1-DB-WORK-PACKAGE-01 — Official work-package carriers

## Exact Closure Slice

Create the official work-package data carriers for filing preparation and OA reply: package header, package status, checklist rows, manifest rows, receipt metadata rows, and override audit rows.

## Explicit Non-Closure

No API routes, no package service logic, no frontend pages, no direct official submission, and no automatic receipt download or OCR.

## Remaining Follow-Up Task IDs

- `PD-P1-BE-WORK-PACKAGE-SERVICE-01`
- `PD-P1-BE-FILING-PACKAGE-API-01`
- `PD-P1-BE-OA-PACKAGE-API-01`
- `PD-P1-BE-RECEIPT-ARCHIVE-API-01`

## Allowed Files

- `tasks/postdemo/PD-P1-DB-WORK-PACKAGE-01.md`
- `backend/app/modules/official_workflows/__init__.py`
- `backend/app/modules/official_workflows/models.py`
- `backend/app/modules/official_workflows/schemas.py`
- `backend/alembic/versions/pd_p1_db_03_official_work_packages.py`
- `backend/tests/test_pd_p1_official_work_package_schema.py`
- `artifacts/PD-P1-DB-WORK-PACKAGE-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/official_workflows backend/tests/test_pd_p1_official_work_package_schema.py`
- `ruff format backend/app/modules/official_workflows backend/tests/test_pd_p1_official_work_package_schema.py`
- `ruff check backend/app/modules/official_workflows backend/tests/test_pd_p1_official_work_package_schema.py`
- `cd backend && pytest -q tests/test_pd_p1_official_work_package_schema.py`
- `./scripts/task_validate.sh PD-P1-DB-WORK-PACKAGE-01`

## Evidence Path

- `artifacts/PD-P1-DB-WORK-PACKAGE-01/`

## Acceptance

- Package kind supports at least new filing and OA reply.
- Status values can represent preparing, needs maintenance, needs confirmation, ready for external submit, submitted, waiting receipt, archived, exception, and override.
- Receipt metadata can store receipt PDF attachment reference, receiving case number, submitter, received time, and received file list.
