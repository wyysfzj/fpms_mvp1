# DOCWIZ-STEP3-FINAL-SUBMIT-01 Plan

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared FE/BE final-submit integration after preview`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `DOCWIZ-STEP3-BE-FINAL-01` | worker / main thread | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/app/modules/documents/schemas.py`, `backend/tests/test_document_wizard_batch_create.py`, `docs/superpowers/specs/2026-04-03-docwiz-step3-final-submit-integration-design.md`, `docs/superpowers/plans/2026-04-03-docwiz-step3-final-submit-integration.md` | Must land before FE final wiring; serialized ownership of documents API/service/schema | Extend wizard final submit carrier to accept Step 3 task rows and create real tasks from explicit values | No Step 4/5, no assignment semantics, no schema change |
| `DOCWIZ-STEP3-FE-FINAL-01` | worker / main thread | `frontend/src/modules/documents/pages/DocumentWizard.vue`, `frontend/src/api/documents.ts`, `frontend/src/api/documents.types.ts`, `docs/superpowers/specs/2026-04-03-docwiz-step3-final-submit-integration-design.md`, `docs/superpowers/plans/2026-04-03-docwiz-step3-final-submit-integration.md` | Depends on BE final carrier; serialized ownership of wizard shell and shared document API/types | Include Step 3 edited preview rows in final payload submitted by wizard | No Step 4/5, no new preview features, no backend changes outside final carrier |
| `DOCWIZ-QA-STEP3-FINAL-01` | monitor / main thread | `artifacts/DOCWIZ-STEP3-BE-FINAL-01/**`, `artifacts/DOCWIZ-STEP3-FE-FINAL-01/**`, `artifacts/DOCWIZ-QA-STEP3-FINAL-01/**`, `tasks/postenhancement/backend/DOCWIZ-QA-STEP3-FINAL-01.md` | Runs after BE+FE final integration slices finish | Audit evidence and close summary for Step 3 final submit integration wave | No product behavior outside Step 3 final integration |

## Verification

- `ruff check --fix backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_batch_create.py`
- `ruff format backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_batch_create.py`
- `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/tests/test_document_wizard_batch_create.py`
- `cd backend && pytest -q tests/test_document_wizard_batch_create.py`
- `cd frontend && npm run lint -- src/modules/documents/pages/DocumentWizard.vue src/api/documents.ts src/api/documents.types.ts`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh DOCWIZ-STEP3-BE-FINAL-01`
- `./scripts/task_validate.sh DOCWIZ-STEP3-FE-FINAL-01`
- `./scripts/task_validate.sh DOCWIZ-QA-STEP3-FINAL-01`

## Done Definition

- Final wizard payload carries Step 3 edited task rows
- Backend creates real tasks from explicit values first
- Existing wizard finalization still works for untouched fields
- Required artifacts exist and all task gates pass
