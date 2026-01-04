# BE-APIv4-028_fees_put_fees_drafts_id — fees PUT /fees/drafts/{id}

## Design references
- `fees/docs/fee_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/fees/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `PUT /fees/drafts/{id}`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `PUT`
- Path: `/fees/drafts/{id}`
- Expected HTTP status: `200`

## Permission (Unified)
- Required permission: `Fee.Draft.Edit`
- Enforce via: `require_perm("Fee.Draft.Edit")`

## Request example
```json
{
  "case_id": "string",
  "client_id": "string"
}
```

## Response example (HTTP 200)
```json
{
  "id": "string",
  "case_id": "string",
  "client_id": "string",
  "draft_type": "string",
  "currency": "string",
  "status": "string"
}
```

## Validation commands
```bash
cd backend
ruff check .
python -m py_compile app/modules/fees/api.py
```

### Curl example (expected HTTP 200)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -X PUT -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{"case_id": "string", "client_id": "string"}' "http://localhost:8000/api/v1/fees/drafts/REPLACE_ID"
```

## Prompt
In `backend/app/modules/fees/api.py`, implement ONLY the endpoint `PUT /fees/drafts/{id}` according to `fees/docs/fee_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Fee.Draft.Edit")`.
- Use existing ORM models and services only.
- Return HTTP 200 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
