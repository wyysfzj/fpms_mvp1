# Universal Atomic Execution Prompt (v2) — ENH-00-12 (FPMS MVP1)

You are a coding agent executing **exactly ONE** atomic task.

## Task File (Authoritative)
- `tasks/backend/mvp1enhance/ENH-00-12.md`

## Goal
Fix global RequestValidationError handling so invalid request bodies return HTTP 422 (not 500).
Root cause: main.py builds ErrorResponse with details=exc.errors() (list), but ErrorDetail.details is dict|None. Wrap the list in a dict.

## Hard Rules
- Execute ONLY ENH-00-12.
- Modify ONLY the allowlisted file.
- Do NOT change errors.py types.
- Do NOT change routers/endpoints, auth/RBAC, DB schema/migrations/seed.
- Keep existing response envelope conventions; do NOT invent a new envelope.

## Allowed Files (Strict Allowlist)
- `backend/app/main.py` ONLY

If any other file seems required, STOP and report.

## Required Change (EXACT)
In the RequestValidationError handler (e.g., `validation_error_handler`), replace:
- `details=exc.errors()`
with:
- `details={"errors": exc.errors()}`

Ensure status code remains 422.

## Verification (MUST RUN)
```bash
cd backend
ruff check app/main.py
ruff format app/main.py
python3 -m py_compile app/main.py
cd ..
```

## Runtime Evidence (MUST PROVIDE)
```bash
curl -i -X POST http://localhost:8000/api/v1/cases   -H "Content-Type: application/json"   -H "Authorization: Bearer $FPMS_TOKEN"   -d '{"invalid":"data"}'
```
Expected: HTTP/1.1 422 and JSON response body; details is dict with `errors` key.

## Required Agent Output
- Task executed
- Files modified (must be ONLY backend/app/main.py)
- Verification results
- Curl evidence

## STOP Contract
STOP if scope expansion is required.
