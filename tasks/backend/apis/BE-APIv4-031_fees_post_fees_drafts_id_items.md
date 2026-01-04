# BE-APIv4-031_fees_post_fees_drafts_id_items — fees POST /fees/drafts/{id}/items

## Design references
- `fees/docs/fee_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/fees/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `POST /fees/drafts/{id}/items`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `POST`
- Path: `/fees/drafts/{id}/items`
- Expected HTTP status: `201`

## Permission (Unified)
- Required permission: `Fee.Item.Create`
- Enforce via: `require_perm("Fee.Item.Create")`

## Request example
```json
{}
```

## Response example (HTTP 201)
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

### Curl example (expected HTTP 201)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}' "http://localhost:8000/api/v1/fees/drafts/REPLACE_ID/items"
```

## Prompt
In `backend/app/modules/fees/api.py`, implement ONLY the endpoint `POST /fees/drafts/{id}/items` according to `fees/docs/fee_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Fee.Item.Create")`.
- Use existing ORM models and services only.
- Return HTTP 201 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
