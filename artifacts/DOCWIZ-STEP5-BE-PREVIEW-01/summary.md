# DOCWIZ-STEP5-BE-PREVIEW-01 Evidence Summary

## Scope
- Backend-only implementation of Step 5 preview-only attachment/template candidate carrier.
- Added wizard attachment preview endpoint and side-effect-free candidate generation.
- Existing unrelated dirty files were left untouched.

## Verification
- `ruff check --fix backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_attachment_preview.py`
- `ruff format backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_attachment_preview.py`
- `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_attachment_preview.py`
- `cd backend && pytest -q tests/test_document_wizard_attachment_preview.py`
- `./scripts/task_validate.sh DOCWIZ-STEP5-BE-PREVIEW-01`

## Expected Outcome
- Step 5 attachment preview returns template-driven candidate rows for applicable wizard draft rows.
- Preview remains side-effect-free and does not create `DocAttachment` records.
- Inapplicable templates return an empty preview result.

## Notes
- Pre-existing unrelated dirty files were not touched:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
