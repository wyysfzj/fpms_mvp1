# PE-FE-DL-03

Status: PASS

Scope:
- `frontend/src/api/tasks.ts`
- `frontend/src/api/tasks.types.ts`
- `frontend/src/modules/tasks/pages/TaskList.vue`
- `frontend/src/modules/tasks/pages/TodayReminders.vue`
- `frontend/src/modules/dashboard/pages/Dashboard.vue`
- `frontend/src/modules/dashboard/components/TodoTable.vue`

Changes:
- added task list role-view toggle
- consumed enriched today-reminder payload
- wired dashboard todo entry to today's tasks
- displayed case/client context in reminders and dashboard

Validation:
- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`

Notes:
- no new route
- no Batch 3 scope touched
