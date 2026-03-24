# Wave 12 Contract Freeze

## Task
- Task ID: `PE-BE-AN-02`
- Task file: `tasks/postenhancement/backend/PE-BE-AN-02.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product file for implementation:
  - `backend/app/modules/annuity/api.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-AN-02/**`
- Out of scope:
  - `backend/app/modules/annuity/service.py` (already delivered by dependency `PE-BE-AN-01`)
  - `backend/app/api/router.py` wiring (reserved for `PE-BE-WIRE-01`)
  - schema/model/migration changes
  - unrelated module refactors

## Endpoint Contract (`GET /annuity/tasks`)
- Method/path:
  - `GET /annuity/tasks`
- Request body:
  - none (GET must not require body)
- Query contract (minimum):
  - `page` (int, `>=1`, default `1`)
  - `page_size` (int, `>=1`, default `20`)
  - due-range filters compatible with AN-01 service (`due_from`, `due_to`)
  - status filters compatible with AN-01 service (`status`, pending mode)
- Optional passthrough filters allowed if already supported by service:
  - `case_id`, `client_id`, `notice_status`
- Success response:
  - HTTP `200`
  - list envelope shape consistent with existing list endpoints:
    - `{"items": [...], "page": <int>, "page_size": <int>, "total": <int>}`

## Permission Contract
- Required permission code:
  - `AnnuityTask.Read` (per `docs/permissions_matrix.md`)
- Enforcement style is mandatory:
  - inject as function parameter, not decorator dependencies list:
  - `_perm: None = Depends(require_perm("AnnuityTask.Read"))`
- Auth/permission error semantics:
  - `401` unauthenticated (`AUTH_REQUIRED`)
  - `403` authenticated but missing permission (`FORBIDDEN`)

## Envelope and Status Semantics
- Must preserve existing module/API envelope conventions; do not invent new response envelope shapes.
- For post-enhancement annuity domain:
  - business validation failures: `400` with BusinessError envelope
  - request validation failures: `422` with validation envelope
  - conflicts (if any in downstream behavior): `409`
- `GET /annuity/tasks` primary success is `200` with content.
- If route is not yet included in `api/router.py`, runtime may still show framework `404` until `PE-BE-WIRE-01`; this is outside this task scope.

## Service Contract Assumptions
- API layer consumes AN-01 service without changing service behavior.
- Filtering, pending-mode interpretation, and deterministic ordering are delegated to existing service logic.
- Pagination metadata (`page`, `page_size`, `total`) is returned by API envelope consistently.

## Regression Risks
- Permission regression:
  - wrong permission code or wrong `Depends` injection pattern can cause false 403 or violate AGENTS policy.
- Envelope regression:
  - returning raw list/model without list envelope can break frontend and contract checks.
- Filter contract drift:
  - query param names not mapped to AN-01 service expectations can produce incorrect result sets.
- Scope violation:
  - router wiring or service edits in this task would violate atomic allowlist.
- False-negative runtime check risk:
  - endpoint may appear unavailable (404) before `PE-BE-WIRE-01`; this should not be misclassified as AN-02 implementation failure.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product file for `PE-BE-AN-02`.
- [ ] `GET /annuity/tasks` endpoint exists in `backend/app/modules/annuity/api.py`.
- [ ] Endpoint enforces permission via:
  - `_perm: None = Depends(require_perm("AnnuityTask.Read"))`
- [ ] Endpoint returns list envelope with pagination metadata:
  - `items`, `page`, `page_size`, `total`
- [ ] Query filtering supports pagination, due-range, and status/pending semantics per AN-01.
- [ ] Status/error semantics align with post-enhancement contract:
  - `200/400/401/403/409/422` as applicable
- [ ] Task verification command passes:
  - `cd backend && ruff check . && pytest -q`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-AN-02/results.jsonl`
  - `artifacts/PE-BE-AN-02/summary.md`
  - `artifacts/PE-BE-AN-02/git/diff.patch`
