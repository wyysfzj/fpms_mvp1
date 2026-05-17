# AD-FE-DOCUMENT-LIST-CASE-DISPLAY-01 — document list case display fallback cleanup

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Task Plan Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Replace the `DocumentList.vue` case column fallback that currently renders raw `case_id` as `#<case_id>` with a Simplified Chinese business placeholder when `case_no` is unavailable.

This closes only:

1. The visible case cell in the document list no longer displays raw internal case UUIDs.
2. The case link still uses the existing internal `case_id` route value.
3. The no-case state uses the existing empty marker.

## Explicit Non-Closure

This task does not:

- modify backend code, document API wrappers/types, router/menu behavior, document create/edit/wizard/dispatch/envelope flows, or response envelopes.
- add a new case selector, case lookup API call, or client-side join.
- change document type, template, reply-state, attachment, or date filtering behavior.
- close raw-ID display issues in task, dashboard, annuity, grant fee, commission, expense, case, consulting, or billing pages.

## Remaining Follow-Up Task IDs

- `AD-FE-TASK-LIST-ID-DISPLAY-01`
- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-COMMISSION-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-DOCUMENT-LIST-CASE-DISPLAY-01.md`
- `frontend/src/modules/documents/pages/DocumentList.vue`
- `artifacts/AD-FE-DOCUMENT-LIST-CASE-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-DOCUMENT-LIST-CASE-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/documents/pages/DocumentList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-DOCUMENT-LIST-CASE-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-DOCUMENT-LIST-CASE-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "#\\$\\{row\\.case_id\\}" frontend/src/modules/documents/pages/DocumentList.vue && rg -n "formatCaseDisplay|未命名案件" frontend/src/modules/documents/pages/DocumentList.vue'
./scripts/evidence_run.sh AD-FE-DOCUMENT-LIST-CASE-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-DOCUMENT-LIST-CASE-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-DOCUMENT-LIST-CASE-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-DOCUMENT-LIST-CASE-DISPLAY-01/summary.md`
- `artifacts/AD-FE-DOCUMENT-LIST-CASE-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-DOCUMENT-LIST-CASE-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-DOCUMENT-LIST-CASE-DISPLAY-01/baseline_external_files.txt`
