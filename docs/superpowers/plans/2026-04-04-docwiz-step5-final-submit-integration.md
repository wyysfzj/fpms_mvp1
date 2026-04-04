# DOCWIZ-STEP5-FINAL-SUBMIT-01 Plan

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `shared FE/BE final-submit integration after Step 5 preview`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `DOCWIZ-STEP5-BE-FINAL-01` | worker / main thread | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/app/modules/documents/schemas.py`, `backend/tests/test_document_wizard_batch_create.py`, `docs/superpowers/specs/2026-04-04-docwiz-step5-final-submit-integration-design.md`, `docs/superpowers/plans/2026-04-04-docwiz-step5-final-submit-integration.md`, `tasks/postenhancement/backend/DOCWIZ-STEP5-BE-FINAL-01.md` | Depends on Step 5 preview wave, template-source prerequisite, render-context prerequisite, attachment-persist prerequisite | Extend final submit backend carrier to accept and apply Step 5 attachment rows, render template output, and persist `DocAttachment` | No dispatch/envelope, no reporting/status work, no single-document attachment enhancement |
| `DOCWIZ-STEP5-FE-FINAL-01` | worker / main thread | `frontend/src/modules/documents/pages/DocumentWizard.vue`, `frontend/src/api/documents.ts`, `frontend/src/api/documents.types.ts`, `docs/superpowers/specs/2026-04-04-docwiz-step5-final-submit-integration-design.md`, `docs/superpowers/plans/2026-04-04-docwiz-step5-final-submit-integration.md`, `tasks/postenhancement/frontend/DOCWIZ-STEP5-FE-FINAL-01.md` | Runs after BE final carrier is available | Include Step 5 edits in wizard final payload | No Step 5 preview expansion, no dispatch/envelope, no attachment page enhancement |
| `DOCWIZ-QA-STEP5-FINAL-01` | monitor / main thread | `artifacts/DOCWIZ-STEP5-BE-FINAL-01/**`, `artifacts/DOCWIZ-STEP5-FE-FINAL-01/**`, `artifacts/DOCWIZ-QA-STEP5-FINAL-01/**`, `tasks/postenhancement/backend/DOCWIZ-QA-STEP5-FINAL-01.md` | Runs after BE/FE final tasks pass | Audit Step 5 final-submit wave evidence and close summary | No product-code change |

## Verification

- `./scripts/task_validate.sh DOCWIZ-STEP5-BE-FINAL-01`
- `./scripts/task_validate.sh DOCWIZ-STEP5-FE-FINAL-01`
- `./scripts/task_validate.sh DOCWIZ-QA-STEP5-FINAL-01`

## Done Definition

- Step 5 preview edits enter final payload
- Backend final write path consumes Step 5 explicit values
- Generated template output is persisted as real `DocAttachment`
- Step 5 finalization reuses prerequisite helpers instead of inventing a parallel path
- Required artifacts exist and all task gates pass
