# Final Atomic Execution Prompt — ENH-01-01 (FPMS MVP1, SQLite-safe)

You are a coding agent executing **exactly ONE** atomic task.

---
## Task ID
ENH-01-01

## Authoritative Task File
- `tasks/backend/mvp1enhance/ENH-01-01.md`

Read it fully before writing any code.

---
## Goal (Authoritative Summary)
Add SQLAlchemy model **T_RolePerm** to RBAC models **EXACTLY** as specified in ENH-01-01.md.

This task is **model-definition only**.
- No migrations
- No seeds
- No auth logic changes

---
## Strict Scope (DO NOT VIOLATE)

### Allowed File (ONLY)
- `backend/app/modules/rbac/models.py`

### Explicitly Forbidden
- Alembic migrations (handled by ENH-01-02)
- Any file outside `rbac/models.py`
- Router wiring
- Auth / RBAC behavior changes
- Seed scripts
- Refactoring existing models

If you believe a migration or any other file is required → **STOP and REPORT**.

---
## SQLite PoC Hard Rules (MANDATORY)
You MUST follow these exactly:

- Primary keys: `Integer` with SQLite-compatible autoincrement
- Foreign keys: type must match referenced PK type
- Timestamp defaults: use `CURRENT_TIMESTAMP` (not `now()` / `func.now()`)
- No PostgreSQL-only types or functions
- No `RETURNING` assumptions

Violating any of the above is a **task failure**.

---
## Implementation Requirements (EXACT)

Implement **T_RolePerm** with:
- Correct table name (as per task file)
- Columns exactly as specified:
  - `id`
  - `role_id` (FK to T_Role)
  - `perm_code`
  - `created_at`
- Unique constraint on `(role_id, perm_code)`
  - Constraint name MUST match ENH-01-01.md exactly
- Minimal imports only (do not reorder unrelated imports)
- No relationships unless explicitly specified in task file

Do NOT:
- Add helper methods
- Add relationships unless explicitly required
- Rename existing models or columns

---
## Verification (RUN, but scoped)
From repo root:

```bash
cd backend
ruff check app/modules/rbac/models.py
ruff format app/modules/rbac/models.py
python3 -m py_compile app/modules/rbac/models.py
cd ..
```

Do NOT run ruff on the whole repository.

---
## Evidence Required
Provide:

- Commands executed + outputs
- `git diff` showing **ONLY** changes in `rbac/models.py`
- Confirmation that no migration files were created

---
## Completion Criteria
Task is DONE only if:
- Model matches ENH-01-01.md exactly
- Only the allowed file was modified
- Verification commands pass
- No migrations or seeds were added

---
## STOP Contract
STOP immediately if:
- A migration seems required
- Any file outside allowlist needs modification
- SQLite rules would be violated
- Task file is ambiguous

When STOPPING, report:
- What blocked you
- Why it is out of scope
