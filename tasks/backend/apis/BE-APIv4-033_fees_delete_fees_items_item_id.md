# BE-APIv4-033_fees_delete_fees_items_item_id — fees DELETE /fees/items/{item_id}

## Design references
- `fees/docs/fee_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/fees/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `DELETE /fees/items/{item_id}`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `DELETE`
- Path: `/fees/items/{item_id}`
- Expected HTTP status: `204`

## Permission (Unified)
- Required permission: `Fee.Item.Delete`
- Enforce via: `require_perm("Fee.Item.Delete")`

## Request example
```json
{}
```

## Response example (HTTP 204)
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

### Curl example (expected HTTP 204)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -X DELETE -H "Authorization: Bearer $FPMS_TOKEN" "http://localhost:8000/api/v1/fees/items/REPLACE_ID"
```

## Prompt
In `backend/app/modules/fees/api.py`, implement ONLY the endpoint `DELETE /fees/items/{item_id}` according to `fees/docs/fee_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Fee.Item.Delete")`.
- Use existing ORM models and services only.
- Return HTTP 204 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
