# B-AUTO-PY-B-NEED-REPLY-DEADLINE-EDIT-P1-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement only `TC-B-013` / `handle_tc_b_013`: assert document `NeedReply` deadline update/cancel behavior through real document update API, including explicit ambiguous action rejection, task update/cancel side effects, and task log visibility.

## Explicit Non-Closure

Do not implement OA fee, billing, payment, commission, `TC-B-005`, backend, frontend, or skeleton data changes.

## Allowed Files

- `tasks/automation/B-AUTO-PY-B-NEED-REPLY-DEADLINE-EDIT-P1-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_b.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_b_partial_landing_handlers.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_b_remaining_landing_handlers.py`
- `artifacts/B-AUTO-PY-B-NEED-REPLY-DEADLINE-EDIT-P1-01/**`

## Verification Commands

From `FPMS_Automation_Skeleton_Pack/pytest_python`:

- `python3 -m ruff check --fix handlers/wave_b.py tests/test_b_partial_landing_handlers.py tests/test_b_remaining_landing_handlers.py`
- `python3 -m ruff format handlers/wave_b.py tests/test_b_partial_landing_handlers.py tests/test_b_remaining_landing_handlers.py`
- `python3 -m ruff check handlers/wave_b.py tests/test_b_partial_landing_handlers.py tests/test_b_remaining_landing_handlers.py`
- `pytest tests/test_b_remaining_landing_handlers.py tests/test_b_partial_landing_handlers.py -q`
- `FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_USERNAME=admin FPMS_PASSWORD="$FPMS_LOCAL_PASSWORD" FPMS_RUN_ID=LOCAL-RUN-BLAND2-013-001 FPMS_DB_DSN= pytest tests/test_wave_b.py -k TC-B-013 -q`
- `./scripts/task_validate.sh B-AUTO-PY-B-NEED-REPLY-DEADLINE-EDIT-P1-01`

## Evidence Path

- `artifacts/B-AUTO-PY-B-NEED-REPLY-DEADLINE-EDIT-P1-01/results.jsonl`
- `artifacts/B-AUTO-PY-B-NEED-REPLY-DEADLINE-EDIT-P1-01/summary.md`
- `artifacts/B-AUTO-PY-B-NEED-REPLY-DEADLINE-EDIT-P1-01/git/diff.patch`

## Remaining Follow-Up Task IDs

None
