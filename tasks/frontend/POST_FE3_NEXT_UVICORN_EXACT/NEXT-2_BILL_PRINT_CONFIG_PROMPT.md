# EXECUTION PROMPT — NEXT‑2 (Config/Runbook)
## Title
NEXT‑2: Unblock Bill Print (`GET /bills/{id}/print` is 409) via deterministic configuration script

## Context (Evidence)
Runtime smoke indicates:
- `GET /api/v1/bills/{id}/print` => **409** (template not configured)

## Objective
1) Capture the exact missing configuration from the 409 envelope.
2) Create an idempotent setup script to configure required templates/letterheads/params.
3) Verify print returns 200 (blob).
4) Document prerequisites in `docs/frontend_smoke_flows.md`.

## Backend Runtime (mandatory)
```bash
cd backend
uvicorn app.main:app --reload
```

## File Allowlist (ONLY modify/add these)
- `scripts/dev/setup_printing.sh` (new)
- `docs/frontend_smoke_flows.md` (update)
- Evidence:
  - `task/frontend/POST_FE3_NEXT/NEXT-2_evidence.md`

If additional files are required, STOP and propose the smallest follow-up task.

## Steps
### 1) Login and capture 409 details (Before)
```bash
curl -sS -o /tmp/fpms_login.json -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
TOKEN="$(jq -r '.access_token' /tmp/fpms_login.json)"

curl -i "http://localhost:8000/api/v1/bills/<BILL_ID>/print" \
  -H "Authorization: Bearer $TOKEN"
```
Record status, envelope, and x-request-id.

### 2) Implement idempotent setup script
Create `scripts/dev/setup_printing.sh` that:
- obtains token
- ensures letterhead exists (create if none)
- ensures required print template exists following backend contract
- ensures required system params exist (upsert)
- verifies print success at the end (re-call `/bills/{id}/print`)

Script must be safe to run multiple times.

### 3) Update smoke docs
Update `docs/frontend_smoke_flows.md` with:
- printing prerequisites
- how to run `scripts/dev/setup_printing.sh`
- expected success signal (200 blob)

### 4) Verify after
- Run script twice.
- Confirm `/bills/{id}/print` returns 200.

### 5) Optional frontend gates (docs change)
```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```

## Acceptance Criteria
- Print returns 200 after setup.
- Script is repeatable.
- Docs updated.
- Evidence includes before/after curl with requestId.

## Evidence Log
Write: `task/frontend/POST_FE3_NEXT/NEXT-2_evidence.md`.

## Final Output
- Script path + usage
- Before/after proof
- Docs summary
