# PE-BE-CS-02 — `POST /expenses`（支出录入）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`POST /expenses`（支出录入）。
- Allowlist:
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`
- 依赖：PE-BE-DB-01
- 验收：支持 case/category/date/amount 校验。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
