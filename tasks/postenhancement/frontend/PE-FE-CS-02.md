# PE-FE-CS-02 — 支出录入与列表页（可复用于普通案件与顾问项目）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
- Type: `endpoint page`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：支出录入与列表页（可复用于普通案件与顾问项目）。
- Allowlist:
  - `frontend/src/modules/expenses/pages/ExpenseList.vue` (new)
  - `frontend/src/modules/expenses/pages/ExpenseCreate.vue` (new)
  - `frontend/src/api/expenses.ts` (new)
  - `frontend/src/api/expenses.types.ts` (new)
- 依赖：PE-BE-CS-02, PE-BE-CS-03
- 验收：按案件/类别/时间筛选。
- 验证：`npm run lint && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Record manual verification if UI task
