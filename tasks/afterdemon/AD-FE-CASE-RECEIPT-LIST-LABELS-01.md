# AD-FE-CASE-RECEIPT-LIST-LABELS-01 — case receipt list client filter and case terminology cleanup

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

Clean up demo-visible client and case terminology in the case receipt list page.

This closes only:

1. Replace the visible `客户ID` free-text filter with an existing-backend client selector that stores the existing `client_id` query value internally.
2. Replace `案卷号` visible labels/placeholders in this page with the current UI term `案号`.
3. Preserve existing case receipt list query behavior and table behavior.

## Explicit Non-Closure

This task does not:

- modify backend code, billing API wrappers/types, `CaseReceiptDialog.vue`, payment/offset pages, bill pages, router/menu behavior, permissions, or response envelopes.
- add a case selector or change the `case_no` filter contract.
- change receipt create/edit behavior or receipt row data.
- close raw-ID or terminology issues outside `CaseReceiptList.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-ANNUITY-GRANT-ID-DISPLAY-01`
- `AD-FE-COMMISSION-ID-DISPLAY-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-TASK-SPECIAL-SEARCH-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-CASE-RECEIPT-LIST-LABELS-01.md`
- `frontend/src/modules/billing/pages/CaseReceiptList.vue`
- `artifacts/AD-FE-CASE-RECEIPT-LIST-LABELS-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-CASE-RECEIPT-LIST-LABELS-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/billing/pages/CaseReceiptList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-CASE-RECEIPT-LIST-LABELS-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-CASE-RECEIPT-LIST-LABELS-01 ux_check /bin/zsh -lc '! rg -n "客户ID|案卷号" frontend/src/modules/billing/pages/CaseReceiptList.vue && rg -n "请选择客户|案号|clientOptions|formatClientOption" frontend/src/modules/billing/pages/CaseReceiptList.vue'
./scripts/evidence_run.sh AD-FE-CASE-RECEIPT-LIST-LABELS-01 task_gate ./scripts/task_validate.sh AD-FE-CASE-RECEIPT-LIST-LABELS-01
```

## Evidence Path

- `artifacts/AD-FE-CASE-RECEIPT-LIST-LABELS-01/results.jsonl`
- `artifacts/AD-FE-CASE-RECEIPT-LIST-LABELS-01/summary.md`
- `artifacts/AD-FE-CASE-RECEIPT-LIST-LABELS-01/git/diff.patch`
- `artifacts/AD-FE-CASE-RECEIPT-LIST-LABELS-01/baseline_allowlist.diff`
- `artifacts/AD-FE-CASE-RECEIPT-LIST-LABELS-01/baseline_external_files.txt`
