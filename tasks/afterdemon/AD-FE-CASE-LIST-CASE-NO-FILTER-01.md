# AD-FE-CASE-LIST-CASE-NO-FILTER-01 - case list case-number filter visibility

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

Make the case list page visibly searchable by business case number using the existing backend-supported `case_no` query parameter.

This closes only:

1. `CaseList.vue` exposes an `案号` filter in the page filter panel.
2. Searching by `DEMO-RUI-20260510A-001` through that filter returns the matching case row.
3. Reset clears the new case-number filter together with the other page filters.

## Explicit Non-Closure

This task does not:

- modify backend code, case API wrappers/types, router/menu behavior, permissions, response envelopes, or global header search behavior.
- add customer/title fuzzy search, command-palette search, sorting, export, pagination changes, or new cross-page search state.
- change case detail navigation, case creation/editing, workflow status display, or table columns.
- close case filter display issues outside `CaseList.vue`.

## Remaining Follow-Up Task IDs

- `PRODUCT-FE-GLOBAL-SEARCH-CONTRACT-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-CASE-LIST-CASE-NO-FILTER-01.md`
- `frontend/src/modules/cases/pages/CaseList.vue`
- `artifacts/AD-FE-CASE-LIST-CASE-NO-FILTER-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-CASE-LIST-CASE-NO-FILTER-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/cases/pages/CaseList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-CASE-LIST-CASE-NO-FILTER-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-CASE-LIST-CASE-NO-FILTER-01 ux_check /bin/zsh -lc 'rg -n "label=\"案号\"|placeholder=\"请输入案号\"|filters\\.case_no|case_no:" frontend/src/modules/cases/pages/CaseList.vue'
./scripts/evidence_run.sh AD-FE-CASE-LIST-CASE-NO-FILTER-01 task_gate ./scripts/task_validate.sh AD-FE-CASE-LIST-CASE-NO-FILTER-01
```

## Evidence Path

- `artifacts/AD-FE-CASE-LIST-CASE-NO-FILTER-01/results.jsonl`
- `artifacts/AD-FE-CASE-LIST-CASE-NO-FILTER-01/summary.md`
- `artifacts/AD-FE-CASE-LIST-CASE-NO-FILTER-01/git/diff.patch`
- `artifacts/AD-FE-CASE-LIST-CASE-NO-FILTER-01/baseline_allowlist.diff`
- `artifacts/AD-FE-CASE-LIST-CASE-NO-FILTER-01/baseline_external_files.txt`
