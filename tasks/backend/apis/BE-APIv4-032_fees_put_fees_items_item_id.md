# BE-APIv4-032_fees_put_fees_items_item_id — fees PUT /fees/items/{item_id}

## Design references
- `fees/docs/fee_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/fees/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `PUT /fees/items/{item_id}`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `PUT`
- Path: `/fees/items/{item_id}`
- Expected HTTP status: `200`

## Permission (Unified)
- Required permission: `Fee.Item.Edit`
- Enforce via: `require_perm("Fee.Item.Edit")`

## Request example
```json
{
  "draft_id": "string",
  "case_id": "string"
}
```

## Response example (HTTP 200)
```json
{
  "id": "string",
  "draft_id": "string",
  "case_id": "string",
  "rate_id": "string",
  "fee_code": "string",
  "fee_name": "string"
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
curl -i -X PUT -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{"draft_id": "string", "case_id": "string"}' "http://localhost:8000/api/v1/fees/items/REPLACE_ID"
```

## Prompt
In `backend/app/modules/fees/api.py`, implement ONLY the endpoint `PUT /fees/items/{item_id}` according to `fees/docs/fee_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Fee.Item.Edit")`.
- Use existing ORM models and services only.
- Return HTTP 200 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
