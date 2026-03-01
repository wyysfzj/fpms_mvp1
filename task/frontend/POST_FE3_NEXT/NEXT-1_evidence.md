## Task
- ID: NEXT-1
- Title: Fix `POST /documents/{id}/attachments` returning 500 and ensure `X-Request-ID` + error envelope on failures
- Date: 2026-02-08
- Agent: Codex (GPT-5)

## Backend (Uvicorn)
- Command attempted:
```bash
cd backend
uvicorn app.main:app --reload
```
- Result: port `8000` was already in use by an existing backend process (`[Errno 48] Address already in use`).
- For traceback capture, a temporary debug server was started on `127.0.0.1:8001`.
- Probe:
```bash
curl -i "http://localhost:8000/api/v1/clients?page=1&page_size=1"
```
- Probe status: `401 Unauthorized` (backend reachable)

## File Allowlist Respected
- ✅ Yes
- Modified files:
  - `backend/app/modules/documents/api.py`
  - `backend/app/core/middleware.py`
  - `task/frontend/POST_FE3_NEXT/NEXT-1_evidence.md`

## Commands Run
```bash
# Repro/login/upload
curl -sS -o /tmp/fpms_login.json -w "%{http_code}" \
  -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
TOKEN="$(jq -r '.access_token' /tmp/fpms_login.json)"

curl -i -X POST "http://localhost:8000/api/v1/documents/<DOC_ID>/attachments" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/next1_upload_file.txt"

# Quality gates
python3 -m compileall backend/app
cd backend && pytest -q
```

## Key Outputs
- backend compile/tests:
  - `python3 -m compileall backend/app` -> PASS
  - `pytest -q` -> `5 passed, 3 warnings in 1.69s`

## Reproduction / Verification
### Before
- Steps:
  1. Login (`admin/admin123`) and get token.
  2. Upload file to `/api/v1/documents/7249af27-45e1-467f-978a-ecda60af7f10/attachments`.
- Result:
```http
HTTP/1.1 500 Internal Server Error
content-type: text/plain; charset=utf-8

Internal Server Error
```
- `x-request-id`: **absent**
- Uvicorn traceback (captured on debug run) showed:
  - `AttributeError: 'DocAttachment' object has no attribute 'uploaded_at'`
  - failing line: `backend/app/modules/documents/api.py` in `add_attachment` response mapping.

### After
- Steps:
  1. Re-run upload with valid doc id and file.
  2. Trigger controlled failure using invalid document id.
- Result (success upload):
```http
HTTP/1.1 201 Created
content-type: application/json
x-request-id: d58d3406-19ba-43ea-aeb3-f6b9a2d85495

{"id":"0f2393f5-5c55-4eb5-b027-1c59cca7e848","document_id":"7249af27-45e1-467f-978a-ecda60af7f10","file_name":"next1_upload_file_after_8000.txt","mime_type":"text/plain","file_size":28,"uploaded_at":"2026-02-08T15:20:46.260903"}
```
- Result (invalid document id):
```http
HTTP/1.1 404 Not Found
content-type: application/json
x-request-id: 849ea885-4aa2-443f-af45-3a0f53213c2f

{"error":{"code":"DOCUMENT_NOT_FOUND","message":"Document not found","details":null}}
```

## API Evidence
- Requests (method + URL + key payload fields):
  - `POST /api/v1/auth/login` (`username`, `password`)
  - `POST /api/v1/documents/{document_id}/attachments` (multipart `file`)
  - `POST /api/v1/documents/00000000-0000-0000-0000-000000000000/attachments` (multipart `file`)
- Status codes:
  - Before fix upload: `500`
  - After fix upload: `201`
  - Controlled failure invalid doc id: `404`
- X-Request-ID samples:
  - Upload success: `d58d3406-19ba-43ea-aeb3-f6b9a2d85495`
  - Invalid doc id failure: `849ea885-4aa2-443f-af45-3a0f53213c2f`

## Notes
- Root cause fix: replace non-existent `attachment.uploaded_at` access with `attachment.created_at` in document attachment response mapping.
- Safety fix: Correlation middleware now catches unhandled exceptions and returns standard error envelope with `X-Request-ID`.
