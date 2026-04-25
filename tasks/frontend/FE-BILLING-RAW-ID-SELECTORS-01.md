# FE-BILLING-RAW-ID-SELECTORS-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Replace raw billing-facing ID inputs with existing business selectors where backend support already exists:

- `BillCreate.vue`: manual bill client selector and optional case selector.
- `PaymentCreate.vue`: bill selector for payment target.
- `PaymentList.vue`: client selector for prepayment filter.

## Explicit Non-Closure

This task does not change backend behavior, API wrappers, commission pages, case create/edit forms, task forms, pay-list manual fee-item selectors, agent/worker selectors, offset dialog behavior, or route/menu configuration.

## Remaining Follow-Up Task IDs

- FE-TASK-CASE-SELECTOR-01
- FE-CASE-RELATED-SELECTORS-01-SPLIT
- PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01

## Allowed Files

- tasks/frontend/FE-BILLING-RAW-ID-SELECTORS-01.md
- frontend/src/modules/billing/pages/BillCreate.vue
- frontend/src/modules/billing/pages/PaymentCreate.vue
- frontend/src/modules/billing/pages/PaymentList.vue
- artifacts/FE-BILLING-RAW-ID-SELECTORS-01/**

## Verification Commands

- cd frontend && npm run typecheck
- cd frontend && npm run build
- rg -n "请选择客户|请选择案件|请选择账单|clientOptions|caseOptions|billOptions" frontend/src/modules/billing/pages/BillCreate.vue frontend/src/modules/billing/pages/PaymentCreate.vue frontend/src/modules/billing/pages/PaymentList.vue
- ./scripts/task_validate.sh FE-BILLING-RAW-ID-SELECTORS-01

## Evidence Path

- artifacts/FE-BILLING-RAW-ID-SELECTORS-01/results.jsonl
- artifacts/FE-BILLING-RAW-ID-SELECTORS-01/summary.md
- artifacts/FE-BILLING-RAW-ID-SELECTORS-01/git/diff.patch
