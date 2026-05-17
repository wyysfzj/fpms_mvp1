# AD-FE-CASE-REPORT-FILTER-ID-LABELS-01 - case report filter ID wording cleanup

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

Normalize visible internal-ID wording in the case report agent filter.

This closes only:

1. `CaseReport.vue` no longer shows `代理人ID` in the agent filter placeholder.
2. Internal `agent_id` filter field remains unchanged for API compatibility.

## Explicit Non-Closure

This task does not:

- modify backend code, report API wrappers/types, route params, permissions, response envelopes, or report fetch behavior.
- add agent selector APIs or any new readable agent filter contract.
- change report calculations, status filters, date filters, result tables, or other report pages.

## Remaining Follow-Up Task IDs

- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-CASE-REPORT-FILTER-ID-LABELS-01.md`
- `frontend/src/modules/reports/pages/CaseReport.vue`
- `artifacts/AD-FE-CASE-REPORT-FILTER-ID-LABELS-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-CASE-REPORT-FILTER-ID-LABELS-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/reports/pages/CaseReport.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-CASE-REPORT-FILTER-ID-LABELS-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-CASE-REPORT-FILTER-ID-LABELS-01 ux_check /bin/zsh -lc '! rg -n "代理人ID" frontend/src/modules/reports/pages/CaseReport.vue && rg -n "placeholder=\"请输入代理人\"" frontend/src/modules/reports/pages/CaseReport.vue'
./scripts/evidence_run.sh AD-FE-CASE-REPORT-FILTER-ID-LABELS-01 task_gate ./scripts/task_validate.sh AD-FE-CASE-REPORT-FILTER-ID-LABELS-01
```

## Evidence Path

- `artifacts/AD-FE-CASE-REPORT-FILTER-ID-LABELS-01/results.jsonl`
- `artifacts/AD-FE-CASE-REPORT-FILTER-ID-LABELS-01/summary.md`
- `artifacts/AD-FE-CASE-REPORT-FILTER-ID-LABELS-01/git/diff.patch`
- `artifacts/AD-FE-CASE-REPORT-FILTER-ID-LABELS-01/baseline_allowlist.diff`
- `artifacts/AD-FE-CASE-REPORT-FILTER-ID-LABELS-01/baseline_external_files.txt`
