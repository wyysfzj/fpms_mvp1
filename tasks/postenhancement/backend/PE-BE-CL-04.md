# PE-BE-CL-04 — `POST /bills/{bill_id}/bad-debt`。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`POST /bills/{bill_id}/bad-debt`。
- Allowlist:
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`
- 依赖：PE-BE-CL-01
- 验收：仅允许未核销余额账单进入坏账。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
