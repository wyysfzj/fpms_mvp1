# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Do not change scope
- Follow design docs under `backend/app/modules/**/docs` if present (design wins)

# BE-APIX-03-01 — Templates — Upload/Register

## Purpose
Implement exactly ONE API endpoint for MVP1 Phase 3-EXT (v4 template).
- No schema changes
- Uses existing ORM models only
- Implement in module-level `api.py` (Approach A)

## Preconditions
1) Phase 2 ORM parity is complete for all involved tables.
2) ORM model(s) exist and are importable.
3) Permission enforcement helper exists: `require_perm("<PermissionCode>")`.

## Target File (Single)
- backend/app/modules/templates/api.py

## Endpoint
- Method: POST
- Path: /templates

## Permission
- require_perm("Template.Create")

## Request
MVP1: implement metadata registration. If existing codebase supports multipart upload, follow it; otherwise accept `file_path` metadata only.

## Response (200)
Return created template metadata.

## Error Responses
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found (when applicable)
- 409 Conflict (when applicable)
- 422 Validation Error

## Implementation Steps
1) Open target file.
2) Add the endpoint handler with the exact method/path above.
3) Enforce permission at the start of handler.
4) Use the existing SQLAlchemy session pattern.
5) Validate inputs; raise the project’s standard HTTP exceptions.
6) Return response JSON matching the example.

## JSON Examples
### Request example
```json
{
  "name": "Billing Template",
  "template_type": "bill",
  "file_path": "s3://bucket/templates/bill.docx"
}
```

### Response example (200)
```json
{
  "id": 10,
  "name": "Billing Template",
  "template_type": "bill",
  "file_path": "s3://bucket/templates/bill.docx",
  "created_at": "2025-01-01T00:00:00Z"
}
```

## Curl Smoke Test
```bash
curl -s -X POST "http://localhost:8000/templates" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Billing Template", "template_type": "bill", "file_path": "s3://bucket/templates/bill.docx"}'
```

## Done Criteria
1) Endpoint reachable and returns documented response shape.
2) Permission enforced (403 without permission).
3) Curl smoke test succeeds with valid token + permission.
