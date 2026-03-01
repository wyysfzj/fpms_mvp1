# PE-BE-DB-04 — 新增 `T_AnnuityTask`（年费任务）。

- Source: `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
- Type: `schema`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：新增 `T_AnnuityTask`（年费任务）。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_annuity_task.py`
  - `backend/app/modules/annuity/models.py`
- 依赖：PE-BE-00-01
- 验收：支持年度、截止日、客户指示、通知状态字段。
- 验证：`cd backend && alembic upgrade head`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement exactly this task
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
