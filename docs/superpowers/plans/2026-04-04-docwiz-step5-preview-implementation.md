# DOCWIZ-STEP5-IMPL-01 Plan

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared FE/BE attachment-preview implementation before final submit integration`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `DOCWIZ-STEP5-BE-PREVIEW-01` | worker / main thread | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/app/modules/documents/schemas.py`, `backend/tests/test_document_wizard_attachment_preview.py`, `docs/superpowers/specs/2026-04-04-docwiz-step5-preview-implementation-design.md`, `docs/superpowers/plans/2026-04-04-docwiz-step5-preview-implementation.md`, `tasks/postenhancement/backend/DOCWIZ-STEP5-BE-PREVIEW-01.md` | Depends on Step 5 contract freeze and existing wizard shell | Add preview-only backend carrier for Step 5 attachment/template candidates | No final attachment write integration, no dispatch/envelope, no single-document attachment page work |
| `DOCWIZ-STEP5-FE-PREVIEW-01` | worker / main thread | `frontend/src/modules/documents/pages/DocumentWizard.vue`, `frontend/src/api/documents.ts`, `frontend/src/api/documents.types.ts`, `docs/superpowers/specs/2026-04-04-docwiz-step5-preview-implementation-design.md`, `docs/superpowers/plans/2026-04-04-docwiz-step5-preview-implementation.md`, `tasks/postenhancement/frontend/DOCWIZ-STEP5-FE-PREVIEW-01.md` | Runs after BE preview contract is available | Render Step 5 attachment/template preview and editable in-memory fields in wizard | No final attachment submit integration, no dispatch/envelope, no single-document attachment page work |
| `DOCWIZ-QA-STEP5-IMPL-01` | monitor / main thread | `artifacts/DOCWIZ-STEP5-BE-PREVIEW-01/**`, `artifacts/DOCWIZ-STEP5-FE-PREVIEW-01/**`, `artifacts/DOCWIZ-QA-STEP5-IMPL-01/**`, `tasks/postenhancement/backend/DOCWIZ-QA-STEP5-IMPL-01.md` | Runs after BE/FE preview tasks pass | Audit Step 5 preview wave evidence and close summary | No product-code change |

## Verification

- `./scripts/task_validate.sh DOCWIZ-STEP5-BE-PREVIEW-01`
- `./scripts/task_validate.sh DOCWIZ-STEP5-FE-PREVIEW-01`
- `./scripts/task_validate.sh DOCWIZ-QA-STEP5-IMPL-01`

## Done Definition

- Step 5 has preview-only backend support
- Step 5 wizard UI shows attachment/template candidates and editable fields
- Preview remains in-memory only
- Step 5 final submit integration remains explicitly deferred
- Required artifacts exist and all task gates pass
