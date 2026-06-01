# PD-P1-BE-OA-PACKAGE-API-01 — OA reply package API

## Exact Closure Slice

Add the backend API resource for OA reply packages embedded in existing `OA_IN` / `OA_OUT` / `reply_to` / task / attachment flows: read package, refresh checklist/manifest, update OA-specific checklist state, and link reply documents.

## Explicit Non-Closure

No official-site automation. No rich-text fidelity conversion. No automatic signature, submit, receipt download, or frontend implementation.

## Remaining Follow-Up Task IDs

- `PD-P1-FE-OA-PACKAGE-01`
- `PD-P1-QA-FULLSCOPE-E2E-01`

## Allowed Files

- `backend/app/modules/official_workflows/api.py`
- `backend/app/modules/official_workflows/schemas.py`
- `backend/app/modules/official_workflows/service.py`
- `backend/app/modules/documents/schemas.py`
- `backend/tests/test_pd_p1_oa_package_api.py`
- `tasks/postdemo/PD-P1-BE-OA-PACKAGE-API-01.md`
- `artifacts/PD-P1-BE-OA-PACKAGE-API-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/official_workflows backend/app/modules/documents/schemas.py backend/tests/test_pd_p1_oa_package_api.py`
- `ruff format backend/app/modules/official_workflows backend/app/modules/documents/schemas.py backend/tests/test_pd_p1_oa_package_api.py`
- `ruff check backend/app/modules/official_workflows backend/app/modules/documents/schemas.py backend/tests/test_pd_p1_oa_package_api.py`
- `cd backend && pytest -q tests/test_pd_p1_oa_package_api.py`
- `./scripts/task_validate.sh PD-P1-BE-OA-PACKAGE-API-01`

## Evidence Path

- `artifacts/PD-P1-BE-OA-PACKAGE-API-01/`

## Acceptance

- API exposes OA source document, reply document, application number, applicant/patentee display, notice code/name, issue sequence, issue date, due dates, reply status, statement Word/text/PDF references, modified claim files, comparison page, proof files, experiment-data flag, and official-page checklist.
- `Document.reply_to_id`, `need_reply`, and tasks remain the internal reply chain; package status is not collapsed into `reply_date`.
