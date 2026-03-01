# Codex Prompt — FE‑3 Runtime Smoke Re‑Run + Contract Drift Fix (Admin creds provided)

## Why this run
The previous FE‑3 QA run had **backend unavailable (curl 000)**, so runtime smoke was blocked, and multiple cross‑module FE/BE contract drifts were left unfixed (FE3‑DEF‑009).  
Now backend is running (probe returns 401), so we must rerun runtime smoke and fix remaining defects **with evidence**.

Known status from last QA:
- Gates PASS (lint/typecheck/build) and multiple UI defects were fixed.
- Remaining critical: FE3‑DEF‑009 (contract drift) + FE3‑DEF‑010 (runtime smoke blocked).  
(Do not trust static guesses; capture real 422 details and align adapters.)

## Credentials (for local QA)
- username: `admin`
- password: `admin123`

## Backend Enum Reference

| Module | Enum | Values |
|--------|------|--------|
| Cases | CaseType | `NORMAL`, `PCT_INTL`, `PCT_NATL`, `PRIORITY` |
| Cases | PatentCategory | `INV`, `UM`, `DES` |
| Cases | FlowDir | `CN_DOMESTIC`, `CN_OUTBOUND`, `FOREIGN_INBOUND` |
| Documents | DocumentDirection | `IN`, `OUT` |
| Tasks | TaskStatus | `OPEN`, `DONE`, `CANCELLED` |
| Tasks | TaskTodayAs | `worker`, `supervisor` |
| Fees | FeeType | `GOV`, `SERVICE`, `MISC` |
| Fees | FeeDraftStatus | `OPEN`, `LOCKED` |

## Entity Dependency Chain

Entities must be created in this order (upstream IDs required by downstream creates):

```
Client → Case (client_id) → Task (case_id) → Document (case_id)
                           ↘ Fee Draft (case_id)
Fee Rate ──────────────────→ Fee Item (rate_id + draft_id)
Fee Draft (lock) ──────────→ Bill from-drafts (draft_ids)
Client ────────────────────→ Bill manual (client_id)
Bill ──────────────────────→ Payment (client_id from bill)
Payment detail ────────────→ Offset (payment_line_id + bill_id)
```

## Hard constraints (do not violate)
- UI source of truth: `reference/case_detail.html`
- Tokens spec: `fpms.css` — DO NOT change the `src/styles/variables.css` token block values.
- No heavy new dependencies.
- No inline styles / magic numbers in Vue templates.
- All API calls must go through shared client; do not bypass.
- If you find an endpoint mismatch and cannot resolve without guessing: STOP and write the smallest fix proposal.

## Required outputs
Create/overwrite:
1) `task/frontend/FE-3/FE-3_RUNTIME_SMOKE_REPORT.md`
2) `task/frontend/FE-3/FE-3_RUNTIME_SMOKE_EVIDENCE.md`

Update:
- `task/frontend/FE-3/FE-3_QA_REVIEW_REPORT.md` (mark runtime results, update defect statuses)
- `task/frontend/FE-3/FE-3_QA_EVIDENCE.md` (append runtime section, do not delete prior baseline)

Optional (recommended):
- `docs/frontend_smoke_flows.md` (ONLY if steps or labels changed; keep it accurate)

## Step 0 — Pre-flight checklist

Before starting runtime smoke, ensure:

### 0.1 Prerequisites
```bash
# Verify curl + jq available
which curl jq

# Verify backend is reachable (expect 200)
curl -sS -o /dev/null -w '%{http_code}' http://localhost:8000/healthz
```

### 0.2 Database seeding (if DB is fresh or was rebuilt)
```bash
cd backend
source .venv/bin/activate
alembic upgrade head
python scripts/seed_dev.py
```

