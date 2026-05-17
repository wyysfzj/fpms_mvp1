# AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01 — annuity pay list visible ID cleanup

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

Remove visible raw pay-list/client internal ID fallback text from the annuity pay list page.

This closes only:

1. `PayList.vue` table pay-list display uses `pay_list_no` or a Chinese fallback instead of `#<id>`.
2. `PayList.vue` table client display uses client name or a Chinese fallback instead of `client_id`.
3. `PayList.vue` client option labels do not fallback to client internal IDs.
4. `PayList.vue` export filename and historical-create success message do not echo internal pay-list IDs.
5. `PayList.vue` unknown pay-list status fallback text is Chinese instead of raw status value.

## Explicit Non-Closure

This task does not:

- modify backend code, gov payment API wrappers/types, pay-list detail page, route params, permissions, response envelopes, or pay-list fetch/create/export behavior.
- add client-name resolution beyond existing `getClients` options and fields already returned to this page.
- change filters, historical form behavior, validation, pagination, detail navigation, export payloads, date/money formatting, or print behavior.
- close raw-ID display issues outside `PayList.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01`
- `AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01.md`
- `frontend/src/modules/annuity/pages/PayList.vue`
- `artifacts/AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/annuity/pages/PayList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "#\\$\\{row\\.id\\}|row\\.client_name \\|\\| row\\.client_id|客户 \\$\\{client\\.id\\}|清单-\\$\\{row\\.id\\}|#\\$\\{created\\.id\\}|return status \\|\\| '未知'" frontend/src/modules/annuity/pages/PayList.vue && rg -n "formatPayListNo|formatClientDisplay|未生成清单编号|未命名客户|未知状态" frontend/src/modules/annuity/pages/PayList.vue'
./scripts/evidence_run.sh AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01/baseline_external_files.txt`
