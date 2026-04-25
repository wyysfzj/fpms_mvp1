# BE-A-TASK-REMINDER-RESPONSE-01

Task ID: `BE-A-TASK-REMINDER-RESPONSE-01`

Role: worker

Story Shape Classification:
- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Expose existing task reminder fields in task detail and list responses so automation can assert `TC-A-014` reminder semantics without DB access.

This task closes only:

1. `GET /api/v1/tasks/{task_id}` includes `remind1`, `remind2`, `remind3`, `daily_remind_from`, and `daily_remind`.
2. `GET /api/v1/tasks` list items include the same reminder fields.
3. Existing task response fields remain backward-compatible.

## Explicit Non-Closure

Do not modify task generation logic, backend case logic, frontend, pytest skeleton handlers, skeleton data, schema migrations, or Playwright assets.

## Remaining Follow-Up Task IDs

- `A-AUTO-PY-A-TASK_REASSIGN-P1-01`

## Allowed Files

- `tasks/backend/apis_ext/BE-A-TASK-REMINDER-RESPONSE-01.md`
- `backend/app/modules/tasks/schemas.py`
- `backend/app/modules/tasks/api.py`
- `backend/tests/test_task_reminder_response.py`
- `artifacts/BE-A-TASK-REMINDER-RESPONSE-01/**`

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/tasks/schemas.py app/modules/tasks/api.py tests/test_task_reminder_response.py
python3 -m ruff format app/modules/tasks/schemas.py app/modules/tasks/api.py tests/test_task_reminder_response.py
python3 -m ruff check app/modules/tasks/schemas.py app/modules/tasks/api.py tests/test_task_reminder_response.py
pytest tests/test_task_reminder_response.py -q
pytest tests/test_apply_fee_limit_base_source.py -q
```

## Evidence Path

- `artifacts/BE-A-TASK-REMINDER-RESPONSE-01/results.jsonl`
- `artifacts/BE-A-TASK-REMINDER-RESPONSE-01/summary.md`
- `artifacts/BE-A-TASK-REMINDER-RESPONSE-01/git/diff.patch`
