# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Do not change scope
- Follow design docs under `backend/app/modules/**/docs` if present (design wins)

# BE-APIX-02-02 — System Params — Upsert One

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
- backend/app/modules/system/api.py

## Endpoint
- Method: PUT
- Path: /system/params/{param_key}

## Permission
- require_perm("SystemParam.Edit")

## Request
JSON body. Implement upsert by param_key using unique constraint on `t_system_param.param_key`.

## Response (200)
Return stored parameter.

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
  "param_value": "en-US",
  "value_type": "string",
  "description": "Default locale",
  "is_secret": false
}
```

### Response example (200)
```json
{
  "param_key": "default_locale",
  "param_value": "en-US",
  "value_type": "string",
  "is_secret": false
}
```

## Curl Smoke Test
```bash
curl -s -X PUT "http://localhost:8000/system/params/default_locale" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"param_value": "en-US", "value_type": "string", "description": "Default locale", "is_secret": false}'
```

## Done Criteria
1) Endpoint reachable and returns documented response shape.
2) Permission enforced (403 without permission).
3) Curl smoke test succeeds with valid token + permission.
