# A-AUTO-PY-A-CASE-CREATE-P0-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement only the pytest-side `TC-A-001` P0 API smoke for A wave minimal case creation:

- `handle_tc_a_001` logs in through the existing runtime API client.
- It reads skeleton data assets for `DS-CL-001`, `DS-AP-001`, `DS-CN`, and `DS-U-FM-01`.
- It resolves the country alias `DS-CN` to real country code `CN`.
- It ensures a run-scoped client and applicant exist through real APIs when they are not found.
- It creates a run-scoped minimal case through `POST /cases`.
- It verifies list/detail API visibility and optional read-only DB assertions for `t_case` and `t_case_applicant`.
- It removes `@skeleton_case` only from `handle_tc_a_001`.

## Explicit Non-Closure

- Do not implement any W0 handler or alter completed W0 handlers.
- Do not implement `TC-A-002` through `TC-A-027`.
- Do not modify testcase IDs, handler registry keys, YAML, JSON, schemas, Playwright, real backend, or real frontend code.
- Do not extend shared `ApiClient`, `DbAssert`, or `SeedCatalog` capabilities.
- Do not write to DB except through real API calls required for the run-scoped client, applicant, and case.
- Do not add cleanup, teardown, duplicate-case negative tests, or downstream A-wave flows.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-CASE-DUPLICATE-P0-01

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-CASE-CREATE-P0-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_create_handler.py`
- `artifacts/A-AUTO-PY-A-CASE-CREATE-P0-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack && python3 scripts/validate_assets.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_asset_integrity.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_auth_client_smoke.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_db_assert.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_helpers_runid_enum.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_seed_data.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_create_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_a.py -k TC-A-001 -q`
- Real smoke, only after backend health is confirmed, with a fresh `FPMS_RUN_ID` and `FPMS_DB_DSN=`.

## Evidence Path

- `artifacts/A-AUTO-PY-A-CASE-CREATE-P0-01/`
