# AD-FE-DUNNING-LIST-ID-DISPLAY-01 - dunning list visible ID cleanup

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

Remove visible raw internal batch/client ID displays from the dunning list page.

This closes only:

1. `DunningList.vue` no longer builds visible fallback dunning numbers from `row.id`.
2. `DunningList.vue` no longer renders `client_id` as the visible customer column.
3. `DunningList.vue` uses `dunning_no` when available and otherwise Chinese business placeholders.
4. The empty-state visual text on this page is Chinese rather than the technical `DN` abbreviation.

## Explicit Non-Closure

This task does not:

- modify backend code, collection API wrappers/types, route params, permissions, response envelopes, or list fetch behavior.
- add customer-name resolution or any new API join.
- change list filters, pagination, detail navigation, status mapping, amount/date formatting, create flow, or row click behavior.
- close raw-ID display issues outside `DunningList.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-CASE-FORM-ID-LABELS-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-DUNNING-LIST-ID-DISPLAY-01.md`
- `frontend/src/modules/collections/pages/DunningList.vue`
- `artifacts/AD-FE-DUNNING-LIST-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-DUNNING-LIST-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/collections/pages/DunningList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-DUNNING-LIST-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-DUNNING-LIST-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "DN-\\$\\{row\\.id\\}|prop=\"client_id\" label=\"客户编号\"|icon=\"DN\"|\\{\\{ row\\.client_id \\}\\}" frontend/src/modules/collections/pages/DunningList.vue && rg -n "formatDunningNo|formatDunningClient|未生成催款单号|已关联客户|icon=\"款\"" frontend/src/modules/collections/pages/DunningList.vue'
./scripts/evidence_run.sh AD-FE-DUNNING-LIST-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-DUNNING-LIST-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-DUNNING-LIST-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-DUNNING-LIST-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-DUNNING-LIST-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-DUNNING-LIST-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-DUNNING-LIST-ID-DISPLAY-01/baseline_external_files.txt`
