# A-AUTO-PY-A-BATCH-SUBMIT-P0-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Implement only TC-A-011 / `handle_tc_a_011`: create three valid NOT_FILED domestic cases, submit batch filing with `generate_list=true`, assert status transition, generated document registration, and APPLY_FEE_LIMIT task trigger.

## Explicit Non-Closure

Do not implement TC-A-013 or later handlers. Do not modify backend, frontend, skeleton YAML/JSON/schema/manifest, or Playwright.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-APPLY-FEE-LIMIT-P0-01

## Allowed Files

- tasks/automation/A-AUTO-PY-A-BATCH-SUBMIT-P0-01.md
- FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
- FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_batch_submit_handler.py
- artifacts/A-AUTO-PY-A-BATCH-SUBMIT-P0-01/**

## Verification Commands

- cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_batch_submit_handler.py -q
- cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_a.py -k TC-A-011 -q
- cd FPMS_Automation_Skeleton_Pack/pytest_python && python3 -m ruff check handlers/wave_a.py tests/test_a_batch_submit_handler.py
- ./scripts/task_validate.sh A-AUTO-PY-A-BATCH-SUBMIT-P0-01

## Evidence Path

- artifacts/A-AUTO-PY-A-BATCH-SUBMIT-P0-01/
