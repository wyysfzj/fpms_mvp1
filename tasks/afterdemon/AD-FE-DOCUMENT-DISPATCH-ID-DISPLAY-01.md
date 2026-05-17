# AD-FE-DOCUMENT-DISPATCH-ID-DISPLAY-01 — document dispatch visible ID cleanup

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

Remove visible raw dispatch/client internal ID displays from the document dispatch page.

This closes only:

1. `DocumentDispatch.vue` no longer renders `currentDispatchId` as the current dispatch display label.
2. `DocumentDispatch.vue` dispatch detail summary uses `client_name` or a Chinese business fallback instead of `client_id`.
3. `DocumentDispatch.vue` dispatch detail metadata no longer renders `dispatchDetail.id`.

## Explicit Non-Closure

This task does not:

- modify backend code, document API wrappers/types, route params, permissions, response envelopes, or dispatch creation/loading behavior.
- change selected document IDs used internally for batch mailing/dispatch requests.
- change filters, candidate loading, client/template selectors, registration behavior, dispatch reload behavior, table columns, pagination, export, or print behavior.
- close raw-ID display issues outside `DocumentDispatch.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-COMMISSION-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-CONSULTING-EXPENSE-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-DOCUMENT-DISPATCH-ID-DISPLAY-01.md`
- `frontend/src/modules/documents/pages/DocumentDispatch.vue`
- `artifacts/AD-FE-DOCUMENT-DISPATCH-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-DOCUMENT-DISPATCH-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/documents/pages/DocumentDispatch.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-DOCUMENT-DISPATCH-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-DOCUMENT-DISPATCH-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "当前交接单编号：\\{\\{ currentDispatchId \\}\\}|dispatchDetail\\.client_name \\|\\| dispatchDetail\\.client_id|交接单编号：\\{\\{ dispatchDetail\\.id \\}\\}" frontend/src/modules/documents/pages/DocumentDispatch.vue && rg -n "formatDispatchClient|交接单已生成|未命名客户" frontend/src/modules/documents/pages/DocumentDispatch.vue'
./scripts/evidence_run.sh AD-FE-DOCUMENT-DISPATCH-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-DOCUMENT-DISPATCH-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-DOCUMENT-DISPATCH-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-DOCUMENT-DISPATCH-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-DOCUMENT-DISPATCH-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-DOCUMENT-DISPATCH-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-DOCUMENT-DISPATCH-ID-DISPLAY-01/baseline_external_files.txt`
