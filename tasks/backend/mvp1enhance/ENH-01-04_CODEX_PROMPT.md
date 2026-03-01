# Universal Atomic Execution Prompt (v2) — ENH-01-04 (FPMS MVP1)

You are a coding agent executing **exactly ONE** atomic task.

## Task File (Authoritative)
- `tasks/backend/mvp1enhance/ENH-01-04.md`

## Goal
Implement service layer function to seed default roles and permissions into the database.

## Hard Rules (MUST FOLLOW)
- Modify ONLY the allowlisted files.
- Do NOT introduce new dependencies.
- Do NOT touch migrations or database schema.

## Allowed Files (Strict Allowlist)
- `backend/app/modules/rbac/services.py` (create the service function)

## Required Steps
1) Implement a service function called `seed_default_roles_perms`.
2) The function should create default roles (e.g., Admin, User) and assign them the appropriate permissions (e.g., `Role.Create`, `Role.Read`).
3) The function should use the existing `T_RolePerm` model for storing role-permission mappings.

## Verification (MUST RUN)
```bash
cd backend
ruff check app/modules/rbac/services.py
ruff format app/modules/rbac/services.py
python3 -m py_compile app/modules/rbac/services.py
cd ..
```

## Evidence Required
Provide:
- Command outputs
- `git diff` showing only the allowed file changes
- Test evidence for the function

## Validation Commands
```bash
cd backend
./scripts/evidence_run.sh ENH-01-04 lint bash -lc "cd backend && ruff check app/modules/rbac/services.py"
./scripts/evidence_run.sh ENH-01-04 fmt bash -lc "cd backend && ruff format app/modules/rbac/services.py"
./scripts/evidence_run.sh ENH-01-04 test bash -lc "cd backend && python3 -m py_compile app/modules/rbac/services.py"
./scripts/evidence_finalize.sh ENH-01-04
./scripts/task_validate.sh ENH-01-04


## STOP Contract
STOP if:
- You need to modify any file outside allowlist
