# W0-AUTO-PY-W0-FEERATE-P0-01

## Story Shape Classification

- `shared_file_density: high`
- `prereq_dependency_density: high`
- `be_fe_coupling: medium`
- `evidence_cost: medium`

## Runbook

- `chosen_runbook: P0-prereq-heavy-story`
- Role: worker

## Exact Closure Slice

Implement only the skeleton pytest-side `TC-W0-007` fixed application fee-rate chain:

- Use existing `runtime.api` auth to log in.
- Use existing `SeedCatalog` and `unique_code` to derive run-scoped fee codes from `DS-RATE-001` and `DS-RATE-002`.
- Create two fixed APPLY fee rates through the real `/fees/rates` API.
- Assert each created fee rate through `/fees/rates` filtered by `fee_code`.
- Run optional read-only DB assertions against `t_fee_rate` when `runtime.db.enabled()` is true.
- Remove `@skeleton_case` only from `handle_tc_w0_007`.

## Explicit Non-Closure

This task does not implement `TC-W0-001`, does not modify the completed client handler, does not implement `TC-W0-002` through `TC-W0-006`, does not implement `TC-W0-008` through `TC-W0-014`, does not implement any `TC-A-*`, does not modify YAML/JSON/schema assets, does not modify Playwright, does not modify real backend/frontend code, does not extend `ApiClient`, `DbAssert`, `SeedCatalog`, or router behavior, does not add cleanup/teardown, does not implement templates/permissions/A-wave fee drafts, and does not write to the business database except through the real API calls needed for this two-rate slice.

## Remaining Follow-Up Task IDs

- `W0-AUTO-PY-W0-TEMPLATE-P0-01`
- `W0-AUTO-PY-W0-PERMISSION-P0-01`
- `W0-AUTO-PY-A-CASE-MIN-P0-01`

## Allowed Files

- `tasks/automation/W0-AUTO-PY-W0-FEERATE-P0-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_fee_rate_handler.py`
- `artifacts/W0-AUTO-PY-W0-FEERATE-P0-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack
python3 scripts/validate_assets.py

cd FPMS_Automation_Skeleton_Pack/pytest_python
pytest tests/test_asset_integrity.py -q
pytest tests/test_auth_client_smoke.py -q
pytest tests/test_db_assert.py -q
pytest tests/test_helpers_runid_enum.py -q
pytest tests/test_seed_data.py -q
pytest tests/test_w0_client_handler.py -q
pytest tests/test_w0_fee_rate_handler.py -q
pytest tests/test_wave_w0.py -k TC-W0-007 -q

FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_USERNAME=admin FPMS_PASSWORD=<set-locally> FPMS_RUN_ID=LOCAL-RUN-001 pytest tests/test_wave_w0.py -k TC-W0-007 -q
```

Task gate:

```bash
./scripts/task_validate.sh W0-AUTO-PY-W0-FEERATE-P0-01
```

## Evidence Path

- `artifacts/W0-AUTO-PY-W0-FEERATE-P0-01/results.jsonl`
- `artifacts/W0-AUTO-PY-W0-FEERATE-P0-01/summary.md`
- `artifacts/W0-AUTO-PY-W0-FEERATE-P0-01/git/diff.patch`
- `artifacts/W0-AUTO-PY-W0-FEERATE-P0-01/baseline_allowlist.diff`
- `artifacts/W0-AUTO-PY-W0-FEERATE-P0-01/baseline_external_files.txt`
