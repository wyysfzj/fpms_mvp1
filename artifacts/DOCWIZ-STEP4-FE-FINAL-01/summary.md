# DOCWIZ-STEP4-FE-FINAL-01 Evidence Summary

## Scope
- Frontend-only final-submit wiring for Step 4 fee rows.
- Updated final wizard payload so Step 4 edited fee candidates are submitted with batch create.
- Existing unrelated dirty files were left untouched.

## Verification
- `cd frontend && npm run lint -- src/modules/documents/pages/DocumentWizard.vue src/api/documents.ts src/api/documents.types.ts`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh DOCWIZ-STEP4-FE-FINAL-01`

## Expected Outcome
- Step 4 preview edits are preserved in the final submit payload.
- Final wizard submit sends `fee_rows` together with existing `rows` and `task_rows`.
- Frontend payload shape stays aligned with backend Step 4 final-submit contract.

## Notes
- Pre-existing unrelated dirty files were not touched:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
