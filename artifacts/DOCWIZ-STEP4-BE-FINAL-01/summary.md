# DOCWIZ-STEP4-BE-FINAL-01 Evidence Summary

## Scope
- Backend-only implementation of Step 4 final-submit integration for `/documents/wizard/batch-create`.
- No frontend files were modified.
- Existing unrelated dirty files were left untouched.

## Verification
- `ruff check --fix backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_document_wizard_batch_create.py`
- `ruff format backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_document_wizard_batch_create.py`
- `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/fee_linking_service.py backend/tests/test_document_wizard_batch_create.py`
- `cd backend && pytest -q tests/test_document_wizard_batch_create.py -k step4`
- `./scripts/task_validate.sh DOCWIZ-STEP4-BE-FINAL-01`

## Expected Outcome
- Step 4 fee rows can be submitted with wizard batch-create payloads.
- Explicit fee values are used to create real `FeeDraft` and `FeeItem` records.
- Invalid Step 4 fee rows are rejected with `DOCUMENT_WIZARD_BATCH_INVALID`.

## Notes
- Pre-existing unrelated dirty files were not touched:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
