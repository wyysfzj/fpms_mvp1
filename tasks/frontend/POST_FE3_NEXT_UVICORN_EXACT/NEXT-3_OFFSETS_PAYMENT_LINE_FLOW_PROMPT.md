# EXECUTION PROMPT — NEXT‑3 (Flow closure)
## Title
NEXT‑3: Close Offsets flow by obtaining valid `payment_line_id` (no guessing)

## Context (Evidence)
Runtime smoke indicates:
- `POST /offsets` => 404 `PAYMENT_LINE_NOT_FOUND`
- Valid `payment_line_id` is not obtainable in the tested flow.

## Objective
1) Discover (OpenAPI + real responses) how to obtain `payment_line_id`.
2) If no endpoint exposes it, implement the smallest backend exposure.
3) Update frontend offsets UI to select a valid payment line and create offset successfully.
4) Provide curl parity proof.

## Backend Runtime (mandatory)
```bash
cd backend
uvicorn app.main:app --reload
```

## File Allowlist (ONLY modify/add these)
### Frontend
- `frontend/src/api/billing.ts`
- `frontend/src/api/billing.types.ts`
- `frontend/src/modules/billing/pages/**` (only pages involved)
- `frontend/src/modules/billing/components/**` (optional)
- `docs/frontend_smoke_flows.md` (only if steps change)

### Backend (ONLY if required)
- `backend/app/modules/billing/**`
- `backend/tests/**` (optional)

### Evidence
- `task/frontend/POST_FE3_NEXT/NEXT-3_evidence.md`

If additional files are required, STOP and propose the smallest follow-up task.

## Steps
### 1) Evidence-based discovery
Use OpenAPI:
```bash
curl -s http://localhost:8000/openapi.json | jq -r '.paths | keys[]' | rg -i "payment|line|offset|alloc|receipt|bill"
```

Inspect actual responses for existing endpoints (token required). Determine whether any response includes:
- payment lines
- line IDs
- a field named `payment_line_id`

Record findings in evidence.

### 2) Choose smallest viable path
- If an existing endpoint already exposes payment lines: update FE to use it.
- Otherwise implement minimal BE exposure:
  - add `GET /payments/{id}/lines` OR include `payment_lines` in payment detail response
Pick smallest change consistent with existing patterns.

### 3) Frontend minimal changes
- Provide a selector for payment lines (id + amount)
- Submit `POST /offsets` with a real `payment_line_id`

### 4) Curl parity proof
- Create payment
- Fetch payment lines and pick a real id
- Create offset
Record status + x-request-id.

### 5) Gates
Frontend:
```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```
Backend:
```bash
python -m compileall backend/app
```
(and pytest if configured)

## Acceptance Criteria
- Deterministic method to obtain valid `payment_line_id`.
- Offset create returns 2xx.
- Evidence includes discovery + proof + file list.

## Evidence Log
Write: `task/frontend/POST_FE3_NEXT/NEXT-3_evidence.md`.
