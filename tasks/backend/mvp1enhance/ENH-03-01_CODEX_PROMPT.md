
# Universal Atomic Execution Prompt (v2) — ENH-03-01 (FPMS MVP1)

You are a coding agent executing **exactly ONE** atomic task.

## Task File (Authoritative)
tasks/backend/mvp1enhance/ENH-03-01.md

## Goal
# ENH-03-01 — Define Case Schema and Validation

Define Pydantic schemas for the case creation and validation in the `schemas.py` file, ensuring data validation for fields such as `case_no`, `client_id`, `case_type`, etc.

## Hard Rules (MUST FOLLOW)
- Modify **ONLY** the appropriate files related to this task.
- Do **NOT** modify any other files outside the scope of this task.

## Allowed Files (Strict Allowlist)
- Modify files as per task description.

## Required Steps
1) Follow the task description to implement the required functionality.
2) Ensure the code passes all validation checks.
3) If applicable, run necessary tests to verify the functionality.

## Verification (MUST RUN)
```bash
cd backend
ruff check backend/
ruff format backend/
python3 -m py_compile backend/
cd ..
```

Evidence Required
-----------------

Provide:

*   Command outputs from running `ruff check`, `ruff format`, and `python3 -m py_compile` for the modified files.
*   `git diff` showing only the changes relevant to this task.

Completion Criteria
-------------------

Task is DONE only if:

*   The task requirements are fully implemented and validated.
*   Code passes all checks and tests.

STOP Contract
-------------

STOP immediately if:

*   You need to modify files outside the scope of this task.
*   The task requirements are not met.

