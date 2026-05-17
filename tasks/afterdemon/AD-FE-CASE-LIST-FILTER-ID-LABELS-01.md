# AD-FE-CASE-LIST-FILTER-ID-LABELS-01 - case list filter ID wording cleanup

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

Normalize visible internal-ID wording in the case list filters.

This closes only:

1. `CaseList.vue` no longer shows `代理人ID` as a visible placeholder.
2. `CaseList.vue` no longer shows `申请人ID` as a visible filter label or placeholder.
3. Internal `agent_id` and `applicant_id` filter fields remain unchanged for API compatibility.

## Explicit Non-Closure

This task does not:

- modify backend code, case API wrappers/types, route params, permissions, response envelopes, or list fetch behavior.
- add agent/applicant selector APIs or any new readable filter contract.
- change table columns, filters outside the two ID wording fields, pagination, navigation, or actions.
- close case batch filing, report filters, create/edit forms, or other pages.

## Remaining Follow-Up Task IDs

- `AD-FE-CASE-BATCH-FILING-FILTER-ID-LABELS-01`
- `AD-FE-REPORT-FILTER-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-CASE-LIST-FILTER-ID-LABELS-01.md`
- `frontend/src/modules/cases/pages/CaseList.vue`
- `artifacts/AD-FE-CASE-LIST-FILTER-ID-LABELS-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-CASE-LIST-FILTER-ID-LABELS-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/cases/pages/CaseList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-CASE-LIST-FILTER-ID-LABELS-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-CASE-LIST-FILTER-ID-LABELS-01 ux_check /bin/zsh -lc '! rg -n "代理人ID|申请人ID" frontend/src/modules/cases/pages/CaseList.vue && rg -n "label=\"申请人\"|placeholder=\"请输入代理人\"|placeholder=\"请输入申请人\"" frontend/src/modules/cases/pages/CaseList.vue'
./scripts/evidence_run.sh AD-FE-CASE-LIST-FILTER-ID-LABELS-01 task_gate ./scripts/task_validate.sh AD-FE-CASE-LIST-FILTER-ID-LABELS-01
```

## Evidence Path

- `artifacts/AD-FE-CASE-LIST-FILTER-ID-LABELS-01/results.jsonl`
- `artifacts/AD-FE-CASE-LIST-FILTER-ID-LABELS-01/summary.md`
- `artifacts/AD-FE-CASE-LIST-FILTER-ID-LABELS-01/git/diff.patch`
- `artifacts/AD-FE-CASE-LIST-FILTER-ID-LABELS-01/baseline_allowlist.diff`
- `artifacts/AD-FE-CASE-LIST-FILTER-ID-LABELS-01/baseline_external_files.txt`
