# Evidence Log — NEXT-3

## Task
- ID: NEXT-3
- Title: Close Offsets flow by obtaining valid `payment_line_id` (no guessing)
- Date: 2026-02-08
- Agent: Codex (GPT-5)

## Backend (Uvicorn)
- Runtime command:
```bash
cd backend
uvicorn app.main:app --reload
```
- Probe:
```bash
curl -i "http://localhost:8000/api/v1/clients?page=1&page_size=1"
```
- Probe result: `401 Unauthorized` with `x-request-id` present (`7a1e0782-d9d7-4a6f-b3de-52a37c65f290`)

## File Allowlist Respected
- ✅ Yes
- Modified files:
  - `backend/app/modules/billing/api.py`
  - `frontend/src/api/billing.ts`
  - `frontend/src/api/billing.types.ts`
  - `frontend/src/modules/billing/pages/PaymentList.vue`
  - `docs/frontend_smoke_flows.md`
  - `task/frontend/POST_FE3_NEXT/NEXT-3_evidence.md`

## 1) Evidence-based discovery

### OpenAPI discovery
Command:
```bash
curl -s http://localhost:8000/openapi.json | jq -r '.paths | keys[]' | rg -i "payment|line|offset|alloc|receipt|bill"
```
Output:
- `/api/v1/payments`
- `/api/v1/payments/{payment_id}`
- `/api/v1/offsets`
- `/api/v1/offsets/{offset_id}/reverse`
- (plus bill/receipt routes)

Finding:
- No dedicated payment-line endpoint in OpenAPI.
- Existing `GET /payments/{payment_id}` did not return `payment_lines` before fix.

### Before fix runtime evidence
1. Login, create payment, fetch payment detail:
   - `POST /api/v1/auth/login` -> `200`
   - `POST /api/v1/payments` -> `201`
   - `GET /api/v1/payments/{payment_id}` -> `200`
   - Response body (before): no `payment_lines` field.
2. Offset attempt without obtainable line id:
   - `POST /api/v1/offsets` with fake `payment_line_id` -> `404`
   - Body:
```json
{"error":{"code":"PAYMENT_LINE_NOT_FOUND","message":"Payment line not found","details":null}}
```
   - `x-request-id`: `0821349e-f85a-49b8-a8a6-bb109ef811d1`

## 2) Chosen smallest path
- Implemented smallest backend exposure by extending existing `GET /api/v1/payments/{payment_id}` response to include:
  - `payment_lines[]` with `id`, `payment_id`, `case_id`, `raw_amount`, `allocated_amt`, `balance_amt`.
- No new route added.
- Frontend updated to consume this response and provide selector-based offset creation:
  - select `Payment` -> fetch `payment_lines`
  - select `Payment Line`
  - select `Bill`
  - submit offset with real `payment_line_id`

## 3) Curl parity proof (after fix)

### Deterministic setup for a payable bill
Commands used:
- `GET /api/v1/fees/rates`
- `GET /api/v1/fees/drafts`
- `POST /api/v1/fees/drafts/{draft_id}/items` -> create positive draft amount
- `POST /api/v1/bills/from-drafts` -> create bill with balance

Results:
- `POST /fees/drafts/{draft_id}/items` -> `201` (`x-request-id`: `310a1985-210f-4aec-b99d-626fe932b90a`)
- `POST /bills/from-drafts` -> `201` (`x-request-id`: `92b89c52-cf20-476a-a322-a4bcc8ffd9e5`)

### Payment + payment line + offset
1. `POST /api/v1/payments` -> `201`
   - `x-request-id`: `e83dd700-fe72-4479-993f-6575b12e3283`
2. `GET /api/v1/payments/{payment_id}` -> `200`
   - Response now includes:
```json
"payment_lines":[
  {
    "id":"c24ffc93-5000-4c8f-a135-eff4181f2f15",
    "payment_id":"a0827637-ac8f-45e3-a220-ce5d2f4df49a",
    "raw_amount":"30.00",
    "allocated_amt":"0.00",
    "balance_amt":"30.00"
  }
]
```
   - `x-request-id`: `be456149-02a9-4c86-a1a8-66360e2cbbad`
3. `POST /api/v1/offsets` with real `payment_line_id` -> `201`
   - Response:
```json
{
  "id":"cf658461-54e1-4569-a201-9ab5e11496e9",
  "payment_line_id":"c24ffc93-5000-4c8f-a135-eff4181f2f15",
  "bill_id":"e8a755bd-e31c-4a32-9f89-500ed71ba085",
  "offset_amt":"5.00",
  "offset_date":"2026-02-08",
  "is_reversed":false
}
```
   - `x-request-id`: `4b19728f-9aa3-4fcb-a4f8-26b816199be0`

Acceptance proof:
- Deterministic method now exists to obtain valid `payment_line_id`.
- Offset creation returns 2xx (`201` observed).

## 4) Gates

### Frontend
```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```
Results:
- `lint`: pass
- `typecheck`: pass (`vue-tsc --noEmit`)
- `build`: pass (`vite build`, completed successfully)

### Backend
```bash
python3 -m compileall backend/app
cd backend && pytest -q
```
Results:
- `compileall`: pass
- `pytest`: pass (`5 passed`)

## Notes
- An initial parallel gate invocation produced a transient ESLint ENOENT on a temporary Vite timestamp file; rerunning `npm run lint` sequentially passed.
