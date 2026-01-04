# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Update ONLY the single target file specified by the task
- Align docs with MVP1 scope and current repo structure
- If any statement conflicts with current code or authoritative scope (docs/00_mvp1_scope.md), scope wins


# DOC-FIX-02 — Update tasks/backend/README.md to include Phase 3.5

## Target File (EXACTLY ONE)
- `tasks/backend/README.md`

## Purpose
Ensure implementers do not miss Phase 3.5 Business Logic tasks.

## Required Edits (Authoritative)
1) Execution order list MUST include (in order):
   1) `tasks/backend/db_bootstrap_ext/` (if needed)
   2) `tasks/backend/models_from_migrations/`
   3) `tasks/backend/apis/`
   4) `tasks/backend/apis_ext/`
   5) `tasks/backend/business_logic/`

2) Add a section: "Phase 3.5 (MVP1 Required)"
Include bullets:
- Bill print `.docx` rendering via docxtpl (GET /bills/{id}/print)
- Task sheet `.docx` rendering (GET /tasks/{id}/print)
- Document → Task auto-generation after document create (OA trigger)

3) Keep existing deprecated-task guidance unchanged unless it contradicts current repo structure.

## Done Criteria
- `tasks/backend/README.md` clearly points to Phase 3.5 directory and the three MVP1 capabilities.
