# Universal Atomic Execution Prompt (v2) — ENH-01-03 (FPMS MVP1)

You are a coding agent executing **exactly ONE** atomic task.

## Task File (Authoritative)
- `tasks/backend/mvp1enhance/ENH-01-03.md`

## Goal
Implement service layer logic for getting user permissions by their role (and/or permission codes).

## Hard Rules (MUST FOLLOW)
- Modify ONLY the allowlisted files.
- Do NOT introduce new dependencies.
- Do NOT touch migrations or database schema.

## Allowed Files (Strict Allowlist)
- `backend/app/modules/rbac/services.py` (create the service function)

## Required Steps
1) Implement a service function called `get_user_permissions` that takes a `role_id` (and optionally a `user_id`) and returns a list of permissions.
2) The function should query `t_role_perm` based on the provided `role_id` and return `perm_code`.
3) The function should return the permissions list (as an array of strings).

## Verification (MUST RUN)
```bash
cd backend
ruff check app/modules/rbac/services.py
ruff format app/modules/rbac/services.py
python3 -m py_compile app/modules/rbac/services.py
cd ..

## Evidence Required

Provide:

Command outputs (ruff + py_compile)

git diff showing only the allowed file changes

Confirmation that get_user_permissions works correctly for permissions retrieval

## Validation commands
cd backend
./scripts/evidence_run.sh ENH-01-03 lint bash -lc "cd backend && ruff check app/modules/rbac/services.py"
./scripts/evidence_run.sh ENH-01-03 fmt bash -lc "cd backend && ruff format app/modules/rbac/services.py"
./scripts/evidence_run.sh ENH-01-03 test bash -lc "cd backend && python3 -m py_compile app/modules/rbac/services.py"
./scripts/evidence_finalize.sh ENH-01-03
./scripts/task_validate.sh ENH-01-03

## STOP Contract

STOP if:

You need to modify any file outside the allowlist

