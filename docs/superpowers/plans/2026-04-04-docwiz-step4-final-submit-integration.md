# DOCWIZ-STEP4-FINAL-SUBMIT-01 Plan

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared FE/BE final-submit integration after Step 4 preview`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `DOCWIZ-STEP4-BE-FINAL-01` | worker / main thread | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/app/modules/documents/schemas.py`, `backend/app/modules/documents/fee_linking_service.py`, `backend/tests/test_document_wizard_batch_create.py`, `docs/superpowers/specs/2026-04-04-docwiz-step4-final-submit-integration-design.md`, `docs/superpowers/plans/2026-04-04-docwiz-step4-final-submit-integration.md`, `tasks/postenhancement/backend/DOCWIZ-STEP4-BE-FINAL-01.md` | Depends on Step 4 preview wave | Extend final submit backend carrier to accept and apply Step 4 fee rows | No Step 5, no billing page work, no downstream fee workflow |
| `DOCWIZ-STEP4-FE-FINAL-01` | worker / main thread | `frontend/src/modules/documents/pages/DocumentWizard.vue`, `frontend/src/api/documents.ts`, `frontend/src/api/documents.types.ts`, `docs/superpowers/specs/2026-04-04-docwiz-step4-final-submit-integration-design.md`, `docs/superpowers/plans/2026-04-04-docwiz-step4-final-submit-integration.md`, `tasks/postenhancement/frontend/DOCWIZ-STEP4-FE-FINAL-01.md` | Runs after BE final carrier is available | Include Step 4 edits in wizard final payload | No Step 5, no billing page work, no preview expansion |
| `DOCWIZ-QA-STEP4-FINAL-01` | monitor / main thread | `artifacts/DOCWIZ-STEP4-BE-FINAL-01/**`, `artifacts/DOCWIZ-STEP4-FE-FINAL-01/**`, `artifacts/DOCWIZ-QA-STEP4-FINAL-01/**`, `tasks/postenhancement/backend/DOCWIZ-QA-STEP4-FINAL-01.md` | Runs after BE/FE final tasks pass | Audit Step 4 final-submit wave evidence and close summary | No product-code change |

## Verification

- `./scripts/task_validate.sh DOCWIZ-STEP4-BE-FINAL-01`
- `./scripts/task_validate.sh DOCWIZ-STEP4-FE-FINAL-01`
- `./scripts/task_validate.sh DOCWIZ-QA-STEP4-FINAL-01`

## Done Definition

- Step 4 preview edits enter final payload
- Backend final write path consumes Step 4 explicit values
- Untouched fields still fall back to preview/template defaults
- Step 5 and downstream fee workflow remain explicitly deferred
- Required artifacts exist and all task gates pass
