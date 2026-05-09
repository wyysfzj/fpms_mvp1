# SKEL-COVERAGE-PY-X-TASK-TODAY-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Implement the pytest Skeleton Pack real handler for `TC-X-017` only, covering the current task views and output endpoints:

- `GET /tasks/today`
- `GET /tasks/export`
- `GET /tasks/print`

The handler must create/reuse deterministic task data through real APIs and assert worker/supervisor views plus export/print responses.

## Explicit Non-Closure

This task does not implement `TC-X-005`, `TC-X-006`, `TC-X-012`, or `TC-X-018` through `TC-X-027`; does not add frontend Playwright assertions; does not change backend task behavior; and does not cover special-search endpoints.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_x.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_case_query_handler.py`
- `tasks/automation/SKEL-COVERAGE-PY-X-TASK-TODAY-01.md`
- `artifacts/SKEL-COVERAGE-PY-X-TASK-TODAY-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_x.py tests/test_x_case_query_handler.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_x_case_query_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_x.py -q -k TC-X-017`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-X-TASK-TODAY-01`

## Remaining Follow-up Task IDs

- `SKEL-COVERAGE-PY-X-TASK-SPECIAL-SEARCH-01`
- `SKEL-COVERAGE-PY-X-TASK-LOGS-01`
- `SKEL-COVERAGE-PW-DYNAMIC-ROUTE-SMOKE-01`

## Done Definition

- `TC-X-017` is no longer decorated with `@skeleton_case`.
- The handler exercises task today, task export, and task print endpoints through real API calls.
- Targeted unit/source test and wave dispatch test pass.
- Required evidence and task gate pass.
