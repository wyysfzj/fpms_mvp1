# SKEL-COVERAGE-PY-X-EXAM-SPECIAL-SEARCH-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Implement the pytest Skeleton Pack real handler for `TC-X-006` only, covering `EXAM_REQUEST_LIMIT` special deadline search through the current real API route family:

- `GET /tasks/special/search`
- `GET /tasks/special/search/export`
- `GET /tasks/special/search/print`

The handler must create/reuse deterministic client, applicant, case, task template, and open task data through real APIs, then assert search filters and output responses for the exam-request deadline code.

## Explicit Non-Closure

This task does not modify the completed `TC-X-005` closure, does not implement task operation logs, does not add frontend Playwright assertions, does not change backend task behavior, and does not implement other X-wave report handlers.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_x.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_case_query_handler.py`
- `tasks/automation/SKEL-COVERAGE-PY-X-EXAM-SPECIAL-SEARCH-01.md`
- `artifacts/SKEL-COVERAGE-PY-X-EXAM-SPECIAL-SEARCH-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_x.py tests/test_x_case_query_handler.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_x_case_query_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_x.py -q -k TC-X-006`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-X-EXAM-SPECIAL-SEARCH-01`

## Remaining Follow-up Task IDs

- `SKEL-COVERAGE-PY-X-TASK-LOGS-01`
- Additional per-case real-handler coverage tasks for the remaining audit gaps.

## Done Definition

- `TC-X-006` is no longer decorated with `@skeleton_case`.
- The handler exercises special-search list, export, and print endpoints through real API calls for `EXAM_REQUEST_LIMIT`.
- Targeted unit/source test and wave dispatch test pass.
- Coverage audit shows one additional pytest real handler.
- Required evidence and task gate pass.
