# Expense Gross-Profit Implementation Plan

- date: `2026-04-06`
- target slice: `EXPSTAT-GROSSPROFIT-01`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: low
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

### `EXPSTAT-GROSSPROFIT-BE-01`

- exact closure slice:
  - add case-level `gross_profit_amounts` to `GET /expenses?include_stats=true`
  - cover receipt-minus-expense semantics with targeted backend tests
- explicit non-closure:
  - no frontend changes
  - no client/department/worker gross-profit
  - no FX conversion
  - no `SPEC 5.11`
- allowlist:
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`
  - `backend/tests/test_expense_stats_api.py`
- verification:
  - `python3 -m ruff check backend/app/modules/expenses/api.py backend/app/modules/expenses/service.py backend/tests/test_expense_stats_api.py`
  - `cd backend && pytest -q tests/test_expense_stats_api.py`
  - `./scripts/task_validate.sh EXPSTAT-GROSSPROFIT-BE-01`
- evidence path:
  - `artifacts/EXPSTAT-GROSSPROFIT-BE-01/**`
- remaining follow-up task ids:
  - `EXPSTAT-GROSSPROFIT-FE-01`
  - `EXPSTAT-GROSSPROFIT-QA-01`

### `EXPSTAT-GROSSPROFIT-FE-01`

- exact closure slice:
  - render case-level gross-profit grouped summary cards on `ExpenseList.vue`
- explicit non-closure:
  - no backend changes
  - no client/department/worker gross-profit UI
  - no `SPEC 5.11` UI
- allowlist:
  - `frontend/src/api/expenses.ts`
  - `frontend/src/api/expenses.types.ts`
  - `frontend/src/modules/expenses/pages/ExpenseList.vue`
- verification:
  - `cd frontend && npm run lint -- src/api/expenses.ts src/api/expenses.types.ts src/modules/expenses/pages/ExpenseList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh EXPSTAT-GROSSPROFIT-FE-01`
- evidence path:
  - `artifacts/EXPSTAT-GROSSPROFIT-FE-01/**`
- remaining follow-up task ids:
  - `EXPSTAT-GROSSPROFIT-QA-01`

### `EXPSTAT-GROSSPROFIT-QA-01`

- exact closure slice:
  - audit evidence, gates, and scope compliance for the expense gross-profit slice
- explicit non-closure:
  - no product-code changes
  - no close-decision update
- allowlist:
  - task/docs/artifacts only
- verification:
  - `./scripts/task_validate.sh EXPSTAT-GROSSPROFIT-BE-01`
  - `./scripts/task_validate.sh EXPSTAT-GROSSPROFIT-FE-01`
  - `./scripts/task_validate.sh EXPSTAT-GROSSPROFIT-QA-01`
- evidence path:
  - `artifacts/EXPSTAT-GROSSPROFIT-QA-01/**`
- remaining follow-up task ids:
  - `None`

## Serialized Shared-file Decisions

- `backend/app/modules/expenses/api.py|service.py|backend/tests/test_expense_stats_api.py` -> BE wave only
- `frontend/src/api/expenses.ts|expenses.types.ts|frontend/src/modules/expenses/pages/ExpenseList.vue` -> FE wave only
