# PE-BE-COM-02 — `GET /commission/rules`。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`GET /commission/rules`。
- Allowlist:
  - `backend/app/modules/commission/api.py`
- 依赖：PE-BE-COM-01
- 验收：分页过滤与权限校验通过。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
