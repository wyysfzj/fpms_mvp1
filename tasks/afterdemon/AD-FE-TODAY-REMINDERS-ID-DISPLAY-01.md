# AD-FE-TODAY-REMINDERS-ID-DISPLAY-01 — today reminders visible ID cleanup

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Task Plan Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Remove visible raw task/user internal ID displays from the today reminders page.

This closes only:

1. `TodayReminders.vue` no longer renders raw `task.id` in reminder cards.
2. `TodayReminders.vue` reminder titles use the task title or a Chinese business fallback instead of relying on an internal ID.
3. `TodayReminders.vue` assignee metadata no longer shows raw `worker_id`, `supervisor_id`, or `assigned_to`; when only an internal ID exists, it shows a Chinese assignment placeholder.

## Explicit Non-Closure

This task does not:

- modify backend code, task API wrappers/types, route params, dashboard pages, task list/detail/create/special-search pages, permissions, or response envelopes.
- add user-name resolution, user selector behavior, or any new API join.
- change reminder fetching, worker/supervisor mode, click navigation, status mapping, filters, pagination, export, or print behavior.
- close raw-ID display issues outside `TodayReminders.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-COMMISSION-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-CONSULTING-EXPENSE-ID-DISPLAY-01`
- `AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-TODAY-REMINDERS-ID-DISPLAY-01.md`
- `frontend/src/modules/tasks/pages/TodayReminders.vue`
- `artifacts/AD-FE-TODAY-REMINDERS-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-TODAY-REMINDERS-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/tasks/pages/TodayReminders.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-TODAY-REMINDERS-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-TODAY-REMINDERS-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "\\{\\{ task\\.id \\}\\}|\\$\\{task\\.supervisor_id\\}|\\$\\{task\\.worker_id\\}|\\$\\{task\\.assigned_to\\}" frontend/src/modules/tasks/pages/TodayReminders.vue && rg -n "formatReminderTitle|formatAssigneeDisplay|未命名任务|已指定" frontend/src/modules/tasks/pages/TodayReminders.vue'
./scripts/evidence_run.sh AD-FE-TODAY-REMINDERS-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-TODAY-REMINDERS-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-TODAY-REMINDERS-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-TODAY-REMINDERS-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-TODAY-REMINDERS-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-TODAY-REMINDERS-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-TODAY-REMINDERS-ID-DISPLAY-01/baseline_external_files.txt`
