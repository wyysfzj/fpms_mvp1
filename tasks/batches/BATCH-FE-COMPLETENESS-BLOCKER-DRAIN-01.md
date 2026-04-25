# BATCH-FE-COMPLETENESS-BLOCKER-DRAIN-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Drain Decision

Readiness did not find a hard backend/product blocker for the first eight P0 FE
capability tasks. Document wizard real-write behavior and broad case raw-ID
selector work are deferred to follow-up tasks and must not be absorbed into this
batch.

## Executable FE Capability Tasks

1. FE-FEE-APPLY-FEE-GENERATE-01
2. FE-PAYLIST-FROM-FEE-ITEMS-01
3. FE-PAYLIST-DETAIL-ENTRY-01
4. FE-GOV-PAYMENT-FROM-PAYLIST-ITEM-01
5. FE-BILL-DIRECTION-VISIBILITY-01
6. FE-PAYMENT-CREATE-ENTRY-01
7. FE-COMMISSION-SETTLEABILITY-VISIBILITY-01
8. FE-MENU-PERMISSION-ALIGNMENT-01

## Deferred Blockers

| Task ID | Type | Reason |
| --- | --- | --- |
| PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01 | product contract | Document wizard preview/write semantics require product confirmation. |
| FE-CASE-RELATED-SELECTORS-01 | frontend usability | Broad selector replacement touches multiple case form surfaces and should be separate. |
| BE-FE-COMMISSION-QUERY-READINESS-01 | backend readiness | Only needed if business-friendly case-no/bill-no commission search is required. |

## Shared File Serialization

- Execute all FE tasks serially.
- Do not run concurrent workers against `frontend/src/api/**`, `frontend/src/constants/menu.ts`, or shared billing/annuity/commission pages.

## Verification

Each executed task must run task-scoped source checks plus final frontend
typecheck/build where practical.
