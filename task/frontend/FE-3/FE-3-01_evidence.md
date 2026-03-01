# FE-3-01 Evidence Log

## Task
- ID: FE-3-01
- Title: Integration: UI Smoke Flows doc + run core MVP1 flows

## File Allowlist Respected
- ✅ Yes
- Files changed:
  - `docs/frontend_smoke_flows.md`
  - `task/frontend/FE-3/FE-3-01_evidence.md`

## Commands Executed
```bash
# Backend bootstrap
cd backend && alembic upgrade head
cd backend && python3 scripts/seed_dev.py
cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000

# Frontend runtime
cd frontend && npm install
cd frontend && npm run dev

# Headless UI smoke execution (Playwright script)
cd frontend && NODE_PATH=./node_modules node /tmp/fe3_ui_smoke.js

# Mandatory quality gates
cd frontend && npm run lint
cd frontend && npm run typecheck
cd frontend && npm run build
```

## Outputs (Key Lines)
- `alembic upgrade head`: success (`SQLiteImpl`, no migration errors)
- `seed_dev.py`: success (`Admin user 'admin' already exists`)
- UI smoke runner output file: `/tmp/fe3_ui_smoke_results.json`
- Quality gates:
  - `npm run lint`: ✅ passed
  - `npm run typecheck`: ✅ passed
  - `npm run build`: ✅ passed (Vite build completed)

## UI Smoke Run Summary (Executed)
Source: `/tmp/fe3_ui_smoke_results.json`

| Flow | Result | Key API statuses observed | requestId example | Notes |
|---|---|---|---|---|
| Auth/session | Partial | `POST /auth/login -> 200` | `9f37c688-8ca0-46ac-9d83-1a38a38cfbc5` | Valid login succeeded. Invalid-login substep blocked by guard state during same session run. |
| Clients (list/create/edit/deactivate) | Partial | `GET /clients -> 200`, `POST /clients -> 422` | `289c68cb-35ba-49d3-ac20-351278a8e661` | Create hits validation mismatch vs backend schema; list works. |
| Cases (list/create/detail/edit/limited-edit) | Partial/Blocked | `GET /cases -> 200` | `c0bb590f-0763-494a-aca0-693be52c43b8` | Create did not complete end-to-end; no case row available for detail/edit/limited-edit in this run. |
| Tasks (list/create/close/reopen/cancel/today) | Partial/Blocked | `GET /tasks -> 200`, `POST /tasks -> 422`, `GET /tasks/today -> 200` | `b679caf1-378e-45e5-b12d-d65b6ed57556` | Create failed validation; no task row to execute close/reopen/cancel. |
| Documents (list/create/detail/upload/download) | Partial/Blocked | `GET /documents -> 200`, `POST /documents -> 422` | `a014e6ea-303f-400c-baba-415aa0d981cc` | Create failed validation; no doc row for detail/upload/download. |
| Fees (rates/drafts/items/lock) | Partial/Blocked | `GET /fees/rates -> 200`, `POST /fees/rates -> 422`, `POST /fees/drafts -> 404`, `GET /fees/drafts -> 200` | `d174b57b-e4f1-4db0-8704-88c318312aa5` | Rate create schema mismatch; draft create used non-existent case id in UI run; no draft row for items/lock. |
| Billing (bills/detail/create/print + payments/offsets + receipts) | Blocked/Partial | `GET /bills -> 200`, `GET /payments -> 200`, `POST /payments -> 422`, `GET /offsets -> 405` | `c310c146-de54-4f75-9fe6-bf43380692ce` | Manual bill create step blocked in UI interaction; payment payload mismatch (422); offsets list endpoint not implemented (`405`). |
| System/Templates (templates upload, params upsert, letterheads) | Partial | `GET /templates -> 200`, `GET /system/params -> 200`, `PUT /system/params/{key} -> 422`, `GET /letterheads -> 200`, `POST /letterheads -> 201` | `d954b7bc-6bf1-40ae-bac5-ef1cf8f8f7dd` | Param upsert payload mismatch (422). Letterhead create works (201). |

## Manual Verification Steps + Results
The smoke flow execution was run through a headless browser (UI route-level actions with real network calls).

1. Logged in at `/login` using `admin/admin123`.
- Result: success (`200`)

2. Navigated each required route family and triggered primary buttons/actions.
- Result: mixed (list/read routes mostly `200`; multiple create/action routes failed due payload/API mismatch)

3. Recorded each API response status and `X-Request-Id` (when present).
- Result: captured in `/tmp/fe3_ui_smoke_results.json`

4. Checked UX state handling in observed flows.
- Loading/empty/error states are present on list/detail pages.
- Pagination rendered on list pages.
- Validation failures surfaced as banners/field errors where API call occurred.

## STOP Conditions / Mismatches Found
Per FE-3-01 rule, execution stops at contract mismatches and documents smallest atomic fix tasks.

### Mismatch A: Clients create/edit payload contract drift
- Observed: `POST /clients -> 422`
- Frontend payload fields (`name`, `contact_person`, etc.) differ from backend schema (`client_code`, `name_cn`, etc.).
- Smallest fix task proposal: **FE-3-01-FIX-A** (align `clients` DTO/form payload and response mapping only).

### Mismatch B: ID type drift across modules (numeric UI vs UUID backend)
- Observed in cases/tasks/documents/fees create/detail linkage.
- Frontend forms and route parsing frequently assume numeric IDs; backend uses string UUID IDs.
- Smallest fix task proposal: **FE-3-01-FIX-B** (UUID/string ID normalization in FE forms/routes/API types for Cases/Tasks/Documents/Fees).

### Mismatch C: Fees rate/item contracts drift
- Observed: `POST /fees/rates -> 422`, draft item flow blocked.
- Frontend rate fields (`name`,`rate`) differ from backend (`fee_code`,`fee_name`,`fee_type`,`default_amount`).
- Fee items frontend expects endpoints/payloads not fully aligned to backend (`rate_id`-driven model).
- Smallest fix task proposal: **FE-3-01-FIX-C** (fees rates/items API contract alignment only).

### Mismatch D: Billing payments/offsets contract drift
- Observed: `POST /payments -> 422`, `GET /offsets -> 405`.
- Frontend payment payload uses bill-centric fields; backend payment schema differs.
- Frontend expects list endpoint for offsets that backend does not provide.
- Smallest fix task proposal: **FE-3-01-FIX-D** (billing payments/offsets endpoint + payload alignment only).

### Mismatch E: System params payload drift
- Observed: `PUT /system/params/{key} -> 422`
- Frontend sends `{ value, description }`; backend expects different keys (`param_value`, `value_type`, `is_secret`).
- Smallest fix task proposal: **FE-3-01-FIX-E** (system params upsert payload mapping only).

## Action Taken (STOP vs In-scope Fix)
- Action: **STOPPED at mismatch reporting** as required by FE-3-01 constraints.
- No product code changes were made outside the allowed doc/evidence files.
- Mismatches were not fixed in this task; only documented with smallest atomic follow-up tasks.
