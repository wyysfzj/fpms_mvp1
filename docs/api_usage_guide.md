# FPMS MVP1 API Usage Guide

## Base URL & Conventions
- Base URL: `http://localhost:8000/api/v1`
- Use JSON: `Content-Type: application/json`
- Auth header: `Authorization: Bearer <token>`
- 307 Temporary Redirect: ensure you use the exact path shown in OpenAPI. If needed, add `-L` to curl.

## Authentication
Login and capture a token into `FPMS_TOKEN`:

```bash
FPMS_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')
echo "$FPMS_TOKEN"
```

## Token Validation (no auth profile endpoint in MVP1)
There is currently **no** auth profile endpoint in MVP1. To validate a token:
- **200**: token is valid *and* has permission for the endpoint.
- **403**: token is valid but missing permission (sync perms + re-login).
- **401**: token missing/invalid/expired.

Example using an existing protected endpoint:

```bash
curl -s -i -X GET "http://localhost:8000/api/v1/clients?page=1&page_size=20" \
  -H "Authorization: Bearer $FPMS_TOKEN"
```

## Permissions & Seeding (IMPORTANT)
If you get unexpected 403s, permissions are likely out of sync.

```bash
python3 scripts/scan_perms.py
python3 scripts/seed_dev.py
```

After syncing permissions, **login again** to refresh your token.

### 401 vs 403 quick guide
- **401 AUTH_REQUIRED**: token missing/invalid/expired → re-login.
- **403 FORBIDDEN**: token valid but missing permission → re-seed perms + re-login.

## Error Response Contract
Current backend behavior includes two envelopes:

1) Business/domain and request-validation errors (preferred):
```json
{
  "error": {
    "code": "SOME_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

2) Some legacy endpoints still return FastAPI `HTTPException`:
```json
{
  "detail": "Human readable message"
}
```

Post-enhancement rule for new domains (`annuity`, `collections`, `commission`, `consulting`):
- Use `BusinessError` envelope for domain/business errors.
- Keep status semantics consistent: `400/401/403/404/409/422`.

## Post-enhancement Domain Status Semantics
As of 2026-02-28, these domain routers are not yet exposed under `/api/v1`:
- `annuity`
- `collections` (dunning/bad-debt)
- `commission`
- `consulting`

Expected status semantics once implemented:
- `201`: create operations (return created resource or identifier).
- `200`: query/read/update operations returning content.
- `204`: delete/no-content operations (must not include body).
- `400`: business validation failure.
- `401`: unauthenticated.
- `403`: permission denied.
- `404`: resource not found.
- `409`: state/configuration conflict.
- `422`: request payload validation error.

Until these routers are implemented, calling such paths may return framework route-not-found `404` with `{"detail":"Not Found"}`.

## Key MVP1 Workflows (curl examples)

### Client: create + list
```bash
CLIENT_ID=$(curl -s -X POST http://localhost:8000/api/v1/clients \
  -H "Authorization: Bearer $FPMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_code":"CURL_C001",
    "name_cn":"Curl Client CN",
    "name_en":"Curl Client EN",
    "client_type":"CLIENT",
    "default_currency":"CNY",
    "is_active":true
  }' | jq -r '.id')
echo "$CLIENT_ID"
```

```bash
curl -s -X GET "http://localhost:8000/api/v1/clients?page=1&page_size=20" \
  -H "Authorization: Bearer $FPMS_TOKEN"
```

### Case: create + list + get
```bash
CASE_ID=$(curl -s -X POST http://localhost:8000/api/v1/cases \
  -H "Authorization: Bearer $FPMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_no":"CURL_CASE_001",
    "case_type":"NORMAL",
    "patent_category":"INV",
    "flow_dir":"CN_DOMESTIC",
    "client_id":"'"$CLIENT_ID"'"
  }' | jq -r '.id')
echo "$CASE_ID"
```

```bash
curl -s -X GET "http://localhost:8000/api/v1/cases?page=1&page_size=20" \
  -H "Authorization: Bearer $FPMS_TOKEN"
```

```bash
curl -s -X GET "http://localhost:8000/api/v1/cases/$CASE_ID" \
  -H "Authorization: Bearer $FPMS_TOKEN"
```

### Document: create + list
```bash
DOC_ID=$(curl -s -X POST http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer $FPMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id":"'"$CASE_ID"'",
    "direction":"IN"
  }' | jq -r '.id')
echo "$DOC_ID"
```

```bash
curl -s -X GET "http://localhost:8000/api/v1/documents?page=1&page_size=20" \
  -H "Authorization: Bearer $FPMS_TOKEN"
```

### Task: create + list + get (case_id required)
```bash
TASK_ID=$(curl -s -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $FPMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id":"'"$CASE_ID"'",
    "title":"CURL Task 001",
    "due_date":"2026-02-01"
  }' | jq -r '.id')
echo "$TASK_ID"
```

```bash
curl -s -X GET "http://localhost:8000/api/v1/tasks?page=1&page_size=20" \
  -H "Authorization: Bearer $FPMS_TOKEN"
