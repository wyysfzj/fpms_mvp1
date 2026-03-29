# DLTPL-FE-TPL-01 — 任务模板提醒字段前端配置

- Source: `docs/superpowers/plans/2026-03-29-task-template-reminder-fields-prereq.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 在任务模板管理页补齐提醒关键字段输入与展示，并对齐后端模板 contract。
- Exact closure slice:
  - 更新 `tasks.ts` / `tasks.types.ts`
  - 更新 `TaskTemplateList.vue`
- Explicit non-closure:
  - 不改任务列表、今日提醒页、任务详情页
  - 不实现 reminder execution 逻辑
  - 不新增 reminder 专用权限
- Remaining follow-up task ids:
  - `DLTPL-QA-01`
- Allowlist:
  - `frontend/src/api/tasks.ts`
  - `frontend/src/api/tasks.types.ts`
  - `frontend/src/modules/system/pages/TaskTemplateList.vue`
- Shared ownership files:
  - `frontend/src/api/tasks.ts`
  - `frontend/src/api/tasks.types.ts`
  - `frontend/src/modules/system/pages/TaskTemplateList.vue`
- Verification:
  - `cd frontend && npm run lint -- src/api/tasks.ts src/api/tasks.types.ts src/modules/system/pages/TaskTemplateList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh DLTPL-FE-TPL-01`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add validation-first UI/API coverage
- [ ] Implement minimal UI + API mapping changes only
- [ ] Run listed verification commands
- [ ] Generate required artifacts including dirty baseline files
