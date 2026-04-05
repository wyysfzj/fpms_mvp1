# GF-NOTICE-DOC-01 Plan

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `cross-module FE/BE notice document generation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `GF-NOTICE-DOC-BE-01` | main thread | `backend/app/modules/grant_fees/api.py`, `backend/app/modules/grant_fees/schemas.py`, `backend/app/modules/grant_fees/service.py`, `backend/tests/test_grant_fee_notice_document_api.py` | Depends on `GF-NOTICE-DOC-SPEC-01`; must not absorb reminder generation or document-detail work | Add batch notice-generation endpoint, real `Document` + attachment creation, and task write-back | No reminder generation, no dispatch/envelope, no bill linkage |
| `GF-NOTICE-DOC-FE-01` | main thread | `frontend/src/api/grantFees.ts`, `frontend/src/api/grantFees.types.ts`, `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue` | Runs after backend contract is fixed | Add real batch “生成通知函” path on existing grant-fee page | No document detail page, no dispatch UI |
| `GF-NOTICE-DOC-QA-01` | main thread | `artifacts/GF-NOTICE-DOC-BE-01/**`, `artifacts/GF-NOTICE-DOC-FE-01/**`, `artifacts/GF-NOTICE-DOC-QA-01/**`, `tasks/postenhancement/backend/GF-NOTICE-DOC-QA-01.md` | Runs after BE and FE closures | Audit evidence, gates, and exact closure for real notice-generation slice | No product-code changes |

## Serialized Shared-file Decisions

- Backend files must be owned first:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_grant_fee_notice_document_api.py`
- Frontend files attach only after backend contract is frozen:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`

## Verification

- `python3 -m ruff format backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_notice_document_api.py`
- `python3 -m ruff check backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_notice_document_api.py`
- `cd backend && pytest -q tests/test_grant_fee_notice_document_api.py`
- `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh GF-NOTICE-DOC-BE-01`
- `./scripts/task_validate.sh GF-NOTICE-DOC-FE-01`
- `./scripts/task_validate.sh GF-NOTICE-DOC-QA-01`

## Done Definition

- Real grant-fee notice documents can be batch-generated from the existing worklist
- Each successful selected row creates one `Document` and one docx attachment
- Task write-back updates `notice_sent / notify_count`
- Required artifacts exist and all task gates pass
