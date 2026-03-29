# DLTPL-DB-01 — 任务模板提醒关键字段持久化前置任务

- Source: `docs/superpowers/plans/2026-03-29-task-template-reminder-fields-prereq.md`
- Type: `migration + model`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为 `TaskTemplate` 与 `Task` 增加 `deadline_base / remind_base / remind_1/2/3_offset_days / daily_remind / default_supervisor_id` 及运行时提醒承载字段，保持 SQLite-safe schema/model 对齐。
- Exact closure slice:
  - 新增 SQLite-safe migration
  - 更新 `backend/app/modules/tasks/models.py`
  - 如需要，补充 `backend/app/modules/tasks/enums.py` 中的稳定枚举
- Explicit non-closure:
  - 不实现模板 CRUD contract
  - 不实现 `task_generation_service`
  - 不实现前端表单
  - 不实现历史 task 回填或重算
- Remaining follow-up task ids:
  - `DLTPL-BE-TPL-01`
  - `DLTPL-BE-GEN-01`
  - `DLTPL-FE-TPL-01`
  - `DLTPL-QA-01`
- Allowlist:
  - `backend/alembic/versions/dltpl_db_01_task_template_reminder_fields.py`
  - `backend/app/modules/tasks/models.py`
  - `backend/app/modules/tasks/enums.py`
- Shared ownership files:
  - `backend/app/modules/tasks/models.py`
  - `backend/app/modules/tasks/enums.py`
- Verification:
  - `ruff check backend/alembic/versions/dltpl_db_01_task_template_reminder_fields.py backend/app/modules/tasks/models.py backend/app/modules/tasks/enums.py`
  - `cd backend && alembic upgrade head`
  - `./scripts/task_validate.sh DLTPL-DB-01`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Write failing schema/model coverage first
- [ ] Verify RED
- [ ] Implement minimal migration/model change
- [ ] Run listed verification commands
- [ ] Generate required artifacts including dirty baseline files
