# A-AUTO-PY-A-APPLY-FEE-LIMIT-P0-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Implement only TC-A-013 / `handle_tc_a_013`: arrange submitted case, locate APPLY_FEE_LIMIT task, assert base date, due/internal date fields, OPEN status, and create log.

## Explicit Non-Closure

Do not implement fee draft, pay list, bill, payment, commission handlers, backend code, frontend code, or skeleton data changes.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-APPLY-FEE-DRAFT-P0-01

## Allowed Files

- tasks/automation/A-AUTO-PY-A-APPLY-FEE-LIMIT-P0-01.md
- FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
- FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_apply_fee_limit_handler.py
- artifacts/A-AUTO-PY-A-APPLY-FEE-LIMIT-P0-01/**

## Verification Commands

- cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_apply_fee_limit_handler.py -q
- cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_a.py -k TC-A-013 -q
- cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_a.py tests/test_a_apply_fee_limit_handler.py
- ./scripts/task_validate.sh A-AUTO-PY-A-APPLY-FEE-LIMIT-P0-01

## Evidence Path

- artifacts/A-AUTO-PY-A-APPLY-FEE-LIMIT-P0-01/
