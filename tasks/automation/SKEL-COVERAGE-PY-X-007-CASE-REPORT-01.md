# SKEL-COVERAGE-PY-X-007-CASE-REPORT-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Convert canonical `TC-X-007` from skeleton to a real pytest handler covering case report summary aggregation through `/cases`.

## Explicit Non-Closure

This task does not implement frontend report UI, spreadsheet export, agent assignment reports, full yearly analytics, legal state transition logic, or any additional canonical cases.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_x.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_case_report_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_case_query_handler.py`
- `tasks/automation/SKEL-COVERAGE-PY-X-007-CASE-REPORT-01.md`
- `artifacts/SKEL-COVERAGE-PY-X-007-CASE-REPORT-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_x.py tests/test_x_case_report_handler.py tests/test_x_case_query_handler.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_x_case_report_handler.py tests/test_x_case_query_handler.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py --json`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-X-007-CASE-REPORT-01`

## Evidence Path

- `artifacts/SKEL-COVERAGE-PY-X-007-CASE-REPORT-01/**`

## Remaining Follow-Up Task IDs

- Additional canonical real-handler coverage tasks for W0/C/D/E/F/G/G0/H/X waves.

## Done Definition

- `TC-X-007` is no longer marked with `@skeleton_case`.
- `TC-X-007` creates or finds report cases with different statuses and countries.
- `TC-X-007` verifies `/cases` summary status counts, client counts, country counts, and total count for the scoped client.
- Coverage audit reduces `cases_without_real_handler_count` by one.
- Required evidence and task gate pass.
