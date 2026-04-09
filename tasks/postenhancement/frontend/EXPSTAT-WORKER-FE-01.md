# EXPSTAT-WORKER-FE-01 — worker user path for expense create/list

- Source: `docs/superpowers/plans/2026-04-09-expense-stat-schema-program.md`
- Type: `frontend`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 接入支出录入和支出查询中的真实 `经手人` 用户路径。
- Exact closure slice:
  - create page supports worker selection/input
  - list page supports worker filter
  - frontend API/types updated
- Explicit non-closure:
  - 不做 department lane
  - 不做 Module 4 close decision
- Remaining follow-up task ids:
  - `EXPSTAT-WORKER-QA-01`
- Allowlist:
  - `frontend/src/api/expenses.ts`
  - `frontend/src/api/expenses.types.ts`
  - `frontend/src/modules/expenses/pages/ExpenseCreate.vue`
  - `frontend/src/modules/expenses/pages/ExpenseList.vue`
- Verification:
  - frontend lint
  - typecheck
