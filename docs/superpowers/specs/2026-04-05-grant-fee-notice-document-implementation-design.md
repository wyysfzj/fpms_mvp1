# Grant Fee Notice Document Implementation Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `cross-module FE/BE notice document generation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Problem Statement

`GF-NOTICE-DOC-SPEC-01` has already frozen the authority for real grant-fee notice generation. The next exact closure slice is to turn the existing grant-fee worklist selection into a real batch notice-document path: generate `Document` rows with `DocTemplate.code = GRANT_FEE_NOTICE`, render and persist docx attachments, and only then write back `notice_sent / notify_count`.

## Closure Slice

- backend:
  - add grant-fee batch notice-generation endpoint
  - create real `Document`
  - render and persist one docx attachment per selected task
  - update `notice_sent / notify_count` only after success
- frontend:
  - add real batch `生成通知函` path on existing grant-fee worklist
  - refresh list after success

## Explicit Non-closure

- no reminder task generation
- no dispatch / envelope
- no bill / settlement semantics
- no detail/edit page

## Shared Ownership

- Backend:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_grant_fee_notice_document_api.py`
- Frontend:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`

## Verification

- `python3 -m ruff format backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_notice_document_api.py`
- `python3 -m ruff check backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_notice_document_api.py`
- `cd backend && pytest -q tests/test_grant_fee_notice_document_api.py`
- `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `cd frontend && npm run typecheck`
