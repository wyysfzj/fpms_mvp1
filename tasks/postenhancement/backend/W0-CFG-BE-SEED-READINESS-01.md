# W0-CFG-BE-SEED-READINESS-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Close only the backend seed/config readiness audit endpoint for `TC-W0-CFG-014`: add a read-only `GET /api/v1/system/config-readiness` API that reports counts and missing required configuration across existing system parameter, fee rate, commission rule, template, letterhead, country, department, doc template, and task template tables.

## Explicit Non-Closure Statement

This task does not seed data, does not add migrations, does not modify frontend code, does not implement fee/commission/template CRUD behavior, and does not add pytest or Playwright Skeleton Pack handlers.

## Remaining Follow-Up Task IDs

- `tasks/automation/W0-CFG-PY-RBAC-SEED-UI-01.md`
- `tasks/automation/W0-CFG-PY-FEE-RATES-01.md`
- `tasks/automation/W0-CFG-PY-COMMISSION-01.md`
- `tasks/automation/W0-CFG-PY-TEMPLATES-01.md`

## Allowed Files

- `tasks/postenhancement/backend/W0-CFG-BE-SEED-READINESS-01.md`
- `backend/app/modules/system/schemas.py`
- `backend/app/modules/system/service.py`
- `backend/app/modules/system/api.py`
- `backend/tests/test_system_params.py`
- `artifacts/W0-CFG-BE-SEED-READINESS-01/**`

## Verification Commands

```bash
cd backend && python3 -m ruff check --fix app/modules/system/schemas.py app/modules/system/service.py app/modules/system/api.py tests/test_system_params.py
cd backend && python3 -m ruff format app/modules/system/schemas.py app/modules/system/service.py app/modules/system/api.py tests/test_system_params.py
cd backend && python3 -m ruff check app/modules/system/schemas.py app/modules/system/service.py app/modules/system/api.py tests/test_system_params.py
cd backend && python3 -m pytest tests/test_system_params.py -q
./scripts/task_validate.sh W0-CFG-BE-SEED-READINESS-01
```

## Evidence Path

- `artifacts/W0-CFG-BE-SEED-READINESS-01/results.jsonl`
- `artifacts/W0-CFG-BE-SEED-READINESS-01/summary.md`
- `artifacts/W0-CFG-BE-SEED-READINESS-01/git/diff.patch`
