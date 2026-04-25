# FE-PAYLIST-FROM-FEE-ITEMS-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Add a frontend action to create an official pay list from selected GOV fee items
in a fee draft.

This task closes only:

1. Fee item API/types expose enough fee metadata to identify GOV items.
2. Fee draft item table allows selecting GOV fee items.
3. UI calls the existing pay-list-from-fee-items backend wrapper.
4. Successful creation navigates to the created pay-list detail.

## Explicit Non-Closure

Do not implement official payment registration. Do not change backend. Do not
implement billing/payment/commission behavior.

## Remaining Follow-Up Task IDs

- FE-PAYLIST-DETAIL-ENTRY-01
- FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01

## Allowed Files

- tasks/frontend/FE-PAYLIST-FROM-FEE-ITEMS-01.md
- frontend/src/api/fees.ts
- frontend/src/api/fees.types.ts
- frontend/src/api/govPayments.ts
- frontend/src/api/govPayments.types.ts
- frontend/src/modules/fees/components/FeeDraftItemsTable.vue
- artifacts/FE-PAYLIST-FROM-FEE-ITEMS-01/**

## Verification Commands

```bash
cd frontend && npm run typecheck
cd frontend && npm run build
./scripts/task_validate.sh FE-PAYLIST-FROM-FEE-ITEMS-01
```

## Evidence Path

- artifacts/FE-PAYLIST-FROM-FEE-ITEMS-01/results.jsonl
- artifacts/FE-PAYLIST-FROM-FEE-ITEMS-01/summary.md
- artifacts/FE-PAYLIST-FROM-FEE-ITEMS-01/git/diff.patch
