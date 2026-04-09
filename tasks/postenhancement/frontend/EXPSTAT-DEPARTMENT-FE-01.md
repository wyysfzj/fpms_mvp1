# EXPSTAT-DEPARTMENT-FE-01 — department user path for expense create/list/stats

- Source: `docs/superpowers/plans/2026-04-09-department-master-program.md`
- Type: `frontend`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 接入支出录入、支出查询和统计中的真实 `部门` 用户路径。
- Exact closure slice:
  - create page supports department selection
  - list page supports department filter
  - stats UI shows department totals
  - frontend API/types updated
- Explicit non-closure:
  - 不做 Module 4 final close
  - 不做 worker lane changes
- Remaining follow-up task ids:
  - `EXPSTAT-DEPARTMENT-QA-01`
- Allowlist:
  - `frontend/src/api/expenses.ts`
  - `frontend/src/api/expenses.types.ts`
  - `frontend/src/modules/expenses/pages/ExpenseCreate.vue`
  - `frontend/src/modules/expenses/pages/ExpenseList.vue`
- Verification:
  - frontend lint
  - typecheck
