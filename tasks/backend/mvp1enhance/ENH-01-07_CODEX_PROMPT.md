# Universal Atomic Execution Prompt (v2) — ENH-01-07 (FPMS MVP1)

You are a coding agent executing **exactly ONE** atomic task.

## Task File (Authoritative)
- `tasks/backend/mvp1enhance/ENH-01-07.md`

## Goal
Implement `POST /auth/login` endpoint for user login, returning an `access_token`.

## Hard Rules (MUST FOLLOW)
- Execute **ONLY ENH-01-07**.
- Do **NOT** introduce new dependencies.
- Do **NOT** modify any migrations or database schema.
- Do **NOT** change any existing behavior of the `require_perm` or `auth` logic.

## Allowed Files (Strict Allowlist)
- `backend/app/modules/auth/api.py` (add route and handler)

## Required Steps
1) Implement the `POST /auth/login` endpoint.
2) The endpoint should accept `username` and `password` fields.
3) It should verify the password against the stored hash using `verify_password`.
4) If successful, generate a JWT token using `create_access_token`.
5) Return the token in the response (`token_type` should be "bearer", `access_token` should be the JWT token).

## Verification (MUST RUN)
```bash
cd backend
ruff check app/modules/auth/api.py
ruff format app/modules/auth/api.py
python3 -m py_compile app/modules/auth/api.py
cd ..
```

## Evidence Required
Provide:
- Command outputs from running `ruff check`, `ruff format`, and `python3 -m py_compile` for `auth/api.py`.
- `git diff` showing only the changes in `app/modules/auth/api.py`.
- Test evidence for the `POST /auth/login` endpoint.

## Completion Criteria
Task is DONE only if:
- The login endpoint is correctly implemented.
- The login flow works as expected (returns JWT token).
- All tests pass.

## STOP Contract
STOP immediately if:
- You need to modify any file outside `auth/api.py`.
- The login functionality is not correctly implemented or fails any verification.
