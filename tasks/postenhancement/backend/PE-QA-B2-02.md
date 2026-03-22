# PE-QA-B2-02 — Batch 2 final close audit after remaining follow-up tasks.

- Source: `tasks/postenhancement/BATCH2_REMAINING_MANIFEST_20260316.md`
- Type: `qa gate`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: determine whether Batch 2 can finally be closed after the remaining follow-up tasks complete.
- Scope checked:
  - all Batch 2 Documents items
  - all Batch 2 Tasks/Deadlines items
- Allowlist:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/app/modules/tasks/api.py`
  - `backend/app/modules/tasks/service.py`
  - `backend/app/modules/tasks/schemas.py`
  - `backend/app/modules/tasks/task_generation_service.py`
  - `backend/app/modules/annuity/service.py`
  - `backend/tests/test_b2_reply_chain.py`
  - `backend/tests/test_b3_fee_linking.py`
  - `backend/tests/test_task_template.py`
  - `frontend/src/modules/documents/pages/DocumentCreate.vue`
  - `frontend/src/modules/documents/pages/DocumentEdit.vue`
  - `frontend/src/modules/documents/pages/DocumentDetail.vue`
  - `frontend/src/modules/documents/pages/DocumentList.vue`
  - `frontend/src/modules/tasks/pages/TaskList.vue`
  - `frontend/src/modules/tasks/pages/TaskDetail.vue`
  - `frontend/src/modules/tasks/pages/TaskCreate.vue`
  - `frontend/src/modules/tasks/pages/TodayReminders.vue`
  - `frontend/src/modules/dashboard/pages/Dashboard.vue`
  - `frontend/src/modules/dashboard/components/TodoTable.vue`
  - `frontend/src/modules/system/pages/TaskTemplateList.vue`
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `frontend/src/api/tasks.ts`
  - `frontend/src/api/tasks.types.ts`
  - `docs/FPMS_Final_Enhancement_execution_summary_20260315.md`
- Verification:
  - `./scripts/task_validate.sh PE-BE-WD-03`
  - `./scripts/task_validate.sh PE-FE-WD-03`
  - `./scripts/task_validate.sh PE-BE-DL-03`
  - `./scripts/task_validate.sh PE-FE-DL-03`
  - `cd backend && pytest -q tests/test_b2_reply_chain.py tests/test_b3_fee_linking.py tests/test_task_template.py`
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`
