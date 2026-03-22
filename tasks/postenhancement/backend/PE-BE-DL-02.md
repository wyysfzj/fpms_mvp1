# PE-BE-DL-02 — Tasks and deadlines backend completion for Batch 2.

- Source: `docs/FPMS_Final_Enhancement_Plan_Native_20260315.md`
- Type: `service + api`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: complete the Batch 2 backend Tasks/Deadlines scope for template rules, auto-generation sources, role views, manual maintenance, and today reminders.
- Covered items:
  - `US-DL-01`
  - `US-DL-02`
  - `US-DL-03`
  - `US-DL-04`
  - `US-DL-05`
  - `US-DL-07`
  - `FR-DL-01`
  - `FR-DL-02`
  - `FR-DL-04`
  - `FR-DL-05`
  - `FR-DL-06`
  - `FR-DL-08`
- Allowlist:
  - `backend/app/modules/tasks/api.py`
  - `backend/app/modules/tasks/service.py`
  - `backend/app/modules/tasks/schemas.py`
  - `backend/app/modules/tasks/task_generation_service.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/annuity/service.py`
  - `backend/tests/test_task_template.py`
- Shared ownership files:
  - `backend/app/modules/tasks/api.py`
  - `backend/app/modules/tasks/service.py`
  - `backend/app/modules/tasks/schemas.py`
  - `backend/app/modules/tasks/task_generation_service.py`
  - `backend/app/modules/documents/service.py`
- Out of scope:
  - `Batch 3+`
  - document generation / task-sheet printing
  - `US-DL-06`
  - `FR-DL-07`
- Acceptance:
  - template maintenance covers Batch 2 rule gap
  - tasks auto-generate from covered sources within scope
  - worker/supervisor views and today reminders match Batch 2 intent
  - manual create/edit/delete behavior is covered where allowed by current model
- Verification:
  - `ruff check --fix backend/app/modules/tasks/api.py backend/app/modules/tasks/service.py backend/app/modules/tasks/schemas.py backend/app/modules/tasks/task_generation_service.py backend/app/modules/documents/service.py backend/app/modules/annuity/service.py backend/tests/test_task_template.py`
  - `ruff format backend/app/modules/tasks/api.py backend/app/modules/tasks/service.py backend/app/modules/tasks/schemas.py backend/app/modules/tasks/task_generation_service.py backend/app/modules/documents/service.py backend/app/modules/annuity/service.py backend/tests/test_task_template.py`
  - `ruff check backend/app/modules/tasks/api.py backend/app/modules/tasks/service.py backend/app/modules/tasks/schemas.py backend/app/modules/tasks/task_generation_service.py backend/app/modules/documents/service.py backend/app/modules/annuity/service.py backend/tests/test_task_template.py`
  - `pytest -q backend/tests/test_task_template.py`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal failing backend tests first
- [ ] Implement minimal backend changes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
