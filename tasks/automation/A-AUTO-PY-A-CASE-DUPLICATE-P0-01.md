# A-AUTO-PY-A-CASE-DUPLICATE-P0-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement only the pytest-side `TC-A-003` P0 duplicate case number negative API smoke:

- Login through the existing runtime API client.
- Use skeleton data semantics for `CASE-A-${RUN_ID}-001`.
- Ensure the baseline case exists without calling `handle_tc_a_001`.
- Attempt a second `POST /cases` with the same `case_no`.
- Assert duplicate case number semantics from the real API response.
- Assert the API list still contains exactly one matching case.
- Run optional read-only DB count assertion only when `runtime.db.enabled()`.
- Remove `@skeleton_case` only from `handle_tc_a_003`.

## Explicit Non-Closure

- Do not implement or modify any W0 handler.
- Do not roll back `handle_tc_a_001`.
- Do not implement `TC-A-002` or `TC-A-004` through `TC-A-027`.
- Do not modify testcase IDs, handler registry keys, YAML, JSON, schemas, Playwright, real backend, or real frontend code.
- Do not extend shared `ApiClient`, `DbAssert`, or `SeedCatalog` capabilities.
- Do not add cleanup, teardown, invalid-combo, complete-case, batch filing, billing, payment, or commission flows.

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-CASE-INVALID-COMBO-P0-01

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-CASE-DUPLICATE-P0-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_duplicate_handler.py`
- `artifacts/A-AUTO-PY-A-CASE-DUPLICATE-P0-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack && python3 scripts/validate_assets.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_asset_integrity.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_auth_client_smoke.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_db_assert.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_helpers_runid_enum.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_seed_data.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_create_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_duplicate_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_wave_a.py -k TC-A-003 -q`
- Real smoke, only after backend health is confirmed, with a fresh `FPMS_RUN_ID` and `FPMS_DB_DSN=`.

## Evidence Path

- `artifacts/A-AUTO-PY-A-CASE-DUPLICATE-P0-01/`
