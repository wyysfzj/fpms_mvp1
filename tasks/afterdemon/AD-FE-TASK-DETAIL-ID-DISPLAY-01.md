# AD-FE-TASK-DETAIL-ID-DISPLAY-01 — task detail visible ID cleanup

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

Remove visible raw task/case/user internal ID displays from the task detail page.

This closes only:

1. `TaskDetail.vue` no longer renders `#<task.id>` in the task header.
2. `TaskDetail.vue` case links keep using `case_id` internally, but visible text uses `case_no` or a Chinese business fallback.
3. `TaskDetail.vue` worker and supervisor fields no longer show raw internal user IDs; when only an internal ID exists, the page shows a Chinese assignment placeholder.

## Explicit Non-Closure

This task does not:

- modify backend code, task API wrappers/types, route params, task list/create/special-search pages, dashboard reminders, logs, permissions, or response envelopes.
- add user-name resolution, user selector behavior, or any new API join.
- change task status transitions, delete/close/reopen/cancel behavior, task log loading, tabs, filters, pagination, export, or print behavior.
- close raw-ID display issues outside `TaskDetail.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-TODAY-REMINDERS-ID-DISPLAY-01`
- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-COMMISSION-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-CONSULTING-EXPENSE-ID-DISPLAY-01`
- `AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-TASK-DETAIL-ID-DISPLAY-01.md`
- `frontend/src/modules/tasks/pages/TaskDetail.vue`
- `artifacts/AD-FE-TASK-DETAIL-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-TASK-DETAIL-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/tasks/pages/TaskDetail.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-TASK-DETAIL-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-TASK-DETAIL-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "#\\{\\{ task\\.id \\}\\}|案件 #\\$\\{task\\.case_id\\}|\\{\\{ task\\.worker_id|\\{\\{ task\\.supervisor_id" frontend/src/modules/tasks/pages/TaskDetail.vue && rg -n "formatTaskDisplayTitle|formatCaseDisplay|formatAssigneeDisplay|未命名任务|未命名案件|已指定" frontend/src/modules/tasks/pages/TaskDetail.vue'
./scripts/evidence_run.sh AD-FE-TASK-DETAIL-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-TASK-DETAIL-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-TASK-DETAIL-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-TASK-DETAIL-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-TASK-DETAIL-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-TASK-DETAIL-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-TASK-DETAIL-ID-DISPLAY-01/baseline_external_files.txt`
