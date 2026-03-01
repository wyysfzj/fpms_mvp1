# EXECUTION PROMPT — NEXT‑1 (Backend)
## Title
NEXT‑1: Fix `POST /documents/{id}/attachments` returning `500` and ensure `X-Request-ID` + error envelope on failures

## Context (Evidence)
Runtime smoke indicates:
- `POST /api/v1/documents/{id}/attachments` returns **500**
- response missing `X-Request-ID`

## Objective
1) Make multipart upload succeed (201/200) for a valid file.
2) Ensure on any failure (including unhandled exceptions):
   - standard error envelope: `{"error":{"code","message","details"}}`
   - `X-Request-ID` header exists.

## Backend Runtime (mandatory)
Start backend in Terminal 1:
```bash
cd backend
uvicorn app.main:app --reload
```

Probe in Terminal 2:
```bash
curl -i "http://localhost:8000/api/v1/clients?page=1&page_size=1"
```

## File Allowlist (ONLY modify/add these)
- `backend/app/modules/documents/**`
- `backend/app/core/**` (ONLY if needed for request-id/exception handling)
- `backend/tests/**` (optional minimal regression test if available)
- `scripts/dev/**` (optional: add a repro curl script)
- Evidence:
  - `task/frontend/POST_FE3_NEXT/NEXT-1_evidence.md`

If additional files are required, STOP and propose the smallest follow-up task.

## Steps (must follow)
### 1) Reproduce before (curl)
Login:
```bash
curl -sS -o /tmp/fpms_login.json -w "%{http_code}" \
  -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
echo
TOKEN="$(jq -r '.access_token' /tmp/fpms_login.json)"
```

Upload:
```bash
curl -i -X POST "http://localhost:8000/api/v1/documents/<DOC_ID>/attachments" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@<PATH_TO_FILE>"
```

Record:
- status
- body
- presence/absence of `x-request-id`

### 2) Identify root cause
Inspect uvicorn logs (stack trace) and identify failure layer.

### 3) Implement minimal fix
Fix the root cause with the smallest change.
Ensure requestId header is still present on 500 (middleware/handler order).

### 4) Verify after
- Re-run upload → expect 2xx.
- Trigger a controlled failure (invalid doc id) → expect:
  - error envelope
  - x-request-id present

### 5) Backend quality gates
Minimum:
```bash
python -m compileall backend/app
```
If pytest exists:
```bash
pytest -q
```

## Acceptance Criteria
- Upload returns 2xx.
- Failures return error envelope + x-request-id.
- Evidence includes before/after curl outputs and requestId samples.

## Evidence Log
Write: `task/frontend/POST_FE3_NEXT/NEXT-1_evidence.md` using the template.

## Final Output to user
- Root cause
- File list changed
- Before/after curl proof
- Gate outputs
