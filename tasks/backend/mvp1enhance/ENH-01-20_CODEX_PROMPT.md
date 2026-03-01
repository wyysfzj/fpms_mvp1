# Universal Atomic Execution Prompt (v2) — ENH-01-20 (FPMS MVP1)

You are a coding agent executing **exactly ONE** atomic task.

## Task File (Authoritative)
- `tasks/backend/mvp1enhance/ENH-01-20.md`

## Goal
Wire the `auth_router` correctly in `router.py` to ensure that the `POST /auth/login` endpoint is properly registered.

## Hard Rules (MUST FOLLOW)
- Modify **ONLY router.py** to fix the router wiring for `auth_router`.
- Do **NOT** modify `api.py` or add new logic to the existing `POST /auth/login` endpoint.
- Ensure **auth_router** is correctly included in **router.py** with the correct prefix (`/auth`) and tags (`["Auth"]`).

## Allowed Files (Strict Allowlist)
- `backend/app/api/router.py`

## Required Steps
1) In `backend/app/api/router.py`, add the following code to ensure the `auth_router` is included with the correct prefix and tags:
   ```python
   from app.modules.auth.api import router as auth_router

   # Include the auth router with the correct prefix and tags
   router.include_router(auth_router, prefix="/auth", tags=["Auth"])
   ```

2) Ensure the `auth_router` is properly imported from `app/modules/auth/api.py`.
3) Verify that the `/auth/login` endpoint is now accessible via `/api/v1/auth/login`.

## Verification (MUST RUN)
```bash
cd backend
ruff check app/api/router.py
ruff format app/api/router.py
python3 -m py_compile app/api/router.py
cd ..
```

## Evidence Required
Provide:
- Command outputs from running `ruff check`, `ruff format`, and `python3 -m py_compile` for `router.py`.
- `git diff` showing only the changes in `app/api/router.py`.
- Test evidence for the `POST /auth/login` endpoint.

## Completion Criteria
Task is DONE only if:
- The `POST /auth/login` endpoint is correctly registered and functional.
- The `auth_router` is correctly wired with the `/auth` prefix and tags.
- The login flow works as expected and returns the JWT token.

## STOP Contract
STOP immediately if:
- You need to modify any file outside `router.py`.
- The `auth_router` is not properly registered or the login functionality is not working as expected.
