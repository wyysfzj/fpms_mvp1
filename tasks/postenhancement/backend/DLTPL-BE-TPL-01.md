# DLTPL-BE-TPL-01 — 任务模板提醒字段 CRUD contract

- Source: `docs/superpowers/plans/2026-03-29-task-template-reminder-fields-prereq.md`
- Type: `api + schema`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 补齐 `TaskTemplate` CRUD contract，使模板 API 能读取和保存提醒关键字段。
- Exact closure slice:
  - 更新 `TaskTemplateCreateIn / UpdateIn / Out`
  - 更新模板 CRUD endpoint 读写行为
  - 修正模板 CRUD 的原子写入与基础 supervisor 校验
  - 增加对应 API 测试
- Explicit non-closure:
  - 不实现 generation logic 生效
  - 不实现前端模板页面
  - 不修改 reminder execution path
- Remaining follow-up task ids:
  - `DLTPL-BE-GEN-01`
  - `DLTPL-FE-TPL-01`
  - `DLTPL-QA-01`
- Allowlist:
  - `backend/app/modules/tasks/api.py`
  - `backend/app/modules/tasks/schemas.py`
  - `backend/app/modules/tasks/service.py`
  - `backend/tests/test_task_template.py`
- Shared ownership files:
  - `backend/app/modules/tasks/api.py`
  - `backend/app/modules/tasks/schemas.py`
  - `backend/app/modules/tasks/service.py`
- Verification:
  - `ruff check backend/app/modules/tasks/api.py backend/app/modules/tasks/schemas.py backend/app/modules/tasks/service.py backend/tests/test_task_template.py`
  - `cd backend && pytest -q tests/test_task_template.py -k 'template'`
  - `./scripts/task_validate.sh DLTPL-BE-TPL-01`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Write failing API/schema tests first
- [ ] Verify RED
- [ ] Implement minimal contract changes
- [ ] Run listed verification commands
- [ ] Generate required artifacts including dirty baseline files
