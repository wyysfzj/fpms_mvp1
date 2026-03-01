# PE-BE-AN-06 — `POST /pay-lists/from-fee-items`（官费清单生成）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`POST /pay-lists/from-fee-items`（官费清单生成）。
- Allowlist:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
- 依赖：PE-BE-DB-02, PE-BE-DB-03
- 验收：同一 client/currency 约束正确。
- 验证：`cd backend && pytest -q`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
