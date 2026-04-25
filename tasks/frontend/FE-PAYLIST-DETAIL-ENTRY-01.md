# FE-PAYLIST-DETAIL-ENTRY-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Add a discoverable row-level detail entry from the official pay-list list page.

## Explicit Non-Closure

Do not change backend APIs. Do not implement official payment registration or
pay-list creation behavior.

## Remaining Follow-Up Task IDs

- FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01

## Allowed Files

- tasks/frontend/FE-PAYLIST-DETAIL-ENTRY-01.md
- frontend/src/modules/annuity/pages/PayList.vue
- frontend/src/modules/annuity/pages/PayListDetail.vue
- artifacts/FE-PAYLIST-DETAIL-ENTRY-01/**

## Verification Commands

```bash
cd frontend && npm run typecheck
cd frontend && npm run build
./scripts/task_validate.sh FE-PAYLIST-DETAIL-ENTRY-01
```

## Evidence Path

- artifacts/FE-PAYLIST-DETAIL-ENTRY-01/results.jsonl
- artifacts/FE-PAYLIST-DETAIL-ENTRY-01/summary.md
- artifacts/FE-PAYLIST-DETAIL-ENTRY-01/git/diff.patch
