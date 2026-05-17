# AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01 - payment create visible ID cleanup

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

Remove visible raw customer ID fallback from the payment creation bill selector.

This closes only:

1. `PaymentCreate.vue` no longer uses `bill.client_id` as visible customer text in bill option labels.
2. `PaymentCreate.vue` uses existing `client_name` when available and otherwise a Chinese customer placeholder.

## Explicit Non-Closure

This task does not:

- modify backend code, billing API wrappers/types, route query names, permissions, response envelopes, or create behavior.
- add customer lookup APIs or any new readable customer display contract.
- change bill selection values, payment creation payload, validation, success routing, payment list behavior, or offset behavior.
- close billing display issues outside `PaymentCreate.vue`.

## Remaining Follow-Up Task IDs

- `AD-FE-CASE-FORM-ID-LABELS-01`
- `AD-FE-CASE-FILTER-ID-LABELS-01`
- `AD-FE-REPORT-FILTER-ID-LABELS-01`
- `AD-FE-DEMO-DISPLAY-CLOSE-AUDIT-01`

## Allowed Files

- `tasks/afterdemon/AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01.md`
- `frontend/src/modules/billing/pages/PaymentCreate.vue`
- `artifacts/AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01/**`

## Verification Commands

Run from repo root:

```bash
./scripts/evidence_run.sh AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01 lint /bin/zsh -lc 'cd frontend && npx eslint src/modules/billing/pages/PaymentCreate.vue --max-warnings 0'
./scripts/evidence_run.sh AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && npm run build'
./scripts/evidence_run.sh AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01 ux_check /bin/zsh -lc '! rg -n "client_name \\|\\| bill\\.client_id|bill\\.client_id \\|\\| |\\$\\{bill\\.client_id\\}" frontend/src/modules/billing/pages/PaymentCreate.vue && rg -n "formatBillClient|未命名客户|未关联客户" frontend/src/modules/billing/pages/PaymentCreate.vue'
./scripts/evidence_run.sh AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01 task_gate ./scripts/task_validate.sh AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01
```

## Evidence Path

- `artifacts/AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01/results.jsonl`
- `artifacts/AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01/summary.md`
- `artifacts/AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01/git/diff.patch`
- `artifacts/AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01/baseline_allowlist.diff`
- `artifacts/AD-FE-BILLING-PAYMENT-CREATE-ID-DISPLAY-01/baseline_external_files.txt`
