# SKEL-COVERAGE-PY-X-013-OFFSET-REVERSE-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Convert canonical `TC-X-013` from skeleton to a real pytest handler covering payment offset reversal through `/offsets/{offset_id}/reverse`, including bill/payment balance restoration and duplicate-reverse rejection.

## Explicit Non-Closure

This task does not implement reversal time-window enforcement, role-specific permission matrix checks, frontend offset UI, or any additional canonical cases.

## Allowed Files

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_x.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_x_offset_reverse_handler.py`
- `tasks/automation/SKEL-COVERAGE-PY-X-013-OFFSET-REVERSE-01.md`
- `artifacts/SKEL-COVERAGE-PY-X-013-OFFSET-REVERSE-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_x.py tests/test_x_offset_reverse_handler.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_x_offset_reverse_handler.py tests/test_x_case_query_handler.py -q`
- `python3 FPMS_Automation_Skeleton_Pack/scripts/audit_current_coverage.py --json`
- `./scripts/task_validate.sh SKEL-COVERAGE-PY-X-013-OFFSET-REVERSE-01`

## Evidence Path

- `artifacts/SKEL-COVERAGE-PY-X-013-OFFSET-REVERSE-01/**`

## Remaining Follow-Up Task IDs

- Additional canonical real-handler coverage tasks for W0/C/D/E/F/G/G0/H/X waves.

## Done Definition

- `TC-X-013` is no longer marked with `@skeleton_case`.
- `TC-X-013` creates an offset from a payment line to a manual bill.
- `TC-X-013` reverses the offset and verifies `is_reversed=true`.
- `TC-X-013` verifies bill and payment line balances are restored.
- `TC-X-013` verifies duplicate reverse is rejected.
- Coverage audit reduces `cases_without_real_handler_count` by one.
- Required evidence and task gate pass.
