# PE-BE-WD-03 — Documents backend follow-up for defaults and reply/deadline closure.

- Source: `tasks/postenhancement/BATCH2_REMAINING_MANIFEST_20260316.md`
- Type: `service + api`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close the remaining feasible Batch 2 backend Documents scope for template defaults and reply/deadline behavior.
- Covered items:
  - `US-WD-01`
  - `US-WD-02`
  - `US-WD-03`
  - `US-WD-04`
  - `FR-WD-01`
  - `FR-WD-03`
  - `FR-WD-04`
- Allowlist:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/app/modules/tasks/task_generation_service.py`
  - `backend/app/modules/tasks/service.py`
  - `backend/tests/test_b2_reply_chain.py`
  - `backend/tests/test_b3_fee_linking.py`
- Out of scope:
  - document generation
  - query/export-only follow-up
  - `Batch 3+`
- Acceptance:
  - create/update/detail behavior exposes and preserves template-default-backed fields needed by FE
  - reply/deadline auto-generation path is test-covered and idempotent for covered flows
  - no generation/printing/export behavior is introduced
- Verification:
  - `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/fee_linking_service.py backend/app/modules/tasks/task_generation_service.py backend/app/modules/tasks/service.py backend/tests/test_b2_reply_chain.py backend/tests/test_b3_fee_linking.py`
  - `cd backend && pytest -q tests/test_b2_reply_chain.py tests/test_b3_fee_linking.py`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal failing backend tests first
- [ ] Implement minimal backend changes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
