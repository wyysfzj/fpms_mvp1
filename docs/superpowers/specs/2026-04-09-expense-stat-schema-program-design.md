# Expense Stat Schema Program Design

- date: `2026-04-09`
- target: `Module 4 / SPEC 5.10.2 schema/carrier implementation program`
- source baseline:
  - `docs/FPMS SPEC 2.0.md`
  - `docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md`
  - `docs/superpowers/specs/2026-04-09-expense-stat-worker-carrier-design.md`
  - `docs/superpowers/specs/2026-04-09-expense-stat-department-carrier-design.md`

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `prereq-heavy with one implementation-ready lane`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

Module 4 still contains two truthful residuals under `SPEC 5.10.2`:

- worker-level filtering / worker statistics
- per-department expense totals

Current authority freeze now proves these lanes are no longer symmetric:

- worker lane has a clear first-round truthful carrier:
  - `T_Expense.worker_id`
- department lane does not yet have a realizable FK target in current repo:
  - `T_User` has no department field
  - no department master/entity exists

Therefore the schema/carrier implementation program must be staged:

- worker lane can enter schema-first implementation
- department lane must first add an organization/department carrier prerequisite

## Current Evidence

- `backend/app/modules/expenses/models.py`
  - no `worker_id`
  - no `department_id`
- `backend/app/modules/auth/models.py`
  - `T_User` has no department field
- `backend/app/modules/cases/models.py`
  - no truthful department authority
- `backend/app/modules/masterdata/clients/models.py`
  - no truthful department authority
- `backend/app/modules/admin/api.py`
  - existing `GET /admin/users` can serve as first-round worker picker source

## Worker Implementation Lane

Worker lane is implementation-ready because:

- carrier authority is frozen:
  - future `T_Expense.worker_id`
- FK target already exists:
  - `t_user.id`
- UI can use existing admin user listing first round, or direct user-id selection if necessary

Worker first-round closure slices should include:

- schema/migration for `worker_id`
- create/list contract updates
- worker filter semantics on expense list/statistics
- frontend create/list user path
- targeted tests

## Department Implementation Lane

Department lane is **not** implementation-ready because:

- authority says ownership belongs on `T_Expense.department_id`
- but current repo has no truthful department target to reference
- adding plain text/code fields now would weaken the already-frozen authority

Therefore department lane requires a new prerequisite:

- organization/department master carrier design
- then future `department_id` schema lane

## Truthful Implementation Order

Recommended order:

1. `EXPSTAT-WORKER-DB-01`
2. `EXPSTAT-WORKER-BE-01`
3. `EXPSTAT-WORKER-FE-01`
4. `EXPSTAT-WORKER-QA-01`
5. `EXPSTAT-DEPARTMENT-MASTER-PRE-01`
6. later department schema/product lanes
7. `EXPSTAT-CLOSE-02`

Rejected orders:

- worker + department schema in one broad wave
- adding `department_id` before a truthful department target exists
- closing Module 4 after worker only

## Schema / Migration Plan

Worker lane first round:

- add nullable `worker_id` to `t_expense`
- FK to `t_user.id`
- index on `worker_id`
- keep existing rows null

Department lane:

- no schema execution yet
- first freeze department master/organization carrier

## Nullable / Backfill Strategy

- `worker_id`:
  - nullable first round
  - no automatic backfill from `created_by / updated_by / case owner`
- `department_id`:
  - blocked until future department carrier exists

## Seed / Bootstrap Implication

- worker lane:
  - no mandatory seed change, because users already exist
- department lane:
  - future organization/department seed likely required

## Exact Conclusion

- worker lane can enter schema-first implementation planning now
- department lane still needs an organization/department master prerequisite first

## Explicit Non-closure

This design wave does not:

- implement any product behavior
- add migration now
- update final audit / close decision
- merge worker and department into one implementation task
