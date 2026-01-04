# BE-APIv4-044_billing_get_payments_id — billing GET /payments/{id}

## Design references
- `billing/docs/bill_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/billing/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `GET /payments/{id}`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `GET`
- Path: `/payments/{id}`
- Expected HTTP status: `200`

## Permission (Unified)
- Required permission: `Payment.Read`
- Enforce via: `require_perm("Payment.Read")`

## Request example
```json
{}
```

## Response example (HTTP 200)
```json
{
  "id": "string",
  "pay_no": "string",
  "client_id": "string",
  "pay_date": "2025-01-01",
  "currency": "string",
  "amount": 0.0
}
```

## Validation commands
```bash
cd backend
ruff check .
python -m py_compile app/modules/billing/api.py
```

### Curl example (expected HTTP 200)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -H "Authorization: Bearer $FPMS_TOKEN" "http://localhost:8000/api/v1/payments/REPLACE_ID"
```

## Prompt
In `backend/app/modules/billing/api.py`, implement ONLY the endpoint `GET /payments/{id}` according to `billing/docs/bill_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Payment.Read")`.
- Use existing ORM models and services only.
- Return HTTP 200 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
