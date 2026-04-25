# FE-COMMISSION-SETTLEABILITY-VISIBILITY-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Expose existing commission wait-pay, force-settle, and settlement eligibility
fields in the commission record list.

## Explicit Non-Closure

Do not add unsupported case-number or bill-number backend search. Do not change
commission calculation, settlement generation, or backend rules.

## Remaining Follow-Up Task IDs

- FE-MENU-PERMISSION-ALIGNMENT-01
- BE-FE-COMMISSION-QUERY-READINESS-01 if case-no/bill-no search is required.

## Allowed Files

- tasks/frontend/FE-COMMISSION-SETTLEABILITY-VISIBILITY-01.md
- frontend/src/api/commission.ts
- frontend/src/api/commission.types.ts
- frontend/src/modules/commission/pages/CommissionList.vue
- artifacts/FE-COMMISSION-SETTLEABILITY-VISIBILITY-01/**

## Verification Commands

```bash
cd frontend && npm run typecheck
cd frontend && npm run build
./scripts/task_validate.sh FE-COMMISSION-SETTLEABILITY-VISIBILITY-01
```

## Evidence Path

- artifacts/FE-COMMISSION-SETTLEABILITY-VISIBILITY-01/results.jsonl
- artifacts/FE-COMMISSION-SETTLEABILITY-VISIBILITY-01/summary.md
- artifacts/FE-COMMISSION-SETTLEABILITY-VISIBILITY-01/git/diff.patch
