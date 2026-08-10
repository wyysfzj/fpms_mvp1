# FPMS-V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-API-20260810-01

Status: FROZEN / READY FOR IMPLEMENTATION
Risk class: `PROTECTED`

## Authority and prerequisites

- Scheme A source `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`
  SHA-256 `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- `V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SCHEMA-CURRENT-ADOPTION`.
- `V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SERVICE-CURRENT-ADOPTION`.
- Existing system-router permission and transaction conventions.

The API makes the approved five duty slots institution-admin configurable. It creates no default
role/user/membership and never weakens service-level gate, effective-time, personnel-readiness,
actual-user-separation, canonical lineage or CAS checks.

## Exact closure

Create strict Pydantic schemas in
`backend/app/modules/system/grant_manual_review_role_schemas.py`:

- `PublishGrantManualReviewRoleConfigIn`: the five exact role UUID fields, `config_version`,
  `effective_from`, nullable `effective_to`, nullable `expected_current_config_id`, and
  `idempotency_key`.
- `RevokeGrantManualReviewRoleConfigIn`: `config_version`, `effective_from`,
  `expected_current_config_id`, and `idempotency_key`.
- `GrantManualReviewRoleConfigOut`: `config_id`, `config_status`, `config_snapshot_hash`, nullable
  `current_identity_key`, and service disposition.

All input fields are required, extra fields are forbidden, strings are exact trimmed nonblank and
NUL-free, UUIDs are canonical, datetimes are UTC-naive, and publication intervals are valid.
Client-supplied `confirmed_by`, `published_at`, gate, scope, status, hash or disposition is rejected.

Add exactly two authenticated routes to `backend/app/modules/system/api.py`:

1. `POST /system/grant-manual-review-role-configurations` delegates once to
   `publish_grant_manual_review_role_config`; it injects `current_user.id` as `confirmed_by` and
   one server `_utc_now()` as `published_at`.
2. `POST /system/grant-manual-review-role-configurations/{config_id}/revoke` delegates once to
   `revoke_grant_manual_review_role_config`; path UUID must exactly equal
   `expected_current_config_id`, otherwise `422 VALIDATION_ERROR`; it injects the same server-owned
   actor/time fields.

Both routes require `SystemParam.Edit` using the existing direct `_perm` dependency. They reuse the
existing caller-owned commit/rollback helper, return `201` for `CREATED`, `200` for `REUSED`, and
preserve service `400/409`, auth `401`, permission `403`, validation `422`, envelope and rollback
semantics.

## Non-closure

No GET/list/readiness/role-directory endpoint; no new permission/role/seed/default; no service,
model, migration, decision gate, evidence candidate, operational acquisition/review action, UI,
legal status, lifecycle, deadline, document, fee or payment change; no generic router refactor.

## Allowed files

- this task file;
- `backend/app/modules/system/grant_manual_review_role_schemas.py`;
- `backend/app/modules/system/api.py`;
- `backend/tests/test_v8_grant_manual_review_role_api.py`.

## Frozen acceptance matrix

1. Strict schemas expose only the exact client-owned fields and reject extras, malformed UUIDs,
   aware datetimes, invalid intervals and server-owned actor/time fields before delegation.
2. Publish maps all five roles and client fields exactly, injects one authenticated actor/time,
   delegates once, commits once, and returns dynamic `201/200`.
3. Revoke rejects path/body mismatch before service/commit, otherwise maps exact command and
   returns dynamic `201/200`.
4. `SystemParam.Edit` is the exact dependency; 401/403 do not call service or commit.
5. Service `BusinessError` and commit failure each roll back once; successful calls never query or
   flush carrier tables in the API and do not mutate any non-closure domain.

## Verification

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_manual_review_role_api.py`
- Shared-router regressions:
  `cd backend && .venv/bin/pytest -q tests/test_v8_grant_evidence_source_api.py tests/test_system_params.py`
- Service regression:
  `cd backend && .venv/bin/pytest -q tests/test_v8_grant_manual_review_role_service.py`
- Ruff:
  `cd backend && .venv/bin/ruff check app/modules/system/grant_manual_review_role_schemas.py app/modules/system/api.py tests/test_v8_grant_manual_review_role_api.py`
- Exact diff-check on the four allowed paths.

One independent High reviewer reviews the exact implementation commit/range and reruns decisive
checks. PASS requires `P0/P1/P2 = 0/0/0`; no broad, Full or release gate belongs here.
