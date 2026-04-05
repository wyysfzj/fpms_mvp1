# Grant Fee Notice Visibility Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `notice carrier visibility slice`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`GF-DOC-SPEC-01` has already frozen that `notice_sent / notify_count` are internal grant-fee workflow carriers and do not prove real `Document` or `Task` linkage. The current worklist only shows a binary `已通知 / 待通知` tag, which is too coarse and can still be misread as real document/reminder linkage. The first product follow-up should stay narrow: expose the internal carrier semantics more precisely on the existing worklist.

## Closure Slice

- Extend grant-fee worklist payload with `notify_count`
- Render a read-only notice visibility block on the existing worklist
- Make the page wording explicit that this is internal notification status, not real document/reminder linkage

## Explicit Non-closure

- No real `Document` generation
- No real `Task` reminder generation
- No state-machine expansion
- No bill / receipt semantics

## Shared Ownership

- Backend:
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_grant_fee_worklist_api.py`
- Frontend:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`

