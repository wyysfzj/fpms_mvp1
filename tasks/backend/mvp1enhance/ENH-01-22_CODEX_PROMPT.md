# Universal Atomic Execution Prompt (v2) — ENH-01-22 (FPMS MVP1)

You are a coding agent executing exactly ONE atomic task.

## Task File (Authoritative)
tasks/backend/mvp1enhance/ENH-01-22.md

## Goal
Implement `get_current_user` and `require_perm` functions for user authentication and authorization.

## Hard Rules
- Execute ONLY ENH-01-22.
- Modify ONLY backend/app/core/dependencies.py.
- Do NOT touch `auth/api.py`, `router.py`, migrations, DB, or any other files.
- No new dependencies.

## Allowed Files (Strict Allowlist)
- backend/app/core/dependencies.py ONLY

If any other file is required: STOP and report.

## Required Steps
1) Implement `get_current_user` to retrieve the authenticated user from the database.
2) Implement `require_perm` to check if the user has the necessary permission based on permission code.
3) Integrate these functions into FastAPI endpoints to handle authentication and authorization.
4) Run validation commands to ensure the code is correct.

## Validation (MUST RUN)
```bash
./scripts/evidence_run.sh ENH-01-22 lint bash -lc "cd backend && ruff check app/core/dependencies.py"
./scripts/evidence_run.sh ENH-01-22 fmt  bash -lc "cd backend && ruff format app/core/dependencies.py"
./scripts/evidence_run.sh ENH-01-22 test bash -lc "cd backend && python3 -m py_compile app/core/dependencies.py"
./scripts/evidence_finalize.sh ENH-01-22
./scripts/task_validate.sh ENH-01-22
```

## Runtime Evidence (MUST PROVIDE)
```bash
curl -i -X GET http://localhost:8000/protected-resource -H "Authorization: Bearer <token>"
```

Expected:
- If the user is authenticated, the resource is accessible.
- If the user is not authenticated, a 404 error is returned.
- If the user does not have the required permission, a 403 error is returned.

## STOP Contract
STOP if you need to modify any file outside `dependencies.py`.
