# BE-APIv4-035_fees_post_fees_rates — fees POST /fees/rates

## Design references
- `fees/docs/fee_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/fees/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `POST /fees/rates`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `POST`
- Path: `/fees/rates`
- Expected HTTP status: `201`

## Permission (Unified)
- Required permission: `Fee.Rate.Create`
- Enforce via: `require_perm("Fee.Rate.Create")`

## Request example
```json
{}
```

## Response example (HTTP 201)
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

### Curl example (expected HTTP 201)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}' "http://localhost:8000/api/v1/fees/rates"
```

## Prompt
In `backend/app/modules/fees/api.py`, implement ONLY the endpoint `POST /fees/rates` according to `fees/docs/fee_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Fee.Rate.Create")`.
- Use existing ORM models and services only.
- Return HTTP 201 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
