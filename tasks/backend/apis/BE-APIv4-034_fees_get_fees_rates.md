# BE-APIv4-034_fees_get_fees_rates — fees GET /fees/rates

## Design references
- `fees/docs/fee_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/fees/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `GET /fees/rates`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `GET`
- Path: `/fees/rates`
- Expected HTTP status: `200`

## Permission (Unified)
- Required permission: `Fee.Rate.Read`
- Enforce via: `require_perm("Fee.Rate.Read")`

## Request example
```json
{}
```

## Response example (HTTP 200)
```json
{
  "items": [
    {
      "id": "string",
      "fee_code": "string",
      "fee_name": "string",
      "fee_type": "string"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
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
curl -i -H "Authorization: Bearer $FPMS_TOKEN" "http://localhost:8000/api/v1/fees/rates"
```

## Prompt
In `backend/app/modules/fees/api.py`, implement ONLY the endpoint `GET /fees/rates` according to `fees/docs/fee_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Fee.Rate.Read")`.
- Use existing ORM models and services only.
- Return HTTP 200 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
