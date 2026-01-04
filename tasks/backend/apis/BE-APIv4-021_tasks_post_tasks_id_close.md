# BE-APIv4-021_tasks_post_tasks_id_close — tasks POST /tasks/{id}/close

## Design references
- `tasks/docs/task_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/tasks/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `POST /tasks/{id}/close`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `POST`
- Path: `/tasks/{id}/close`
- Expected HTTP status: `200`

## Permission (Unified)
- Required permission: `Task.Action`
- Enforce via: `require_perm("Task.Action")`

## Request example
```json
{}
```

## Response example (HTTP 200)
```json
{
  "status": "ok"
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
curl -i -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}' "http://localhost:8000/api/v1/tasks/REPLACE_ID/close"
```

## Prompt
In `backend/app/modules/tasks/api.py`, implement ONLY the endpoint `POST /tasks/{id}/close` according to `tasks/docs/task_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Task.Action")`.
- Use existing ORM models and services only.
- Return HTTP 200 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
