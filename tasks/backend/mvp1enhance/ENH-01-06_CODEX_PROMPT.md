# Universal Atomic Execution Prompt (v2) — ENH-01-06 (FPMS MVP1)

You are a coding agent executing **exactly ONE** atomic task.

## Task File (Authoritative)
- `tasks/backend/mvp1enhance/ENH-01-06.md`

## Goal
Implement a permission-checking service to verify if a user has the appropriate permissions based on their role.

## Hard Rules (MUST FOLLOW)
- Execute **ONLY ENH-01-06**.
- Do **NOT** introduce new dependencies.
- Do **NOT** modify any migrations or database schema.
- Do **NOT** change authentication / authorization logic.

## Allowed Files (Strict Allowlist)
- `backend/app/modules/rbac/service.py` (add service function)

## Required Steps
1) Implement a service function called `check_user_permission` that:
   - Takes `user_id` and `permission_code` as input.
   - Returns `True` if the user has the specified permission, `False` otherwise.

2) The function should query the `T_RolePerm` table based on the user's roles and check if any of the permissions associated with the user's roles match the given `permission_code`.

3) If the user has the permission, return `True`; otherwise, return `False`.

## Verification (MUST RUN)
```bash
cd backend
ruff check app/modules/rbac/service.py
ruff format app/modules/rbac/service.py
python3 -m py_compile app/modules/rbac/service.py
cd ..
```

## Evidence Required
Provide:
- Command outputs from running `ruff check`, `ruff format`, and `python3 -m py_compile` for `rbac/service.py`.
- `git diff` showing only the changes in `app/modules/rbac/service.py`.
- Any test evidence that shows the function works correctly for checking user permissions.

## Completion Criteria
Task is DONE only if:
- The `check_user_permission` service function is correctly implemented and validated.
- The function returns the correct permission check result.
- The service function is properly tested and passing all tests.

## STOP Contract
STOP immediately if:
- You need to modify any file outside `rbac/service.py`.
- The function is not correctly checking user permissions.