### 0.3 Bill print setup (resolves RT-002 template-not-configured)
```bash
# From repo root — creates letterhead, template record, and system param
bash scripts/dev/setup_printing.sh
```
This script:
- Creates `backend/storage/templates/bill_default.docx` if missing
- Creates a letterhead record
- Creates a template record pointing to the `.docx` file
- Upserts `bill_template_path` system param
- Verifies `GET /bills/{id}/print` returns 200

## Step 1 — Confirm backend connectivity
Run:
```bash
curl -i "http://localhost:8000/api/v1/clients?page=1&page_size=1"
```
Expected: **401** (or another HTTP status), but NOT `000`.

Record the output in `FE-3_RUNTIME_SMOKE_EVIDENCE.md`.

## Step 2 — Discover the real login endpoint (do NOT guess)
Find OpenAPI:
```bash
curl -s http://localhost:8000/openapi.json | head
curl -s http://localhost:8000/api/v1/openapi.json | head
```

If you get JSON, list login/token paths:
```bash
curl -s http://localhost:8000/openapi.json | jq -r '.paths | keys[]' | rg -i "auth|login|token"
```

From OpenAPI, determine:
- login URL
- request content-type (JSON vs form)
- response token field name

## Step 3 — Login and capture token (admin/admin123)
Perform login using the discovered endpoint and correct content type.
Save the response to `/tmp/fpms_login.json` and extract token safely using jq (field name from OpenAPI).

Record:
- status code
- response body (redact password)
- extracted token length/prefix (do not print full token)

## Step 4 — Runtime API smoke (curl parity) for each module flow
Use `Authorization: Bearer <token>`.

Set up shell variables for convenience:
```bash
BASE="http://localhost:8000/api/v1"
TOKEN=$(jq -r '.access_token' /tmp/fpms_login.json)
AUTH="Authorization: Bearer $TOKEN"
```

For each call record:
- endpoint + method
- request payload (redact secrets)
- status code
- response body (especially 422 `error.details`)
- `X-Request-ID` header if present

### Minimum flows to execute (in dependency order)

> **Convention**: Save each create response to `/tmp/fpms_<entity>.json` and extract the ID for downstream calls:
> ```bash
> CLIENT_ID=$(jq -r '.id' /tmp/fpms_client.json)
> ```

#### 1) Clients
```bash
# list
curl -sS -H "$AUTH" "$BASE/clients?page=1&page_size=5"

# create → save to /tmp/fpms_client.json
curl -sS -o /tmp/fpms_client.json -w '\n%{http_code}' -X POST "$BASE/clients" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"name_cn":"测试客户A","name_en":"Test Client A","client_code":"TC-001","client_type":"enterprise","default_currency":"CNY"}'
CLIENT_ID=$(jq -r '.id' /tmp/fpms_client.json)

# update
curl -sS -X PUT "$BASE/clients/$CLIENT_ID" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"name_en":"Test Client A Updated"}'

# deactivate
curl -sS -X PUT "$BASE/clients/$CLIENT_ID/deactivate" -H "$AUTH"
```

#### 2) Cases
```bash
# list
curl -sS -H "$AUTH" "$BASE/cases?page=1&page_size=5"

# create → save to /tmp/fpms_case.json
curl -sS -o /tmp/fpms_case.json -w '\n%{http_code}' -X POST "$BASE/cases" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d "{\"case_no\":\"SMOKE-$(date +%s)\",\"case_type\":\"NORMAL\",\"patent_category\":\"INV\",\"flow_dir\":\"CN_DOMESTIC\",\"client_id\":\"$CLIENT_ID\"}"
CASE_ID=$(jq -r '.id' /tmp/fpms_case.json)

# detail
curl -sS -H "$AUTH" "$BASE/cases/$CASE_ID"

# update
curl -sS -X PUT "$BASE/cases/$CASE_ID" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"title_cn":"烟雾测试案件"}'

# limited-edit
curl -sS -X POST "$BASE/cases/$CASE_ID/limited-edit" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"title_cn":"烟雾测试案件-已编辑","title_en":"Smoke Test Case Edited"}'
```

