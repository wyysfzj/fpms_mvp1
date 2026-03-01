
# Universal Atomic Execution Prompt (v2) — ENH-02-05-01 (FPMS MVP1)

You are a coding agent executing **exactly ONE** atomic task.

## Task File (Authoritative)
- `tasks/backend/mvp1enhance/ENH-02-05-01.md`

## Goal
Define or restore the `CaseCreateIn` schema in `schemas.py` to resolve the `ImportError` in the `POST /api/v1/cases` endpoint.

## Hard Rules (MUST FOLLOW)
- Modify **ONLY `schemas.py`** to define or fix the `CaseCreateIn` schema.
- Do **NOT** modify any other files outside `schemas.py`.

## Allowed Files (Strict Allowlist)
- `backend/app/modules/cases/schemas.py`

## Required Steps
1) In `schemas.py`, define the `CaseCreateIn` schema, including:
   - The required fields for case creation (e.g., `case_no`, `client_id`, `case_type`).
   - Validation using **Pydantic**.
   
2) Ensure that the schema is used for validation in the `POST /api/v1/cases` endpoint.

## Verification (MUST RUN)
```bash
cd backend
ruff check app/modules/cases/schemas.py
ruff format app/modules/cases/schemas.py
python3 -m py_compile app/modules/cases/schemas.py
cd ..
```

Evidence Required
-----------------

Provide:

- Command outputs from running `ruff check`, `ruff format`, and `python3 -m py_compile` for `schemas.py`.
- `git diff` showing only the changes in `schemas.py`.
- Ensure the import of `CaseCreateIn` in `api.py` works correctly.

Completion Criteria
-------------------

Task is DONE only if:

- The `CaseCreateIn` schema is correctly defined in `schemas.py`.
- The import error is resolved in `api.py`.
- Code passes all validation checks.

STOP Contract
-------------

STOP immediately if:

- You need to modify any file outside `schemas.py`.
- The import error is not resolved or the schema is not correctly defined.
