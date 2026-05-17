# AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01 — gov payment registration visible ID cleanup

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

Remove visible raw pay-list, fee-item, gov-payment, and client internal ID displays from the official payment registration page.

This closes only:

1. `GovPaymentCreate.vue` disabled context fields show Chinese selection states instead of raw `pay_list_id` and `fee_item_id`.
2. `GovPaymentCreate.vue` registration results no longer render `result.gov_payment.id`, `result.gov_payment.fee_item_id`, `result.pay_list.id`, or `result.pay_list.client_id`.
3. `GovPaymentCreate.vue` status fallback text is Chinese instead of raw status values.
4. `GovPaymentCreate.vue` visible labels/messages no longer frame internal context as user-facing IDs.

## Explicit Non-Closure

This task does not:

- modify backend code, gov payment API wrappers/types, route params, permissions, response envelopes, or registration payload contracts.
- add pay-list-number, fee-item-number, or client-name resolution beyond fields already returned to this page.
- change validation rules, route-context parsing, submit behavior, field-error mapping, money formatting, navigation, export, or print behavior.
- close raw-ID display issues outside `GovPaymentCreate.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01.md`
- `frontend/src/modules/annuity/pages/GovPaymentCreate.vue`
- `artifacts/AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/annuity/pages/GovPaymentCreate.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "缴费记录编号|费用项编号|客户编号|#\\$\\{result\\.pay_list\\.id\\}|\\{\\{ result\\.gov_payment\\.(id|fee_item_id) \\}\\}|\\{\\{ result\\.pay_list\\.client_id \\}\\}|return status \\|\\| '未知'|v-model=\"form\\.(pay_list_id|fee_item_id)\"" frontend/src/modules/annuity/pages/GovPaymentCreate.vue && rg -n "formatPayListContext|formatFeeItemContext|formatGovPaymentDisplay|formatClientDisplay|已选择清单|已登记缴费|未知状态" frontend/src/modules/annuity/pages/GovPaymentCreate.vue'
./scripts/evidence_run.sh AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-ANNUITY-GOV-PAYMENT-RESULT-ID-DISPLAY-01/baseline_external_files.txt`
