# BE-APIv4-039_billing_post_bills_manual — billing POST /bills/manual

## Design references
- `billing/docs/bill_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/billing/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `POST /bills/manual`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `POST`
- Path: `/bills/manual`
- Expected HTTP status: `201`

## Permission (Unified)
- Required permission: `Bill.Create`
- Enforce via: `require_perm("Bill.Create")`

## Request example
```json
{}
```

## Response example (HTTP 201)
```json
{
  "id": "string",
  "bill_no": "string",
  "client_id": "string",
  "currency": "string",
  "direction": "string",
  "status": "string"
}
```

## Validation commands
```bash
cd backend
ruff check .
python -m py_compile app/modules/billing/api.py
```

### Curl example (expected HTTP 201)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}' "http://localhost:8000/api/v1/bills/manual"
```

## Prompt
In `backend/app/modules/billing/api.py`, implement ONLY the endpoint `POST /bills/manual` according to `billing/docs/bill_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Bill.Create")`.
- Use existing ORM models and services only.
- Return HTTP 201 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
