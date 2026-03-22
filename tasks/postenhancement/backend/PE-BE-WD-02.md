# PE-BE-WD-02 — Documents backend completion for Batch 2.

- Source: `docs/FPMS_Final_Enhancement_Plan_Native_20260315.md`
- Type: `service + api`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: complete the Batch 2 backend Documents scope for template defaults, reply/deadline linkage, fee/status linkage, and query capability.
- Covered items:
  - `US-WD-01`
  - `US-WD-02`
  - `US-WD-03`
  - `US-WD-04`
  - `US-WD-06`
  - `FR-WD-01`
  - `FR-WD-03`
  - `FR-WD-04`
  - `FR-WD-07`
- Allowlist:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/app/modules/tasks/task_generation_service.py`
  - `backend/tests/test_b2_reply_chain.py`
  - `backend/tests/test_b3_fee_linking.py`
- Shared ownership files:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/documents/schemas.py`
  - `backend/app/modules/documents/fee_linking_service.py`
  - `backend/app/modules/tasks/task_generation_service.py`
- Out of scope:
  - `Batch 3+`
  - document generation / printing / envelope / handoff-sheet
  - `FR-WD-02`
  - `US-WD-07`
  - `FR-WD-08`
  - `FR-WD-09`
- Acceptance:
  - common-file definitions populate missing defaults consistently
  - reply-required documents create or update deadline-linked task records correctly
  - fee/status linkage works for covered non-generation flows
  - query APIs support the Batch 2 filter/reporting gap without implementing document output generation
- Verification:
  - `ruff check --fix backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/fee_linking_service.py backend/app/modules/tasks/task_generation_service.py backend/tests/test_b2_reply_chain.py backend/tests/test_b3_fee_linking.py`
  - `ruff format backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/fee_linking_service.py backend/app/modules/tasks/task_generation_service.py backend/tests/test_b2_reply_chain.py backend/tests/test_b3_fee_linking.py`
  - `ruff check backend/app/modules/documents/api.py backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/fee_linking_service.py backend/app/modules/tasks/task_generation_service.py backend/tests/test_b2_reply_chain.py backend/tests/test_b3_fee_linking.py`
  - `pytest -q backend/tests/test_b2_reply_chain.py backend/tests/test_b3_fee_linking.py`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal failing backend tests first
- [ ] Implement minimal backend changes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
