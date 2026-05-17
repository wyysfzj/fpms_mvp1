# AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01 — annuity pay list detail visible ID cleanup

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

Remove visible raw pay-list/client/fee-item/case internal ID displays from the annuity pay list detail page.

This closes only:

1. `PayListDetail.vue` pay-list display uses `pay_list_no` or a Chinese fallback instead of `#<id>`.
2. `PayListDetail.vue` client display uses a Chinese association placeholder instead of `client_id`.
3. `PayListDetail.vue` gov payment rows use Chinese placeholders instead of `fee_item_id` and `case_id`.
4. `PayListDetail.vue` export filename does not fallback to internal pay-list IDs.
5. `PayListDetail.vue` unknown pay-list/gov-payment status fallback text is Chinese instead of raw status value.

## Explicit Non-Closure

This task does not:

- modify backend code, gov payment API wrappers/types, pay-list list page, route params, permissions, response envelopes, or detail/export/mark-paid behavior.
- add client-name, case-name, pay-list-number, or fee-item-number resolution beyond fields already returned to this page.
- change manual row behavior, payment registration query params, validation, date/money formatting, export payloads, or print behavior.
- close raw-ID display issues outside `PayListDetail.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01.md`
- `frontend/src/modules/annuity/pages/PayListDetail.vue`
- `artifacts/AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/annuity/pages/PayListDetail.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "#\\$\\{(detail\\.pay_list|payList\\.value|target)\\.id\\}|\\{\\{ detail\\.pay_list\\.client_id \\}\\}|row\\.fee_item_id \\|\\||prop=\"case_id\" label=\"案件编号\"|清单-\\$\\{target\\.id\\}|return status \\|\\| '未知'" frontend/src/modules/annuity/pages/PayListDetail.vue && rg -n "formatPayListNo|formatClientDisplay|formatFeeItemDisplay|formatCaseDisplay|未生成清单编号|已关联客户|已关联费用项|未知状态" frontend/src/modules/annuity/pages/PayListDetail.vue'
./scripts/evidence_run.sh AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01/baseline_external_files.txt`
