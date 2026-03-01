# Final Atomic Execution Prompt — ENH-01-01 (FPMS MVP1, UUID/TEXT PK approved)

You are a coding agent executing **exactly ONE** atomic task.

---
## Task ID
ENH-01-01

## Authoritative Task File
- `tasks/backend/mvp1enhance/ENH-01-01.md`

## Decision Reference (Authoritative)
- `docs/decisions/DECISION-ENH-01-01-UUID-PK.md`

This decision resolves the conflict between the task spec (UUID PK) and the SQLite PK preference in AGENTS.

---
## Goal (Authoritative Summary)
Add SQLAlchemy model **T_RolePerm** to RBAC models **EXACTLY** as specified in ENH-01-01.md, using **UUID/TEXT PK** generated in application code.

This task is **model-definition only**.
- No migrations (ENH-01-02 handles migrations)
- No seeds
- No RBAC behavior changes

---
## Strict Scope (DO NOT VIOLATE)

### Allowed File (ONLY)
- `backend/app/modules/rbac/models.py`

### Explicitly Forbidden
- Alembic migrations (handled by ENH-01-02)
- Any file outside `rbac/models.py`
- Router wiring
- Auth/RBAC behavior changes
- Seed scripts
- Refactoring existing models

If you believe a migration or any other file is required → **STOP and REPORT**.

---
## SQLite PoC Hard Rules (MANDATORY, as applied here)
- UUID PK is allowed for this table per decision document:
  - Store as TEXT (`String(36)` or equivalent)
  - Generate UUID in application code (`uuid4()`), not DB-side
- Foreign key types MUST match referenced PK types exactly.
- Timestamp defaults: `CURRENT_TIMESTAMP` (SQLite-safe). Do NOT use `now()` / `func.now()`.
- No PostgreSQL-only types/functions.
- No RETURNING assumptions.

---
## Implementation Requirements (EXACT)
Implement **T_RolePerm** with:
- Table name and columns exactly as per ENH-01-01.md
- `id`: UUID/TEXT PK per spec and decision
- `role_id`: FK to `T_Role` with type exactly matching `T_Role.id`
- `perm_code`: per spec
- `created_at`: SQLite-safe default
- Unique constraint on `(role_id, perm_code)` with the exact constraint name in task

Do NOT add relationships unless explicitly required by ENH-01-01.md.

---
## Verification (RUN, scoped)
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
- Command outputs
- `git diff` showing ONLY changes in `rbac/models.py`
- Confirmation that no migration files were created

---
## Completion Criteria
Task is DONE only if:
- Model matches ENH-01-01.md exactly
- Decision constraints are satisfied (UUID/TEXT PK, FK type alignment)
- Only the allowed file was modified
- Verification commands pass

---
## STOP Contract
STOP if:
- Any file outside allowlist needs modification
- FK typing cannot be aligned without touching other models
- Task file is ambiguous or conflicts with the decision
