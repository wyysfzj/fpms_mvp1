# DLTPL-BE-GEN-01 — 新任务时限与提醒生成逻辑

- Source: `docs/superpowers/plans/2026-03-29-task-template-reminder-fields-prereq.md`
- Type: `service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 让 `task_generation_service` 读取模板提醒关键字段，并对新生成任务的 deadline / remind1/2/3 / daily_remind 结果生效。
- Exact closure slice:
  - 更新 `task_generation_service.py`
  - 增加对应生成逻辑测试
- Explicit non-closure:
  - 不回填已有 task
  - 不改模板前端表单
  - 不改提醒页展示
- Remaining follow-up task ids:
  - `DLTPL-FE-TPL-01`
  - `DLTPL-QA-01`
- Allowlist:
  - `backend/app/modules/tasks/task_generation_service.py`
  - `backend/tests/test_task_generation.py`
- Shared ownership files:
  - `backend/app/modules/tasks/task_generation_service.py`
- Verification:
  - `ruff check backend/app/modules/tasks/task_generation_service.py backend/tests/test_task_generation.py`
  - `cd backend && pytest -q tests/test_task_generation.py`
  - `./scripts/task_validate.sh DLTPL-BE-GEN-01`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Write failing generation tests first
- [ ] Verify RED
- [ ] Implement minimal service changes
- [ ] Run listed verification commands
- [ ] Generate required artifacts including dirty baseline files
