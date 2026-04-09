# EXPSTAT-DEPARTMENT-MASTER-PRE-01 — department master prerequisite for expense statistics

- Source: `docs/superpowers/plans/2026-04-09-expense-stat-schema-program.md`
- Type: `prerequisite`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 冻结 department lane 的真实 FK target / organization carrier prerequisite，明确 future `department_id` 应该引用什么实体。
- Exact closure slice:
  - freeze department master/organization prerequisite
  - define future department schema target
- Explicit non-closure:
  - 不做 department schema implementation
  - 不做 worker lane
  - 不做 product code
- Remaining follow-up task ids:
  - `EXPSTAT-CLOSE-02`
- Allowlist:
  - docs/tasks only
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-DEPARTMENT-MASTER-PRE-01`
