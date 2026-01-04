# BE-APIv4-043_billing_post_payments — billing POST /payments

## Design references
- `billing/docs/bill_02_api.md` 
- `docs/execution_order_v2.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Target
- **File:** `backend/app/modules/billing/api.py`
- **Atomic rule:** modify/create ONLY this file; implement ONLY this ONE endpoint.

## Scope decision (MVP1 – FIXED)
- Implement ONLY `POST /payments`.
- No schema changes, no new tables, no migration changes.
- Use existing ORM models only.

## Endpoint (EXACT)
- Method: `POST`
- Path: `/payments`
- Expected HTTP status: `201`

## Permission (Unified)
- Required permission: `Payment.Create`
- Enforce via: `require_perm("Payment.Create")`

## Request example
```json
{}
```

## Response example (HTTP 201)
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

### Curl example (expected HTTP 201)
```bash
export FPMS_TOKEN="REPLACE_ME"
curl -i -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}' "http://localhost:8000/api/v1/payments"
```

## Prompt
In `backend/app/modules/billing/api.py`, implement ONLY the endpoint `POST /payments` according to `billing/docs/bill_02_api.md`.

Requirements:
- Enforce permission using `require_perm("Payment.Create")`.
- Use existing ORM models and services only.
- Return HTTP 201 on success.
- Keep request/response shapes consistent with examples above (adjust only if API doc specifies differently).

Do NOT:
- Add other endpoints
- Modify schema/migrations
- Ask clarification questions
