# W0-AUTO-PY-SEED-HELPER-01

## Story Shape Classification

- `shared_file_density: high`
- `prereq_dependency_density: high`
- `be_fe_coupling: medium`
- `evidence_cost: medium`

## Runbook

- `chosen_runbook: P0-prereq-heavy-story`
- Role: worker

## Exact Closure Slice

Implement the minimum skeleton pytest-side seed data catalog foundation:

- Load existing YAML and JSON seed assets from `FPMS_Automation_Skeleton_Pack/data/seeds/`.
- Expand `${RUN_ID}` recursively.
- Provide `SeedCatalog.get`, `maybe_get`, `list_by_group`, `country_code`, and `normalized`.
- Reuse existing enum/country normalization helpers instead of duplicating mapping.
- Return defensive copies so callers cannot mutate catalog state.
- Detect conflicting duplicate seed ids with a clear error.

## Explicit Non-Closure

This task does not implement any `TC-W0-*` or `TC-A-*` handler, remove any `@skeleton_case`, change testcase ids, modify YAML/JSON/schema assets, touch Playwright, modify real backend/frontend code, call real APIs, write to a business database, add API endpoint wrappers, extend DB assertions, run migrations, or create W0 master data in the real system.

## Remaining Follow-Up Task IDs

- `W0-AUTO-PY-W0-CLIENT-P0-01`
- `W0-AUTO-PY-W0-FEERATE-P0-01`
- `W0-AUTO-PY-A-CASE-MIN-P0-01`

## Allowed Files

- `tasks/automation/W0-AUTO-PY-SEED-HELPER-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/framework/seed_data.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/framework/data_loader.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_seed_data.py`
- `artifacts/W0-AUTO-PY-SEED-HELPER-01/**`

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
pytest tests/test_asset_integrity.py tests/test_auth_client_smoke.py tests/test_db_assert.py tests/test_helpers_runid_enum.py tests/test_seed_data.py -q
```

Task gate:

```bash
./scripts/task_validate.sh W0-AUTO-PY-SEED-HELPER-01
```

## Evidence Path

- `artifacts/W0-AUTO-PY-SEED-HELPER-01/results.jsonl`
- `artifacts/W0-AUTO-PY-SEED-HELPER-01/summary.md`
- `artifacts/W0-AUTO-PY-SEED-HELPER-01/git/diff.patch`
- `artifacts/W0-AUTO-PY-SEED-HELPER-01/baseline_allowlist.diff`
- `artifacts/W0-AUTO-PY-SEED-HELPER-01/baseline_external_files.txt`
