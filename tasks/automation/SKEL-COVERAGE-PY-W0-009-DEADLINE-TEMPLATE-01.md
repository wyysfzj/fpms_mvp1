# SKEL-COVERAGE-PY-W0-009-DEADLINE-TEMPLATE-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Convert canonical `TC-W0-009` from skeleton to a real handler by reusing the existing `TC-W0-CFG-008` deadline-template and linked document-template coverage slice.

## Explicit Non-Closure

This task does not add deadline-template backend behavior, does not implement additional unhappy-path validations beyond the existing CFG slice, does not touch UI automation, and does not convert any other W0 skeleton case.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_task_deadline_template_handler.py`
- `tasks/automation/SKEL-COVERAGE-PY-W0-009-DEADLINE-TEMPLATE-01.md`
- `artifacts/SKEL-COVERAGE-PY-W0-009-DEADLINE-TEMPLATE-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_w0.py tests/test_w0_task_deadline_template_handler.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_w0_task_deadline_template_handler.py tests/test_wave_w0.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-W0-009-DEADLINE-TEMPLATE-01`

## Remaining Follow-up Task IDs

- Additional canonical real-handler coverage tasks for W0/C/D/E/F/G/G0/H/X waves.

## Done Definition

- `TC-W0-009` is no longer marked with `@skeleton_case`.
- `TC-W0-009` executes the real deadline-template coverage flow.
- Coverage audit reduces `cases_without_real_handler_count` by one.
- Required evidence and task gate pass.
