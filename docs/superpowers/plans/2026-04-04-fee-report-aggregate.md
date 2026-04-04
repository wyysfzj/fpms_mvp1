# FEERPT-AGGREGATE-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `resolved by residual map`
- `be_fe_coupling`: `shared summary contract across API client and FeeDraftList page`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `FEERPT-AGG-BE-01` | main thread | `backend/app/modules/fees/service.py`, `backend/app/modules/fees/schemas.py`, `backend/tests/test_fee_report.py` | Depends on `FEERPT-RESIDUAL-01` | Extend `GET /fees/drafts` summary with `client_amounts`, `case_type_amounts`, and `country_amounts` | No agent-income, no billed/received/unpaid semantics, no frontend, no schema changes |
| `FEERPT-AGG-FE-01` | main thread | `frontend/src/api/fees.ts`, `frontend/src/api/fees.types.ts`, `frontend/src/modules/fees/pages/FeeDraftList.vue` | Runs after backend summary contract is stable | Render grouped fee-report amount summaries on existing fee report page | No new page, no chart/export, no agent-income UI, no trend UI |
| `FEERPT-AGG-QA-01` | main thread | `artifacts/FEERPT-AGG-BE-01/**`, `artifacts/FEERPT-AGG-FE-01/**`, `artifacts/FEERPT-AGG-QA-01/**`, `tasks/postenhancement/backend/FEERPT-AGG-QA-01.md` | Runs after BE/FE completion | Audit evidence, gates, and exact close summary for the grouped fee-aggregate slice | No product-code changes |

## Serialized Shared-file Decisions

- Backend wave owns:
  - `backend/app/modules/fees/service.py`
  - `backend/app/modules/fees/schemas.py`
  - `backend/tests/test_fee_report.py`
- Frontend wave owns:
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
  - `frontend/src/modules/fees/pages/FeeDraftList.vue`

## Verification

- `python3 -m ruff format backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/tests/test_fee_report.py`
- `python3 -m ruff check backend/app/modules/fees/api.py backend/app/modules/fees/service.py backend/app/modules/fees/schemas.py backend/tests/test_fee_report.py`
- `cd backend && pytest -q tests/test_fee_report.py`
- `cd frontend && npm run lint -- src/api/fees.ts src/api/fees.types.ts src/modules/fees/pages/FeeDraftList.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh FEERPT-AGG-BE-01`
- `./scripts/task_validate.sh FEERPT-AGG-FE-01`
- `./scripts/task_validate.sh FEERPT-AGG-QA-01`

## Done Definition

- backend summary returns the three grouped amount arrays
- frontend renders the grouped summaries in Simplified Chinese
- grouped summaries stay inside fee-draft semantics only
- billed / received / unpaid and trend reporting remain deferred
- required artifacts exist and all task gates pass
