# Curl Key Flows (Manual Smoke)

All commands assume:
- API base: `http://localhost:8000`
- A running backend server
- You have run seed if needed (`python3 scripts/seed_dev.py`)

Notes:
- If you see 403, re-run permission scan/seed, then re-login to refresh token.
- If you see 307, remove/add the trailing slash in the URL.

## 1) Login (capture token)

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')
echo "$TOKEN"
```

## 2) Create client → create case → create task

```bash
CLIENT_ID=$(curl -s -X POST http://localhost:8000/api/v1/clients \
  -H "Authorization: Bearer $TOKEN" \
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
CASE_ID=$(curl -s -X POST http://localhost:8000/api/v1/cases \
  -H "Authorization: Bearer $TOKEN" \
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
TASK_ID=$(curl -s -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id":"'"$CASE_ID"'",
    "title":"CURL Task 001",
    "due_date":"2026-02-01"
  }' | jq -r '.id')
echo "$TASK_ID"
```

## 3) Fees: create rate → create draft → add item → lock

```bash
RATE_ID=$(curl -s -X POST http://localhost:8000/api/v1/fees/rates \
  -H "Authorization: Bearer $TOKEN" \
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
  -H "Authorization: Bearer $TOKEN" \
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
  -H "Authorization: Bearer $TOKEN" \
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
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## 4) Documents list smoke (optional)

```bash
curl -s -X GET http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer $TOKEN"
```
