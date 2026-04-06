# Fee Overview Frontend Implementation Plan

- date: `2026-04-06`
- target slice: `FEOVERVIEW-FE-01`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: low
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

### `FEOVERVIEW-FE-01`

- exact closure slice:
  - replace the legacy unified-query page with the truthful `SPEC 5.11` two-pane frontend user path
  - add upper-pane API client/types
  - add lower-pane API client/types
  - connect the page to the dedicated upper/lower endpoints
  - update the visible menu label to `费用情况一览`
- explicit non-closure:
  - no backend changes
  - no export/print
  - no unified-query backend removal
  - no close-decision update
  - no unsupported upper-pane `fee_type` filter
- allowlist:
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/constants/menu.ts`
  - `frontend/src/modules/billing/pages/FeeUnifiedQuery.vue`
- verification:
  - `cd frontend && npm run lint -- src/api/billing.ts src/api/billing.types.ts src/constants/menu.ts src/modules/billing/pages/FeeUnifiedQuery.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh FEOVERVIEW-FE-01`
- evidence path:
  - `artifacts/FEOVERVIEW-FE-01/**`
- remaining follow-up task ids:
  - `FEOVERVIEW-QA-01`

### `FEOVERVIEW-QA-01`

- exact closure slice:
  - audit evidence, gates, and scope compliance for the fee-overview frontend slice
- explicit non-closure:
  - no product-code changes
  - no close-decision update
- allowlist:
  - task/docs/artifacts only
- verification:
  - `./scripts/task_validate.sh FEOVERVIEW-FE-01`
  - `./scripts/task_validate.sh FEOVERVIEW-QA-01`
- evidence path:
  - `artifacts/FEOVERVIEW-QA-01/**`
- remaining follow-up task ids:
  - `None`

## Serialized Shared-file Decisions

- `frontend/src/api/billing.ts|frontend/src/api/billing.types.ts|frontend/src/constants/menu.ts|frontend/src/modules/billing/pages/FeeUnifiedQuery.vue` -> frontend wave only
