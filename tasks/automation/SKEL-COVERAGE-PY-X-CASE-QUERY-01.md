# SKEL-COVERAGE-PY-X-CASE-QUERY-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Implement the pytest Skeleton Pack real handler for `TC-X-001` only, covering the current `/cases` advanced query surface for basic dimensions: case number, application number, case type, patent category, flow direction, status, client, and filing date range.

## Explicit Non-Closure

This task does not implement `TC-X-002` through `TC-X-027`, does not add frontend Playwright assertions, does not change backend query behavior, and does not create report/export coverage.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_x.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_case_query_handler.py`
- `tasks/automation/SKEL-COVERAGE-PY-X-CASE-QUERY-01.md`
- `artifacts/SKEL-COVERAGE-PY-X-CASE-QUERY-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_x.py tests/test_x_case_query_handler.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_x_case_query_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_x.py -q -k TC-X-001`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-X-CASE-QUERY-01`

## Remaining Follow-up Task IDs

- `SKEL-COVERAGE-PY-X-CONTROL-FILTERS-01`
- `SKEL-COVERAGE-PY-X-DOCUMENT-QUERY-01`
- `SKEL-COVERAGE-PY-X-TASK-REPORT-01`

## Done Definition

- `TC-X-001` is no longer decorated with `@skeleton_case`.
- The handler creates or reuses deterministic test data and queries the real `/cases` API across the defined basic dimensions.
- Targeted unit/source test and wave dispatch test pass.
- Required evidence and task gate pass.
