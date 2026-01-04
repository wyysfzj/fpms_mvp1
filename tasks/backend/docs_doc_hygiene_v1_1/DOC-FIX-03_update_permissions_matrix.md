# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Update ONLY the single target file specified by the task
- Align docs with MVP1 scope and current repo structure
- If any statement conflicts with current code or authoritative scope (docs/00_mvp1_scope.md), scope wins


# DOC-FIX-03 — Update docs/permissions_matrix.md for Phase 3-EXT and Phase 3.5

## Target File (EXACTLY ONE)
- `docs/permissions_matrix.md`

## Purpose
Align permissions matrix with:
- Phase 3-EXT endpoints (apis_ext)
- Phase 3.5 endpoints (business_logic)

## Required Edits (Authoritative)

### A) Add/ensure these permission codes exist (exact spelling)
- `AdminUser.Read`
- `AdminUser.Create`
- `AdminUser.Edit`
- `SystemParam.Read`
- `SystemParam.Edit`
- `Template.Read`
- `Template.Create`
- `LetterHead.Read`
- `LetterHead.Create`

### B) Endpoint mappings (must be explicit)
Add mapping entries (or update existing) for:
- `Bill.Print` → `GET /bills/{id}/print`
- `Task.Read` → `GET /tasks/{id}/print`  (MVP1 uses Task.Read for print)

### C) Naming convention note
If the file contains mixed naming, normalize to Title.Action and include a short note that this is MVP1 convention.

## Done Criteria
- The matrix lists all new codes and maps Bill/Task print endpoints correctly.
