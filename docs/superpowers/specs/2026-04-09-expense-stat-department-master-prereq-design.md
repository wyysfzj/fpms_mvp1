# Expense Stat Department Master Prerequisite Design

- date: `2026-04-09`
- task: `EXPSTAT-DEPARTMENT-MASTER-PRE-01`

## Problem

`SPEC 5.10.2` 仍要求 `每部门支出`，但当前仓库不存在可被 truthful 复用的 department carrier。`T_Expense.department_id` 已被冻结为未来方向，但 FK target 仍不存在。

## Current Evidence

- `backend/app/modules/expenses/models.py`
  - `T_Expense` 当前没有 `department_id`
- `backend/app/modules/auth/models.py`
  - `T_User` 当前没有 `department_id`
- `backend/app/modules/cases/models.py`
  - `T_Case` 当前没有 department carrier
- `backend/app/modules/masterdata/clients/models.py`
  - client master 也不是部门 carrier
- repo 当前不存在 department / organization master model

## Rejected Pseudo-closures

- 用 case bucket 冒充 department totals
- 用 client bucket 冒充 department totals
- 把当前 `T_User` 外推成 department master
- 用任意现有 master-data label 硬映射成部门

## Authority Freeze

- future department statistics 必须先引入真实 department master / organization carrier
- future `T_Expense.department_id` 应引用新的 department master 主键，而不是复用现有 case/client/user 字段
- first-round backfill 继续采用 `null-first`
- 在真实 department master 存在前，department lane 不得进入 schema/product implementation

## Result

- Module 4 的 department residual 进入新的 prerequisite lane
- next prerequisite:
  - `organization/department master program`
- follow-up after that:
  - `T_Expense.department_id` schema lane
  - department backend aggregation lane
  - department frontend path

## Non-closure

- 不做 department schema implementation
- 不做 worker lane
- 不做任何产品代码
- 不更新 final audit / close decision
