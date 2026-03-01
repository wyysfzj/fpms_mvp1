# Universal Atomic Execution Prompt (v2) — ENH-01-21 (FPMS MVP1)

You are a coding agent executing exactly ONE atomic task.

## Task File (Authoritative)
tasks/backend/mvp1enhance/ENH-01-21.md

## Goal
Add `jwt_expire_minutes: int = 60` to Settings so auth/login does not crash.

## Hard Rules
- Execute ONLY ENH-01-21.
- Modify ONLY backend/app/core/config.py.
- Do NOT touch auth/api.py, router.py, migrations, DB, seed, or any other files.
- No new dependencies.

## Allowed Files (Strict Allowlist)
- backend/app/core/config.py ONLY

If any other file is required: STOP and report.

## Required Steps
1) Add `jwt_expire_minutes: int = 60` to the Settings class.
2) Keep default value 60.
3) Run validation commands.

## Validation (MUST RUN)
```bash
./scripts/evidence_run.sh ENH-01-21 lint bash -lc "cd backend && ruff check app/core/config.py"
./scripts/evidence_run.sh ENH-01-21 fmt  bash -lc "cd backend && ruff format app/core/config.py"
./scripts/evidence_run.sh ENH-01-21 test bash -lc "cd backend && python3 -m py_compile app/core/config.py"
./scripts/evidence_finalize.sh ENH-01-21
./scripts/task_validate.sh ENH-01-21
```

## Runtime Evidence (MUST PROVIDE)
```bash
curl -i -X POST http://localhost:8000/api/v1/auth/login   -H "Content-Type: application/json"   -d '{"username":"admin","password":"admin123"}'
```

Expected:
- NOT 500 AttributeError
- Response may be 200 / 401 / 400 depending on seed

## STOP Contract
STOP if you need to modify any file outside config.py.
