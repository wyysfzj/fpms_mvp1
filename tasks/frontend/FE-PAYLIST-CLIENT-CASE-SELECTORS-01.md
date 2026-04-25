# FE-PAYLIST-CLIENT-CASE-SELECTORS-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Replace PayList raw client/case-id entry points with existing-backend selectors where the current API contract already supports IDs.

This task closes only:

1. `PayList.vue` list filter uses a customer selector backed by existing `getClients()`.
2. `PayList.vue` historical pay-list creation uses a customer selector backed by existing `getClients()`.
3. `ManualGovPaymentDialog.vue` historical detail entry uses a case selector backed by existing `getCases()`.
4. Existing payload fields remain `client_id` and `case_id`.

## Explicit Non-Closure

Do not:

- add a manual fee-item selector.
- change PayList or GovPayment backend behavior.
- modify `govPayments` API wrappers or types.
- add PayList case filtering if backend query does not already support it.
- modify PayList detail registration handoff.
- change menu/router/permission wiring.
- modify skeleton data or automation handlers.

## Remaining Follow-Up Task IDs

- `PRODUCT-FE-PAYLIST-MANUAL-FEE-ITEM-SELECTOR-CONTRACT-01`
- `PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01`
- `PRODUCT-COMMISSION-BILL-NO-QUERY-CONTRACT-01`

## Allowed Files

- `tasks/frontend/FE-PAYLIST-CLIENT-CASE-SELECTORS-01.md`
- `frontend/src/modules/annuity/pages/PayList.vue`
- `frontend/src/modules/annuity/components/ManualGovPaymentDialog.vue`
- `artifacts/FE-PAYLIST-CLIENT-CASE-SELECTORS-01/**`

## Verification Commands

Run from repo root unless noted:

```bash
./scripts/evidence_run.sh FE-PAYLIST-CLIENT-CASE-SELECTORS-01 red /bin/zsh -lc 'rg -n "请选择客户|请选择案件|clientOptions|caseOptions|formatClientOption|formatCaseOption" frontend/src/modules/annuity/pages/PayList.vue frontend/src/modules/annuity/components/ManualGovPaymentDialog.vue'
./scripts/evidence_run.sh FE-PAYLIST-CLIENT-CASE-SELECTORS-01 lint /bin/zsh -lc 'cd frontend && npm run typecheck'
./scripts/evidence_run.sh FE-PAYLIST-CLIENT-CASE-SELECTORS-01 eslint /bin/zsh -lc 'cd frontend && npx eslint src/modules/annuity/pages/PayList.vue src/modules/annuity/components/ManualGovPaymentDialog.vue --max-warnings 0'
./scripts/evidence_run.sh FE-PAYLIST-CLIENT-CASE-SELECTORS-01 test /bin/zsh -lc 'cd frontend && npm run build'
./scripts/evidence_run.sh FE-PAYLIST-CLIENT-CASE-SELECTORS-01 ux_check /bin/zsh -lc 'rg -n "请选择客户|请选择案件|clientOptions|caseOptions|formatClientOption|formatCaseOption|费用项编号（可选）" frontend/src/modules/annuity/pages/PayList.vue frontend/src/modules/annuity/components/ManualGovPaymentDialog.vue'
./scripts/evidence_run.sh FE-PAYLIST-CLIENT-CASE-SELECTORS-01 task_gate ./scripts/task_validate.sh FE-PAYLIST-CLIENT-CASE-SELECTORS-01
```

## Evidence Path

- `artifacts/FE-PAYLIST-CLIENT-CASE-SELECTORS-01/results.jsonl`
- `artifacts/FE-PAYLIST-CLIENT-CASE-SELECTORS-01/summary.md`
- `artifacts/FE-PAYLIST-CLIENT-CASE-SELECTORS-01/git/diff.patch`
- `artifacts/FE-PAYLIST-CLIENT-CASE-SELECTORS-01/baseline_allowlist.diff`
- `artifacts/FE-PAYLIST-CLIENT-CASE-SELECTORS-01/baseline_external_files.txt`
