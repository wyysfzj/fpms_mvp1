# PE-BE-DB-03 — 新增 `T_GovPayment`（官费缴费明细）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `schema`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：新增 `T_GovPayment`（官费缴费明细）。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_gov_payment.py`
  - `backend/app/modules/annuity/models.py`
- 依赖：PE-BE-DB-02
- 验收：与 `T_PayList`/Case/FeeItem 外键正确。
- 验证：`cd backend && alembic upgrade head`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
