# PE-BE-CL-05 — `POST /bills/{bill_id}/bad-debt/restore`。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`POST /bills/{bill_id}/bad-debt/restore`。
- Allowlist:
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`
- 依赖：PE-BE-CL-04
- 验收：坏账恢复后状态一致。
- 验证：`cd backend && pytest -q`

---

## BE-B4 — Commission

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
