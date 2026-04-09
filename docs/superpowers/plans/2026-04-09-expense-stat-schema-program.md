# Expense Stat Schema Program Plan

- date: `2026-04-09`
- design: `docs/superpowers/specs/2026-04-09-expense-stat-schema-program-design.md`

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `prereq-heavy with one implementation-ready lane`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

### Wave 1

- `EXPSTAT-SCHEMA-PROGRAM-SPEC-01`
  - owner: `main thread`
  - exact closure slice:
    - freeze staged implementation program for remaining Module 4 residuals
  - explicit non-closure:
    - no product code
    - no migration execution

### Wave 2

- `EXPSTAT-QA-SCHEMA-PROGRAM-SPEC-01`
  - owner: `main thread`
  - exact closure slice:
    - audit program-spec wave evidence
  - explicit non-closure:
    - no product code

### Wave 3

- `EXPSTAT-WORKER-DB-01`
  - owner: `main thread`
  - exact closure slice:
    - add `worker_id` carrier to expense schema/model
  - explicit non-closure:
    - no department carrier
    - no FE path

### Wave 4

- `EXPSTAT-WORKER-BE-01`
  - owner: `main thread`
  - exact closure slice:
    - backend worker filter/create semantics + targeted tests
  - explicit non-closure:
    - no FE path
    - no department lane

### Wave 5

- `EXPSTAT-WORKER-FE-01`
  - owner: `main thread`
  - exact closure slice:
    - frontend worker input/filter path
  - explicit non-closure:
    - no department lane

### Wave 6

- `EXPSTAT-WORKER-QA-01`
  - owner: `main thread`
  - exact closure slice:
    - worker lane close audit
  - explicit non-closure:
    - no Module 4 full close

### Wave 7

- `EXPSTAT-DEPARTMENT-MASTER-PRE-01`
  - owner: `main thread`
  - exact closure slice:
    - freeze future organization/department master prerequisite
  - explicit non-closure:
    - no department schema implementation
    - no worker changes

## Serialized Shared-file Decisions

- `backend/app/modules/expenses/models.py` and alembic versions require serialized DB ownership
- `backend/app/modules/expenses/api.py|service.py|backend/tests/test_expense_stats_api.py` require serialized backend ownership
- `frontend/src/api/expenses.ts|frontend/src/api/expenses.types.ts|frontend/src/modules/expenses/pages/ExpenseCreate.vue|frontend/src/modules/expenses/pages/ExpenseList.vue` require serialized frontend ownership
- `EXPSTAT-DEPARTMENT-MASTER-PRE-01` remains doc/task only

## Verification

- `./scripts/task_validate.sh EXPSTAT-SCHEMA-PROGRAM-SPEC-01`
- `./scripts/task_validate.sh EXPSTAT-QA-SCHEMA-PROGRAM-SPEC-01`
