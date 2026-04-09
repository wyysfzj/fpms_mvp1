# Department Master Program Plan

- date: `2026-04-09`
- design: `docs/superpowers/specs/2026-04-09-department-master-program-design.md`

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `medium`
- `evidence_cost`: `high`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

### Wave 1

- `DEPTMASTER-PROGRAM-SPEC-01`
  - owner: `main thread`
  - exact closure slice:
    - freeze department master implementation program and task graph
  - explicit non-closure:
    - no product code
    - no migration execution

### Wave 2

- `DEPTMASTER-QA-PROGRAM-SPEC-01`
  - owner: `main thread`
  - exact closure slice:
    - audit program-spec wave evidence
  - explicit non-closure:
    - no product code

### Future Waves

- `DEPTMASTER-DB-01`
  - exact closure slice:
    - add department master schema/model/migration
  - explicit non-closure:
    - no expense `department_id`
- `DEPTMASTER-BE-01`
  - exact closure slice:
    - add department master backend list/create/update/deactivate contract
  - explicit non-closure:
    - no expense department stats
- `DEPTMASTER-FE-01`
  - exact closure slice:
    - add department master management path
  - explicit non-closure:
    - no expense department stats
- `EXPSTAT-DEPARTMENT-DB-01`
  - exact closure slice:
    - add `t_expense.department_id`
  - explicit non-closure:
    - no backend aggregation semantics
- `EXPSTAT-DEPARTMENT-BE-01`
  - exact closure slice:
    - expense backend create/filter/group semantics for department
  - explicit non-closure:
    - no frontend path
- `EXPSTAT-DEPARTMENT-FE-01`
  - exact closure slice:
    - expense frontend department input/filter/stats path
  - explicit non-closure:
    - no close audit
- `EXPSTAT-DEPARTMENT-QA-01`
  - exact closure slice:
    - audit department lane DB/BE/FE evidence
  - explicit non-closure:
    - no Module 4 full close

## Serialized Shared-file Decisions

- `backend/app/api/router.py` requires serialized ownership if a new department module is introduced
- `backend/app/modules/expenses/models.py` and future alembic files require serialized DB ownership
- `backend/app/modules/expenses/api.py|service.py|backend/tests/test_expense_stats_api.py` require serialized backend ownership
- any new `masterdata/departments/*` files should be owned only by department-master waves
- `frontend/src/api/expenses.ts|frontend/src/api/expenses.types.ts|frontend/src/modules/expenses/pages/*.vue` require serialized FE ownership

## Verification

- `./scripts/task_validate.sh DEPTMASTER-PROGRAM-SPEC-01`
- `./scripts/task_validate.sh DEPTMASTER-QA-PROGRAM-SPEC-01`
