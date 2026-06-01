# PD-P1-BE-ATTACHMENT-MANIFEST-SERVICE-01 — Attachment manifest service rules

## Exact Closure Slice

Add deterministic backend service rules for official attachment roles, role aliases, hash calculation/storage, upload-position labels, and package file-list classification.

## Explicit Non-Closure

No new route. No UI. No physical file conversion. No XML/PDF generation. No receipt extraction.

## Remaining Follow-Up Task IDs

- `PD-P1-BE-FILING-PACKAGE-API-01`
- `PD-P1-BE-OA-PACKAGE-API-01`
- `PD-P1-FE-ATTACHMENT-GATES-01`

## Allowed Files

- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/schemas.py`
- `backend/tests/test_pd_p1_attachment_manifest_service.py`
- `tasks/postdemo/PD-P1-BE-ATTACHMENT-MANIFEST-SERVICE-01.md`
- `artifacts/PD-P1-BE-ATTACHMENT-MANIFEST-SERVICE-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_pd_p1_attachment_manifest_service.py`
- `ruff format backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_pd_p1_attachment_manifest_service.py`
- `ruff check backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_pd_p1_attachment_manifest_service.py`
- `cd backend && pytest -q tests/test_pd_p1_attachment_manifest_service.py`
- `./scripts/task_validate.sh PD-P1-BE-ATTACHMENT-MANIFEST-SERVICE-01`

## Evidence Path

- `artifacts/PD-P1-BE-ATTACHMENT-MANIFEST-SERVICE-01/`

## Acceptance

- Service returns filing roles, OA roles, archive roles, and historical alias roles separately.
- Missing technical disclosure and conditional commission instruction can be detected without confusing them with official filing documents.
