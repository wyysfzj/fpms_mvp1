# W0-AUTO-PY-DB-ASSERT-01

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## Runbook

- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Implement the minimum read-only database assertion foundation for the skeleton pytest runtime:

- `DbAssert` connects to SQLite/PostgreSQL DSNs through SQLAlchemy.
- Empty DSN keeps DB assertions disabled with clear errors if query methods are called.
- `fetch_one`, `fetch_all`, `assert_row_exists`, and `assert_count` support parameterized read-only checks.
- Table and column identifiers are strictly validated before SQL assembly.
- Local SQLite unit tests cover the behavior without requiring the real business database.

## Explicit Non-Closure Statement

This task does not implement W0/A testcase handlers, does not remove skeleton markers, does not modify YAML/JSON/schema assets, does not modify Playwright, does not modify real business frontend/backend code, does not implement seed helpers, does not implement RUN_ID/enum helpers, does not write to a business database, and does not run migrations.

## Remaining Follow-Up Task IDs

- `W0-AUTO-PY-RUNID-ENUM-01`
- `W0-AUTO-PY-SEED-HELPER-01`
- `W0-AUTO-PW-AUTH-FIXTURE-01`
- `A-AUTO-PY-CASECREATE-001`

## Allowed Files

```text
tasks/automation/W0-AUTO-PY-DB-ASSERT-01.md
FPMS_Automation_Skeleton_Pack/pytest_python/framework/db_assert.py
FPMS_Automation_Skeleton_Pack/pytest_python/framework/runtime.py
FPMS_Automation_Skeleton_Pack/pytest_python/conftest.py
FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_db_assert.py
FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_db_assert_smoke.py
artifacts/W0-AUTO-PY-DB-ASSERT-01/**
```

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack
python3 scripts/validate_assets.py
```

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python
pytest tests/test_asset_integrity.py -q
pytest tests/test_auth_client_smoke.py -q
pytest tests/test_db_assert.py -q
```

## Evidence Path

```text
artifacts/W0-AUTO-PY-DB-ASSERT-01/**
```
