# PE-BE-DB-02 — 新增 `T_PayList`（官费清单头）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `schema`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：新增 `T_PayList`（官费清单头）。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_pay_list.py`
  - `backend/app/modules/annuity/models.py`
- 依赖：PE-BE-DB-01
- 验收：表结构含状态/币种/日期/创建审计字段。
- 验证：`cd backend && alembic upgrade head`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
