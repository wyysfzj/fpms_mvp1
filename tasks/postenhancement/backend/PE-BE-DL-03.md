# PE-BE-DL-03 — Tasks backend follow-up for views and today reminders.

- Source: `tasks/postenhancement/BATCH2_REMAINING_MANIFEST_20260316.md`
- Type: `service + api`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: close the remaining feasible Batch 2 backend Tasks scope for worker/supervisor views and today reminders.
- Covered items:
  - `US-DL-01`
  - `US-DL-02`
  - `US-DL-03`
  - `US-DL-04`
  - `US-DL-07`
  - `FR-DL-01`
  - `FR-DL-02`
  - `FR-DL-04`
  - `FR-DL-05`
  - `FR-DL-08`
- Allowlist:
  - `backend/app/modules/tasks/api.py`
  - `backend/app/modules/tasks/service.py`
  - `backend/app/modules/tasks/schemas.py`
  - `backend/app/modules/tasks/task_generation_service.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/annuity/service.py`
  - `backend/tests/test_task_template.py`
- Out of scope:
  - document generation
  - Batch 3+
  - schema migrations
- Acceptance:
  - `/tasks` supports the role-view filters needed by Batch 2 FE
  - `/tasks/today` returns the display fields needed by TodayReminders/Dashboard
  - covered auto-generation sources remain green and idempotent
- Verification:
  - `ruff check backend/app/modules/tasks/api.py backend/app/modules/tasks/service.py backend/app/modules/tasks/schemas.py backend/app/modules/tasks/task_generation_service.py backend/app/modules/documents/service.py backend/app/modules/annuity/service.py backend/tests/test_task_template.py`
  - `cd backend && pytest -q tests/test_task_template.py`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal failing backend tests first
- [ ] Implement minimal backend changes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
