# W0-AUTO-PY-W0-CLIENT-P0-01

## Story Shape Classification

- `shared_file_density: high`
- `prereq_dependency_density: high`
- `be_fe_coupling: medium`
- `evidence_cost: medium`

## Runbook

- `chosen_runbook: P0-prereq-heavy-story`
- Role: worker

## Exact Closure Slice

Implement only the skeleton pytest-side `TC-W0-001` client master-data chain:

- Use existing `runtime.api` auth to log in.
- Use existing `SeedCatalog` and `unique_code` to derive a run-scoped `DS-CL-001` client payload.
- Create one client through the real `/clients` API.
- Create two client addresses through `/clients/{client_id}/addresses`.
- Create one client contact through `/clients/{client_id}/contacts`.
- Assert the created client, addresses, and contact through API reads.
- Run optional read-only DB assertions when `runtime.db.enabled()` is true.
- Remove `@skeleton_case` only from `handle_tc_w0_001`.

## Explicit Non-Closure

This task does not implement `TC-W0-002` through `TC-W0-014`, any `TC-A-*`, any Playwright work, any real backend/frontend changes, any YAML/JSON/schema changes, any API client extension, any DB assert extension, cleanup/teardown, fee-rate/template/permission scenarios, migrations, or writes outside the real API calls needed for this client/address/contact slice.

## Remaining Follow-Up Task IDs

- `W0-AUTO-PY-W0-FEERATE-P0-01`
- `W0-AUTO-PY-W0-DOCTEMPLATE-P0-01`
- `W0-AUTO-PY-A-CASE-MIN-P0-01`

## Allowed Files

- `tasks/automation/W0-AUTO-PY-W0-CLIENT-P0-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_client_handler.py`
- `artifacts/W0-AUTO-PY-W0-CLIENT-P0-01/**`

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
pytest tests/test_wave_w0.py -k TC-W0-001 -q
pytest tests/test_asset_integrity.py tests/test_auth_client_smoke.py tests/test_db_assert.py tests/test_helpers_runid_enum.py tests/test_seed_data.py tests/test_w0_client_handler.py -q
```

Task gate:

```bash
./scripts/task_validate.sh W0-AUTO-PY-W0-CLIENT-P0-01
```

## Evidence Path

- `artifacts/W0-AUTO-PY-W0-CLIENT-P0-01/results.jsonl`
- `artifacts/W0-AUTO-PY-W0-CLIENT-P0-01/summary.md`
- `artifacts/W0-AUTO-PY-W0-CLIENT-P0-01/git/diff.patch`
- `artifacts/W0-AUTO-PY-W0-CLIENT-P0-01/baseline_allowlist.diff`
- `artifacts/W0-AUTO-PY-W0-CLIENT-P0-01/baseline_external_files.txt`