#### 3) Tasks
```bash
# list
curl -sS -H "$AUTH" "$BASE/tasks?page=1&page_size=5"

# create → save to /tmp/fpms_task.json
curl -sS -o /tmp/fpms_task.json -w '\n%{http_code}' -X POST "$BASE/tasks" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d "{\"case_id\":\"$CASE_ID\",\"title\":\"Smoke Test Task\",\"due_date\":\"$(date -v+7d +%Y-%m-%d 2>/dev/null || date -d '+7 days' +%Y-%m-%d)\",\"remark\":\"runtime smoke\"}"
TASK_ID=$(jq -r '.id' /tmp/fpms_task.json)

# close
curl -sS -X POST "$BASE/tasks/$TASK_ID/close" \
  -H "$AUTH" -H 'Content-Type: application/json' -d '{"remark":"smoke close"}'

# reopen
curl -sS -X POST "$BASE/tasks/$TASK_ID/reopen" \
  -H "$AUTH" -H 'Content-Type: application/json' -d '{"remark":"smoke reopen"}'

# cancel
curl -sS -X POST "$BASE/tasks/$TASK_ID/cancel" \
  -H "$AUTH" -H 'Content-Type: application/json' -d '{"remark":"smoke cancel"}'

# today reminders
curl -sS -H "$AUTH" "$BASE/tasks/today?as=worker&page=1&page_size=5"
curl -sS -H "$AUTH" "$BASE/tasks/today?as=supervisor&page=1&page_size=5"
```

#### 4) Documents
```bash
# list
curl -sS -H "$AUTH" "$BASE/documents?page=1&page_size=5"

# create → save to /tmp/fpms_document.json
curl -sS -o /tmp/fpms_document.json -w '\n%{http_code}' -X POST "$BASE/documents" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d "{\"case_id\":\"$CASE_ID\",\"direction\":\"IN\",\"doc_date\":\"$(date +%Y-%m-%d)\",\"title\":\"Smoke Test Doc\",\"doc_template_id\":null}"
DOC_ID=$(jq -r '.id' /tmp/fpms_document.json)

# detail (also returns attachments array)
curl -sS -H "$AUTH" "$BASE/documents/$DOC_ID"

# upload attachment (multipart)
echo "smoke test content" > /tmp/fpms_test_upload.txt
curl -sS -o /tmp/fpms_attachment.json -w '\n%{http_code}' \
  -X POST "$BASE/documents/$DOC_ID/attachments" \
  -H "$AUTH" -F "file=@/tmp/fpms_test_upload.txt"
ATTACH_ID=$(jq -r '.id' /tmp/fpms_attachment.json)

# download attachment (blob)
curl -sS -o /tmp/fpms_downloaded_file -w '\n%{http_code}' \
  -H "$AUTH" "$BASE/documents/$DOC_ID/attachments/$ATTACH_ID/download"
```

