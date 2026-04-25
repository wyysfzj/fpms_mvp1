# FE-BILL-DIRECTION-VISIBILITY-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Display existing bill direction (`AR`/`AP`) in bill list and bill detail.

## Explicit Non-Closure

Do not change bill generation, billing API behavior, payment, offset, or bad
debt logic.

## Remaining Follow-Up Task IDs

- FE-PAYMENT-CREATE-ENTRY-01

## Allowed Files

- tasks/frontend/FE-BILL-DIRECTION-VISIBILITY-01.md
- frontend/src/api/billing.ts
- frontend/src/api/billing.types.ts
- frontend/src/modules/billing/pages/BillList.vue
- frontend/src/modules/billing/pages/BillDetail.vue
- artifacts/FE-BILL-DIRECTION-VISIBILITY-01/**

## Verification Commands

```bash
cd frontend && npm run typecheck
cd frontend && npm run build
./scripts/task_validate.sh FE-BILL-DIRECTION-VISIBILITY-01
```

## Evidence Path

- artifacts/FE-BILL-DIRECTION-VISIBILITY-01/results.jsonl
- artifacts/FE-BILL-DIRECTION-VISIBILITY-01/summary.md
- artifacts/FE-BILL-DIRECTION-VISIBILITY-01/git/diff.patch
