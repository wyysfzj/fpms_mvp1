# DOCWIZ-STEP4-IMPL-01 Plan

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared FE/BE fee-preview implementation before final submit integration`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `DOCWIZ-STEP4-BE-PREVIEW-01` | worker / main thread | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/app/modules/documents/schemas.py`, `backend/app/modules/documents/fee_linking_service.py`, `backend/tests/test_document_wizard_fee_preview.py`, `docs/superpowers/specs/2026-04-04-docwiz-step4-preview-implementation-design.md`, `docs/superpowers/plans/2026-04-04-docwiz-step4-preview-implementation.md`, `tasks/postenhancement/backend/DOCWIZ-STEP4-BE-PREVIEW-01.md` | Depends on Step 4 contract freeze and existing wizard shell | Add preview-only backend carrier for Step 4 fee candidates | No final fee write integration, no Step 5, no billing page work |
| `DOCWIZ-STEP4-FE-PREVIEW-01` | worker / main thread | `frontend/src/modules/documents/pages/DocumentWizard.vue`, `frontend/src/api/documents.ts`, `frontend/src/api/documents.types.ts`, `docs/superpowers/specs/2026-04-04-docwiz-step4-preview-implementation-design.md`, `docs/superpowers/plans/2026-04-04-docwiz-step4-preview-implementation.md`, `tasks/postenhancement/frontend/DOCWIZ-STEP4-FE-PREVIEW-01.md` | Runs after BE preview contract is available | Render Step 4 fee preview and editable in-memory fields in wizard | No final fee submit integration, no Step 5, no billing page work |
| `DOCWIZ-QA-STEP4-IMPL-01` | monitor / main thread | `artifacts/DOCWIZ-STEP4-BE-PREVIEW-01/**`, `artifacts/DOCWIZ-STEP4-FE-PREVIEW-01/**`, `artifacts/DOCWIZ-QA-STEP4-IMPL-01/**`, `tasks/postenhancement/backend/DOCWIZ-QA-STEP4-IMPL-01.md` | Runs after BE/FE preview tasks pass | Audit Step 4 preview wave evidence and close summary | No product-code change |

## Verification

- `./scripts/task_validate.sh DOCWIZ-STEP4-BE-PREVIEW-01`
- `./scripts/task_validate.sh DOCWIZ-STEP4-FE-PREVIEW-01`
- `./scripts/task_validate.sh DOCWIZ-QA-STEP4-IMPL-01`

## Done Definition

- Step 4 has preview-only backend support
- Step 4 wizard UI shows fee candidates and editable fields
- Preview remains in-memory only
- Step 4 final submit integration remains explicitly deferred
- Required artifacts exist and all task gates pass
