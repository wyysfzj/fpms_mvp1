# A-AUTO-PY-A-COMMISSION-P0-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Implement only TC-A-023 / `handle_tc_a_023`: arrange SERVICE fee bill and agent split, create NORMAL commission rule, and assert two commission rows with 70/30 split and settleable initial flags.

## Explicit Non-Closure

Do not implement settlement execution, TC-A-024, backend code, frontend code, or skeleton data changes.

## Remaining Follow-Up Task IDs

- BATCH-A-DEPENDENT-UNHAPPY-P0P1-01

## Allowed Files

- tasks/automation/A-AUTO-PY-A-COMMISSION-P0-01.md
- FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
- FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_commission_handler.py
- artifacts/A-AUTO-PY-A-COMMISSION-P0-01/**

## Verification Commands

- cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_commission_handler.py -q
- cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_a.py -k TC-A-023 -q
- cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_a.py tests/test_a_commission_handler.py
- ./scripts/task_validate.sh A-AUTO-PY-A-COMMISSION-P0-01

## Evidence Path

- artifacts/A-AUTO-PY-A-COMMISSION-P0-01/
