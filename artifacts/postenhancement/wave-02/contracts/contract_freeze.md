# Wave 02 Contract Freeze (Architect)

Date: 2026-02-28  
Scope: Wave 02 atomic tasks only (`PE-BE-00-02`, `PE-FE-00-02`)

## Freeze Rules (Wave 02)
- Execute each atomic task in a separate run.
- Stay strictly inside each task allowlist.
- No router rewiring, no DB schema/migration changes, no envelope changes.
- Permission naming stays `Title.Action` only.

## PE-BE-00-02
- Task: unify new-module permission constants and write them into RBAC seed dictionary.
- Allowed files:
  - `backend/app/modules/rbac/service.py`
  - `docs/permissions_matrix.md`
- Expected permission/API behavior impact:
  - No new endpoint and no endpoint signature/status change.
  - RBAC seed source of truth (`ROLE_PERMISSIONS`) is updated so seeded roles (especially `Admin`) include newly introduced domain permissions.
  - `docs/permissions_matrix.md` remains consistent with backend `require_perm("...")` usage and `Title.Action` naming.
  - Seed behavior remains idempotent (re-running seed does not create duplicate role-perm rows or fail).
- Regression risks:
  - Permission code rename instead of additive update breaks existing access checks.
  - Drift between `ROLE_PERMISSIONS` and `permissions_matrix` causes docs/runtime mismatch.
  - Duplicate perm strings inside one role list can trigger unique-constraint failures (`uq_role_perm`) during seed.
  - Mixed naming styles (`FeeRate.*` vs `Fee.Rate.*`) can create ambiguous effective permission surface.
- Acceptance checklist:
  - New/adjusted permission codes follow `Title.Action`.
  - `Admin` role includes all new domain permissions required by current protected APIs.
  - Seeding roles/permissions is idempotent (second run introduces zero net new role-perm records and no error).
  - `docs/permissions_matrix.md` reflects runtime permission mapping for changed domain permissions.
  - Task verification command passes: `cd backend && pytest -q tests/test_system_params.py`.
  - Recommended consistency check (non-gate): `cd backend && python scripts/scan_perms.py` shows no unexpected `ADMIN_MISSING`.

## PE-FE-00-02
- Task: fetch real permissions after login and write into auth store (remove permissive unknown behavior).
- Allowed files:
  - `frontend/src/stores/auth.ts`
  - One API file only: `frontend/src/api/system.ts` or newly added `frontend/src/api/auth.ts`
- Expected permission/API behavior impact:
  - Login flow adds post-login permission load path (read real permissions from backend API).
  - Secure default is fail-closed: before permissions are loaded, `hasPermission`/`hasAnyPermission` must deny routes/menu items that require non-empty permissions.
  - Permission-load failure must not silently widen UI access; no fallback to allow-all when permissions are unknown.
  - Existing backend API contracts and error envelope remain unchanged; frontend only consumes them.
- Regression risks:
  - Leaving `unknown => allow` logic in store silently widens client-side access.
  - Permission fetch failure path leaves stale token or stale permissions from prior session.
  - Login UX dead-end if fetch fails and state machine does not resolve into explicit denied/logout path.
  - Fetching from a non-authoritative endpoint gives incomplete permission set and wrong UI gating.
- Acceptance checklist:
  - Store has explicit permission-load state (loaded vs not loaded), and non-empty permission checks deny until loaded.
  - After successful permission fetch, `hasAnyPermission` reflects real permission set only.
  - On logout and unauthorized events, token and permissions are both cleared.
  - Permission-fetch failures do not result in permissive rendering.
  - No edits outside allowlist.
  - Task verification commands pass: `cd frontend && npm run lint && npm run typecheck`.

## Cross-Task Compatibility Notes
- Backend permission updates (PE-BE-00-02) and frontend permission consumption (PE-FE-00-02) must stay aligned on exact string values.
- Frontend must not derive permissions from static constants or optimistic defaults; only backend-authoritative permission payload is valid.

## Blocker / Decision Needed
- Current backend runtime exposes `POST /auth/login` but no implemented `GET /auth/me` endpoint returning current user permissions.
- `PE-FE-00-02` requires an authoritative permission source; without such endpoint, secure fail-closed behavior can be implemented, but successful permission loading cannot be fully completed end-to-end.
