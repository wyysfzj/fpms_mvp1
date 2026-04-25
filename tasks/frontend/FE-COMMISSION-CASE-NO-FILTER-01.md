# FE-COMMISSION-CASE-NO-FILTER-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Update the commission list frontend to use backend-supported business case number search:

- `CommissionListParams` accepts `case_no`.
- frontend backend-record mapping preserves returned `case_no`.
- `CommissionList.vue` sends `case_no` instead of raw `case_id` for the user-facing case filter.
- the commission table displays the business case number when available.

## Explicit Non-Closure

This task does not implement `bill_no` search, agent selector, backend changes, settlement behavior, commission generation behavior, or raw-ID cleanup outside the commission case-number filter.

## Remaining Follow-Up Task IDs

- PRODUCT-COMMISSION-BILL-NO-QUERY-CONTRACT-01
- FE-BILLING-RAW-ID-SELECTORS-01
- FE-CASE-RELATED-SELECTORS-01-SPLIT

## Allowed Files

- tasks/frontend/FE-COMMISSION-CASE-NO-FILTER-01.md
- frontend/src/api/commission.ts
- frontend/src/api/commission.types.ts
- frontend/src/modules/commission/pages/CommissionList.vue
- artifacts/FE-COMMISSION-CASE-NO-FILTER-01/**

## Verification Commands

- cd frontend && npm run typecheck
- cd frontend && npm run build
- rg -n "case_no|案卷号|案件号" frontend/src/api/commission.ts frontend/src/api/commission.types.ts frontend/src/modules/commission/pages/CommissionList.vue
- ./scripts/task_validate.sh FE-COMMISSION-CASE-NO-FILTER-01

## Evidence Path

- artifacts/FE-COMMISSION-CASE-NO-FILTER-01/results.jsonl
- artifacts/FE-COMMISSION-CASE-NO-FILTER-01/summary.md
- artifacts/FE-COMMISSION-CASE-NO-FILTER-01/git/diff.patch
