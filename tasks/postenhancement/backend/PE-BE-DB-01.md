# PE-BE-DB-01 — 新增 `T_Expense`（通用第三方支出）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `schema`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：新增 `T_Expense`（通用第三方支出）。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_expense.py`
  - `backend/app/modules/expenses/models.py`
- 依赖：PE-BE-00-01
- 验收：SQLite migrate 成功，模型可导入。
- 验证：`cd backend && alembic upgrade head && python3 -m py_compile app/modules/expenses/models.py`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
