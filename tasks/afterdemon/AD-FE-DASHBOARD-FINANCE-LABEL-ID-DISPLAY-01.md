# AD-FE-DASHBOARD-FINANCE-LABEL-ID-DISPLAY-01 — dashboard finance label ID cleanup

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

Remove visible short internal ID fallback labels from dashboard finance feed data.

This closes only:

1. `dashboard.api.ts` payment finance items no longer build labels from `p.id.slice(0, 8)`.
2. `dashboard.api.ts` payment finance items use `reference` or a Chinese business fallback.
3. `dashboard.api.ts` bill finance items use `bill_no` or a Chinese business fallback.

## Explicit Non-Closure

This task does not:

- modify backend code, dashboard components, billing API wrappers/types, router/menu behavior, permissions, or response envelopes.
- change dashboard item IDs used internally for Vue rendering or navigation.
- change finance feed ordering, filtering, amounts, currency formatting, status badges, dates, pagination, export, or print behavior.
- close raw-ID display issues outside `frontend/src/modules/dashboard/dashboard.api.ts`.

## Remaining Follow-Up Task IDs

- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-COMMISSION-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-CONSULTING-EXPENSE-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-DASHBOARD-FINANCE-LABEL-ID-DISPLAY-01.md`
- `frontend/src/modules/dashboard/dashboard.api.ts`
- `artifacts/AD-FE-DASHBOARD-FINANCE-LABEL-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-DASHBOARD-FINANCE-LABEL-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/dashboard/dashboard.api.ts --max-warnings 0'
./scripts/evidence_run.sh AD-FE-DASHBOARD-FINANCE-LABEL-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-DASHBOARD-FINANCE-LABEL-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "slice\\(0,\\s*8\\)|回款#" frontend/src/modules/dashboard/dashboard.api.ts && rg -n "未生成回款编号|未生成账单号" frontend/src/modules/dashboard/dashboard.api.ts'
./scripts/evidence_run.sh AD-FE-DASHBOARD-FINANCE-LABEL-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-DASHBOARD-FINANCE-LABEL-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-DASHBOARD-FINANCE-LABEL-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-DASHBOARD-FINANCE-LABEL-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-DASHBOARD-FINANCE-LABEL-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-DASHBOARD-FINANCE-LABEL-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-DASHBOARD-FINANCE-LABEL-ID-DISPLAY-01/baseline_external_files.txt`
