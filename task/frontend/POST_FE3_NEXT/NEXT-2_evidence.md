# Evidence Log — NEXT-2

## Task
- ID: NEXT-2
- Title: Unblock Bill Print (`GET /bills/{id}/print` 409) via deterministic configuration script
- Date: 2026-02-08
- Agent: Codex (GPT-5)

## Backend (Uvicorn)
- Command:
```bash
cd backend
uvicorn app.main:app --reload
```
- Uvicorn key log lines:
  - Backend already serving on `localhost:8000` during this run (probe responded; not curl `000`).
- Probe:
```bash
curl -i "http://localhost:8000/api/v1/clients?page=1&page_size=1"
```
- Probe status:
  - `401 Unauthorized`
  - `x-request-id: 4d6e2d9a-f7c6-4776-9cbd-8e3b6953d81e`
  - Body: `{"error":{"code":"AUTH_REQUIRED","message":"Authentication required","details":null}}`

## File Allowlist Respected
- ✅ Yes
- Modified only:
  - `scripts/dev/setup_printing.sh` (new)
  - `docs/frontend_smoke_flows.md` (updated)
  - `task/frontend/POST_FE3_NEXT/NEXT-2_evidence.md` (new)

## Commands Run
```bash
# Login
curl -sS -D /tmp/fpms_login_headers.txt -o /tmp/fpms_login.json -w "%{http_code}\n" \
  -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# List bills (choose bill id for print validation)
TOKEN=$(jq -r '.access_token' /tmp/fpms_login.json)
curl -sS -D /tmp/fpms_bills_headers.txt -o /tmp/fpms_bills.json -w "%{http_code}\n" \
  "http://localhost:8000/api/v1/bills?page=1&page_size=5" \
  -H "Authorization: Bearer $TOKEN"

# Before: reproduce 409
BILL_ID=$(jq -r '.items[0].id' /tmp/fpms_bills.json)
curl -sS -D /tmp/fpms_bill_print_before_headers.txt -o /tmp/fpms_bill_print_before.json -w "%{http_code}\n" \
  "http://localhost:8000/api/v1/bills/${BILL_ID}/print" \
  -H "Authorization: Bearer $TOKEN"

# Run setup script twice (idempotency)
scripts/dev/setup_printing.sh "$BILL_ID"
scripts/dev/setup_printing.sh "$BILL_ID"

# After: verify print success
curl -sS -D /tmp/fpms_bill_print_after_headers.txt -o /tmp/fpms_bill_print_after.bin -w "%{http_code}\n" \
  "http://localhost:8000/api/v1/bills/${BILL_ID}/print" \
  -H "Authorization: Bearer $TOKEN"
```

## Key Outputs
- Login:
  - HTTP `200`
  - token extracted (`len=165`, prefix `eyJhbGciOiJI...`)
- Bills list:
  - HTTP `200`
  - sample bill id used: `636d413c-cc06-4b9d-a78d-781b0bae641b`
- Before print:
  - HTTP `409 Conflict`
  - `x-request-id: 3026f4cd-daca-45ed-91a1-40afd6bb85b6`
  - Body: `{"detail":"Bill template not configured"}`
- Setup script run #1:
  - template file exists/created check passed
  - letterhead exists check passed
  - template record check passed
  - system param upsert passed
  - print verification passed: `status=200`, `x-request-id=9b2c30c9-6ed1-4c28-8882-a0f63ee86a11`, `bytes=36690`
- Setup script run #2:
  - all checks repeated successfully (idempotent)
  - print verification passed: `status=200`, `x-request-id=15b5c2e2-0cce-4545-9a9a-f02cf9fae5ab`, `bytes=36690`
- After print:
  - HTTP `200 OK`
  - `content-type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`
  - `content-disposition: attachment; filename="bill_636d413c-cc06-4b9d-a78d-781b0bae641b.docx"`
  - `x-request-id: 1a8fb3b2-e214-4e5d-9de4-7f6753373436`
  - Blob size: `36690` bytes

## Reproduction / Verification
### Before
- Steps:
  1. Login with admin account.
  2. Call `GET /api/v1/bills/{bill_id}/print`.
- Result:
  - `409 Conflict`, message `Bill template not configured`.

### After
- Steps:
  1. Run `scripts/dev/setup_printing.sh <BILL_ID>`.
  2. Re-call `GET /api/v1/bills/{bill_id}/print`.
- Result:
  - `200 OK` DOCX blob, `x-request-id` present.
  - Script was run twice; second run remained successful.

## API Evidence
- Requests (method + URL + key payload fields):
  - `POST /api/v1/auth/login` (`username`, `password`)
  - `GET /api/v1/bills?page=1&page_size=5`
  - `GET /api/v1/bills/{bill_id}/print` (before/after)
  - `GET /api/v1/letterheads`
  - `GET /api/v1/templates?page=1&page_size=100`
  - `PUT /api/v1/system/params/bill_template_path` (`param_value`, `value_type`, `is_secret`)
  - `POST /api/v1/templates` (only when missing)
  - `POST /api/v1/letterheads` (only when missing)
- Status codes:
  - Before print: `409`
  - After setup: `200`
- X-Request-ID samples:
  - `3026f4cd-daca-45ed-91a1-40afd6bb85b6` (before 409)
  - `1a8fb3b2-e214-4e5d-9de4-7f6753373436` (after 200)

## Notes
- A transient `500` occurred only during an earlier concurrent test where two setup runs were launched in parallel; acceptance verification was repeated sequentially and passed twice.
