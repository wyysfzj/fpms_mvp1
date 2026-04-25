# W0-AUTO-PY-RUNID-ENUM-01

## Story Shape Classification

- `shared_file_density: high`
- `prereq_dependency_density: high`
- `be_fe_coupling: medium`
- `evidence_cost: medium`

## Runbook

- `chosen_runbook: P0-prereq-heavy-story`
- Role: worker

## Exact Closure Slice

Implement the skeleton pytest-side pure helper base for RUN_ID-derived dynamic values and real-system enum normalization:

- Add stable `unique_code(prefix, run_id, suffix=None)` behavior.
- Add country, case type, patent category, flow direction, and case status normalization helpers.
- Add `normalize_payload_enums(payload)` for currently known payload fields only.
- Add task-scoped unit tests for the helper behavior.

## Explicit Non-Closure

This task does not implement any `TC-W0-*` or `TC-A-*` handler, remove any `@skeleton_case`, change testcase ids, modify YAML/JSON/schema assets, touch Playwright, modify real backend/frontend code, add seed helpers, add API client endpoint wrappers, extend DB assertions, write to business databases, run migrations, or expand outside W0/A prerequisite helper work.

## Remaining Follow-Up Task IDs

- `W0-AUTO-PY-SEED-HELPER-01`
- `W0-AUTO-PY-W0-CLIENT-P0-01`
- `W0-AUTO-PY-A-CASE-MIN-P0-01`

## Allowed Files

- `tasks/automation/W0-AUTO-PY-RUNID-ENUM-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/framework/helpers.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/framework/runtime.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/conftest.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_helpers_runid_enum.py`
- `artifacts/W0-AUTO-PY-RUNID-ENUM-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack
python3 scripts/validate_assets.py

cd FPMS_Automation_Skeleton_Pack/pytest_python
pytest tests/test_asset_integrity.py -q
pytest tests/test_auth_client_smoke.py -q
pytest tests/test_db_assert.py -q
pytest tests/test_helpers_runid_enum.py -q
pytest tests/test_asset_integrity.py tests/test_auth_client_smoke.py tests/test_db_assert.py tests/test_helpers_runid_enum.py -q
```

Task gate:

```bash
./scripts/task_validate.sh W0-AUTO-PY-RUNID-ENUM-01
```

## Evidence Path

- `artifacts/W0-AUTO-PY-RUNID-ENUM-01/results.jsonl`
- `artifacts/W0-AUTO-PY-RUNID-ENUM-01/summary.md`
- `artifacts/W0-AUTO-PY-RUNID-ENUM-01/git/diff.patch`
- `artifacts/W0-AUTO-PY-RUNID-ENUM-01/baseline_allowlist.diff`
- `artifacts/W0-AUTO-PY-RUNID-ENUM-01/baseline_external_files.txt`
