# Wave 30 Contract Freeze

## Task
- Task ID: `PE-BE-COM-08`
- Task file: `tasks/postenhancement/backend/PE-BE-COM-08.md`
- Role: Architect (`explorer`)
- Scope intent: freeze implementation contract for one atomic backend endpoint task.

## Allowlist Boundaries
- In-scope product files for implementation:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- In-scope evidence outputs:
  - `artifacts/PE-BE-COM-08/**`
- Out of scope:
  - router wiring
  - schema/model/migration edits
  - unrelated module refactors

## Endpoint Contract (`POST /commission/settlements`)
- Method/path:
  - `POST /commission/settlements`
- Success status:
  - `201 Created`
- Success payload semantics:
  - returns created settlement header resource (full created object or equivalent canonical subset), including:
    - `id`
    - `settlement_no` (if generated)
    - `agent_id`
    - `status`
    - `currency`
    - `period_from`
    - `period_to`
    - `line_count`
    - `total_amount`
    - `remark`
    - `created_at`
    - `updated_at`

## Request Contract
- Required/primary fields:
  - `agent_id` (required for agent-specific settlement scope)
  - `currency` (required, non-empty; default not assumed by API contract)
- Optional fields:
  - `period_from` (optional date)
  - `period_to` (optional date)
  - `remark` (optional string)
- Validation constraints:
  - if both period fields provided, `period_from <= period_to`.
  - `agent_id` and `currency` must be normalized (trimmed) and non-empty after normalization.

## Uniqueness Rule and Status Initialization
- Status initialization:
  - newly created settlement header must initialize to `DRAFT`.
- Uniqueness rule (business-level, deterministic):
  - reject duplicate active settlement header for same scope:
    - same `agent_id`
    - same `currency`
    - same `period_from`
    - same `period_to`
    - status in active pre-final states (at minimum includes `DRAFT`)
- Conflict result:
  - return `409` with domain code `COMMISSION_SETTLEMENT_CONFLICT` (or equivalent consistent business code).

## Permission Contract
- Required permission:
  - `CommissionSettlement.Create`
- Mandatory parameter-injection pattern:
  - `_perm: None = Depends(require_perm("CommissionSettlement.Create"))`
- Do not use decorator-level `dependencies=[...]` for permission checks.

## Error Semantics (400/409)
- `400`:
  - business validation failures (invalid period range, missing/blank required fields, invalid currency scope).
- `409`:
  - uniqueness conflict for existing active settlement in same scope.
- `422`:
  - request schema/type validation failures (FastAPI native validation).
- Preserve existing BusinessError/FastAPI envelope conventions.

## Regression Risks
- Permission regression:
  - wrong permission code or non-parameter injection breaks auth control.
- State-init regression:
  - creating non-`DRAFT` initial status breaks downstream generate-lines/status-flow expectations.
- Uniqueness drift:
  - weak conflict check allows duplicate settlement batches for same period and agent scope.
- Contract regression:
  - returning non-created status or non-canonical payload breaks client assumptions.
- Scope risk:
  - edits outside allowlist violate atomic policy.

## Acceptance Checklist
- [ ] Implementation edits only allowlisted product files:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- [ ] `POST /commission/settlements` endpoint is implemented.
- [ ] Request supports `agent_id`, `period_from`, `period_to`, `currency`, `remark` contract.
- [ ] Permission enforced with parameter-injected:
  - `Depends(require_perm("CommissionSettlement.Create"))`
- [ ] New settlement initializes with `status=DRAFT`.
- [ ] Uniqueness conflict check enforced for same active scope and returns `409`.
- [ ] Success returns `201` with created settlement payload.
- [ ] Error semantics include required business `400/409` behavior.
- [ ] Task verification passes:
  - `cd backend && pytest -q`
- [ ] Lint/format discipline passes:
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
- [ ] Evidence artifacts are generated for completion claim:
  - `artifacts/PE-BE-COM-08/results.jsonl`
  - `artifacts/PE-BE-COM-08/summary.md`
  - `artifacts/PE-BE-COM-08/git/diff.patch`
