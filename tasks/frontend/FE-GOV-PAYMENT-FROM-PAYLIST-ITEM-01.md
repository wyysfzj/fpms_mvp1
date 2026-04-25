# FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Allow official payment registration from a specific pay-list fee item so the
registration page receives both `pay_list_id` and `fee_item_id`.

## Explicit Non-Closure

Do not implement pay-list creation, backend payment rules, or billing/payment
offset behavior.

## Remaining Follow-Up Task IDs

- FE-BILL-DIRECTION-VISIBILITY-01

## Allowed Files

- tasks/frontend/FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01.md
- frontend/src/modules/annuity/pages/PayListDetail.vue
- frontend/src/modules/annuity/pages/GovPaymentCreate.vue
- artifacts/FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01/**

## Verification Commands

```bash
cd frontend && npm run typecheck
cd frontend && npm run build
./scripts/task_validate.sh FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01
```

## Evidence Path

- artifacts/FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01/results.jsonl
- artifacts/FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01/summary.md
- artifacts/FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01/git/diff.patch
