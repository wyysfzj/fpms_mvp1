# PE-BE-CL-02 — `POST /dunning`。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`POST /dunning`。
- Allowlist:
  - `backend/app/modules/collections/api.py`
- 依赖：PE-BE-CL-01
- 验收：创建催款批次并返回摘要。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
