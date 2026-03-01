# CURL Key Flows (Mock Data) — FPMS MVP1

> This document is a **manual integration smoke** using curl with mock data.
> It complements pytest integration tests.

## Prerequisites
- Server running:
  ```bash
  cd backend
  uvicorn app.main:app --reload
  ```
- Admin seeded:
  ```bash
  cd backend
  python3 scripts/seed_dev.py
  ```
- Ensure permissions are synced (optional but recommended after adding endpoints/perms):
  ```bash
  cd backend
  python3 scripts/scan_perms.py
  python3 scripts/seed_dev.py
  ```

## 0) Login and capture token
```bash
FPMS_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "TOKEN=${FPMS_TOKEN:0:24}..."
```

## 1) Create a Client (Master Data)
```bash
CLIENT_ID=$(curl -s -X POST "http://localhost:8000/api/v1/clients" \
  -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" \
  -d '{"client_code":"CURL_C001","name_cn":"Curl客户","name_en":"Curl Client","client_type":"CORP","default_currency":"CNY"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "CLIENT_ID=$CLIENT_ID"
```

## 2) Create a Case
```bash
CASE_ID=$(curl -s -X POST "http://localhost:8000/api/v1/cases" \
  -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" \
  -d '{"case_no":"CURL_CASE_001","title":"Curl Case","client_id":"'"$CLIENT_ID"'"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "CASE_ID=$CASE_ID"
```

## 3) Create a Task (requires case_id due to DB constraint)
```bash
TASK_ID=$(curl -s -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" \
  -d '{"case_id":"'"$CASE_ID"'","title":"Curl Task","due_date":"2026-01-31"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "TASK_ID=$TASK_ID"
```

## 4) Close + Reopen the Task
```bash
curl -i -X POST "http://localhost:8000/api/v1/tasks/$TASK_ID/close" \
  -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}'

curl -i -X POST "http://localhost:8000/api/v1/tasks/$TASK_ID/reopen" \
  -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}'
```

## 5) Fees: Create rate -> create draft -> add item -> lock
```bash
RATE_ID=$(curl -s -X POST "http://localhost:8000/api/v1/fees/rates" \
  -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" \
  -d '{"fee_code":"CURL_FEE","fee_name":"Curl Fee","fee_type":"GOV","currency":"CNY","default_amount":"100","enabled":true}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "RATE_ID=$RATE_ID"

DRAFT_ID=$(curl -s -X POST "http://localhost:8000/api/v1/fees/drafts" \
  -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" \
  -d '{"case_id":"'"$CASE_ID"'","client_id":"'"$CLIENT_ID"'","currency":"CNY"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "DRAFT_ID=$DRAFT_ID"

ITEM_ID=$(curl -s -X POST "http://localhost:8000/api/v1/fees/drafts/$DRAFT_ID/items" \
  -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" \
  -d '{"rate_id":"'"$RATE_ID"'","quantity":"1","unit_price":"100"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "ITEM_ID=$ITEM_ID"

curl -i -X POST "http://localhost:8000/api/v1/fees/drafts/$DRAFT_ID/lock" \
  -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" -d '{}'
```

## 6) Billing: Generate bill from fee draft (if your API supports it)
If you have a bill generation endpoint (example):
- POST `/bills` with `fee_draft_id`

```bash
# Example (adjust to your actual API)
curl -i -X POST "http://localhost:8000/api/v1/bills" \
  -H "Authorization: Bearer $FPMS_TOKEN" -H "Content-Type: application/json" \
  -d '{"fee_draft_id":"'"$DRAFT_ID"'"}'
```

## 7) Documents: List and create (if enabled)
```bash
curl -i -H "Authorization: Bearer $FPMS_TOKEN" \
  "http://localhost:8000/api/v1/documents?page=1&page_size=20"
```

## Cleanup note
MVP1 dev DB is SQLite and typically disposable. If you want a clean slate:
- delete the sqlite file and rerun alembic + seed, per your project scripts.
