# FPMS MVP1 — Backend Atomic Tasks (Authoritative)

## Execution Order (Do NOT change)
1) `tasks/backend/db_bootstrap_ext/` (if needed)
2) `tasks/backend/models_from_migrations/`
3) `tasks/backend/apis/`
4) `tasks/backend/apis_ext/`
5) `tasks/backend/business_logic/`

## Phase 3.5 (MVP1 Required)
- Bill print `.docx` rendering via docxtpl (GET /bills/{id}/print)
- Task sheet `.docx` rendering (GET /tasks/{id}/print)
- Document → Task auto-generation after document create (OA trigger)

## Rules
- One task = one file = one responsibility.
- No optional scope inside a task.
- If a task conflicts with a design doc under `backend/app/modules/**/docs`, the design doc wins.
- Phase 3 APIs must not change schema and must rely on existing ORM models only.

## Deprecated Tasks
Root-level coarse-grained tasks that overlap with `models_from_migrations/` are deprecated and must not be executed.
