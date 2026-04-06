# Fee Overview Upper Fee-Type Implementation Plan

- date: `2026-04-06`
- target slice: `FEOVERVIEW-UPPER-FEETYPE`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: low
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

### `FEOVERVIEW-UPPER-FEETYPE-BE-01`

- exact closure slice:
  - add truthful first-round `fee_type` filter support to `GET /fee-overview/gov-payments`
  - implement the filter via `FeeDraft.draft_type`
  - add targeted backend tests
- explicit non-closure:
  - no lower-pane changes
  - no frontend changes
  - no table column expansion
  - no export/print
  - no schema/migration
- allowlist:
  - `backend/app/modules/billing/api.py`
  - `backend/app/modules/billing/service.py`
  - `backend/tests/test_fee_overview_upper_api.py`
- verification:
  - `python3 -m ruff check backend/app/modules/billing/api.py backend/app/modules/billing/service.py backend/tests/test_fee_overview_upper_api.py`
  - `cd backend && pytest -q tests/test_fee_overview_upper_api.py`
  - `./scripts/task_validate.sh FEOVERVIEW-UPPER-FEETYPE-BE-01`
- evidence path:
  - `artifacts/FEOVERVIEW-UPPER-FEETYPE-BE-01/**`
- remaining follow-up task ids:
  - `FEOVERVIEW-UPPER-FEETYPE-FE-01`
  - `FEOVERVIEW-UPPER-FEETYPE-QA-01`

### `FEOVERVIEW-UPPER-FEETYPE-FE-01`

- exact closure slice:
  - add the truthful first-round `fee_type` selector to the upper pane of `费用情况查询一览`
  - send the selected value to `/fee-overview/gov-payments`
- explicit non-closure:
  - no lower-pane changes
  - no result-table column expansion
  - no export/print
  - no close-decision update
- allowlist:
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/modules/billing/pages/FeeUnifiedQuery.vue`
- verification:
  - `cd frontend && npm run lint -- src/api/billing.ts src/api/billing.types.ts src/modules/billing/pages/FeeUnifiedQuery.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh FEOVERVIEW-UPPER-FEETYPE-FE-01`
- evidence path:
  - `artifacts/FEOVERVIEW-UPPER-FEETYPE-FE-01/**`
- remaining follow-up task ids:
  - `FEOVERVIEW-UPPER-FEETYPE-QA-01`

### `FEOVERVIEW-UPPER-FEETYPE-QA-01`

- exact closure slice:
  - audit evidence, gates, and scope compliance for the upper-pane fee-type implementation batch
- explicit non-closure:
  - no product-code changes
  - no close-decision update
- allowlist:
  - task/docs/artifacts only
- verification:
  - `./scripts/task_validate.sh FEOVERVIEW-UPPER-FEETYPE-BE-01`
  - `./scripts/task_validate.sh FEOVERVIEW-UPPER-FEETYPE-FE-01`
  - `./scripts/task_validate.sh FEOVERVIEW-UPPER-FEETYPE-QA-01`
- evidence path:
  - `artifacts/FEOVERVIEW-UPPER-FEETYPE-QA-01/**`
- remaining follow-up task ids:
  - `None`

## Serialized Shared-file Decisions

- `backend/app/modules/billing/api.py|backend/app/modules/billing/service.py|backend/tests/test_fee_overview_upper_api.py` -> backend wave only
- `frontend/src/api/billing.ts|frontend/src/api/billing.types.ts|frontend/src/modules/billing/pages/FeeUnifiedQuery.vue` -> frontend wave only
