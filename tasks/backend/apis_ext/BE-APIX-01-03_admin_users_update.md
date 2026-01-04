# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Do not change scope
- Follow design docs under `backend/app/modules/**/docs` if present (design wins)

# BE-APIX-01-03 — Admin Users — Update

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
- Method: PUT
- Path: /admin/users/{user_id}

## Permission
- require_perm("AdminUser.Edit")

## Request
JSON body. Allow updating roles and activation status using existing RBAC models. Do not invent new fields.

## Response (200)
Return updated user summary.

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
  "roles": [
    "Staff"
  ],
  "is_active": true
}
```

### Response example (200)
```json
{
  "id": 2,
  "username": "jane",
  "is_active": true,
  "roles": [
    "Staff"
  ]
}
```

## Curl Smoke Test
```bash
curl -s -X PUT "http://localhost:8000/admin/users/2" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"roles": ["Staff"], "is_active": true}'
```

## Done Criteria
1) Endpoint reachable and returns documented response shape.
2) Permission enforced (403 without permission).
3) Curl smoke test succeeds with valid token + permission.
