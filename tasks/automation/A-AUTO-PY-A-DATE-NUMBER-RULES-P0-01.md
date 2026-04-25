# A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01

**Role:** worker
**Chosen Runbook:** P0-prereq-heavy-story

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## Exact Closure Slice

Implement skeleton pytest-side TC-A-008 date and number consistency rules:

1. `PUBLISHED` missing publication fields rejected with `CASE_PUBLISHED_FIELDS_REQUIRED`.
2. `GRANTED` missing grant fields rejected with `CASE_GRANTED_FIELDS_REQUIRED`.
3. `filing_date` before priority rejected with `CASE_FILING_BEFORE_PRIORITY`.
4. `filing_date` equal earliest priority is accepted.
5. Invalid `app_no` rejected with `CASE_APP_NO_INVALID`.
6. DB disabled/enabled behavior is covered.
7. Stale skeleton-state expectations caused by `handle_tc_a_008` implementation are updated only in allowlisted tests.

## Explicit Non-Closure

- Do not modify backend or frontend application code.
- Do not modify skeleton YAML/JSON/schema/Playwright assets.
- Do not expand `ApiClient`, `DbAssert`, or `SeedCatalog`.
- Do not implement any handler other than `handle_tc_a_008`.
- Do not stretch this task to other A-wave cases.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_date_number_rules_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_applicant_rules_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_create_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_wave_a.py`
- `artifacts/A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01/**`

## Verification Commands

From `FPMS_Automation_Skeleton_Pack/pytest_python`:

- `pytest tests/test_a_date_number_rules_handler.py -q`
- `pytest tests/test_wave_a.py -k TC-A-008 -q`
- `pytest tests/test_a_applicant_rules_handler.py -q`
- `pytest tests/test_a_foreign_required_handler.py -q`
- `pytest tests/test_a_case_create_handler.py -q`
- `pytest tests/test_a_case_duplicate_handler.py -q`
- `pytest tests/test_a_case_invalid_combo_handler.py -q`
- `pytest tests/test_asset_integrity.py -q`
- `pytest tests/test_auth_client_smoke.py -q`
- `pytest tests/test_db_assert.py -q`
- `pytest tests/test_helpers_runid_enum.py -q`
- `pytest tests/test_seed_data.py -q`
- `python3 -m ruff check --fix FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_date_number_rules_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_applicant_rules_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_create_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `python3 -m ruff format FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_date_number_rules_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_applicant_rules_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_create_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_date_number_rules_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_applicant_rules_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_create_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- Real smoke:
  `cd FPMS_Automation_Skeleton_Pack/pytest_python && FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_USERNAME=admin FPMS_PASSWORD="$FPMS_LOCAL_PASSWORD" FPMS_RUN_ID=LOCAL-RUN-ADATE-P01-001 FPMS_DB_DSN= pytest tests/test_wave_a.py -k TC-A-008 -q`

## Evidence Path

- `artifacts/A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01/**`

## Done Definition

- `handle_tc_a_008` is implemented and no longer skeleton.
- TC-A-008 offline pytest coverage passes.
- Real smoke passes against the live backend.
- Scoped Ruff checks pass on the allowlisted files.
- Task gate passes.
- Evidence artifacts are written under the task evidence path.
