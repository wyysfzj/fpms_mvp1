# BE-APIv4-004_clients_put_clients_id_deactivate — clients PUT /clients/{id}/deactivate

## Design references
- `masterdata/clients/docs/client_00_overview.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/masterdata/clients/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `PUT /clients/{id}/deactivate`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `PUT`
- Path: `/clients/{id}/deactivate`
- Expected HTTP status: `200`

## Permission (Unified)
- Required permission: `Client.Action`
- Enforce via: `require_perm("Client.Action")`

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
python -m py_compile app/modules/masterdata/clients/api.py
```

### Curl example (expected HTTP 200)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -X PUT -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}' "http://localhost:8000/api/v1/clients/REPLACE_ID/deactivate"
```

## Prompt
In `backend/app/modules/masterdata/clients/api.py`, implement ONLY the endpoint `PUT /clients/{id}/deactivate` according to `masterdata/clients/docs/client_00_overview.md`.

Requirements:
- Enforce permission using `require_perm("Client.Action")`.
- Use existing ORM models and services only.
- Return HTTP 200 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