#### 5) Fees
```bash
# rates list
curl -sS -H "$AUTH" "$BASE/fees/rates?page=1&page_size=50"

# rate create → save to /tmp/fpms_rate.json
curl -sS -o /tmp/fpms_rate.json -w '\n%{http_code}' -X POST "$BASE/fees/rates" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"fee_code":"SMOKE-FEE","fee_name":"烟雾测试费","fee_type":"SERVICE","currency":"CNY","default_amount":100.00}'
RATE_ID=$(jq -r '.id' /tmp/fpms_rate.json)

# drafts list
curl -sS -H "$AUTH" "$BASE/fees/drafts?page=1&page_size=20"

# draft create → save to /tmp/fpms_draft.json
curl -sS -o /tmp/fpms_draft.json -w '\n%{http_code}' -X POST "$BASE/fees/drafts" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d "{\"case_id\":\"$CASE_ID\",\"currency\":\"CNY\"}"
DRAFT_ID=$(jq -r '.id' /tmp/fpms_draft.json)

# draft detail
curl -sS -H "$AUTH" "$BASE/fees/drafts/$DRAFT_ID"

# item add → save to /tmp/fpms_item.json
curl -sS -o /tmp/fpms_item.json -w '\n%{http_code}' -X POST "$BASE/fees/drafts/$DRAFT_ID/items" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d "{\"rate_id\":\"$RATE_ID\",\"quantity\":2,\"unit_price\":100.00,\"remark\":\"smoke item\"}"
ITEM_ID=$(jq -r '.id' /tmp/fpms_item.json)

# item update
curl -sS -X PUT "$BASE/fees/drafts/$DRAFT_ID/items/$ITEM_ID" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"quantity":3,"remark":"smoke item updated"}'

# item delete (204 No Content)
curl -sS -o /dev/null -w '%{http_code}' -X DELETE "$BASE/fees/items/$ITEM_ID" -H "$AUTH"

# re-add item for lock test
curl -sS -o /tmp/fpms_item2.json -w '\n%{http_code}' -X POST "$BASE/fees/drafts/$DRAFT_ID/items" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d "{\"rate_id\":\"$RATE_ID\",\"quantity\":1,\"unit_price\":200.00}"

# lock
curl -sS -X POST "$BASE/fees/drafts/$DRAFT_ID/lock" -H "$AUTH"

# unlock
curl -sS -X POST "$BASE/fees/drafts/$DRAFT_ID/unlock" -H "$AUTH"
```

#### 6) Billing
```bash
# bills list
curl -sS -H "$AUTH" "$BASE/bills?page=1&page_size=20"

# manual bill create → save to /tmp/fpms_bill_manual.json
curl -sS -o /tmp/fpms_bill_manual.json -w '\n%{http_code}' -X POST "$BASE/bills/manual" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d "{\"client_id\":\"$CLIENT_ID\",\"currency\":\"CNY\"}"
BILL_MANUAL_ID=$(jq -r '.id' /tmp/fpms_bill_manual.json)

# lock the fee draft first, then create bill from drafts
curl -sS -X POST "$BASE/fees/drafts/$DRAFT_ID/lock" -H "$AUTH"
curl -sS -o /tmp/fpms_bill_drafts.json -w '\n%{http_code}' -X POST "$BASE/bills/from-drafts" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d "{\"draft_ids\":[\"$DRAFT_ID\"]}"
BILL_DRAFTS_ID=$(jq -r '.id' /tmp/fpms_bill_drafts.json)

# bill detail
curl -sS -H "$AUTH" "$BASE/bills/$BILL_MANUAL_ID"

# print (should work after setup_printing.sh pre-flight)
curl -sS -o /tmp/fpms_bill_print.docx -D /tmp/fpms_bill_print_headers.txt -w '\n%{http_code}' \
  -H "$AUTH" "$BASE/bills/$BILL_MANUAL_ID/print"

# payment create → save to /tmp/fpms_payment.json
curl -sS -o /tmp/fpms_payment.json -w '\n%{http_code}' -X POST "$BASE/payments" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d "{\"client_id\":\"$CLIENT_ID\",\"amount\":500.00,\"currency\":\"CNY\",\"pay_date\":\"$(date +%Y-%m-%d)\",\"remark\":\"smoke payment\"}"
PAYMENT_ID=$(jq -r '.id' /tmp/fpms_payment.json)

# payment detail (extract payment_line_id for offset)
curl -sS -o /tmp/fpms_payment_detail.json -H "$AUTH" "$BASE/payments/$PAYMENT_ID"
PAYMENT_LINE_ID=$(jq -r '.payment_lines[0].id // empty' /tmp/fpms_payment_detail.json)

# offset create (requires valid payment_line_id + bill_id)
if [ -n "$PAYMENT_LINE_ID" ]; then
  curl -sS -o /tmp/fpms_offset.json -w '\n%{http_code}' -X POST "$BASE/offsets" \
    -H "$AUTH" -H 'Content-Type: application/json' \
    -d "{\"payment_line_id\":\"$PAYMENT_LINE_ID\",\"bill_id\":\"$BILL_MANUAL_ID\",\"offset_amt\":100.00}"
  OFFSET_ID=$(jq -r '.id' /tmp/fpms_offset.json)

  # offset reverse
  curl -sS -X POST "$BASE/offsets/$OFFSET_ID/reverse" -H "$AUTH"
else
  echo "SKIP: offset — no payment_line_id available"
fi

# case receipts
curl -sS -H "$AUTH" "$BASE/cases/$CASE_ID/receipts"
```

