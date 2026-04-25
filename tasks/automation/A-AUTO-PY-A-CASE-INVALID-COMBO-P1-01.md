# A-AUTO-PY-A-CASE-INVALID-COMBO-P1-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## Runbook

- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Assess and, only if supported by the real system, implement the pytest-side `TC-A-004` case type / patent category invalid-combination negative chain.

Current execution found no real backend rule or stable API error for the skeleton-expected invalid combination behavior, so the automation closure is blocked and the handler remains skeleton.

## Explicit Non-Closure

- Do not implement or modify any W0 handler.
- Do not roll back `handle_tc_a_001` or `handle_tc_a_003`.
- Do not implement `TC-A-002` or `TC-A-005` through `TC-A-027`.
- Do not remove `@skeleton_case` from `handle_tc_a_004` unless the real invalid-combination rule exists.
- Do not modify YAML, JSON, schemas, Playwright, real backend, or real frontend code.
- Do not fake an invalid-combination pass with a different validation failure.

## Remaining Follow-Up Task IDs

- BE-A-CASE-COMBO-RULE-01

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-CASE-INVALID-COMBO-P1-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_case_invalid_combo_handler.py`
- `artifacts/A-AUTO-PY-A-CASE-INVALID-COMBO-P1-01/**`

## Verification Commands

- `cd FPMS_Automation_Skeleton_Pack && python3 scripts/validate_assets.py`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_asset_integrity.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_auth_client_smoke.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_db_assert.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_helpers_runid_enum.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_seed_data.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_create_handler.py -q`
- `cd FPMS_Automation_Skeleton_Pack/pytest_python && pytest tests/test_a_case_duplicate_handler.py -q`
- Task gate and evidence validation for the BLOCKED decision.

## Evidence Path

- `artifacts/A-AUTO-PY-A-CASE-INVALID-COMBO-P1-01/`
