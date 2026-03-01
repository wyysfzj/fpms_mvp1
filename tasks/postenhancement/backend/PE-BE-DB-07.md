# PE-BE-DB-07 — 新增 `T_Commission`。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `schema`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：新增 `T_Commission`。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_commission.py`
  - `backend/app/modules/commission/models.py`
- 依赖：PE-BE-DB-06
- 验收：支持 base fee、阶段金额、状态与可结算标志。
- 验证：`cd backend && alembic upgrade head`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
