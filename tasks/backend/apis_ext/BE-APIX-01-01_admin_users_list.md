# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Do not change scope
- Follow design docs under `backend/app/modules/**/docs` if present (design wins)

# BE-APIX-01-01 — Admin Users — List

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
- backend/app/modules/admin/api.py

## Endpoint
- Method: GET
- Path: /admin/users

## Permission
- require_perm("AdminUser.Read")

## Request
No body. Follow existing project pagination conventions if present; do not invent new query params.

## Response (200)
Return list payload. Follow existing project response conventions (items/total vs plain list).

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
{}
```

### Response example (200)
```json
{
  "items": [
    {
      "id": 1,
      "username": "admin",
      "is_active": true,
      "roles": [
        "Admin"
      ],
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

## Curl Smoke Test
```bash
curl -s -X GET "http://localhost:8000/admin/users" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Done Criteria
1) Endpoint reachable and returns documented response shape.
2) Permission enforced (403 without permission).
3) Curl smoke test succeeds with valid token + permission.
