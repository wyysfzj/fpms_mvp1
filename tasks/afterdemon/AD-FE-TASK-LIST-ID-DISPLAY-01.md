# AD-FE-TASK-LIST-ID-DISPLAY-01 — task list visible ID fallback cleanup

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

Remove visible raw task/case/user internal ID fallbacks from the primary task list and dashboard todo table task-row display.

This closes only:

1. `TaskList.vue` no longer renders the internal task `id` column.
2. `TaskList.vue` case links use `case_no` or a Simplified Chinese placeholder instead of `#<case_id>`.
3. `TaskList.vue` row action aria labels do not fallback to internal task IDs.
4. `TaskList.vue` assignee display hides UUID-shaped internal assignee values behind a Chinese business placeholder.
5. `TodoTable.vue` case links use `case_no` or a Simplified Chinese placeholder instead of a truncated `case_id`.

## Explicit Non-Closure

This task does not:

- modify backend code, task API wrappers/types, router/menu behavior, task detail/create pages, task special search, task templates, or dashboard data loading.
- add user-name resolution, a user selector, a case selector, or any new API join.
- change task status transitions, export/print behavior, filters, pagination, permissions, or response envelopes.
- close raw-ID display issues in document, annuity, grant fee, commission, expense, case, consulting, billing, or system settings pages.

## Remaining Follow-Up Task IDs

- `AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01`
- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-COMMISSION-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-TASK-LIST-ID-DISPLAY-01.md`
- `frontend/src/modules/tasks/pages/TaskList.vue`
- `frontend/src/modules/dashboard/components/TodoTable.vue`
- `artifacts/AD-FE-TASK-LIST-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-TASK-LIST-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/tasks/pages/TaskList.vue src/modules/dashboard/components/TodoTable.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-TASK-LIST-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-TASK-LIST-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "#\\$\\{row\\.case_id\\}|row\\.case_id\\.slice|prop=\"id\"|row\\.title \\|\\| row\\.id" frontend/src/modules/tasks/pages/TaskList.vue frontend/src/modules/dashboard/components/TodoTable.vue && rg -n "formatCaseDisplay|formatAssigneeDisplay|未命名案件|已分配" frontend/src/modules/tasks/pages/TaskList.vue frontend/src/modules/dashboard/components/TodoTable.vue'
./scripts/evidence_run.sh AD-FE-TASK-LIST-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-TASK-LIST-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-TASK-LIST-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-TASK-LIST-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-TASK-LIST-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-TASK-LIST-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-TASK-LIST-ID-DISPLAY-01/baseline_external_files.txt`
