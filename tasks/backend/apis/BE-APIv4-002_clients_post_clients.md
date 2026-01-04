# BE-APIv4-002_clients_post_clients — clients POST /clients

## Design references
- `masterdata/clients/docs/client_00_overview.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/masterdata/clients/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `POST /clients`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `POST`
- Path: `/clients`
- Expected HTTP status: `201`

## Permission (Unified)
- Required permission: `Client.Create`
- Enforce via: `require_perm("Client.Create")`

## Request example
```json
{}
```

## Response example (HTTP 201)
```json
{
  "id": "string",
  "client_code": "string",
  "name_cn": "string",
  "name_en": "string",
  "client_type": "string",
  "default_currency": "string"
}
```

## Validation commands
```bash
cd backend
ruff check .
python -m py_compile app/modules/masterdata/clients/api.py
```

### Curl example (expected HTTP 201)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}' "http://localhost:8000/api/v1/clients"
```

## Prompt
In `backend/app/modules/masterdata/clients/api.py`, implement ONLY the endpoint `POST /clients` according to `masterdata/clients/docs/client_00_overview.md`.

Requirements:
- Enforce permission using `require_perm("Client.Create")`.
- Use existing ORM models and services only.
- Return HTTP 201 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
