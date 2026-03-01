# PE-BE-AN-02 — `GET /annuity/tasks`。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`GET /annuity/tasks`。
- Allowlist:
  - `backend/app/modules/annuity/api.py`
- 依赖：PE-BE-AN-01, PE-BE-00-02
- 验收：分页、过滤、权限与 envelope 符合规范。
- 验证：`cd backend && ruff check . && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
