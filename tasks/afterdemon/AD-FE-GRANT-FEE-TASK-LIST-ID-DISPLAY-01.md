# AD-FE-GRANT-FEE-TASK-LIST-ID-DISPLAY-01 — grant fee task list visible ID cleanup

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

Remove visible raw task/case/bill internal ID displays and raw enum fallbacks from the grant fee task list page.

This closes only:

1. `GrantFeeTaskList.vue` no longer renders the internal `task_id` column.
2. `GrantFeeTaskList.vue` case links use `case_no` or a Chinese fallback instead of `case_id`.
3. `GrantFeeTaskList.vue` bill links use `linked_bill_no` or a Chinese fallback instead of `linked_bill_id`.
4. `GrantFeeTaskList.vue` unknown status/client-instruction fallback text is Chinese instead of the raw enum value.

## Explicit Non-Closure

This task does not:

- modify backend code, grant fee API wrappers/types, route params, permissions, response envelopes, or task action payloads.
- add case-name, bill-number, or task-number resolution beyond fields already returned to this page.
- change filters, selection, batch actions, notice generation, draft generation, mark-done behavior, amount/date formatting, pagination, export, or print behavior.
- close raw-ID display issues outside `GrantFeeTaskList.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-ANNUITY-TASK-LIST-ID-DISPLAY-01`
- `AD-FE-ANNUITY-PAY-LIST-ID-DISPLAY-01`
- `AD-FE-ANNUITY-PAY-LIST-DETAIL-ID-DISPLAY-01`
- `AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-GRANT-FEE-TASK-LIST-ID-DISPLAY-01.md`
- `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `artifacts/AD-FE-GRANT-FEE-TASK-LIST-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-GRANT-FEE-TASK-LIST-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/grantFees/pages/GrantFeeTaskList.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-GRANT-FEE-TASK-LIST-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-GRANT-FEE-TASK-LIST-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "prop=\"task_id\" label=\"任务编号\"|row\\.case_no \\|\\| row\\.case_id|row\\.linked_bill_no \\|\\| row\\.linked_bill_id|return labels\\[status\\] \\|\\| status|return labels\\[input\\] \\|\\| input" frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue && rg -n "formatCaseDisplay|formatBillDisplay|未知状态|未知指示|未命名案件|未生成账单号" frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue'
./scripts/evidence_run.sh AD-FE-GRANT-FEE-TASK-LIST-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-GRANT-FEE-TASK-LIST-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-GRANT-FEE-TASK-LIST-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-GRANT-FEE-TASK-LIST-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-GRANT-FEE-TASK-LIST-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-GRANT-FEE-TASK-LIST-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-GRANT-FEE-TASK-LIST-ID-DISPLAY-01/baseline_external_files.txt`
