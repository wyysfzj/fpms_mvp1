# Universal Atomic Execution Prompt (v2) — ENH-01-09 (FPMS MVP1)

You are a coding agent executing **exactly ONE** atomic task.

## Task File (Authoritative)
- `tasks/backend/mvp1enhance/ENH-01-09.md`

## Goal
Implement proper `require_perm` integration for user role-based permission checking.

## Hard Rules (MUST FOLLOW)
- Execute **ONLY ENH-01-09**.
- Do **NOT** introduce new dependencies.
- Do **NOT** modify any migrations or database schema.

## Allowed Files (Strict Allowlist)
- `backend/app/modules/auth/dependencies.py` (modify the `require_perm` function)

## Required Steps
1) Modify the `require_perm` function in `dependencies.py` to integrate with `T_RolePerm`.
2) The `require_perm` function should query `T_RolePerm` and check if the user has the required permission based on their role.

## Verification (MUST RUN)
```bash
cd backend
ruff check app/modules/auth/dependencies.py
ruff format app/modules/auth/dependencies.py
python3 -m py_compile app/modules/auth/dependencies.py
cd ..
```

## Evidence Required
Provide:
- Command outputs from running `ruff check`, `ruff format`, and `python3 -m py_compile` for `auth/dependencies.py`.
- `git diff` showing only the changes in `app/modules/auth/dependencies.py`.
- Test evidence for the `require_perm` functionality.

## Completion Criteria
Task is DONE only if:
- The `require_perm` function is correctly integrated with `T_RolePerm`.
- Permission checks work correctly.
- All tests pass.

## STOP Contract
STOP immediately if:
- You need to modify any file outside `auth/dependencies.py`.
- The functionality is not correctly integrated or fails any verification.
