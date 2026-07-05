# FPMS-ATTACHMENT-ROLE-VALIDATION-20260705-01

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Add role-level upload extension/MIME validation for official package attachment roles, including XML zip, receipt PDF, OA statement Word/PDF, modified claims, amendment comparison page, and proof/extra files.

## Explicit Non-Closure

Do not change attachment storage paths, add virus scanning, change the official notice catalog, change attachment role vocabulary, add manual override, or implement automatic official upload.

## Allowed Files

- `tasks/reviews/FPMS-ATTACHMENT-ROLE-VALIDATION-20260705-01.md`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_document_attachment_upload_metadata_api.py`
- `artifacts/FPMS-ATTACHMENT-ROLE-VALIDATION-20260705-01/**`

## Verification Commands

- `cd backend && PYTHONPATH=. pytest tests/test_document_attachment_upload_metadata_api.py -q`
- `cd backend && python -m ruff check --fix app/modules/documents/service.py tests/test_document_attachment_upload_metadata_api.py`
- `cd backend && python -m ruff format app/modules/documents/service.py tests/test_document_attachment_upload_metadata_api.py`
- `cd backend && python -m ruff check app/modules/documents/service.py tests/test_document_attachment_upload_metadata_api.py`
- `./scripts/task_validate.sh FPMS-ATTACHMENT-ROLE-VALIDATION-20260705-01`

## Done Definition

- XML zip role rejects non-zip uploads.
- Receipt/PDF roles reject non-PDF uploads.
- Word roles accept Word extensions and reject incompatible extensions.
- Existing valid OA PDF upload still passes.
- Required evidence files and task gate exist.

## Evidence Path

- `artifacts/FPMS-ATTACHMENT-ROLE-VALIDATION-20260705-01/**`

## Remaining Follow-Up Task IDs

None
