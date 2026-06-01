# PD-P1-DB-ATTACHMENT-MANIFEST-01 — Official attachment manifest carriers

## Exact Closure Slice

Add SQLite-safe carriers that let a document attachment be classified for official submission: official file role, source role alias, external upload position, content hash, package usage hint, and archive/receipt relevance.

## Explicit Non-Closure

No upload endpoint changes. No UI changes. No file conversion, XML generation, official submission, or receipt extraction.

## Remaining Follow-Up Task IDs

- `PD-P1-BE-ATTACHMENT-MANIFEST-SERVICE-01`
- `PD-P1-FE-ATTACHMENT-GATES-01`

## Allowed Files

- `tasks/postdemo/PD-P1-DB-ATTACHMENT-MANIFEST-01.md`
- `backend/app/modules/documents/models.py`
- `backend/app/modules/documents/schemas.py`
- `backend/alembic/versions/pd_p1_db_02_attachment_manifest.py`
- `backend/tests/test_pd_p1_attachment_manifest_schema.py`
- `artifacts/PD-P1-DB-ATTACHMENT-MANIFEST-01/**`

## Verification Commands

- `ruff check --fix backend/app/modules/documents/models.py backend/app/modules/documents/schemas.py backend/tests/test_pd_p1_attachment_manifest_schema.py`
- `ruff format backend/app/modules/documents/models.py backend/app/modules/documents/schemas.py backend/tests/test_pd_p1_attachment_manifest_schema.py`
- `ruff check backend/app/modules/documents/models.py backend/app/modules/documents/schemas.py backend/tests/test_pd_p1_attachment_manifest_schema.py`
- `cd backend && pytest -q tests/test_pd_p1_attachment_manifest_schema.py`
- `./scripts/task_validate.sh PD-P1-DB-ATTACHMENT-MANIFEST-01`

## Evidence Path

- `artifacts/PD-P1-DB-ATTACHMENT-MANIFEST-01/`

## Acceptance

- Attachment metadata can distinguish technical disclosure, commission instruction, claims, statement, comparison page, proof file, XML zip, merged PDF, and receipt roles.
- Existing attachment behavior remains backward compatible when official role metadata is absent.
