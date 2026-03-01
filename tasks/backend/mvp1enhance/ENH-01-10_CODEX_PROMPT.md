# Universal Atomic Execution Prompt (v2) — ENH-01-10 (FPMS MVP1)

You are a coding agent executing **exactly ONE** atomic task.

## Task File (Authoritative)
tasks/backend/mvp1enhance/ENH-01-10.md

## Goal
Create the **dev seed script** to initialize default roles and permissions, ensuring that the `seed_default_roles_perms` function is called to seed the `T_RolePerm` table.

## Hard Rules (MUST FOLLOW)
- Modify **ONLY** the `backend/scripts/seed_dev.py` file.
- Do **NOT** modify `api.py`, `models.py`, or any other files.
- Ensure the script calls `seed_default_roles_perms(db)` and that the roles and permissions are seeded correctly.

## Allowed Files (Strict Allowlist)
- `backend/scripts/seed_dev.py`

## Required Steps
1) In `backend/scripts/seed_dev.py`, create a script that:
   - Imports `seed_default_roles_perms`.
   - Calls `seed_default_roles_perms(db)` to seed default roles and permissions.
   
2) The script should use `db` (SQLAlchemy session) to interact with the database.

3) Ensure the script can be run multiple times without issues (idempotent).

## Verification (MUST RUN)
```bash
cd backend
ruff check backend/scripts/seed_dev.py
ruff format backend/scripts/seed_dev.py
python3 -m py_compile backend/scripts/seed_dev.py
cd ..
```

Evidence Required
-----------------

Provide:

*   Command outputs from running `ruff check`, `ruff format`, and `python3 -m py_compile` for `seed_dev.py`.
*   `git diff` showing only the changes in `backend/scripts/seed_dev.py`.
*   Ensure the script runs successfully and the default roles and permissions are seeded correctly.

Completion Criteria
-------------------

Task is DONE only if:

*   `seed_dev.py` correctly calls `seed_default_roles_perms` and seeds default roles and permissions.
*   The script is idempotent, meaning it can be run multiple times without errors.
*   The script passes all validation checks (`ruff check`, `ruff format`, `python3 -m py_compile`).

STOP Contract
-------------

STOP immediately if:

*   You need to modify any file outside `seed_dev.py`.
*   The script does not correctly seed the roles and permissions.
