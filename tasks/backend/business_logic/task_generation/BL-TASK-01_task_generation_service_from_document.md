# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Follow design docs in `docs/*.md` and project conventions in `docs/04_backend_architecture.md`
- If a task conflicts with an authoritative design doc, the design doc wins


# BL-TASK-01 — TaskGenerationService: generate tasks from a Document (minimal OA trigger)

## Purpose
Implement MVP1 minimal business logic: when a document is registered (IN direction) and is an Office Action (OA),
auto-generate docket tasks based on existing `T_TaskTemplate` rules.

Design references:
- `docs/00_mvp1_scope.md` (case → documents → deadline tasks)
- `docs/04_backend_architecture.md` (service.py business logic)
- `docs/03_database_mvp1_subset.md` (T_TaskTemplate, T_Task, T_TaskLog)

## Output (EXACTLY ONE FILE)
Create ONE new file:
- `backend/app/modules/tasks/task_generation_service.py`

## Preconditions
- ORM models exist for Document, TaskTemplate, Task, TaskLog (names may differ).
- You must inspect existing ORM/model locations and import them correctly.

## Required Interface (Authoritative)
Implement:

```python
class TaskGenerationService:
    def generate_from_document(self, db, document) -> list:
        ...
```

Rules:
- `db` is an active SQLAlchemy Session.
- `document` is an ORM instance.
- Returns list of created Task ORM instances (may be empty).

## Matching Rule (Authoritative)
A TaskTemplate matches a document if:
1) Document is incoming:
   - `document.flow_dir` (or equivalent) indicates IN; OR
   - `document.direction` indicates IN.
   Use the existing field(s) on Document model.
2) Document type equals template trigger:
   - Use TaskTemplate field that represents the trigger doc type (commonly `trigger_doc_type` or `doc_type`).
3) If document lacks required fields (case_id/doc_date), return empty list.

Due date rule:
- Due date = `document.doc_date + offset_days`
- Where `offset_days` is from TaskTemplate field representing due offset (commonly `offset_days`/`due_offset_days`).
- If offset field missing, raise RuntimeError with detail "TaskTemplate missing offset_days mapping" (do not silently default).

Task creation rule:
- Create Task with:
  - `case_id` from document
  - `task_template_id` from matched template
  - `title` from template name/code (use existing fields)
  - `due_date` computed above
  - status initialized to the project’s default (use existing enum/value)

Logging:
- Create a TaskLog entry for each created task with action "AUTO_CREATE_FROM_DOCUMENT" (or existing log action pattern).

Idempotency rule (MVP1):
- Do NOT create duplicate tasks for the same (document_id, task_template_id).
- Implement by checking existing tasks linked to the same document if such field exists; otherwise, check by (case_id, task_template_id, due_date, title) equality.
- If duplicate exists, skip creating that task.

## Done Criteria
1) File imports:
   `PYTHONPATH=backend python -c "from app.modules.tasks.task_generation_service import TaskGenerationService; print('OK')"`
2) Unit-level manual test in REPL can create tasks for a mock document with matching templates.
