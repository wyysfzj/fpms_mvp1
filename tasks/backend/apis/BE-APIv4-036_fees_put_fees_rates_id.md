# BE-APIv4-036_fees_put_fees_rates_id — fees PUT /fees/rates/{id}

## Design references
- `fees/docs/fee_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/fees/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `PUT /fees/rates/{id}`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `PUT`
- Path: `/fees/rates/{id}`
- Expected HTTP status: `200`

## Permission (Unified)
- Required permission: `Fee.Rate.Edit`
- Enforce via: `require_perm("Fee.Rate.Edit")`

## Request example
```json
{
  "fee_code": "string",
  "fee_name": "string"
}
```

## Response example (HTTP 200)
```json
{
  "id": "string",
  "fee_code": "string",
  "fee_name": "string",
  "fee_type": "string",
  "currency": "string",
  "default_amount": 0.0
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
curl -i -X PUT -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{"fee_code": "string", "fee_name": "string"}' "http://localhost:8000/api/v1/fees/rates/REPLACE_ID"
```

## Prompt
In `backend/app/modules/fees/api.py`, implement ONLY the endpoint `PUT /fees/rates/{id}` according to `fees/docs/fee_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Fee.Rate.Edit")`.
- Use existing ORM models and services only.
- Return HTTP 200 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