```

```bash
curl -s -X GET "http://localhost:8000/api/v1/tasks/$TASK_ID" \
  -H "Authorization: Bearer $FPMS_TOKEN"
```

### Fees: create rate → create draft → add item → lock
```bash
RATE_ID=$(curl -s -X POST http://localhost:8000/api/v1/fees/rates \
  -H "Authorization: Bearer $FPMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fee_code":"CURL_FEE_001",
    "fee_name":"Service Fee",
    "fee_type":"SERVICE",
    "currency":"CNY",
    "default_amount":"100.00",
    "enabled":true
  }' | jq -r '.id')
echo "$RATE_ID"
```

```bash
DRAFT_ID=$(curl -s -X POST http://localhost:8000/api/v1/fees/drafts \
  -H "Authorization: Bearer $FPMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id":"'"$CASE_ID"'",
    "client_id":"'"$CLIENT_ID"'",
    "draft_type":"GENERIC",
    "currency":"CNY"
  }' | jq -r '.id')
echo "$DRAFT_ID"
```

```bash
ITEM_ID=$(curl -s -X POST http://localhost:8000/api/v1/fees/drafts/$DRAFT_ID/items \
  -H "Authorization: Bearer $FPMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rate_id":"'"$RATE_ID"'",
    "quantity":"1",
    "unit_price":"100.00"
  }' | jq -r '.id')
echo "$ITEM_ID"
```

```bash
curl -s -X POST http://localhost:8000/api/v1/fees/drafts/$DRAFT_ID/lock \
  -H "Authorization: Bearer $FPMS_TOKEN"
```

### Billing: create bill (manual) → create payment → create offset
```bash
BILL_ID=$(curl -s -X POST http://localhost:8000/api/v1/bills/manual \
  -H "Authorization: Bearer $FPMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id":"'"$CLIENT_ID"'",
    "bill_no":"CURL_BILL_001",
    "currency":"CNY",
    "direction":"AR",
    "status":"UNSETTLED"
  }' | jq -r '.id')
echo "$BILL_ID"
```

```bash
PAYMENT_ID=$(curl -s -X POST http://localhost:8000/api/v1/payments \
  -H "Authorization: Bearer $FPMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id":"'"$CLIENT_ID"'",
    "amount":"100.00",
    "currency":"CNY",
    "pay_no":"CURL_PAY_001"
  }' | jq -r '.id')
echo "$PAYMENT_ID"
```

```bash
# NOTE: Offset requires a payment_line_id produced by payment processing.
# If your payment processing generates payment lines, use that ID here.
curl -s -X POST http://localhost:8000/api/v1/offsets \
  -H "Authorization: Bearer $FPMS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_line_id":"PAYLINE_ID_HERE",
    "bill_id":"'"$BILL_ID"'",
    "offset_amt":"50.00"
  }'
```

### Templates/System params (read-only examples)
```bash
curl -s -X GET http://localhost:8000/api/v1/templates \
  -H "Authorization: Bearer $FPMS_TOKEN"
```

```bash
curl -s -X GET http://localhost:8000/api/v1/system/params \
  -H "Authorization: Bearer $FPMS_TOKEN"
```

## Common Errors & Fixes
- **401 AUTH_REQUIRED**: token missing/invalid/expired → login again.
- **403 FORBIDDEN**: token valid but missing permission → run `python3 scripts/scan_perms.py`, then `python3 scripts/seed_dev.py`, re-login.
- **400 BUSINESS_ERROR**: domain rule validation failed (see `error.code` for the exact failure).
- **404 NOT_FOUND**: resource does not exist; for not-yet-routed domains, this may be route-level `{"detail":"Not Found"}`.
- **422 VALIDATION_ERROR**: request body/fields invalid (check required fields and types).
- **409 CONFLICT**:
  - Missing config for printing (e.g., bill template not configured).
  - Fee draft already locked / not locked when expected.
  - Currency mismatch between fee draft and fee rate.

## Appendix: Quick Smoke Script

```bash
BASE="http://localhost:8000/api/v1"
TOKEN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

CLIENT_ID=$(curl -s -o /dev/null -w "%{http_code} " -X POST "$BASE/clients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"client_code":"CURL_SMOKE_001","name_cn":"Smoke Client","default_currency":"CNY"}')
echo "create client HTTP: $CLIENT_ID"

CASE_CODE=$(curl -s -o /dev/null -w "%{http_code} " -X POST "$BASE/cases" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"case_no":"CURL_SMOKE_CASE_001","case_type":"NORMAL","patent_category":"INV","flow_dir":"CN_DOMESTIC"}')
echo "create case HTTP: $CASE_CODE"

TASK_CODE=$(curl -s -o /dev/null -w "%{http_code} " -X POST "$BASE/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"case_id":"REPLACE_WITH_CASE_ID","title":"Smoke Task","due_date":"2026-02-01"}')
echo "create task HTTP: $TASK_CODE"
```
