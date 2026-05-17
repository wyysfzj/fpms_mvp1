# AD-FE-CASE-BATCH-FILING-FILTER-ID-LABELS-01 - case batch filing filter ID wording cleanup

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

Normalize visible internal-ID wording in the case batch filing primary-agent filter.

This closes only:

1. `CaseBatchFiling.vue` no longer shows `代理人ID` in the primary-agent filter placeholder.
2. Internal `primary_agent_id` filter field remains unchanged for API compatibility.

## Explicit Non-Closure

This task does not:

- modify backend code, case API wrappers/types, route params, permissions, response envelopes, or batch filing behavior.
- add agent selector APIs or any new readable agent filter contract.
- change candidate queries, batch actions, client selector values, table columns, or validation.
- close case list, report filters, create/edit forms, or other pages.

## Remaining Follow-Up Task IDs

- `AD-FE-REPORT-FILTER-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-CASE-BATCH-FILING-FILTER-ID-LABELS-01.md`
- `frontend/src/modules/cases/pages/CaseBatchFiling.vue`
- `artifacts/AD-FE-CASE-BATCH-FILING-FILTER-ID-LABELS-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-CASE-BATCH-FILING-FILTER-ID-LABELS-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/cases/pages/CaseBatchFiling.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-CASE-BATCH-FILING-FILTER-ID-LABELS-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-CASE-BATCH-FILING-FILTER-ID-LABELS-01 ux_check /bin/zsh -lc '! rg -n "代理人ID" frontend/src/modules/cases/pages/CaseBatchFiling.vue && rg -n "placeholder=\"请输入代理人\"" frontend/src/modules/cases/pages/CaseBatchFiling.vue'
./scripts/evidence_run.sh AD-FE-CASE-BATCH-FILING-FILTER-ID-LABELS-01 task_gate ./scripts/task_validate.sh AD-FE-CASE-BATCH-FILING-FILTER-ID-LABELS-01
```

## Evidence Path

- `artifacts/AD-FE-CASE-BATCH-FILING-FILTER-ID-LABELS-01/results.jsonl`
- `artifacts/AD-FE-CASE-BATCH-FILING-FILTER-ID-LABELS-01/summary.md`
- `artifacts/AD-FE-CASE-BATCH-FILING-FILTER-ID-LABELS-01/git/diff.patch`
- `artifacts/AD-FE-CASE-BATCH-FILING-FILTER-ID-LABELS-01/baseline_allowlist.diff`
- `artifacts/AD-FE-CASE-BATCH-FILING-FILTER-ID-LABELS-01/baseline_external_files.txt`
