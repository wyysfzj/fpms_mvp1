# AD-FE-CLIENT-LIST-ID-DISPLAY-01 - client list visible ID cleanup

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

Remove visible raw internal client ID displays from the client list page.

This closes only:

1. `ClientList.vue` no longer renders the internal `id` column as a visible customer number.
2. `ClientList.vue` uses `client_code` as the visible customer number when available.
3. `ClientList.vue` no longer falls back to `row.id` in the row action aria-label.

## Explicit Non-Closure

This task does not:

- modify backend code, client API wrappers/types, route params, permissions, response envelopes, or list fetch behavior.
- add customer code generation or any new readable customer identifier contract.
- change client detail/edit navigation, pagination, sorting, creation, or any client detail/address/contact pages.
- close raw-ID display issues outside `ClientList.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-CLIENT-DETAIL-ID-DISPLAY-01`
- `AD-FE-CASE-FORM-ID-LABELS-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-CLIENT-LIST-ID-DISPLAY-01.md`
- `frontend/src/modules/clients/pages/ClientList.vue`
- `artifacts/AD-FE-CLIENT-LIST-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-CLIENT-LIST-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/clients/pages/ClientList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-CLIENT-LIST-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-CLIENT-LIST-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "prop=\"id\" label=\"编号\"|row\\.name \\|\\| row\\.id|\\{\\{ row\\.id \\}\\}" frontend/src/modules/clients/pages/ClientList.vue && rg -n "client_code|formatClientDisplay|未命名客户|未设置" frontend/src/modules/clients/pages/ClientList.vue'
./scripts/evidence_run.sh AD-FE-CLIENT-LIST-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-CLIENT-LIST-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-CLIENT-LIST-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-CLIENT-LIST-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-CLIENT-LIST-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-CLIENT-LIST-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-CLIENT-LIST-ID-DISPLAY-01/baseline_external_files.txt`
