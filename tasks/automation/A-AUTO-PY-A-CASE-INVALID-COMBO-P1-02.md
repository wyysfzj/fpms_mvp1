# A-AUTO-PY-A-CASE-INVALID-COMBO-P1-02

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement only skeleton pytest handler coverage for `TC-A-004` after the real backend rule was added by `BE-A-CASE-COMBO-RULE-01`.

The handler must submit an illegal `SEARCH + DES` case payload to `/cases`, assert `400 CASE_TYPE_COMBO_INVALID`, and assert that the negative case was not persisted when DB assertions are enabled.

## Explicit Non-Closure

- Do not implement any W0 handler.
- Do not roll back `handle_tc_a_001` or `handle_tc_a_003`.
- Do not implement `TC-A-002` or `TC-A-005` through `TC-A-027`.
- Do not modify testcase IDs, manifests, YAML, JSON, schemas, Playwright, real backend, or real frontend code.
- Do not extend `ApiClient`, `DbAssert`, or `SeedCatalog`.
- Do not use duplicate case number, invalid enum, missing field, permission failure, or backend unavailable skip as the illegal-combination assertion.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-FOREIGN-REQUIRED-P0-01

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-CASE-INVALID-COMBO-P1-02.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `artifacts/A-AUTO-PY-A-CASE-INVALID-COMBO-P1-02/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack && python3 scripts/validate_assets.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_asset_integrity.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_auth_client_smoke.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_db_assert.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_helpers_runid_enum.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_seed_data.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_create_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_duplicate_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_invalid_combo_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_a.py -k TC-A-004 -q`
- `./scripts/task_validate.sh A-AUTO-PY-A-CASE-INVALID-COMBO-P1-02`

## Evidence Path

- `artifacts/A-AUTO-PY-A-CASE-INVALID-COMBO-P1-02/`
