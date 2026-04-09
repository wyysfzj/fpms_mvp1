# Expense Stat Department Carrier Plan

- date: `2026-04-09`
- design: `docs/superpowers/specs/2026-04-09-expense-stat-department-carrier-design.md`

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `schema-authority first`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-prereq-heavy-story`

## Result Shape

- `department carrier authority freeze only`
- no product implementation in this wave

## Batch Manifest

### Wave 1

- `EXPSTAT-DEPARTMENT-CARRIER-01`
  - owner: `main thread`
  - exact closure slice:
    - freeze business department carrier authority
    - freeze schema/backfill direction
  - explicit non-closure:
    - no worker authority
    - no product code
    - no migration execution

## Serialized Shared-file Decisions

- this wave touches only doc/task files
- future department implementation, if approved later, must serialize ownership over:
  - `backend/app/modules/expenses/models.py`
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`
  - `frontend/src/api/expenses.ts`
  - `frontend/src/api/expenses.types.ts`
  - `frontend/src/modules/expenses/pages/ExpenseList.vue`

## Verification

- `./scripts/task_validate.sh EXPSTAT-DEPARTMENT-CARRIER-01`
