# GF-BILL-VIS-01 Design

## Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Problem Statement
`GF-BILL-SPEC-01` has already frozen bill-linkage semantics for grant-fee tasks. What is still missing is a narrow visibility slice on the grant-fee worklist so users can tell whether a `DRAFT_GENERATED` task has already entered billing, without adding a new state or bill-generation action.

## Closure Slice
- Extend grant-fee worklist projection with bill visibility fields derived from existing draft and bill lineage.
- Show bill visibility on the grant-fee task board, including a link to the existing bill detail page when available.

## Non-Closure
- No new grant-fee task state.
- No bill generation trigger from the grant-fee page.
- No receipt/payment semantics.
- No document/reminder linkage.

## Authority
- `FeeItem.remark = GRANT_FEE_TASK:<task_id>` is the grant-fee task marker.
- `BillItem.draft_id` is the billing lineage authority.
- First-round worklist visibility should expose:
  - `billed`
  - `linked_bill_id`
  - `linked_bill_no`

## Shared Ownership
- Backend:
  - `backend/app/modules/grant_fees/service.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/tests/test_grant_fee_worklist_api.py`
- Frontend:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`

