# PE-FE-DL-03 — Tasks frontend follow-up for views and today reminders.

- Source: `tasks/postenhancement/BATCH2_REMAINING_MANIFEST_20260316.md`
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close the remaining feasible Batch 2 frontend Tasks scope for role views, today reminders, and dashboard entry.
- Covered items:
  - `US-DL-01`
  - `US-DL-03`
  - `US-DL-04`
  - `US-DL-07`
  - `FR-DL-01`
  - `FR-DL-04`
  - `FR-DL-05`
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
- Out of scope:
  - document generation
  - unrelated dashboard redesign
  - Batch 3+
- Acceptance:
  - TaskList supports worker/supervisor Batch 2 view expectations
  - TodayReminders and Dashboard can show today items with enough context
  - TaskTemplateList exposes the existing template rule fields more completely
- Verification:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Implement minimal UI + API mapping changes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
