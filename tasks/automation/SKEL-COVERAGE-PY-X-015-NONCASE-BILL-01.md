# SKEL-COVERAGE-PY-X-015-NONCASE-BILL-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Convert canonical `TC-X-015` from skeleton to a real pytest handler covering manual non-case bill creation through `/bills/manual` and detail verification through `/bills/{bill_id}`.

## Explicit Non-Closure

This task does not implement manual AP bill coverage, bill printing/export, case receipt posting, collection statistics, frontend bill UI, or any additional canonical cases.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_x.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_noncase_bill_handler.py`
- `tasks/automation/SKEL-COVERAGE-PY-X-015-NONCASE-BILL-01.md`
- `artifacts/SKEL-COVERAGE-PY-X-015-NONCASE-BILL-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_x.py tests/test_x_noncase_bill_handler.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_x_noncase_bill_handler.py tests/test_x_case_query_handler.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py --json`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-X-015-NONCASE-BILL-01`

## Evidence Path

- `artifacts/SKEL-COVERAGE-PY-X-015-NONCASE-BILL-01/**`

## Remaining Follow-Up Task IDs

- Additional canonical real-handler coverage tasks for W0/C/D/E/F/G/G0/H/X waves.

## Done Definition

- `TC-X-015` is no longer marked with `@skeleton_case`.
- `TC-X-015` creates a manual bill without a `case_id`.
- `TC-X-015` verifies bill detail and bill item rows remain non-case scoped.
- Coverage audit reduces `cases_without_real_handler_count` by one.
- Required evidence and task gate pass.
