# Copilot/Codex Task List

## Atomic Task Rules (MUST READ)

1. One task = one file = one responsibility.
2. Task scope MUST be deterministic. No conditional language is allowed.
3. Design documents are the single source of truth.
4. Task prompt MUST fully enumerate fields / behavior.
5. If a task conflicts with design docs, follow the design docs.

## Prerequisite (DB)
Before executing backend tasks, ensure DB migrations are applied.

- Reference: `backend/docs/db_migrations_overview.md`

### SQLite (PoC)
```bash
cd backend
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

## How to execute
- Run tasks in order (00 → ...). Each task contains:
  - Target files
  - Acceptance criteria
  - Ready-to-paste prompt text for Copilot/Codex
- Keep the generated code consistent with:
  - `docs/*`
  - `backend/app/modules/**/docs/*`
  - `frontend/src/modules/**/docs/*`

## Task sets
- `backend_tasks.md`
- `frontend_tasks.md`
- `backend_tasks_atomic.md` (recommended for Copilot continuous generation)
- `frontend_tasks_atomic.md` (recommended for Copilot continuous generation)
- `integration_tasks.md`
