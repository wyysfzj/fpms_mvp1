# Auth Module (MVP1)

## Responsibilities
- Login (username/password) and issue JWT token.
- Provide `/auth/me` for frontend to obtain:
  - user profile
  - roles
  - permission codes list

## Data model (MVP1)
- T_User: id, username, display_name, password_hash, is_active, created_at, updated_at
- T_Role: id, code, name
- T_UserRole: user_id, role_id
- Optional: T_RolePerm (role_id, perm_code) — or seed static mapping in code.

## API (MVP1)
- POST `/api/v1/auth/login`
- GET `/api/v1/auth/me`
- POST `/api/v1/auth/logout` (optional for JWT; frontend-only)

## Non-MVP
- password reset flow
- MFA/SSO
- audit trails
