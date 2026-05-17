# AD-FE-DUNNING-DETAIL-ID-DISPLAY-01 — dunning detail visible ID cleanup

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

Remove visible raw dunning batch/client internal ID displays from the dunning detail page.

This closes only:

1. `DunningDetail.vue` no longer builds fallback display text from `dunningItem.id`.
2. `DunningDetail.vue` no longer renders `dunningItem.id` as a batch number.
3. `DunningDetail.vue` no longer renders `dunningItem.client_id` as a customer number.
4. `DunningDetail.vue` uses `dunning_no` or Chinese business placeholders for visible batch/customer identity.

## Explicit Non-Closure

This task does not:

- modify backend code, collection API wrappers/types, route params, permissions, response envelopes, or dunning fetch behavior.
- add customer-name resolution or any new API join.
- change status mapping, amount/date formatting, list navigation, detail lines, filters, pagination, export, or print behavior.
- close raw-ID display issues outside `DunningDetail.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-COMMISSION-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-CONSULTING-EXPENSE-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-DUNNING-DETAIL-ID-DISPLAY-01.md`
- `frontend/src/modules/collections/pages/DunningDetail.vue`
- `artifacts/AD-FE-DUNNING-DETAIL-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-DUNNING-DETAIL-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/collections/pages/DunningDetail.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-DUNNING-DETAIL-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-DUNNING-DETAIL-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "DN-\\$\\{dunningItem\\.id\\}|\\{\\{ dunningItem\\.id \\}\\}|\\{\\{ dunningItem\\.client_id \\}\\}" frontend/src/modules/collections/pages/DunningDetail.vue && rg -n "formatDunningNo|formatDunningClient|未生成催款单号|已关联客户" frontend/src/modules/collections/pages/DunningDetail.vue'
./scripts/evidence_run.sh AD-FE-DUNNING-DETAIL-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-DUNNING-DETAIL-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-DUNNING-DETAIL-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-DUNNING-DETAIL-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-DUNNING-DETAIL-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-DUNNING-DETAIL-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-DUNNING-DETAIL-ID-DISPLAY-01/baseline_external_files.txt`
