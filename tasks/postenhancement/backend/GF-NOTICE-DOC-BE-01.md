# GF-NOTICE-DOC-BE-01 — grant-fee real notice generation backend

- Source: `docs/superpowers/plans/2026-04-05-grant-fee-notice-document-implementation.md`
- Type: `backend api + service`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为授权费任务补上真实通知函生成的最小后端闭环，新增 batch notice-generation endpoint，创建 `Document`、渲染并落库 docx 附件，并在成功后回写 `notice_sent / notify_count`。
- Exact closure slice:
  - 新增 batch notice request/response schema
  - 新增 backend endpoint
  - 新增 grant-fee notice generation service rule
  - 新增 targeted backend tests
- Explicit non-closure:
  - 不做 reminder task generation
  - 不做 dispatch / envelope
  - 不做 bill / settlement semantics
  - 不做 detail/edit
- Remaining follow-up task ids:
  - `GF-NOTICE-DOC-FE-01`
  - `GF-NOTICE-DOC-QA-01`
- Allowlist:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/tests/test_grant_fee_notice_document_api.py`
- Verification:
  - `python3 -m ruff format backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_notice_document_api.py`
  - `python3 -m ruff check backend/app/modules/grant_fees/api.py backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/service.py backend/tests/test_grant_fee_notice_document_api.py`
  - `cd backend && pytest -q tests/test_grant_fee_notice_document_api.py`

## Execution Checklist

- [ ] Add batch notice-generation schemas and endpoint
- [ ] Reuse frozen `GRANT_FEE_NOTICE` template authority
- [ ] Create `Document`, render and persist attachment, then write back task carrier
- [ ] Add success, invalid-state, missing-template, and permission tests
