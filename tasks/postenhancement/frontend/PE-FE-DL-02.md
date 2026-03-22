# PE-FE-DL-02 — Tasks and reminders frontend completion for Batch 2.

- Source: `docs/FPMS_Final_Enhancement_Plan_Native_20260315.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: complete the Batch 2 frontend Tasks/Deadlines scope for task views, today reminders, manual maintenance, and template-related UX gaps.
- Covered items:
  - `US-DL-01`
  - `US-DL-02`
  - `US-DL-03`
  - `US-DL-04`
  - `US-DL-05`
  - `US-DL-07`
  - `FR-DL-01`
  - `FR-DL-02`
  - `FR-DL-04`
  - `FR-DL-05`
  - `FR-DL-06`
  - `FR-DL-08`
- Allowlist:
  - `frontend/src/modules/tasks/pages/TaskList.vue`
  - `frontend/src/modules/tasks/pages/TaskDetail.vue`
  - `frontend/src/modules/tasks/pages/TaskCreate.vue`
  - `frontend/src/modules/tasks/pages/TodayReminders.vue`
  - `frontend/src/modules/dashboard/pages/Dashboard.vue`
  - `frontend/src/modules/dashboard/components/TodoTable.vue`
  - `frontend/src/modules/system/pages/TaskTemplateList.vue`
  - `frontend/src/api/tasks.ts`
  - `frontend/src/api/tasks.types.ts`
- Shared ownership files:
  - `frontend/src/api/tasks.ts`
  - `frontend/src/api/tasks.types.ts`
  - `frontend/src/modules/dashboard/pages/Dashboard.vue`
  - `frontend/src/modules/dashboard/components/TodoTable.vue`
- Out of scope:
  - `Batch 3+`
  - document generation / task-sheet printing
  - unrelated dashboard redesign
- Acceptance:
  - worker and supervisor task views cover Batch 2 filters and display gaps
  - today reminders and dashboard entry reflect the covered backend today APIs
  - manual task maintenance flows are available within Batch 2 scope
  - all user-facing text remains Simplified Chinese
- Verification:
  - `npm run lint`
  - `npm run typecheck`
  - manual notes for task list / detail / create / today reminders / dashboard entry

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal validation-first step
- [ ] Implement minimal UI + API mapping changes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
