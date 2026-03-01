# PE-BE-DB-08 — 新增 `T_CommissionSettlement` + `T_CommissionSettleLine`。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `schema`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：新增 `T_CommissionSettlement` + `T_CommissionSettleLine`。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_commission_settlement.py`
  - `backend/app/modules/commission/models.py`
- 依赖：PE-BE-DB-07
- 验收：可支撑结算批次与明细关联。
- 验证：`cd backend && alembic upgrade head`

---

## BE-B2 — Annual Fee 生命周期

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
