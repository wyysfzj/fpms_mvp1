# Department Master Program Design

- date: `2026-04-09`
- target: `Module 4 / SPEC 5.10.2 department residual`

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `medium`
- `evidence_cost`: `high`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`SPEC 5.10.2` 的剩余 gap 里，worker lane 已闭合，但 `每部门支出` 仍缺 truthful carrier。`T_Expense.department_id` 的 ownership 已冻结，但当前 repo 没有可引用的 department master/entity，因此要继续 Module 4 mitigation，必须先开启独立的 department master program。

## Current Evidence

- `backend/app/modules/expenses/models.py`
  - no `department_id`
- `backend/app/modules/auth/models.py`
  - `T_User` has no department field
- `backend/app/modules/cases/models.py`
  - `T_Case` has no department carrier
- `backend/app/modules/masterdata/clients/models.py`
  - `Client` is not a department master
- `backend/app/api/router.py`
  - masterdata modules currently include applicants / clients / countries only

## Authority Freeze

- future department ownership still belongs on `T_Expense.department_id`
- but that FK must target a new department master entity
- department master must be introduced before any expense department schema/product lane
- first-round backfill remains `null-first`

## Recommended Program Shape

1. `DEPTMASTER-DB-01`
   - add new department master model + migration
2. `DEPTMASTER-BE-01`
   - add backend CRUD/list contract for department master
3. `DEPTMASTER-FE-01`
   - add truthful management path for department master
4. `EXPSTAT-DEPARTMENT-DB-01`
   - add `t_expense.department_id`
5. `EXPSTAT-DEPARTMENT-BE-01`
   - add backend create/filter/group semantics
6. `EXPSTAT-DEPARTMENT-FE-01`
   - add expense create/list/stats department path
7. `EXPSTAT-DEPARTMENT-QA-01`
   - close-audit the department lane

## Minimal First-round Department Master

- entity: `Department`
- required fields:
  - `id`
  - `department_code`
  - `name_cn`
  - `is_active`
- optional future fields stay out of scope:
  - hierarchy
  - organization tree
  - manager binding
  - cost center

## Rejected Alternatives

- derive department from `T_User`
- derive department from case/client ownership
- add `t_expense.department_id` before a real FK target exists
- expose FE department selector backed only by hard-coded labels

## Risks

- broadening into a generic HR/organization module
- merging department master and expense department stats into one mega task
- introducing non-SQLite-safe migration patterns

## Non-closure

- this design does not implement department master
- this design does not implement `t_expense.department_id`
- this design does not update final audit / close decision
