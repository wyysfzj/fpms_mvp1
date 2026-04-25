# BATCH-FE-RAW-ID-SELECTORS-RESIDUAL-CLOSE-AUDIT-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Audit recent FE raw-ID and discoverability remediation work, map remaining selector gaps to focused follow-up tasks, and run final frontend verification.

## Explicit Non-Closure

This task does not implement new frontend features, backend behavior, selectors, routes, product contracts, or automation handlers.

## Remaining Follow-Up Task IDs

- FE-DOCUMENT-CASE-SELECTORS-01
- FE-PAYLIST-CLIENT-CASE-SELECTORS-01
- PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01
- PRODUCT-FE-PAYLIST-MANUAL-FEE-ITEM-SELECTOR-CONTRACT-01
- PRODUCT-COMMISSION-BILL-NO-QUERY-CONTRACT-01

## Allowed Files

- tasks/batches/BATCH-FE-RAW-ID-SELECTORS-RESIDUAL-CLOSE-AUDIT-01.md
- docs/frontend/FE_RAW_ID_SELECTORS_RESIDUAL_CLOSE_AUDIT.md
- artifacts/BATCH-FE-RAW-ID-SELECTORS-RESIDUAL-CLOSE-AUDIT-01/**

## Verification Commands

- cd frontend && npm run typecheck
- cd frontend && npm run build
- rg -n "Fixed|Residual|GO|NO-GO|FE-DOCUMENT-CASE-SELECTORS-01|PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01" docs/frontend/FE_RAW_ID_SELECTORS_RESIDUAL_CLOSE_AUDIT.md
- ./scripts/task_validate.sh BATCH-FE-RAW-ID-SELECTORS-RESIDUAL-CLOSE-AUDIT-01

## Evidence Path

- artifacts/BATCH-FE-RAW-ID-SELECTORS-RESIDUAL-CLOSE-AUDIT-01/results.jsonl
- artifacts/BATCH-FE-RAW-ID-SELECTORS-RESIDUAL-CLOSE-AUDIT-01/summary.md
- artifacts/BATCH-FE-RAW-ID-SELECTORS-RESIDUAL-CLOSE-AUDIT-01/git/diff.patch
