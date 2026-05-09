# SKEL-COVERAGE-PY-X-CASE-EXPORT-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Extend the existing pytest Skeleton Pack real handler for `TC-X-001` with one endpoint assertion only:

- `GET /cases/export`

The handler must reuse the deterministic `TC-X-001` case data and assert the exported filtered list contains that case.

## Explicit Non-Closure

This task does not add new case query dimensions, does not implement report aggregation, does not change backend export behavior, does not modify frontend code, and does not alter other X-wave handlers.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_x.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_case_query_handler.py`
- `tasks/automation/SKEL-COVERAGE-PY-X-CASE-EXPORT-01.md`
- `artifacts/SKEL-COVERAGE-PY-X-CASE-EXPORT-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_x.py tests/test_x_case_query_handler.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_x_case_query_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_x.py -q -k TC-X-001`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-X-CASE-EXPORT-01`

## Remaining Follow-up Task IDs

- Additional per-endpoint route coverage tasks for the remaining backend audit gaps.
- Additional per-case real-handler coverage tasks for the remaining canonical case gaps.

## Done Definition

- `TC-X-001` asserts `GET /cases/export` through real API calls.
- Targeted unit/source test and wave dispatch test pass.
- Coverage audit no longer lists `GET /cases/export` as a rough backend uncovered route.
- Required evidence and task gate pass.
