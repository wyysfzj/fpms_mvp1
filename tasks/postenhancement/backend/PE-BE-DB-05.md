# PE-BE-DB-05 — 新增 `T_Dunning` + `T_DunningLine`。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `schema`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：新增 `T_Dunning` + `T_DunningLine`。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_dunning.py`
  - `backend/app/modules/collections/models.py`
- 依赖：PE-BE-00-01
- 验收：支持多轮催款与账单快照。
- 验证：`cd backend && alembic upgrade head`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
