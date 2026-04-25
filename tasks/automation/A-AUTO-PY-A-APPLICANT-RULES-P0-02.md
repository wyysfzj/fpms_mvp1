# A-AUTO-PY-A-APPLICANT-RULES-P0-02

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement only `TC-A-006` / `handle_tc_a_006` for A1 applicant list rules:

1. no applicants is rejected with `CASE_APPLICANT_REQUIRED`
2. multiple first applicants is rejected with `CASE_DUPLICATE_FIRST_APPLICANT`
3. applicant kind mismatch is rejected with `CASE_APPLICANT_KIND_MISMATCH`
4. corrected applicant kind succeeds
5. DB disabled/enabled behavior is covered
6. stale skeleton-state expectations caused by `handle_tc_a_006` are updated only in the allowlisted tests

## Explicit Non-Closure

- Do not implement `TC-A-008`.
- Do not modify backend code or frontend code.
- Do not modify skeleton YAML, JSON, schema, or Playwright assets.
- Do not expand `ApiClient`, `DbAssert`, or `SeedCatalog`.
- Do not implement any other A-wave handler.
- Do not add non-TC-A-006 behavior to `handle_tc_a_006`.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-APPLICANT-RULES-P0-02.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_applicant_rules_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `artifacts/A-AUTO-PY-A-APPLICANT-RULES-P0-02/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_applicant_rules_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_a.py -k TC-A-006 -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_foreign_required_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_create_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_duplicate_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_invalid_combo_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_asset_integrity.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_auth_client_smoke.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_db_assert.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_helpers_runid_enum.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_seed_data.py -q`
- `python3 -m ruff check --fix FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_applicant_rules_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `python3 -m ruff format FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_applicant_rules_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `python3 -m ruff check FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_applicant_rules_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_required_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `curl -sS http://127.0.0.1:8000/healthz`
- `curl -sS http://127.0.0.1:8000/openapi.json`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_USERNAME=admin FPMS_PASSWORD="$FPMS_LOCAL_PASSWORD" FPMS_RUN_ID=LOCAL-RUN-AAPPLICANT-P02-001 FPMS_DB_DSN= pytest tests/test_wave_a.py -k TC-A-006 -q`
- `./scripts/task_validate.sh A-AUTO-PY-A-APPLICANT-RULES-P0-02`

## Evidence Path

- `artifacts/A-AUTO-PY-A-APPLICANT-RULES-P0-02/`
