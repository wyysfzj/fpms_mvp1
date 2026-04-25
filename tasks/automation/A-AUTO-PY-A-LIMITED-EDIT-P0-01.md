# A-AUTO-PY-A-LIMITED-EDIT-P0-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement only TC-A-010 / `handle_tc_a_010` limited-edit automation.

This task closes only:

1. Arrange a legal baseline case with valid applicant prerequisites.
2. Use a run-scoped Agent user carrying `Case.EditLimited`.
3. Assert limited-edit whitelist fields persist.
4. Assert blacklist fields do not mutate through limited-edit.
5. Assert regular full edit is forbidden for the limited user.
6. Assert status/task/fee side effects are not created.
7. Update stale TC-A-010 skeleton expectations only in allowlisted tests.

## Explicit Non-Closure

Do not implement other handlers, backend/frontend behavior, skeleton YAML/JSON/schema changes, Playwright, or notes/remarks persistence.

## Remaining Follow-Up Task IDs

- BATCH-A-WAVE-CLOSE-AUDIT-01

## Allowed Files

- tasks/automation/A-AUTO-PY-A-LIMITED-EDIT-P0-01.md
- FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
- FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_limited_edit_handler.py
- FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_foreign_combo_handler.py
- FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_minimal_required_handler.py
- FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_spec_fee_discount_handler.py
- artifacts/A-AUTO-PY-A-LIMITED-EDIT-P0-01/**

## Verification Commands

Run from `FPMS_Automation_Skeleton_Pack/pytest_python`:

```bash
pytest tests/test_a_limited_edit_handler.py -q
pytest tests/test_wave_a.py -k TC-A-010 -q
pytest tests/test_a_foreign_combo_handler.py -q
pytest tests/test_a_minimal_required_handler.py -q
pytest tests/test_a_spec_fee_discount_handler.py -q
pytest tests/test_asset_integrity.py -q
pytest tests/test_auth_client_smoke.py -q
pytest tests/test_db_assert.py -q
pytest tests/test_helpers_runid_enum.py -q
pytest tests/test_seed_data.py -q
```

Real smoke:

```bash
FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_USERNAME=admin FPMS_PASSWORD="$FPMS_LOCAL_PASSWORD" FPMS_RUN_ID=LOCAL-RUN-ALIMITED-001 FPMS_DB_DSN= pytest tests/test_wave_a.py -k TC-A-010 -q
```

## Evidence Path

- artifacts/A-AUTO-PY-A-LIMITED-EDIT-P0-01/results.jsonl
- artifacts/A-AUTO-PY-A-LIMITED-EDIT-P0-01/summary.md
- artifacts/A-AUTO-PY-A-LIMITED-EDIT-P0-01/git/diff.patch
