# SKEL-COVERAGE-PY-X-FEE-OVERVIEW-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Implement the pytest Skeleton Pack real handler for `TC-X-004` only, covering the current fee overview double-table APIs:

- `GET /fee-overview/case-receipts`
- `GET /fee-overview/gov-payments`

The handler must create/reuse deterministic data through real APIs and assert case/applicant/date/fee filters.

## Explicit Non-Closure

This task does not implement `TC-X-002`, `TC-X-003`, or `TC-X-005` through `TC-X-027`; does not add frontend Playwright assertions; does not change backend fee overview behavior; and does not cover export/report endpoints.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_x.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_case_query_handler.py`
- `tasks/automation/SKEL-COVERAGE-PY-X-FEE-OVERVIEW-01.md`
- `artifacts/SKEL-COVERAGE-PY-X-FEE-OVERVIEW-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_x.py tests/test_x_case_query_handler.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_x_case_query_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_x.py -q -k TC-X-004`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-X-FEE-OVERVIEW-01`

## Remaining Follow-up Task IDs

- `SKEL-COVERAGE-PY-X-DOCUMENT-QUERY-01`
- `SKEL-COVERAGE-PY-X-TASK-REPORT-01`
- `SKEL-COVERAGE-PY-X-REPORTS-01`

## Done Definition

- `TC-X-004` is no longer decorated with `@skeleton_case`.
- The handler exercises both fee overview endpoints through real API calls.
- Targeted unit/source test and wave dispatch test pass.
- Required evidence and task gate pass.
