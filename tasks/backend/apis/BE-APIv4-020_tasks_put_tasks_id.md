# BE-APIv4-020_tasks_put_tasks_id — tasks PUT /tasks/{id}

## Design references
- `tasks/docs/task_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/tasks/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `PUT /tasks/{id}`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `PUT`
- Path: `/tasks/{id}`
- Expected HTTP status: `200`

## Permission (Unified)
- Required permission: `Task.Edit`
- Enforce via: `require_perm("Task.Edit")`

## Request example
```json
{
  "case_id": "string",
  "document_id": "string"
}
```

## Response example (HTTP 200)
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

### Curl example (expected HTTP 200)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -X PUT -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{"case_id": "string", "document_id": "string"}' "http://localhost:8000/api/v1/tasks/REPLACE_ID"
```

## Prompt
In `backend/app/modules/tasks/api.py`, implement ONLY the endpoint `PUT /tasks/{id}` according to `tasks/docs/task_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Task.Edit")`.
- Use existing ORM models and services only.
- Return HTTP 200 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
