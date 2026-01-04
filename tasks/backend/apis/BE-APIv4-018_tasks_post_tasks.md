# BE-APIv4-018_tasks_post_tasks — tasks POST /tasks

## Design references
- `tasks/docs/task_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/tasks/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `POST /tasks`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `POST`
- Path: `/tasks`
- Expected HTTP status: `201`

## Permission (Unified)
- Required permission: `Task.Create`
- Enforce via: `require_perm("Task.Create")`

## Request example
```json
{}
```

## Response example (HTTP 201)
```json
{
  "id": "string",
  "case_id": "string",
  "document_id": "string",
  "task_template_id": "string",
  "title": "text",
  "base_date": "2025-01-01"
}
```

## Validation commands
```bash
cd backend
ruff check .
python -m py_compile app/modules/tasks/api.py
```

### Curl example (expected HTTP 201)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}' "http://localhost:8000/api/v1/tasks"
```

## Prompt
In `backend/app/modules/tasks/api.py`, implement ONLY the endpoint `POST /tasks` according to `tasks/docs/task_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Task.Create")`.
- Use existing ORM models and services only.
- Return HTTP 201 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
