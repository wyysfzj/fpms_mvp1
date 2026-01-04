# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Follow design docs in `docs/*.md` and project conventions in `docs/04_backend_architecture.md`
- If a task conflicts with an authoritative design doc, the design doc wins


# BL-DOC-05 — Add Task print endpoint (GET /tasks/{id}/print) with docxtpl docx download

## Purpose
Add MVP1-required endpoint to print a single task sheet as `.docx` using docxtpl.

Design references:
- `docs/00_mvp1_scope.md`
- `docs/04_backend_architecture.md`
- `docs/permissions_matrix.md` (use `Task.Read` for MVP1 unless a dedicated Task.Print exists)

## Output (EXACTLY ONE FILE)
Edit ONLY:
- `backend/app/modules/tasks/api.py`

## Preconditions
1) `BL-DOC-01` and `BL-DOC-04` completed.
2) A task-sheet template `.docx` path is configured via system param:
   - `task_sheet_template_path` in `t_system_param.param_key`
   If not present, endpoint must return 409 "Task sheet template not configured".

## Endpoint (Authoritative)
- Method: GET
- Path: `/tasks/<built-in function id>/print`
- Permission: `Task.Read`
  (Enforce using lint-safe injection parameter, not decorator dependencies.)

## Required Behavior
1) Load Task by id; if not found => 404.
2) Load related Case and Client if Task has case_id; if not available, keep them None.
3) Resolve template path via system param `task_sheet_template_path`; if missing => 409 with exact detail.
4) Build context using `TaskSheetContextBuilder.build(task, case, client)`.
5) Render `.docx` bytes using `DocxRenderer`.
6) Return download response with correct docx content-type and filename `task_<id>.docx`.

## Done Criteria
1) Endpoint appears in OpenAPI.
2) Calling endpoint with configured template returns a `.docx` download.
3) Missing template param returns 409 with exact detail.
