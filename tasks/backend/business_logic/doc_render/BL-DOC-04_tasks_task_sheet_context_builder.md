# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Follow design docs in `docs/*.md` and project conventions in `docs/04_backend_architecture.md`
- If a task conflicts with an authoritative design doc, the design doc wins


# BL-DOC-04 — Tasks: TaskSheetContextBuilder (dict context)

## Purpose
Create a context builder for printing a single task sheet as a `.docx`.

Design references:
- `docs/00_mvp1_scope.md` (task sheet output)
- `docs/04_backend_architecture.md` (context builders)

## Output (EXACTLY ONE FILE)
Create ONE new file:
- `backend/app/modules/tasks/doc_render_task_sheet_context.py`

## Preconditions
- ORM models for Task exist and are importable.

## Required Interface (Authoritative)
Implement:

```python
class TaskSheetContextBuilder:
    def build(self, task, case, client) -> dict:
        ...
```

Rules:
- Inputs are ORM instances loaded by caller.
- No DB queries in builder.

## Required Context Keys (Minimum)
- `task` (dict)
- `case` (dict or None)
- `client` (dict or None)

Include at minimum:
- task id/title/status/due_date/worker/supervisor
- case case_no/title
- client name/code

## Done Criteria
`PYTHONPATH=backend python -c "from app.modules.tasks.doc_render_task_sheet_context import TaskSheetContextBuilder; print('OK')"`
