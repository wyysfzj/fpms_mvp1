# PE-BE-WD-02

Status: PASS

Scope:
- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/fee_linking_service.py`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/tests/test_b2_reply_chain.py`
- `backend/tests/test_b3_fee_linking.py`

Changes:
- guarded document-driven case `status_effect` updates with the existing case status transition validator
- added backend regression coverage that rejects document template status regression from terminal case states
- added Batch 2 query filters for `need_reply` and `replied` on `/documents`
- added regression coverage for document-list reply-state filtering
- confirmed current reply-chain and fee-linking behavior remains green in task-scoped tests

Validation:
- `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/fee_linking_service.py backend/app/modules/tasks/task_generation_service.py backend/tests/test_b2_reply_chain.py backend/tests/test_b3_fee_linking.py`
- `cd backend && pytest -q tests/test_b2_reply_chain.py tests/test_b3_fee_linking.py`
- `./scripts/task_validate.sh PE-BE-WD-02`

Notes:
- pytest must run from `backend/` because the test harness expects `backend/alembic.ini`
- no document-generation scope was implemented
- this closes an additional Batch 2 query-gap slice, but does not yet prove all remaining Documents backend scope is complete
