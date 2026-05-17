# AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01 — special task search visible ID cleanup

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

Remove visible raw task/case internal ID displays and raw task-type enum code displays from the special task search result rows.

This closes only:

1. `TaskSpecialSearch.vue` no longer renders a user-visible `任务ID` column.
2. `TaskSpecialSearch.vue` task detail navigation keeps using `task_id` internally, but the visible task link text is the task title or a Chinese business fallback.
3. `TaskSpecialSearch.vue` case navigation keeps using `case_id` internally, but the visible case link text is `case_no` or a Chinese business fallback.
4. `TaskSpecialSearch.vue` no longer renders `case_id` as secondary visible text under the case column.
5. `TaskSpecialSearch.vue` task type result cells display Chinese labels instead of raw enum codes such as `APPLY_FEE_LIMIT`.

## Explicit Non-Closure

This task does not:

- modify backend code, task API wrappers/types, router/menu behavior, task list/detail/create pages, dashboard pages, export/print payloads, or response envelopes.
- add task-number, user-name, or case-name resolution beyond fields already returned to this page.
- change special search filters, pagination, status transitions, export behavior, print behavior, permissions, or request parameters.
- close raw-ID display issues in today reminders, task detail, document, annuity, grant fee, commission, expense, case, consulting, billing, or system settings pages.

## Remaining Follow-Up Task IDs

- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-COMMISSION-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-CONSULTING-EXPENSE-ID-DISPLAY-01`
- `AD-FE-SYSTEM-TEMPLATE-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01.md`
- `frontend/src/modules/tasks/pages/TaskSpecialSearch.vue`
- `artifacts/AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/tasks/pages/TaskSpecialSearch.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "label=\"任务ID\"|\\{\\{ row\\.task_id \\}\\}|\\{\\{ row\\.case_id \\}\\}|\\{\\{ row\\.task_code \\}\\}" frontend/src/modules/tasks/pages/TaskSpecialSearch.vue && rg -n "formatTaskTitle|formatCaseDisplay|未命名任务|未命名案件|未知任务类型" frontend/src/modules/tasks/pages/TaskSpecialSearch.vue'
./scripts/evidence_run.sh AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01/baseline_external_files.txt`
