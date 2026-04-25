# FE-MENU-ROUTE-DISCOVERABILITY-02

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Expose already-existing residual frontend routes through discoverable sidebar menu entries and list/home page actions:

- documents list
- document wizard action
- document dispatch action
- fee rates
- letterheads
- masterdata home
- department card in masterdata home

## Explicit Non-Closure

This task does not implement backend behavior, does not change route definitions, does not change document wizard write semantics, does not implement raw-ID selector replacements, and does not change billing/payment/commission behavior.

## Remaining Follow-Up Task IDs

- FE-DOCUMENT-WIZARD-REAL-WRITE-UX-01
- FE-CASE-RELATED-SELECTORS-01-SPLIT
- FE-BILLING-RAW-ID-SELECTORS-01
- BE-FE-COMMISSION-QUERY-READINESS-01

## Allowed Files

- tasks/frontend/FE-MENU-ROUTE-DISCOVERABILITY-02.md
- frontend/src/constants/menu.ts
- frontend/src/constants/perms.ts
- frontend/src/modules/documents/pages/DocumentList.vue
- frontend/src/modules/settings/pages/MasterDataHome.vue
- artifacts/FE-MENU-ROUTE-DISCOVERABILITY-02/**

## Verification Commands

- cd frontend && npm run typecheck
- cd frontend && npm run build
- ./scripts/task_validate.sh FE-MENU-ROUTE-DISCOVERABILITY-02

## Evidence Path

- artifacts/FE-MENU-ROUTE-DISCOVERABILITY-02/results.jsonl
- artifacts/FE-MENU-ROUTE-DISCOVERABILITY-02/summary.md
- artifacts/FE-MENU-ROUTE-DISCOVERABILITY-02/git/diff.patch
