# PE-BE-AN-07 — `POST /gov-payments`（官方缴费登记）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `endpoint`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：`POST /gov-payments`（官方缴费登记）。
- Allowlist:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
- 依赖：PE-BE-AN-06
- 验收：可回写清单状态，支持重复保护。
- 验证：`cd backend && pytest -q`

---

## BE-B3 — Dunning / Bad Debt

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
