# Universal Atomic Execution Prompt (v2) — ENH-01-05 (FPMS MVP1)

You are a coding agent executing **exactly ONE** atomic task.

## Task File (Authoritative)
- `tasks/backend/mvp1enhance/ENH-01-05.md`

## Goal
Create the Pydantic schemas for auth endpoints:
- **LoginRequest**: Schema for login requests (username and password).
- **TokenResponse**: Schema for token response (access token).
- **MeResponse**: Schema for the "me" endpoint response (current user data).


## Hard Rules (MUST FOLLOW)
- Execute **ONLY ENH-01-05**.
- Modify ONLY the allowlisted files.
- Do NOT introduce new dependencies.
- Do NOT touch migrations or database schema.

## Allowed Files (Strict Allowlist)
- `backend/app/modules/auth/schemas.py`ONLY

If any other file is required, STOP and report.

## Required Steps
1) **Create Pydantic schemas**:
   - **LoginRequest**: For login requests with `username` and `password`.
     - Required fields: `username: str`, `password: str`.
   - **TokenResponse**: For responses containing the generated `access_token`.
     - Required fields: `access_token: str`, `token_type: str` (e.g., `bearer`).
   - **MeResponse**: For returning user profile data.
     - Required fields: `user_id: str`, `name: str`, `email: str`, `permissions: List[str]`.

2) Ensure proper validation of the fields, including any necessary constraints (e.g., string lengths, format).

## Verification (MUST RUN)
```bash
cd backend
ruff check app/modules/auth/schemas.py
ruff format app/modules/auth/schemas.py
python3 -m py_compile app/modules/auth/schemas.py
cd ..
```

## Evidence Required
Provide:
- Command outputs
- `git diff` showing only the allowed file changes
- Test evidence for the schemas
- Any test evidence that shows the schemas correctly validate the user data.
  
## Completion Criteria

Task is DONE only if:

Pydantic schemas are correctly defined and validated.

The schemas are properly tested and pass all tests.

The LoginRequest, TokenResponse, and MeResponse schemas are properly implemented.

STOP Contract

## STOP Contract
STOP if:
- You need to modify any file outside allowlist
