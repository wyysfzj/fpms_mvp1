# PE-FE-DL-02

Status: PASS

Scope:
- `frontend/src/modules/tasks/pages/TaskList.vue`
- `frontend/src/modules/tasks/pages/TaskDetail.vue`
- `frontend/src/modules/tasks/pages/TaskCreate.vue`
- `frontend/src/modules/tasks/pages/TodayReminders.vue`
- `frontend/src/modules/dashboard/pages/Dashboard.vue`
- `frontend/src/modules/dashboard/components/TodoTable.vue`
- `frontend/src/modules/system/pages/TaskTemplateList.vue`
- `frontend/src/api/tasks.ts`
- `frontend/src/api/tasks.types.ts`

Changes:
- added frontend task-delete API wrapper for Batch 2 manual maintenance
- exposed delete action in task list and task detail pages
- kept all changes inside the tasks frontend allowlist

Validation:
- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh PE-FE-DL-02`

Notes:
- this closes a frontend manual-maintenance slice, not all remaining Batch 2 task-view and today-reminder scope
- no document-generation scope was implemented
