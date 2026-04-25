# A-AUTO-PY-A-FOREIGN-REQUIRED-P0-02-TEST-MAINT

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: low
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Update stale skeleton-state expectations in existing A handler regression tests after `TC-A-005` was implemented, then run `TC-A-005` real backend smoke if the local backend is reachable.

Current expected A handler state:

- `handle_tc_a_001`: implemented
- `handle_tc_a_002`: skeleton
- `handle_tc_a_003`: implemented
- `handle_tc_a_004`: implemented
- `handle_tc_a_005`: implemented
- `handle_tc_a_006`: skeleton

## Explicit Non-Closure

- Do not implement or edit any handler.
- Do not modify `wave_a.py`.
- Do not implement `TC-A-006`, `TC-A-007`, `TC-A-008`, or any other testcase.
- Do not modify backend or frontend code.
- Do not modify skeleton data, YAML, JSON, schema, or Playwright assets.
- Do not expand ApiClient, DbAssert, or SeedCatalog.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-APPLICANT-RULES-P0-01
- A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01
- BE-A-APPLICANT-RULES-01 if backend applicant-kind rules are missing
- BE-A-DATE-NUMBER-RULES-01 if backend date/number rules are missing
- ENV-LOCAL-BACKEND-SMOKE-01 if local backend real smoke is unavailable

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-FOREIGN-REQUIRED-P0-02-TEST-MAINT.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `artifacts/A-AUTO-PY-A-FOREIGN-REQUIRED-P0-02-TEST-MAINT/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_duplicate_handler.py tests/test_a_case_invalid_combo_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_foreign_required_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_a.py -k TC-A-005 -q`
- `python3 -m ruff check --fix FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `python3 -m ruff format FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_USERNAME=admin FPMS_PASSWORD="$FPMS_LOCAL_PASSWORD" FPMS_RUN_ID=LOCAL-RUN-AFOREIGN-MAINT-001 FPMS_DB_DSN= pytest tests/test_wave_a.py -k TC-A-005 -q`
- `./scripts/task_validate.sh A-AUTO-PY-A-FOREIGN-REQUIRED-P0-02-TEST-MAINT`

## Evidence Path

- `artifacts/A-AUTO-PY-A-FOREIGN-REQUIRED-P0-02-TEST-MAINT/`