#### 7) System/Templates
```bash
# templates list
curl -sS -H "$AUTH" "$BASE/templates?page=1&page_size=20"

# template create
curl -sS -o /tmp/fpms_template.json -w '\n%{http_code}' -X POST "$BASE/templates" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"name":"Smoke Test Template","group":"TEST","language":"en","file_path":"/tmp/smoke_template.docx","enabled":true}'

# system params list
curl -sS -H "$AUTH" "$BASE/system/params"

# system param upsert
curl -sS -X PUT "$BASE/system/params/smoke_test_key" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"param_value":"smoke_test_value","value_type":"string","is_secret":false}'

# letterheads list
curl -sS -H "$AUTH" "$BASE/letterheads"

# letterhead create
curl -sS -o /tmp/fpms_letterhead.json -w '\n%{http_code}' -X POST "$BASE/letterheads" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"name":"Smoke Test Letterhead","locale":"en","header_text":"FPMS Smoke","is_default":false}'
```

If any endpoint returns 404 because it doesn't exist:
- Record it as a defect with evidence.
- Do NOT invent alternative endpoints.
- Propose the smallest fix (frontend remove usage OR backend expose endpoint) — choose the smallest change that restores the documented workflow.

## Step 5 — Identify contract drift precisely (evidence-based)
For any 422 responses:
- Capture `error.details` fully.
- Map them to which frontend form/API wrapper produced the payload.
- Determine the minimal adapter changes required:
  - field renames
  - required fields
  - enum/value mapping
  - nested structures

Create a “Contract Drift Table” in `FE-3_RUNTIME_SMOKE_REPORT.md`:

| Module | Action | FE payload keys | BE expected (from 422 details / schema) | Fix approach | Status |
|---|---|---|---|---|---|

## Step 6 — Fix defects (batched allowed, but minimal + style‑safe)
You MAY fix multiple defects in one pass (bypassing strict atomic PR rule), but:
- keep changes minimal and localized
- do not change token values
- do not add dependencies

Preferred fix layer order:
1) API adapter layer (`src/api/*.ts`) — map FE view models to BE DTOs
2) Types (`src/api/*.types.ts`) — align with actual payload/response
3) Forms/pages — ensure required fields exist and 422 maps to field errors

Important:
- Avoid sweeping refactors. Make the smallest changes that make the runtime smoke pass.

After fixes, rerun the affected curl calls and confirm statuses.

## Step 7 — Re-run frontend gates
Run:
```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```
Record outputs in `FE-3_RUNTIME_SMOKE_EVIDENCE.md`.

## Step 8 — Update QA report and finalize
Update `task/frontend/FE-3/FE-3_QA_REVIEW_REPORT.md`:
- Mark Runtime statuses (PASS/FAIL/Partial)
- Update defect statuses:
  - FE3‑DEF‑009 should be decomposed into specific defects with evidence and fixed status.
  - FE3‑DEF‑010 should become Fixed (runtime executed) once backend is available.

## Final response to user
Return:
- Paths to `FE-3_RUNTIME_SMOKE_REPORT.md` and `FE-3_RUNTIME_SMOKE_EVIDENCE.md`
- A short summary: which flows now pass, what defects remain (if any), and what changes were made (file list).
