# A-AUTO-PY-A-CASE-INVALID-COMBO-P1-03

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: low
- evidence_cost: low

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Update the stale skeleton-state assertion in `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py` so the TC-A-003 regression test reflects that `handle_tc_a_004` is now implemented while `handle_tc_a_005` remains skeleton.

## Explicit Non-Closure

- Do not implement or modify any handler.
- Do not modify backend or frontend code.
- Do not modify skeleton data, YAML, JSON, schema, or Playwright assets.
- Do not expand ApiClient, DbAssert, or SeedCatalog.
- Do not change HANDLERS keys or testcase ids.
- Do not mark TC-A-004 as P0.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-CASE-INVALID-COMBO-P1-04-REAL-SMOKE
- A-AUTO-PY-A-FOREIGN-REQUIRED-P0-01

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-CASE-INVALID-COMBO-P1-03.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py`
- `artifacts/A-AUTO-PY-A-CASE-INVALID-COMBO-P1-03/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_duplicate_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_invalid_combo_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_a.py -k TC-A-004 -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_create_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_asset_integrity.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_auth_client_smoke.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_db_assert.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_helpers_runid_enum.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_seed_data.py -q`
- `python3 -m ruff check --fix FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py`
- `python3 -m ruff format FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py`
- `./scripts/task_validate.sh A-AUTO-PY-A-CASE-INVALID-COMBO-P1-03`

## Evidence Path

- `artifacts/A-AUTO-PY-A-CASE-INVALID-COMBO-P1-03/`
