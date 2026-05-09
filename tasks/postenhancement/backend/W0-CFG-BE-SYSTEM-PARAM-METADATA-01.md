# W0-CFG-BE-SYSTEM-PARAM-METADATA-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: low

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Close only the backend API metadata gap for `TC-W0-CFG-001`: `GET /api/v1/system/params` must include existing `description`, `created_at`, and `updated_at` fields while preserving secret value masking and existing permission behavior.

## Explicit Non-Closure Statement

This task does not modify frontend code, does not add new system parameter storage fields, does not change permission codes, does not add migrations, does not implement pytest/Playwright Skeleton Pack handlers, and does not alter unrelated system endpoints.

## Remaining Follow-Up Task IDs

- `tasks/postenhancement/frontend/W0-CFG-FE-SYSTEM-PARAMS-01.md`
- `tasks/automation/W0-CFG-PY-SYSTEM-PARAMS-01.md`

## Allowed Files

- `tasks/postenhancement/backend/W0-CFG-BE-SYSTEM-PARAM-METADATA-01.md`
- `backend/app/modules/system/schemas.py`
- `backend/app/modules/system/api.py`
- `backend/tests/test_system_params.py`
- `artifacts/W0-CFG-BE-SYSTEM-PARAM-METADATA-01/**`

## Verification Commands

```bash
cd backend && python3 -m ruff check --fix app/modules/system/schemas.py app/modules/system/api.py tests/test_system_params.py
cd backend && python3 -m ruff format app/modules/system/schemas.py app/modules/system/api.py tests/test_system_params.py
cd backend && python3 -m ruff check app/modules/system/schemas.py app/modules/system/api.py tests/test_system_params.py
cd backend && python3 -m pytest tests/test_system_params.py -q
./scripts/task_validate.sh W0-CFG-BE-SYSTEM-PARAM-METADATA-01
```

## Evidence Path

- `artifacts/W0-CFG-BE-SYSTEM-PARAM-METADATA-01/results.jsonl`
- `artifacts/W0-CFG-BE-SYSTEM-PARAM-METADATA-01/summary.md`
- `artifacts/W0-CFG-BE-SYSTEM-PARAM-METADATA-01/git/diff.patch`
