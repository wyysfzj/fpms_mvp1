# DOCWIZ-STEP3-IMPL-01 Plan

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared preview implementation before final submit integration`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `DOCWIZ-STEP3-BE-PREVIEW-01` | worker / main thread | `backend/app/modules/documents/api.py`, `backend/app/modules/documents/service.py`, `backend/app/modules/documents/schemas.py`, `docs/superpowers/specs/2026-04-03-docwiz-step3-preview-implementation-design.md`, `docs/superpowers/plans/2026-04-03-docwiz-step3-preview-implementation.md` | Must land before FE wiring; serialized ownership of documents API/service/schema | Add preview-only Step 3 backend carrier that projects task candidates from wizard draft rows without writing real `T_Task` rows | No final submit integration, no Step 4/5, no schema change |
| `DOCWIZ-STEP3-FE-PREVIEW-01` | worker / main thread | `frontend/src/modules/documents/pages/DocumentWizard.vue`, `frontend/src/api/documents.ts`, `frontend/src/api/documents.types.ts`, `docs/superpowers/specs/2026-04-03-docwiz-step3-preview-implementation-design.md`, `docs/superpowers/plans/2026-04-03-docwiz-step3-preview-implementation.md` | Depends on BE preview carrier; serialized ownership of wizard shell and shared document API/types | Render Step 3 task candidate preview, editable fields, and empty state in wizard Step 3 | No final submit integration, no Step 4/5, no backend patch outside preview carrier |
| `DOCWIZ-QA-STEP3-IMPL-01` | monitor / main thread | `artifacts/DOCWIZ-STEP3-BE-PREVIEW-01/**`, `artifacts/DOCWIZ-STEP3-FE-PREVIEW-01/**`, `artifacts/DOCWIZ-QA-STEP3-IMPL-01/**`, `tasks/postenhancement/backend/DOCWIZ-QA-STEP3-IMPL-01.md` | Runs after BE+FE preview slices finish | Audit evidence and close summary for Step 3 preview implementation wave | No product behavior outside the Step 3 preview slice |

## Verification

- `ruff check --fix backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py`
- `ruff format backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py`
- `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py`
- `cd frontend && npm run lint -- src/modules/documents/pages/DocumentWizard.vue src/api/documents.ts src/api/documents.types.ts`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh DOCWIZ-STEP3-BE-PREVIEW-01`
- `./scripts/task_validate.sh DOCWIZ-STEP3-FE-PREVIEW-01`
- `./scripts/task_validate.sh DOCWIZ-QA-STEP3-IMPL-01`

## Done Definition

- Backend preview endpoint/service/schema exist without writing real tasks
- Wizard Step 3 shows candidate preview, editable fields, and empty state
- Step 3 remains in-memory only
- Required artifacts exist and all task gates pass
