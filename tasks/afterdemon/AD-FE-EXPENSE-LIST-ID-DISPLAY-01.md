# AD-FE-EXPENSE-LIST-ID-DISPLAY-01 — expense list visible ID cleanup

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

Remove visible raw case/worker/department internal ID displays and raw enum fallbacks from the expense list page.

This closes only:

1. `ExpenseList.vue` no longer renders `row.case_id`, `row.worker_id`, or `row.department_id` as table text.
2. `ExpenseList.vue` uses Chinese placeholders for missing or internally identified case/project, worker, and department values.
3. `ExpenseList.vue` unknown category/status fallback text is Chinese instead of the raw enum value.

## Explicit Non-Closure

This task does not:

- modify backend code, expense API wrappers/types, route params, create/report pages, permissions, response envelopes, or expense fetch behavior.
- add case/user/department name resolution or any new API join.
- change filters, query parameters, date/amount formatting, pagination, create navigation, export, or print behavior.
- close raw-ID display issues outside `ExpenseList.vue`.

## Remaining Follow-Up Task IDs

- `PRODUCT-FE-CASE-USER-DEPARTMENT-SELECTOR-CONTRACT-01`
- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-COMMISSION-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-CONSULTING-EXPENSE-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-EXPENSE-LIST-ID-DISPLAY-01.md`
- `frontend/src/modules/expenses/pages/ExpenseList.vue`
- `artifacts/AD-FE-EXPENSE-LIST-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-EXPENSE-LIST-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/expenses/pages/ExpenseList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-EXPENSE-LIST-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-EXPENSE-LIST-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "\\{\\{ row\\.(case_id|worker_id|department_id) \\|\\| '—' \\}\\}|return CATEGORY_TEXT\\[category\\] \\|\\| category|return STATUS_TEXT\\[status\\] \\|\\| status" frontend/src/modules/expenses/pages/ExpenseList.vue && rg -n "formatCaseDisplay|formatWorkerDisplay|formatDepartmentDisplay|未知类别|未知状态" frontend/src/modules/expenses/pages/ExpenseList.vue'
./scripts/evidence_run.sh AD-FE-EXPENSE-LIST-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-EXPENSE-LIST-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-EXPENSE-LIST-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-EXPENSE-LIST-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-EXPENSE-LIST-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-EXPENSE-LIST-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-EXPENSE-LIST-ID-DISPLAY-01/baseline_external_files.txt`
