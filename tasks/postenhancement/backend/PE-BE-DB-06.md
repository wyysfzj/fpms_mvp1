# PE-BE-DB-06 — 新增 `T_CommissionRule`。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `schema`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：新增 `T_CommissionRule`。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_commission_rule.py`
  - `backend/app/modules/commission/models.py`
- 依赖：PE-BE-00-02
- 验收：规则支持 CaseType/FeeType/S1/S2/WaitPay/ForceSettle。
- 验证：`cd backend && alembic upgrade head`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
