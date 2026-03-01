# Universal Atomic Execution Prompt (v2) — ENH-01-08 (FPMS MVP1)

You are a coding agent executing **exactly ONE** atomic task.

## Task File (Authoritative)
- `tasks/backend/mvp1enhance/ENH-01-08.md`

## Goal
Implement `GET /auth/me` endpoint to retrieve current user information.

## Hard Rules (MUST FOLLOW)
- Execute **ONLY ENH-01-08**.
- Do **NOT** introduce new dependencies.
- Do **NOT** modify any migrations or database schema.
- Do **NOT** change any existing behavior of the `require_perm` or `auth` logic.

## Allowed Files (Strict Allowlist)
- `backend/app/modules/auth/api.py` (add route and handler)

## Required Steps
1) Implement the `GET /auth/me` endpoint.
2) The endpoint should validate the incoming JWT token.
3) The endpoint should return the current user's information: `user_id`, `name`, `email`, and `permissions`.
4) The response should match the format defined in `MeResponse` schema.

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
- Test evidence for the `GET /auth/me` endpoint.

## Completion Criteria
Task is DONE only if:
- The `GET /auth/me` endpoint is correctly implemented.
- The user info is correctly returned.
- All tests pass.

## STOP Contract
STOP immediately if:
- You need to modify any file outside `auth/api.py`.
- The functionality is not correctly implemented or fails any verification.
