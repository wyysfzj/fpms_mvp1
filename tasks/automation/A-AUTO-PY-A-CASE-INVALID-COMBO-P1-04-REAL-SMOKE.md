# A-AUTO-PY-A-CASE-INVALID-COMBO-P1-04-REAL-SMOKE

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: low
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Run and record the real backend smoke for `TC-A-004`, verifying that the implemented `handle_tc_a_004` reaches the real `/api/v1/cases` endpoint and the backend rejects `SEARCH + DES` with `CASE_TYPE_COMBO_INVALID`.

## Explicit Non-Closure

- Do not implement or modify any handler.
- Do not modify pytest test code.
- Do not modify backend or frontend code.
- Do not modify skeleton data, YAML, JSON, schema, or Playwright assets.
- Do not expand ApiClient, DbAssert, or SeedCatalog.
- Do not change HANDLERS keys or testcase ids.
- Do not mark `TC-A-004` as P0.
- Do not treat offline skip as real smoke PASS.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-FOREIGN-REQUIRED-P0-01
- ENV-LOCAL-BACKEND-SMOKE-01 if local backend remains unavailable
- A-AUTO-PY-A-CASE-INVALID-COMBO-P1-05-FIX if pytest assertion needs a follow-up adjustment
- BE-A-CASE-COMBO-RULE-FIX-01 if the real backend rule regresses

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-CASE-INVALID-COMBO-P1-04-REAL-SMOKE.md`
- `artifacts/A-AUTO-PY-A-CASE-INVALID-COMBO-P1-04-REAL-SMOKE/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_invalid_combo_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_duplicate_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_a.py -k TC-A-004 -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_asset_integrity.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_auth_client_smoke.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_db_assert.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_helpers_runid_enum.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_seed_data.py -q`
- `curl -sS http://127.0.0.1:8000/healthz`
- `curl -sS http://127.0.0.1:8000/openapi.json`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_USERNAME=admin FPMS_PASSWORD="$FPMS_LOCAL_PASSWORD" FPMS_RUN_ID=LOCAL-RUN-AINVCOMBO-SMOKE-001 FPMS_DB_DSN= pytest tests/test_wave_a.py -k TC-A-004 -q`
- `./scripts/task_validate.sh A-AUTO-PY-A-CASE-INVALID-COMBO-P1-04-REAL-SMOKE`

## Evidence Path

- `artifacts/A-AUTO-PY-A-CASE-INVALID-COMBO-P1-04-REAL-SMOKE/`
