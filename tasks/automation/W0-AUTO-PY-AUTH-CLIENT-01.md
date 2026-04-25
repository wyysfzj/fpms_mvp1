# W0-AUTO-PY-AUTH-CLIENT-01

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## Runbook

- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Implement the minimum pytest skeleton API authentication foundation needed to talk to the real FPMS backend:

- `ApiClient` can use the real API base URL.
- `ApiClient.login(username, password)` calls `/auth/login`, stores `access_token`, and returns it.
- Follow-up requests automatically include `Authorization: Bearer <token>`.
- Explicit caller headers are preserved.
- Existing `get/post/put/patch/delete` helper methods remain compatible.
- Runtime pytest configuration defaults to `http://localhost:8000/api/v1` and supports `FPMS_API_URL`, `FPMS_RUN_ID`, `FPMS_USERNAME`, and `FPMS_PASSWORD`.
- Add a task-scoped smoke test for login plus `/auth/me`, skipped when the backend is unavailable.

## Explicit Non-Closure Statement

This task does not implement W0/A testcase handlers, does not remove any skeleton markers, does not modify YAML/JSON/schema assets, does not modify Playwright, does not modify real business frontend/backend code, does not implement DB assertions, and does not implement seed helpers.

## Remaining Follow-Up Task IDs

- `W0-AUTO-PY-DB-ASSERT-01`
- `W0-AUTO-PY-RUNID-ENUM-01`
- `W0-AUTO-PY-SEED-HELPER-01`
- `W0-AUTO-PW-AUTH-FIXTURE-01`
- `A-AUTO-PY-CASECREATE-001`

## Allowed Files

```text
tasks/automation/W0-AUTO-PY-AUTH-CLIENT-01.md
FPMS_Automation_Skeleton_Pack/pytest_python/framework/api_client.py
FPMS_Automation_Skeleton_Pack/pytest_python/framework/runtime.py
FPMS_Automation_Skeleton_Pack/pytest_python/conftest.py
FPMS_Automation_Skeleton_Pack/pytest_python/framework/helpers.py
FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_auth_client_smoke.py
artifacts/W0-AUTO-PY-AUTH-CLIENT-01/**
```

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack
python3 scripts/validate_assets.py
```

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python
pytest tests/test_asset_integrity.py -q
```

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python
FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_USERNAME=admin FPMS_PASSWORD=admin123 pytest tests/test_auth_client_smoke.py -q
```

## Evidence Path

```text
artifacts/W0-AUTO-PY-AUTH-CLIENT-01/**
```
