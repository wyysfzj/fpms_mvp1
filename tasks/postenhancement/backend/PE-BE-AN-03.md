# PE-BE-AN-03 — `PUT /annuity/tasks/{task_id}/instruction`（客户指示录入）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`PUT /annuity/tasks/{task_id}/instruction`（客户指示录入）。
- Allowlist:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
- 依赖：PE-BE-AN-02
- 验收：状态流转合法，400/404/409 语义正确。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
