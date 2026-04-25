# B-AUTO-PY-B-REPLY-TASK-P0-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement only `TC-B-004` / `handle_tc_b_004`: create OA incoming document and assert linked `OA_REPLY` task, `OPEN` status, due date, title, and creation log action.

## Explicit Non-Closure

Do not implement reply submit or auto write-off. Do not implement other B handlers.

## Allowed Files

- `tasks/automation/B-AUTO-PY-B-REPLY-TASK-P0-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_b.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_b_partial_landing_handlers.py`
- `artifacts/B-AUTO-PY-B-REPLY-TASK-P0-01/**`

## Verification Commands

See batch manifest scoped B partial commands. Real smoke target: `pytest tests/test_wave_b.py -k TC-B-004 -q` with `FPMS_DB_DSN=`.

## Evidence Path

- `artifacts/B-AUTO-PY-B-REPLY-TASK-P0-01/results.jsonl`
- `artifacts/B-AUTO-PY-B-REPLY-TASK-P0-01/summary.md`
- `artifacts/B-AUTO-PY-B-REPLY-TASK-P0-01/git/diff.patch`

## Remaining Follow-Up Task IDs

None
