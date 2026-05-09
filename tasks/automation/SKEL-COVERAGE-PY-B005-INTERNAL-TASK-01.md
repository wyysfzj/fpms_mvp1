# SKEL-COVERAGE-PY-B005-INTERNAL-TASK-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Convert `TC-B-005` from skeleton to a real pytest handler for B3 internal preparation tasks.

The handler must create an OA incoming document context, capture the official OA reply task, create a separate manual internal preparation task, assign worker/supervisor responsibility, update the task remark, assert task logs include create/assign evidence, and assert the official OA reply task is not changed by the internal task workflow.

## Explicit Non-Closure

This task does not implement UI automation, does not add new backend behavior, does not change task service logging semantics, does not cover other B-wave handlers, and does not convert other skeleton canonical cases.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_b.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_b_partial_landing_handlers.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_b_remaining_landing_handlers.py`
- `tasks/automation/SKEL-COVERAGE-PY-B005-INTERNAL-TASK-01.md`
- `artifacts/SKEL-COVERAGE-PY-B005-INTERNAL-TASK-01/**`

## Verification

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_b.py tests/test_b_partial_landing_handlers.py tests/test_b_remaining_landing_handlers.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_b_partial_landing_handlers.py tests/test_b_remaining_landing_handlers.py tests/test_wave_b.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-B005-INTERNAL-TASK-01`

## Remaining Follow-up Task IDs

- Additional canonical real-handler coverage tasks for C/D/E/F/G/G0/H/W0/X waves.

## Done Definition

- `TC-B-005` is no longer marked with `@skeleton_case`.
- Handler source references real task create/assign/update/log APIs.
- B-wave landing tests reflect that no B handler remains skeleton-only.
- Coverage audit reduces `cases_without_real_handler_count` by one.
- Required evidence and task gate pass.
